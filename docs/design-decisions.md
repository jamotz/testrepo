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

Jack's sheets supply brand, name, category, prices, copy **and the strain** —
which, since 2026-08-12, also supplies the lifestyle. What the sheets don't
carry is feelings, taste and terpene; those are **authored per real strain**
(Jack Herer piney, GMO Cookies garlicky/heavy) rather than randomized.

*Lifestyle was on this list until 2026-08-12 and should never have been.* Every
catalog stated the strain outright and four generators derived it anyway, each
with a different invented rule. Before writing a table that assigns something
per strain, check the source for a column that already says it.

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

## Lifestyle is the strain, renamed

**Jack, 2026-08-12:** *"Sativa, Sativa hybrid, hybrid, Indica Hybrid, Indica =
Discovery, Adventurous, Social, Unwind, Nightlife in that order. CBD = Holistic.
We will later create a toggle in the settings that switches them back and forth
for advanced users."*

So lifestyle and strain are **one axis with two vocabularies**, not two
independent facts:

| Strain | Lifestyle |
|---|---|
| Sativa | Discovery |
| Sativa Hybrid | Adventurous |
| Hybrid | Social |
| Indica Hybrid | Unwind |
| Indica | Nightlife |
| CBD | Holistic |

They must stay one-to-one or the planned toggle can't work. 218 of 234 products
satisfy it exactly; the exceptions are listed below and each is the sheet's own
doing, not a judgment call here.

### Every catalog states this — read it, don't derive it
Each source already carries the strain, so no generator authors a lifestyle any
more:

| Type | Column | Notes |
|---|---|---|
| Flower | `Type:` in the .docx | all six values, plus a "CBD Flower Options" section |
| Pre-roll | `H` Lifestyle + `D` branch | branch (THC/CBD/Blend) is the cannabinoid decision |
| Concentrate | `F` Type | all six values |
| Edible | `F` Lifestyle | only on `THC Edibles` rows; the rest are Holistic by category |
| Topical | — | all Holistic, see below |

**The rules this replaced were all invented, and each one fought its sheet:**

- *"Any product carrying a non-psychoactive cannabinoid is Holistic."* Applied
  literally at a **1% CBD threshold** on pre-rolls, it swept the whole Blend
  family into Holistic — even though the sheet files those rows under `Blend`,
  not `CBD`. The sheet had already made that call.
- *Concentrates* collapsed `Indica Hybrid → Indica` and `Sativa Hybrid → Sativa`
  in an `ST` table, throwing away two of the six values the app now needs.
- *Edibles* fell back to `st:"Hybrid"` for any row where the sheet left Lifestyle
  blank, inventing a strain the sheet never stated. Those rows read `CBD` now.
- *Flower* authored Indica/Sativa per strain in `PROFILE` while the .docx stated
  the type outright — and the doc's `Indica Hybrid` / `Sativa Hybrid` had been
  flattened to `Indica` / `Sativa`.

### The 16 rows that don't satisfy the bijection
- **15 CBD-branch pre-rolls.** The sheet's own two columns disagree: column D
  says `CBD - Flower`, column H says `Sativa Hybrid`. Per *CBD = Holistic* the
  branch decides the lifestyle, and column H is left as written rather than
  overwritten with `CBD`. Harlequin therefore reads Holistic with a Sativa
  Hybrid strain. **If the settings toggle needs a strict bijection, this is the
  set to revisit.**
- **1 legacy drink**, which has no catalog behind it at all (see next steps).

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

### Every topical is Holistic
**Jack, 2026-08-12:** you can't get high off a topical unless it's a mainly-THC
transdermal, and the catalog has none. So the strain axis doesn't apply to this
shelf at all — the use case (Pain Relief, Recovery, Massage, Intimacy, …) stands
in for it, and that's already `sub`. All 38 read `st:"CBD"`, `f:["holistic"]`.

This overrules the previous split, which routed Massage to Unwind and Intimacy
to Nightlife on the reasoning that they read closer to those moods. That was a
judgment about mood; the deciding fact is that none of these products are
psychoactive.

---

## Pre-rolls

### The sheet was never broken — the reader was
**Superseded 2026-08-12.** This section used to say the catalog's columns didn't
match its own header: that Flower rows kept sizes in `E` ("Concentrate Type")
and that every row kept its price in `K` ("Other Cannabinoids") with `L`/`M`
empty. None of that is true of the sheet. Every column sits exactly where its
header says — `E` Concentrate Type (empty on Flower rows), `F` Available Sizes,
`M` WA Retail Price.

The shift was produced by the readers themselves. `read_cells()` matched cells
with `<c[^>]*>.*?</c>|<c[^>]*/>` — open-tag branch first — so a self-closing
empty cell (`<c r="E2" s="29" t="str"/>`) matched the *open* branch and its
`.*?</c>` ran on to the following cell's closing tag, swallowing that cell's
value. Every empty cell shifted its row one column left. That is exactly what
made sizes look like they sat in `E` and the price in `K`.

`gen_prerolls.py` had been written to compensate, reading sizes from `E` for
Flower rows and the price from `K`. The two errors cancelled, so the 50 emitted
products were correct all along and nothing looked wrong. What it cost was a
`check_columns()` that asserted the corrupted layout and would have rejected the
sheet if the reader were ever fixed — the guard was holding the bug in place.

Both halves are now fixed: the alternation tries the self-closing branch first
in all four generators, and `gen_prerolls.py` reads `F` and `M` as labelled.
Verified by regenerating all four before and after — **output is byte-identical**,
which is what proves the product data was never affected.

*Two things to keep:* read cells by column letter (not document order), and keep
`check_columns()` asserting the real layout — a reader that mishandles empty
cells shifts whole rows and still looks plausible.

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

### The sheet's "Lifestyle" column is *both* — it's the strain and the lifestyle
**Corrected 2026-08-12.** This section used to say the IA's Lifestyle metadata
(Indica / Indica Hybrid / Hybrid / Sativa Hybrid / Sativa) was the app's `st`
and emphatically **not** its `f`, on the grounds that the sheet doesn't supply
lifestyle. That reading was wrong: the two are the same axis under different
names, so the column supplies both. See *Lifestyle is the strain, renamed*.

`f` used to be **reused** from the flower catalog for the 12 strains that exist
there and **authored** per real strain for the other 23. Both tables are now
dead for lifestyle — they still carry the terpene, which the sheet genuinely
doesn't state — and `gen_prerolls.py` reads `LIFESTYLE[st]` instead.

(`S.strain` is never assigned a non-null value anywhere in the app, so the two
extra `st` values still change no filter behaviour today. They will matter to
the settings toggle.)

### Blend is not Holistic — the sheet already said so
**Superseded 2026-08-12.** This used to force Holistic at a 1% CBD threshold,
which put all 15 CBD *and* all 10 Blend products on Holistic. The threshold was
invented and it contradicted the sheet: column D files those rows under `Blend`,
a branch the IA defines separately from `CBD`, and Jack's rule names only CBD as
Holistic.

Blend rows now take their strain's lifestyle like any other row. Holistic on
this shelf is exactly the 15 rows whose branch says `CBD` — no threshold, no
inference. (The families do separate cleanly by percentage — THC 0.1%, Blend
8.9–15.2%, CBD 10.8–24.8% — which is why the threshold looked right. It was
still deriving a fact the sheet stated outright.)

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

## Account

### The Loyalty header runs on the Account header's type scale
The two page-tops are built from the same two lines so they read as one family:

| | Account | Loyalty |
|---|---|---|
| line 1, 1.72rem | Noelle Smith | Current Balance: **3400** |
| line 2, 0.82rem | the email | How to Earn & Use Points |
| right, 42px ring / 22px icon | gear | notification bell |

The points sit **on** the balance line rather than under it — the frame drew a
separate "Total:" row, but the number is the balance, so it inherits that
line's size instead of restating it one line down. The gear and bell share one
treatment; the bell used to carry its ring inside its own SVG at 36px.

### The ledger's table is a fixed 30/40/30
`Date` is left-aligned and `Total` right-aligned onto their own data, and the
columns are fixed so `Status` is centred **on the table** rather than on
whatever width its content happened to claim. Before, the headers were centred
over columns whose values sat hard left and hard right, so nothing lined up.

### Points-in are named from the amount
Points coming *out* carry their own stored reason because you can't infer it.
Points going *in* are derived: a 50 is the credit for leaving a **Review**,
anything larger came from a **Purchase**. So the label can't go stale when an
amount is edited — the same reason `ACPTS` sums the ledger rather than being
written twice.

**There is no "Expired".** Jack cut it: losing points reads badly on a loyalty
screen. It became a second Redeemed, placed on 1/11 alongside that day's
purchase, since points get spent at the till. The 1/20 purchase is 1500 rather
than the frame's 1466 so the ledger still lands on 3400 with the expiry gone.

Every redemption now sits under a purchase on the same day. The purchase
amounts absorb the difference so the ledger still lands on 3400 — that's why
1/20 reads 450 rather than the frame's 1466.

### Both stores live in one `STORES` table
The landing frame gave Redmond and Seattle **identical** hours, which would have
made the About Us store switch look broken. Seattle's hours are authored, and
both locations now live in a single `STORES` const that the landing cards *and*
the About Us tiles render from — so the two screens can't drift apart. Adding a
third shop is one row.

On About Us the two locations are orange pills (solid when selected, outlined
when not, matching `.st-btn`), and picking one swaps the address, phone and
hours beneath them. The three section headings (Our shops / Address / Hours)
and the address block are centred; the hours keep their day-left, time-right
split.

**Copy address** derives its string from the same `addr` field the page renders
— the `<br>`s become spaces — so there is no second copy of the address to keep
in sync, and it always copies whichever shop is selected. `navigator.clipboard`
needs a `clipboard-write` permission the artifact's iframe may not carry, so it
falls back to an offscreen textarea plus `execCommand`, and the toast reports
which happened.

### Order lines state total weight, tiles state serving/total
An order line shows the size multiplied by the pack count **and** the quantity
ordered: a 2-pack of 0.5 g joints reads `1G`, and two of a single 0.5 g joint
reads `1G` too. The price beside it is already a line total, so a per-unit
weight next to a total price was a mismatched pair.

Product tiles keep `servTotal`'s `0.5G / 1G` instead, because there the question
is what one package contains — not what someone walked out with.

### The circle holds a gear, and it opens Account Settings
The ring beside Noelle's name in `ACCOUNT.png` reads as an empty circle because
the icon didn't survive the frame export — Jack confirmed it's a **gear**. It
opens Account Settings, which is also what **Manage Notifications** does (that
button was the only route the frames drew before the gear was identified).

### The four unframed rows are authored first drafts
Order History, Recommended Products, Past Reviews and About Us are rows in
`ACCOUNT.png` with no screen behind them. Jack asked for pages built "based on
the other frames … we can edit it as we go", so each is a draft in the app's
existing visual language rather than a guess at a frame:

- **Order History** — order cards (number, date, status pill, lines, total).
  Prices run through `priceFor`/`linePrice`, so the totals track the real
  catalog instead of being typed in.
- **Recommended Products** — the shop's own `.pgrid` and `feedCard`, showing
  top-rated products in the lifestyles her order history implies, minus what
  she already bought. Cards behave exactly as they do in the shop.
- **Past Reviews** — product, brand, stars via the existing `stars()`, date and
  body copy.
- **About Us** — brand copy plus the Redmond address and hours already used on
  the order-confirmation screen.

Noelle's orders and reviews are **authored mock history**, marked `AUTHORED` in
the source. Every line references a real catalog product through `acFind()`, so
renaming a product drops the line rather than leaving a phantom.

### The points ledger is derived, not typed
`AC - LOYALTY POINTS.png` drew a 3400 balance over ten entries totalling
**−3184**. Jack's call: make both 3400. His dates and his Added/Redeemed/
Expired pattern are kept; the three redemptions and the expiry were re-cut so
the ledger lands exactly on 3400 *and* the running balance never dips below
zero (oldest-first it runs 50 → 1300 → 800 → 550 → 2550 → 4016 → 4066 →
5066 → 3866 → 3400).

`ACPTS` is now **summed from `ACLEDGER`** rather than written twice, so the
headline balance, the Account row and the table can't drift apart again. Edit
the entries and the balance follows.

### Section headings are sentence case here
The global `h1–h4` rule uppercases every heading. Jack's settings frame draws
"Account Info" and "Manage Notifications" in sentence case, so `.ach3` opts out
with `text-transform:none`. The three screen titles in the brown bar *are*
uppercase, matching the frames and the Origins U bars.

### Pills, not the frames' square corners
The Account frames draw square buttons, but every other button in the app is a
100px pill. Jack's call: the app's shape wins. Colour assignments stay as drawn
— orange fill for the primary action, olive outline for secondaries, orange
outline for Delete Account — with one change: the frames' pure-black policy
buttons use `--brown`, the palette's near-black, so they stay visually lesser
than the olive actions without introducing a colour the app never uses.

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

---

## Drinks

### The photo is the vessel; the colour is the flavour
Jack supplied 11 shots: three bottle colours, four shot colours, two can sizes,
one sorbet, one honey. One flat photo per Type would have made all 20 bottled
drinks identical on the shelf, so the **Type picks the vessel and the flavour
picks its colour** (`COLOR_RULES` in `gen_drinks.py`).

The rules are an ordered list, first match wins, so the specific idea has to
precede the generic one: `grapefruit` before `grape`, `blue raspberry` before
`raspberry`, `peach` before `apple` (Apple Peach reads as a peach). All 11
photos end up used, 9/8/3 across the red/orange/yellow bottles.

**Seltzers are the exception** — the two cans differ by *size*, not colour, so
size picks them. **Bottles have no blue**, so a Blueberry Lemonade bottle falls
back to red and reads with the other berries rather than borrowing a shot glass.

### A drink's size is a volume, so the tile states the dose instead
`servTotal` derived an edible's total from its size (`100 mg` is the package).
A drink's size is `12 oz` — a volume — so the same code compared milligrams to
ounces and would have rendered `10 mg / 12 oz`. Drinks now carry `tot` (the
package milligrams) explicitly and the tile reads `10mg / 100mg`.

Nothing is lost: every drink names its volume in the product name ("Blackberry
Lemonade 12 oz"), so the slot is free to carry the dose.

### THC is milligrams here, and `cannList` assumes percent
`cannList()` renders `p.thc` as `"%"` unless a potency string is present, so a
100 mg drink read **"THC 100%"**. Drinks emit `pot:"100 mg THC"` the way edibles
do. *If you add another mg-dosed type, emit `pot` or it will claim to be 100%
THC.*

### Two rows are still on the sheet's old layout
The catalog gained a `Serving Size` column at H, which pushed everything after
it one to the right. The last two rows (Peach Lemonade 12 oz, Blueberry Lemonade
12 oz) were appended before that and never moved, so for them H is THC mg, K is
the price and L is the source note. `LEGACY_MAP` in `gen_drinks.py` reads them
correctly and the generator names them on stderr on every run.

Every value is recoverable **except the serving size, which those rows simply
don't have** — so those two products state no dose rather than being given an
invented one. Add the serving size to the sheet and the fallback stops firing.

### Which drinks file to use
There are two 50-row drinks catalogs. Use
`..._Source_Inspired_Unique_Descriptions.xlsx`. The other one,
`..._Final_CBG_Fix.xlsx`, is **identical except for the Description and Source
columns** — the CBG data it is named for is the same in both — and 17 of its 50
descriptions are truncated mid-word.

### Not yet done: the bubble path
`sub` carries THC/CBD/Blend and `sub2` the Type, matching the IA, but
`renderList` has no drinks branch so the shelf renders as a flat grid. The
first level is the same THC/CBD/Blend the pre-rolls use, so it can share that
bubble component.

---

## The old terpene vocabulary is gone

**Removed 2026-08-12**, ahead of Jack's feelings/scents mapping.

Products carried a single `tp` field holding one of 11 values — Citrus, Creamy,
Diesel, Earthy, Flowery, Fruity, Herbal, Lavender, Nutty, Pepper, Piney. These
were never terpenes; they were *scents* under a terpene label. The real terpene
names (Myrcene, Limonene, Caryophyllene, …) live in `cannabis_terpenes.xlsx` and
were never in the app.

The vocabulary was also broken in a way nobody had noticed: the Filter drawer's
Terpenes section offered only **6** of the 11 values, so `Herbal`, `Flowery`,
`Creamy`, `Nutty` and `Diesel` were unreachable — 73 products could not be found
by the one facet that described them.

What came out:

| Where | What |
|---|---|
| `origins-app.src.html` | the `TERPS` const, the drawer's Terpenes section and its handler, `S.terp`, the `match()` clause, the `activeCount()` entry, the clear-all reset, and `tp:"…"` from all 282 rows |
| all six generators | the `tp` field in each row template, its argument, and four now-dead flavour→terpene lookup tables |
| `asm_app.py` | a stale `scent_skunky` mapping pointing at a file that never existed — the build's only WARN |

`gen_prerolls.py` and `gen_catalog_products.py` keep their tables: those tuples
carry feelings, taste and copy alongside the terpene, so only the unpacking
changed. The dead slot is named `_terp_dead` in the flower generator so it can't
be mistaken for live data.

Verified by regenerating all five sheet-driven types and diffing against the app
— every one matches byte for byte, so nothing but `tp` moved.

**The replacement is not a like-for-like.** Feelings and scents are separate
16/14-term vocabularies with their own icons, arranged in three tiers, and the
terpene name is backing data rather than something the shopper filters on.
Don't reintroduce a single `tp` string.
