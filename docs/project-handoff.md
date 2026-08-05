# Origins App — Project Handoff

**Last updated:** 2026-08-05 · branch `claude/cloud-container-access-p7024t`
**Live prototype:** https://claude.ai/code/artifact/ff102055-8262-4b48-a681-8d77f802c968

Hi-fi clickable prototype of the **Origins** cannabis retail app, built for Jack
Motzkin's UX portfolio case study. Everything is a single self-contained HTML
file assembled from a source file plus image assets.

---

## Start here (new session)

```bash
git fetch origin claude/cloud-container-access-p7024t
git checkout -B claude/cloud-container-access-p7024t origin/claude/cloud-container-access-p7024t
python3 -m pip install --quiet Pillow          # recycles remove it
python3 reference/origins/hifi-build/asm_app.py
```

The build prints `wrote <path> (NNNN KB); imgs=84; markers left=0` and a `WARN`
line for any asset it can't resolve. **Containers are ephemeral — commit and
push often.**

Rendering/screenshots use the preinstalled Chromium via Playwright:
`/opt/pw-browsers/chromium-*/chrome-linux/chrome` (path moves after recycles;
`require('/opt/node22/lib/node_modules/playwright/index.js')`).

---

## Working rules (Jack's, non-negotiable)

1. **Stay true to Jack's frames by default.** Deviate only when he says so.
2. **One screen at a time** — build, screenshot, get sign-off, then move on.
3. **Ask clarifying questions before building anything non-trivial.** Wrong
   guesses on structure cost real rework (see `design-decisions.md`).
4. **Never invent product data** that contradicts his sheets. Authored filler is
   fine when he's asked for it, but mark it clearly (see the `AUTHORED` block in
   `gen_concentrates.py`).

---

## Current state

**149 products** across six types:

| Type | Count | Source | Photos |
|---|---:|---|---|
| Flower | 35 | `Flower Product Catalog.docx` | strain-based ✓ |
| Concentrate | 60 | `WA_Mock_Concentrate_Inventory_50…xlsx` + 10 added rows | per consistency ✓ |
| Edible | 50 | `WA_Edibles_By_Brand_Sectioned.xlsx` | 15 by form/flavour ✓ |
| Pre-roll | 2 | original mock data | ✗ **missing** |
| Drink | 1 | original mock data | ✗ **missing** |
| Topical | 1 | original mock data | balm photo ✓ |

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 8 topic pages) · vape dead-end.

**Screens still to build:** **Account** (`ACCOUNT.png`, `AC - AC SETTINGS.png`,
`AC - LOYALTY POINTS.png`) — the last major frame in Jack's set.

---

## Immediate next steps

1. **Topicals** — 10 photos are in the repo (`Topicals/`, named by form: Balm/Salve,
   Bath Salts, Cream, Gel, Lotion, Lubricant, Oil, Roll-on, Stick, Transdermal
   Patch) but **not wired up**. Jack said "hold up on that for now." They imply
   a form-based filter like edibles, and there's only 1 topical product.
2. **Pre-roll + drink photos** — the only products still rendering blank.
3. **Account screens** — the remaining frames.
4. **Drinks** — the edibles IA says drinks are "intentionally excluded and will
   be implemented separately." The app still has 1 legacy drink product and a
   Drinks category circle.

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
│   └── gen_holistic_logo.py      ← generates the Holistic lifestyle logo
├── product info/                 ← Jack's source data (.docx/.xlsx)
├── assets/
│   ├── product assets/           ← photos by category (Concentrate has sub-folders)
│   ├── Lifestyle logos/          ← the six lifestyle logos
│   ├── Various Brand Logos/      ← Royal Tree, Saints, Freddy's, Skörd
│   └── origins logos/, scents assets/, …
├── hifi-final/                   ← Jack's Figma frames (the source of truth)
└── HANDOFF.md                    ← older handoff, still has useful frame notes
docs/                             ← you are here
```

`origins-app.src.html` is one big file by design — it assembles into a single
portable HTML artifact with no external requests.

---

## Gotchas

- **The artifact URL is stable.** Republish with `url=` to keep it; a new path
  mints a new URL.
- **Don't publish with missing photos.** The build still succeeds when assets are
  gone (WARN + blank tiles) — check the WARN lines before publishing.
- **Jack sometimes uploads an older `origins-app.src.html`** alongside his data
  files via the GitHub web UI, which silently reverts work. Diff before rebasing;
  it happened once and was caught.
- **Git drops empty directories.** Every asset folder has a `README.md` so the
  structure survives deleting its photos (learned the hard way with `Rosin/`).
- **`.empty` is a global CSS class** (empty-cart state, `padding:40px 20px`).
  Don't reuse that name for modifiers — it silently deformed the filter circles.
- **Build takes ~2 min** since the WebP encode; run it in the background.
