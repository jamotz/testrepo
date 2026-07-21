# RESUME HERE — Jack Motzkin portfolio (Origins in progress)

**To resume in a fresh session:** "Read reference/origins/HANDOFF.md and continue the Origins Guide Me wizard."

Everything below is committed. **Recycles wipe uncommitted work** — always start with:
`git fetch origin claude/portfolio-redesign-81crin && git checkout -B claude/portfolio-redesign-81crin origin/claude/portfolio-redesign-81crin`
Commit + push after every change. Branch: `claude/portfolio-redesign-81crin`.

## The working rule (Jack's, non-negotiable)
**Stay true to Jack's frames by default; deviate only when he explicitly says so.**
Work **one screen at a time**, show a screenshot, get sign-off, then next. Ask clarifying
questions before building anything non-trivial.

## Skills — USE THEM when designing the website + interactive elements
When designing/building the actual website pages and any interactive elements
(the app prototype, wizard, filters, hover/scroll behaviors, animations), **invoke the
design skills** rather than hand-coding cold — call `Skill` first, then execute:
- `ui-ux-pro-max` — UI/UX decisions: layout, palettes, font pairing, components, interaction patterns
- `frontend-design` — distinctive visual direction for new UI
- `ui-styling` — accessible, component-level styling
- `artifact-design` — auto-loads when publishing; design fundamentals for artifacts
Skills refine **execution** — they never override Jack's frames, which stay the source of truth.

## What's DONE
- **Oxfam** case study (`site/src/pages/work/oxfam.astro` in the real Astro site + standalone
  artifacts). Landing card wired. Clickable "website within a website" prototype embedded.
- **Origins app prototype** (`reference/origins/hifi-build/origins-app.src.html` +
  `asm_app.py`) and **Origins case study** (`origins-case.src.html` + `asm_case.py`).

### Origins Guide Me wizard — dialed so far
- **FEEL** = the **Lifestyle Overview**: real brand logos (Discovery/Adventurous/Social/
  Unwind/Nightlife), left-aligned, whole button in the lifestyle color, checkbox kept,
  logo enlarged. (Logos are glyph-extracted in `asm_app.py` via `embed_glyph`.)
- **METHOD** = 7 methods incl **Tincture**.
- **Branching (verified):** smokeable (Flower, Pre-Roll, Concentrate) → **Taste**;
  **Edible** → type-of-edible (Chocolate/Gummy/Mint/Drink), **no Taste**; Topical/Tincture
  → straight to Recommendations; **Vape** → web-only dead-end. Flower has **no** Indoor/Outdoor.
- Progress bar present; wizard is **full-screen immersive** (nav/tabs hidden during it).
- Location **fixed to Redmond**; "Show tap points" toggle; iPhone proportions (393×852).
- Finish/Recommendations → "Browse products" hands off to Shop **pre-filtered** (never empty).
- **Case study prototype section**: nav **auto-hides** + phone **grows to fill screen** on scroll
  (IntersectionObserver in `origins-case.src.html`).

## What's NEXT (agreed order)
1. Finish walking Guide Me; then rebuild **sub-type screens** (`GM - CONCENTRATES`,
   `GM - EDIBLES`), **Taste**, and **Finish** 1:1 against the frames in
   `reference/origins/hifi-final/` (bring the **small monogram logos** into the finish chips).
2. Then, one at a time, faithful to `hifi-final/`: **Landing** (store picker, Redmond),
   **Shop** + `SHOP-CONCENTRATE` + `PI 1`(concentrate) / `PI 2`(flower) + Vape,
   **Cart** (`SC-CHECKOUT` / `SC-OVERVIEW`), **Deals**, **Account** (+ settings, loyalty),
   **Origins U** (+ `ED-FLOWER`).

## Frame naming (Jack's convention)
Full name on hub, abbreviated on subpages: `GM-`=Guide Me, `SC-`=Shopping Cart, `AC-`=Account,
`ED-`=Education, `SHOP-`, `PI`=Product Info. Note: `SHOP-VAPE` was renamed from a mislabeled
`SHOP-FLOWER`; the flower detail is `PI 2`, concentrate detail is `PI 1`.

## Palette / fonts
Origins accent **orange #F1601C**. Lifestyles: Discovery #A0463C, Adventurous #C09A64,
Social #F3D390, Unwind #78A6C5, Nightlife #5D8A85. Brown #2E261E, olive #555624, cream #E6C7A7.
App fonts: Oswald (headings) + Georgia (body). Case-study shell: Space Grotesk + IBM Plex.

## Build / verify
- `python3 -m pip install --quiet Pillow` (recycles remove it)
- Assemble app: `python3 reference/origins/hifi-build/asm_app.py`
- Assemble case study: `python3 reference/origins/hifi-build/asm_case.py`
- Playwright chrome path (moves after recycles):
  `find /opt/pw-browsers/chromium-* -name chrome -path '*chrome-linux*'`
- Fonts cached in `reference/oxfam/hifi-build/fontcache/` (shared).

## Artifact URLs (stable — republish with `url=` to keep them)
- Origins app: https://claude.ai/code/artifact/ff102055-8262-4b48-a681-8d77f802c968
- Origins case study: https://claude.ai/code/artifact/cca806e2-af8f-4133-9492-7d1ddfb8a29e
- Oxfam hi-fi: https://claude.ai/code/artifact/2c86d450-0bdc-4708-ab41-c5a093c44316
- Oxfam clickable proto: https://claude.ai/code/artifact/b82aa575-1167-4ddb-875e-619ff0f92108
- MOTZ landing (Kinetic): https://claude.ai/code/artifact/fb62ff96-edb1-4670-b9a0-28a104581b23
