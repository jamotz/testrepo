#!/usr/bin/env python3
"""Turn Jack's drinks catalog into the app's drink products.

Source (reference/origins/product info/):
  - WA_Drinks_IA_Condensed.xlsx   the filter IA + the rules sheet
  - WA_Drinks_Regulatory_Audited.xlsx
                                  the 50 products (Jack, 2026-09-22)

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

Lifestyle is stated by the sheet (column E) since 2026-09-21; it was derived
from Strain Type before. See LIFE_OF in feelmap.py.

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
                    "WA_Drinks_Regulatory_Audited.xlsx")

from xlsxread import read_cells
from html import unescape as unesc

# The sheet states the LIFESTYLE outright now (column E, renamed from "Strain
# Type" by Jack on 2026-09-21), using the same vocabulary as his feelings chart:
# a strain name, or "Holistic". So the mapping lives in exactly one place -
# feelmap.LIFE_OF - and the sheet and the chart cannot disagree about what
# "Holistic" means.
#
# WHY THE SHEET CHANGED: lifestyle used to be derived from the strain alone, so
# a drink carrying CBD or CBN still read as its strain while the equivalent
# EDIBLE read Holistic (gen_edibles makes any product with a secondary
# cannabinoid Holistic). 17 drinks sat on the wrong side of that. Jack did not
# apply a blanket rule - he judged them one at a time, moving 9 of the 17 and
# leaving 8 THC-dominant blends where they were. That judgement is data, which
# is why it belongs in the sheet and not in a rule here.
from feelmap import LIFE_OF, feelings_for

# A drink's strain, for the settings toggle's strain-vs-lifestyle wording. The
# sheet no longer states it separately: for the five strain lifestyles the
# column IS the strain, and a Holistic drink takes "CBD", the same value
# gen_edibles gives its Holistic rows, so strain and lifestyle stay one-to-one.
def strain_of(lifestyle):
    return "CBD" if lifestyle == "Holistic" else lifestyle

CANNABINOIDS = ["THC", "CBD", "CBN", "CBG", "CBC"]
REQUIRED = (["Brand", "Product Name", "Flavor", "Cannabinoid Category", "Lifestyle",
             "Type", "Size", "Cannabinoid Combo", "Ratio (Tile)"]
            + ["%s %s mg" % (c, w) for c in CANNABINOIDS for w in ("Serving", "Total")]
            + ["Servings Per Package", "WA Retail Price", "Description",
               "Net Qty Basis", "Net Amount (US)", "US Unit",
               "Regulatory Quantity Display"])

# The sheet names every drink after its own volume -- "Blackberry Lemonade
# 12 oz". Jack, 2026-09-22: take it out of the name, because the regulatory net
# quantity now has a line of its own on the product page and the name was
# carrying a fact twice. Only an EXACT trailing " " + the Size cell comes off,
# so a name that happens to end in a number keeps it.
def trim_size(name, size):
    tail = " " + size.strip()
    return name[:-len(tail)] if name.endswith(tail) else name

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


# Feelings come from Jack's uniform chart, shared with edibles - see feelmap.py.
# The table that used to sit here was keyed by lifestyle alone, so all 50 drinks
# collapsed to 5 triples and half its words ("Chatty", "Body High", "Buzzed")
# had no icon in Jack's set.
from feelmap import feelings_for


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


def category(r):
    """The drinks IA's first level: THC / CBD / Blend.

    The 2026-09-21 sheet relabelled this column's "THC" as "THC Only", matching
    the Cannabinoid Combo vocabulary - but left "CBD" as "CBD", so the set reads
    THC Only / CBD / Blend. Taken verbatim that renames one of the three bubbles
    on the Drinks shop screen and leaves it asymmetric with its two neighbours.
    The partition is untouched (still 26 / 7 / 17, exactly matching the combo),
    so this is a label edit, and one that looks incidental rather than intended.
    Normalised back to the documented IA here, and flagged to Jack: if he wants
    the bubble to read "THC Only", that is a deliberate IA change and this
    function is where to make it.
    """
    return {"THC Only": "THC", "CBD Only": "CBD"}.get(
        r["Cannabinoid Category"], r["Cannabinoid Category"])


def check(rows):
    """Refuse to emit rather than emit something plausible and wrong."""
    bad = []
    for i, r in enumerate(rows, 2):
        if category(r) not in ("THC", "CBD", "Blend"):
            bad.append("row %d: cannabinoid category %r" % (i, r["Cannabinoid Category"]))
        if r["Lifestyle"] not in LIFE_OF:
            bad.append("row %d: lifestyle %r" % (i, r["Lifestyle"]))
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

    # Two Sungaze seltzers differ only by volume ("... 12 oz" / "... Supernova
    # 16 oz"), so prove the trim leaves 50 distinguishable products rather than
    # discovering a collision on the shelf.
    trimmed = [(unesc(r["Brand"]), trim_size(unesc(r["Product Name"]), r["Size"]))
               for r in rows]
    dupes = {k for k in trimmed if trimmed.count(k) > 1}
    if dupes:
        sys.exit("gen_drinks: trimming the size collides these products: %s"
                 % sorted(dupes))

    out, unknown = [], set()
    for i, r in enumerate(rows):
        size = r["Size"]
        name, brand = trim_size(unesc(r["Product Name"]), size), unesc(r["Brand"])
        # The regulatory declaration, and the two numbers the cart adds up.
        # The sheet formats with Excel's TEXT(x,"0.##"), which leaves a whole
        # number wearing a trailing point; correct in a spreadsheet, wrong on a
        # product page, so it comes off here and the sheet stays uniform.
        nq  = re.sub(r"(\d)\.(?=\s)", r"\1", r["Regulatory Quantity Display"])
        nqa = num(r["Net Amount (US)"])
        nqb = r["Net Qty Basis"]
        if not nq or not nqa or nqb not in ("Weight", "Volume"):
            sys.exit("gen_drinks: %s has no usable net quantity (%r/%r/%r)"
                     % (name, nq, nqa, nqb))
        life = LIFE_OF[r["Lifestyle"]]
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

        # No `ta`. The Flavor column is already the product name - all 50 rows
        # had their flavour string contained in their own name ("Blackberry
        # Lemonade" in "Blackberry Lemonade 12 oz") - so a Taste row restated
        # the title three lines above it. photo_for() still reads Flavor for
        # the colour rules; only the chip is gone (Jack, 2026-09-21).
        out.append(
            ' {t:"drink",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
            'nq:"%s",nqa:%g,nqb:"%s",'
            'mg:%g,srv:%g,%s%ssub:"%s",sub2:"%s",main:"%s",combo:"%s",ratio:"%s",'
            'st:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],d:"%s"},'
            % (esc(name), esc(r["Brand"]), photo_for(r, unknown),
               price, size, price, size, esc(nq), nqa, nqb,
               serving[main_c], srv, cbd_flag, can,
               category(r), r["Type"], main_c,
               r["Cannabinoid Combo"], esc(ratio),
               esc(strain_of(r["Lifestyle"])), life,
               round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
               '","'.join(feelings_for(life, total, name)), esc(r["Description"])))

    print("\n".join(out))

    import collections
    print("%d drinks - %s" % (len(out), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(collections.Counter(
            (category(r) + " - " + r["Type"]) for r in rows).items()))),
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
