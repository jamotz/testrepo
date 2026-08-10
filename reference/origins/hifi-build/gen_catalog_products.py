import re, json, random, zipfile, sys

DOCX = "/home/user/testrepo/reference/origins/product info/Flower Product Catalog.docx"
x = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf-8")
paras = re.findall(r"<w:p[ >].*?</w:p>", x, re.S)
lines = []
def strip_cbd(name):
    """Holistic products already say CBD three ways — the green border, the
    Holistic badge and the potency chip. The name doesn't need to as well."""
    return re.sub(r"\s*\bCBD\b\s*", " ", name).strip()

for p in paras:
    t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
    t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()
    if t:
        lines.append(t)

# parse: "Brand: XStrain: YType: ZSizes & Prices:" followed by "<size> — $<price>" lines
prods = []
cur = None
for ln in lines:
    m = re.match(r"Brand:\s*(.+?)Strain:\s*(.+?)Type:\s*(.+?)Sizes & Prices:", ln)
    if m:
        if cur: prods.append(cur)
        cur = {"brand": m.group(1).strip(), "strain": m.group(2).strip(),
               "type": m.group(3).strip(), "prices": {}}
        continue
    m2 = re.match(r"([\d.]+g)\s*[—-]\s*\$([\d.]+)", ln)
    if m2 and cur:
        size = m2.group(1).replace("g", " g")
        cur["prices"][size] = float(m2.group(2))
if cur: prods.append(cur)

print("parsed", len(prods), "products", file=sys.stderr)

# --- supporting attributes. Catalog gives brand/strain/type/prices only, so the
# rest is authored from each real strain's well-known profile (doc is mock data).
PROFILE = {
 "Power":            ("Indica","unwind",   ["Relaxed","Heavy","Calm"],      ["Earthy","Skunky","Herbal"], "Earthy",  "A heavy indica-leaning cut with a deep earthy nose and full-body ease."),
 "Purple Ripple":    ("Indica","unwind",   ["Sleepy","Relaxed","Giddy"],    ["Fruity","Flowery","Herbal"],"Lavender","Grape-forward purple genetics with a soft floral finish."),
 "Trop Cherry":      ("Sativa","social",   ["Uplifted","Giddy","Social"],   ["Fruity","Citrus","Creamy"], "Citrus",  "Tropical cherry candy on the nose, bright and conversational."),
 "Red Velvet":       ("Hybrid","social",   ["Balanced","Giddy","Relaxed"],  ["Creamy","Fruity","Nutty"],  "Fruity",  "Dessert-leaning hybrid — smooth, sweet and even-keeled."),
 "Gelato Cake":      ("Indica","unwind",   ["Relaxed","Heavy","Hungry"],    ["Creamy","Fruity","Earthy"], "Fruity",  "Rich gelato dessert genetics with a weighty, cozy finish."),
 "Jack Herer":       ("Sativa","adventurous",["Focused","Energized","Clear"],["Pine","Peppery","Citrus"], "Piney",   "The classic daytime sativa — piney, sharp and clear-headed."),
 "Blue Dream":       ("Hybrid","discovery",["Uplifted","Creative","Balanced"],["Fruity","Flowery","Herbal"],"Fruity", "Blueberry-sweet hybrid, gentle and famously easy to enjoy."),
 "Gas Face":         ("Indica","nightlife",["Heavy","Relaxed","Euphoric"],  ["Diesel","Skunky","Peppery"],"Pepper",  "Loud, gassy indica built for the end of the night."),
 "Permanent Marker": ("Hybrid","nightlife",["Euphoric","Giddy","Relaxed"],  ["Diesel","Creamy","Peppery"],"Pepper",  "Sharp solvent-y nose over a creamy exhale. A modern favorite."),
 "Zour Beltz":       ("Hybrid","social",   ["Giddy","Uplifted","Social"],   ["Citrus","Fruity","Diesel"], "Citrus",  "Sour candy terps with a lively, social lift."),
 "GMO BX":           ("Indica","unwind",   ["Heavy","Relaxed","Hungry"],    ["Skunky","Diesel","Earthy"], "Earthy",  "Savory garlic-and-diesel GMO backcross. Deeply sedating."),
 "Ginger Tea":       ("Sativa","discovery",["Clear","Focused","Uplifted"],  ["Peppery","Herbal","Citrus"],"Pepper",  "Warm spiced nose, clean and clear in effect."),
 "Animal Face":      ("Indica","unwind",   ["Relaxed","Euphoric","Heavy"],  ["Skunky","Diesel","Herbal"], "Earthy",  "Animal Mints x Face Off OG — potent and full-bodied."),
 "Wedding Cake":     ("Indica","unwind",   ["Relaxed","Giddy","Hungry"],    ["Creamy","Nutty","Fruity"],  "Fruity",  "Vanilla frosting sweetness with a calm, heavy landing."),
 "Super Lemon Haze": ("Sativa","adventurous",["Energized","Uplifted","Focused"],["Citrus","Peppery","Herbal"],"Citrus","Zesty lemon haze — bright, fast and energizing."),
 "Cosmic Queen":     ("Sativa","adventurous",["Energized","Creative","Clear"],["Citrus","Pine","Fruity"], "Citrus",  "Bright sativa hybrid with a crisp citrus-pine lift."),
 "Blueberry Muffin": ("Hybrid","social",   ["Giddy","Balanced","Relaxed"],  ["Fruity","Creamy","Flowery"],"Fruity",  "True blueberry baked-goods nose. Warm and easygoing."),
 "GMO Cookies":      ("Indica","unwind",   ["Heavy","Relaxed","Sleepy"],    ["Skunky","Diesel","Earthy"], "Earthy",  "Garlic-forward GMO with a savory, couch-bound finish."),
 "Cherry Pie":       ("Hybrid","social",   ["Giddy","Relaxed","Balanced"],  ["Fruity","Creamy","Earthy"], "Fruity",  "Tart cherry over a doughy sweetness. A reliable hybrid."),
 "Pineapple Express":("Sativa","social",   ["Uplifted","Social","Energized"],["Citrus","Fruity","Pine"],  "Citrus",  "Tropical pineapple and pine — famously upbeat."),
 "Northern Lights":  ("Indica","unwind",   ["Sleepy","Relaxed","Calm"],     ["Earthy","Herbal","Pine"],   "Earthy",  "The legendary indica benchmark. Quiet, heavy, restful."),
 "Royal Kush":       ("Indica","unwind",   ["Relaxed","Heavy","Calm"],      ["Earthy","Pine","Herbal"],   "Earthy",  "Old-school kush structure with a grounded, piney depth."),
 "Strawberry Cough": ("Sativa","social",   ["Uplifted","Social","Giddy"],   ["Fruity","Flowery","Herbal"],"Fruity",  "Sweet strawberry on the inhale, open and talkative."),
 "Sunset Sherbet":   ("Hybrid","social",   ["Giddy","Relaxed","Euphoric"],  ["Fruity","Creamy","Citrus"], "Fruity",  "Creamy sherbet terps with a smooth, sunny lift."),
 "ACDC":             ("CBD","holistic",    ["Clear","Calm","Relief"],       ["Herbal","Earthy","Pine"],   "Earthy",  "High-CBD, very low THC. Clear-headed relief without the high."),
 "Charlotte's Web":  ("CBD","holistic",    ["Calm","Clear","Relief"],       ["Herbal","Flowery","Earthy"],"Earthy",  "The best-known CBD cultivar — gentle and non-intoxicating."),
 "Harlequin":        ("CBD","holistic",    ["Clear","Balanced","Calm"],     ["Citrus","Herbal","Earthy"], "Citrus",  "CBD-dominant with a touch of THC for a balanced calm."),
 "Sour Space Candy": ("CBD","holistic",    ["Calm","Uplifted","Clear"],     ["Citrus","Fruity","Herbal"], "Citrus",  "Sour hemp candy terps, relaxed but clear."),
 "Lifter":           ("CBD","holistic",    ["Clear","Uplifted","Calm"],     ["Herbal","Citrus","Earthy"], "Herbal",  "Daytime CBD flower with a light, lifted feel."),
 "Hawaiian Haze CBD":("CBD","holistic",    ["Uplifted","Clear","Calm"],     ["Fruity","Citrus","Flowery"],"Citrus",  "Tropical hemp haze — bright, breezy and non-intoxicating."),
}

rnd = random.Random(20260730)              # seeded: same shuffle every build
IMG_POOL = ["fl_indica","fl_indica2","fl_indica3","fl_sativa","fl_sativa2",
            "fl_hybrid","fl_hybrid2","fl_indhyb","fl_indhyb2","fl_sathyb",
            "fl_sathyb2","fl_universal"]   # keys that exist in asm_app.py's map   # new uploads + the ones already in use

def esc(s): return s.replace("'", "\\'")

out = []
for pr in prods:
    strain = pr["strain"]
    prof = PROFILE.get(strain)
    if not prof:
        print("!! no profile for", strain); continue
    st, life, feels, taste, terp, desc = prof
    sizes = list(pr["prices"].keys())
    eighth = pr["prices"].get("3.5 g") or list(pr["prices"].values())[0]
    thc = round(rnd.uniform(0.4, 0.9), 1) if st == "CBD" else round(rnd.uniform(19.5, 29.5), 1)
    # the catalog doc carries no CBD, so author it the way THC already is. The
    # bands mirror the concentrate sheet's real numbers: CBD cultivars land
    # around 15%, everything else keeps a trace.
    cbdpct = round(rnd.uniform(12.0, 17.5), 1) if st == "CBD" else round(rnd.uniform(0.1, 0.8), 1)
    img = rnd.choice(IMG_POOL)
    sub = rnd.choice(["Indoor", "Indoor", "Outdoor"])
    rating = round(rnd.uniform(3.9, 4.9), 1)
    revs = rnd.randint(4, 40)
    cbd = (",cbd:1" if st == "CBD" else "") + ",cbdv:%g" % cbdpct
    entry = (' {t:"flower",n:"%s",b:"%s",img:"%s",pr:%s,pz:%s,szs:%s,thc:%s%s,sub:"%s",st:"%s",tp:"%s",'
             'f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},') % (
        esc(strip_cbd(strain)), esc(pr["brand"]), img, eighth,
        json.dumps(pr["prices"]).replace('"', '"'), json.dumps(sizes),
        thc, cbd, sub, st, terp, life,
        rating, revs, '","'.join(feels), '","'.join(taste), esc(desc))
    out.append(entry)

# stdout, like the other two generators — this used to write to a scratchpad
# path from a long-dead session, which made the script unrunnable
print("\n".join(out))
# image distribution
from collections import Counter
# print(Counter(re.search(r'img:"(\w+)"', e).group(1) for e in out))
