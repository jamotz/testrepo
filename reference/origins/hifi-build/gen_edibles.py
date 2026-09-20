#!/usr/bin/env python3
"""Turn Jack's edibles files into the app's edible products.

Sources (reference/origins/product info/):
  - Edible_Filter_Architecture_v2.xlsx  -> the filter IA (levels + effect tiles)
  - WA_Edibles_By_Brand_Final_Curated_Cannabinoid_Serving_Totals.xlsx
      -> the 50 products, prices, and a SERVING and TOTAL mg for every
         cannabinoid plus Servings Per Package (Jack, 2026-09-20)

Filter path per the IA (Jack confirmed the THC drill-down):
  Edibles -> category  (THC Edibles / CBD Edibles / THC Dominant / CBD Dominant / Balanced)
    THC Edibles -> extraction (Distillate / Live Resin / Rosin / Live Rosin) -> strain
    everything else -> effect tile (Pain Relief, Relax, Focus, Unwind, ...)

Packaging: the sheet states it outright now. Every row carries
"<CANNABINOID> Serving mg" and "<CANNABINOID> Total mg" for THC/CBD/CBN/CBG and
a "Servings Per Package" — so nothing here derives a dose, and the old note
about 10 mg servings / 100 mg totals is retired as an assumption. It happens to
be true of all 50 rows today; the point is that the app no longer relies on it.

This replaced a sheet with a single "Other mg" column, which could not express
a product carrying CBD *and* CBN. Prices come from the sheet.

Run: python3 reference/origins/hifi-build/gen_edibles.py
"""
import os, re, sys, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/WA_Edibles_By_Brand_Final_Curated_Cannabinoid_Serving_Totals.xlsx")

def read_rows(path):
    z = zipfile.ZipFile(path); names = z.namelist()
    ss = []
    if "xl/sharedStrings.xml" in names:
        x = z.read("xl/sharedStrings.xml").decode("utf-8")
        ss = [re.sub(r"<[^>]+>", "", m) for m in re.findall(r"<(?:x:)?si>(.*?)</(?:x:)?si>", x, re.S)]
    sheet = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml", n))[0]
    sh = z.read(sheet).decode("utf-8"); rows = []
    for r in re.findall(r"<(?:x:)?row[^>]*>(.*?)</(?:x:)?row>", sh, re.S):
        cells = []
        for c in re.findall(r"<(?:x:)?c[^>]*/>|<(?:x:)?c[^>]*>.*?</(?:x:)?c>", r, re.S):
            # place each cell by its column letter — Excel omits empty cells
            # entirely, so appending in document order silently shifts columns
            ref = re.search(r'r="([A-Z]+)\d+"', c)
            if ref:
                col = 0
                for ch in ref.group(1): col = col * 26 + ord(ch) - 64
                while len(cells) < col - 1: cells.append("")
            t = re.search(r't="(\w+)"', c)
            ins = re.search(r"<(?:x:)?is>(.*?)</(?:x:)?is>", c, re.S)
            v = re.search(r"<(?:x:)?v>(.*?)</(?:x:)?v>", c)
            if ins: cells.append(re.sub(r"<[^>]+>", "", ins.group(1)))
            elif v: cells.append(ss[int(v.group(1))] if t and t.group(1) == "s" else v.group(1))
            else: cells.append("")
        rows.append(cells)
    return rows

rows = read_rows(XLSX)
hdr = rows[0]
# pad short rows, and drop the sheet's "=== SECTION ===" separators
# Re-assert the sheet's layout on every run and refuse to emit rather than
# emit shifted data. A reader that mishandles empty cells shifts whole rows and
# still looks plausible - see design-decisions.md, "The sheet was never broken,
# the reader was".
CANNABINOIDS = ["THC", "CBD", "CBN", "CBG"]
REQUIRED = (["Brand", "Product Name", "Edible Type", "Category", "Extraction",
             "Lifestyle", "Effect Filter", "Cannabinoid Combo", "Ratio (Tile)"]
            + ["%s %s mg" % (c, w) for c in CANNABINOIDS for w in ("Serving", "Total")]
            + ["Servings Per Package", "Flavor", "Description",
               "WA Retail Price (USD)"])
missing = [c for c in REQUIRED if c not in hdr]
if missing:
    sys.exit("gen_edibles: sheet is missing column(s): %s" % ", ".join(missing))

recs = [dict(zip(hdr, r + [""] * (len(hdr) - len(r))))
        for r in rows[1:]
        if len(r) > 3 and r[0].strip() and not r[0].startswith("===")]

# ---- photos: 3 variants per form, chosen by the product name ----
# The sheet's Flavor column doesn't track the names, so the name is the source
# of truth here (Jack: "flavor doesn't matter, apply the one that looks closest").
GUMMY = [(("blackberry","marionberry","elderberry"), "ed_gum_purple"),
         (("huckleberry","raspberry"),               "ed_gum_red"),
         (("peach","pear","pineapple"),              "ed_gum_orange")]
CANDY = [(("green apple","pear"),                    "ed_hard_green"),
         (("cherry","strawberry","watermelon","blue raspberry"), "ed_hard_red"),
         (("mango","lemon","pineapple","peach"),      "ed_hard_yellow")]
CHOC  = [(("dark","espresso","raspberry"),           "ed_choc_dark"),
         (("milk","peanut butter","sea salt caramel"),"ed_choc_milk"),
         (("cookies & cream","cookies and cream"),   "ed_choc_white")]
BAKED = [(("brownie",),                              "ed_baked_brownie"),
         (("crispy","rice"),                         "ed_baked_rice")]
CAP_ALT = ["ed_cap_brown", "ed_cap_white", "ed_cap_yellow"]

def pick(table, name, default):
    n = name.replace("&amp;", "&").lower()
    for words, key in table:
        if any(w in n for w in words): return key
    return default

def photo(etype, name, i):
    if etype == "Gummies":    return pick(GUMMY, name, "ed_gum_red")
    if etype == "Hard Candy": return pick(CANDY, name, "ed_hard_red")
    if etype == "Chocolate":  return pick(CHOC,  name, "ed_choc_milk")
    if etype == "Baked Goods":return pick(BAKED, name, "ed_baked_cookie")  # cookies get the cookie
    return CAP_ALT[i % len(CAP_ALT)]                                       # capsules rotate

def flavour_of(name):
    """The flavour is in the name; the Flavor column is not reliable."""
    n = name.replace("&amp;", "&")
    for w in ("Cookies & Cream","Sea Salt Caramel","Peanut Butter","Double Chocolate",
              "Chocolate Chip","Oatmeal Raisin","Snickerdoodle","Fudge Brownie",
              "Blue Raspberry","Green Apple","Dark Chocolate","Milk Chocolate",
              "Marionberry","Elderberry","Huckleberry","Blackberry","Raspberry",
              "Strawberry","Watermelon","Pineapple","Espresso","Cherry","Mango",
              "Peach","Lemon","Pear"):
        if w.lower() in n.lower(): return w
    return "Unflavored"   # the capsules; an empty taste chip renders blank

# effect / strain -> the app's six lifestyles (drives card colour + badge)
LIFE_EFFECT = {"Pain Relief":"holistic","Relax":"holistic","Focus":"discovery","Unwind":"unwind",
               "Sleep":"unwind","Giggly":"social","Calm":"holistic","Chill":"unwind",
               "Creative":"discovery","Balanced":"social","Deep Sleep":"unwind","Happy":"social"}
# The sheet's Lifestyle column, renamed (Jack, 2026-08-12): Sativa, Sativa
# Hybrid, Hybrid, Indica Hybrid, Indica = Discovery, Adventurous, Social,
# Unwind, Nightlife; CBD = Holistic. This sheet only uses three of the six.
LIFE_STRAIN = {"Sativa":"discovery","Sativa Hybrid":"adventurous","Hybrid":"social",
               "Indica Hybrid":"unwind","Indica":"nightlife","CBD":"holistic"}
# effect -> the three "Feelings" chips on the product page
FEEL = {"Pain Relief":["Relief","Calm","Clear"],"Relax":["Relaxed","Calm","Mellow"],
        "Focus":["Focused","Clear","Uplifted"],"Unwind":["Relaxed","Mellow","Calm"],
        "Sleep":["Sleepy","Heavy","Relaxed"],"Giggly":["Giddy","Social","Uplifted"],
        "Calm":["Calm","Balanced","Clear"],"Chill":["Mellow","Relaxed","Calm"],
        "Creative":["Creative","Uplifted","Clear"],"Balanced":["Balanced","Calm","Giddy"],
        "Deep Sleep":["Sleepy","Heavy","Calm"],"Happy":["Giddy","Uplifted","Social"]}
FEEL_STRAIN = {"Sativa":["Uplifted","Energized","Focused"],"Hybrid":["Balanced","Giddy","Relaxed"],
               "Indica":["Relaxed","Sleepy","Calm"]}

# Brands merged on 2026-09-11, when deriving the Brands facet from the catalog
# showed one brand under two spellings. That merge was made in the sheets AS
# WELL AS the app specifically so a regeneration could not undo it - and then
# this sheet arrived with "Constellation Cannabis" again, which re-split the
# facet 6/6 and took the catalog from 42 brands back to 43. Normalising here
# too means an upload cannot reintroduce it: the sheet is still the source for
# everything else, this is only the one rename it keeps losing.
BRAND_MERGE = {"Constellation Cannabis": "Constellation", "Swift": "Swifts"}

def esc(s): return s.replace('"', '\\"')

out = []
for i, r in enumerate(recs):
    etype, cat = r["Edible Type"], r["Category"]
    name   = r["Product Name"]
    flavor = flavour_of(name)          # derived; the sheet's Flavor column is unreliable
    effect = r["Effect Filter"]
    strain = r["Lifestyle"]                      # sheet calls Sativa/Hybrid/Indica "Lifestyle"
    combo, ratio = r["Cannabinoid Combo"], r["Ratio (Tile)"]
    srv = float(r["Servings Per Package"] or 0)
    if srv <= 0:
        sys.exit("gen_edibles: %s has no Servings Per Package" % name)

    # Serving AND total, per cannabinoid, both read from the sheet. The sheet
    # asserts total == serving x servings; check it rather than trusting it,
    # because a row that breaks the relationship would otherwise render a
    # bubble that silently disagrees with the serving line beside it.
    serving, total = {}, {}
    for c in CANNABINOIDS:
        sv = float(r["%s Serving mg" % c] or 0)
        tv = float(r["%s Total mg" % c] or 0)
        if not sv and not tv:
            continue
        if abs(tv - sv * srv) > 0.01:
            sys.exit("gen_edibles: %s %s total %g != serving %g x %g servings"
                     % (name, c, tv, sv, srv))
        serving[c], total[c] = sv, tv

    # Order the chips the way the combo names them, so "THC:CBD:CBN" reads
    # THC, CBD, CBN left to right. "THC Only"/"CBD Only" name one.
    order = [c for c in combo.replace(" Only", "").split(":") if c in serving]
    for c in CANNABINOIDS:                      # anything the combo forgot to name
        if c in serving and c not in order:
            order.append(c)
    if not order:
        sys.exit("gen_edibles: %s states no cannabinoid at all" % name)

    # can: the one place an edible's cannabinoid numbers live. [serving, total]
    # per cannabinoid, in combo order. The tile shows the totals, the size slot
    # shows the serving; neither is stored twice.
    can = "can:{%s}," % ",".join('%s:[%g,%g]' % (c, serving[c], total[c]) for c in order)
    thc = serving.get("THC", 0)
    cbd = serving.get("CBD", 0)
    main = order[0]                              # what the serving line names
    pack = "100 mg"                              # one package size across the shelf
    # anything carrying more than straight THC is a Holistic product, whatever the
    # strain or effect would otherwise suggest
    if combo != "THC Only":
        life = "holistic"
    else:
        life = LIFE_STRAIN.get(strain, "social") if cat == "THC Edibles" else LIFE_EFFECT.get(effect, "social")
    feels = FEEL_STRAIN.get(strain, ["Balanced","Calm","Giddy"]) if cat == "THC Edibles" else FEEL.get(effect, ["Balanced","Calm","Giddy"])
    # Only "THC Edibles" rows carry a Lifestyle on the sheet. The rest are the
    # CBD/Dominant/Balanced categories, which are Holistic - so they read "CBD"
    # on the strain axis, keeping strain and lifestyle one-to-one for the
    # settings toggle. This used to fall back to "Hybrid" for any row with THC
    # in it, which invented a strain the sheet never stated.
    st = strain if cat == "THC Edibles" else "CBD"
    sub2 = r["Extraction"] if cat == "THC Edibles" else effect
    p = float(r["WA Retail Price (USD)"])   # real WA retail, straight from the sheet
    out.append(
        ' {t:"edible",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],mg:%g,srv:%g,%s%s'
        'sub:"%s",sub2:"%s"%s,etype:"%s",main:"%s",combo:"%s",ratio:"%s",'
        'st:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(name), esc(BRAND_MERGE.get(r["Brand"], r["Brand"])),
           photo(etype, name, i), p, pack, p, pack,
           serving[main], srv, ("cbd:1," if cbd and cbd >= thc else ""), can,
           cat, sub2, (',sub3:"%s"' % strain if cat == "THC Edibles" else ""), etype,
           main, combo, ratio, st, life,
           round(4.0 + (i % 10) * 0.1, 1), 5 + (i * 5) % 34,
           '","'.join(feels), flavor, esc(r["Description"])))

print("\n".join(out))
