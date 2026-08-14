#!/usr/bin/env python3
"""The one xlsx reader every generator uses.

Rows come back as {column letter: value}, addressed by the letter in each cell's
r="" rather than by position. Two separate hazards make that necessary:

1. Excel omits empty cells entirely, so appending in document order silently
   shifts every column after a blank.
2. Excel also writes empty cells self-closing (`<c r="E2" s="29" t="str"/>`).
   A cell pattern that tries `<c…>.*?</c>` before `<c…/>` matches the
   self-closing tag as an *open* tag and swallows the next cell's value — the
   same one-column shift, but silent even when addressing by letter. The
   self-closing branch must come first.

(2) was live in all four generators until 2026-08-12 and produced two days of
"this sheet's columns don't match its header" notes about a sheet that was
correctly laid out the whole time. See design-decisions.md.
"""
import re, zipfile


def read_cells(path, sheet_idx=0):
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
