#!/usr/bin/env python3
"""Turn Jack's edibles files into the app's edible products.

Sources (reference/origins/product info/):
  - Edible_Filter_Architecture_v2.xlsx  -> the filter IA (levels + effect tiles)
  - WA_Edibles_By_Brand_Sectioned.xlsx  -> the 50 products

Filter path per the IA (Jack confirmed the THC drill-down):
  Edibles -> category  (THC Edibles / CBD Edibles / THC Dominant / CBD Dominant / Balanced)
    THC Edibles -> extraction (Distillate / Live Resin / Rosin / Live Rosin) -> strain
    everything else -> effect tile (Pain Relief, Relax, Focus, Unwind, ...)

Packaging: one package per product — 10 mg servings, 100 mg total (the lone
CBD-only product is 25 mg CBD). Prices are authored (the sheet has none).

Run: python3 reference/origins/hifi-build/gen_edibles.py
"""
import os, re, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/WA_Edibles_By_Brand_Sectioned.xlsx")

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
        for c in re.findall(r"<(?:x:)?c[^>]*>.*?</(?:x:)?c>|<(?:x:)?c[^>]*/>", r, re.S):
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
recs = [dict(zip(hdr, r)) for r in rows[1:] if any(x.strip() for x in r)]

# ---- photos: 3 variants per edible form, picked by flavour where it reads ----
GUMMY  = {"Blackberry":"ed_gum_purple","Blue Raspberry":"ed_gum_purple",
          "Huckleberry":"ed_gum_red",   # red huckleberry — uses the red gummy photo

          "Raspberry":"ed_gum_red","Strawberry":"ed_gum_red","Cherry Lime":"ed_gum_red","Watermelon":"ed_gum_red",
          "Pineapple":"ed_gum_orange","Mango":"ed_gum_orange","Tangerine":"ed_gum_orange",
          "Blood Orange":"ed_gum_orange","Peach":"ed_gum_orange","Lemon":"ed_gum_orange","Pear":"ed_gum_orange"}
CANDY  = {"Blue Raspberry":"ed_hard_green","Pear":"ed_hard_green","Cherry Lime":"ed_hard_green",
          "Huckleberry":"ed_hard_green","Blackberry":"ed_hard_green",
          "Strawberry":"ed_hard_red","Raspberry":"ed_hard_red","Watermelon":"ed_hard_red","Blood Orange":"ed_hard_red",
          "Mango":"ed_hard_yellow","Lemon":"ed_hard_yellow","Peach":"ed_hard_yellow",
          "Pineapple":"ed_hard_yellow","Tangerine":"ed_hard_yellow","Dark Chocolate":"ed_hard_red"}
# no chocolate product carries a "Dark Chocolate" flavour, so rotate all three
CHOC_ALT = ["ed_choc_dark", "ed_choc_milk", "ed_choc_white"]
CAP_ALT  = ["ed_cap_brown", "ed_cap_white", "ed_cap_yellow"]
# baked goods were all "Cookie Bites"; rename some so the brownie and rice-crispy
# photos get used too (Jack: "rename some things to fit the variety of pictures")
BAKED_RENAME = {"Raspberry":("Brownie Bites","ed_baked_brownie"),
                "Blood Orange":("Brownie Bites","ed_baked_brownie"),
                "Peach":("Crispy Treats","ed_baked_rice"),
                "Lemon":("Crispy Treats","ed_baked_rice")}

def photo(etype, flavor, i):
    if etype == "Gummies":  return GUMMY.get(flavor, "ed_gum_red")
    if etype == "Hard Candy": return CANDY.get(flavor, "ed_hard_red")
    if etype == "Chocolate":
        return CHOC_ALT[i % len(CHOC_ALT)]
    if etype == "Capsules / Softgels":
        return "ed_cap_brown" if flavor == "Dark Chocolate" else CAP_ALT[i % len(CAP_ALT)]
    return BAKED_RENAME.get(flavor, (None, "ed_baked_cookie"))[1]

def baked_name(name, flavor):
    """Rename some Cookie Bites to Brownie Bites / Crispy Treats for variety."""
    ren = BAKED_RENAME.get(flavor)
    return name.replace("Cookie Bites", ren[0]) if ren else name

# ---- authored WA-realistic prices: base by form + extraction/formulation premium ----
BASE = {"Gummies": 18, "Chocolate": 22, "Hard Candy": 15, "Baked Goods": 20, "Capsules / Softgels": 25}
EXTRA = {"Distillate": 0, "Live Resin": 6, "Rosin": 4, "Live Rosin": 10}
def price(r):
    p = BASE.get(r["Edible Type"], 20) + EXTRA.get(r["Extraction"], 0)
    if r["Category"] != "THC Edibles":
        p += 5                       # ratio/formulated products carry a premium
    if r["Effect Filter"] == "Pain Relief":
        p += 4                       # high-mg CBD
    return p

# effect / strain -> the app's six lifestyles (drives card colour + badge)
LIFE_EFFECT = {"Pain Relief":"holistic","Relax":"holistic","Focus":"discovery","Unwind":"unwind",
               "Sleep":"unwind","Giggly":"social","Calm":"holistic","Chill":"unwind",
               "Creative":"discovery","Balanced":"social","Deep Sleep":"unwind","Happy":"social"}
LIFE_STRAIN = {"Sativa":"adventurous","Hybrid":"social","Indica":"unwind"}
# flavour -> the app's terpene list
TERP = {"Blackberry":"Fruity","Huckleberry":"Fruity","Blue Raspberry":"Fruity","Raspberry":"Fruity",
        "Strawberry":"Fruity","Watermelon":"Fruity","Pineapple":"Citrus","Mango":"Citrus",
        "Tangerine":"Citrus","Blood Orange":"Citrus","Lemon":"Citrus","Cherry Lime":"Citrus",
        "Peach":"Fruity","Pear":"Fruity","Dark Chocolate":"Earthy"}
# effect -> the three "Feelings" chips on the product page
FEEL = {"Pain Relief":["Relief","Calm","Clear"],"Relax":["Relaxed","Calm","Mellow"],
        "Focus":["Focused","Clear","Uplifted"],"Unwind":["Relaxed","Mellow","Calm"],
        "Sleep":["Sleepy","Heavy","Relaxed"],"Giggly":["Giddy","Social","Uplifted"],
        "Calm":["Calm","Balanced","Clear"],"Chill":["Mellow","Relaxed","Calm"],
        "Creative":["Creative","Uplifted","Clear"],"Balanced":["Balanced","Calm","Giddy"],
        "Deep Sleep":["Sleepy","Heavy","Calm"],"Happy":["Giddy","Uplifted","Social"]}
FEEL_STRAIN = {"Sativa":["Uplifted","Energized","Focused"],"Hybrid":["Balanced","Giddy","Relaxed"],
               "Indica":["Relaxed","Sleepy","Calm"]}

def esc(s): return s.replace('"', '\\"')

out = []
for i, r in enumerate(recs):
    etype, cat = r["Edible Type"], r["Category"]
    flavor, effect = r["Flavor"], r["Effect Filter"]
    strain = r["Lifestyle"]                      # sheet calls Sativa/Hybrid/Indica "Lifestyle"
    thc, cbd, other = float(r["THC mg"] or 0), float(r["CBD mg"] or 0), float(r["Other mg"] or 0)
    combo, ratio = r["Cannabinoid Combo"], r["Ratio (Tile)"]
    # the tile chips carry real numbers only — the cannabinoid combo and its ratio
    # live in the product name instead (Jack, 2026-08-06)
    pot  = "%g mg THC" % thc
    pack = "%g mg" % cbd if combo == "CBD Only" else "100 mg"
    cbdf = 'cbdv:%g,cbdu:" mg",' % cbd if (combo != "THC Only" and cbd) else ""
    # the third cannabinoid (CBG/CBN) — its name comes from the combo, its
    # weight from the sheet's "Other mg"
    if combo != "THC Only" and other:
        cbdf += 'othv:%g,' % other
    # anything carrying more than straight THC is a Holistic product, whatever the
    # strain or effect would otherwise suggest
    if combo != "THC Only":
        life = "holistic"
    else:
        life = LIFE_STRAIN.get(strain, "social") if cat == "THC Edibles" else LIFE_EFFECT.get(effect, "social")
    feels = FEEL_STRAIN.get(strain, ["Balanced","Calm","Giddy"]) if cat == "THC Edibles" else FEEL.get(effect, ["Balanced","Calm","Giddy"])
    st = strain if cat == "THC Edibles" else ("CBD" if thc == 0 else "Hybrid")
    sub2 = r["Extraction"] if cat == "THC Edibles" else effect
    p = price(r)
    # the combo + ratio ride on the photo as a tile overlay, so the name stays short
    name = baked_name(r["Product Name"], flavor) if etype == "Baked Goods" else r["Product Name"]
    name = name.replace("Chocolate Squares", "Chocolates")   # Jack's wording
    out.append(
        ' {t:"edible",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],mg:%g,%s%s'
        'sub:"%s",sub2:"%s"%s,etype:"%s",pot:"%s",combo:"%s",ratio:"%s",'
        'st:"%s",tp:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(name), esc(r["Brand"]), photo(etype, flavor, i), p, pack, p, pack,
           thc if thc else cbd, ("cbd:1," if cbd and cbd >= thc else ""), cbdf,
           cat, sub2, (',sub3:"%s"' % strain if cat == "THC Edibles" else ""), etype,
           pot, combo, ratio, st, TERP.get(flavor, "Fruity"), life,
           round(4.0 + (i % 10) * 0.1, 1), 5 + (i * 5) % 34,
           '","'.join(feels), flavor, esc(r["Description"])))

print("\n".join(out))
