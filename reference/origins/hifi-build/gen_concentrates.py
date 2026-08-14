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
XLSX = os.path.join(REPO, "reference/origins/product info/Concentrate Final Product List for WA.xlsx")

# --- read the sheet ---
# The "Final" sheet uses sharedStrings where the old mock one used inline
# strings, so it goes through the shared reader (by column letter, self-closing
# cells first) rather than the positional one this file used to carry.
from xlsxread import read_cells
from terpmap import pairs as terp_pairs, check as terp_check
from html import unescape as _u

_COLS = ["ID","Brand","Product Name","Category","Subcategory","Type","Size","Price",
         "THC %","CBD %","Description","Terp 1","Terp 2","Terp 3"]
_rows = [r for r in read_cells(XLSX)[1:] if r.get("A")]
recs = [{k: _u(r.get(chr(65 + i), "")).strip() for i, k in enumerate(_COLS)} for r in _rows]

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
# The sheet's Type column already carries all six values; it used to be
# collapsed to four here (Indica Hybrid -> Indica, Sativa Hybrid -> Sativa),
# which threw away the two the app now needs. Kept verbatim.
ST = {"Indica":"Indica","Indica Hybrid":"Indica Hybrid","Sativa":"Sativa",
      "Sativa Hybrid":"Sativa Hybrid","Hybrid":"Hybrid","CBD":"CBD"}

# The app's six lifestyles are the six strain values renamed (Jack, 2026-08-12).
# A settings toggle will swap the vocabularies, so they stay one-to-one.
LIFESTYLE = {"Sativa":"discovery","Sativa Hybrid":"adventurous","Hybrid":"social",
             "Indica Hybrid":"unwind","Indica":"nightlife","CBD":"holistic"}

def esc(s): return s.replace('"', '\\"')

def strip_cbd(name):
    """Same reasoning as the consistency: the Holistic signal is already carried
    by the border, the badge and the chip."""
    return re.sub(r"\s*\bCBD\b\s*", " ", name).strip()

def strip_form(name, sub, cat):
    """Drop the consistency (and category) off the tail of a product name.

    The breadcrumb above the name already reads "Rosin > Rosin Sap", so
    "Lemon Cherry Gelato Rosin Sap" says it twice and costs a whole line on
    the tile. Edibles deliberately keep their form ("Blackberry Gummies").
    """
    norm = name.replace("&amp;", "&")
    for tail in (sub.replace("&amp;", "&").strip(), cat.strip()):
        if tail and norm.lower().endswith(tail.lower()):
            norm = norm[:-len(tail)].strip(" -\u2013")
    return norm.replace("&", "&amp;")

terp_check([[r["Terp 1"], r["Terp 2"], r["Terp 3"]] for r in recs], "gen_concentrates")

out, unmatched = [], []
for i, r in enumerate(recs):
    key = (r["Category"], r["Subcategory"].replace("&amp;", "&"))
    if key not in JOIN:
        unmatched.append(key); continue
    cat, form, img = JOIN[key]
    st = ST.get(r["Type"], "Hybrid")
    life = LIFESTYLE[st]          # the sheet's Type column, renamed
    feels, scents = terp_pairs([r["Terp 1"], r["Terp 2"], r["Terp 3"]])
    price = float(r["Price"])
    thc, cbd = float(r["THC %"]), float(r["CBD %"])
    rating = round(3.9 + (i % 11) * 0.1, 1)
    revs = 4 + (i * 7) % 37
    out.append(
        ' {t:"concentrate",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"1 g":%g},szs:["1 g"],'
        'thc:%g%s,sub:"%s",sub2:"%s",st:"%s",f:["%s"],sale:0,r:%s,rv:%d,'
        'fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(strip_cbd(strip_form(r["Product Name"], r["Subcategory"], r["Category"]))), esc(r["Brand"]), img, price, price,
           thc, ((",cbd:1" if st == "CBD" else "") + (",cbdv:%g" % cbd if cbd else "")), cat, form, st, life,
           rating, revs, '","'.join(feels), '","'.join(scents), esc(r["Description"])))

print("\n".join(out))
if unmatched:
    print("\n// UNMATCHED:", set(unmatched))
