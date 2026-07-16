#!/usr/bin/env python3
"""Resize the Oxfam source screenshots into real JPEG assets under
site/public/work/oxfam/ so the Astro case-study page can reference them by URL
(no base64 in source). Run from repo root: python3 reference/oxfam/hifi-build/gen_site_images.py
"""
from PIL import Image
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
ref = REPO / "reference/oxfam"
out = REPO / "site/public/work/oxfam"
out.mkdir(parents=True, exist_ok=True)

M = {
 "hero":       ("process/hill.webp", 1600, 80),
 "persona":    ("process/Screen Shot 2023-10-06 at 12.48.30 PM.png", 1200, 84),
 "wf_ia":      ("process/Screen Shot 2023-09-30 at 2.48.04 PM.png", 1200, 86),
 "wf_landing": ("process/Screen Shot 2023-09-30 at 2.52.45 PM.png", 1200, 86),
 "wf_portal":  ("process/Screen Shot 2023-11-07 at 2.18.07 PM.png", 1200, 86),
 "annotated":  ("process/Screen Shot 2022-12-18 at 7.08.08 PM.png", 1300, 84),
 "home":       ("page-00-landing/Landing Page 2022-12-18 at 6.00.15 PM.png", 1200, 82),
 "faq":        ("page-01/FAQ 2022-12-18 at 6.14.15 PM.png", 1100, 82),
 "feedback":   ("page-02/Feedback 2022-12-18 at 6.21.18 PM.png", 1100, 82),
 "myoxfam":    ("page-03/MyOxfam 2022-12-18 at 6.21.52 PM.png", 1100, 82),
 "portal":     ("page-03/MyOxfam Portal 2022-12-18 at 6.23.43 PM.png", 1200, 82),
 "fundraising":("page-04/Fundraising 2022-12-18 at 7.19.09 PM.png", 1100, 82),
 "media":      ("page-05/Media 2022-12-18 at 7.20.00 PM.png", 1100, 82),
 "report":     ("page-06/Report 2022-12-18 at 6.25.48 PM.png", 1100, 82),
}

for key, (rel, maxw, q) in M.items():
    im = Image.open(ref / rel)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    dst = out / f"{key}.jpg"
    im.save(dst, "JPEG", quality=q, optimize=True)
    print(f"{key:12s} -> {dst.relative_to(REPO)}  ({dst.stat().st_size//1024} KB, {im.width}x{im.height})")
