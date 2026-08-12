#!/usr/bin/env python3
"""Turn Jack's pre-roll catalog into the app's pre-roll products.

Source (reference/origins/product info/):
  - WA_PreRolls_IA_Condensed.xlsx    the filter IA + the rules sheet
  - WA_PreRolls_50_Product_List.xlsx sheet 1: the 50 products
                                     sheet 2: the catalog rules

Filter path (from the IA): Pre-Rolls -> cannabinoid branch (THC / CBD / Blend)
-> type (Flower / Infused / Trifecta) -> concentrate type, Infused only. Size
stays a Filter-drawer facet because products don't exist in all three sizes.

  sub  = THC / CBD / Blend
  sub2 = Flower / Infused / Trifecta
  sub3 = concentrate type on Infused; the component combination on Trifecta,
         which the IA calls metadata rather than navigation — so nothing ever
         renders a Trifecta sub3 bubble and it only shows in the breadcrumb.

Ratios are deliberately absent: the IA reserves them for standardized-dose
formats (edibles, tinctures, drinks) and says to display actual THC % and CBD %
for Blend instead.

The sheet's columns match its header exactly: E Concentrate Type (empty on
Flower rows), F Available Sizes, K Other Cannabinoids and L Ratio (empty
throughout), M WA Retail Price. check_columns() re-asserts that layout on every
invocation and aborts rather than emit shifted products.

This file used to claim the opposite — that Flower rows kept sizes in E and
every row kept its price in K — and read the sheet accordingly. That was never
true of the sheet. read_cells() matched a self-closing empty cell
(`<c r="E2" s="29" t="str"/>`) with the *open-tag* branch of its alternation, so
the `.*?</c>` ran on to the next cell's closing tag and E swallowed F's value.
Every empty cell shifted the row one column left, which is what made sizes look
like they sat in E and the price in K. The two compensations cancelled the bug
and the emitted products were correct, so it went unnoticed. The alternation now
tries the self-closing branch first; see read_cells().

Run: python3 reference/origins/hifi-build/gen_prerolls.py
"""
import os, re, sys, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/WA_PreRolls_50_Product_List.xlsx")


def read_cells(path, sheet_idx=0):
    """Rows as {column letter: value}, addressed by the letter in each cell's
    r="". Excel may omit an empty cell entirely *or* write it self-closing
    (`<c r="E2" s="29" t="str"/>`), so the self-closing branch of the cell
    pattern must come first — matched the other way round it reads as an open
    tag and swallows the next cell's value, shifting the row one column left."""
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
        d = {}
        for c in re.findall(r"<(?:x:)?c[^>]*/>|<(?:x:)?c[^>]*>.*?</(?:x:)?c>", r, re.S):
            ref = re.search(r'r="([A-Z]+)\d+"', c)
            if not ref:
                continue
            t = re.search(r't="(\w+)"', c)
            ins = re.search(r"<(?:x:)?is>(.*?)</(?:x:)?is>", c, re.S)
            v = re.search(r"<(?:x:)?v>(.*?)</(?:x:)?v>", c)
            if ins:   d[ref.group(1)] = re.sub(r"<[^>]+>", "", ins.group(1))
            elif v:   d[ref.group(1)] = ss[int(v.group(1))] if t and t.group(1) == "s" else v.group(1)
            else:     d[ref.group(1)] = ""
        rows.append(d)
    return rows


SIZE_RE = re.compile(r"^[\d.]+ g( each)?( / [\d.]+ g( each)?)*$")
PRICE_RE = re.compile(r"^\$[\d.]+( / \$[\d.]+)*$")


def family(row):
    """'THC - Infused' -> 'Infused'. The branch is everything before the dash."""
    return row["D"].split(" - ")[-1].strip()


def branch(row):
    return row["D"].split(" - ")[0].strip()


def size_cell(row):
    """Available Sizes is column F on every row, as the header says."""
    return row.get("F", "") or ""


def check_columns(rows):
    """Assert the sheet's layout before trusting a single value. Any drift and
    we stop rather than emit shifted products — a reader that mis-handles empty
    cells shifts whole rows one column left and still looks plausible."""
    bad = []
    for i, r in enumerate(rows, 1):
        fam, sz, price = family(r), size_cell(r), r.get("M", "")
        if not SIZE_RE.match(sz):
            bad.append("row %d: size cell %r" % (i, sz))
        if not PRICE_RE.match(price):
            bad.append("row %d: price cell %r" % (i, price))
        if len(sz.split(" / ")) != len(price.split(" / ")):
            bad.append("row %d: %d sizes but %d prices" % (i, len(sz.split(" / ")), len(price.split(" / "))))
        if fam == "Flower" and r.get("E"):
            bad.append("row %d: flower row has a concentrate type in E (%r)" % (i, r.get("E")))
        if fam != "Flower" and not r.get("E"):
            bad.append("row %d: %s row has no concentrate type in E" % (i, fam))
        if r.get("K") or r.get("L"):
            bad.append("row %d: K/L populated — expected Other Cannabinoids and Ratio to be empty" % i)
        for col in "ABCDGHIJN":
            if not r.get(col):
                bad.append("row %d: column %s empty" % (i, col))
    if bad:
        print("gen_prerolls: sheet layout changed — refusing to emit shifted data:",
              file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


# ---- photo per (type family, pack count). Jack supplied one shot for each
#      combination the catalog actually uses; the 3-pack shot goes unused
#      because nothing in these 50 is a 3-pack. ----
PHOTO = {("Flower", "1-Pack"):   "pr_flower",
         ("Flower", "2-Pack"):   "pr_flower_2pk",
         ("Flower", "20-Pack"):  "pr_flower_20pk",
         ("Infused", "1-Pack"):  "pr_infused",
         ("Infused", "2-Pack"):  "pr_infused_2pk",
         ("Trifecta", "1-Pack"): "pr_trifecta"}

# ---- The app's six lifestyles are the sheet's five Lifestyle values plus CBD,
#      renamed. Jack, 2026-08-12: "Sativa, Sativa hybrid, hybrid, Indica Hybrid,
#      Indica = Discovery, Adventurous, Social, Unwind, Nightlife in that order.
#      CBD = Holistic." A settings toggle will later swap the two vocabularies
#      for advanced users, so they must stay one-to-one. ----
LIFESTYLE = {"Sativa":        "discovery",
             "Sativa Hybrid": "adventurous",
             "Hybrid":        "social",
             "Indica Hybrid": "unwind",
             "Indica":        "nightlife",
             "CBD":           "holistic"}

# ---- Terpene, feelings and taste are not in Jack's sheet. ----
#
# REUSED: these 12 strains already exist in the flower catalog, so the app's
# terpene is taken from those rows verbatim — the same strain should not read
# differently depending on which shelf it sits on. (The lifestyle half of each
# pair is now dead: lifestyle comes from the sheet. Kept so the tables stay
# diffable against the flower catalog.)
REUSED = {
    "ACDC":              ("holistic",    "Earthy"),
    "Animal Face":       ("unwind",      "Earthy"),
    "Blue Dream":        ("discovery",   "Fruity"),
    "Harlequin":         ("holistic",    "Citrus"),
    "Hawaiian Haze":     ("holistic",    "Citrus"),
    "Jack Herer":        ("adventurous", "Piney"),
    "Lifter":            ("holistic",    "Herbal"),
    "Northern Lights":   ("unwind",      "Earthy"),
    "Permanent Marker":  ("nightlife",   "Pepper"),
    "Pineapple Express": ("social",      "Citrus"),
    "Sour Space Candy":  ("holistic",    "Citrus"),
    "Wedding Cake":      ("unwind",      "Fruity"),
}

# AUTHORED (2026-08-10): the remaining 23 strains have no flower counterpart.
# Assigned per real strain character the way the flower catalog was — GMO
# garlicky and heavy, Durban Poison bright and energizing — not randomized.
AUTHORED = {
    "Biscotti":             ("unwind",      "Earthy"),
    "Cannatonic":           ("holistic",    "Citrus"),
    "Critical Mass":        ("holistic",    "Earthy"),
    "Dancehall":            ("holistic",    "Citrus"),
    "Durban Poison":        ("adventurous", "Piney"),
    "GMO":                  ("unwind",      "Earthy"),
    "Gelato":               ("social",      "Fruity"),
    "Gushers":              ("unwind",      "Fruity"),
    "Ice Cream Cake":       ("unwind",      "Lavender"),
    "Lemon Cherry Gelato":  ("social",      "Citrus"),
    "MAC 1":                ("discovery",   "Citrus"),
    "Mimosa":               ("social",      "Citrus"),
    "Pennywise":            ("holistic",    "Pepper"),
    "RS11":                 ("discovery",   "Earthy"),
    "Rainbow Belts":        ("social",      "Fruity"),
    "Remedy":               ("holistic",    "Lavender"),
    "Ringo's Gift":         ("holistic",    "Earthy"),
    "Runtz":                ("social",      "Fruity"),
    "Sour Tsunami":         ("holistic",    "Citrus"),
    "Super Boof":           ("discovery",   "Citrus"),
    "Suver Haze":           ("holistic",    "Piney"),
    "Sweet and Sour Widow": ("holistic",    "Earthy"),
    "Zkittlez":             ("unwind",      "Fruity"),
}
STRAIN = dict(REUSED); STRAIN.update(AUTHORED)

# AUTHORED: taste chips per strain, from each strain's real terpene reputation.
TASTE = {
    "ACDC": ["Earthy", "Herbal", "Pine"],           "Animal Face": ["Pine", "Lemon", "Fuel"],
    "Biscotti": ["Cookie", "Spice", "Gas"],         "Blue Dream": ["Berry", "Citrus", "Pine"],
    "Cannatonic": ["Citrus", "Earthy", "Pine"],     "Critical Mass": ["Earthy", "Sweet", "Herbal"],
    "Dancehall": ["Citrus", "Herbal", "Spice"],     "Durban Poison": ["Anise", "Citrus", "Herbal"],
    "GMO": ["Garlic", "Earthy", "Diesel"],          "Gelato": ["Cream", "Berry", "Gas"],
    "Gushers": ["Tropical", "Cream", "Gas"],        "Harlequin": ["Mango", "Pine", "Herbal"],
    "Hawaiian Haze": ["Tropical", "Citrus", "Floral"], "Ice Cream Cake": ["Vanilla", "Dough", "Sweet"],
    "Jack Herer": ["Pine", "Lemon", "Herbal"],      "Lemon Cherry Gelato": ["Lemon", "Cherry", "Cream"],
    "Lifter": ["Herbal", "Citrus", "Earthy"],       "MAC 1": ["Citrus", "Cream", "Diesel"],
    "Mimosa": ["Orange", "Tangerine", "Floral"],    "Northern Lights": ["Earthy", "Pine", "Sweet"],
    "Pennywise": ["Pepper", "Coffee", "Sweet"],     "Permanent Marker": ["Gas", "Floral", "Spice"],
    "Pineapple Express": ["Pineapple", "Cedar", "Citrus"], "RS11": ["Gas", "Cream", "Earthy"],
    "Rainbow Belts": ["Candy", "Citrus", "Berry"],  "Remedy": ["Floral", "Herbal", "Pine"],
    "Ringo's Gift": ["Earthy", "Herbal", "Citrus"], "Runtz": ["Candy", "Fruit", "Cream"],
    "Sour Space Candy": ["Sour", "Citrus", "Candy"], "Sour Tsunami": ["Sour", "Citrus", "Earthy"],
    "Super Boof": ["Orange", "Cherry", "Spice"],    "Suver Haze": ["Pine", "Herbal", "Citrus"],
    "Sweet and Sour Widow": ["Sweet", "Sour", "Earthy"], "Wedding Cake": ["Vanilla", "Dough", "Pepper"],
    "Zkittlez": ["Grape", "Candy", "Sweet"],
}

# AUTHORED: feelings per lifestyle, matching the vocabulary the other
# generators already use for the product-page chips.
FEEL = {"discovery":   ["Creative", "Focused", "Uplifted"],
        "adventurous": ["Energetic", "Focused", "Uplifted"],
        "social":      ["Giddy", "Chatty", "Happy"],
        "unwind":      ["Relaxed", "Sleepy", "Body High"],
        "nightlife":   ["Euphoric", "Giddy", "Buzzed"],
        "holistic":    ["Calm", "Clear-Headed", "Relaxed"]}


def esc(s):
    return s.replace('"', '\\"').replace("&", "&amp;")


def sizes_and_prices(row):
    """'0.5 g / 1 g' + '$6.99 / $11.99' -> (['0.5 g','1 g'], [6.99, 11.99]).

    'each' is dropped: the IA's selectable sizes are exactly 0.5 g / 0.75 g /
    1 g, and pack count already reads in the product name ('Mimosa 20-Pack').
    """
    szs = [s.replace(" each", "").strip() for s in size_cell(row).split(" / ")]
    prices = [float(p.strip().lstrip("$")) for p in row["M"].split(" / ")]
    return szs, prices


def main():
    rows = read_cells(XLSX)[1:]
    rows = [r for r in rows if r.get("A")]
    check_columns(rows)

    out, unknown = [], set()
    for i, r in enumerate(rows):
        fam, br = family(r), branch(r)
        strain, name, brand = r["B"].strip(), r["C"].strip(), r["A"].strip()
        pack = r["G"].strip()
        szs, prices = sizes_and_prices(r)
        thc, cbd = float(r["I"]), float(r["J"])

        # The IA's Lifestyle column is Indica/Sativa/Hybrid — the app's `st`,
        # not the app's `f`. Kept verbatim, including the two hybrid variants.
        st = r["H"].strip()

        terp = STRAIN.get(strain, ("", "Earthy"))[1]
        if strain not in STRAIN:
            unknown.add(strain)
        # Lifestyle is the sheet's own Lifestyle column, renamed (Jack,
        # 2026-08-12) - not something derived here. The branch in column D is
        # the sheet's cannabinoid decision, so CBD rows are Holistic and Blend
        # rows keep their strain's lifestyle. An earlier version forced
        # Holistic at >=1% CBD, which swept the Blend family in against the
        # sheet's own classification.
        life = "holistic" if br == "CBD" else LIFESTYLE[st]

        # sub3 carries the concentrate type on Infused and the component
        # combination on Trifecta; Trifecta's is metadata, never a bubble.
        sub3 = (r.get("E") or "").strip() if fam in ("Infused", "Trifecta") else ""

        img = PHOTO.get((fam, pack))
        if not img:
            print("gen_prerolls: no photo for %s / %s (%s)" % (fam, pack, name), file=sys.stderr)
            img = "pr_flower"

        # pack count drives the serving-vs-total bubble on the tile: the size is
        # per joint, so a 2-pack of 0.5 g totals 1 g. Emitted only when there is
        # more than one joint — a 1-pack has nothing to compare.
        npk = int(re.match(r"(\d+)", pack).group(1))

        pz = ",".join('"%s":%g' % (s, p) for s, p in zip(szs, prices))
        out.append(
            ' {t:"preroll",n:"%s",b:"%s",img:"%s",pr:%g,pz:{%s},szs:["%s"],'
            'thc:%g,cbdv:%g,%s%ssub:"%s",sub2:"%s",%sst:"%s",tp:"%s",f:["%s"],'
            'sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
            % (esc(name), esc(brand), img, prices[0], pz, '","'.join(szs),
               thc, cbd, ("cbd:1," if cbd >= 1 else ""),
               ("pk:%d," % npk if npk > 1 else ""),
               br, fam, ('sub3:"%s",' % esc(sub3) if sub3 else ""),
               esc(st), terp, life,
               round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
               '","'.join(FEEL[life]), '","'.join(TASTE.get(strain, ["Earthy", "Herbal", "Pine"])),
               esc(r["N"])))

    print("\n".join(out))
    if unknown:
        print("gen_prerolls: no authored lifestyle/terpene for: %s" % ", ".join(sorted(unknown)),
              file=sys.stderr)
    fams = {}
    for r in rows:
        fams[r["D"]] = fams.get(r["D"], 0) + 1
    print("%d pre-rolls — %s" % (len(out), ", ".join("%s %d" % (k, v) for k, v in sorted(fams.items()))),
          file=sys.stderr)
    print("%d Holistic" % sum(1 for o in out if 'f:["holistic"]' in o), file=sys.stderr)


if __name__ == "__main__":
    main()
