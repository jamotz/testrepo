# Origins App — Design Decisions

Why things are the way they are. Ordered roughly by how much rework they'd cause
if someone "fixed" them without knowing the history.

---

## Product data & pricing

### Flower `pr` is the eighth (3.5 g) price, not the gram price
Originally `sizeMult` treated `pr` as the 1 g price, so the shop computed
3.5 g = `pr × 3` = **$174** while the home deal used `pr` directly = **$58** for
the same product. Fixed by setting flower's multipliers to
`[0.4, 1, 1.8, 3.2, 5.5]` so **3.5 g = 1.0**. Every window now derives from one
`priceFor()`. *Don't "correct" the 0.4 — it's deliberate.*

### Flower defaults to the eighth, everything else to its cheapest size
Jack: show 1 g as available but make 3.5 g the one displayed, falling back to
1 g if an eighth doesn't exist.

### Tax is inclusive
The listed price is what the customer pays; tax is 37% **of** that total, not
added on top. A $174 eighth = $64.38 tax included. Cart shows pre-tax subtotal,
the included tax, and the total.

### The discounts *are* the two home-page flower deals
An earlier version had arbitrary `sale` flags with a flat 1.3× "was" price,
which put strikethroughs on random products (Distillate, Kief) while three of
the four actual deal flowers showed none. Now the deals are the only discounts:

- **2 for $50** → $25/eighth on the four deal flowers, **pairs only** (2, 4, …).
  Odd units stay at regular price. Jack asked for this explicitly.
- **40% off** → 14 g / 28 g on the same four, no quantity requirement.

### Catalog products carry explicit per-size prices
Jack's flower catalog lists exact prices per size that don't follow a clean
multiplier, and Torus products have no 1 g. So products can override with `pz`
(price map) and `szs` (own size list). The multiplier path still serves the
original mock products.

---

## Filters

### Concentrates: two layers, drill in place
Jack's first look at a stacked two-row text-chip layout was rejected. What he
wanted: **keep the existing bubbles**, and tapping a category *replaces* the row
with its consistencies, with the category parked far-left as a filled orange
back bubble. Tap it again to go back.

- **Main filters keep photos; sub filters were photo-less** until he supplied
  consistency photos — now both have them.
- **No product counts** under the bubbles.
- **"Rosin"**, not "Rosin (Solventless)". **"Diamonds"**, not "Diamonds & Sauce".
- **Order is fixed**: Distillate, Live Resin, Rosin, Kief, Hash, RSO.
- Bubble labels never wrap — every bubble sits at the same height.

### Edibles: category → extraction → strain (THC), or category → effect
The IA sheet lists Level 3 as `"Distillate → Sativa"` (12 combinations), which
reads as either 12 flat tiles or a further drill. **Jack confirmed: drill** —
extraction bubbles first, then strain. The other four categories drill straight
to their effect tiles.

### Edible form is a drawer facet, not part of the IA path
The IA filters by cannabinoid category only. Jack still wanted shoppers to
narrow by form, so Gummies / Chocolate / Hard Candy / Baked Goods / Capsules
live in the Filter drawer (`S.eform`) rather than the bubble path.

### Ratios are metadata, not filters
Straight from the IA notes. Tiles *display* the cannabinoid combo and ratio
("CBD:CBN 10:1"); effect filters decide which products appear. The one CBD-only
product (Pain Relief) shows **total CBD mg** instead of a ratio.

### Breadcrumbs mirror the filter, not the product type
Concentrate tiles read **"Rosin › Live Rosin"** (category › consistency), not
"Concentrates › Rosin". Edibles read **"Gummies › Distillate"** (form ›
extraction/effect). Flower still reads "Flower › Indoor".

---

## Layout & sizing

### Shop browse rows cap at 10; the filter shows everything
Category rows preview 10 products; "See All" / the category circle opens the
full catalog (flower: 10 in the row, all 35 under the filter).

### Tile size is toggle-ready
Home and shop tiles both render at `zoom:.9`, applied via a `tiles-compact`
class on `#view`. **Removing that class restores the larger tiles** — reserved
for a future accessibility size toggle. Don't delete the class.

### Product-page Add to Cart becomes a stepper *in place*
Tapping Add to Cart swaps the solid orange pill for a white pill with an orange
outline, `−` and `+` at the ends, count centred — same footprint, so nothing
shifts. An earlier version used floating circles and was rejected.

### The "2 for $50" label is permanent
It stays visible on eligible eighths at every quantity, as the deal's label
rather than a temporary prompt. The 40%-off items carry an equivalent line.

### Small category icons scale 50%
Flower, Pre-Rolls, Vapes and Topicals sit small inside the category ring, so
they're scaled 1.5× to match the others visually.

---

## Assets

### One asset tree, Concentrate is the only nested folder
`product assets/` mirrors Jack's own folder layout: Concentrate (with
Distillate, Live Resin, Rosin, Kief, Hash, RSO) plus flat Flower, Edibles,
Prerolls, Topicals, Vapes. Background-free cut-outs sit **beside** their
originals rather than in a parallel tree.

### Every folder keeps a README
Git doesn't track empty directories — deleting the last file in `Rosin/` removed
the folder from GitHub. Each folder now has a `README.md` (which also lists the
image keys the app expects) so the structure can't vanish.

### Background-free photos are preferred automatically
Resolution order: `NOBG` map → a file named exactly `<key>.png` → the
white-background original. Drop in `rosin.png` and it wires itself up.

### WebP for transparent photos
`embed_rgba` emits WebP q86 instead of PNG — identical alpha, build down from
8.75 MB to 2.3 MB. Costs ~2 min of encode time per build.

### Auto background removal is retired
`embed_cut()` (edge flood-fill) was used before Jack supplied cut-outs. It left
halos where products had interior white — the gummies needed a special
lower-threshold global mode. Now that real cut-outs exist, nothing calls it.
Kept in the file as a fallback.

---

## Content authored vs. supplied

Jack's sheets supply brand, name, category, prices and copy. The app also needs
THC%, lifestyle, feelings, taste and terpene, which the sheets don't carry.
Those were **authored per real strain** (Jack Herer piney/energizing, GMO
Cookies garlicky/heavy, ACDC clear/CBD → Holistic) rather than randomized.

Explicitly authored, flagged in code:

- **Concentrate rows 57–60** (Distillate Syringe ×2, RSO Oil Syringe ×2) —
  `AUTHORED` block in `gen_concentrates.py`.
- **Kief rows 51–56** — supplied by Jack in chat, kept in an `EXTRA` block since
  they're not in the xlsx.
- **Edible prices** — the sheet has none; authored to realistic WA levels,
  scaled by form and extraction premium.

### Edible photo assignment
Photos are assigned by flavour where it reads (Blackberry → purple gummy, Mango
→ yellow hard candy). Three adjustments to use all 15:

- Chocolates rotate all three shots — no chocolate product has a "Dark
  Chocolate" flavour, so reserving the dark photo for it left it unused.
- Huckleberry → **red** gummy (red huckleberry is a real PNW species), so purple,
  red and orange are all in play across only three gummy flavours.
- Some baked goods renamed with Jack's blessing: Raspberry / Blood Orange →
  **Brownie Bites**, Peach / Lemon → **Crispy Treats**. They were all "Cookie
  Bites", leaving the brownie and rice-crispy photos unused.

---

## Copy & branding

- **"Types of Cannabinoids"**, not "Types of THC". Delta-8 was removed
  ("that shit nasty" — Jack); a "Types of CBD" tab was added.
- **Typos in Jack's frames are corrected** in the app (Continue, Chocolates,
  Differences) — a standing decision.
- **Cream → white background.** The brand moved off cream.
- **Holistic** is the sixth lifestyle, added for CBD-forward products, placed
  last. Its logo is generated: a blocky "H" with a leaf cut into each bar, sized
  to match Jack's other leading letters (~1.05× the wordmark cap height), and the
  wordmark recomposed from his real letterforms (H,T from NIGHTLIFE; O,L,I,S,C
  from SOCIAL) so the font matches exactly.
- **Landing store cards**: phone top-right, address stacked below, no "Open
  until" line ("people can use their brain").
