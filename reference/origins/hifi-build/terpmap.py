#!/usr/bin/env python3
"""Terpenes -> the app's feelings and scents.

Jack's product sheets name three terpenes per product (Terp 1/2/3). The app
shows three feelings and three smell/taste chips. `cannabis_terpene_mapping.xlsx`
is the bridge: every terpene has three (Feeling, Smell & Taste) pairs ranked
Primary / Secondary / Tertiary.

**Each terpene contributes its PRIMARY pair**, in Terp 1/2/3 order. That is the
reading the sheets were authored for, and it is checkable rather than a guess:
across all 160 products in the three smokeable catalogs it yields three distinct
feelings and three distinct scents *every time*. The alternative reading —
Terp 1 -> Primary, Terp 2 -> Secondary, Terp 3 -> Tertiary — collides on 56% of
products, repeating a feeling within the same tile.

Secondary and Tertiary are therefore unused today. They are not dead: they are
what a product with fewer than three terpenes would fall back to (`pairs()`
below does this), and nothing else in the app can supply that.

Vocabulary: the mapping only ever emits terms from `cannabis_feelings.xlsx` (14)
and `cannabis_smell_taste.xlsx` (16), which are exactly the 30 icons in
`assets/scents assets/icons/`. `check()` asserts that on every run.
"""
import os, re, sys, zipfile
from html import unescape

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
INFO = os.path.join(REPO, "reference/origins/product info")

from xlsxread import read_cells

ORDER = ("Primary", "Secondary", "Tertiary")


def _load():
    m = {}
    for r in read_cells(os.path.join(INFO, "cannabis_terpene_mapping.xlsx"))[1:]:
        if not r.get("A"):
            continue
        m[(unescape(r["A"]).strip(), unescape(r["B"]).strip())] = (
            unescape(r["C"]).strip(), unescape(r["D"]).strip())
    return m


MAP = _load()
TERPENES = sorted({k[0] for k in MAP})


def _vocab(fname):
    return [unescape(r["A"]).strip() for r in read_cells(os.path.join(INFO, fname))[1:] if r.get("A")]


FEELINGS = _vocab("cannabis_feelings.xlsx")
SCENTS = _vocab("cannabis_smell_taste.xlsx")


def pairs(terps):
    """[terpene, ...] -> ([feeling x3], [scent x3]).

    Normally one terpene per tier, each giving its Primary pair. If a product
    names fewer than three terpenes, the last one is walked down its own
    Secondary and Tertiary rows rather than repeating its Primary.
    """
    terps = [t.strip() for t in terps if t and t.strip()]
    if not terps:
        return None, None
    out = []
    for i in range(3):
        if i < len(terps):
            key = (terps[i], "Primary")
        else:                                   # short list: extend the last terpene
            key = (terps[-1], ORDER[i - len(terps) + 1])
        if key not in MAP:
            raise KeyError("no mapping row for %r" % (key,))
        out.append(MAP[key])
    # a short list can still collide; drop repeats rather than show a term twice
    feels, scents = [], []
    for f, s in out:
        if f not in feels:
            feels.append(f)
        if s not in scents:
            scents.append(s)
    return feels, scents


def check(rows_terps, label):
    """Assert the mapping covers everything the catalog names, and that the
    result never repeats a term inside one product."""
    bad = []
    for i, terps in enumerate(rows_terps, 1):
        named = [t for t in terps if t and t.strip()]
        for t in named:
            if (t.strip(), "Primary") not in MAP:
                bad.append("row %d: terpene %r is not in the mapping" % (i, t))
        if not named:
            bad.append("row %d: no terpenes named" % i)
            continue
        f, s = pairs(terps)
        if len(f) < 3 or len(s) < 3:
            bad.append("row %d: %r collapsed to %d feelings / %d scents" % (i, named, len(f), len(s)))
        for v in f:
            if v not in FEELINGS:
                bad.append("row %d: feeling %r is outside cannabis_feelings.xlsx" % (i, v))
        for v in s:
            if v not in SCENTS:
                bad.append("row %d: scent %r is outside cannabis_smell_taste.xlsx" % (i, v))
    if bad:
        print("%s: terpene mapping problems - refusing to emit:" % label, file=sys.stderr)
        for b in bad[:20]:
            print("   " + b, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("%d terpenes, %d feelings, %d scents" % (len(TERPENES), len(FEELINGS), len(SCENTS)))
    for t in TERPENES:
        print("  %-14s %s" % (t, " | ".join("%s=%s/%s" % (s, *MAP[(t, s)]) for s in ORDER)))
