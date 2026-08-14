#!/usr/bin/env python3
"""Turn Jack's pre-roll catalog into the app's pre-roll products.

Source (reference/origins/product info/):
  - WA_PreRolls_IA_Condensed.xlsx        the filter IA + the rules sheet
  - Pre-roll Product List Final for WA.xlsx   the 60 products

Filter path (from the IA): Pre-Rolls -> cannabinoid branch (THC / CBD / Blend)
-> type (Flower / Infused / Trifecta) -> concentrate type, Infused only. Size
stays a Filter-drawer facet because products don't exist in all three sizes.

  sub  = THC / CBD / Blend        (before the dash in column C)
  sub2 = Flower / Infused / Trifecta   (after it)
  sub3 = concentrate type on Infused; the component combination on Trifecta,
         which the IA calls metadata rather than navigation — so nothing ever
         renders a Trifecta sub3 bubble and it only shows in the breadcrumb.

Feelings and smell/taste come from the sheet's three terpenes via
`terpmap.py`; nothing is authored here. Ratios are deliberately absent: the IA
reserves them for standardized-dose formats and says to display actual THC %
and CBD % for Blend instead.

Column layout (this sheet states it correctly, unlike the previous one):
  A Brand  B Product Name  C Type  D Concentrate Type  E Available Sizes
  F Pack Count  G Lifestyle  H THC %  I CBD %  J WA Retail Price
  K Description  L/M/N Terp 1-3

Sizes: the sheet writes "0.5 g each" on multi-packs and a bare size on 1-packs.
`szs` and `pz` store the size **bare** either way, so the Filter drawer keeps
the IA's three options rather than growing to six; the tile appends "each"
itself from `pk`. See design-decisions.md.

Run: python3 reference/origins/hifi-build/gen_prerolls.py
"""
import os, re, sys, zipfile
from html import unescape as unesc

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/Pre-roll Product List Final for WA.xlsx")


from xlsxread import read_cells
from terpmap import pairs as terp_pairs, check as terp_check

SIZE_RE = re.compile(r"^[\d.]+ g( each)?( / [\d.]+ g( each)?)*$")
PRICE_RE = re.compile(r"^\$[\d.]+( / \$[\d.]+)*$")

# ---- The app's six lifestyles are the sheet's Lifestyle column renamed ----
LIFESTYLE = {"Sativa":        "discovery",
             "Sativa Hybrid": "adventurous",
             "Hybrid":        "social",
             "Indica Hybrid": "unwind",
             "Indica":        "nightlife",
             "CBD":           "holistic"}

# ---- photo per (type family, pack count) ----
PHOTO = {("Flower", "1-Pack"):    "pr_flower",
         ("Flower", "2-Pack"):    "pr_flower_2pk",
         ("Flower", "3-Pack"):    "pr_flower_3pk",
         ("Flower", "20-Pack"):   "pr_flower_20pk",
         ("Infused", "1-Pack"):   "pr_infused",
         ("Infused", "2-Pack"):   "pr_infused_2pk",
         ("Infused", "3-Pack"):   "pr_infused_2pk",
         ("Infused", "20-Pack"):  "pr_flower_20pk",
         ("Trifecta", "1-Pack"):  "pr_trifecta",
         ("Trifecta", "2-Pack"):  "pr_infused_2pk",
         ("Trifecta", "3-Pack"):  "pr_infused_2pk"}


def family(row):
    return row["C"].split(" - ")[-1].strip()


def branch(row):
    return row["C"].split(" - ")[0].strip()


def check_columns(rows):
    """Assert the sheet's layout before trusting a single value. A reader that
    mishandles empty cells shifts whole rows one column left and still looks
    plausible, so this re-runs on every invocation."""
    bad = []
    for i, r in enumerate(rows, 2):
        sz, price = r.get("E", ""), r.get("J", "")
        if not SIZE_RE.match(sz):
            bad.append("row %d: size cell %r" % (i, sz))
        if not PRICE_RE.match(price):
            bad.append("row %d: price cell %r" % (i, price))
        if len(sz.split(" / ")) != len(price.split(" / ")):
            bad.append("row %d: %d sizes but %d prices" % (i, len(sz.split(" / ")), len(price.split(" / "))))
        if branch(r) not in ("THC", "CBD", "Blend"):
            bad.append("row %d: cannabinoid branch %r" % (i, r.get("C")))
        if family(r) not in ("Flower", "Infused", "Trifecta"):
            bad.append("row %d: type %r" % (i, r.get("C")))
        if family(r) == "Flower" and r.get("D"):
            bad.append("row %d: flower row has a concentrate type in D (%r)" % (i, r.get("D")))
        if family(r) != "Flower" and not r.get("D"):
            bad.append("row %d: %s row has no concentrate type in D" % (i, family(r)))
        if r.get("G", "").strip() not in LIFESTYLE:
            bad.append("row %d: lifestyle %r" % (i, r.get("G")))
        # a re-export once clipped every description to 80 chars
        if r.get("K", "").rstrip().endswith(("...", "…")):
            bad.append("row %d: description is truncated (%r)" % (i, r["K"][-38:]))
        for col in "ABCEFGHIJK":
            if not r.get(col):
                bad.append("row %d: column %s empty" % (i, col))
    if bad:
        print("gen_prerolls: sheet layout changed — refusing to emit shifted data:",
              file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


def esc(s):
    return unesc(s).replace('"', '\\"').replace("&", "&amp;")


def sizes_and_prices(row):
    """'0.5 g each' + '$8.99' -> (['0.5 g'], [8.99]).

    "each" is dropped from the stored size: the IA's selectable sizes are
    exactly 0.5 g / 0.75 g / 1 g, and keeping "each" would put six options in
    the Filter drawer instead of three. The tile re-adds it from `pk`.
    """
    szs = [s.replace(" each", "").strip() for s in row["E"].split(" / ")]
    prices = [float(p.strip().lstrip("$")) for p in row["J"].split(" / ")]
    return szs, prices


def main():
    rows = [r for r in read_cells(XLSX)[1:] if r.get("A")]
    check_columns(rows)
    terp_check([[r.get("L", ""), r.get("M", ""), r.get("N", "")] for r in rows], "gen_prerolls")

    out, nophoto = [], set()
    for i, r in enumerate(rows):
        fam, br = family(r), branch(r)
        name, brand = unesc(r["B"]).strip(), unesc(r["A"]).strip()
        pack = r["F"].strip()
        szs, prices = sizes_and_prices(r)
        thc, cbd = float(r["H"]), float(r["I"])
        st = r["G"].strip()
        life = LIFESTYLE[st]
        feels, scents = terp_pairs([r.get("L", ""), r.get("M", ""), r.get("N", "")])

        sub3 = (r.get("D") or "").strip() if fam in ("Infused", "Trifecta") else ""

        img = PHOTO.get((fam, pack))
        if not img:
            nophoto.add((fam, pack))
            img = "pr_flower"

        npk = int(re.match(r"(\d+)", pack).group(1))

        pz = ",".join('"%s":%g' % (s, p) for s, p in zip(szs, prices))
        out.append(
            ' {t:"preroll",n:"%s",b:"%s",img:"%s",pr:%g,pz:{%s},szs:["%s"],'
            'thc:%g,cbdv:%g,%s%ssub:"%s",sub2:"%s",%sst:"%s",f:["%s"],'
            'sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
            % (esc(name), esc(brand), img, prices[0], pz, '","'.join(szs),
               thc, cbd, ("cbd:1," if cbd >= 1 else ""),
               ("pk:%d," % npk if npk > 1 else ""),
               br, fam, ('sub3:"%s",' % esc(sub3) if sub3 else ""),
               esc(st), life,
               round(4.0 + (i % 10) * 0.1, 1), 6 + (i * 7) % 33,
               '","'.join(feels), '","'.join(scents), esc(r["K"])))

    print("\n".join(out))
    import collections
    fams = collections.Counter(r["C"] for r in rows)
    print("%d pre-rolls — %s" % (len(out), ", ".join("%s %d" % (k, v) for k, v in sorted(fams.items()))),
          file=sys.stderr)
    print("%d Holistic" % sum(1 for o in out if 'f:["holistic"]' in o), file=sys.stderr)
    print("photos: %s" % dict(collections.Counter(re.search(r'img:"([^"]*)"', o).group(1) for o in out)),
          file=sys.stderr)
    if nophoto:
        print("gen_prerolls: no photo for %s" % sorted(nophoto), file=sys.stderr)


if __name__ == "__main__":
    main()
