#!/usr/bin/env python3
"""Turn Jack's edibles catalog into the app's edible products.

Source (reference/origins/product info/):
  - WA_Edibles_THC_CBD_Blend_Expanded_CBD_Weights_Fixed.xlsx  (Jack, 2026-09-22)
      the 55 products, their net weights, and the cannabinoid mg per serving
  - Edible_Filter_Architecture_THC_CBD_Blend.xlsx
      the filter IA, which this file implements but does not read

FILTER PATH (Jack, 2026-09-22 -- this replaced the old one wholesale):

    Edibles -> Cannabinoid (THC / CBD / Blend)
            -> Product Type (Gummies, Chocolate, Hard Candy, Baked Goods, Capsules)
            -> Concentrate Type (Distillate, Rosin, Live Resin, Live Rosin)

  sub  = THC / CBD / Blend        sub2 = Product Type       sub3 = Concentrate Type

What it replaced opened on five mixed categories -- THC Edibles, CBD Edibles,
THC Dominant, CBD Dominant, Balanced -- which put a cannabinoid decision and an
effect decision on the same row of bubbles, then drilled to extraction for one
of them and to effect tiles for the other four. Lifestyle and Effect are no
longer a level at all; they are reached from the lifestyle chips and the global
filter, which is where every other shelf keeps them.

THREE THINGS THIS SHEET STATES DIFFERENTLY FROM THE ONE IT REPLACED, all
recovered here rather than assumed:

  Servings.  There is no "Servings Per Package" column. Net Amount (Metric) /
  Serving Amount (g) gives it, and it is 10 for all 55 rows -- asserted below,
  not trusted, because a row that broke it would render a package total that
  disagreed with the serving line beside it.

  The third cannabinoid.  One "Other mg" column replaced the named CBN/CBG/CBC
  pairs. Cannabinoid Combo names which one it is ("THC:CBN" -> CBN), and the
  Ratio column is checked against the two figures so a mislabelled row fails
  here instead of rendering a bubble that contradicts its own ratio.

  Price.  THE SHEET HAS NO PRICE COLUMN AT ALL. 44 of the 55 products are new,
  so there is nothing to match old prices to by name either. Rather than invent
  55 retail prices, each brand re-uses ITS OWN price ladder from the sheet this
  one replaced (recovered at 759e5ad^) -- see PRICE_LADDER. Every brand makes
  exactly one form in both sheets, and the ladder is walked in order so the
  brand keeps its price level and its spread. This is the one field in the
  catalog that is not Jack's current data; the moment the sheet carries a price
  column, delete PRICE_LADDER and read it.

Run: python3 reference/origins/hifi-build/gen_edibles.py
"""
import os, re, sys, collections

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/"
                    "WA_Edibles_THC_CBD_Blend_Expanded_CBD_Weights_Fixed.xlsx")

from xlsxread import read_cells
from html import unescape as unesc
from feelmap import feelings_for

CANNABINOIDS = ["THC", "CBD", "CBN", "CBG", "CBC"]
REQUIRED = ["Brand", "Product Name", "Product Type", "Cannabinoid Category",
            "Concentrate Type", "Lifestyle", "Effect", "Cannabinoid Combo",
            "Ratio (Tile)", "THC mg", "CBD mg", "Other mg", "Description",
            "Net Qty Basis", "Net Amount (US)", "US Unit",
            "Net Amount (Metric)", "Metric Unit", "Serving Amount (g)"]

EFORMS  = ["Gummies", "Chocolate", "Hard Candy", "Baked Goods", "Capsules"]
ECONC   = ["Distillate", "Rosin", "Live Resin", "Live Rosin"]
ECATS   = ["THC", "CBD", "Blend"]

# ---- the one field the new sheet does not carry: see the module docstring ----
# Each brand's own WA retail prices from
# WA_Edibles_By_Brand_Final_Curated_Cannabinoid_Serving_Totals.xlsx, sorted, and
# walked in order for that brand's rows. Five brands gained a row in the new
# sheet, so their ladder wraps -- which repeats one of the brand's own prices
# rather than inventing a new one.
PRICE_LADDER = {
    "Ceres":            [18, 18, 20, 22, 24, 24],
    "Constellation":    [22, 22, 24, 24, 26, 26],
    "Good Tide":        [20, 20, 24, 24, 26, 26],
    "Green Revolution": [20, 20, 22, 22, 22, 24],
    "Journeyman":       [24, 24, 28, 30, 30, 30],
    "Marmas":           [22, 22, 22, 24],
    "Pioneer Squares":  [18, 22, 22, 22],
    "Swifts":           [22, 22, 24, 24],
    "Verdelux":         [18, 18, 22, 22],
    "Wyld":             [28, 28, 28, 30],
}

# ---- photos: 3 variants per form, chosen by the product name ----
# The sheet's Flavor column doesn't track the names, so the name is the source
# of truth here (Jack: "flavor doesn't matter, apply the one that looks closest").
GUMMY = [(("blackberry", "marionberry", "elderberry"), "ed_gum_purple"),
         (("huckleberry", "raspberry"),                "ed_gum_red"),
         (("peach", "pear", "pineapple"),              "ed_gum_orange")]
CANDY = [(("green apple", "pear"),                     "ed_hard_green"),
         (("cherry", "strawberry", "watermelon", "blue raspberry"), "ed_hard_red"),
         (("mango", "lemon", "pineapple", "peach"),    "ed_hard_yellow")]
CHOC  = [(("dark", "espresso", "raspberry"),           "ed_choc_dark"),
         (("milk", "peanut butter", "sea salt caramel"), "ed_choc_milk"),
         (("cookies & cream", "cookies and cream"),    "ed_choc_white")]
BAKED = [(("brownie",),                                "ed_baked_brownie"),
         (("crispy", "rice"),                          "ed_baked_rice")]
CAP_ALT = ["ed_cap_brown", "ed_cap_white", "ed_cap_yellow"]


def pick(table, name, default):
    n = name.replace("&amp;", "&").lower()
    for words, key in table:
        if any(w in n for w in words):
            return key
    return default


def photo(etype, name, i):
    if etype == "Gummies":     return pick(GUMMY, name, "ed_gum_red")
    if etype == "Hard Candy":  return pick(CANDY, name, "ed_hard_red")
    if etype == "Chocolate":   return pick(CHOC,  name, "ed_choc_milk")
    if etype == "Baked Goods": return pick(BAKED, name, "ed_baked_cookie")
    return CAP_ALT[i % len(CAP_ALT)]                       # capsules rotate


# effect / strain -> the app's six lifestyles (drives card colour + badge)
LIFE_EFFECT = {"Pain Relief": "holistic", "Relax": "holistic", "Focus": "discovery",
               "Unwind": "unwind", "Sleep": "unwind", "Giggly": "social",
               "Calm": "holistic", "Chill": "unwind", "Creative": "discovery",
               "Balanced": "social", "Deep Sleep": "unwind", "Happy": "social"}
# The sheet's Lifestyle column, renamed (Jack, 2026-08-12): Sativa, Sativa
# Hybrid, Hybrid, Indica Hybrid, Indica = Discovery, Adventurous, Social,
# Unwind, Nightlife; CBD/Holistic = Holistic.
LIFE_STRAIN = {"Sativa": "discovery", "Sativa Hybrid": "adventurous", "Hybrid": "social",
               "Indica Hybrid": "unwind", "Indica": "nightlife",
               "CBD": "holistic", "Holistic": "holistic"}

# Brands merged on 2026-09-11 in the sheets AS WELL AS the app, so a
# regeneration could not undo it; kept here because an upload keeps losing it.
BRAND_MERGE = {"Constellation Cannabis": "Constellation", "Swift": "Swifts"}


def esc(s):
    return unesc(s).replace('"', '\\"').replace("&", "&amp;")


def num(v):
    v = (v or "").strip()
    return float(v) if v not in ("", "-") else 0.0


def load():
    """-> [row-by-header-name], having proved the sheet is the shape we expect.

    Addressed by NAME, never by letter: a reader that mishandles an empty cell
    shifts whole rows and still looks plausible (design-decisions.md, "The sheet
    was never broken, the reader was")."""
    raw = read_cells(XLSX)
    head = {(v or "").strip(): k for k, v in raw[0].items() if (v or "").strip()}
    missing = [c for c in REQUIRED if c not in head]
    if missing:
        sys.exit("gen_edibles: sheet is missing column(s): %s" % ", ".join(missing))
    rows = []
    for src in raw[1:]:
        r = {name: (src.get(letter) or "").strip() for name, letter in head.items()}
        # the sheet's "THC PRODUCTS" / "CBD PRODUCTS" banner rows carry a Brand
        # and nothing else, so require a Product Type to count as a product
        if r["Brand"] and r["Product Type"]:
            rows.append(r)
    return rows


def check(rows):
    """Refuse to emit rather than emit something plausible and wrong."""
    bad = []
    for i, r in enumerate(rows, 2):
        if r["Cannabinoid Category"] not in ECATS:
            bad.append("row %d: cannabinoid category %r" % (i, r["Cannabinoid Category"]))
        if r["Product Type"] not in EFORMS:
            bad.append("row %d: product type %r" % (i, r["Product Type"]))
        if r["Concentrate Type"] not in ECONC:
            bad.append("row %d: concentrate type %r" % (i, r["Concentrate Type"]))
        if BRAND_MERGE.get(r["Brand"], r["Brand"]) not in PRICE_LADDER:
            bad.append("row %d: no price ladder for brand %r" % (i, r["Brand"]))
        if r["Description"].rstrip().endswith(("...", "…")):
            bad.append("row %d: description is truncated (%r)" % (i, r["Description"][-38:]))
        for col in ("Product Name", "Cannabinoid Combo", "Description",
                    "Net Qty Basis", "Net Amount (US)", "US Unit",
                    "Net Amount (Metric)", "Metric Unit", "Serving Amount (g)"):
            if not r[col]:
                bad.append("row %d: column %r empty" % (i, col))
    # every brand must make exactly one form, or the price ladder is keyed wrong
    for brand, forms in collections.Counter(
            (BRAND_MERGE.get(r["Brand"], r["Brand"]), r["Product Type"]) for r in rows).items():
        pass
    bybrand = collections.defaultdict(set)
    for r in rows:
        bybrand[BRAND_MERGE.get(r["Brand"], r["Brand"])].add(r["Product Type"])
    for brand, forms in sorted(bybrand.items()):
        if len(forms) > 1:
            bad.append("brand %r now makes %s - the price ladder assumes one form"
                       % (brand, sorted(forms)))
    if bad:
        print("gen_edibles: sheet layout changed - refusing to emit:", file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


def doses(r):
    """-> (ordered cannabinoid list, {c: serving}, {c: total}, servings).

    Servings is derived, then asserted: the sheet has no servings column, so
    net weight / serving weight has to stand in for one."""
    name = r["Product Name"]
    net, per = num(r["Net Amount (Metric)"]), num(r["Serving Amount (g)"])
    if per <= 0:
        sys.exit("gen_edibles: %s has no serving amount" % name)
    srv = net / per
    if abs(srv - round(srv)) > 0.01:
        sys.exit("gen_edibles: %s net %g / serving %g = %g, not a whole number of servings"
                 % (name, net, per, srv))
    srv = float(round(srv))

    combo = r["Cannabinoid Combo"]
    named = [c for c in combo.replace(" Only", "").split(":") if c]
    # "Other mg" is whichever cannabinoid the combo names that isn't THC or CBD
    other = [c for c in named if c not in ("THC", "CBD")]
    if len(other) > 1:
        sys.exit("gen_edibles: %s names two 'other' cannabinoids (%s)" % (name, combo))
    mg = {"THC": num(r["THC mg"]), "CBD": num(r["CBD mg"])}
    if other:
        if other[0] not in CANNABINOIDS:
            sys.exit("gen_edibles: %s names unknown cannabinoid %r" % (name, other[0]))
        mg[other[0]] = num(r["Other mg"])
    elif num(r["Other mg"]):
        sys.exit("gen_edibles: %s carries Other mg but the combo names no third cannabinoid"
                 % name)

    serving = {c: v for c, v in mg.items() if v}
    order = [c for c in named if c in serving]
    for c in CANNABINOIDS:
        if c in serving and c not in order:
            order.append(c)
    if not order:
        sys.exit("gen_edibles: %s states no cannabinoid at all" % name)

    # the Ratio column is a second statement of the same numbers - check them
    # against each other so a mislabelled row fails here, not on the shelf
    ratio = r["Ratio (Tile)"].strip()
    if ratio and len(order) > 1:
        parts = ratio.split(":")
        if len(parts) == len(order):
            want = [float(x) for x in parts]
            got = [serving[c] for c in order]
            k = got[0] / want[0] if want[0] else 0
            if k and any(abs(g - w * k) > 0.01 for g, w in zip(got, want)):
                sys.exit("gen_edibles: %s ratio %s disagrees with %s"
                         % (name, ratio, dict(zip(order, got))))

    total = {c: serving[c] * srv for c in serving}
    return order, serving, total, srv


def main():
    rows = load()
    if len(rows) != 55:
        sys.exit("gen_edibles: expected 55 product rows, read %d" % len(rows))
    check(rows)

    seen = collections.Counter()
    out, servings_seen = [], collections.Counter()
    for i, r in enumerate(rows):
        brand = BRAND_MERGE.get(r["Brand"], r["Brand"])
        name  = r["Product Name"]
        etype = r["Product Type"]
        cat   = r["Cannabinoid Category"]
        conc  = r["Concentrate Type"]
        order, serving, total, srv = doses(r)
        servings_seen[srv] += 1
        main_c = order[0]

        ladder = PRICE_LADDER[brand]
        price  = float(ladder[seen[brand] % len(ladder)])
        seen[brand] += 1

        # the package size label names the MAIN cannabinoid's package total, so
        # a 25 mg/serving CBD gummy reads 250 mg rather than borrowing the THC
        # shelf's flat 100 mg. The Size facet reads can.THC, not this.
        pack = "%g mg" % total[main_c]
        can  = "can:{%s}," % ",".join("%s:[%g,%g]" % (c, serving[c], total[c]) for c in order)
        thc, cbd = serving.get("THC", 0), serving.get("CBD", 0)

        # anything carrying more than straight THC is a Holistic product,
        # whatever the strain or effect would otherwise suggest
        if r["Cannabinoid Combo"] != "THC Only":
            life = "holistic"
        elif r["Lifestyle"]:
            life = LIFE_STRAIN.get(r["Lifestyle"], "social")
        else:
            life = LIFE_EFFECT.get(r["Effect"], "social")
        st = r["Lifestyle"] if (cat == "THC" and r["Lifestyle"]) else "CBD"
        feels = feelings_for(life, total, name)

        nq  = re.sub(r"(\d)\.(?=\s)", r"\1",
                     "%s %s %s (%s %s)" % ("Net Wt." if r["Net Qty Basis"] == "Weight" else "Net Vol.",
                                           r["Net Amount (US)"], r["US Unit"],
                                           r["Net Amount (Metric)"], r["Metric Unit"]))
        out.append(
            ' {t:"edible",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
            'nq:"%s",nqa:%g,nqb:"%s",mg:%g,srv:%g,%s%s'
            'sub:"%s",sub2:"%s",sub3:"%s",etype:"%s",main:"%s",combo:"%s",ratio:"%s",'
            'st:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],d:"%s"},'
            % (esc(name), esc(brand), photo(etype, name, i), price, pack, price, pack,
               esc(nq), num(r["Net Amount (US)"]), r["Net Qty Basis"],
               serving[main_c], srv, ("cbd:1," if cbd and cbd >= thc else ""), can,
               cat, etype, conc, etype, main_c, r["Cannabinoid Combo"],
               esc(r["Ratio (Tile)"]), esc(st), life,
               round(4.0 + (i % 10) * 0.1, 1), 5 + (i * 5) % 34,
               '","'.join(feels), esc(r["Description"])))

    print("\n".join(out))
    print("%d edibles - %s" % (len(out), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(collections.Counter(
            r["Cannabinoid Category"] + " / " + r["Product Type"] for r in rows).items()))),
        file=sys.stderr)
    print("servings per package: %s" % dict(servings_seen), file=sys.stderr)
    print("photos: %s" % dict(collections.Counter(
        re.search(r'img:"([^"]*)"', o).group(1) for o in out)), file=sys.stderr)


if __name__ == "__main__":
    main()
