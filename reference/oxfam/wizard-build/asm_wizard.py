#!/usr/bin/env python3
"""Assemble the ONE combined Oxfam wizard artifact (landing/FAQ/feedback as
in-page screens toggled by nav(), not three separate artifacts).
Run from anywhere: python3 reference/oxfam/wizard-build/asm_wizard.py
Fonts (Oswald, Open Sans) are fetched from Google Fonts once and cached
durably in ./fontcache so later runs work offline.
Output: <scratchpad>/oxfam-wizard.html (or ./oxfam-wizard.html)."""
from PIL import Image
import base64, io, os, pathlib, re, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
ref = REPO / "reference/oxfam"
build = pathlib.Path(__file__).resolve().parent
cache = build / "fontcache"; cache.mkdir(exist_ok=True)
src = (build / "wizard.src.html").read_text()

SCRATCH = pathlib.Path(os.environ.get("CLAUDE_SCRATCHPAD", ""))
out_dir = SCRATCH if SCRATCH.exists() else pathlib.Path(".")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# ---- fonts: parse Google Fonts css2, grab the latin subset per family/weight ----
def gf_css():
    url = ("https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700"
           "&family=Open+Sans:wght@400;600;700&display=swap")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode()

want = {("Oswald", "500"), ("Oswald", "600"), ("Oswald", "700"),
        ("Open Sans", "400"), ("Open Sans", "600"), ("Open Sans", "700")}
missing_cache = any(not (cache / f"{fam.lower().replace(' ', '-')}-{wt}.woff2").exists() for fam, wt in want)
picked = {}
if missing_cache:
    css = gf_css()
    blocks = re.findall(r"@font-face\s*\{([^}]*)\}", css)
    for b in blocks:
        fam = re.search(r"font-family:\s*'([^']+)'", b)
        wt = re.search(r"font-weight:\s*(\d+)", b)
        urlm = re.search(r"url\((https://[^)]+\.woff2)\)", b)
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if not (fam and wt and urlm and ur):
            continue
        key = (fam.group(1), wt.group(1))
        if key in want and "U+0000-00FF" in ur.group(1):
            picked[key] = urlm.group(1)
    assert want <= set(picked), f"missing faces: {want - set(picked)}"

def font_b64(fam, wt):
    fn = cache / f"{fam.lower().replace(' ', '-')}-{wt}.woff2"
    if not fn.exists():
        req = urllib.request.Request(picked[(fam, wt)], headers={"User-Agent": UA})
        fn.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return base64.b64encode(fn.read_bytes()).decode()

fcss = []
for fam, wt in [("Oswald", "500"), ("Oswald", "600"), ("Oswald", "700"),
                ("Open Sans", "400"), ("Open Sans", "600"), ("Open Sans", "700")]:
    b = font_b64(fam, wt)
    fcss.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{wt};'
                f'font-display:swap;src:url(data:font/woff2;base64,{b}) format("woff2")}}')
src = src.replace("/*FONTS*/", "\n".join(fcss))

# ---- logo (real traced SVG, inlined so it scales crisply in the header) ----
logo = (ref / "logos/oxfam-logo-horizontal.svg").read_text()
logo = re.sub(r'<svg ', '<svg class="logo" ', logo, count=1)
src = src.replace("<!--LOGO-->", logo)

# ---- images ----
def embed(relpath, maxw, q=82):
    im = Image.open(ref / relpath)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

def embed_crop_square(relpath, box, maxw, q=82):
    """box = (left, top, right, bottom) in source pixels; crops then embeds as PNG (keeps transparency)."""
    im = Image.open(ref / relpath)
    im = im.crop(box)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

def embed_crop(relpath, box, maxw, q=82):
    """box = (left, top, right, bottom) in source pixels; crops then embeds as JPEG."""
    im = Image.open(ref / relpath)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im = im.crop(box)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

src = src.replace("%%HERO_IMG%%", embed("photos/hill.webp", 1400, 80))
src = src.replace("%%MAP_IMG%%", embed("photos/Australia Map.png", 1000, 82))
src = src.replace("%%FAQ_IMG%%", embed("photos/FAQ photo.webp", 900, 82))
src = src.replace("%%FEEDBACK_IMG%%", embed("photos/Volunteer Photo.jpeg", 1400, 80))
src = src.replace("%%YOUTUBE_IMG%%", embed("photos/Media - Youtube Photo.png", 1200, 82))
src = src.replace("%%EVENT1_IMG%%", embed("photos/Fundraiser Photo 3.png", 700, 82))
src = src.replace("%%EVENT2_IMG%%", embed("photos/Fundraiser Photo.png", 700, 82))
src = src.replace("%%FB_COVER_IMG%%", embed_crop("photos/Media - Facebook Photo.png", (0, 0, 2192, 745), 1200, 82))
src = src.replace("%%FB_AVATAR_IMG%%", embed_crop_square("logos/OxFam Logo w: Background.png", (0, 50, 400, 450), 160))
src = src.replace("%%EXPERTS_IMG%%", embed("photos/Media Photo.png", 700, 82))
src = src.replace("%%CONTACT_IMG%%", embed("photos/Media Contact Headshot 2.png", 300, 84))
src = src.replace("%%REPORT_IMG%%", embed("photos/Report Photo.jpeg", 1200, 80))
src = src.replace("%%PORTAL_IMG%%", embed("photos/OxFam Portal Photo.webp", 700, 82))

# ---- entity-encode everything outside <script>/<style> ----
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(x if (x[:7] == '<script' or x[:6] == '<style')
              else x.encode('ascii', 'xmlcharrefreplace').decode() for x in segs)

out = out_dir / "oxfam-wizard.html"
out.write_text(src)
markers = src.count("%%") + src.count("/*FONTS*/") + src.count("<!--LOGO-->")
print(f"wrote {out} ({len(src)//1024} KB); fonts={len(fcss)}; markers left={markers}")
