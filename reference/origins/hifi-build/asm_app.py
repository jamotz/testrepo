#!/usr/bin/env python3
"""Assemble the Origins clickable app prototype into one self-contained file.
Run: python3 reference/origins/hifi-build/asm_app.py
Fonts: reuses Oswald from reference/oxfam/hifi-build/fontcache (fetches if missing).
Output: <scratchpad>/origins-app.html (or ./origins-app.html)."""
from PIL import Image
import base64, io, json, pathlib, re, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
assets = REPO / "reference/origins/assets"
build = pathlib.Path(__file__).resolve().parent
cache = REPO / "reference/oxfam/hifi-build/fontcache"
src = (build / "origins-app.src.html").read_text()

SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
out_dir = SCRATCH if SCRATCH.exists() else pathlib.Path(".")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# ---- fonts: Oswald only (headers); body is system Georgia ----
FACES = [("Oswald", "500"), ("Oswald", "600"), ("Oswald", "700")]
def ensure_fonts():
    cache.mkdir(exist_ok=True)
    need = [(f, w) for f, w in FACES if not (cache / f"oswald-{w}.woff2").exists()]
    if not need:
        return
    url = "https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap"
    css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode()
    picked = {}
    for b in re.findall(r"@font-face\s*\{([^}]*)\}", css):
        wt = re.search(r"font-weight:\s*(\d+)", b)
        um = re.search(r"url\((https://[^)]+\.woff2)\)", b)
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if wt and um and ur and "U+0000-00FF" in ur.group(1):
            picked[wt.group(1)] = um.group(1)
    for _, w in need:
        data = urllib.request.urlopen(urllib.request.Request(picked[w], headers={"User-Agent": UA}), timeout=30).read()
        (cache / f"oswald-{w}.woff2").write_bytes(data)

ensure_fonts()
fcss = []
for fam, wt in FACES:
    b64 = base64.b64encode((cache / f"oswald-{wt}.woff2").read_bytes()).decode()
    fcss.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{wt};'
                f'font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
src = src.replace("/*FONTS*/", "\n".join(fcss))

# ---- product images (small: phone-card scale) ----
def embed(relpath, maxw=340, q=80):
    im = Image.open(assets / relpath)
    if im.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        rgba = im.convert("RGBA")
        bg.paste(rgba, mask=rgba.split()[-1])
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

M = {
 "flower":    "product assets/flower.png",
 "gdp":       "product assets/Unproccessed Flower.jpg",
 "preroll":   "product assets/preroll.png",
 "liveresin": "product assets/Live Resin.jpeg",
 "rosin":     "product assets/Concentrate (Rosin).png",
 "sugar":     "product assets/Sugar.webp",
 "thca":      "product assets/THC-A Crystals.png",
 "badder":    "product assets/Butter Concentrate.png",
 "hash":      "product assets/hash.jpeg",
 "keif":      "product assets/keif.jpeg",
 "gummy":     "product assets/Gummy Edibles.png",
 "gummy2":    "product assets/Gummy Edibles.webp",
 "choc":      "product assets/Chocolate Edible.png",
 "vape":      "product assets/vape.png",
 "topical":   "product assets/topical.png",
}
IMG = {}
for k, rel in M.items():
    try:
        IMG[k] = embed(rel)
    except Exception as e:
        print("WARN", k, rel, e)
src = src.replace("/*IMGMAP*/", json.dumps(IMG))

# ---- entity-encode outside script/style ----
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(x if (x[:7] == '<script' or x[:6] == '<style')
              else x.encode('ascii', 'xmlcharrefreplace').decode() for x in segs)

out = out_dir / "origins-app.html"
out.write_text(src)
print(f"wrote {out} ({len(src)//1024} KB); imgs={len(IMG)}; markers left={src.count('/*IMGMAP*/')+src.count('/*FONTS*/')}")
