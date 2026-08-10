#!/usr/bin/env python3
"""Turn Jack's topicals catalog into the app's topical products.

Source (reference/origins/product info/):
  - WA_Topicals_Product_Catalog_Final.xlsx
      sheet 1: the filter IA  (effect -> the forms available for it)
      sheet 2: the 35 products

Filter path: Topicals -> effect (Pain Relief, Recovery, Cooling, Warming,
Massage, Skincare, Intimacy), then the form as the second level, matching how
concentrates drill category -> consistency.

Every product carries one size and its own MSRP, so prices are exact rather
than multiplied — the same `pz` / `szs` override concentrates use.

Run: python3 reference/origins/hifi-build/gen_topicals.py
"""
import os, re, sys, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/WA_Topicals_Product_Catalog_Final.xlsx")


def read_rows(path, sheet_idx=0):
    """Cells placed by column letter — Excel omits empty cells entirely, and
    appending in document order silently shifts every column after a blank."""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    ss = []
    if "xl/sharedStrings.xml" in names:
        x = z.read("xl/sharedStrings.xml").decode("utf-8")
        ss = [re.sub(r"<[^>]+>", "", m)
              for m in re.findall(r"<(?:x:)?si>(.*?)</(?:x:)?si>", x, re.S)]
    sheets = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    sh = z.read(sheets[sheet_idx]).decode("utf-8")
    rows = []
    for r in re.findall(r"<(?:x:)?row[^>]*>(.*?)</(?:x:)?row>", sh, re.S):
        cells = []
        for c in re.findall(r"<(?:x:)?c[^>]*>.*?</(?:x:)?c>|<(?:x:)?c[^>]*/>", r, re.S):
            ref = re.search(r'r="([A-Z]+)\d+"', c)
            if ref:
                col = 0
                for ch in ref.group(1):
                    col = col * 26 + ord(ch) - 64
                while len(cells) < col - 1:
                    cells.append("")
            t = re.search(r't="(\w+)"', c)
            ins = re.search(r"<(?:x:)?is>(.*?)</(?:x:)?is>", c, re.S)
            v = re.search(r"<(?:x:)?v>(.*?)</(?:x:)?v>", c)
            if ins:   cells.append(re.sub(r"<[^>]+>", "", ins.group(1)))
            elif v:   cells.append(ss[int(v.group(1))] if t and t.group(1) == "s" else v.group(1))
            else:     cells.append("")
        rows.append(cells)
    hdr = rows[0]
    return hdr, [dict(zip(hdr, r + [""] * (len(hdr) - len(r))))
                 for r in rows[1:] if len(r) > 3 and r[0].strip()]


# ---- form -> photo. Every form in the sheet has a shot in the repo. ----
PHOTO = {"Balm / Salve": "top_balm", "Bath Soak": "top_bath", "Cream": "top_cream",
         "Gel": "top_gel", "Lotion": "top_lotion", "Lubricant": "top_lube",
         "Oil": "top_oil", "Roll-On": "top_rollon", "Stick": "top_stick",
         "Transdermal Patch": "top_patch"}

# ---- effect -> lifestyle. Topicals are relief-led, so most land on Holistic;
#      massage and intimacy read closer to Unwind and Nightlife. ----
LIFE = {"Pain Relief": "holistic", "Recovery": "holistic", "Cooling": "holistic",
        "Warming": "holistic", "Skincare": "holistic",
        "Massage": "unwind", "Intimacy": "nightlife"}

# ---- effect -> the three Feelings chips on the product page ----
FEEL = {"Pain Relief": ["Relief", "Calm", "Clear"], "Recovery": ["Relief", "Relaxed", "Calm"],
        "Cooling": ["Clear", "Relief", "Calm"],     "Warming": ["Relaxed", "Calm", "Relief"],
        "Massage": ["Relaxed", "Mellow", "Calm"],   "Skincare": ["Clear", "Calm", "Balanced"],
        "Intimacy": ["Relaxed", "Giddy", "Calm"]}

# ---- form -> taste/scent stand-in. Topicals aren't eaten; the app still wants
#      a terpene for the wizard, so use the profile each form reads as. ----
TERP = {"Balm / Salve": "Herbal", "Bath Soak": "Flowery", "Cream": "Flowery",
        "Gel": "Piney", "Lotion": "Flowery", "Lubricant": "Herbal",
        "Oil": "Herbal", "Roll-On": "Piney", "Stick": "Piney",
        "Transdermal Patch": "Herbal"}


def esc(s):
    return s.replace('"', '\\"').replace("&", "&amp;")


def size_label(raw):
    """Sizes are millilitres except the patches, which come by the piece."""
    raw = (raw or "").strip()
    return raw if not raw.replace(".", "").isdigit() else "%g mL" % float(raw)


def cannabinoids(r):
    """Returns (pot, cbdv, othv, othname, combo, ratio).

    The sheet's Ratio column mixes forms — '1:1', 'CBD', 'CBD:CBG 4:1' — so the
    combo is derived from which cannabinoids actually carry milligrams and only
    the numeric tail of Ratio is kept.
    """
    thc = float(r["THC (mg)"] or 0)
    cbd = float(r["CBD (mg)"] or 0)
    oth_raw = (r["Other Cannabinoids"] or "").strip()
    othname, othv = "", 0.0
    m = re.match(r"([A-Za-z]+)\s*([\d.]+)\s*mg", oth_raw)
    if m:
        othname, othv = m.group(1).upper(), float(m.group(2))

    parts = []
    if thc: parts.append("THC")
    if cbd: parts.append("CBD")
    if othname: parts.append(othname)
    combo = ":".join(parts) if len(parts) > 1 else (parts[0] + " Only" if parts else "")

    ratio = ""
    rm = re.search(r"(\d+(?::\d+)+)", r["Ratio"] or "")
    if rm and len(parts) > 1:
        ratio = rm.group(1)
    return ("%g mg THC" % thc if thc else "", cbd, othv, othname, combo, ratio)


# ---- AUTHORED: not in Jack's sheet, added on request (2026-08-10).
# Two THC-only Pain Relief products and one CBD:CBN Recovery cream. Columns
# match the sheet exactly so they flow through the same code path.
AUTHORED = """Agro Couture\tDeep Relief Roll-On\tRoll-On\tPain Relief\t200\t0\t\t\t100\t27.99\tTHC-forward roll-on built for targeted relief on sore joints and hard-worked muscles.
Heylo\tRescue Balm\tBalm / Salve\tPain Relief\t200\t0\t\t\t60\t22.99\tThick THC balm that stays where it is applied, for concentrated relief on a single sore spot.
Mary's Medicinals\tNight Recovery Cream\tCream\tRecovery\t0\t100\tCBN 100mg\tCBD:CBN 1:1\t50\t32.99\tEvening recovery cream pairing CBD with CBN, formulated for the end of a long day."""

hdr, recs = read_rows(XLSX, 1)
for line in AUTHORED.strip().split("\n"):
    recs.append(dict(zip(hdr, line.split("\t"))))
out = []
for i, r in enumerate(recs):
    form, effect = r["Product Type"].strip(), r["Effect"].strip()
    pot, cbd, othv, othname, combo, ratio = cannabinoids(r)
    size = size_label(r["Size (mL)"])
    price = float(r["MSRP (USD)"])
    thc = float(r["THC (mg)"] or 0)

    extra = ""
    if cbd: extra += 'cbdv:%g,cbdu:" mg",' % cbd
    if othv: extra += 'othv:%g,' % othv
    if cbd and cbd >= thc:
        extra += "cbd:1,"          # the flag the CBD filter reads

    out.append(
        ' {t:"topical",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
        '%s%ssub:"%s",sub2:"%s",etype:"%s",%scombo:"%s",ratio:"%s",'
        'st:"%s",tp:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
        % (esc(r["Product Name"]), esc(r["Brand"]), PHOTO.get(form, "top_balm"),
           price, size, price, size,
           ("thc:%g," % thc if thc else ""), extra,
           esc(effect), esc(form), esc(form),
           ('pot:"%s",' % pot if pot else ""), combo, ratio,
           "CBD" if thc == 0 else "Hybrid", TERP.get(form, "Herbal"),
           LIFE.get(effect, "holistic"),
           round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
           '","'.join(FEEL.get(effect, ["Calm", "Relief", "Clear"])),
           esc(form), esc(r["Description"])))

print("\n".join(out))
print("%d topicals across %d forms" % (len(out), len({r["Product Type"] for r in recs})),
      file=sys.stderr)
