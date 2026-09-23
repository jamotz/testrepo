#!/usr/bin/env python3
"""Turn Jack's topicals catalog into the app's topical products.

Source (reference/origins/product info/):
  - WA_Topicals_Regulatory_Audited_Patch_Weights_Simplified.xlsx
      sheet 1: the filter IA  (effect -> the forms available for it)
      sheet 2: the 35 products

Two sizes, deliberately. The sheet now carries a REGULATORY net quantity
("Net Wt. 2. oz (56.7 g)") alongside the raw figure the catalog was built on
(60, 75, 100, ...). Jack's call, 2026-09-22: the tile keeps the millilitre
figure shoppers have been seeing, and the regulatory declaration gets its own
line on the product page and drives the cart's weight bar. They are different
facts about the same jar, so they get different fields: `szs`/`pz` stay in mL,
`nq` is the printed declaration, and `nqa`/`nqb` are what the cart adds up.

Filter path: Topicals -> effect (Pain Relief, Recovery, Cooling, Warming,
Massage, Skincare, Intimacy), then the form as the second level, matching how
concentrates drill category -> consistency.

Every product carries one size and its own MSRP, so prices are exact rather
than multiplied — the same `pz` / `szs` override concentrates use.

Run: python3 reference/origins/hifi-build/gen_topicals.py
"""
import os, re, sys, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/"
                    "WA_Topicals_Regulatory_Audited_Patch_Weights_Simplified.xlsx")


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
        for c in re.findall(r"<(?:x:)?c[^>]*/>|<(?:x:)?c[^>]*>.*?</(?:x:)?c>", r, re.S):
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

# ---- Every topical is Holistic (Jack, 2026-08-12). ----
# Topicals aren't psychoactive - you can't get high off one unless it's a
# mainly-THC transdermal, and the catalog has none. So the strain axis doesn't
# apply to this shelf at all: the use case (Pain Relief, Massage, Intimacy, ...)
# stands in for it, and that's already `sub`. An earlier version routed Massage
# to Unwind and Intimacy to Nightlife; that's overruled.
LIFE = {}

# ---- effect -> three Feelings chips ----
# NOT RENDERED since 2026-09-21: the product page shows one "Best For" tile
# naming the use case instead. This table is exactly why - it is a lookup FROM
# the use case, so all ten Pain Relief products produced the same three words
# and the row said nothing the crumb did not. Kept, not deleted: real feelings
# data for topicals is parked (see project-handoff.md), and when it arrives the
# row comes back with something product-specific in it.
FEEL = {"Pain Relief": ["Relief", "Calm", "Clear"], "Recovery": ["Relief", "Relaxed", "Calm"],
        "Cooling": ["Clear", "Relief", "Calm"],     "Warming": ["Relaxed", "Calm", "Relief"],
        "Massage": ["Relaxed", "Mellow", "Calm"],   "Skincare": ["Clear", "Calm", "Balanced"],
        "Intimacy": ["Relaxed", "Giddy", "Calm"]}


def esc(s):
    return s.replace('"', '\\"').replace("&", "&amp;")


def size_label(raw):
    """Sizes are millilitres except the patches, which come by the piece.

    The sheet's "App Tile Size" column already reads "60 mL" / "1 Patch", so
    this now only has to cope with the AUTHORED rows below, which still carry
    a bare number the way the old sheet did."""
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
# Two THC-only Pain Relief products and one CBD:CBN Recovery cream. These three
# are the reason the app has 38 topicals against the sheet's 35.
#
# Their net quantities are NOT in any sheet, so they are taken from the form's
# own convention in Jack's data rather than made up per product: every Roll-On
# he lists is 3.4 fl oz (100 mL), every Balm / Salve 2 oz (56.7 g), every Cream
# 2 oz (56.7 g). Asserted against the sheet below, so if he ever re-sizes a
# form these stop agreeing loudly instead of drifting quietly.
AUTHORED_NQ = {"Roll-On":      ("Volume", 3.4, "fl oz", 100.0, "mL"),
               "Balm / Salve": ("Weight", 2.0, "oz",     56.7, "g"),
               "Cream":        ("Weight", 2.0, "oz",     56.7, "g")}
AUTHORED = """Agro Couture\tDeep Relief Roll-On\tRoll-On\tPain Relief\t200\t0\t\t\t100\t27.99\tTHC-forward roll-on built for targeted relief on sore joints and hard-worked muscles.
Heylo\tRescue Balm\tBalm / Salve\tPain Relief\t200\t0\t\t\t60\t22.99\tThick THC balm that stays where it is applied, for concentrated relief on a single sore spot.
Mary's Medicinals\tNight Recovery Cream\tCream\tRecovery\t0\t100\tCBN 100mg\tCBD:CBN 1:1\t50\t32.99\tEvening recovery cream pairing CBD with CBN, formulated for the end of a long day."""

hdr, recs = read_rows(XLSX, 1)
NQ_COLS = ["Net Qty Basis", "Net Amount (US)", "US Unit",
           "Net Amount (Metric)", "Metric Unit", "Regulatory Quantity Display",
           "App Tile Size"]
missing = [c for c in NQ_COLS if c not in hdr]
if missing:
    sys.exit("gen_topicals: sheet is missing column(s): %s" % ", ".join(missing))
if len(recs) != 35:
    sys.exit("gen_topicals: expected 35 sheet rows, read %d" % len(recs))

# The forms the AUTHORED rows borrow a net quantity from must still agree with
# the sheet, or the borrowed figure has quietly gone stale.
for form, (_b, us, uu, _m, _mu) in AUTHORED_NQ.items():
    seen = {(r["Net Amount (US)"], r["US Unit"]) for r in recs if r["Product Type"] == form}
    if ("%g" % us, uu) not in {(str(float(a)).rstrip("0").rstrip("."), u) for a, u in seen}:
        sys.exit("gen_topicals: AUTHORED_NQ[%r] says %g %s, sheet says %s"
                 % (form, us, uu, sorted(seen)))

for line in AUTHORED.strip().split("\n"):
    r = dict(zip(hdr, line.split("\t")))
    basis, us, uu, mt, mu = AUTHORED_NQ[r["Product Type"]]
    r["Net Qty Basis"], r["Net Amount (US)"], r["US Unit"] = basis, us, uu
    r["Net Amount (Metric)"], r["Metric Unit"] = mt, mu
    r["Regulatory Quantity Display"] = "%s %g %s (%g %s)" % (
        "Net Wt." if basis == "Weight" else "Net Vol.", us, uu, mt, mu)
    r["App Tile Size"] = ""                      # falls through to size_label()
    recs.append(r)
out = []
for i, r in enumerate(recs):
    form, effect = r["Product Type"].strip(), r["Effect"].strip()
    pot, cbd, othv, othname, combo, ratio = cannabinoids(r)
    size = size_label(r["App Tile Size"] or r["Original Size Entry"])
    # The regulatory declaration, and the two numbers the cart adds up:
    # `nqa` is the US amount, `nqb` its basis ("Weight" -> oz, "Volume" -> fl oz).
    # The sheet formats with Excel's TEXT(x,"0.##"), which leaves a whole
    # number wearing a trailing point -- "Net Wt. 2. oz (56.7 g)". Correct in a
    # spreadsheet, wrong on a product page, so the point goes here rather than
    # in the sheet, where it keeps all 35 rows formatted alike.
    nq   = re.sub(r"(\d)\.(?=\s)", r"\1", r["Regulatory Quantity Display"].strip())
    nqa  = float(r["Net Amount (US)"])
    nqb  = r["Net Qty Basis"].strip()
    if not nq or not nqa:
        sys.exit("gen_topicals: %s has no net quantity" % r["Product Name"])
    price = float(r["MSRP (USD)"])
    thc = float(r["THC (mg)"] or 0)

    extra = ""
    if cbd: extra += 'cbdv:%g,cbdu:" mg",' % cbd
    if othv: extra += 'othv:%g,' % othv
    if cbd and cbd >= thc:
        extra += "cbd:1,"          # the flag the CBD filter reads

    # No `ta`. It used to carry the FORM - the same string as sub2 and etype -
    # so the product page rendered "Cream" and "Roll-On" under a Taste heading.
    # A topical has no taste; the field is simply wrong for this shelf.
    out.append(
        ' {t:"topical",n:"%s",b:"%s",img:"%s",pr:%g,pz:{"%s":%g},szs:["%s"],'
        'nq:"%s",nqa:%g,nqb:"%s",'
        '%s%ssub:"%s",sub2:"%s",etype:"%s",%scombo:"%s",ratio:"%s",'
        'st:"%s",f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],d:"%s"},'
        % (esc(r["Product Name"]), esc(r["Brand"]), PHOTO.get(form, "top_balm"),
           price, size, price, size, esc(nq), nqa, nqb,
           ("thc:%g," % thc if thc else ""), extra,
           esc(effect), esc(form), esc(form),
           ('pot:"%s",' % pot if pot else ""), combo, ratio,
           "CBD",
           "holistic",
           round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
           '","'.join(FEEL.get(effect, ["Calm", "Relief", "Clear"])),
           esc(r["Description"])))

print("\n".join(out))
print("%d topicals across %d forms" % (len(out), len({r["Product Type"] for r in recs})),
      file=sys.stderr)
