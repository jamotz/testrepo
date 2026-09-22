# Origins App — Project Handoff

**Last updated:** 2026-09-22 · branch `claude/accessibility-handoff-review-dhabtz`
**Live prototype:** https://claude.ai/artifact/YVnSR6tsChLJoyZrABAT4j — **Version 46**, built at `232e7b4`

> Both of these address the same artifact and either works as `url=`:
> `claude.ai/artifact/YVnSR6tsChLJoyZrABAT4j` (what the tool returns now) and
> `claude.ai/code/artifact/ff102055-8262-4b48-a681-8d77f802c968` (the older
> form this file carried for weeks). A republish through the old form comes
> back labelled with the new one — that is the **same** artifact, not a second
> one. Confirmed 2026-09-17 by listing: one *Origins — App Prototype*, 🌿,
> version 27 → 28. Don't "fix" a mismatch here by publishing without `url=`.

Hi-fi clickable prototype of the **Origins** cannabis retail app, built for Jack
Motzkin's UX portfolio case study. Everything is a single self-contained HTML
file assembled from a source file plus image assets.

---

## Where this sits

The **portfolio website** (`site/`, Astro) is the overall project. Origins is one
case study inside it, and this prototype is what its case page will show. The
root `HANDOFF.md` covers the site; this folder covers the app.

**The `main` branch is unrelated.** It holds old coursework — Jupyter notebooks,
`firstpython.py` — and none of this project. GitHub shows it by default, so a
browse that "can't find the files" is almost always looking at `main`. All work
lives on the `claude/*` branches.

**Only the branch named at the top of this file is current.** Superseded
branches stay on origin and look plausible — `sz8jwv` predates the pre-rolls and
every Account screen, and `4b84p7` stops before the deals, the calendar and
everything after. `os7hx4` is the most recent of these and the easiest to
mistake for current: it holds every screen and reads as complete, and it is
behind by exactly the phone-bezel fix. Check this line against `git log` before
trusting a branch, and update it here when the work moves.

**They have no common ancestor with this branch** (verified 2026-09-11:
`git merge-base` returns nothing for every one of them). Git ancestry therefore
proves nothing here — "is this commit contained in the current branch" has no
answer, and `git log` alone cannot tell you whether a branch is behind or just
different. **Compare trees, not history**, and compare *files*, not commits:

```bash
CUR=origin/claude/accessibility-handoff-review-dhabtz
comm -13 <(git ls-tree -r --name-only $CUR | sort) \
         <(git ls-tree -r --name-only origin/<branch> | sort)   # files only they have
```

**Do not delete these branches without running that first.** Four of them hold
the only copy of files that are not on this branch, original source material
among them:

| Branch | Files not on this branch |
|---|---|
| `project-docs-review-todos-os7hx4` | **none** — strict subset, safe to delete |
| `project-docs-review-4b84p7` | **none** — strict subset, safe to delete |
| `project-docs-review-sz8jwv` | 6 — incl. **`Flower Product Catalog.docx`**, `WA_Mock_Concentrate_Inventory_50_with_Flavors.xlsx`, `WA_PreRolls_50_Product_List.xlsx`, three `Scent (…)` assets |
| `cloud-container-access-p7024t` | 7 — the same source files, plus build cruft |
| `portfolio-redesign-81crin` | 24 — the original `product assets/` photos |
| `handoff-reference-continue-anuqh5` | 24 — the same photos |
| `install-ui-ux-pro-max-sf4kkp` | 82 — skill fonts only, no project content |

The superseded ones are superseded as **data** — `Flower Product Catalog.docx`
was replaced by the Final pt2 catalog — but `design-decisions.md` still cites
that .docx by name as the source that stated the flower types, and this branch
does not contain it. Rescue anything worth keeping onto this branch **before**
any cleanup, rather than trusting "superseded" to mean "duplicated".

---

## Start here (new session)

```bash
git fetch origin claude/accessibility-handoff-review-dhabtz
git checkout -B claude/accessibility-handoff-review-dhabtz origin/claude/accessibility-handoff-review-dhabtz
python3 -m pip install --quiet Pillow          # recycles remove it
python3 reference/origins/hifi-build/asm_app.py
```

The build prints `wrote <path> (NNNN KB); imgs=142; markers left=0` and a `WARN`
line for any asset it can't resolve. If you are touching Enlarged view, add:

```bash
python3 reference/origins/hifi-build/standard-guard.py        # must print PASS
``` **Containers are ephemeral — commit and
push often.**

Rendering/screenshots use the preinstalled Chromium via Playwright:
`/opt/pw-browsers/chromium-*/chrome-linux/chrome` (path moves after recycles;
`require('/opt/node22/lib/node_modules/playwright/index.js')`).

Publishing: republish to the **same artifact URL** above, or the link Jack has
already shared stops being the live one. Pass the URL as `url=` — publishing
without it mints a separate artifact. **The live link is current as of
`d50e9b9`** (**Version 40**, republished 2026-09-22). Every check was
re-run at that commit rather than assumed: `standard-guard.py` PASS 224 = 224,
`snapshot-guard.js` PASS on all 24 screens, `enlarged-check.js` 0 findings
across 4 viewports × 24 screens, `ratio.js` unchanged, `filter-audit.js`
308/308 products reachable via Brands with no missing brands.

**Both guards baseline at `fa3be8e`** — the Terpenes section is a new visible
element, so it moved stylesheet text *and* computed styles and both were
re-baselined together. They do not always track: read each file's constant.
The paragraph below is why they once differed, and is worth keeping.

**The two guards sometimes baseline at DIFFERENT commits, on purpose.**
`standard-guard.py` is still at `89136db`: the drinks change moved no
stylesheet text at all, so it passed untouched. `snapshot-guard.js` is at
`ad9a463`, because drinks moved COMPUTED styles on one screen. That is the
whole point of running both — one reads stylesheet text, the other reads what
the browser actually computes, and a data-only change shows up in exactly one
of them. Read the constants in each file, not this line.

The drinks re-baseline was checked card by card rather than reasoned about:
10 of the `shop` screen's 74 cards changed, all ten drinks, the other 64
byte-identical. The method is worth reusing — `snapshot-guard` tells you a
screen moved, not which elements, so diffing the rendered cards between the
two builds is what turns "one screen changed" into an argument.

Version 31 carries, on top of 30: **edibles state the package TOTAL in the
bubbles and the serving on the slot** ("10mg THC / Serving"), from a rebuilt
sheet that gives every cannabinoid its own Serving and Total column; the
**Filter drawer's edible Size facet is a per-serving dose** (1 / 2 / 5 / 10 mg,
all four live, replacing package sizes of which three matched nothing) with a
note saying so; and **one weight-pill colour**, the solid dark olive, on every
shelf.

Versions 29–30 carry, on top of 28: the full-screen EXIT chip clearing its own
strip (one rule, inset live again), a lifestyle chip filtering the whole shop
instead of the shelf you are standing on, and the home rows stating that they
scroll — **one affordance per mode**, a drawn grey scrollbar in Standard and,
in Enlarged, arrows in a strip *below* the row with a dash per tile between
them (orange on the tile you are on). The arrows step exactly one tile,
measured from the row's real pitch rather than a fraction of its width.

**Only the Standard bar and the Enlarged strip are on home.** The shop's
`.feedrow`, `.catcircles` and `.subcats` scroll the same way and still say
nothing; `hrow()` takes them unchanged if Jack wants them covered.

*Version 27 shipped with the Standard guard red and this line claiming
otherwise. That is fixed, and the rule it broke is at the bottom of this file —
**re-run the check before repeating the claim.***
The build is the Final/pt2 catalogs, terpene-driven
feelings and scents rendered with Jack's icon set, drinks with their IA bubbles,
the four deal flowers with bag-wide mix & match, the Deals Calendar (two-a-week
rota, running-now first), the brown title bar on every screen, the outlined
button family with one weight pill, and Advanced Settings. Since 2026-08-20 it
also carries the phone bezel taking its own unscaled width (the black frame
wraps the screen evenly at every window size), Filter in Origins U's Search
olive, and Origins U on the shop's own card — olive border, no label bar — with
Liquid Edibles and Vapes as their own categories and the Lifestyles tile on its
six colours, and Enlarged view as a token-driven accessibility layer with the full type
scale — every font-size in the app is a token, and the curve is anchored to the
one-card-across layout rather than tuned on its own, then flattened to a
near-uniform ~22px on Jack's call that legibility beats hierarchy in this mode,
then both rounds of his punch list on top of it (hours, tab bar, Filter/Sort row,
strain name at 32px, and the cart badge as option B's soft pill).
**Standard is untouched by all of it** — but that had to be *fixed*, not just
claimed: flattening the scale wrote six enlarged values into Standard for one
build (see below, and `design-decisions.md`). Bump this line whenever you
republish; it's the only way a new session can tell whether the link is behind
the branch.

Since 42f2956 it also carries the two controls Enlarged used to miss: the
product page's back button (52px, up from a hard-coded 26px) and the vape
screen's back button, whose inline `font-size` put it outside the token system
altogether (24px/52px in Enlarged, up from 14.4px/29px in both modes) — plus the
full-screen exit strip growing 48 → 68px in Enlarged so the EXIT chip stops
sitting on the mood chip bar, and the vape screen finally wearing the shop
chrome (`.sbar` + white chipbar) like every other shop page, with its four
consistency circles carrying real photos on the shop's own `.cc` ring.

**Write the hash *after* the commit exists, not the one you expect to get.** An
earlier value of this line, `4b1e0c9`, was never a commit on this branch —
`git cat-file -t` doesn't resolve it — so the line pointed at nothing.

If the publish is refused with *"hasn't viewed the latest version"*, another
session republished since. `WebFetch` the artifact URL first — it **is**
fetchable despite the claude.ai login, and it saves the full HTML locally so
you can diff the live body against your build before deciding. Only use
`force:true` if Jack says to discard the other version.

The build carries **no `<title>` tag** (it is a fragment), so the artifact takes
its name from the `title` parameter — pass `Origins — App Prototype` on every
republish or the gallery entry renames itself. Favicon 🌿; keep it, a changed
icon reads as a different tab.



---

## Working rules (Jack's, non-negotiable)

1. **Stay true to Jack's frames by default.** Deviate only when he says so.
2. **One screen at a time** — build, screenshot, get sign-off, then move on.
3. **Ask clarifying questions before building anything non-trivial.** Wrong
   guesses on structure cost real rework (see `design-decisions.md`).
4. **Never invent product data** that contradicts his sheets. Authored filler is
   fine when he's asked for it, but mark it clearly. As of 2026-08-14 almost
   nothing is authored: the generators' invented tables are gone and the sheets
   supply strain, lifestyle, potency, prices, copy and the terpenes that drive
   feelings and scents. What remains, all flagged in place:
   - the 10 Kief/RSO rows written onto the concentrate sheet — strains, types
     and terpenes copied from the flower catalog; only brand, size and copy
     composed. They **are** on the sheet and in the app (6 Kief, 4 RSO); only
     their provenance is authored
   - flower's star rating and review count (`gen_catalog_products.stable()`) —
     no sheet states them
   - the Account block in `origins-app.src.html`: Noelle's orders and reviews,
     and Seattle's opening hours
   - which four flowers carry the deal (`DEALS` in `gen_catalog_products.py`) —
     Jack named the two brands, the strains within them are a first pass
   - the deals calendar's schedule (`DEALDEF`) — seven deals on a four-week
     rota, two a week, and the edible deal's brand (Wyld). The **line-ups aren't authored**: each
     deal resolves its products from the catalog, by price rank where Jack
     described one ("the 4 cheapest", "the 5 most expensive")
   - run-out dates are generated (3–7 days after a run starts, hashed so they
     don't move between renders). `DEAL_UNTIL` pins one if Jack wants a fixed
     date
   - (nothing here any more — edible and drink feelings now come from Jack's
     uniform chart via feelmap.py; see item 4)

   **Before writing a table that assigns something per strain, check the source
   for a column that already says it.** That mistake has been made twice — once
   with lifestyle, once with terpenes.
5. **Say what isn't built, in the UI as well as here.** When *Enlarged view*
   was a placeholder it carried a "Coming soon" tag and toasted, rather than
   quietly doing nothing. It is built now (2026-08-20) and the tag is gone —
   the rule stands, the example is just retired. Origins U's *Search* pill is
   the live one: it toasts "coming soon" because there is no search behind it.

---

## Current state

**313 products** across six types:

| Type | Count | Source | Photos |
|---|---:|---|---|
| Flower | 50 | `Flower Final pt2 Product List for WA.xlsx` | by strain type ✓ |
| Concentrate | 60 | `Concentrate Final Product List for WA.xlsx` (all 60 rows, Kief and RSO included) | per consistency ✓ |
| Edible | 55 | `WA_Edibles_THC_CBD_Blend_COMPLETE_Unique_Descriptions.xlsx` | by form + name ✓ |
| Pre-roll | 60 | `Pre-roll pt2 Product List Final for WA.xlsx` | by type + pack count ✓ |
| Topical | 38 | `WA_Topicals_Regulatory_Audited_Patch_Weights_Simplified.xlsx` (sheet 2) + 3 authored | one per form ✓ |
| Drink | 50 | `WA_Drinks_Regulatory_Audited.xlsx` | by type + flavour colour ✓ |

**Three of those six sources were replaced on 2026-09-22** and the old
filenames are deleted from the branch — a generator pointed at one of them now
fails at `read_rows`, which is the intended failure. The edibles file is a
**catalogue replacement, not an edit**: 44 of its 55 products are new and 41 of
the old 50 are gone, so nothing can be matched across by name.

**Every edible, drink and topical now carries a regulatory net quantity**
(`nq` the printed declaration, `nqa` the US amount, `nqb` "Weight"/"Volume"),
shown on the product page between Details and Feelings and added up by the
cart's weight bars. Flower, pre-rolls and concentrates don't need one: their
size pill IS the regulatory weight.

**87 Holistic products**; **62 carry a cannabinoid ratio** (pre-rolls carry
none by design — see `design-decisions.md`).

**Feelings and scents come from the terpenes** on flower, concentrates and
pre-rolls (170 products) via `terpmap.py` — nothing authored. **Real per-strain
terpene profiles landed 2026-09-21** (`10a9367`): all 87 strains re-profiled
from published chemistry, written into columns L/M/N of the three product
lists. Linalool went from 1 product to 20 and humulene, ocimene, bisabolol and
nerolidol appear for the first time, so all 10 terpenes are now in play. The
rare ones sit deliberately on the low-confidence house names (Cosmic Queen,
Ginger Tea, Power, Gas Face, Zour Beltz), which have no published chemistry to
contradict. What shipped is recorded strain by strain at
<https://claude.ai/artifact/W3VwLRU77whWAKLgFBfyeC>.

**Terpenes are a property of a STRAIN, not a product row.** Eight pack variants
had drifted from their base strain — *Purple Punch 3-Pack* differed from
*Purple Punch*, *White Widow 3-Pack* from *White Widow* by a whole terpene.
Fixed, and the way to keep it fixed is to assign per strain and apply to every
row carrying it. `feelmap`-style: one decision, many rows. Edibles and
drinks still carry the old placeholders and are the remaining work.

**Flower, pre-rolls and concentrates now show a Terpenes row** (2026-09-21,
`c76ea7d`) between Details and Feelings — the three terpene names as
colour-coded bubbles, colour following aroma. It sits above Feelings and Taste
because it is their cause: `terpmap` derives both rows from exactly those three
names in that order, so the three rows read as columns. `TERPC` in the app
holds all ten colours, `tp` on the product row holds the names. Every pair
clears WCAG AA against its tint and against white.

**Topicals no longer show either row** (2026-09-21). They render a single
**"Best For"** tile naming the IA use case instead, because both rows were
derived rather than observed: `ta` was emitted as the product's FORM, so
"Taste" read *Cream* and *Roll-On*, and the three Feelings are a seven-entry
lookup from the use case, so all ten Pain Relief products said *Relief, Calm,
Clear*. `fe` is still emitted — the parked feelings work below is not
cancelled, and the row returns when real data lands. The seven use-case icons
are drawn in-app (`USES`, beside `ICONS`/`FLAVORS`), consulted after `IMG` so
supplied art would override them.

**Lifestyle is the strain, renamed** (Jack, 2026-08-12) — Sativa/Sativa
Hybrid/Hybrid/Indica Hybrid/Indica/CBD = Discovery/Adventurous/Social/Unwind/
Nightlife/Holistic, one-to-one. Every catalog states the strain, so **no
generator authors a lifestyle** — read the column, don't invent a rule. Four
generators each had their own invented rule until this landed; all four
disagreed with their sheets. Topicals are uniformly Holistic (nothing there is
psychoactive).

The **Use product type** switch in Advanced Settings swaps the two vocabularies
app-wide (2026-08-18). It is a label lookup, not a data change: `lifeLabel(key)`
is the only place a lifestyle word is printed — **use it, or your new screen
won't follow the toggle**.

Since 2026-09-11 it swaps the **glyph** too: `lifeGlyph(key, cls, alt)` prints a
plain letter — **S / SH / H / IH / I** — in place of the lifestyle logo, and is
the only place a glyph is printed, for the same reason `lifeLabel()` is the only
place a word is. **Holistic keeps its logo**: it is a cannabinoid profile, not a
strain, so it has no letter and `lifeGlyph()` falls through to the image. Seven
call sites were printing `IMG["sm_"+k]` directly before this; all now go through
the helper.

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 10 topic pages) · vape dead-end · Deals Calendar (running now, then a
month of upcoming) · Account · Loyalty Points · Account Settings · Advanced
Settings · Order History · Recommended Products · Past Reviews · About Us.

**Every frame in Jack's `hifi-final/` set is now built.** The Deals Calendar and
Advanced Settings have no frames behind them either — Jack specified both in
chat, the way the four unframed Account pages were specified. What's left is
polish and the open questions below.

**The visual language settled on 2026-08-18** and is worth reading in
`design-decisions.md` before adding a control:

- **Buttons are outlined** — coloured border, white interior, coloured text.
  Filter and Origins U's Search share one olive; Sort/Continue/Logout orange. A
  **solid fill now means the primary action** (Add to Cart, Checkout, the hero).
- **One weight pill everywhere** — outlined olive for a size you could pick,
  solid olive for the one you are on, tinted chip for serving/total, which is a
  fact rather than a choice.
- **Every screen wears the brown `.sbar` title bar.**
- **Cards are the shop's product tile** — white, 1.5px `#E1DBCD` border, 12px
  radius, one shadow. Origins U's tiles joined it on 2026-08-20, dropping a
  `#D9A87C` peach that was in no other screen. They keep one departure: no
  label bar (the name is olive text under the photo) and an `--olive` border,
  since with the bar gone the border is what carries the colour.

---

## Immediate next steps

1. ~~**`standard-guard.py` is FAILING on the current tip**~~ — **FIXED
   2026-09-17.** It was red from `5f66ce8` for six days while this file said all
   four guards were green; nothing had re-run it. `BASELINE` is now `5f66ce8`
   and the guard is green at 220 = 220.

   The re-baseline was the whole fix, and it was deliberate, not a way to get to
   green: 0 lost, 6 gained, no selector on both sides — **not** the `count=1`
   signature. All six gains were `.lglyph`, an element that did not exist before
   `5f66ce8` added the strain letters, and a new element needs sizes. Still
   validated against the fault: `8be0ad6` and `e67f341` both still exit 1.

   The six are now `--lglyph-*` tokens rather than hard-coded literals, so the
   "every font-size is a token" invariant holds again — see `architecture.md`
   for why they are their own family and not part of the `--fs-*` curve.

   **Two claims written here on 2026-09-11 were wrong. Both are worth keeping
   as a caution, because both sounded right:**

   - ~~"Three of the six have no Enlarged override … the letters stay Standard-
     sized while the screen doubles, the back button again."~~ **No.** Each
     `.lglyph` replaces a lifestyle *logo*, and it is sized to that image, not
     to the type curve. `.chip`, `.fcard .fbadge` and `.oc.life` grow **because
     their images grow** (`.chiplg` 16→20.5, `fbadge img` 24→31, `.lifeglyph`
     28→36); `.pimg .life`, `.educard .edulife` and `.feelchip` hold **because
     their images hold** — those three have no `#scr.enlarged` rule either.
     `5f66ce8` got this right. Measured on a build, both modes, 254 elements:
     the letter matches its twin everywhere. *Whether those three **images**
     should grow in Enlarged is a separate, older question about how far the
     mode reaches into decoration — it predates the letters and is not this.*
   - ~~"They are literals not tokens, which is *why* the guard counted them."~~
     **No.** The guard resolves tokens back to literals and counts declarations
     either way. The count rose because six declarations were *added*.
     Tokenising changed nothing about the guard, and the re-baseline would have
     been needed regardless. Two independent things that read as one.

   *The standing rule that actually broke here is written down twice in this
   file:* **a verification claim is only as good as the script behind it —
   re-run the check yourself before repeating the claim.** That applies to a
   diagnosis as much as to a green run: the first bullet above was written from
   reading the stylesheet, and one build would have disproved it.

   **Republished 2026-09-17 at `fea857b`, Version 28**, and the live-link line
   above now names it.

2. **General touch-ups** — Jack is doing a pass across the app, screen by
   screen. Home, shop, cart, Origins U and the account screens have each been
   through a round (see `design-decisions.md` for what was decided and why).
3. **Enlarged view is built and is now a token layer, not a zoom.** The
   `--enlarge: 1.25` / `zoom` description that stood here is retired — it was
   replaced on 2026-08-20 and the rest of this file, `architecture.md` and
   `design-decisions.md` now describe the token system. In short: every
   `font-size` in the app is a `--fs-*` token whose Standard value is the
   original literal; `#scr.enlarged` overrides the tokens once. To make the mode
   stronger or weaker, **move the token values, and re-run the guard** — don't
   add per-rule font sizes, and don't reach for `zoom` again (why it lost is in
   `design-decisions.md`).

   **Run the Standard guard after every change to this layer:**

   ```bash
   python3 reference/origins/hifi-build/standard-guard.py     # PASS / FAIL, exit 0 / 1
   ```

   It resolves every token back to its literal, drops every rule scoped to
   `#scr.enlarged`, and compares what's left against the stylesheet as it was
   *before any Enlarged work existed* — 214 Standard font-size declarations,
   which must match exactly. It takes about a second, needs no build, no
   browser and no assets, so there is no excuse for skipping it.

   **Both guards now baseline at `623bcf8`** (`standard-guard.py:97`, and the
   worktree recipe in `snapshot-guard.js`) — re-baselined to `c77eff1` earlier
   on 2026-09-11 and moved again to `623bcf8` the same day. **Read the constant
   in the script, not this paragraph**, which has been wrong once already. The
   pre-Enlarged anchor is retired on both. `standard-guard.py` moved off
   `cc6edad` because replacing the vape screen's grey placeholder discs with
   real photo circles deleted the `.vape .vc` rule and with it one Standard
   declaration (213 now, was 214). Deliberate visual changes are re-baselines,
   not accepted deltas. The verification `cc6edad` provided is not lost — it is
   in the git history and in `design-decisions.md` — but neither guard now
   proves anything about the Enlarged refactor, which was verified long ago.
   Both still exit 1 on `e67f341` and `8be0ad6`, the commits that carried the
   real regression, which is the check that they still work.

   **`snapshot-guard.js` was first re-baselined to `470e2b5` on 2026-09-03.** It was
   `cc6edad`; it moved when Standard started changing for reasons unrelated to
   Enlarged (the vape screen taking the shop chrome). That is a real change to
   what Standard renders, so it is not an accepted delta — those are for
   differences that move nothing on screen — and the documented answer to a
   legitimate Standard change is to re-baseline deliberately. The cost, stated
   plainly: this guard now measures against the last verified state, not against
   pre-Enlarged. ~~`standard-guard.py` still runs against `cc6edad` with zero
   exceptions, 214 = 214~~ — **no longer true, and it was contradicted by the
   paragraph directly above it for a week.** Both guards moved off `cc6edad` on
   2026-09-11; neither anchors to pre-Enlarged any more. Re-baseline again only
   after a run whose every difference you have read and can name.

   **The baseline is a commit, not a captured file** — the guard reads its
   source straight out of git. `cc6edad`, the last commit before the Enlarged
   work began (verified: zero `--fs-*` tokens, zero `#scr.enlarged` rules), was
   that commit until 2026-09-11; it is `623bcf8` now.
   This matters more than it looks: a baseline captured from the *current* file
   would certify whatever regression is already sitting in it. If you ever
   rewrite this guard, keep that property.

   **A legitimate change to Standard will fail this guard, and should.** If Jack
   asks for a different size in *normal* view, Standard has moved and the guard
   says so. Re-baseline deliberately: point `BASELINE` at the commit that made
   the change, in a commit that says what moved and why. **Don't** widen the
   guard, add per-selector exceptions, or drop declarations from the comparison
   to get it green — that trades the whole check for the one change in front of
   you. Telling the two cases apart from the FAIL output: a regression shows
   Standard taking recognisably *enlarged* values (22px, 24px, 1.8rem) on
   selectors you never meant to touch, usually several at once; a deliberate
   change shows the value you intended, on the selector you intended, usually
   alone. When it isn't obvious, assume regression.

   **The heavier check is `snapshot-guard.js`** — run it before publishing, and
   after any change that could move layout rather than just type. It walks all
   24 screens in Chromium and compares **computed** styles (5,582 elements),
   which catches what the text guard cannot: a rule that wins on specificity, an
   `#scr.enlarged` rule that lost its class scope, a size set from JS, or a
   token that moves a layout property. It needs a build of both sides, so budget
   ~2 min each:

   ```bash
   SP=<scratchpad>
   git worktree add -f $SP/base 623bcf8   # keep in step with snapshot-guard.js
   python3 -m pip install --quiet Pillow
   python3 reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/cur.html
   python3 $SP/base/reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/base.html
   node reference/origins/hifi-build/snapshot-guard.js $SP/base.html $SP/cur.html
   ```

   `asm_app.py` writes to the same scratchpad path both times — **move the first
   output before building the second** or the second silently overwrites it.

   It carries a short **accepted-deltas** list: differences from the baseline
   that are known and intended, each with a reason, and the run prints how many
   it applied so they stay visible. Today there are 5 — `.fbtn` and `.edusearch`
   taking `min-height:47px` from `--control-height` in the token refactor
   (visually inert: both already rendered at 50px), and the `span.advsoon`
   "Coming soon" tag removed when Enlarged shipped. **Never add an entry to turn
   a red run green** — an entry means someone checked that the change to
   Standard was deliberate. If the list starts growing, the baseline is wrong,
   not the app.

   **Both of those guard Standard.** Neither says anything about whether
   Enlarged itself works. Two more cover that side:

   ```bash
   node reference/origins/hifi-build/ratio.js         <built.html>   # the curve
   node reference/origins/hifi-build/enlarged-check.js <built.html>  # the mode
   ```

   **Neither Enlarged check sees the full-screen chrome.** `enlarged-check.js`
   walks elements inside `.s[data-s="<screen>"]`, and `#fsexit`, the status bar
   and the island all live *outside* that root — so the exit chip covering the
   mood chip bar in Enlarged went unnoticed by all four checks and was found by
   looking at a screenshot. If you widen anything here, widen this: the chrome
   layer has no coverage at all.

   `ratio.js` prints each element as a percentage of its card in both modes —
   the check for whether the curve is still anchored to its container.
   `enlarged-check.js` turns the mode on and walks all 24 screens looking for
   the toggle failing to round-trip, page-level horizontal scrolling
   (WCAG 1.4.10), content spilling past the app frame, and tap targets under
   24px (WCAG 2.5.8). Note its carousel exception: deal rows and chip rows
   scroll horizontally, so their children sit outside the frame legitimately —
   without that exception the spill check reports five screens of false
   positives.

   It sweeps **4 viewports** (1440×900 and 1366×768 framed, 393×852 and
   320×568 full screen), because a single viewport proves very little here: the
   app always lays out at 452px and is transform-scaled by `k`, so what a reader
   actually gets is `design px × k`.

   Verified on a build of `1ca26e4`: round-trip clean at every viewport (name
   14→32→14px, nav 9→15→9, tab icon 21→34→21), no horizontal overflow, nothing
   spilling the frame, **0 findings across 4 viewports × 24 screens**.

   **The relative gain is scale-invariant — exactly ×2.32 on body text at every
   viewport, framed and full.** Both modes scale by the same `k`, so Enlarged
   always delivers its full benefit; what changes is the absolute size. Framed
   mode floors at `k=0.5`, so on a 1280×600 window Standard body renders at
   4.8px and Enlarged at 11.0px — the mode is working, the stage is just small.
   **Review the mode in full screen**, where a real phone puts it: 393×852 full
   gives 8.3 → 19.1px, 320×568 full gives 6.7 → 15.6px.

   The check separates a target under 24px **by design** (a real defect) from
   one that only falls under once `k` shrinks it (a property of the preview
   stage). Don't conflate them — measuring `getBoundingClientRect` alone reports
   9 false findings at these viewports.

   **The regression it exists to catch has already happened once.** Flattening
   the Enlarged type scale used `re.sub(..., count=1)` on six semantic tokens.
   `count=1` replaces the *first* match in the file, which is `:root` — the
   **Standard** block — not the `#scr.enlarged` one below it, so Standard
   silently took the enlarged values (`--text-body` 13px → 22px, `--text-nav`
   9px → 22px, and four more): the nav bar, product card text, weights and
   filter labels all read as enlarged in normal view. Fixed in `25c88fe` by
   anchoring each rewrite on the actual `:root{…}` and `#scr.enlarged{…}` spans
   instead of on match order. **Any script that edits one of the two blocks must
   anchor on the block, never on ordinal position.**

4. **Feelings on edibles and drinks — DONE** (`a40ec64`, 2026-09-21). Jack
   supplied `Origins_Uniform_Lifestyle_Feelings_Edibles_Drinks.xlsx`: three
   standardised Feelings per lifestyle, and for Holistic a set chosen by the
   prominent secondary cannabinoid (CBD / CBG / CBN). Read by **`feelmap.py`**,
   shared by both generators.

   **Edit the chart, not the code.** `feelmap.py` reads the .xlsx, so adding a
   `Holistic / CBC` row gives both shelves that rule with no code change. A
   Holistic product whose secondary has no row stops the build with a message
   naming the row to add — it never guesses.

   The chart uses exactly the 14 feeling terms Jack's icon set provides, so both
   shelves now render his art with **zero** fallbacks to generated SVGs. Before
   this, ten terms had no icon (edibles: Balanced, Clear, Giddy, Heavy, Relief;
   drinks: Body High, Chatty, Clear-Headed, Energetic, Giddy) and the mismatch
   was visible next to flower.

   It replaced **two private FEEL tables** — `gen_edibles.py` had FEEL +
   FEEL_STRAIN, `gen_drinks.py` its own FEEL — which is how one uniform idea
   became 14 words on one shelf and 12 on the other. One uniform rule deserves
   one reader.

   ~~**Open decision Jack has not made.**~~ **SETTLED 2026-09-21** (`8721092`).
   Drinks were keying lifestyle off strain alone while edibles made any product
   with a secondary cannabinoid Holistic, leaving 17 drinks on the wrong side.
   Jack settled it **in the sheet, per product** rather than by a rule: column E
   is now `Lifestyle` and states the value outright, he moved 9 of the 17, and
   left 8 THC-dominant blends alone (each has at least twice the THC of its
   secondary). Holistic drinks 7 → 16, all resolving to chart rows.

   `gen_drinks.py`'s private LIFESTYLE table is gone — the mapping lives once in
   `feelmap.LIFE_OF`, so the sheet and the chart cannot disagree about what
   Holistic means. Strain is derived back for the settings toggle: the column IS
   the strain for the five strain lifestyles, Holistic takes `CBD`.

   **Watch column D on that sheet.** The same upload relabelled 26 rows from
   `THC` to `THC Only` while leaving `CBD` as `CBD`, which taken verbatim would
   rename one Drinks bubble and leave the set asymmetric (THC Only / CBD /
   Blend). The partition never changed (26/17/7, matching the combo), so
   `category()` in `gen_drinks.py` normalises it back to the documented IA. Three
   other rows in that column were a REAL correction — Sweet Watermelon,
   Agave Lime MAX and Blue Raspberry MAX moved THC → Blend — and pass straight
   through. A relabel and a recategorisation arriving in one column is worth
   telling apart before taking either.

   **Taste chips: closed on every shelf.** Topicals stated their form, drinks
   and edibles restated their own product name; flower, pre-rolls and
   concentrates keep theirs because `terpmap.py` gives them real descriptors.
   See design-decisions.md, "A taste chip has to say something the title does
   not".

5. **Four sub-bubbles have photos but no products**: `Rosin Coins`,
   `Full Melt Hash`, `Distillate Syringe`, `Dab Applicator` — one level down
   inside Rosin, Hash and Distillate. Re-checked 2026-09-11: still 0 products
   each. Every category itself is stocked, **Kief (6) and RSO (4) included** —
   an earlier note claiming those two were empty was wrong (Jack, 2026-08-17;
   see `design-decisions.md`).

6. ~~**`body.fs .fsexit` is declared twice and the notch handling is dead
   code**~~ — **FIXED 2026-09-17.** One rule now, carrying
   `top:calc(9px + env(safe-area-inset-top,0px))`.

   It was not only a notch bug, which is why it could be fixed without a
   handset: at the hard-coded `top:14px` the 35px chip measured **49px against
   its own 48px strip**, overhanging by 1px on every device. Now 9 → 44 against
   48 (clearance +4), and 9 → 59 against 68 in Enlarged (+9). Measured at
   393×852 and 320×568 by `fsexit-probe.js`, committed beside the other checks.

   **Still open, and now a smaller question:** `env(safe-area-inset-*)` is 0 in
   headless Chromium, so what a *notched* iPhone does is still unverified — but
   it is a live value now rather than dead code. Worth one look on a real
   handset.

7. **Open questions for Jack**, each flagged where it lives:

   - The **four deal flowers** are his brands but my strain picks (`DEALS` in
     `gen_catalog_products.py`, one line each to swap). Asked and explained
     2026-09-22; still unanswered.
   - ~~**The edibles sheet has no price column**~~ — **CLOSED 2026-09-22.**
     The COMPLETE sheet carries `WA Retail Price (USD)` with a Pricing Notes
     tab naming each brand's anchor, rule and source. `PRICE_LADDER` is
     deleted, not kept as a fallback: a stale price table fails silently.
   - ~~**Pre-rolls get one 1 oz bar**~~ — **CLOSED 2026-09-22.** Jack: "Flower
     includes plain flower pre rolls and flower. Concentrate includes
     concentrate and infused/trifecta pre-rolls. They are not separate
     entities." Five buckets now, and the pre-roll shelf has no bar of its own:
     `limitKey()` sends its 35 plain rows to flower and its 25 Infused/Trifecta
     rows to concentrate, which is also what WAC and the CCRS guidance say.
   - **Topicals still get their own 72 oz bar.** The rule puts liquid topicals
     in the *same* bucket as liquid edibles, and says nothing clear about a
     solid balm or a bath soak. Open, and deliberate.
   - **Three topicals are not in any sheet** — `Deep Relief Roll-On`,
     `Rescue Balm`, `Night Recovery Cream`, authored 2026-08-10 and living in
     `AUTHORED` in `gen_topicals.py`. Their net quantities are borrowed from
     the per-form convention in Jack's own data and asserted against it on
     every run. Adding them to the sheet retires the block.

8. **Four sub-bubbles still have photos but no products** — see item 5.

   *The Filter-pill contrast question is closed* (2026-08-20): Filter now uses
   Origins U's Search olive `#555624` at 7.66:1, clearing AA and AAA. The
   `#5C7540` drop-in that was earmarked for it is no longer needed.

### Done in this pass (2026-08-17 → 18)

| | |
|---|---|
| Home deals | Four flowers nominated in `DEALS`; 2-for-$50 mixes and matches across the whole bag; brand tiles matched to the product tiles; Torus replaced Freddy's; a See All card per row opens the whole deal |
| Deals Calendar | New screen from both hero buttons — seven deals on a four-week rota, two a week, **running now** then a month of upcoming, each with a generated run-out date and a product dropdown |
| Drinks | Bubble path built from `WA_Drinks_IA_Condensed.xlsx`; the size facet lists real volumes derived from the catalog (`SIZES.drink`, overwritten at runtime just after the catalog — the literal in `SIZES` is dead, so read the override, not the constant). Dose is per serving on the tile, totals in the bubbles |
| Kief / RSO | The "no products" note was wrong — the sheet has all 60 concentrate rows |
| Chrome | Brown title bar on every screen; trolley icon over Cart; "Your Cart"; Origins U photos wired to images the build actually embeds |
| Buttons | The outlined family, one weight pill app-wide, hero type at the app's own size, Logout matched to Account Settings |
| Advanced Settings | New screen: **Use product type**, **Enlarged view** and **Reduce motion** — all three working (Enlarged view landed 2026-08-20) |

*Size as a navigation step was considered and rejected* (Jack, 2026-08-12):
size lives in the product tile, not the filter path. Don't re-propose it.

### Done since (2026-08-20 → 09-02) — the accessibility pass

| | |
|---|---|
| Enlarged view | Rebuilt from `zoom:1.25` into a **token layer**: 49 distinct font sizes, 204 declarations, all `--fs-*` tokens, overridden once in `#scr.enlarged`. Reflow rules sit beside them — one card across, names wrap, metadata stacks |
| The curve | Anchored to the container, not chosen in isolation: a card goes 198→409px, so a type curve tuned on its own shrinks everything *relative to its card*. `ratio.js` measures each element as a % of its card in both modes |
| Flattening | Then flattened to a near-uniform ~22px (Jack's call: in this mode legibility beats hierarchy). Hierarchy now comes from weight and colour, not size |
| Punch list r1 | Lifestyle badge, bell/gear rings, the Advanced Settings switch itself (not just its hit box), Origins U title/Search/tiles |
| Punch list r2 | Hours spans sized to their content, tab bar (icons 34px, label 15px, one line), Filter/Sort back on one row at 20px, strain name 32px |
| Cart badge | Option B, the soft pill — rounded rect with a white keyline, lifted clear of the trolley. Enlarged only; Standard keeps its 16px circle |
| Standard regression | Six enlarged values leaked into `:root` via `re.sub(count=1)`; fixed by anchoring on the blocks. See next steps §2 |

*`zoom` was tried first and lost* (2026-08-20): it magnified decoration along
with content, grew every gap equally whether it needed it, and shrank the
layout's coordinate space exactly when the content got bigger. Don't re-propose
it.

### Done since (2026-09-03 → 09-11)

| | |
|---|---|
| Brands facet | `BRANDS` is gone; `brandList()` derives the options from `P`. **308 of 308 products reachable** (was 15), **0 catalog brands unoffered** (was 43). Why it is a function and not a `const`, and the three name collisions merged at the source — 45 brands → **42** — are in `design-decisions.md` |
| Capsules | Edible form → "Capsules / Softgels" matched 0 products; the catalog says `etype:"Capsules"` and only the label disagreed. Now matches its 10 |
| Filter audit | `filter-audit.js` drives the app's own `match()` over every drawer option and reports the count behind each — the only way a dead facet surfaces, since it looks identical to an empty shelf. `drawer-test.js` beside it |
| Product back button | `.pihead .pihback` joined the Enlarged target-size enumeration (`06d2673`). It was the one control under WCAG 2.5.8's 24px, at 23px on a 393×852 phone. **The open item that said "not fixed — Jack's call" was stale for a week** |
| Vapes circle | `vape` registered as an image key (`8c18000`); the shop circle had been rendering its `noimg` fallback since the shelf existed. Vape consistency circles got real photos, normalised for how much of the ring each fills |
| Lifestyle ring | The selection ring goes black — the only colour that clears all six lifestyle colours |

*The lesson from the back button is about **enumerations**, not that button:*
most of Enlarged is a token every component inherits, but `--target-size` is a
**list**, and a list is a thing you can be left off. Anything sized by a
hard-coded `width`/`height` rather than a token has to be named somewhere, and
naming is where things get forgotten.

---

## Repo layout

```
reference/origins/
├── hifi-build/
│   ├── origins-app.src.html      ← THE app (markup + CSS + JS + product data)
│   ├── asm_app.py                ← build: inlines fonts + images -> one HTML file
│   ├── gen_catalog_products.py   ← flower products from the .xlsx
│   ├── gen_drinks.py             ← drinks from the .xlsx + drinks IA
│   ├── terpmap.py                ← terpenes -> feelings + scents
│   ├── ratio.js                  ← Enlarged guard: each element as a % of its card
│   ├── standard-guard.py         ← Enlarged guard: Standard must not move (run it)
│   ├── snapshot-guard.js         ← Enlarged guard: same, from computed styles
│   ├── enlarged-check.js         ← does Enlarged itself work (overflow/targets)
│   ├── lglyph-probe.js           ← the strain letters, both modes (nothing else sees them)
│   ├── fsexit-probe.js           ← the full-screen EXIT chip vs its strip (ditto)
│   ├── mood-probe.js             ← what a lifestyle chip does to the filter state
│   ├── rowarrow-probe.js         ← home row affordances + the tile-height trap
│   ├── filter-audit.js           ← counts products behind every filter option
│   ├── drawer-test.js            ← drives the Brands clamp / type scoping
│   ├── xlsxread.py               ← the one xlsx reader they all share
│   ├── gen_concentrates.py       ← concentrates from the .xlsx
│   ├── gen_edibles.py            ← edibles from the .xlsx + filter IA
│   ├── gen_prerolls.py           ← pre-rolls from the .xlsx
│   ├── gen_topicals.py           ← topicals from the .xlsx (+ 3 authored rows)
│   ├── gen_holistic_logo.py      ← generates the Holistic lifestyle logo
│   └── origins-case.src.html     ← case-study page, built by asm_case.py
├── product info/                 ← Jack's source data (.docx/.xlsx)
├── assets/
│   ├── product assets/           ← photos by category (Concentrate has sub-folders)
│   ├── Lifestyle logos/          ← the six lifestyle logos
│   ├── Various Brand Logos/      ← Royal Tree, Saints, Torus, Skord (+ Freddy's, unused)
│   └── origins logos/, scents assets/, …
├── hifi-final/                   ← Jack's Figma frames (the source of truth)
└── HANDOFF.md                    ← older handoff, still has useful frame notes
site/                             ← the Astro portfolio site (the umbrella project)
docs/                             ← you are here
```

`origins-app.src.html` is one big file by design — it assembles into a single
portable HTML artifact with no external requests.

---

## Regenerating product data

Each generator prints rows to stdout; splice them over the matching block in
`origins-app.src.html`, then rebuild. The rows for one type are contiguous.

```bash
python3 reference/origins/hifi-build/gen_topicals.py > /tmp/topicals.txt
# replace the {t:"topical"…} lines in origins-app.src.html, then:
python3 reference/origins/hifi-build/asm_app.py
```

**Flower regenerates like everything else now** — the old "don't regenerate
flower" warning is retired. It existed because photos were drawn sequentially
from a shuffled pool, so inserting one product reshuffled every photo after it.
Photos are now chosen by hashing the strain name against a pool scoped to that
strain's type, so a strain keeps its photo across rebuilds and row order doesn't
matter.

**Regenerating flower is in fact how you change the deal line-up**: `DEALS` in
`gen_catalog_products.py` decides which four rows carry `sale:1`, and the
generator refuses to emit if a nomination stops matching exactly one row, or if
a nominated eighth is at or under the $25 deal price.

---

## Gotchas

- **The artifact URL is stable.** Republish with `url=` to keep it; a new path
  mints a new URL.
- **Empty cells shift rows two different ways.** Excel omits some empty cells
  entirely (a reader appending in document order shifts every column after a
  blank — this is why a sheet once parsed with `Cannabinoid Combo` landing in
  `Effect Filter`), *and* writes others self-closing, `<c r="E2" s="29"
  t="str"/>`. A cell regex that tries the open-tag branch before the
  self-closing one reads `<c …/>` as an open tag and swallows the next cell's
  value — the same shift, but silent even when you address by column letter.
  Address by letter **and** match the self-closing branch first. Copy the reader
  in `gen_prerolls.py`; the other three now match it.
- **The sheets use TWO cell encodings, and a replacement written for one
  silently matches nothing in the other.** Topicals writes
  `<c t="inlineStr"><is><t>`; Concentrate writes namespaced `<x:c t="str"><x:v>`.
  The first pass of the brand merge changed **0 of 4 cells** in Concentrate and
  reported success. Same family as the self-closing-cell hazard above. **Dry-run
  any sheet edit and check the counts against a `grep` done up front**, and edit
  the worksheet XML inside the zip rather than round-tripping through a library,
  which rewrites styles and docProps too.
- **Sectioned sheets carry `=== SECTION ===` rows.** Filter them out or they
  parse as products.
- **Don't trust a "this sheet is malformed" note without re-checking it.** The
  pre-roll catalog was documented for two days as having columns that didn't
  match its own header. It doesn't — that was the self-closing-cell bug above,
  and `gen_prerolls.py` had been written to compensate for it. Both are fixed
  and the emitted products never changed. If a sheet looks shifted, parse it
  with `xml.etree` first and compare before writing code around it.
- **Don't publish with missing photos.** The build still succeeds when assets are
  gone (WARN + blank tiles) — check the WARN lines before publishing.
- **Jack sometimes uploads an older `origins-app.src.html`** alongside his data
  files via the GitHub web UI, which silently reverts work. Diff before rebasing;
  it happened once and was caught.
- **Copy address can't be verified from a build container.** The About Us copy
  control tries `navigator.clipboard` and falls back to an offscreen textarea +
  `execCommand`; both branches are tested locally (including with the Clipboard
  API removed and with `writeText` rejecting), but which one the *published*
  artifact takes depends on the iframe's permission policy, which isn't visible
  from outside the frame. The published page can't be clicked from here — it's
  behind claude.ai auth and WebFetch only reads HTML. Ask Jack to tap it once.
  If the toast shows the address instead of "Address copied", both branches were
  blocked and the fallback is to render the address in a selectable `<input>`.
- **Git drops empty directories.** Every asset folder has a `README.md` so the
  structure survives deleting its photos (learned the hard way with `Rosin/`).
- **A lifestyle word is only ever printed by `lifeLabel(key)`.** Print `FEEL[k]`
  directly and Advanced Settings' *Use product type* switch won't reach your
  screen. The Guide Me wizard is the exception that proves it: its lifestyle
  words are *wordmark images*, so each option carries a text twin that CSS swaps
  in.
- **A fixed height inside a `.dealrow` stretches every product tile in it.**
  Flex rows default to `align-items:stretch`, so a brand or See All card with
  its own height drags the tiles up to meet it — that shipped once, 40px too
  tall. Let them stretch; only the brand row, which has no product tile to set
  the height, is measured.
- **A hidden screen measures zero.** Anything that sizes itself from a rendered
  element has to run when its screen is actually on (`nav()`), not at load.
- **`.s` and `.empty` are global CSS classes** — `.s{display:none}` in
  particular. Namespace anything new (the size sheet uses `fs*`), or it vanishes
  silently.
- **Build takes ~2 min** since the WebP encode; run it in the background.
- **`re.sub(pattern, repl, css, count=1)` edits the wrong block.** The Standard
  tokens (`:root`) come *first* in the stylesheet and the Enlarged overrides
  (`#scr.enlarged`) second, so a first-match rewrite aimed at Enlarged lands on
  Standard. Anchor on the block's own `{…}` span. This shipped once; six
  Standard font sizes silently took enlarged values.
- **A tooling script that isn't committed is gone.** Containers are reclaimed,
  and `standard-guard.py`, `std_before.json`, `snapshot.js` and `coverage.js`
  were written, used, documented as required — and never added to git.
  Both have since been rewritten and committed as `standard-guard.py` and
  `snapshot-guard.js`, each deriving its baseline from **a commit** rather than
  from a captured file, so neither can be lost that way again. Commit any guard
  you write, and prefer a baseline git can regenerate over one you store.
  (Which commit has moved twice — `cc6edad` → `c77eff1` → `623bcf8`. The
  property that matters is "a commit", not the particular hash; read it from
  the script.)
- **A verification claim in these docs is only as good as the script behind
  it.** "Standard is provably untouched" was written from a snapshot run whose
  script no longer exists, and the regression above landed after it. Re-run the
  check yourself before repeating the claim.
- **The cart badge is not an icon.** It was swept into the generated
  icon-scaling pass *and* the round-1 punch list, so two rules fought over it
  and it grew to 34px, sitting on top of the trolley it belongs to. It is sized
  on its own rule now; keep it out of any bulk icon selector.
