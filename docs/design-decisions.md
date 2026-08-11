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
- **Edible prices** — *superseded.* The curated sheet now carries real WA retail
  prices ($18–$30) and they're used directly. The authored `BASE`/`EXTRA` table
  is gone.

### Edible photos come from the product name, not the Flavor column
The curated sheet's `Flavor` column doesn't track its own product names — 24 of
50 disagree (Espresso Chocolates reads "Dark Chocolate", Green Apple Hard Candy
reads "Blue Raspberry"). Jack: *flavour doesn't matter, apply the one that looks
closest.* So `flavour_of(name)` derives it and `Flavor` is never read.

Cookies take the cookie shot, brownies the brownie, capsules rotate all three.
Only the rice-crispy photo goes unused — nothing in the catalog is a crispy
treat. Capsules have no flavour in their names ("Daily", "Rest"), so they fall
back to **Unflavored** rather than emitting a blank taste chip.

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

---

## Naming

### Concentrate names drop the consistency
The breadcrumb directly above already reads "Rosin › Rosin Sap", so "Lemon
Cherry Gelato Rosin Sap" said it twice and cost a second line on the tile.
`strip_form()` removes the sheet's Subcategory then its Category from the tail.
Longest concentrate name: 34 → 25 characters.

Flower now has two products called **Northern Lights** — Royal Tree at 0.8% THC
and Passion Flower at 26.8%. Jack: *two growers selling the same strain is
realistic.* Brand, breadcrumb, border colour and the THC bubble separate them.

### CBD comes out of Holistic names
The tile already says CBD three ways — green border, Holistic badge, CBD bubble.
`strip_cbd()` handles it in both generators. Edibles keep their form
("Blackberry Gummies") because it fills the tile and reads naturally.

---

## Tiles

### One line, ellipsis, uniform height
Names clamp to one line. Ragged two-line names were adding 17px to *some* tiles,
which is what made a row look uneven rather than merely tall. Only a handful of
edibles ("Blue Raspberry Chocolates") ever truncate.

### Size far left, price far right, one row
Merging them saved ~28px on **every** tile. Together with the one-line name,
cards went from a ragged 294–311px to a uniform 222px.

### The photo overlay means one thing
Ratio top-left, cannabinoids top-right. An earlier version put the lead *feeling*
top-left on all 149 products; it was dropped because 28% of the catalog leads
with "Relaxed", only 16 distinct values covered everything, and the lifestyle
badge two lines below already carries the mood. The combo string was dropped too
— the bubbles name the cannabinoids, so "THC:CBD:CBG" beside three chips saying
THC, CBD and CBG was the same fact twice.

### The size slot states serving *and* total
The size on a tile meant two different things depending on the shelf: an
edible's `100 mg` is the whole package, a pre-roll's `0.5 g` is one joint. So an
edible hid its serving and a multi-pack pre-roll hid its total. The slot now
reads serving-first — `10mg / 100mg`, `0.5G / 1G` — for edibles and pre-rolls,
with drinks wired to the same path for when they get data.

It keeps the olive it already had but takes the **cannabinoid bubbles' tinted
treatment** rather than the solid fill: serving/total is a fact about the
product, and the solid fill means *the selected size*. Products with one serving
(1-pack pre-rolls, single-dose edibles) keep the plain solid pill, so the two
readings never collide. Flower, concentrates and topicals are untouched.

**The underlying sizes did not change** — `szs`, `pz`, `S.size` and the size
sheet all still key on the same strings. This is display only.

### The tile's cart affordance
Add to Cart became **See more sizes**, opening the sheet. Tapping the card
anywhere still opens the product page — the sheet's own controls are excluded
from that handler, which is easy to forget when adding a new one.

---

## Holistic

**Any product carrying a non-psychoactive cannabinoid is Holistic** — CBD, CBG
or CBN. CBC isn't common enough to include and doesn't appear in the data.
Verified against the sheet: no THC-only edible carries any of them, so the rule
and the data agree exactly.

This overrides whatever strain or effect would otherwise suggest. 65 products.

---

## Topicals

### The filter path is effect → form
From sheet 1 of the catalog: Pain Relief, Recovery, Cooling, Warming, Massage,
Skincare, Intimacy, then the form as the second level — the same shape as
concentrates' category → consistency. This replaced three placeholder words
(Cooling / Warming / Soothing) that predated the sheet.

### Sizes and prices are per product
Every topical carries one size and its own MSRP, so `pz`/`szs` override the
multiplier path entirely. Sizes run 50–250 mL plus "1 Patch" for transdermals.

### The Ratio column is mixed and isn't trusted
It holds `1:1`, `CBD`, and `CBD:CBG 4:1` in the same column. The combo is derived
from which cannabinoids actually carry milligrams; only the numeric tail of
Ratio is kept.

### Massage and Intimacy aren't Holistic
Every other effect is. Massage reads closer to Unwind and Intimacy to Nightlife,
which keeps the Holistic badge meaning relief rather than "topical".

---

## Pre-rolls

### The sheet's columns don't match its header — read by letter *and* row family
The catalog's header labels 14 columns, but the data doesn't sit in them. Flower
rows put sizes in `E` ("Concentrate Type") and leave `F` empty; Infused and
Trifecta rows use `E`/`F` as labelled. Every row keeps its price in `K` ("Other
Cannabinoids"), and `L`/`M` are empty throughout. Reading by header name yields
50 silently shifted products.

`gen_prerolls.py` therefore addresses cells by column letter *and* branches on
the row's type family, then re-asserts the entire layout on every run. If Jack
re-saves the sheet with its columns fixed, the assertion fails loudly and the
generator exits rather than emitting garbage. *Don't "simplify" it back to
header-name lookup.*

### The filter path is cannabinoid branch → type → concentrate type
Straight from the IA: THC / CBD / Blend first, then Flower / Infused / Trifecta,
then the concentrate type on Infused only. Same drill-in-place bubbles as
concentrates. This replaced three placeholder words (Traditional / Infused /
Blunt) that predated the sheet.

**Trifecta deliberately stops at the type level.** The IA calls its component
combination metadata, not navigation, so "Live Resin / Kief" rides in `sub3` and
shows only in the breadcrumb — no third-level bubble is ever offered for it.

### Size is a drawer facet, and the labels drop "each"
The IA keeps size as a filter "because products may not exist in all three
sizes", and names exactly three: 0.5 g, 0.75 g, 1 g. So sizes are stored bare —
the sheet's "0.5 g each" on the 20-packs is normalised away. Adding "each" for
multi-packs would have produced six distinct size strings and put six options in
the drawer, breaking the IA's three. Pack count already reads in the product
name ("Mimosa 20-Pack").

### No ratios on pre-rolls
The IA reserves ratios for standardized-dose formats (edibles, tinctures,
drinks) and says Blend should "display actual THC % and CBD %, no ratios". So
every pre-roll emits `thc` and `cbdv` and no `ratio` — the app's ratio count
stays at 45.

### The sheet's "Lifestyle" column is the app's *strain*, not its lifestyle
The IA's Lifestyle metadata is Indica / Indica Hybrid / Hybrid / Sativa Hybrid /
Sativa — that's the app's `st`, and it's kept verbatim, which adds the two
hybrid variants to the four `st` already used. It is **not** the app's `f`
(Discovery / Adventurous / Social / Unwind / Nightlife / Holistic), which drives
tile border colour and the monogram badge and which the sheet doesn't supply.

`f` is instead: **reused** from the flower catalog for the 12 strains that
already exist there, so a strain reads the same on every shelf; and
**authored** per real strain for the other 23, the way flower was done. Both
tables are marked in `gen_prerolls.py`.

(`S.strain` is never assigned a non-null value anywhere in the app, so the two
new `st` values change no filter behaviour today.)

### Blend counts as Holistic, at a 1% CBD threshold
The standing rule — any product carrying a meaningful non-psychoactive
cannabinoid is Holistic — applied literally. The families separate cleanly: THC
pre-rolls are uniformly 0.1% CBD, CBD ones 10.8–24.8%, Blend 8.9–15.2%. A 1%
threshold puts all 15 CBD and all 10 Blend products on Holistic (25 of 50) and
excludes the THC family's trace without a special case.

### The branch bubbles pick a photo no earlier branch used
A THC joint and a CBD joint photograph identically, so taking the first product
of each branch put the same shot in all three bubbles. Jack confirmed the
photos themselves are fine — you genuinely can't tell the types apart — so the
row instead prefers, per branch, a product whose photo no earlier branch has
already claimed. That lands on a single joint, a crossed pair and a parallel
pair. It's a display-time choice, not a reordering of `P`.

### One photo per type family × pack count
Jack supplied seven shots; six are used, keyed on (Flower/Infused/Trifecta ×
1-Pack/2-Pack/20-Pack). The **3-pack shot goes unused** — nothing in these 50 is
a 3-pack — but it stays wired so a 3-pack product would pick it up with no code
change, the same way the rice-crispy edible photo sits unused.

All seven carry real alpha, including the two `.webp` files, so they all take
the `embed_rgba` path.

---

## The phone frame

### The design width is 452 and never changes
Width used to be *derived* from a height capped at `86vh`, so on any window
under ~990px tall the frame shrank below 452 and content built for 452 ran off
the right edge. On a 900px window it rendered at 411px.

Now the app always lays out at 452 and the frame is **scaled** to fit. Framed
mode is capped at 440pt — an iPhone 16 Pro Max, the largest real screen — and
shrinks further to keep the whole phone visible without zooming the browser.

### Full screen fills the height on desktop, the width on a phone
Scaling to the viewport width is right on a phone and absurd on a 1440px
monitor (3.2×). The width only binds when the viewport is phone-shaped.

### Mobile type is accepted as smaller
A 14px name renders near 12px on a 393px iPhone. Jack accepted this rather than
bump the design type — phones are held a foot from your face. Revisit only after
looking at it on a real device.
