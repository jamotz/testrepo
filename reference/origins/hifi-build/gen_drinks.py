#!/usr/bin/env python3
"""Turn Jack's drinks catalog into the app's drink products.

Source (reference/origins/product info/):
  - WA_Drinks_IA_Condensed.xlsx   the filter IA + the rules sheet
  - WA_Drinks_50_Product_List_Cannabinoid_Serving_Totals_Normalized.xlsx
                                  the 50 products (Jack, 2026-09-20)

That normalised sheet replaced one that stated the dose as PROSE in a single
"Serving Size" column, in eight different shapes -- "10mg THC / 100mg package",
"10mg THC + 10mg CBD / 10 servings", "1 can (2.5mg THC / 5mg CBD)" and so on.
Parsing it worked for 47 of 50 rows and quietly produced wrong numbers for the
rest: the single-serve cans had their THC and CBD summed into one figure, and
three rows contradicted themselves outright. It now carries a SERVING and a
TOTAL column per cannabinoid plus Servings Per Package, exactly like the
edibles sheet, so nothing here derives a dose from prose any more.

Filter path (from the IA): Drinks -> cannabinoid branch (THC / CBD / Blend)
-> type (Drink / Shot / Seltzer / Sorbet / Honey). Same first level as
pre-rolls, so the same bubble component serves both.

  sub  = THC / CBD / Blend   (the sheet's own cannabinoid decision)
  sub2 = Drink / Shot / Seltzer / Sorbet / Honey

Lifestyle is the sheet's Strain Type column renamed - see LIFESTYLE below.

COLUMNS ARE ADDRESSED BY NAME, NOT BY LETTER. The previous version hard-coded
letters, and when the sheet gained a column every field after it shifted one to
the right. That was patched with a LEGACY_MAP translating the two rows still on
the old layout -- a workaround that would have had to grow with every future
column. Resolving the header row to letters on each run costs nothing and makes
an inserted column a non-event; an inserted column that is also RENAMED still
fails loudly, below, rather than emitting shifted data.

Run: python3 reference/origins/hifi-build/gen_drinks.py
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/"
                    "WA_Drinks_50_Product_List_Cannabinoid_Serving_Totals_Normalized.xlsx")

from xlsxread import read_cells
from html import unescape as unesc

LIFESTYLE = {"Sativa": "discovery", "Sativa Hybrid": "adventurous", "Hybrid": "social",
             "Indica Hybrid": "unwind", "Indica": "nightlife", "CBD": "holistic"}

CANNABINOIDS = ["THC", "CBD", "CBN", "CBG", "CBC"]
REQUIRED = (["Brand", "Product Name", "Flavor", "Cannabinoid Category", "Strain Type",
             "Type", "Size", "Cannabinoid Combo", "Ratio (Tile)"]
            + ["%s %s mg" % (c, w) for c in CANNABINOIDS for w in ("Serving", "Total")]
            + ["Servings Per Package", "WA Retail Price", "Description"])

# ---- Photos. Jack supplied 11 shots: three bottle colours, four shot colours,
#      two can sizes, one sorbet and one honey. One flat photo per type would
#      have made all 20 drinks identical, so colour is chosen from the flavour.
#
# Ordered longest-idea-first: the first rule whose text appears in the flavour
# wins, so "grapefruit" must precede "grape", "blue raspberry" precede
# "raspberry", and "peach" precede "apple" (Apple Peach reads as a peach).
COLOR_RULES = [
    ("blue raspberry", "blue"), ("blueberry", "blue"), ("acai", "blue"),
    ("grapefruit", "orange"),                       # before "grape"
    ("peach", "orange"),                            # before "apple"
    ("orange", "orange"), ("mango", "orange"), ("tropical", "orange"),
    ("root beer", "orange"), ("cola", "orange"),
    ("blackberry", "red"), ("huckleberry", "red"), ("raspberry", "red"),
    ("strawberry", "red"), ("watermelon", "red"), ("fruit punch", "red"),
    ("cherry", "red"), ("grape", "red"), ("pink", "red"), ("berry", "red"),
    ("apple", "yellow"), ("pineapple", "yellow"), ("lemon", "yellow"),
    ("lime", "yellow"), ("citrus", "yellow"), ("ginger", "yellow"),
    ("chamomile", "yellow"), ("agave", "yellow"), ("mojo", "yellow"),
    ("cucumber", "yellow"), ("honey", "yellow"),
]

# Which colours each type actually has a photo for, and what to fall back to.
# Bottles have no blue, so a Blueberry Lemonade bottle reads red like the other
# berries rather than borrowing a shot glass.
BOTTLE = {"red": "dr_bottle_red", "orange": "dr_bottle_orange", "yellow": "dr_bottle_yellow"}
SHOT   = {"blue": "dr_shot_blue", "orange": "dr_shot_orange",
          "red": "dr_shot_red", "yellow": "dr_shot_yellow"}
FALLBACK = {"blue": "red"}          # bottles only


def colour_of(flavour):
    f = flavour.lower()
    for word, col in COLOR_RULES:
        if word in f:
            return col
    return "yellow"


def photo_for(r, unknown):
    """Type decides the vessel; flavour decides its colour. Seltzers are the
    exception - the two cans differ by size, not colour, so size picks."""
    typ, flav, size = r["Type"], unesc(r["Flavor"]), r["Size"]
    if typ == "Sorbet":
        return "dr_sorbet"
    if typ == "Honey":
        return "dr_honey"
    if typ == "Seltzer":
        return "dr_can_16" if size.startswith("16") else "dr_can_12"
    col = colour_of(flav)
    if typ == "Shot":
        return SHOT[col]
    if typ == "Drink":
        return BOTTLE[FALLBACK.get(col, col)]
    unknown.add(typ)
    return "dr_bottle_orange"


def esc(s):
    return unesc(s).replace('"', '\\"').replace("&", "&amp;")


def num(v):
    v = (v or "").strip()
    return float(v) if v not in ("", "-") else 0.0


FEEL = {"discovery":   ["Creative", "Focused", "Uplifted"],
        "adventurous": ["Energetic", "Focused", "Uplifted"],
        "social":      ["Giddy", "Chatty", "Happy"],
        "unwind":      ["Relaxed", "Sleepy", "Body High"],
        "nightlife":   ["Euphoric", "Giddy", "Buzzed"],
        "holistic":    ["Calm", "Clear-Headed", "Relaxed"]}


def load():
    """-> [row-by-header-name], having proved the sheet is the shape we expect."""
    raw = read_cells(XLSX)
    head = {(v or "").strip(): k for k, v in raw[0].items() if (v or "").strip()}
    missing = [c for c in REQUIRED if c not in head]
    if missing:
        sys.exit("gen_drinks: sheet is missing column(s): %s" % ", ".join(missing))
    rows = []
    for src in raw[1:]:
        if not (src.get(head["Brand"]) or "").strip():
            continue
        rows.append({name: (src.get(letter) or "").strip() for name, letter in head.items()})
    return rows


def check(rows):
    """Refuse to emit rather than emit something plausible and wrong."""
    bad = []
    for i, r in enumerate(rows, 2):
        if r["Cannabinoid Category"] not in ("THC", "CBD", "Blend"):
            bad.append("row %d: cannabinoid category %r" % (i, r["Cannabinoid Category"]))
        if r["Strain Type"] not in LIFESTYLE:
            bad.append("row %d: strain type %r" % (i, r["Strain Type"]))
        if r["Type"] not in ("Drink", "Shot", "Seltzer", "Sorbet", "Honey"):
            bad.append("row %d: type %r" % (i, r["Type"]))
        if not re.match(r"^\$[\d.]+$", r["WA Retail Price"]):
            bad.append("row %d: price %r" % (i, r["WA Retail Price"]))
        if num(r["Servings Per Package"]) <= 0:
            bad.append("row %d: servings per package %r" % (i, r["Servings Per Package"]))
        # the pre-roll sheet came back once with every description clipped
        if r["Description"].rstrip().endswith(("...", "…")):
            bad.append("row %d: description is truncated (%r)" % (i, r["Description"][-38:]))
        for col in ("Brand", "Product Name", "Flavor", "Size", "Cannabinoid Combo", "Description"):
            if not r[col]:
                bad.append("row %d: column %r empty" % (i, col))
    if bad:
        print("gen_drinks: sheet layout changed - refusing to emit:", file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


def doses(r):
    """-> (ordered cannabinoid list, {c: serving}, {c: total}, servings).

    The sheet asserts total == serving x servings; check it rather than trust
    it, because a row that breaks the relationship renders a bubble that
    silently disagrees with the serving line beside it. The sheet this replaced
    contained three such rows."""
    name = r["Product Name"]
    srv = num(r["Servings Per Package"])
    serving, total = {}, {}
    for c in CANNABINOIDS:
        sv, tv = num(r["%s Serving mg" % c]), num(r["%s Total mg" % c])
        if not sv and not tv:
            continue
        if abs(tv - sv * srv) > 0.01:
            sys.exit("gen_drinks: %s %s total %g != serving %g x %g servings"
                     % (name, c, tv, sv, srv))
        serving[c], total[c] = sv, tv
    # Order the chips the way the combo names them, so "THC:CBD:CBN" reads THC,
    # CBD, CBN left to right. "THC Only"/"CBD Only" name one.
    order = [c for c in r["Cannabinoid Combo"].replace(" Only", "").split(":") if c in serving]
    for c in CANNABINOIDS:                      # anything the combo forgot to name
        if c in serving and c not in order:
            order.append(c)
    if not order:
        sys.exit("gen_drinks: %s states no cannabinoid at all" % name)
    return order, serving, total, srv


def main():
    rows = load()
    check(rows)

    out, unknown = [], set()
    for i, r in enumerate(rows):
        name, brand = unesc(r["Product Name"]), unesc(r["Brand"])
        size = r["Size"]
        life = LIFESTYLE[r["Strain Type"]]
        order, serving, total, srv = doses(r)
        main_c = order[0]                        # what the serving line names
        price = float(r["WA Retail Price"].lstrip("$"))

        # can: the one place a drink's cannabinoid numbers live. [serving,
        # total] per cannabinoid, in combo order. The tile's bubbles show the
        # totals, the size slot shows the serving; neither is stored twice.
        can = "can:{%s}," % ",".join("%s:[%g,%g]" % (c, serving[c], total[c]) for c in order)
        # No thc: field. It used to hold MILLIGRAMS, which the THC % facet then
        # read as a percentage - a 100 mg bottle sorted and filtered as "High
        # (20%+)". Edibles state no thc for the same reason, so drinks now sit
        # out that facet too and are found by the mg-per-serving Size facet
        # instead. `cbd` still flags the CBD-dominant ones for "Only CBD".
        cbd_flag = "cbd:1," if serving.get("CBD", 0) >= max(serving.get("THC", 0), 0.01) else ""
        ratio = r["Ratio (Tile)"]

        out.append(
            ' {t:"drink",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
            'mg:%g,srv:%g,%s%ssub:"%s",sub2:"%s",main:"%s",combo:"%s",ratio:"%s",'
            'st:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
            % (esc(r["Product Name"]), esc(r["Brand"]), photo_for(r, unknown),
               price, size, price, size,
               serving[main_c], srv, cbd_flag, can,
               r["Cannabinoid Category"], r["Type"], main_c,
               r["Cannabinoid Combo"], esc(ratio),
               esc(r["Strain Type"]), life,
               round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
               '","'.join(FEEL[life]), esc(r["Flavor"]), esc(r["Description"])))

    print("\n".join(out))

    import collections
    print("%d drinks - %s" % (len(out), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(collections.Counter(
            (r["Cannabinoid Category"] + " - " + r["Type"]) for r in rows).items()))),
        file=sys.stderr)
    print("photos: %s" % dict(collections.Counter(
        re.search(r'img:"([^"]*)"', o).group(1) for o in out)), file=sys.stderr)
    print("THC per serving: %s" % dict(sorted(collections.Counter(
        num(r["THC Serving mg"]) for r in rows).items())), file=sys.stderr)
    print("servings per package: %s" % dict(sorted(collections.Counter(
        num(r["Servings Per Package"]) for r in rows).items())), file=sys.stderr)
    if unknown:
        print("gen_drinks: no photo rule for type(s): %s" % ", ".join(sorted(unknown)),
              file=sys.stderr)


if __name__ == "__main__":
    main()
