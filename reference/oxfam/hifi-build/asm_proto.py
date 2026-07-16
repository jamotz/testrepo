#!/usr/bin/env python3
"""Assemble the Oxfam clickable prototype (mini-site) into one self-contained file.
Run: python3 reference/oxfam/hifi-build/asm_proto.py
Uses fonts cached by asm_landing.py (fontcache/); embeds sunset + map images.
Output: <scratchpad>/oxfam-proto.html (or ./oxfam-proto.html)."""
from PIL import Image
import base64, io, pathlib, re, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
ref = REPO / "reference/oxfam"
build = pathlib.Path(__file__).resolve().parent
cache = build / "fontcache"; cache.mkdir(exist_ok=True)
src = (build / "oxfam-proto.src.html").read_text()

SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
out_dir = SCRATCH if SCRATCH.exists() else pathlib.Path(".")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# ---- fonts: reuse cache; fetch latin subset if missing ----
FACES = [("Oswald", "500"), ("Oswald", "600"), ("Oswald", "700"),
         ("Open Sans", "400"), ("Open Sans", "600"), ("Open Sans", "700")]

def ensure_fonts():
    need = [(f, w) for f, w in FACES if not (cache / f"{f.lower().replace(' ', '-')}-{w}.woff2").exists()]
    if not need:
        return
    url = ("https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700"
           "&family=Open+Sans:wght@400;600;700&display=swap")
    css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode()
    picked = {}
    for b in re.findall(r"@font-face\s*\{([^}]*)\}", css):
        fam = re.search(r"font-family:\s*'([^']+)'", b); wt = re.search(r"font-weight:\s*(\d+)", b)
        um = re.search(r"url\((https://[^)]+\.woff2)\)", b); ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if fam and wt and um and ur and (fam.group(1), wt.group(1)) in need and "U+0000-00FF" in ur.group(1):
            picked[(fam.group(1), wt.group(1))] = um.group(1)
    for (f, w) in need:
        data = urllib.request.urlopen(urllib.request.Request(picked[(f, w)], headers={"User-Agent": UA}), timeout=30).read()
        (cache / f"{f.lower().replace(' ', '-')}-{w}.woff2").write_bytes(data)

ensure_fonts()
fcss = []
for fam, wt in FACES:
    b = base64.b64encode((cache / f"{fam.lower().replace(' ', '-')}-{wt}.woff2").read_bytes()).decode()
    fcss.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{wt};'
                f'font-display:swap;src:url(data:font/woff2;base64,{b}) format("woff2")}}')
src = src.replace("/*FONTS*/", "\n".join(fcss))

# ---- images ----
def embed(relpath, maxw, q=80):
    im = Image.open(ref / relpath)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

src = src.replace("%%SUNSET%%", embed("process/Account back.jpeg", 1200, 78))
src = src.replace("%%MAP%%", embed("process/Screen Shot 2022-11-02 at 4.55.51 PM.png", 1000, 82))

# ---- entity-encode everything outside <script>/<style> ----
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(x if (x[:7] == '<script' or x[:6] == '<style')
              else x.encode('ascii', 'xmlcharrefreplace').decode() for x in segs)

out = out_dir / "oxfam-proto.html"
out.write_text(src)
print(f"wrote {out} ({len(src)//1024} KB); markers left={src.count('%%') + src.count('/*FONTS*/')}")
