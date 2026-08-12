# Scent & Feeling icons

30 individual icons, sliced out of `../Scents and Feelings.png` — Jack's contact
sheet, which carried all 30 in one image with the filename printed under each.

## Where they came from

The sheet is a 1536×1024 RGBA image laid out as four bands of icons, each
followed by a ~19px label strip. The bands are **not** a uniform grid — the two
orange rows hold 7 each and the two olive rows hold 8 — so the slicer finds the
bands and columns by ink projection rather than assuming a grid.

Two icons contain internal gaps that split into separate columns and have to be
merged back: **cerebral** (the brain's central fissure) and **peppery** (the
mill and its scattered flecks). Column runs closer than 30px are merged; real
icons are 50–100px apart, so the threshold is comfortable.

Each icon is then tightened to its own alpha bounding box, padded 10%, centred
on a square canvas and resampled to **256×256** with alpha preserved.

## The 30 names

They match the vocabulary sheets exactly — 30 terms, 30 icons, no gaps in either
direction:

| Set | Source sheet | Count | Colour |
|---|---|---:|---|
| Feelings | `cannabis_feelings.xlsx` | 14 | orange |
| Smell & Taste | `cannabis_smell_taste.xlsx` | 16 | olive |

**Feelings** — relaxed, uplifted, energized, focused, creative, calm, sleepy,
happy, euphoric, social, cerebral, grounded, motivated, mellow

**Smell & Taste** — citrus, fruity, sweet, floral, pine, earthy, herbal, spicy,
woody, hoppy, musky, peppery, skunky, tropical, berry, diesel

## Colour

As supplied the icons are **#F54001** (orange) and **#44420F** (olive), which is
close to but not the app palette — `--or` is `#F1601C` and `--olive` is
`#555624`. They are flat single-colour shapes with clean alpha, so recolouring
to the exact tokens is a per-pixel swap if Jack wants them to match.

## Naming

Name a file exactly `<image key>.png` and the build picks it up automatically.
These are keyed by their lowercase term, so `pIcon("Relaxed")` resolves to
`relaxed.png` with a simple lowercase.

---
*Keep this README — it's what keeps the folder in git. An empty folder disappears from GitHub.*
