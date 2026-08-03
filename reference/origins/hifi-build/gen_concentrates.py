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

# Kief rows 51-56, supplied by Jack as an addendum to the sheet (same columns).
EXTRA = """51\tSkord\tMAC 1 Loose Kief\tKief\tLoose Kief\tHybrid\t1g\t22\t48.6\t0.2\tFinely sifted trichomes ideal for topping flower or boosting potency.\tBalanced\tHappy\tEuphoric\tCitrus, Pine, Earth
52\tPlaid Jacket\tBlue Dream Loose Kief\tKief\tLoose Kief\tSativa Hybrid\t1g\t20\t46.9\t0.2\tClassic kief with bright terpene expression and versatile use.\tCreative\tUplifted\tFocused\tBerry, Sweet, Herbal
53\tRefine\tGMO Dry Sift Kief\tKief\tDry Sift Kief\tIndica Hybrid\t1g\t24\t51.4\t0.1\tTraditional dry sift concentrate with rich cannabinoid content.\tRelaxed\tCalm\tHappy\tGarlic, Diesel, Earth
54\tDank Czar\tPermanent Marker Dry Sift Kief\tKief\tDry Sift Kief\tHybrid\t1g\t25\t53.2\t0.1\tHigh-quality dry sift with bold aroma and smooth texture.\tEuphoric\tBalanced\tRelaxed\tGas, Candy, Floral
55\tBuddies\tACDC Infused Kief\tKief\tInfused Kief\tCBD\t1g\t18\t9.8\t38.5\tCBD-rich kief designed for a mellow, clear-headed experience.\tCalm\tClear-Headed\tRelaxed\tLemon, Herbal, Pine
56\tPassion Flower\tRainbow Belts Infused Kief\tKief\tInfused Kief\tHybrid\t1g\t23\t55.1\t0.2\tTerpene-enhanced kief for sprinkling over flower or bowls.\tHappy\tRelaxed\tCreative\tCandy, Tropical, Citrus"""

# Rows 57-60 authored to Jack's schema (not from the sheet) to stock the two
# syringe consistencies. Rosin Coins and both applicator forms stay empty.
AUTHORED = """57\tDabstract\tNorthern Lights Distillate Syringe\tDistillate\tSyringe\tIndica\t1g\t32\t88.4\t0.3\tUltra-refined distillate in an easy-dose syringe for dabbing or infusing.\tRelaxed\tSleepy\tBody High\tEarth, Herbal, Sweet
58\tRefine\tSour Diesel Distillate Syringe\tDistillate\tSyringe\tSativa\t1g\t34\t90.2\t0.2\tUltra-refined distillate in an easy-dose syringe for dabbing or infusing.\tEnergetic\tFocused\tUplifted\tDiesel, Citrus, Fuel
59\tSkagit Organics\tFull Spectrum RSO Syringe\tRSO\tOil Syringe\tIndica\t1g\t38\t72.5\t1.8\tUnrefined full-spectrum extract in a measured syringe. Start small.\tRelaxed\tSleepy\tBody High\tEarth, Herbal, Pine
60\tBuddies\t1:1 CBD RSO Syringe\tRSO\tOil Syringe\tCBD\t1g\t40\t32.4\t31.8\tBalanced full-spectrum RSO for measured, clear-headed relief.\tCalm\tRelaxed\tClear-Headed\tHerbal, Earth, Pepper"""

for line in (EXTRA + "\n" + AUTHORED).strip().split("\n"):
    recs.append(dict(zip(hdr, line.split("\t"))))

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
