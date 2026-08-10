#!/usr/bin/env python3
"""Turn Jack's edibles files into the app's edible products.

Sources (reference/origins/product info/):
  - Edible_Filter_Architecture_v2.xlsx  -> the filter IA (levels + effect tiles)
  - WA_Edibles_By_Brand_Final_Curated_Normalized.xlsx -> the 50 products + prices

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
XLSX = os.path.join(REPO, "reference/origins/product info/WA_Edibles_By_Brand_Final_Curated_Normalized.xlsx")

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
LIFE_STRAIN = {"Sativa":"adventurous","Hybrid":"social","Indica":"unwind"}
# flavour -> the app's terpene list
TERP = {# berries and stone fruit
        "Blackberry":"Fruity","Marionberry":"Fruity","Elderberry":"Fruity",
        "Huckleberry":"Fruity","Raspberry":"Fruity","Blue Raspberry":"Fruity",
        "Strawberry":"Fruity","Cherry":"Fruity","Watermelon":"Fruity",
        "Peach":"Fruity","Pear":"Fruity","Green Apple":"Fruity",
        # bright and sharp
        "Lemon":"Citrus","Mango":"Citrus","Pineapple":"Citrus","Blood Orange":"Citrus",
        "Tangerine":"Citrus","Cherry Lime":"Citrus",
        # bakery and confection
        "Dark Chocolate":"Earthy","Espresso":"Earthy","Double Chocolate":"Earthy",
        "Milk Chocolate":"Creamy","Cookies & Cream":"Creamy","Sea Salt Caramel":"Creamy",
        "Chocolate Chip":"Creamy","Fudge Brownie":"Creamy","Snickerdoodle":"Creamy",
        "Peanut Butter":"Nutty","Oatmeal Raisin":"Nutty",
        # capsules
        "Unflavored":"Herbal"}

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
    name   = r["Product Name"]
    flavor = flavour_of(name)          # derived; the sheet's Flavor column is unreliable
    effect = r["Effect Filter"]
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
    p = float(r["WA Retail Price (USD)"])   # real WA retail, straight from the sheet
    out.append(
        ' {t:"edible",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],mg:%g,%s%s'
        'sub:"%s",sub2:"%s"%s,etype:"%s",pot:"%s",combo:"%s",ratio:"%s",'
        'st:"%s",tp:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(name), esc(r["Brand"]), photo(etype, name, i), p, pack, p, pack,
           thc if thc else cbd, ("cbd:1," if cbd and cbd >= thc else ""), cbdf,
           cat, sub2, (',sub3:"%s"' % strain if cat == "THC Edibles" else ""), etype,
           pot, combo, ratio, st, TERP.get(flavor, "Sweet"), life,
           round(4.0 + (i % 10) * 0.1, 1), 5 + (i * 5) % 34,
           '","'.join(feels), flavor, esc(r["Description"])))

print("\n".join(out))
