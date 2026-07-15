#!/usr/bin/env python3
"""Assemble the Oxfam landing carbon-copy artifact: embed fonts + header/map images.
Run from anywhere: python3 reference/oxfam/hifi-build/asm_landing.py
Fonts (Oswald, Open Sans) are fetched from Google Fonts once and cached durably
in ./fontcache so later runs work offline.
Output: <scratchpad>/oxfam-landing.html (or ./oxfam-landing.html)."""
from PIL import Image
import base64, io, pathlib, re, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
ref = REPO / "reference/oxfam"
build = pathlib.Path(__file__).resolve().parent
cache = build / "fontcache"; cache.mkdir(exist_ok=True)
src = (build / "oxfam-landing.src.html").read_text()

SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
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
css = gf_css()
blocks = re.findall(r"@font-face\s*\{([^}]*)\}", css)
picked = {}  # (fam,wt) -> woff2 url  (latin subset only)
for b in blocks:
    fam = re.search(r"font-family:\s*'([^']+)'", b)
    wt = re.search(r"font-weight:\s*(\d+)", b)
    urlm = re.search(r"url\((https://[^)]+\.woff2)\)", b)
    ur = re.search(r"unicode-range:\s*([^;]+);", b)
    if not (fam and wt and urlm and ur):
        continue
    key = (fam.group(1), wt.group(1))
    # latin subset is the block whose range includes U+0000-00FF
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

# ---- images ----
def embed(relpath, maxw, q=82):
    im = Image.open(ref / relpath)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

src = src.replace("%%HEADER_IMG%%", embed("process/Account back.jpeg", 1400, 80))
src = src.replace("%%MAP_IMG%%", embed("process/Screen Shot 2022-11-02 at 4.55.51 PM.png", 1000, 82))

# ---- entity-encode everything outside <script>/<style> ----
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(x if (x[:7] == '<script' or x[:6] == '<style')
              else x.encode('ascii', 'xmlcharrefreplace').decode() for x in segs)

out = out_dir / "oxfam-landing.html"
out.write_text(src)
markers = src.count("%%") + src.count("/*FONTS*/")
print(f"wrote {out} ({len(src)//1024} KB); fonts={len(fcss)}; markers left={markers}")
