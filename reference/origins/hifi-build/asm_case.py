#!/usr/bin/env python3
"""Assemble the Origins case-study artifact: embed fonts, logo, all real assets,
and the working app prototype (as a base64 data-URI iframe).
Run: python3 reference/origins/hifi-build/asm_case.py
Output: <scratchpad>/origins-case.html (or ./origins-case.html)."""
from PIL import Image
import base64, io, json, pathlib, re, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[3]
org = REPO / "reference/origins"
site = REPO / "site"
build = pathlib.Path(__file__).resolve().parent
cache = REPO / "reference/oxfam/hifi-build/fontcache"
src = (build / "origins-case.src.html").read_text()

SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
out_dir = SCRATCH if SCRATCH.exists() else pathlib.Path(".")

# ---- fonts: site woff2 (Space Grotesk + IBM Plex) + cached Oswald for the type specimen ----
fcss = []
for fam, wt, fn in [("Space Grotesk",400,"space-grotesk-400"),("Space Grotesk",500,"space-grotesk-500"),
                    ("Space Grotesk",700,"space-grotesk-700"),("IBM Plex Sans",400,"ibm-plex-sans-400"),
                    ("IBM Plex Sans",500,"ibm-plex-sans-500"),("IBM Plex Sans",600,"ibm-plex-sans-600"),
                    ("IBM Plex Mono",400,"ibm-plex-mono-400"),("IBM Plex Mono",500,"ibm-plex-mono-500")]:
    b64 = base64.b64encode((site / "public/fonts" / f"{fn}.woff2").read_bytes()).decode()
    fcss.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{wt};font-display:swap;'
                f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
for wt in ("500","600","700"):
    fp = cache / f"oswald-{wt}.woff2"
    if fp.exists():
        b64 = base64.b64encode(fp.read_bytes()).decode()
        fcss.append(f'@font-face{{font-family:"Oswald";font-style:normal;font-weight:{wt};font-display:swap;'
                    f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
src = src.replace("/*FONTS*/", "\n".join(fcss))

# ---- images ----
def embed(relpath, maxw, q=82):
    im = Image.open(org / relpath)
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
 "hero":      ("assets/origins logos/falls.jpeg", 1500, 80),
 "cluttered": ("screens/Cluterred Home.png", 800, 82),
 "pricing":   ("screens/Contradictory Pricing Deal.PNG", 800, 82),
 "survey_u":  ("flow/User Survey - In-Person.png", 1100, 84),
 "survey_n":  ("flow/Non-User Survey - In-Person.png", 1100, 84),
 "persona1":  ("assets/persona assets/Persona 1 - Noelle.png", 1100, 84),
 "persona2":  ("assets/persona assets/Persona 2 - Jared.png", 1100, 84),
 "flow_pain": ("flow/User Flow Analysis - Pain Points.png", 1500, 84),
 "filt_pain": ("flow/Filter - Pain Points.png", 1500, 84),
 "lofi_new":  ("lofi/Low-Fi New Sections .png", 1100, 84),
 "lofi_g1a":  ("lofi/Lo-Fi Guide Page V1a.png", 760, 82),
 "lofi_g1b":  ("lofi/Lo-Fi Guide Page V1b .png", 760, 82),
 "lofi_g2":   ("lofi/Lo-Fi Guide Page V2.png", 760, 82),
 "lofi_shop": ("lofi/Lo-Fi Main Shop Page.png", 760, 82),
 "lofi_scroll":("lofi/Lo-Fi Main Shop Page - Scrolled Down.png", 760, 82),
 "lifestyle": ("assets/Brand Identity/Lifestyle Overview.png", 900, 84),
 "sizetoggle":("hifi/Hi-Fi Full Size Toggle.png", 900, 84),
 "home_v1":   ("hifi/Hi-Fi Home Page V1.png", 760, 82),
 "home_v1b":  ("hifi/Hi-Fi Home Page V1b - Bigger Image.png", 760, 82),
 "home_v2":   ("hifi/Hi-Fi Home Page V2.png", 760, 82),
 "acct_v1":   ("hifi/Hi-Fi Account Settings V1.png", 760, 82),
 "acct_v2":   ("hifi/Hi-Fi Account Settings V2.png", 760, 82),
 "abtest":    ("flow/User Testing - Hi-Fi Shop Variation - Flower.png", 860, 82),
 "flow_rec":  ("flow/User Flow - Recommended Changes.png", 1500, 84),
 "filt_rec":  ("flow/Filters - Recommended Changes.png", 1500, 84),
 "hifi_over": ("hifi/Hi-Fi Overview.png", 1500, 84),
 "hifi_land": ("hifi/Hi-Fi Landing Page.png", 760, 82),
 "hifi_prod": ("hifi/Hi-Fi Product Page - Shop - Concentrate.png", 760, 82),
 "hifi_acct": ("hifi/Hi-Fi Account Page.png", 760, 82),
}
IMG = {}
for k, (rel, w, q) in M.items():
    try:
        IMG[k] = embed(rel, w, q)
    except Exception as e:
        print("WARN", k, rel, e)
IMG["home_v2b"] = IMG.get("home_v2", "")
src = src.replace("/*IMGMAP*/", json.dumps(IMG))

# ---- logo ----
logo = (site / "public/brand/motz-white.svg").read_text()
logo = re.sub(r'fill="#[0-9A-Fa-f]{6}"', 'fill="currentColor"', logo)
logo = re.sub(r'<svg ', '<svg style="display:block;width:100%;height:100%" ', logo, count=1)
src = src.replace("<!--LOGO-->", logo)

# ---- app prototype: build fresh, then embed as base64 ----
subprocess.run([sys.executable, str(build / "asm_app.py")], check=True, cwd=str(REPO))
app_path = (SCRATCH if SCRATCH.exists() else pathlib.Path(".")) / "origins-app.html"
app_doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1">'
           '<title>Origins App</title></head><body>' + app_path.read_text() + '</body></html>')
src = src.replace("/*PROTODOC*/", base64.b64encode(app_doc.encode()).decode())

# ---- encode: entities outside script/style, \u-escapes inside script ----
def esc_script(block):
    return ''.join(c if ord(c) < 128 else '\\u%04X' % ord(c) for c in block)
segs = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>)', src)
src = ''.join(esc_script(x) if x[:7] == '<script'
              else (x if x[:6] == '<style'
                    else x.encode('ascii', 'xmlcharrefreplace').decode()) for x in segs)

out = out_dir / "origins-case.html"
out.write_text(out_s := src)
print(f"wrote {out} ({len(out_s)//1024} KB); imgs={len(IMG)}; "
      f"markers left={out_s.count('/*IMGMAP*/')+out_s.count('/*FONTS*/')+out_s.count('<!--LOGO-->')+out_s.count('/*PROTODOC*/')}")
