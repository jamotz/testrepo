#!/usr/bin/env python3
"""The uniform Feelings mapping for edibles and drinks, read from Jack's chart.

Source: reference/origins/product info/
        Origins_Uniform_Lifestyle_Feelings_Edibles_Drinks.xlsx   (Jack, 2026-09-21)

Three standardised Feelings icons per lifestyle, and for Holistic the set is
chosen by the prominent secondary cannabinoid (CBD / CBG / CBN).

WHY THIS IS A SHARED MODULE AND NOT A TABLE IN EACH GENERATOR
The chart is explicitly *uniform* across the two shelves, so two copies of it
would be two things to keep in step - and the thing this replaces was exactly
that: gen_edibles.py and gen_drinks.py each had their own FEEL table, which is
how the two shelves ended up with 14 and 12 different feeling words between
them, ten of which had no icon. One reader, one source, no drift.

It reads the .xlsx rather than restating it in Python for the same reason every
other generator here reads its sheet: editing the chart is how you change the
app. Add a "Holistic / CBC" row and both shelves pick it up with no code change.

THE CHART'S FIRST COLUMN IS HEADED "Lifestyle" BUT HOLDS STRAIN NAMES
Sativa, Sativa Hybrid, Hybrid, Indica Hybrid, Indica - plus Holistic. Origins'
own lifestyle vocabulary is Discovery / Adventurous / Social / Unwind /
Nightlife / Holistic. The two are one-to-one by Jack's 2026-08-12 naming, which
every generator already encodes; LIFE_OF below is that same bijection, written
once more here so a reader of this file can check it without opening another.
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/"
                    "Origins_Uniform_Lifestyle_Feelings_Edibles_Drinks.xlsx")

from xlsxread import read_cells

# chart's first column -> Origins' lifestyle key (Jack, 2026-08-12)
LIFE_OF = {"Sativa": "discovery", "Sativa Hybrid": "adventurous", "Hybrid": "social",
           "Indica Hybrid": "unwind", "Indica": "nightlife", "Holistic": "holistic"}

# Every lifestyle the app can assign. If the chart ever stops covering one of
# these, that is a missing rule, and a missing rule must stop the build rather
# than fall back to something invented.
REQUIRED_LIFESTYLES = set(LIFE_OF.values())


def _load():
    """-> ({lifestyle: [f1,f2,f3]}, {cannabinoid: [f1,f2,f3]} for Holistic)."""
    rows = read_cells(XLSX)
    head = None
    plain, holistic = {}, {}
    for r in rows:
        cells = {k: (v or "").strip() for k, v in r.items()}
        if cells.get("A") == "Lifestyle" and cells.get("C", "").startswith("Feeling"):
            head = True
            continue
        if not head:
            continue                                  # title + subtitle lines
        name = cells.get("A", "")
        if name not in LIFE_OF:
            continue
        feels = [cells.get(c, "") for c in ("C", "D", "E")]
        if not all(feels):
            sys.exit("feelmap: row %r does not state three feelings" % name)
        if name == "Holistic":
            sec = cells.get("B", "").strip()
            if sec in ("", "-", "—"):
                sys.exit("feelmap: a Holistic row must name its secondary cannabinoid")
            holistic[sec.upper()] = feels
        else:
            plain[LIFE_OF[name]] = feels
    missing = REQUIRED_LIFESTYLES - set(plain) - ({"holistic"} if holistic else set())
    if missing:
        sys.exit("feelmap: chart has no rule for lifestyle(s): %s" % ", ".join(sorted(missing)))
    return plain, holistic


PLAIN, HOLISTIC = _load()


def secondary(totals):
    """The prominent secondary cannabinoid: the largest non-THC total.

    Ranked by the PACKAGE total rather than by the combo's order, so "prominent"
    means what it says - a product carrying 200 mg CBG and 10 mg CBD is a CBG
    product whichever order its combo happens to name them in. Ties fall to the
    alphabetically first, which only matters if a product carries two
    cannabinoids at identical totals; none does today.
    """
    rest = sorted(((v, k) for k, v in (totals or {}).items() if k != "THC"), reverse=True)
    return rest[0][1] if rest else None


def feelings_for(life, totals, what=""):
    """The three Feelings for one product. `totals` is {cannabinoid: package mg}."""
    if life != "holistic":
        if life not in PLAIN:
            sys.exit("feelmap: no rule for lifestyle %r (%s)" % (life, what))
        return PLAIN[life]
    sec = secondary(totals)
    if sec is None:
        sys.exit("feelmap: %s is Holistic but carries no secondary cannabinoid, "
                 "so the chart cannot choose a feelings set" % (what or "a product"))
    if sec not in HOLISTIC:
        sys.exit("feelmap: %s is Holistic with %s as its prominent secondary "
                 "cannabinoid, and the chart has no Holistic/%s row. Add one to "
                 "%s rather than guessing." % (what or "a product", sec, sec,
                                               os.path.basename(XLSX)))
    return HOLISTIC[sec]


if __name__ == "__main__":
    print("plain lifestyles:")
    for k, v in sorted(PLAIN.items()):
        print("  %-12s %s" % (k, " / ".join(v)))
    print("holistic, by prominent secondary cannabinoid:")
    for k, v in sorted(HOLISTIC.items()):
        print("  %-12s %s" % (k, " / ".join(v)))
