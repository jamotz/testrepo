#!/usr/bin/env python3
"""Turn Jack's drinks catalog into the app's drink products.

Source (reference/origins/product info/):
  - WA_Drinks_IA_Condensed.xlsx   the filter IA + the rules sheet
  - WA_Drinks_50_Product_List_Source_Inspired_Unique_Descriptions.xlsx
                                  the 50 products

  There is also a ..._Final_CBG_Fix.xlsx. Don't use it: the two files are
  identical except for the Description and Source columns, the CBG data it is
  named for is the same in both, and 17 of its 50 descriptions are truncated
  mid-word. The Unique_Descriptions file is the same catalog with full copy.

Filter path (from the IA): Drinks -> cannabinoid branch (THC / CBD / Blend)
-> type (Drink / Shot / Seltzer / Sorbet / Honey). Same first level as
pre-rolls, so the same bubble component serves both.

  sub  = THC / CBD / Blend   (column D, the sheet's own cannabinoid decision)
  sub2 = Drink / Shot / Seltzer / Sorbet / Honey

Lifestyle is the sheet's Strain Type column renamed - see LIFESTYLE below.
Column D and column E agree on CBD (7 rows each), so the bijection holds with
no special case.

Run: python3 reference/origins/hifi-build/gen_drinks.py
"""
import os, re, sys, zipfile
from html import unescape as unesc

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/"
                    "WA_Drinks_50_Product_List_Source_Inspired_Unique_Descriptions.xlsx")

from xlsxread import read_cells

LIFESTYLE = {"Sativa": "discovery", "Sativa Hybrid": "adventurous", "Hybrid": "social",
             "Indica Hybrid": "unwind", "Indica": "nightlife", "CBD": "holistic"}

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


def photo_for(row, unknown):
    """Type decides the vessel; flavour decides its colour. Seltzers are the
    exception - the two cans differ by size, not colour, so size picks."""
    typ, flav, size = row["F"].strip(), unesc(row["C"]).strip(), row["G"].strip()
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


# ---- Serving size. Column H states the dose in several shapes:
#        "10mg THC / 100mg package"          -> 10 per serving, 100 per package
#        "10mg THC + 10mg CBD / 10 servings" -> 20 per serving, x10 for the package
#        "1 can (2.5mg THC / 5mg CBD)"       -> the whole can is one serving
#      The tile shows serving/total, so a one-serving product returns no total
#      and keeps the plain size pill - the same rule edibles and pre-rolls use.
PKG_RE  = re.compile(r"([\d.]+)\s*mg[^/]*/\s*([\d.]+)\s*mg\s*package", re.I)
SERV_RE = re.compile(r"^(.*?)/\s*(\d+)\s+servings", re.I)
MG_RE   = re.compile(r"([\d.]+)\s*mg")


def dose(cell):
    """-> (serving mg, package mg or None). None means a single serving."""
    cell = cell.strip()
    m = PKG_RE.search(cell)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = SERV_RE.match(cell)
    if m:
        per = sum(float(x) for x in MG_RE.findall(m.group(1)))
        return per, per * int(m.group(2))
    per = sum(float(x) for x in MG_RE.findall(cell))
    return (per, None) if per else (None, None)


def esc(s):
    return unesc(s).replace('"', '\\"').replace("&", "&amp;")


# ---- Two rows are still on the sheet's previous 14-column layout ----
# The catalog gained a "Serving Size" column at H, which pushed THC/CBD/Other/
# Price/Description/Source/Ratio one to the right. The last two rows were
# appended before that and never moved, so for them H is THC mg, I is CBD mg,
# K is the price and L is the source note. Every value except the serving size
# is recoverable; the serving size simply isn't in those rows, so those two
# products state no dose rather than being given an invented one.
LEGACY_MAP = {"I": "H", "J": "I", "K": "J", "L": "K", "M": "L", "N": "M", "O": "N"}


def is_legacy(row):
    """A real Serving Size always names a unit; the legacy rows hold a bare
    number there because that cell is actually THC mg."""
    return "mg" not in row.get("H", "").lower()


def cols(row):
    """Address a row canonically whichever layout it is on."""
    if not is_legacy(row):
        return row
    out = dict(row)
    out["H"] = ""                                   # no serving size on these
    for new, old in LEGACY_MAP.items():
        out[new] = row.get(old, "")
    return out


def check_columns(rows):
    bad = []
    for i, r in enumerate((cols(x) for x in rows), 2):
        if r["D"].strip() not in ("THC", "CBD", "Blend"):
            bad.append("row %d: cannabinoid category %r" % (i, r.get("D")))
        if r["E"].strip() not in LIFESTYLE:
            bad.append("row %d: strain type %r" % (i, r.get("E")))
        if r["F"].strip() not in ("Drink", "Shot", "Seltzer", "Sorbet", "Honey"):
            bad.append("row %d: type %r" % (i, r.get("F")))
        if not re.match(r"^\$[\d.]+$", r.get("L", "")):
            bad.append("row %d: price %r" % (i, r.get("L")))
        if r.get("H") and dose(r["H"])[0] is None:
            bad.append("row %d: unreadable serving size %r" % (i, r.get("H")))
        # the pre-roll sheet came back once with every description clipped
        if r.get("M", "").rstrip().endswith(("...", "…")):
            bad.append("row %d: description is truncated (%r)" % (i, r["M"][-38:]))
        for col in "ABCDEFGLM":
            if not r.get(col):
                bad.append("row %d: column %s empty" % (i, col))
    if bad:
        print("gen_drinks: sheet layout changed - refusing to emit:", file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


FEEL = {"discovery":   ["Creative", "Focused", "Uplifted"],
        "adventurous": ["Energetic", "Focused", "Uplifted"],
        "social":      ["Giddy", "Chatty", "Happy"],
        "unwind":      ["Relaxed", "Sleepy", "Body High"],
        "nightlife":   ["Euphoric", "Giddy", "Buzzed"],
        "holistic":    ["Calm", "Clear-Headed", "Relaxed"]}


def main():
    rows = [r for r in read_cells(XLSX)[1:] if r.get("A")]
    check_columns(rows)

    out, unknown, legacy = [], set(), []
    for i, raw in enumerate(rows):
        r = cols(raw)
        if is_legacy(raw):
            legacy.append(unesc(raw["B"]).strip())
        name, brand = unesc(r["B"]).strip(), unesc(r["A"]).strip()
        br, st, typ = r["D"].strip(), r["E"].strip(), r["F"].strip()
        size = r["G"].strip()
        life = LIFESTYLE[st]
        img = photo_for(r, unknown)
        serving, total = dose(r["H"])
        price = float(r["L"].lstrip("$"))
        thc, cbd = float(r.get("I") or 0), float(r.get("J") or 0)
        ratio = unesc(r.get("O", "")).strip()

        # THC is milligrams here, not a percentage. cannList() renders p.thc as
        # "%" unless a potency string is present, so state it the way edibles do.
        extra = 'pot:"%g mg THC",' % thc if thc else ""
        if cbd:
            extra += 'cbdv:%g,cbdu:" mg",' % cbd
        if cbd and cbd >= thc:
            extra += "cbd:1,"
        if ratio:
            extra += 'ratio:"%s",' % esc(ratio)
        # mg is the serving, tot the package - the tile reads "10mg / 100mg"
        if serving:
            extra += "mg:%g," % serving
        if total and total != serving:
            extra += "tot:%g," % total

        out.append(
            ' {t:"drink",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
            'thc:%g,%ssub:"%s",sub2:"%s",st:"%s",f:["%s"],sale:0,'
            'r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
            % (esc(name), esc(brand), img, price, size, price, size,
               thc, extra, br, typ, esc(st), life,
               round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
               '","'.join(FEEL[life]), esc(unesc(r["C"]).strip()),
               esc(r["M"].strip())))

    print("\n".join(out))
    import collections
    print("%d drinks - %s" % (len(out), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(collections.Counter(
            (r["D"] + " - " + r["F"]) for r in rows).items()))), file=sys.stderr)
    print("photos: %s" % dict(collections.Counter(
        re.search(r'img:"([^"]*)"', o).group(1) for o in out)), file=sys.stderr)
    if legacy:
        print("gen_drinks: %d row(s) still on the pre-Serving-Size layout, read via "
              "LEGACY_MAP and emitting no dose: %s" % (len(legacy), ", ".join(legacy)),
              file=sys.stderr)
    if unknown:
        print("gen_drinks: no photo rule for type(s): %s" % ", ".join(sorted(unknown)),
              file=sys.stderr)


if __name__ == "__main__":
    main()
