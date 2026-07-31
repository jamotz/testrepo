#!/usr/bin/env python3
"""Turn Jack's WA_Mock_Concentrate_Inventory_50_with_Flavors.xlsx into the app's
concentrate products, joining each row to a photo by its sub-filter name.

The join key is (Category, Subcategory) from the sheet -> the app's
(category, consistency) taxonomy from the "Concentrate Categories and filters"
doc -> the uploaded photo, which is named after that consistency.

Run: python3 reference/origins/hifi-build/gen_concentrates.py
Prints the product entries for origins-app.src.html (P array).
"""
import json, os, re, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/WA_Mock_Concentrate_Inventory_50_with_Flavors.xlsx")

# --- read the sheet (inline-string xlsx, no sharedStrings) ---
z = zipfile.ZipFile(XLSX)
sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
def cell(c):
    ins = re.search(r"<is>(.*?)</is>", c, re.S)
    if ins: return re.sub(r"<[^>]+>", "", ins.group(1))
    v = re.search(r"<v>(.*?)</v>", c)
    return v.group(1) if v else ""
rows = []
for r in re.findall(r"<row[^>]*>(.*?)</row>", sheet, re.S):
    rows.append([cell(c) for c in re.findall(r"<c[^>]*>.*?</c>|<c[^>]*/>", r, re.S)])
hdr, recs = rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]

# --- sheet (Category, Subcategory) -> (app category, app consistency, image key) ---
# app taxonomy + photo names come from the same source, so this is the join table
JOIN = {
 ("Live Resin","Badder"):            ("Live Resin","Badder/Batter","clr_badder"),
 ("Live Resin","Sugar"):             ("Live Resin","Sugar","clr_sugar"),
 ("Live Resin","Sauce"):             ("Live Resin","Sauce","clr_sauce"),
 ("Live Resin","Diamonds & Sauce"):  ("Live Resin","Diamonds","clr_diamonds"),
 ("Live Resin","Wax"):               ("Live Resin","Wax","clr_wax"),
 ("Live Resin","Crumble"):           ("Live Resin","Crumble","clr_crumble"),
 ("Live Resin","Shatter"):           ("Live Resin","Shatter","clr_shatter"),
 ("Rosin","Live Rosin"):             ("Rosin","Live Rosin","cro_live"),
 ("Rosin","Rosin Badder"):           ("Rosin","Rosin Badder","cro_badder"),
 ("Rosin","Rosin Jam"):              ("Rosin","Rosin Jam","cro_jam"),
 ("Rosin","Rosin Coins"):            ("Rosin","Rosin Coins","cro_coins"),
 ("Rosin","Rosin Sap"):              ("Rosin","Rosin Sap","cro_sap"),
 ("Hash","Bubble Hash"):             ("Hash","Bubble Hash","ch_bubble"),
 ("Hash","Ice Water Hash"):          ("Hash","Ice Water Hash","ch_icewater"),
 ("Hash","Dry Sift"):                ("Hash","Dry Sift","ch_drysift"),
 ("Hash","Full Melt Hash"):          ("Hash","Full Melt Hash","ch_fullmelt"),
 ("Hash","Temple Ball"):             ("Hash","Temple Ball Hash","ch_templeball"),
 ("Distillate","Distillate Oil"):    ("Distillate","Oil","cd_oil"),
 ("Distillate","Syringe"):           ("Distillate","Syringe","cd_syringe"),
 ("Distillate","Dab Applicator"):    ("Distillate","Dab Applicator","cd_applicator"),
 ("Kief","Loose Kief"):              ("Kief","Loose Kief","ck_loose"),
 ("Kief","Dry Sift Kief"):           ("Kief","Dry Sift Kief","ck_drysift"),
 ("Kief","Infused Kief"):            ("Kief","Infused Kief","ck_infused"),
 ("RSO","Oil Syringe"):              ("RSO","Oil Syringe","crso_oil"),
 ("RSO","Applicator"):               ("RSO","Applicator","crso_applicator"),
}

# effect -> lifestyle (the app's six)
LIFE = {"Relaxed":"unwind","Sleepy":"unwind","Body High":"unwind","Calm":"unwind",
        "Happy":"social","Euphoric":"nightlife","Balanced":"social","Uplifted":"social",
        "Energetic":"adventurous","Focused":"adventurous","Creative":"discovery",
        "Clear-Headed":"discovery"}
# flavour note -> the app's terpene list
TERP = {"Citrus":"Citrus","Lemon":"Citrus","Lime":"Citrus","Orange":"Citrus","Tropical":"Citrus",
        "Mango":"Citrus","Pine":"Piney","Herbal":"Piney","Mint":"Piney","Pepper":"Pepper",
        "Diesel":"Pepper","Fuel":"Pepper","Gas":"Pepper","Garlic":"Pepper","Skunk":"Pepper",
        "Floral":"Lavender","Vanilla":"Lavender","Earth":"Earthy","Earthy":"Earthy",
        "Coffee":"Earthy","Chocolate":"Earthy","Dough":"Earthy","Cookie":"Earthy",
        "Berry":"Fruity","Blueberry":"Fruity","Grape":"Fruity","Apple":"Fruity","Pear":"Fruity",
        "Fruit":"Fruity","Sweet":"Fruity","Candy":"Fruity","Cream":"Fruity"}
ST = {"Indica":"Indica","Indica Hybrid":"Indica","Sativa":"Sativa","Sativa Hybrid":"Sativa",
      "Hybrid":"Hybrid","CBD":"CBD"}

def esc(s): return s.replace('"', '\\"')

out, unmatched = [], []
for i, r in enumerate(recs):
    key = (r["Category"], r["Subcategory"].replace("&amp;", "&"))
    if key not in JOIN:
        unmatched.append(key); continue
    cat, form, img = JOIN[key]
    st = ST.get(r["Type"], "Hybrid")
    effects = [r["Effect 1"], r["Effect 2"], r["Effect 3"]]
    life = LIFE.get(effects[0], "social") if st != "CBD" else "holistic"
    flavors = [f.strip() for f in r["Flavor Notes"].split(",")]
    terp = next((TERP[f] for f in flavors if f in TERP), "Earthy")
    price = float(r["Price"])
    thc, cbd = float(r["THC %"]), float(r["CBD %"])
    rating = round(3.9 + (i % 11) * 0.1, 1)
    revs = 4 + (i * 7) % 37
    out.append(
        ' {t:"concentrate",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"1 g":%g},szs:["1 g"],'
        'thc:%g%s,sub:"%s",sub2:"%s",st:"%s",tp:"%s",f:["%s"],sale:0,r:%s,rv:%d,'
        'fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(r["Product Name"]), esc(r["Brand"]), img, price, price,
           thc, (",cbd:1" if st == "CBD" else ""), cat, form, st, terp, life,
           rating, revs, '","'.join(effects), '","'.join(flavors[:3]), esc(r["Description"])))

print("\n".join(out))
if unmatched:
    print("\n// UNMATCHED:", set(unmatched))
