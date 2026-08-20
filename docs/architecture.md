# Origins App — Architecture

Information architecture, data model and build pipeline.

---

## Build pipeline

```
                  ┌─ xlsxread.py  (the one reader — by column letter)
Jack's sheets ─→ ─┤
                  └─ terpmap.py   (terpenes → feelings + scents)
                         │
                         ├─→ gen_catalog_products.py ─┐
                         ├─→ gen_concentrates.py      │
                         ├─→ gen_edibles.py           ├─→ product rows,
                         ├─→ gen_prerolls.py          │   spliced by hand
                         ├─→ gen_topicals.py          │   into the P array
                         └─→ gen_drinks.py           ─┘

origins-app.src.html  ──┐
assets/**             ──┼─→  asm_app.py  →  origins-app.html  →  Artifact
fontcache/oswald-*.woff2┘                    (single file, ~3.2 MB)
```

Every generator prints rows to stdout and **all six share `xlsxread.read_cells`**,
which places cells by column letter. It used to be copy-pasted per generator,
which is how one bug survived in four copies at once.

`gen_catalog_products`, `gen_concentrates` and `gen_prerolls` also call
`terpmap.pairs()` — their sheets name three terpenes per product and the chips
are derived from those, not authored.

Two distinct hazards, both of which have bitten:

1. **Excel omits empty cells** from the file, so appending in document order
   shifts every column after a blank. Hence addressing by letter.
2. **Excel also writes empty cells self-closing** (`<c r="E2" s="29" t="str"/>`).
   A cell pattern that tries `<c…>.*?</c>` before `<c…/>` matches the
   self-closing tag as an *open* tag and swallows the next cell's value — the
   same one-column shift, but silent even when you address by letter. The
   self-closing branch must come first. This was live in all four generators
   until 2026-08-12; see `design-decisions.md`.

Each generator re-asserts its sheet's layout on every run (`check_columns`) and
exits non-zero rather than emit shifted data. `gen_prerolls` and `gen_drinks`
also reject a description ending in `...`, after a re-export once clipped all 50
of them to 80 characters.

`asm_app.py` replaces two markers in the source:

| Marker | Replaced with |
|---|---|
| `/*FONTS*/` | Oswald woff2 files as base64 `@font-face` rules |
| `/*IMGMAP*/` | `IMG` — a JSON map of image key → data URI |

**Image embedding functions:**

| Function | Use | Output |
|---|---|---|
| `embed()` | white-background photos | JPEG, flattened, max 340px |
| `embed_rgba()` | background-free photos | **WebP** q86, max 400px, alpha kept |
| `embed_cut()` | legacy auto background removal | PNG (now unused) |
| `embed_glyph()` | logos/glyphs | black-on-transparent PNG |
| `embed_svg()` | SVG assets | inline data URI |
| `embed_hero()` | landing hero | cropped JPEG |

`embed_rgba` emits WebP rather than PNG — same alpha, 8.75 MB → 2.3 MB build.

**Image resolution order** (`nobg_file`): the `NOBG` map (background-free) →
a file named exactly `<key>.png` → the `M` map (white-background original).
So dropping in `rosin.png` wires itself up with no code change.

**A key that isn't in the map renders an empty `<img>`, silently.** Origins U
sat like that for weeks: six of its eight card images named keys `asm_app.py`
had never carried. The `EDU` table now points at keys the build definitely
embeds, and the same check is worth making for anything new that reads `IMG[…]`
outside a product row.

---

## Product data model

Products live in the `P` array inside `origins-app.src.html`. Generators emit
these lines; the array is the single runtime source of truth.

```js
{t:"flower", n:"Animal Sherbert", b:"Gold Leaf", img:"fl_indica", pr:58,
 pz:{"1 g":12,"3.5 g":38,…}, szs:["1 g","3.5 g",…], thc:22.5, cbd:1,
 sub:"Indoor", sub2:…, sub3:…, etype:…, pot:…, combo:…, ratio:…,
 st:"Indica Hybrid", f:["unwind"], sale:0, r:4.0, rv:11,
 fe:["Relaxed","Grounded","Uplifted"], ta:["Earthy","Peppery","Citrus"], d:"…"}
```

| Field | Meaning |
|---|---|
| `t` | type: flower / preroll / concentrate / edible / drink / topical |
| `n` `b` | name, brand |
| `img` | key into `IMG` |
| `pr` | base price — **for flower this is the eighth (3.5 g) price** |
| `pz` | explicit per-size prices (catalog products); overrides `pr × sizeMult` |
| `szs` | this product's own size list; falls back to `SIZES[type]` |
| `sub` `sub2` `sub3` | filter levels (meaning varies by type — see below) |
| `etype` | edible form (Gummies / Chocolate / …) |
| `pot` `combo` `ratio` | potency line, cannabinoid combo, ratio (edibles + topicals) |
| `cbdv` `cbdu` | measured CBD and its unit (`" mg"`, or `%` when absent) |
| `othv` | the third cannabinoid's weight; its name comes from `combo` |
| `cbd` | legacy has-CBD **flag** the CBD filter reads — not a measurement |
| `mg` `tot` | a serving and its package total — edibles state `mg`, drinks both |
| `pk` | a pre-roll's pack count (the size is one joint); absent on 1-packs |
| `st` | strain: Sativa / Sativa Hybrid / Hybrid / Indica Hybrid / Indica / CBD |
| `f` | lifestyle — **`st` renamed**, one-to-one; drives border colour + badge |
| `fe` `ta` | feelings, smell/taste (product-info chips, and the icon keys) |
| `sale` | 1 = eligible for the home flower deals. **Four flowers carry it** — set by `DEALS` in `gen_catalog_products.py`, not by the sheet |

There is no `tp`. A single "terpene" string held one of 11 values that were
really scents, and only 6 of them were reachable in the filter; it was deleted
on 2026-08-12 along with the Terpenes drawer facet. Real terpene names live in
the sheets and reach the app only through `terpmap.py`.

### Filter levels per type

| Type | `sub` | `sub2` | `sub3` |
|---|---|---|---|
| Flower | Indoor / Outdoor | — | — |
| Concentrate | category (Live Resin, Rosin…) | consistency (Badder, Sauce…) | — |
| Edible | cannabinoid category | extraction *or* effect | strain (THC path only) |
| Pre-roll | cannabinoid branch (THC / CBD / Blend) | type (Flower / Infused / Trifecta) | concentrate type (Infused); component combination (Trifecta) |
| Topical | effect (Pain Relief, Recovery…) | form (Cream, Roll-On…) | — |
| Drink | cannabinoid branch (THC / CBD / Blend) | type (Drink / Shot / Seltzer / Sorbet / Honey) | — |

Drinks stop at two levels by their IA's own rule; see below.

---

## Pricing

`priceFor(product, size)` is the single source of truth used by every window
(home deals, shop cards, product info, cart, confirmation).

```
base = pz[size]  ??  pr × sizeMult(product, size)
```

`sizeMult` for flower is `[0.4, 1, 1.8, 3.2, 5.5]` for 1 g → 28 g, so **3.5 g = 1.0**
and `pr` *is* the eighth price. This alignment was a bug fix — the shop showed
$174 while the home deal showed $58 for the same product.

**Deals** (`priceFor` applies them; they are the only discounts in the app):

| Deal | Applies to | Rule |
|---|---|---|
| 2 for $50 | the 4 `sale:1` flowers, 3.5 g | $25/eighth, **only in pairs, mixed & matched across the whole bag** |
| 40% off | same 4 flowers, 14 g / 28 g | 60% of the regular price, no quantity requirement |

Each banner carries a run-out date under its copy, from `dealUntil(key)` — see
*The deals calendar*, which generates it.

Five further deals exist on the calendar only (concentrates, edibles,
pre-rolls). They are **not** in `priceFor`: they run on future dates, so
discounting the shop today would be wrong.

The four are two Passion Flower (Northern Lights, Pineapple Express) and two
Lifestyles (Gelato Cake, Jack Herer) — one per lifestyle colour except Social.

**Mix & match is a pool, not a per-line rule.** `dealAlloc(lines)` takes
`[{p, size, q}, …]` and returns how many units of each line the pairing covers:
every deal eighth in the bag joins one pool, `floor(pool / 2)` pairs get $25,
and the odd eighth left over stays regular. It is the **cheapest** one — the
units are sorted dearest-first before pairing, so the shopper keeps the largest
discount the pool can give. Two of one strain and one each of two strains price
identically, which is what the banner promises.

`cartLines()` runs that allocation once and hands every window the same answer
(`cartSub`, `cartDiscount`, the cart rows, confirmation, and the product page's
unit price). Each checkout is its own pool, so an order in Account › Order
History re-prices against its own lines, not against today's bag.

`linePrice(p, size, qty, dq)` returns `{total, regTotal}`, where `dq` is that
line's covered units; the cart shows the struck `regTotal` beside `total` and a
red **Discount −$X** row.

Tax is **inclusive**: listed price = what you pay; tax is 37% *of* the total,
not added on top.

---

## Filter architecture

### Concentrates — two layers
Source: `Concentrate Categories and filters.docx`.

```
Distillate · Live Resin · Rosin · Kief · Hash · RSO      (category bubbles)
   └─ tap → consistency bubbles, category parked far-left as a back bubble
```

`CONC` holds the categories and their forms; `FORMIMG` maps
`"Category|Form"` → image key so bubbles and products share one photo set.

### Edibles — up to three layers
Source: `Edible_Filter_Architecture_v2.xlsx`.

```
THC Edibles ──→ Distillate / Live Resin / Rosin / Live Rosin ──→ Sativa / Hybrid / Indica
CBD Edibles ──→ Pain Relief / Relax / Focus
THC Dominant ─→ Unwind / Sleep / Giggly
CBD Dominant ─→ Calm / Chill / Creative
Balanced ─────→ Balanced / Deep Sleep / Happy
```

`EDIB` holds the structure. Per the IA: **ratios are metadata, not filters** —
tiles display the cannabinoid combo and ratio, and effect filters decide which
products appear. The CBD-only *Pain Relief* product shows **total CBD mg**
instead of a ratio. Edible **form** isn't in the IA path, so it's a facet in the
Filter drawer (`S.eform`).

### Pre-rolls — up to three layers
Source: `WA_PreRolls_IA_Condensed.xlsx`.

```
THC ───→ Flower / Infused / Trifecta
CBD ───→ Flower / Infused          ──→ Infused only: Live Resin / Rosin /
Blend ─→ Flower / Infused                            Distillate / Hash / Kief
```

`PREROLL` holds the branches and their types; `PRCONC` the five concentrate
types. **Trifecta stops at the type level** — its component combination
("Live Resin / Kief") rides in `sub3` as metadata the breadcrumb shows, and no
Trifecta third-level bubble is ever rendered, per the IA's "concentrate
components are metadata, not navigation."

Size stays a Filter-drawer facet (`S.size`) rather than a bubble level, because
products don't exist in all three sizes. **No pre-roll carries a ratio**: the IA
reserves ratios for standardized-dose formats and asks for actual THC % and
CBD % on Blend instead.

### Drinks — two layers
Source: `WA_Drinks_IA_Condensed.xlsx`.

```
THC ──┐
CBD ──┼─→ Drink / Shot / Seltzer / Sorbet / Honey
Blend ┘
```

`DRINK` holds the three branches, `DRTYPES` the five product types. The IA is as
explicit about what is *not* a layer as about what is: size, dose and ratio are
all tile metadata, never navigation. So there is no third level to build.

Size is still a **drawer facet** (Jack, 2026-08-17, overruling the IA's "do not
filter by size" — the list is short and every volume is in the product's own
name anyway). `SIZES.drink` is derived from the catalog at load — the distinct
`szs` across drinks, sorted numerically: 2 / 4 / 6.7 / 12 / 16 oz. It used to
borrow the edible mg list, which matched no drink at all. Nothing prices off
that list: every drink carries an explicit `pz` for each of its sizes, so
`sizeMult` is never consulted.

One deviation from the other shelves, and it is the IA's: *"only show product
types that exist for the selected cannabinoid category"* — an empty type is
**dropped** here rather than dimmed. All 15 branch × type combinations are
stocked today, so the two behaviours are currently indistinguishable.

All four systems share the same bubble component (`.cc` + `.ring`), the
far-left filled back bubble, and dimming for zero-result options (drinks
excepted, above).

---

## Filter state

```js
S = {type, strain, sub, sub2, sub3, eform, mood, brands[], size, thc, terp,
     sale, deal, sort, cart[], screen}
```

`match(p)` ANDs every active facet; `results()` applies sorting.

**`deal` is the one facet that isn't a product property.** It holds a `DEALDEF`
key — set by the "See All" card at the end of each home deal row — and `match()`
tests membership of that deal's resolved product set, memoised in `DEALSETS`. In
deal mode `renderList` hides the shelf bubbles and heads the list with the deal's
own banner. It clears on every path that re-aims the list (shop circles, the
drawer's type buttons, Guide Me's finish, Clear).
`activeCount()` feeds the Filter pill badge. Clearing a level always clears the
deeper ones (`S.sub = null` also clears `sub2`/`sub3`).

---

## Screens

`nav(key)` toggles `.s[data-s=key]`, syncs the bottom tab via `TABMAP`, and
applies `.immersive` (hides nav) for the landing screen and the Guide Me wizard.

`landing · home · guide · method · subtype · taste · finish · shop · list ·
vape · product · cart · confirm · dealcal · edu · edutopic · account ·
acloyalty · acsettings · acadv · acorders · acrecs · acreviews · acabout`

### Origins U

`EDU` holds ten categories, `EDU_ORDER` lays them out (shelves first, then the
concept pages), and **`EDUMAP` is the single table routing a shop type to one of
them** — `openEduFor(type, idx)` is the only way in, from the shop list, the
recommendations screen and the vape dead-end alike.

| Route | Lands on | Why |
|---|---|---|
| flower · preroll | Flower | a pre-roll is flower, or infused flower |
| concentrate | Concentrate | |
| edible | Edibles | |
| drink | Liquid Edibles | own page since 2026-08-20; was Edibles |
| topical | Topicals | |
| vape | Vapes | own page since 2026-08-20; was Concentrate |
| tincture | Forms of CBD | that page covers tinctures; none in the catalog |

Adding a category means an `EDU` entry, an `EDU_ORDER` slot, and an `img` key
**checked against the built `IMG`** — a missing key renders an empty `<img>` in
silence, which is how six of the original eight sat broken for weeks.

Every screen except the landing page and the wizard wears the same brown title
bar, `.sbar` (2026-08-18). Shop and the product list had their own white
`.shophead` and the cart had no header at all; all three now use the shared
component, and the cart's reads **Your Cart**.

`dealcal` maps to the `home` tab — both "See Deals Calendar" buttons live on
home, and the calendar is that page's deals seen forward in time.

The eight Account screens all map to the `account` tab via `TABMAP`, so the tab
stays lit while drilling into Loyalty Points or Settings. Their markup is static
(it mirrors the frames one-for-one); the row list, the points ledger, the order
cards, the recommendations, the reviews and the store block are rendered from
data by `renderAccount()` and `renderStores()`. Clicks are delegated from the
seven sections rather than the document, so the dynamic rows work without a
global handler. Everything is namespaced `ac*` — `.s` is a global
`display:none`.

### The deals calendar

`renderDealCal()` builds a date-led list from a **four-week rota**, not a list
of dates. `DEALDEF` holds the seven deals — each with the shelf it runs on
(`t`), the week of the cycle and the weekday it runs (`week`, `dow`), the label
and copy its banner carries, the size its prices quote, and an `items()` that
resolves its products out of `P`. The renderer walks the next `DEALCAL_DAYS`
(30) days from *today*, emits a section for each day `dcRunsOn()` matches, and
orders same-day deals by `DEALCAL_ORDER`.

| Week · day | Deal | Shelf | `items()` |
|---|---|---|---|
| 0 · Tue | 30% Off | Edibles | one brand, `edbrand.brand` |
| 0 · Fri | 2 For $50 | Flower | the `sale:1` flowers |
| 1 · Thu | BOGO $40 | Concentrates | `dcRank("concentrate", 1, 4)` — cheapest 4 |
| 1 · Sun | 40% Off | Flower | the `sale:1` flowers |
| 2 · Tue | 25% Off | Pre-Rolls | `dcRank("preroll", -1, 5)` — dearest 5 |
| 2 · Fri | 2 For $50 | Flower | the `sale:1` flowers |
| 3 · Mon | 30% Off | Concentrates | `dcRank("concentrate", -1, 4)` — dearest 4 |
| 3 · Sat | 30% Off | Flower | four brand labels, prefix-matched |

Two deals a week, eight in a 30-day view. `dcWeek(date)` derives the cycle
position from the date (whole weeks since the epoch, turning over on a Sunday),
so it never drifts; `dcRunsOn(key, date)` is the single test everything else
builds on.

`dcOccurrences()` turns the rota into a flat list of runs — `{k, start, end,
live}` — scanning from **seven days back** (a run lasts 3–7 days, so one that
started before today can still be on) to `DEALCAL_DAYS` ahead, dropping anything
already finished. The page renders it in two parts: **Running now**, ordered by
which ends soonest and headed by the day each started, then **Upcoming**,
grouped by start day. `dealUntil()` reads the same list, so the home banners and
the calendar always name the same end date for a deal.

**End dates are generated.** `dealEnd(key, date)` puts a run's end 3–7 days
after its start, from a hash of the key and the date — stable across renders,
unlike `Math.random()`. `dealUntil(key)` is what the **home** banners print: the
end of that deal's current run, so the two screens agree. `DEAL_UNTIL[key]` pins
a date when a fixed one is wanted.

| Piece | What it is |
|---|---|
| `.dcdate` | the day — the section title. Today/Tomorrow prefix in orange |
| `.deal-banner` | the deal's title, the same component the home page uses (`dealBanner`), minus the "Until" line the date makes redundant |
| `.dctog` | the dropdown control: the shelf's name, "See the N products", chevron flips on open |
| `.dcpanel` | the products, shown by a `dcopen` class on the wrapper |
| `.dcp` | one product row — photo, name, brand · size, price, lifestyle border. Tapping opens the product page |

On the **home page**, each deal row ends with a `.dseeall` card that opens the
same deal in the shop list (`S.deal`). Brand tiles and See All cards take their
height from a rendered product tile via `sizeDealRows()`, so all three cards in
a row are the same size.

Prices come from `priceFor` like everywhere else, and the size slot from the
tiles' own `servTotal` (so a 20-pack reads `0.5G EACH`, an edible `10MG /
100MG`). The two flower deals are live in pricing, so their rows show the struck
regular price beside the deal price. **The other five aren't modelled in
`priceFor` on purpose** — they run on future dates, and making them live would
discount the shop today — so their rows show today's price and each panel
carries a note saying the discount comes off on the day.

### Account data is derived, not restated

Nothing on these screens is written down twice. Each of these exists so that
editing one number can't leave a stale label or total somewhere else:

| Helper | Derives |
|---|---|
| `ACPTS` | the headline balance, summed from `ACLEDGER` |
| `acStatus(row)` | Purchase / Review from a positive amount; negatives keep their stored reason |
| `acLineWeight(p,size,qty)` | an order line's total weight — size × `pk` × quantity |
| `acFind(name,type)` | resolves order and review rows against `P`, so a renamed product drops the line rather than leaving a phantom |
| `acCopyAddr()` | the copyable address, from the rendered `addr` with `<br>`s flattened |

`STORES` holds both shop locations once. The landing store cards *and* the
About Us tiles render their address and hours from it, so the two screens can't
disagree; adding a third shop is one row.

---

## Lifestyles

Six, each with a colour and a logo: **Discovery** `#A0463C` · **Adventurous**
`#C09A64` · **Social** `#F3D390` · **Unwind** `#78A6C5` · **Nightlife** `#5D8A85`
· **Holistic** `#7E9A5B`.

**Lifestyle is `st` renamed** — one axis, two vocabularies, kept one-to-one so
the *Use product type* switch in Advanced Settings can swap them (built
2026-08-18; see **Advanced Settings** below):

```
Sativa → Discovery   Sativa Hybrid → Adventurous   Hybrid → Social
Indica → Nightlife   Indica Hybrid → Unwind        CBD    → Holistic
```

Every catalog states the strain, so no generator derives `f`; it is read and
renamed. Topicals are the exception and are uniformly Holistic — nothing on that
shelf is psychoactive, so the use case (`sub`) stands in for the strain axis.

Holistic was added later for CBD-forward products; its logo is generated by
`gen_holistic_logo.py` (an "H" built to match Jack's letterforms, with the
"HOLISTIC" wordmark recomposed from letters lifted out of his other logos).

Lifestyle drives the product-card border colour and the monogram badge.

---

## Advanced Settings

`acadv`, reached from the lower button group on Account Settings. `ADV` holds
the switch states, `setAdv(key, on)` applies them, and the switches are `.sw` —
the same component the filter drawer uses.

| Switch | Key | Effect |
|---|---|---|
| Use product type | `strain` | `lifeLabel()` returns `STRAINNAME[k]` instead of `FEEL[k]` |
| Enlarged view | `enlarged` | `#scr.enlarged` puts `zoom: var(--enlarge)` (1.25) on `.view` **and** `.tabs` |
| Reduce motion | `nomotion` | `#scr.nomotion` kills every transition and animation |

**`lifeLabel(key)` is the only place a lifestyle word is printed.** Reach for
`FEEL[k]` directly on a new screen and the toggle won't follow you there — the
six call sites all go through it. `P` is never touched: the six lifestyles are
the six strains renamed one-to-one, so the swap is a lookup.

Labels are baked in at render time, so `setAdv()` re-renders whatever is on
screen — the mood chips, the home page, the shop, and the list, product or cart
screen if that is where you are.

**One place needed more than a lookup:** the Guide Me wizard shows each
lifestyle as a *wordmark image*, which can't be re-lettered. Each option carries
a text twin that `#scr.strainnames` swaps in.

**Enlarged view is one number.** `--enlarge` (1.25) scales `.view` and `.tabs`
together, so type, photos, buttons, borders and spacing all grow by the same
factor and the children get a narrower coordinate space — 452 / 1.25 = **362 px
effective** — so the app *reflows* like a smaller phone rather than magnifying.
The fake status bar and island are excluded: they are the handset, not the app.

Measured ceiling: clean to **1.30**; at 1.35 the 218 px product cards can no
longer sit two-up and shop/list overflow. WCAG 1.4.10 Reflow's 320 px floor is
reached at 1.41. One rule needs an exception — `.deal-banner .bs` is
`white-space:nowrap`, the only thing in the app that cannot reflow narrower, so
enlarged lets it wrap.

`tiles-compact` stays on `#view` in both modes. It was reserved for this work,
but removing it in enlarged mode would scale tiles 11% more than everything
else — the opposite of scaling as a unit.

---

## Feelings & smell/taste

Two closed vocabularies, defined by Jack's sheets and rendered with his icons:

| | Sheet | Terms | Icon colour |
|---|---|---:|---|
| Feelings | `cannabis_feelings.xlsx` | 14 | `--or` `#F1601C` |
| Smell & Taste | `cannabis_smell_taste.xlsx` | 16 | `--olive` `#555624` |

Products don't state either. They state **three terpenes**, and
`cannabis_terpene_mapping.xlsx` maps each of the 10 terpenes to three
(Feeling, Smell & Taste) pairs ranked Primary / Secondary / Tertiary.

**`terpmap.pairs()` takes each terpene's Primary pair, in Terp 1/2/3 order.**
That is checkable, not a guess: it yields three distinct feelings and three
distinct scents on all 160 smokeable products, where the obvious alternative
(Terp 1 → Primary, Terp 2 → Secondary, Terp 3 → Tertiary) repeats a feeling
inside the same tile on 56% of them. Secondary and Tertiary are the fallback for
a product naming fewer than three terpenes.

`terpmap.check()` runs on every generation and refuses to emit if a terpene is
missing from the mapping, if a product collapses to fewer than three terms, or
if any term falls outside the 30.

### Icons
The 30 icons live in `assets/scents assets/icons/`, sliced from Jack's contact
sheet and recoloured to the two palette tokens. They are registered as image
keys under their **own bare lowercase term**, so `pIcon("Relaxed")` resolves to
`IMG["relaxed"]` with no lookup table.

They embed via **`embed_rgba` at 128px**, dispatched on the asset folder.
`embed_glyph` would repaint them black and throw the palette away; the default
path would flatten the alpha onto white and box each one.

**Coverage:** flower, concentrates and pre-rolls are fully on this vocabulary.
Edibles, topicals and drinks still carry the old placeholder terms and fall
through to `pIcon`'s generated SVGs — 1288 chips resolve to a supplied icon,
284 fall back, and the 284 are exactly those three shelves.

---

## Palette & type

Orange `#F1601C` · brown `#2E261E` · olive `#555624` · cream `#E6C7A7` ·
white background. Headings **Oswald** (self-hosted woff2), body **Georgia**.

---

## Cannabinoid display

`cannList(p)` returns `[[name, value], …]` — the single source for both the tile
bubbles and the product-page row.

```
combo present and not "X Only"  →  split it; values come from pot / cbdv / othv
otherwise                       →  THC (pot, thc%, or mg) then CBD (cbdv)
```

A cannabinoid with no number is **left out rather than guessed at**. Colours:
THC `#C0392B`, CBD `#5C7540` (the Holistic green), CBN `#6F53A3`, CBG `#B4651A`
— deliberately not the brand orange, so a bubble never reads as a button. Fills
are opaque, not tinted alpha, because a photo behind them bleeds through.

`tileOverlay(p)` places the ratio pill top-left and the bubbles top-right, both
flush to the card's inner edge and top-aligned. The product page puts the ratio
on the breadcrumb line and the bubbles in a horizontal row on the brand line, at
11.5 px instead of 10.

---

## The phone frame

The app always lays out in **452 CSS px of width** — the design unit. Height and
render scale vary; width never derives from a capped height, which is what used
to clip content on short windows.

| Mode | Scale | Height |
|---|---|---|
| Framed | `min(440/452, (vw−32)/474)` — never larger than an iPhone 16 Pro Max, and shrunk to fit the window | 852 |
| Full screen | width binds only when the viewport is phone-shaped (≤1×); anything wider fills the height, clamped 1×–1.5×, centred | `vh / scale` |

`fitFrame()` measures the page chrome from the phone's own offset rather than
assuming a header height. Full screen is entered by tapping **Open full screen**
— never automatically, so it can't hijack a tile tap — and exited by the `✕ Exit`
chip or Escape.

Three boxes, and each needs its width stated for a different reason: `#phonebox`
is pinned to the **scaled** footprint (a transform doesn't shrink the page box),
`.phone` to the **unscaled** `DESIGN_W + bez`, and `.scr` to the design width.
Leave `.phone`'s off and it inherits `#phonebox`'s scaled width, drawing the
bezel narrower than the 452px screen inside it — see `design-decisions.md`.

The script injects a `viewport` meta if the host page has none, and appends
`viewport-fit=cover` if it has one without it. Without that, `env(safe-area-inset-*)`
reports 0 and the full-screen tab bar sits under the home indicator.

---

## The tile's size slot

`servTotal(p, size)` returns the slot's text, or `null` to fall back to the
plain size pill. `size` means something different on each shelf, so each has its
own branch:

| Type | `size` means | slot reads |
|---|---|---|
| Pre-roll | one joint (`0.5 g`) | `0.5G EACH` on multi-packs; `null` on 1-packs |
| Edible | the whole package (`100 mg`) | `10mg / 100mg` — serving `p.mg`, total the size |
| Drink | a **volume** (`12 oz`) | `10mg / 100mg` — serving `p.mg`, total `p.tot` |

Flower, concentrates and topicals never enter the function.

Two traps here, both of which have already been hit:

- **A drink's size is a volume, not a dose.** It used to share the edible branch,
  which derived the total from the size — comparing milligrams to ounces and
  rendering `10 mg / 12 oz`. Drinks carry `tot` explicitly. Nothing is lost from
  the tile: every drink names its volume in the product name.
- **`feedPill()` strips the word "each"**, left over from when sizes arrived
  carrying it. Append "each" *outside* that call or it silently vanishes.

`sizePill()` renders every form as the same `.fsz` element so the size sheet's
live update keeps its selector.

**Styling (2026-08-18):** one weight pill across tiles, deal cards and the
product page — **outlined olive** for a size you could pick, **solid olive with
cream text** for the size you are on, and the tinted `#EDEFE1` chip for
serving/total, which is a fact about the product rather than a choice. This
replaced the tinted `#D2DBBC` tile pill and the brown deal-card override that
existed only to undo it.

---

## The size sheet

Tiles show one size and a **See more sizes** control instead of Add to Cart. The
sheet slides up over the whole card: size/price pill buttons (white outlined,
solid orange when selected), a chevron to drop it back, and Add to Cart at the
bottom that becomes the product page's quantity stepper.

Products with a single size (edibles, concentrates, topicals) keep Add to Cart —
there's nothing to open. Sheet classes live in the `fs*` namespace because `.s`
is a global `display:none` rule.

---

## The accessibility display system

`displayMode` is `ADV.enlarged`, and everything it changes flows from **semantic
tokens in `:root`**, overridden once in `#scr.enlarged`. No component names a
mode; a new screen inherits Enlarged view by using the tokens.

| Token | Standard | Enlarged | |
|---|---:|---:|---|
| `--text-micro` | 9.5px | 13px | brand line, tab labels |
| `--text-secondary` | 11.5px | 15px | chips, breadcrumbs |
| `--text-body` | 13px | 16.5px | description, body |
| `--text-product-title` | 14px | 18px | product name |
| `--text-heading` | 1.4rem | 1.66rem | `.sbar` titles |
| `--text-button` | 1rem | 1.15rem | Filter, Sort, Continue |
| `--text-nav` / `--text-pill` | 9px / 11px | 12px / 14px | tab label, weight pill |
| `--icon-size` / `--icon-size-sm` | 21px / 15px | 27px / 19px | |
| `--control-height` | 47px | 54px | Filter / Sort pill |
| `--target-size` | 44px | 52px | minimum hit area |
| `--card-padding` / `--grid-gap` / `--section-gap` | 12 / 13 / 10px | 16 / 16 / 14px | |

**Type is compressed upward, not scaled uniformly** — the 9.5px floor gains 37%
while a heading gains 19%, because the small labels are what fail at arm's
length. Targets grow faster than the text inside them, and decoration doesn't
grow at all.

This replaced a `zoom:1.25` on the whole frame. Uniform zoom magnified
decoration with content, grew every gap equally whether it needed it, and shrank
the layout's coordinate space exactly when the content got bigger.

Reflow lives beside the tokens: `.pgrid` drops to one column, every card row
gives its card the full width, product names wrap instead of truncating, card
metadata stacks, and the deal banner's `nowrap` is released.

**Standard is provably untouched.** A computed-style snapshot of ~400 elements
across 11 screens is identical before and after the token refactor — 0 diffs.
Re-run it (`snapshot.js`) before landing any change to this system.

**Persistence** is `localStorage["origins.display.v1"]`, every access wrapped —
a private window or a blocked accessor can throw on *read*, and the app must
still boot. **OS Reduce Motion** is honoured through `motionOff()`: the in-app
switch can turn motion off, never back on against the system preference.
