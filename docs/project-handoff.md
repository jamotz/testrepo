# Origins App — Project Handoff

**Last updated:** 2026-08-10 · branch `claude/project-docs-review-sz8jwv`
**Live prototype:** https://claude.ai/code/artifact/ff102055-8262-4b48-a681-8d77f802c968

Hi-fi clickable prototype of the **Origins** cannabis retail app, built for Jack
Motzkin's UX portfolio case study. Everything is a single self-contained HTML
file assembled from a source file plus image assets.

---

## Where this sits

The **portfolio website** (`site/`, Astro) is the overall project. Origins is one
case study inside it, and this prototype is what its case page will show. The
root `HANDOFF.md` covers the site; this folder covers the app.

**The `main` branch is unrelated.** It holds old coursework — Jupyter notebooks,
`firstpython.py` — and none of this project. GitHub shows it by default, so a
browse that "can't find the files" is almost always looking at `main`. All work
lives on the `claude/*` branches.

---

## Start here (new session)

```bash
git fetch origin claude/project-docs-review-sz8jwv
git checkout -B claude/project-docs-review-sz8jwv origin/claude/project-docs-review-sz8jwv
python3 -m pip install --quiet Pillow          # recycles remove it
python3 reference/origins/hifi-build/asm_app.py
```

The build prints `wrote <path> (NNNN KB); imgs=93; markers left=0` and a `WARN`
line for any asset it can't resolve. **Containers are ephemeral — commit and
push often.**

Rendering/screenshots use the preinstalled Chromium via Playwright:
`/opt/pw-browsers/chromium-*/chrome-linux/chrome` (path moves after recycles;
`require('/opt/node22/lib/node_modules/playwright/index.js')`).

Publishing: republish to the **same artifact URL** above, or the link Jack has
already shared stops being the live one.

---

## Working rules (Jack's, non-negotiable)

1. **Stay true to Jack's frames by default.** Deviate only when he says so.
2. **One screen at a time** — build, screenshot, get sign-off, then move on.
3. **Ask clarifying questions before building anything non-trivial.** Wrong
   guesses on structure cost real rework (see `design-decisions.md`).
4. **Never invent product data** that contradicts his sheets. Authored filler is
   fine when he's asked for it, but mark it clearly (see the `AUTHORED` blocks in
   `gen_concentrates.py` and `gen_topicals.py`).

---

## Current state

**186 products** across six types:

| Type | Count | Source | Photos |
|---|---:|---|---|
| Flower | 35 | `Flower Product Catalog.docx` + 5 legacy mock rows | strain-based ✓ |
| Concentrate | 60 | `WA_Mock_Concentrate_Inventory_50…xlsx` + 10 added rows | per consistency ✓ |
| Edible | 50 | `WA_Edibles_By_Brand_Final_Curated_Normalized.xlsx` | by form + name ✓ |
| Topical | 38 | `WA_Topicals_Product_Catalog_Final.xlsx` (sheet 2) + 3 authored | one per form ✓ |
| Pre-roll | 2 | original mock data | ✗ **missing** |
| Drink | 1 | original mock data | reuses a gummy shot |

**65 Holistic products**; **45 carry a cannabinoid ratio**.

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 8 topic pages) · vape dead-end.

**Screens still to build:** **Account** (`ACCOUNT.png`, `AC - AC SETTINGS.png`,
`AC - LOYALTY POINTS.png`) — the last major frame in Jack's set.

---

## Immediate next steps

1. **Pre-rolls** — the only products still short of data. Two legacy mock rows,
   no photos, no CBD figures. Needs a sheet like the others.
2. **Account screens** — the remaining frames.
3. **Terpene + feeling setup** — Jack wants a proper pass over both once the
   product data is finished. They're currently mapped from form/effect tables in
   the generators.
4. **Drinks** — the edibles IA says drinks are "intentionally excluded and will
   be implemented separately." The app still has 1 legacy drink and a Drinks
   category circle.

---

## Repo layout

```
reference/origins/
├── hifi-build/
│   ├── origins-app.src.html      ← THE app (markup + CSS + JS + product data)
│   ├── asm_app.py                ← build: inlines fonts + images -> one HTML file
│   ├── gen_catalog_products.py   ← flower products from the .docx
│   ├── gen_concentrates.py       ← concentrates from the .xlsx (+ authored rows)
│   ├── gen_edibles.py            ← edibles from the .xlsx + filter IA
│   ├── gen_topicals.py           ← topicals from the .xlsx (+ authored rows)
│   ├── gen_holistic_logo.py      ← generates the Holistic lifestyle logo
│   └── origins-case.src.html     ← case-study page, built by asm_case.py
├── product info/                 ← Jack's source data (.docx/.xlsx)
├── assets/
│   ├── product assets/           ← photos by category (Concentrate has sub-folders)
│   ├── Lifestyle logos/          ← the six lifestyle logos
│   ├── Various Brand Logos/      ← Royal Tree, Saints, Freddy's, Skörd
│   └── origins logos/, scents assets/, …
├── hifi-final/                   ← Jack's Figma frames (the source of truth)
└── HANDOFF.md                    ← older handoff, still has useful frame notes
site/                             ← the Astro portfolio site (the umbrella project)
docs/                             ← you are here
```

`origins-app.src.html` is one big file by design — it assembles into a single
portable HTML artifact with no external requests.

---

## Regenerating product data

Each generator prints rows to stdout; splice them over the matching block in
`origins-app.src.html`, then rebuild. The rows for one type are contiguous.

```bash
python3 reference/origins/hifi-build/gen_topicals.py > /tmp/topicals.txt
# replace the {t:"topical"…} lines in origins-app.src.html, then:
python3 reference/origins/hifi-build/asm_app.py
```

**Flower is the exception — don't regenerate it.** `gen_catalog_products.py`
picks images from `IMG_POOL`, and the app's flower rows were hand-updated to the
real `fl_*` keys afterwards. The pool now points at keys that exist, but the
per-product assignment would still be reshuffled. Patch flower rows in place.

---

## Gotchas

- **The artifact URL is stable.** Republish with `url=` to keep it; a new path
  mints a new URL.
- **Excel omits empty cells entirely.** A reader that appends cells in document
  order silently shifts every column after a blank — this is why a sheet once
  parsed with `Cannabinoid Combo` landing in `Effect Filter`. All the generators
  now place cells by column letter. Copy that reader for any new sheet.
- **Sectioned sheets carry `=== SECTION ===` rows.** Filter them out or they
  parse as products.
- **Don't publish with missing photos.** The build still succeeds when assets are
  gone (WARN + blank tiles) — check the WARN lines before publishing.
- **Jack sometimes uploads an older `origins-app.src.html`** alongside his data
  files via the GitHub web UI, which silently reverts work. Diff before rebasing;
  it happened once and was caught.
- **Git drops empty directories.** Every asset folder has a `README.md` so the
  structure survives deleting its photos (learned the hard way with `Rosin/`).
- **`.s` and `.empty` are global CSS classes** — `.s{display:none}` in
  particular. Namespace anything new (the size sheet uses `fs*`), or it vanishes
  silently.
- **Build takes ~2 min** since the WebP encode; run it in the background.
