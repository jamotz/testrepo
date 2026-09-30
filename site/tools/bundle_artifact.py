#!/usr/bin/env python3
"""Bundle the built site (site/dist) into the "motz-kinetic-live" Artifact.

Run after `npm run build`:  python3 site/tools/bundle_artifact.py [out_dir]

Writes (default out_dir: ./artifact-bundle):
  motz-kinetic-live.html   landing page as a fragment (the Artifact tool wraps
                           the main page in its own <!doctype>/<head>/<body>)
  oxfam.html               the Oxfam case study, a full standalone document
  work/oxfam/*.jpg, proto.html   images + the embedded prototype, as-is

CSS, JS and fonts are inlined into both pages (fonts as data: URIs) so each
page stands alone; only images and the prototype stay separate files. Root-
absolute links are rewritten relative: the landing page is the artifact's
index.html, the case study sits beside it as oxfam.html.
"""
import base64, pathlib, re, shutil, sys

SITE = pathlib.Path(__file__).resolve().parents[1]
DIST = SITE / "dist"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "artifact-bundle").resolve()


def inline_fonts(css):
    def repl(m):
        font = (SITE / "public" / m.group(1).lstrip("/")).read_bytes()
        return "url(data:font/woff2;base64," + base64.b64encode(font).decode() + ")"
    return re.sub(r"url\((/fonts/[^)]+\.woff2)\)", repl, css)


def js(name):
    """A hoisted bundle's source, with its sibling import dropped (it's inlined first)."""
    src = (DIST / "assets" / name).read_text()
    return re.sub(r'^import"\./[^"]+";', "", src)


def inline_head(html):
    html = re.sub(r'<link rel="(?:canonical|icon|preload)"[^>]*>', "", html)
    html = re.sub(r'<link rel="stylesheet" href="/assets/([^"]+)">',
                  lambda m: "<style>" + inline_fonts((DIST / "assets" / m.group(1)).read_text()) + "</style>",
                  html)

    def script(m):
        own = js(m.group(1))
        dep = re.match(r'^import"\./([^"]+)";', (DIST / "assets" / m.group(1)).read_text())
        parts = ([js(dep.group(1))] if dep else []) + [own]
        return "".join(f'<script type="module">{p}</script>' for p in parts)
    return re.sub(r'<script type="module" src="/assets/([^"]+)"></script>', script, html)


def fragment(html):
    """<head> content (title, styles, theme script) + <body> content, no document shell."""
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
    head = re.sub(r"<meta [^>]*>", "", head)
    # keep <title> after the (large) inlined styles: the artifact is named from its
    # file, "motz-kinetic-live", and a title in the first 8KB would rename it
    title = re.search(r"<title>.*?</title>", head, re.S)
    if title:
        head = head.replace(title.group(0), "") + title.group(0)
    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)
    return head + body


# ---- landing page (main page) ----
landing = inline_head((DIST / "index.html").read_text())
landing = landing.replace('href="/work/oxfam"', 'href="oxfam.html"')
landing = re.sub(r'href="/#([\w-]+)"', r'href="#\1"', landing)
landing = landing.replace('href="/"', 'href="#top"')
landing = fragment(landing)

# ---- Oxfam case study (second page) ----
oxfam = inline_head((DIST / "work/oxfam/index.html").read_text())
oxfam = oxfam.replace('"/work/oxfam/', '"work/oxfam/')
oxfam = re.sub(r'href="/#([\w-]+)"', r'href="index.html#\1"', oxfam)
oxfam = oxfam.replace('href="/"', 'href="index.html"')
# no Origins case-study page exists yet; send "next project" back to the work grid
oxfam = oxfam.replace('href="/work/origins"', 'href="index.html#work"')

leftover = re.findall(r'(?:href|src)="/[^"]*"', landing + oxfam)
assert not leftover, f"unrewritten root-absolute refs: {leftover}"

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "work/oxfam").mkdir(parents=True)
(OUT / "motz-kinetic-live.html").write_text(landing)
(OUT / "oxfam.html").write_text(oxfam)
for f in (DIST / "work/oxfam").iterdir():
    if f.suffix in (".jpg", ".png") or f.name == "proto.html":
        shutil.copy2(f, OUT / "work/oxfam" / f.name)

for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"{p.relative_to(OUT)}  {p.stat().st_size // 1024} KB")
