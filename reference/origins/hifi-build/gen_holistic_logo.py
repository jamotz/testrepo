#!/usr/bin/env python3
"""Generate the Holistic lifestyle logos (big + small) to match Jack's set.

There was no Holistic brand logo, so we build one from Jack's own assets:
  - Wordmark "HOLISTIC": recomposed from his real letterforms — H,T lifted from
    the NIGHTLIFE logo and O,L,I,S,C from the SOCIAL logo (both share the same
    cap height), segmented by column gaps. This makes the word an exact match
    for the other lifestyle wordmarks' font.
  - Decorative leading "H": drawn chunky to match the D/N leading-letter weight,
    proportioned ~0.97 h/w so it renders the same size as the others, with a
    small leaf cut into each vertical bar (negative-space motif, like D's key).

Outputs (black on the --hol sage field, like the other logos):
  Lifestyle logos/Holistic Logo.png        (H + HOLISTIC)
  Lifestyle logos/Holistic Small Logo.png  (H glyph only)

Run:  python3 reference/origins/hifi-build/gen_holistic_logo.py
Re-run after tweaking; then rebuild with asm_app.py.
"""
import math, os
from PIL import Image, ImageDraw, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets", "Lifestyle logos"))
SAGE = (126, 154, 91)  # --hol #7E9A5B

def ink_data(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    g = im.convert("L").load()
    a = im.getchannel("A").load()
    def isink(x, y): return 1 if (g[x, y] < 95 and a[x, y] > 60) else 0
    cols = [sum(isink(x, y) for y in range(h)) for x in range(w)]
    return im, cols, w, h, isink

def segment(cols, minink=2):
    runs, x, W = [], 0, len(cols)
    while x < W:
        if cols[x] > minink:
            x0 = x
            while x < W and cols[x] > minink: x += 1
            runs.append((x0, x))
        else:
            x += 1
    return runs

def crop_letter(isink, x0, x1, ytop, ybot):
    out = Image.new("RGBA", (x1 - x0, ybot - ytop), (0, 0, 0, 0)); op = out.load()
    for xx in range(x0, x1):
        for yy in range(ytop, ybot):
            if isink(xx, yy): op[xx - x0, yy - ytop] = (0, 0, 0, 255)
    return out

def extract(path):
    im, cols, w, h, isink = ink_data(path)
    runs = segment(cols)[1:]  # drop the decorative leading glyph
    ytop, ybot = h, 0
    for (a, b) in runs:
        for xx in range(a, b):
            for yy in range(h):
                if isink(xx, yy): ytop = min(ytop, yy); ybot = max(ybot, yy)
    ybot += 1
    return [crop_letter(isink, a, b, ytop, ybot) for (a, b) in runs], ybot - ytop

soc, soc_h = extract(os.path.join(ASSETS, "Social Logo.png"))      # S O C I A L
nig, nig_h = extract(os.path.join(ASSETS, "Nightlife Logo.png"))   # N I G H T L I F E

TARGET = 150
def scaled(letter, capH):
    f = TARGET / capH
    return letter.resize((max(1, round(letter.width * f)), TARGET), Image.LANCZOS)

# HOLISTIC = H(nig3) O(soc1) L(soc5) I(soc3) S(soc0) T(nig4) I(soc3) C(soc2)
seq = [(nig[3], nig_h), (soc[1], soc_h), (soc[5], soc_h), (soc[3], soc_h),
       (soc[0], soc_h), (nig[4], nig_h), (soc[3], soc_h), (soc[2], soc_h)]
imgs = [scaled(l, c) for (l, c) in seq]
gap = round(0.10 * TARGET)
wordmark = Image.new("RGBA", (sum(i.width for i in imgs) + gap * (len(imgs) - 1), TARGET), (0, 0, 0, 0))
x = 0
for i in imgs:
    wordmark.alpha_composite(i, (x, 0)); x += i.width + gap

# decorative chunky H (~0.97 h/w to match the set), leaf cut into each bar
GH = int(TARGET * 1.5); GW = int(GH * 1.03)
t = int(GW * 0.235); r = int(t * 0.26)
glyph = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
d = ImageDraw.Draw(glyph)
d.rounded_rectangle([0, 0, t, GH - 1], radius=r, fill=(0, 0, 0, 255))
d.rounded_rectangle([GW - t, 0, GW - 1, GH - 1], radius=r, fill=(0, 0, 0, 255))
cbh = int(GH * 0.205); cby = (GH - cbh) // 2
d.rectangle([t - 2, cby, GW - t + 2, cby + cbh], fill=(0, 0, 0, 255))

def leaf_poly(cx, cy, length, width, angle):
    pts, n = [], 30
    for i in range(n + 1):
        u = -1 + 2 * i / n; pts.append((u * length / 2, (width / 2) * (1 - u * u)))
    for i in range(n + 1):
        u = 1 - 2 * i / n; pts.append((u * length / 2, -(width / 2) * (1 - u * u)))
    ca, sa = math.cos(angle), math.sin(angle)
    return [(cx + px * ca - py * sa, cy + px * sa + py * ca) for (px, py) in pts]

def cut_leaf(cx, cy, length, width, angle):
    m = Image.new("L", glyph.size, 0)
    ImageDraw.Draw(m).polygon(leaf_poly(cx, cy, length, width, angle), fill=255)
    glyph.putalpha(ImageChops.subtract(glyph.getchannel("A"), m))
    ca, sa = math.cos(angle), math.sin(angle)
    ImageDraw.Draw(glyph).line(
        [(cx - length * 0.42 * ca, cy - length * 0.42 * sa),
         (cx + length * 0.42 * ca, cy + length * 0.42 * sa)],
        fill=(0, 0, 0, 255), width=max(2, int(t * 0.08)))

leafL, leafW = int(GH * 0.5), int(t * 0.6)
cut_leaf(t / 2, GH / 2, leafL, leafW, math.pi / 2 - 0.28)
cut_leaf(GW - t / 2, GH / 2, leafL, leafW, math.pi / 2 + 0.28)

PAD, gap2 = int(GH * 0.16), int(GH * 0.18)
big = Image.new("RGBA", (PAD * 2 + GW + gap2 + wordmark.width, PAD * 2 + GH), (0, 0, 0, 0))
big.alpha_composite(glyph, (PAD, PAD))
big.alpha_composite(wordmark, (PAD + GW + gap2, PAD + GH - TARGET))
bigbg = Image.new("RGBA", big.size, SAGE + (255,)); bigbg.alpha_composite(big)
bigbg.convert("RGB").save(os.path.join(ASSETS, "Holistic Logo.png"))

SPAD = int(GW * 0.18)
small = Image.new("RGBA", (GW + SPAD * 2, GH + SPAD * 2), SAGE + (255,))
small.alpha_composite(glyph, (SPAD, SPAD))
small.convert("RGB").save(os.path.join(ASSETS, "Holistic Small Logo.png"))
print("wrote Holistic Logo.png (%dx%d) and Holistic Small Logo.png (%dx%d)" %
      (bigbg.width, bigbg.height, small.width, small.height))
