# Origins App — Project Handoff

**Last updated:** 2026-08-20 · branch `claude/accessibility-handoff-review-dhabtz`
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
`sz8jwv` predates the pre-rolls and every Account screen, and `4b84p7` stops
before the deals, the calendar and everything after. `os7hx4` is the most
recent of these and the easiest to mistake for current: it holds every screen
and reads as complete, and it is behind by exactly the phone-bezel fix. Check
this line against `git log` before trusting a branch, and update it here when
the work moves.

---

## Start here (new session)

```bash
git fetch origin claude/accessibility-handoff-review-dhabtz
git checkout -B claude/accessibility-handoff-review-dhabtz origin/claude/accessibility-handoff-review-dhabtz
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
`231a9ac`** (published 2026-08-20) — the Final/pt2 catalogs, terpene-driven
feelings and scents rendered with Jack's icon set, drinks with their IA bubbles,
the four deal flowers with bag-wide mix & match, the Deals Calendar (two-a-week
rota, running-now first), the brown title bar on every screen, the outlined
button family with one weight pill, and Advanced Settings. Since 2026-08-20 it
also carries the phone bezel taking its own unscaled width (the black frame
wraps the screen evenly at every window size), Filter in Origins U's Search
olive, and Origins U on the shop's own card — olive border, no label bar — with
Liquid Edibles and Vapes as their own categories and the Lifestyles tile on its
six colours, and Enlarged view as a token-driven accessibility layer (see architecture.md). Bump this line whenever you republish; it's the only way a new
session can tell whether the link is behind the branch.

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
5. **Say what isn't built, in the UI as well as here.** When *Enlarged view*
   was a placeholder it carried a "Coming soon" tag and toasted, rather than
   quietly doing nothing. It is built now (2026-08-20) and the tag is gone —
   the rule stands, the example is just retired. Origins U's *Search* pill is
   the live one: it toasts "coming soon" because there is no search behind it.

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
Nightlife/Holistic, one-to-one. Every catalog states the strain, so **no
generator authors a lifestyle** — read the column, don't invent a rule. Four
generators each had their own invented rule until this landed; all four
disagreed with their sheets. Topicals are uniformly Holistic (nothing there is
psychoactive).

The **Use product type** switch in Advanced Settings swaps the two vocabularies
app-wide (2026-08-18). It is a label lookup, not a data change: `lifeLabel(key)`
is the only place a lifestyle word is printed — **use it, or your new screen
won't follow the toggle**.

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 10 topic pages) · vape dead-end · Deals Calendar (running now, then a
month of upcoming) · Account · Loyalty Points · Account Settings · Advanced
Settings · Order History · Recommended Products · Past Reviews · About Us.

**Every frame in Jack's `hifi-final/` set is now built.** The Deals Calendar and
Advanced Settings have no frames behind them either — Jack specified both in
chat, the way the four unframed Account pages were specified. What's left is
polish and the open questions below.

**The visual language settled on 2026-08-18** and is worth reading in
`design-decisions.md` before adding a control:

- **Buttons are outlined** — coloured border, white interior, coloured text.
  Filter and Origins U's Search share one olive; Sort/Continue/Logout orange. A
  **solid fill now means the primary action** (Add to Cart, Checkout, the hero).
- **One weight pill everywhere** — outlined olive for a size you could pick,
  solid olive for the one you are on, tinted chip for serving/total, which is a
  fact rather than a choice.
- **Every screen wears the brown `.sbar` title bar.**
- **Cards are the shop's product tile** — white, 1.5px `#E1DBCD` border, 12px
  radius, one shadow. Origins U's tiles joined it on 2026-08-20, dropping a
  `#D9A87C` peach that was in no other screen. They keep one departure: no
  label bar (the name is olive text under the photo) and an `--olive` border,
  since with the bar gone the border is what carries the colour.

---

## Immediate next steps

1. **General touch-ups** — Jack is doing a pass across the app, screen by
   screen. Home, shop, cart, Origins U and the account screens have each been
   through a round (see `design-decisions.md` for what was decided and why).
2. **Enlarged view is built** (2026-08-20) — one scale factor, `--enlarge`
   1.25, applied as `zoom` to `.view` and `.tabs`, so type, photos, buttons and
   spacing all grow together and the app reflows into an effective 362px. Clean
   to 1.30; 1.35 breaks the two-up product grid. If Jack wants it stronger,
   change the one number and re-run the overflow check — don't start adding
   per-rule font sizes.

3. **Feelings and scents on edibles, topicals and drinks — parked** (Jack,
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
4. **The drawer's Brands facet matches almost nothing.** `BRANDS` lists
   `Artizen · Freddy's · Royal Tree · Saints · Skörd · St. Ideal` and `match()`
   compares it to `p.b` exactly, but the catalog says `Royal Tree Gardens` and
   `Skord` (no umlaut), and carries no `Freddy's` or `St. Ideal` at all — so
   four of the six return zero products. (Freddy's is out of the home brand row
   as of 2026-08-18, but the drawer still offers it.) Found while wiring the
   calendar, which matches the same labels as a **prefix** and resolves 26
   flowers from three brands. Fix is either a prefix match in `match()` or a
   `BRANDS` list taken from the catalog; needs Jack's call on which brands
   should be offered.
5. **Four sub-bubbles have photos but no products**: `Rosin Coins`,
   `Full Melt Hash`, `Distillate Syringe`, `Dab Applicator` — one level down
   inside Rosin, Hash and Distillate. Every category itself is stocked,
   **Kief (6) and RSO (4) included** — an earlier note claiming those two were
   empty was wrong (Jack, 2026-08-17; see `design-decisions.md`).
6. **One open question for Jack**, flagged where it lives: the **four deal
   flowers** are his brands but my strain picks (`DEALS` in
   `gen_catalog_products.py`, one line each to swap).

   *The Filter-pill contrast question is closed* (2026-08-20): Filter now uses
   Origins U's Search olive `#555624` at 7.66:1, clearing AA and AAA. The
   `#5C7540` drop-in that was earmarked for it is no longer needed.

### Done in this pass (2026-08-17 → 18)

| | |
|---|---|
| Home deals | Four flowers nominated in `DEALS`; 2-for-$50 mixes and matches across the whole bag; brand tiles matched to the product tiles; Torus replaced Freddy's; a See All card per row opens the whole deal |
| Deals Calendar | New screen from both hero buttons — seven deals on a four-week rota, two a week, **running now** then a month of upcoming, each with a generated run-out date and a product dropdown |
| Drinks | Bubble path built from `WA_Drinks_IA_Condensed.xlsx`; the size facet lists real volumes derived from the catalog |
| Kief / RSO | The "no products" note was wrong — the sheet has all 60 concentrate rows |
| Chrome | Brown title bar on every screen; trolley icon over Cart; "Your Cart"; Origins U photos wired to images the build actually embeds |
| Buttons | The outlined family, one weight pill app-wide, hero type at the app's own size, Logout matched to Account Settings |
| Advanced Settings | New screen: **Use product type**, **Enlarged view** and **Reduce motion** — all three working (Enlarged view landed 2026-08-20) |

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
│   ├── Various Brand Logos/      ← Royal Tree, Saints, Torus, Skord (+ Freddy's, unused)
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

**Flower regenerates like everything else now** — the old "don't regenerate
flower" warning is retired. It existed because photos were drawn sequentially
from a shuffled pool, so inserting one product reshuffled every photo after it.
Photos are now chosen by hashing the strain name against a pool scoped to that
strain's type, so a strain keeps its photo across rebuilds and row order doesn't
matter.

**Regenerating flower is in fact how you change the deal line-up**: `DEALS` in
`gen_catalog_products.py` decides which four rows carry `sale:1`, and the
generator refuses to emit if a nomination stops matching exactly one row, or if
a nominated eighth is at or under the $25 deal price.

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
- **A lifestyle word is only ever printed by `lifeLabel(key)`.** Print `FEEL[k]`
  directly and Advanced Settings' *Use product type* switch won't reach your
  screen. The Guide Me wizard is the exception that proves it: its lifestyle
  words are *wordmark images*, so each option carries a text twin that CSS swaps
  in.
- **A fixed height inside a `.dealrow` stretches every product tile in it.**
  Flex rows default to `align-items:stretch`, so a brand or See All card with
  its own height drags the tiles up to meet it — that shipped once, 40px too
  tall. Let them stretch; only the brand row, which has no product tile to set
  the height, is measured.
- **A hidden screen measures zero.** Anything that sizes itself from a rendered
  element has to run when its screen is actually on (`nav()`), not at load.
- **`.s` and `.empty` are global CSS classes** — `.s{display:none}` in
  particular. Namespace anything new (the size sheet uses `fs*`), or it vanishes
  silently.
- **Build takes ~2 min** since the WebP encode; run it in the background.
