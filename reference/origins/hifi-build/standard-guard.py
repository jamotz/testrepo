#!/usr/bin/env python3
"""Standard-mode guard for the Enlarged view accessibility layer.

WHAT THIS IS FOR
Enlarged view is a token layer: every font-size in the app is a --fs-* or
--text-* token whose *Standard* value is the original literal, overridden once
in #scr.enlarged. Standard is not supposed to move when Enlarged changes. Once,
it did: flattening the Enlarged scale used re.sub(..., count=1) on six semantic
tokens, count=1 matched the FIRST occurrence in the file -- which is :root, the
Standard block, not the #scr.enlarged one below it -- and Standard silently took
the enlarged values for the nav bar, product cards, weights and filter labels.
Nothing looks wrong while you work, because you are looking at Enlarged.

This resolves every token back to its literal, drops every rule scoped to
#scr.enlarged, and compares what is left against the same stylesheet as it was
before any Enlarged work existed. Standard should be byte-identical in effect.

    python3 standard-guard.py                 # working tree vs the baseline
    python3 standard-guard.py --rev HEAD      # a committed revision instead
    python3 standard-guard.py --verbose       # list every declaration compared

Exit status is 0 on PASS, 1 on FAIL. Run it after every change to the Enlarged
layer, and before publishing.

THE BASELINE IS A COMMIT, NOT A CAPTURED FILE
BASELINE below is the last commit before the Enlarged work began -- verified to
contain zero --fs-* tokens and zero #scr.enlarged rules. Deriving the baseline
from git is the whole point: a baseline captured from the *current* file would
certify whatever regression is already in it. If this guard is ever rewritten,
keep that property. Note that the expected sizes are re-derived from BASELINE on
every run rather than stored here -- freezing them in would assert one author's
reading of the file instead of the file itself.

ACCEPTED DELTAS
A declaration can change here without Standard changing on screen -- the case
this was built for is a style moving from an inline style attribute into the
stylesheet. The rendered result is identical, but the stylesheet gains a
declaration the baseline does not have, so this guard fails and is right to.
ACCEPTED below lists such changes, each with a reason, and every run PRINTS how
many it applied so they stay visible.

An entry is only legitimate when snapshot-guard.js -- which compares COMPUTED
styles rather than stylesheet text -- passes on the same build. That is the
evidence that Standard did not actually move; without it an entry is just a
red run silenced. Never add one to get to green.

WHEN THE FAILURE IS LEGITIMATE
If Standard type is deliberately changed -- Jack asks for a different size in
NORMAL view, not in Enlarged -- this guard fails, and it is right to. Standard
did move. The response is to RE-BASELINE DELIBERATELY: set BASELINE to the
commit that made the change, in a commit that says what moved and why. Do not
widen the guard, add per-selector exceptions, or drop declarations from the
comparison until it goes green; that trades the whole check for the one change
in front of you.

Reading the FAIL output to tell the two apart:
  - a REGRESSION shows Standard taking recognisably *enlarged* values -- 22px,
    24px, 1.8rem -- on selectors you did not mean to touch, usually several at
    once, and usually while you were editing the Enlarged block
  - a DELIBERATE change shows the value you intended, on the selector you
    intended, and typically alone
When it is not obvious which you are looking at, assume regression and check the
Enlarged block for a rewrite that landed on :root.

WHAT IT DOES NOT COVER
Stylesheet text only. It will not see a size applied by JS at runtime, or a
cascade/specificity effect that changes which rule wins. The heavier check --
a computed-style snapshot driven through Playwright over every screen, diffed
as a multiset per screen -- is still worth building; see docs/architecture.md.
That one needs a build of the baseline commit, so it costs ~2 min a side.
"""
import argparse, re, subprocess, sys
from collections import Counter

# Last commit before Enlarged: "Lifestyles tile wears its six colours".
BASELINE = "cc6edad"

# Declarations that differ from the baseline without Standard rendering
# differently. See ACCEPTED DELTAS above: each needs a reason, and each needs
# snapshot-guard.js passing on the same build as its evidence.
ACCEPTED = [
    {
        "selector": ".vape .bk",
        "value": ".9rem",
        "gained": True,
        "why": "The vape screen's back button carried its font-size as an INLINE "
               "style, so no --fs-* token could reach it and it never grew in "
               "Enlarged. Moved into the stylesheet as .vape .bk with the same "
               "value; nothing else targets the element, so Standard renders "
               "identically. Verified by snapshot-guard.js on the same build.",
    },
]


def is_accepted(sel, val, gained):
    return any(a["selector"] == sel and a["value"] == val and a.get("gained", False) == gained
               for a in ACCEPTED)
SRC = "reference/origins/hifi-build/origins-app.src.html"


def stylesheet(rev=None):
    if rev is None:
        text = open(SRC, encoding="utf-8").read()
    else:
        text = subprocess.run(["git", "show", f"{rev}:{SRC}"],
                              capture_output=True, text=True, check=True).stdout
    m = re.search(r"<style>(.*?)</style>", text, re.S)
    if not m:
        sys.exit(f"no <style> block found in {rev or 'working tree'}")
    return m.group(1)


def tokens(css):
    """The Standard token values, anchored on their own blocks.

    Anchor on the block, never on offset or match order: :root and
    #scr.enlarged declare the SAME token names by design, so a first-match or
    slice-based read silently returns the enlarged values. That is the bug this
    guard exists to catch, and it is just as easy to write here."""
    out = {}
    sem = re.search(r"\n:root\{(.*?)\n\}", css, re.S)          # first :root = Standard
    fs = re.search(r"/\* ── Type scale.*?\n:root\{(.*?)\n\}", css, re.S)
    for block in (sem, fs):
        if block:
            out.update(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block.group(1)))
    return out


def standard_font_sizes(css):
    """(selector, font-size) for every rule that is NOT scoped to Enlarged."""
    tok = tokens(css)
    unresolved = set()

    def resolve(value):
        for _ in range(4):                       # tokens may point at tokens
            new = re.sub(r"var\((--[\w-]+)\)",
                         lambda m: tok.get(m.group(1), m.group(0)), value)
            if new == value:
                break
            value = new
        unresolved.update(re.findall(r"var\((--[\w-]+)\)", value))
        return re.sub(r"\s+", " ", value.strip())

    found = Counter()
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        if "#scr.enlarged" in sel or sel.startswith("@"):
            continue
        sel = re.sub(r"/\*.*?\*/", "", sel, flags=re.S)        # strip lead comments
        sel = re.sub(r"\s+", " ", sel).strip()
        for raw in re.findall(r"font-size:\s*([^;}]+)", body):
            found[(sel, resolve(raw))] += 1
    return found, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", help="compare this revision instead of the working tree")
    ap.add_argument("--baseline", default=BASELINE)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    base, _ = standard_font_sizes(stylesheet(a.baseline))
    cur, unresolved = standard_font_sizes(stylesheet(a.rev))

    where = a.rev or "working tree"
    print(f"baseline {a.baseline}: {sum(base.values())} Standard font-size declarations")
    print(f"{where}: {sum(cur.values())} Standard font-size declarations")

    if unresolved:
        print("\nFAIL — token(s) used but not defined in Standard:")
        for t in sorted(unresolved):
            print(f"  {t}")
        return 1

    lost, gained = base - cur, cur - base
    accepted = 0
    for bag, is_gain in ((lost, False), (gained, True)):
        for (sel, val), n in list(bag.items()):
            if is_accepted(sel, val, is_gain):
                del bag[(sel, val)]
                accepted += n
    if accepted:
        print(f"{accepted} accepted delta(s) applied (see ACCEPTED in this file)")
    if a.verbose:
        for (sel, val), n in sorted(cur.items()):
            print(f"  {val:<12} {sel}")

    if not lost and not gained:
        print("\nPASS — Standard resolves identically to the pre-Enlarged baseline"
              + (f", with {accepted} accepted delta(s)." if accepted else "."))
        return 0

    print(f"\nFAIL — Standard has moved ({sum(lost.values())} lost, "
          f"{sum(gained.values())} gained).")
    print("A '+' whose selector also appears as '-' is the count=1 bug: an "
          "Enlarged value written into the Standard block.")
    for (sel, val), n in sorted(lost.items()):
        print(f"  - {val:<12} {sel}")
    for (sel, val), n in sorted(gained.items()):
        print(f"  + {val:<12} {sel}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
