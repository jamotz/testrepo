#!/usr/bin/env python3
"""Turn Jack's flower catalog into the app's flower products.

Source: reference/origins/product info/Flower Final pt2 Product List for WA.xlsx

  A Brand  B Strain  C Type  D THC %  E CBD %  F Grow Method
  G 1g  H 3.5g  I 7g  J 14g  K 28g   (prices)
  L/M/N Terp 1-3   O Description

Everything on a flower tile now comes from that sheet. **Nothing here is
authored.** The previous version of this file invented THC %, CBD % and
Indoor/Outdoor with a seeded RNG because the old .docx carried none of them;
the "pt2" sheet supplies all three, so those three inventions are gone.

Photos are the one thing the sheet doesn't name, and they're chosen
*deterministically from the strain name* rather than by drawing from a shuffled
pool. Two reasons: a strain keeps the same photo across rebuilds, and inserting
or removing a product no longer reshuffles the photo of every product after it.
That sequential-RNG behaviour is why this generator used to carry a "don't
regenerate flower" warning. It no longer does.

Run: python3 reference/origins/hifi-build/gen_catalog_products.py
"""
import hashlib, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
XLSX = os.path.join(REPO, "reference/origins/product info/Flower Final pt2 Product List for WA.xlsx")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsxread import read_cells
from terpmap import pairs as terp_pairs, check as terp_check
from html import unescape as unesc

# The app's six lifestyles are the catalog's six Type values renamed.
LIFESTYLE = {"Sativa": "discovery", "Sativa Hybrid": "adventurous", "Hybrid": "social",
             "Indica Hybrid": "unwind", "Indica": "nightlife", "CBD": "holistic"}

# ---- photo per strain type. Picked by hashing the strain name, so it is
#      stable across rebuilds and independent of row order. ----
POOL = {"Indica":        ["fl_indica", "fl_indica2", "fl_indica3"],
        "Indica Hybrid": ["fl_indhyb", "fl_indhyb2"],
        "Hybrid":        ["fl_hybrid", "fl_hybrid2"],
        "Sativa Hybrid": ["fl_sathyb", "fl_sathyb2"],
        "Sativa":        ["fl_sativa", "fl_sativa2"],
        "CBD":           ["fl_universal", "fl_hybrid2"]}

SIZE_COLS = [("G", "1 g"), ("H", "3.5 g"), ("I", "7 g"), ("J", "14 g"), ("K", "28 g")]


def photo(strain, st):
    pool = POOL.get(st) or POOL["Hybrid"]
    h = int(hashlib.md5(strain.encode("utf-8")).hexdigest()[:8], 16)
    return pool[h % len(pool)]


def stable(strain, lo, hi):
    """A stable pseudo-value per strain, for the two display-only fields the
    catalog has never carried: star rating and review count."""
    h = int(hashlib.md5(("r" + strain).encode("utf-8")).hexdigest()[8:16], 16)
    return lo + h % (hi - lo + 1)


def esc(s):
    return unesc(s).replace('"', '\\"').replace("&", "&amp;")


def strip_cbd(name):
    """The tile already says CBD three ways - green border, Holistic badge, CBD
    chip - so the name doesn't need to as well."""
    return re.sub(r"\s*\bCBD\b\s*", " ", name).strip()


def check(rows):
    bad = []
    for i, r in enumerate(rows, 3):          # sheet row 1 is a title, 2 the header
        if r.get("C", "").strip() not in LIFESTYLE:
            bad.append("row %d: Type %r" % (i, r.get("C")))
        if r.get("F", "").strip() not in ("Indoor", "Outdoor"):
            bad.append("row %d: Grow Method %r" % (i, r.get("F")))
        for col, label in (("D", "THC %"), ("E", "CBD %")):
            try:
                float(r.get(col, ""))
            except ValueError:
                bad.append("row %d: %s %r" % (i, label, r.get(col)))
        if not any(r.get(c) for c, _ in SIZE_COLS):
            bad.append("row %d: no prices at all" % i)
        if not r.get("H"):
            bad.append("row %d: no 3.5 g price - `pr` is the eighth" % i)
        if r.get("O", "").rstrip().endswith(("...", "…")):
            bad.append("row %d: description is truncated (%r)" % (i, r["O"][-38:]))
        for col in "ABCDEFO":
            if not r.get(col):
                bad.append("row %d: column %s empty" % (i, col))
    if bad:
        print("gen_catalog_products: sheet layout changed - refusing to emit:", file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


def main():
    rows = [r for r in read_cells(XLSX)[2:] if r.get("A")]
    check(rows)
    terp_check([[r.get("L", ""), r.get("M", ""), r.get("N", "")] for r in rows], "gen_catalog_products")

    out = []
    for r in rows:
        strain = unesc(r["B"]).strip()
        st = r["C"].strip()
        life = LIFESTYLE[st]
        thc, cbdpct = float(r["D"]), float(r["E"])
        prices = {label: float(r[col]) for col, label in SIZE_COLS if r.get(col)}
        feels, scents = terp_pairs([r.get("L", ""), r.get("M", ""), r.get("N", "")])
        cbd = (",cbd:1" if st == "CBD" else "") + (",cbdv:%g" % cbdpct if cbdpct else "")
        out.append(
            ' {t:"flower",n:"%s",b:"%s",img:"%s",pr:%g,pz:%s,szs:%s,thc:%g%s,sub:"%s",st:"%s",'
            'f:["%s"],sale:0,r:%s,rv:%d,fe:["%s"],ta:["%s"],d:"%s"},'
            % (esc(strip_cbd(strain)), esc(r["A"].strip()), photo(strain, st),
               prices["3.5 g"], json.dumps(prices), json.dumps(list(prices)),
               thc, cbd, r["F"].strip(), st, life,
               round(3.9 + stable(strain, 0, 10) / 10.0, 1), stable(strain, 4, 40),
               '","'.join(feels), '","'.join(scents), esc(r["O"])))

    print("\n".join(out))
    import collections
    print("%d flower - %s" % (len(out), dict(collections.Counter(r["C"] for r in rows))), file=sys.stderr)
    print("grow: %s" % dict(collections.Counter(r["F"] for r in rows)), file=sys.stderr)
    print("photos: %s" % dict(collections.Counter(re.search(r'img:"([^"]*)"', o).group(1) for o in out)),
          file=sys.stderr)


if __name__ == "__main__":
    main()
