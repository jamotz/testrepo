#!/usr/bin/env python3
"""Bundle the built site (site/dist) into the "motz-kinetic-live" Artifact.

Run after `npm run build`:  python3 site/tools/bundle_artifact.py [out_dir]
Draft preview (its own artifact): python3 site/tools/bundle_artifact.py --draft premier [out_dir]
  builds a scratch copy of the site with src/pages/work/_premier.astro enabled (the
  underscore keeps it off the live site) and writes <out_dir>/premier.html, plus the
  page's images (public/work/premier/*) at <out_dir>/work/premier/.

Writes (default out_dir: ./artifact-bundle):
  motz-kinetic-live.html   landing page as a fragment (the Artifact tool wraps
                           the main page in its own <!doctype>/<head>/<body>)
  oxfam.html               the Oxfam case study, a full standalone document
  origins.html             the Origins case study (built by asm_case.py --site)
  work/oxfam/*.jpg, proto.html      Oxfam images + embedded prototype, as-is
  work/origins/img/*, app.html      Origins images + embedded app, as-is

CSS, JS and fonts are inlined into both pages (fonts as data: URIs) so each
page stands alone; only images and the prototype stay separate files. Root-
absolute links are rewritten relative: the landing page is the artifact's
index.html, the case study sits beside it as oxfam.html.
"""
import base64, os, pathlib, re, shutil, subprocess, sys

SITE = pathlib.Path(__file__).resolve().parents[1]
DIST = SITE / "dist"
args = sys.argv[1:]
DRAFT = None
if "--draft" in args:
    i = args.index("--draft"); DRAFT = args[i + 1]; del args[i:i + 2]
OUT = pathlib.Path(args[0] if args else "artifact-bundle").resolve()


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
    # the Artifact skeleton supplies <html>, so re-apply the page's accent attribute on it
    accent = re.search(r'<html[^>]*data-accent="([\w-]+)"', html)
    if accent:
        head = f"<script>document.documentElement.setAttribute('data-accent','{accent.group(1)}')</script>" + head
    return head + body


if DRAFT:
    tmp = OUT.parent / f".draft-site-{DRAFT}"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(SITE, tmp, ignore=shutil.ignore_patterns("node_modules", "dist", ".astro"))
    os.symlink(SITE / "node_modules", tmp / "node_modules")
    (tmp / f"src/pages/work/_{DRAFT}.astro").rename(tmp / f"src/pages/work/{DRAFT}.astro")
    subprocess.run(["npm", "run", "build"], cwd=tmp, check=True, stdout=subprocess.DEVNULL)
    DIST = tmp / "dist"
    page = fragment(inline_head((DIST / f"work/{DRAFT}/index.html").read_text()))
    # the page's own images ship beside it: /work/<draft>/x -> work/<draft>/x
    page = page.replace(f'"/work/{DRAFT}/', f'"work/{DRAFT}/')
    # a standalone mockup: links to the rest of the site have nowhere to go, so they return to the top
    page = re.sub(r'href="/[^"]*"', 'href="#case-top"', page)
    title = re.search(r"<title>(.*?)(?: — Jack Motzkin)?</title>", page).group(1)
    page = f"<title>{title}</title>" + re.sub(r"<title>.*?</title>", "", page)
    assert not re.findall(r'(?:href|src)="/[^"]*"', page)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{DRAFT}.html").write_text(page)
    assets = [f for f in (DIST / f"work/{DRAFT}").iterdir() if f.name != "index.html"]
    if assets:
        (OUT / f"work/{DRAFT}").mkdir(parents=True, exist_ok=True)
        for f in assets:
            shutil.copy2(f, OUT / f"work/{DRAFT}" / f.name)
    shutil.rmtree(tmp)
    print(f"{OUT / (DRAFT + '.html')}  {len(page) // 1024} KB")
    sys.exit(0)

# ---- landing page (main page) ----
landing = inline_head((DIST / "index.html").read_text())
landing = landing.replace('href="/work/oxfam"', 'href="oxfam.html"').replace('href="/work/origins"', 'href="origins.html"')
landing = re.sub(r'href="/#([\w-]+)"', r'href="#\1"', landing)
landing = landing.replace('href="/"', 'href="#top"')
landing = fragment(landing)

# ---- Oxfam case study (second page) ----
oxfam = inline_head((DIST / "work/oxfam/index.html").read_text())
oxfam = oxfam.replace('"/work/oxfam/', '"work/oxfam/')
oxfam = re.sub(r'href="/#([\w-]+)"', r'href="index.html#\1"', oxfam)
oxfam = oxfam.replace('href="/"', 'href="index.html"')
oxfam = oxfam.replace('href="/work/origins"', 'href="origins.html"')

# ---- Origins case study (third page; already self-contained apart from images + app) ----
origins = (DIST / "work/origins/index.html").read_text()
origins = re.sub(r'<link rel="icon"[^>]*>', "", origins)
origins = origins.replace('"/work/origins/', '"work/origins/')   # app src + image map (in script)
origins = re.sub(r'href="/#([\w-]+)"', r'href="index.html#\1"', origins)

leftover = re.findall(r'(?:href|src)="/[^"]*"|"/work/[^"]*"', landing + oxfam + origins)
assert not leftover, f"unrewritten root-absolute refs: {leftover}"

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "work/oxfam").mkdir(parents=True)
(OUT / "motz-kinetic-live.html").write_text(landing)
(OUT / "oxfam.html").write_text(oxfam)
(OUT / "origins.html").write_text(origins)
for f in (DIST / "work/oxfam").iterdir():
    if f.suffix in (".jpg", ".png") or f.name == "proto.html":
        shutil.copy2(f, OUT / "work/oxfam" / f.name)
shutil.copytree(DIST / "work/origins/img", OUT / "work/origins/img")
shutil.copy2(DIST / "work/origins/app.html", OUT / "work/origins/app.html")

for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"{p.relative_to(OUT)}  {p.stat().st_size // 1024} KB")
