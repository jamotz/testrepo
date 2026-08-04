#!/usr/bin/env python3
"""Assemble the Origins clickable app prototype into one self-contained file.
Run: python3 reference/origins/hifi-build/asm_app.py
Fonts: reuses Oswald from reference/oxfam/hifi-build/fontcache (fetches if missing).
Output: <scratchpad>/origins-app.html (or ./origins-app.html)."""
from PIL import Image, ImageChops
import base64, io, json, pathlib, re, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
assets = REPO / "reference/origins/assets"
build = pathlib.Path(__file__).resolve().parent
cache = REPO / "reference/oxfam/hifi-build/fontcache"
src = (build / "origins-app.src.html").read_text()

# Write the assembled artifact to the session scratchpad (path changes each session/recycle),
# discovered by glob so it never hardcodes a stale session id; fall back to CWD.
_scratch = sorted(pathlib.Path("/tmp/claude-0").glob("*/*/scratchpad"))
out_dir = _scratch[-1] if _scratch else pathlib.Path(".")
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

def embed_rgba(relpath, maxw=400):
    """Embed a pre-cut transparent product photo as-is (keeps the alpha channel;
    no white flatten). Used for the background-free product photos."""
    im = Image.open(assets / relpath).convert("RGBA")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "WEBP", quality=86, method=6)   # alpha kept, far smaller than PNG
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()

def embed_cut(relpath, maxw=400, thr=238, mode="flood"):
    """Knock out a flat near-white background to transparent. mode="flood"
    (default) flood-fills from the image edges, so only the *surrounding*
    background is removed and light areas *inside* the product (white crystals,
    pale gummies) survive. mode="global" removes every near-white pixel — use it
    only for products saturated enough that no interior reads as white (e.g.
    colored gummies), where the background is also trapped between the product.
    Returns a transparent PNG data URI. Not for photographic backgrounds."""
    from collections import deque
    im = Image.open(assets / relpath).convert("RGBA")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    w, h = im.size
    px = im.load()
    def is_bg(x, y):
        r, g, b, a = px[x, y]
        return a > 0 and r >= thr and g >= thr and b >= thr
    if mode == "global":
        for y in range(h):
            for x in range(w):
                if is_bg(x, y):
                    r, g, b, a = px[x, y]; px[x, y] = (r, g, b, 0)
        b = io.BytesIO(); im.save(b, "PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    dq = deque()
    for x in range(w):
        if is_bg(x, 0): dq.append((x, 0))
        if is_bg(x, h - 1): dq.append((x, h - 1))
    for y in range(h):
        if is_bg(0, y): dq.append((0, y))
        if is_bg(w - 1, y): dq.append((w - 1, y))
    seen = bytearray(w * h)
    while dq:
        x, y = dq.popleft()
        i = y * w + x
        if seen[i]: continue
        seen[i] = 1
        if not is_bg(x, y): continue
        r, g, b, a = px[x, y]; px[x, y] = (r, g, b, 0)
        if x > 0: dq.append((x - 1, y))
        if x < w - 1: dq.append((x + 1, y))
        if y > 0: dq.append((x, y - 1))
        if y < h - 1: dq.append((x, y + 1))
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

M = {
 # extra bud photos (no white-bg original; resolved via NOBG -> embed_rgba)

 # concentrate consistency photos (Jack's uploads, named by sub-filter)
 "cd_oil": "product assets/Concentrate/Distillate/Distalite Oil.png",
 "cd_syringe": "product assets/Concentrate/Distillate/Distillate Syringe.png",
 "cd_applicator": "product assets/Concentrate/Distillate/Dist Applicator.webp",
 "clr_badder": "product assets/Concentrate/Live Resin/Live Resin Badder.png",
 "clr_sugar": "product assets/Concentrate/Live Resin/Live Resin Sugar.png",
 "clr_sauce": "product assets/Concentrate/Live Resin/LR Sauce.webp",
 "clr_diamonds": "product assets/Concentrate/Live Resin/Live Resin Diamonds.png",
 "clr_wax": "product assets/Concentrate/Live Resin/LR Wax .png",
 "clr_crumble": "product assets/Concentrate/Live Resin/LR Crumble .png",
 "clr_shatter": "product assets/Concentrate/Live Resin/LR Shatter.png",
 "cro_live": "product assets/Concentrate/Rosin/Live Rosin.webp",
 "cro_badder": "product assets/Concentrate/Rosin/Rosin Badder.png",
 "cro_jam": "product assets/Concentrate/Rosin/Rosin Jam .png",
 "cro_coins": "product assets/Concentrate/Rosin/Rosin Coins.webp",
 "cro_sap": "product assets/Concentrate/Rosin/Rosin Sap.png",
 "ck_loose": "product assets/Concentrate/Kief/Loose Keif.png",
 "ck_drysift": "product assets/Concentrate/Kief/Dry Sift Kief Background Removed.png",
 "ck_infused": "product assets/Concentrate/Kief/Infused Kief Background Removed.png",
 "ch_bubble": "product assets/Concentrate/Hash/Bubble Hash.png",
 "ch_icewater": "product assets/Concentrate/Hash/Ice Water Hash.png",
 "ch_drysift": "product assets/Concentrate/Hash/Dry Sift Hash.png",
 "ch_fullmelt": "product assets/Concentrate/Hash/Full Melt Hash.png",
 "ch_templeball": "product assets/Concentrate/Hash/Temple Ball Hash.png",
 "crso_oil": "product assets/Concentrate/RSO/RSO Oil.png",
 "crso_applicator": "product assets/Concentrate/RSO/RSO Applicator .png",

 # edible + flower photos (Jack's uploads)
 "top_balm": "product assets/Topicals/Balm:Salve.png",
 "ed_gum_orange": "product assets/Edibles/Orange Gummy Edible.png",
 "ed_gum_purple": "product assets/Edibles/Purple Gummy Edible.png",
 "ed_gum_red": "product assets/Edibles/Red Gummy Edible.png",
 "ed_choc_dark": "product assets/Edibles/Dark Chocolate Edible.png",
 "ed_choc_milk": "product assets/Edibles/Milk Chocolate Edible.png",
 "ed_choc_white": "product assets/Edibles/White Chocolate Edible.png",
 "ed_hard_green": "product assets/Edibles/Green Hard Candy Edible.png",
 "ed_hard_red": "product assets/Edibles/Red Hard Candy Edible.png",
 "ed_hard_yellow": "product assets/Edibles/Yellow Hard Candy Edible.png",
 "ed_cap_brown": "product assets/Edibles/Brown Capsule Edible.png",
 "ed_cap_white": "product assets/Edibles/White Capsule Edible.png",
 "ed_cap_yellow": "product assets/Edibles/Yellow Capsule Edible.png",
 "ed_baked_brownie": "product assets/Edibles/Brownie Edible.png",
 "ed_baked_cookie": "product assets/Edibles/Cookie Edible.png",
 "ed_baked_rice": "product assets/Edibles/Rice Crispy Edible.png",
 "fl_indica": "product assets/Flower/Indica.png",
 "fl_indica2": "product assets/Flower/Indica 2.png",
 "fl_indica3": "product assets/Flower/Indica.webp",
 "fl_sativa": "product assets/Flower/Sativa.webp",
 "fl_sativa2": "product assets/Flower/Sativa 2.png",
 "fl_hybrid": "product assets/Flower/Hybrid.png",
 "fl_hybrid2": "product assets/Flower/Hybrid 2.png",
 "fl_indhyb": "product assets/Flower/Indica Hybrid.png",
 "fl_indhyb2": "product assets/Flower/Indica hybrid 2.png",
 "fl_sathyb": "product assets/Flower/Sativa Hybrid.png",
 "fl_sathyb2": "product assets/Flower/Sativa Hybrid 2.png",
 "fl_universal": "product assets/Flower/Universal Nug.png",
 "growbud": "product assets/Flower/Full Bud - educational .webp",
 "map_redmond": "Various other assets/Redmond Map.png",
 "scent_skunky": "scents assets/Scent (Skunky).png",
 "hero_mtn": "origins logos/Origin background.jpeg",
 "brand_royaltree": "Various Brand Logos/Royal Tree Main Logo.png",
 "brand_saints": "Various Brand Logos/Saints Main Logo.png",
 "brand_freddys": "Various Brand Logos/Freddy's Main Logo.png",
 "brand_skord": "Various Brand Logos/Skord Main Logo.png",
 "logo_origins": "origins logos/logo_header_origins.svg",
 "life_discovery":   "Lifestyle logos/Discovery Logo.png",
 "life_adventurous": "Lifestyle logos/Adventurous Logo.png",
 "life_social":      "Lifestyle logos/Social Logo.png",
 "life_unwind":      "Lifestyle logos/Unwind Logo.png",
 "life_nightlife":   "Lifestyle logos/Nightlife Logo.png",
 "life_holistic":    "Lifestyle logos/Holistic Logo.png",
 "sm_discovery":   "Lifestyle logos/Discovery Small Logo.png",
 "sm_adventurous": "Lifestyle logos/Adventurous Small Logo.png",
 "sm_social":      "Lifestyle logos/Social Small Logo.png",
 "sm_unwind":      "Lifestyle logos/Unwind Small Logo.png",
 "sm_nightlife":   "Lifestyle logos/Nightlife Small Logo.png",
 "sm_holistic":    "Lifestyle logos/Holistic Small Logo.png",
}
def embed_glyph(relpath, maxw=560):
    """Extract just the black icon+wordmark on a transparent background (so it can
    sit directly on a lifestyle-colored button), trimmed to its bounding box."""
    im = Image.open(assets / relpath).convert("RGBA")
    gray = im.convert("L")
    dark = gray.point(lambda v: 255 if v < 80 else 0)
    alpha = im.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    mask = ImageChops.multiply(dark, alpha)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), mask)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    if out.width > maxw:
        out = out.resize((maxw, round(out.height * maxw / out.width)), Image.LANCZOS)
    buf = io.BytesIO(); out.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def embed_wordmark(relpath, maxw=560):
    """Just the wordmark (drop the leading decorative glyph), black on
    transparent and trimmed. Lets the FEEL step align every lifestyle's word to
    a common left edge beside a fixed-width glyph slot, instead of inheriting
    each combined logo's baked-in glyph width + gap."""
    im = Image.open(assets / relpath).convert("RGBA")
    w, h = im.size
    g = im.convert("L").load(); al = im.getchannel("A").load()
    cols = [sum(1 for y in range(h) if g[x, y] < 80 and al[x, y] > 40) for x in range(w)]
    runs = []; x = 0
    while x < w:
        if cols[x] > 2:
            x0 = x
            while x < w and cols[x] > 2: x += 1
            runs.append((x0, x))
        else:
            x += 1
    if len(runs) < 2:
        return embed_glyph(relpath)
    crop = im.crop((runs[1][0], 0, w, h))
    dark = crop.convert("L").point(lambda v: 255 if v < 80 else 0)
    alpha = crop.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    mask = ImageChops.multiply(dark, alpha)
    out = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", crop.size, (0, 0, 0, 255)), (0, 0), mask)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    if out.width > maxw:
        out = out.resize((maxw, round(out.height * maxw / out.width)), Image.LANCZOS)
    buf = io.BytesIO(); out.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def embed_svg(relpath):
    """Inline an SVG asset as a data URI (vector, no rasterization)."""
    data = (assets / relpath).read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(data).decode()

def embed_png(relpath, maxw=380):
    """Embed a PNG keeping transparency (for logos that sit on dark tiles)."""
    im = Image.open(assets / relpath).convert("RGBA")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def embed_hero(relpath, box=(0.20, 0.0, 0.80, 1.0), maxw=1000, q=82):
    """Crop the hero photo to a peak-focused region (baked-in 'zoom') then embed.
    Used with background-size:cover so the hero always fills cleanly at any screen
    size — never tiles/repeats — while staying framed on the summit."""
    im = Image.open(assets / relpath).convert("RGB")
    w, h = im.size
    l, t, r, b = box
    im = im.crop((int(w*l), int(h*t), int(w*r), int(h*b)))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def bg_color(relpath):
    """Sample a logo's own background colour (its opaque corner/edge) so a tile
    behind it can match and the visible 'box' disappears."""
    from collections import Counter
    im = Image.open(assets / relpath).convert("RGBA")
    w, h = im.size; px = im.load()
    # Sample the whole perimeter (not just the corners) so a few stray edge
    # pixels can't win a tie — e.g. Skord's logo has gray patches along its
    # edges that beat black in a 6-point sample and turned the tile gray.
    cols = []
    sx, sy = max(1, w // 60), max(1, h // 60)
    for x in range(0, w, sx):
        for y in (0, 1, 2, h - 3, h - 2, h - 1):
            if px[x, y][3] > 200: cols.append(px[x, y][:3])
    for y in range(0, h, sy):
        for x in (0, 1, 2, w - 3, w - 2, w - 1):
            if px[x, y][3] > 200: cols.append(px[x, y][:3])
    if not cols:
        return "#0b0b0b"
    r, g, b = Counter(cols).most_common(1)[0][0]
    return "#%02x%02x%02x" % (r, g, b)

# Jack's uploaded background-free photos map to product keys by their own
# filenames (named after the originals, not the key). A matching '<key>.png'
# also works as a drop-in. When neither exists we fall back to the white-bg
# source in 'product assets/'.
NOBG_DIR = "product assets"
NOBG = {
    "top_balm": "Topicals/Balm:Salve.png",
    "ed_gum_orange": "Edibles/Orange Gummy Edible.png",
    "ed_gum_purple": "Edibles/Purple Gummy Edible.png",
    "ed_gum_red": "Edibles/Red Gummy Edible.png",
    "ed_choc_dark": "Edibles/Dark Chocolate Edible.png",
    "ed_choc_milk": "Edibles/Milk Chocolate Edible.png",
    "ed_choc_white": "Edibles/White Chocolate Edible.png",
    "ed_hard_green": "Edibles/Green Hard Candy Edible.png",
    "ed_hard_red": "Edibles/Red Hard Candy Edible.png",
    "ed_hard_yellow": "Edibles/Yellow Hard Candy Edible.png",
    "ed_cap_brown": "Edibles/Brown Capsule Edible.png",
    "ed_cap_white": "Edibles/White Capsule Edible.png",
    "ed_cap_yellow": "Edibles/Yellow Capsule Edible.png",
    "ed_baked_brownie": "Edibles/Brownie Edible.png",
    "ed_baked_cookie": "Edibles/Cookie Edible.png",
    "ed_baked_rice": "Edibles/Rice Crispy Edible.png",
    "fl_indica": "Flower/Indica.png",
    "fl_indica2": "Flower/Indica 2.png",
    "fl_indica3": "Flower/Indica.webp",
    "fl_sativa": "Flower/Sativa.webp",
    "fl_sativa2": "Flower/Sativa 2.png",
    "fl_hybrid": "Flower/Hybrid.png",
    "fl_hybrid2": "Flower/Hybrid 2.png",
    "fl_indhyb": "Flower/Indica Hybrid.png",
    "fl_indhyb2": "Flower/Indica hybrid 2.png",
    "fl_sathyb": "Flower/Sativa Hybrid.png",
    "fl_sathyb2": "Flower/Sativa Hybrid 2.png",
    "fl_universal": "Flower/Universal Nug.png",
    "growbud": "Flower/Full Bud - educational .webp",
    "cd_oil": "Concentrate/Distillate/Distalite Oil.png",
    "cd_syringe": "Concentrate/Distillate/Distillate Syringe.png",
    "cd_applicator": "Concentrate/Distillate/Dist Applicator.webp",
    "clr_badder": "Concentrate/Live Resin/Live Resin Badder.png",
    "clr_sugar": "Concentrate/Live Resin/Live Resin Sugar.png",
    "clr_sauce": "Concentrate/Live Resin/LR Sauce.webp",
    "clr_diamonds": "Concentrate/Live Resin/Live Resin Diamonds.png",
    "clr_wax": "Concentrate/Live Resin/LR Wax .png",
    "clr_crumble": "Concentrate/Live Resin/LR Crumble .png",
    "clr_shatter": "Concentrate/Live Resin/LR Shatter.png",
    "cro_live": "Concentrate/Rosin/Live Rosin.webp",
    "cro_badder": "Concentrate/Rosin/Rosin Badder.png",
    "cro_jam": "Concentrate/Rosin/Rosin Jam .png",
    "cro_coins": "Concentrate/Rosin/Rosin Coins.webp",
    "cro_sap": "Concentrate/Rosin/Rosin Sap.png",
    "ck_loose": "Concentrate/Kief/Loose Keif.png",
    "ck_drysift": "Concentrate/Kief/Dry Sift Kief Background Removed.png",
    "ck_infused": "Concentrate/Kief/Infused Kief Background Removed.png",
    "ch_bubble": "Concentrate/Hash/Bubble Hash.png",
    "ch_icewater": "Concentrate/Hash/Ice Water Hash.png",
    "ch_drysift": "Concentrate/Hash/Dry Sift Hash.png",
    "ch_fullmelt": "Concentrate/Hash/Full Melt Hash.png",
    "ch_templeball": "Concentrate/Hash/Temple Ball Hash.png",
    "crso_oil": "Concentrate/RSO/RSO Oil.png",
    "crso_applicator": "Concentrate/RSO/RSO Applicator .png",
    # extra bud photos, mixed in across the catalog flower products
}
def nobg_file(k):
    for name in (NOBG.get(k), k + ".png"):
        if name and (assets / NOBG_DIR / name).exists():
            return NOBG_DIR + "/" + name
    return None

IMG = {}
for k, rel in M.items():
    try:
        if rel.endswith(".svg"):
            IMG[k] = embed_svg(rel)
        elif k.startswith("brand_"):
            IMG[k] = embed_png(rel)
            IMG["bg_" + k] = bg_color(rel)
        elif k == "hero_mtn":
            IMG[k] = embed_hero(rel)
        elif k.startswith("life_") or k.startswith("sm_") or k.startswith("scent_"):
            IMG[k] = embed_glyph(rel)
        else:
            nb = nobg_file(k)
            IMG[k] = embed_rgba(nb) if nb else embed(rel)
    except Exception as e:
        print("WARN", k, rel, e)

# wordmark-only images (leading glyph dropped) so the FEEL step can align every
# lifestyle's word to a common left edge next to a fixed glyph slot
for name in ["discovery", "adventurous", "social", "unwind", "nightlife", "holistic"]:
    try:
        IMG["word_" + name] = embed_wordmark(M["life_" + name])
    except Exception as e:
        print("WARN word", name, e)

# Growing Process education card uses Jack's full-plant illustration


src = src.replace("/*IMGMAP*/", json.dumps(IMG))

# ---- entity-encode outside script/style; \u-escape non-ASCII inside script ----
def esc_script(block):
    return ''.join(c if ord(c) < 128 else '\\u%04X' % ord(c) for c in block)
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(esc_script(x) if x[:7] == '<script'
              else (x if x[:6] == '<style'
                    else x.encode('ascii', 'xmlcharrefreplace').decode()) for x in segs)

out = out_dir / "origins-app.html"
out.write_text(src)
print(f"wrote {out} ({len(src)//1024} KB); imgs={len(IMG)}; markers left={src.count('/*IMGMAP*/')+src.count('/*FONTS*/')}")
