# Origins App — Project Handoff

**Last updated:** 2026-08-18 · branch `claude/project-docs-review-todos-os7hx4`
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

**Only the branch named at the top of this file is current.** Superseded
`claude/project-docs-review-*` branches stay on origin and look plausible —
`sz8jwv` is 18 commits behind and predates the pre-rolls and every Account
screen. Check this line against `git log` before trusting a branch, and update
it here when the work moves.

---

## Start here (new session)

```bash
git fetch origin claude/project-docs-review-todos-os7hx4
git checkout -B claude/project-docs-review-todos-os7hx4 origin/claude/project-docs-review-todos-os7hx4
python3 -m pip install --quiet Pillow          # recycles remove it
python3 reference/origins/hifi-build/asm_app.py
```

The build prints `wrote <path> (NNNN KB); imgs=142; markers left=0` and a `WARN`
line for any asset it can't resolve. **Containers are ephemeral — commit and
push often.**

Rendering/screenshots use the preinstalled Chromium via Playwright:
`/opt/pw-browsers/chromium-*/chrome-linux/chrome` (path moves after recycles;
`require('/opt/node22/lib/node_modules/playwright/index.js')`).

Publishing: republish to the **same artifact URL** above, or the link Jack has
already shared stops being the live one. Pass the URL as `url=` — publishing
without it mints a separate artifact. **The live link is current as of
`1182af6`** (published 2026-08-18) — the Final/pt2 catalogs, terpene-driven
feelings and scents rendered with Jack's icon set, drinks with their IA bubbles,
the four deal flowers with bag-wide mix & match, the Deals Calendar (two-a-week
rota, running-now first), the home deal rows with matched brand tiles, Torus and
a See All per deal, and the brown title bar on every screen. Bump this line whenever you
republish; it's the only way a new session can tell whether the link is behind
the branch.

If the publish is refused with *"hasn't viewed the latest version"*, another
session republished since. `WebFetch` the artifact URL first — it **is**
fetchable despite the claude.ai login, and it saves the full HTML locally so
you can diff the live body against your build before deciding. Only use
`force:true` if Jack says to discard the other version.

The build carries **no `<title>` tag** (it is a fragment), so the artifact takes
its name from the `title` parameter — pass `Origins — App Prototype` on every
republish or the gallery entry renames itself. Favicon 🌿; keep it, a changed
icon reads as a different tab.



---

## Working rules (Jack's, non-negotiable)

1. **Stay true to Jack's frames by default.** Deviate only when he says so.
2. **One screen at a time** — build, screenshot, get sign-off, then move on.
3. **Ask clarifying questions before building anything non-trivial.** Wrong
   guesses on structure cost real rework (see `design-decisions.md`).
4. **Never invent product data** that contradicts his sheets. Authored filler is
   fine when he's asked for it, but mark it clearly. As of 2026-08-14 almost
   nothing is authored: the generators' invented tables are gone and the sheets
   supply strain, lifestyle, potency, prices, copy and the terpenes that drive
   feelings and scents. What remains, all flagged in place:
   - the 10 Kief/RSO rows written onto the concentrate sheet — strains, types
     and terpenes copied from the flower catalog; only brand, size and copy
     composed. They **are** on the sheet and in the app (6 Kief, 4 RSO); only
     their provenance is authored
   - flower's star rating and review count (`gen_catalog_products.stable()`) —
     no sheet states them
   - the Account block in `origins-app.src.html`: Noelle's orders and reviews,
     and Seattle's opening hours
   - which four flowers carry the deal (`DEALS` in `gen_catalog_products.py`) —
     Jack named the two brands, the strains within them are a first pass
   - the deals calendar's schedule (`DEALDEF`) — seven deals on a four-week
     rota, two a week, and the edible deal's brand (Wyld). The **line-ups aren't authored**: each
     deal resolves its products from the catalog, by price rank where Jack
     described one ("the 4 cheapest", "the 5 most expensive")
   - run-out dates are generated (3–7 days after a run starts, hashed so they
     don't move between renders). `DEAL_UNTIL` pins one if Jack wants a fixed
     date
   - topical and edible feelings/taste, until those sheets catch up

   **Before writing a table that assigns something per strain, check the source
   for a column that already says it.** That mistake has been made twice — once
   with lifestyle, once with terpenes.

---

## Current state

**308 products** across six types:

| Type | Count | Source | Photos |
|---|---:|---|---|
| Flower | 50 | `Flower Final pt2 Product List for WA.xlsx` | by strain type ✓ |
| Concentrate | 60 | `Concentrate Final Product List for WA.xlsx` (all 60 rows, Kief and RSO included) | per consistency ✓ |
| Edible | 50 | `WA_Edibles_By_Brand_Final_Curated_Normalized.xlsx` | by form + name ✓ |
| Pre-roll | 60 | `Pre-roll pt2 Product List Final for WA.xlsx` | by type + pack count ✓ |
| Topical | 38 | `WA_Topicals_Product_Catalog_Final.xlsx` (sheet 2) + 3 authored | one per form ✓ |
| Drink | 50 | `WA_Drinks_50_Product_List_Source_Inspired_Unique_Descriptions.xlsx` | by type + flavour colour ✓ |

**87 Holistic products**; **62 carry a cannabinoid ratio** (pre-rolls carry
none by design — see `design-decisions.md`).

**Feelings and scents come from the terpenes** on flower, concentrates and
pre-rolls (170 products) via `terpmap.py` — nothing authored. Edibles, topicals
and drinks still carry the old placeholders and are the remaining work.

**Lifestyle is the strain, renamed** (Jack, 2026-08-12) — Sativa/Sativa
Hybrid/Hybrid/Indica Hybrid/Indica/CBD = Discovery/Adventurous/Social/Unwind/
Nightlife/Holistic, one-to-one, with a settings toggle planned to swap the two
vocabularies. Every catalog states the strain, so **no generator authors a
lifestyle** — read the column, don't invent a rule. Four generators each had
their own invented rule until this landed; all four disagreed with their sheets.
Topicals are uniformly Holistic (nothing there is psychoactive).

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 8 topic pages) · vape dead-end · Deals Calendar (7 deals, every shelf) · Account · Loyalty
Points · Account Settings · Order History · Recommended Products · Past
Reviews · About Us.

**Every frame in Jack's `hifi-final/` set is now built.** The Deals Calendar
(2026-08-18) has no frame behind it either — Jack specified it in chat, the way
the four unframed Account pages were specified. What's left is polish and the
open questions below.

---

## Immediate next steps

1. **General touch-ups** — Jack is doing a pass across the app. The Account
   screens have been through one round already (see `design-decisions.md`).
2. **Feelings and scents on edibles, topicals and drinks — parked** (Jack,
   2026-08-17: "ignore for now"). Don't pick this up without him. The other
   three shelves are done; these 138 products still carry the old vocabulary, so
   their chips fall back to generated SVGs while flower/concentrate/pre-roll
   show Jack's icons. The mismatch is visible side by side. Three separate
   problems:
   - **topicals use their own *form* as a taste** — `Roll-On`, `Lotion`,
     `Balm / Salve`. Always wrong; just never noticed. A topical arguably
     shouldn't carry a taste at all.
   - **drinks use the whole flavour string** as one value (`Blackberry Lemonade`,
     `Mojo-Rita`) — product names, not descriptors.
   - **edibles use raw flavour words** (Cream, Gas, Candy, Lemon), most of which
     map cleanly onto the 16.

   These sheets have no terpene columns, so they can't use `terpmap`. Either add
   terpenes, or map their existing flavour/effect columns onto the 30 terms.
   Offered but not built: a remapping sheet listing all ~120 old values with a
   proposed new term and product counts, so Jack reviews 120 rows instead of 138
   products.
3. ~~The home-page deals have no products.~~ **Done 2026-08-17.** Four flowers
   are nominated in `DEALS` (`gen_catalog_products.py`) — Passion Flower's
   Northern Lights and Pineapple Express, Lifestyles' Gelato Cake and Jack
   Herer — so both deal sections render again. 2-for-$50 now mixes and matches
   across the whole bag (any two deal eighths, same strain or not). **Jack still
   owns the strain picks**: he named the two brands, the four strains were
   chosen to spread the row across four lifestyles and are one line each to
   swap.
4. ~~Drinks — the bubble path.~~ **Done 2026-08-17**, from
   `WA_Drinks_IA_Condensed.xlsx`: THC / CBD / Blend → Drink / Shot / Seltzer /
   Sorbet / Honey, two levels, reusing the pre-roll bubbles. The IA rules out a
   third level (size, dose and ratio are all tile metadata, never navigation),
   so the drawer's size facet is locked off for drinks.
5. **The settings toggle** that swaps strain names for lifestyle names. Unblocked
   — all 308 products satisfy strain ↔ lifestyle, so it's a label lookup, not a
   data migration.
6. **Four sub-bubbles have photos but no products**: `Rosin Coins`,
   `Full Melt Hash`, `Distillate Syringe`, `Dab Applicator` — one level down
   inside Rosin, Hash and Distillate. Every category itself is stocked,
   **Kief (6) and RSO (4) included** — an earlier note claiming those two were
   empty was wrong (Jack, 2026-08-17; see `design-decisions.md`).

7. **The drawer's Brands facet matches almost nothing.** (Freddy's is now out
   of the home row — see below — but the drawer still lists it.) `BRANDS` lists
   `Artizen · Freddy's · Royal Tree · Saints · Skörd · St. Ideal` and `match()`
   compares it to `p.b` exactly, but the catalog says `Royal Tree Gardens` and
   `Skord` (no umlaut), and carries no `Freddy's` or `St. Ideal` at all — so
   four of the six return zero products. Found 2026-08-18 while wiring the
   calendar, which matches the same labels as a **prefix** and resolves 18
   flowers from three brands. Fix is either a prefix match in `match()` or a
   `BRANDS` list taken from the catalog; needs Jack's call on which brands
   should be offered.

*Size as a navigation step was considered and rejected* (Jack, 2026-08-12):
size lives in the product tile, not the filter path. Don't re-propose it.

---

## Repo layout

```
reference/origins/
├── hifi-build/
│   ├── origins-app.src.html      ← THE app (markup + CSS + JS + product data)
│   ├── asm_app.py                ← build: inlines fonts + images -> one HTML file
│   ├── gen_catalog_products.py   ← flower products from the .xlsx
│   ├── gen_drinks.py             ← drinks from the .xlsx + drinks IA
│   ├── terpmap.py                ← terpenes -> feelings + scents
│   ├── xlsxread.py               ← the one xlsx reader they all share
│   ├── gen_concentrates.py       ← concentrates from the .xlsx
│   ├── gen_edibles.py            ← edibles from the .xlsx + filter IA
│   ├── gen_prerolls.py           ← pre-rolls from the .xlsx
│   ├── gen_topicals.py           ← topicals from the .xlsx (+ 3 authored rows)
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
- **Empty cells shift rows two different ways.** Excel omits some empty cells
  entirely (a reader appending in document order shifts every column after a
  blank — this is why a sheet once parsed with `Cannabinoid Combo` landing in
  `Effect Filter`), *and* writes others self-closing, `<c r="E2" s="29"
  t="str"/>`. A cell regex that tries the open-tag branch before the
  self-closing one reads `<c …/>` as an open tag and swallows the next cell's
  value — the same shift, but silent even when you address by column letter.
  Address by letter **and** match the self-closing branch first. Copy the reader
  in `gen_prerolls.py`; the other three now match it.
- **Sectioned sheets carry `=== SECTION ===` rows.** Filter them out or they
  parse as products.
- **Don't trust a "this sheet is malformed" note without re-checking it.** The
  pre-roll catalog was documented for two days as having columns that didn't
  match its own header. It doesn't — that was the self-closing-cell bug above,
  and `gen_prerolls.py` had been written to compensate for it. Both are fixed
  and the emitted products never changed. If a sheet looks shifted, parse it
  with `xml.etree` first and compare before writing code around it.
- **Don't publish with missing photos.** The build still succeeds when assets are
  gone (WARN + blank tiles) — check the WARN lines before publishing.
- **Jack sometimes uploads an older `origins-app.src.html`** alongside his data
  files via the GitHub web UI, which silently reverts work. Diff before rebasing;
  it happened once and was caught.
- **Copy address can't be verified from a build container.** The About Us copy
  control tries `navigator.clipboard` and falls back to an offscreen textarea +
  `execCommand`; both branches are tested locally (including with the Clipboard
  API removed and with `writeText` rejecting), but which one the *published*
  artifact takes depends on the iframe's permission policy, which isn't visible
  from outside the frame. The published page can't be clicked from here — it's
  behind claude.ai auth and WebFetch only reads HTML. Ask Jack to tap it once.
  If the toast shows the address instead of "Address copied", both branches were
  blocked and the fallback is to render the address in a selectable `<input>`.
- **Git drops empty directories.** Every asset folder has a `README.md` so the
  structure survives deleting its photos (learned the hard way with `Rosin/`).
- **`.s` and `.empty` are global CSS classes** — `.s{display:none}` in
  particular. Namespace anything new (the size sheet uses `fs*`), or it vanishes
  silently.
- **Build takes ~2 min** since the WebP encode; run it in the background.
