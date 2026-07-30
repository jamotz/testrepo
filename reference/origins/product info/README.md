# Product info

Drop product copy here — Word docs (`.docx`) are fine, as are `.md`/`.txt`/`.csv`.
Jack supplies the real product details; this is the source of truth for what the
app shows on the Product Info (PI) screens and shop cards.

## What the app uses per product
The in-app product model currently carries these fields, so anything covering
them can be mapped straight in:

| Field | Meaning | Example |
|-------|---------|---------|
| name | Product name | Animal Sherbert |
| brand | Producer | Gold Leaf |
| type | flower / preroll / concentrate / edible / drink / topical | flower |
| sub | Sub-type | Indoor, Rosin (SHO), Gummies |
| strain | Indica / Sativa / Hybrid / CBD | Indica |
| THC % (or mg) | Potency — mg for edibles/drinks | 22.5% |
| price | **Eighth (3.5 g) price for flower**, unit price otherwise | 58 |
| lifestyle | Discovery / Adventurous / Social / Unwind / Nightlife / Holistic | Unwind |
| feelings | 3 effects | Giddy, Relaxed, Hungry |
| taste | 3 scent/flavor notes | Aromatic, Skunky, Diesel |
| terpene | Dominant terp | Diesel |
| description | Short paragraph on the PI page | — |
| rating / reviews | Stars + count | 4.0 / 11 |

Anything extra (lab results, harvest date, grower notes, COA links) is welcome —
tell me where it should surface and I'll add it to the PI layout.

## Notes
- Sizes come from the app's per-type size list; prices scale from the base price
  (flower is priced per eighth).
- Deals are separate from product copy — the two home-page flower deals
  (2-for-$50 eighths, 40% off 14g/28g) are configured in `asm_app.py`/the app
  source, not here.
- Once files land here, tell me and I'll parse them and wire the real copy into
  the product data.
