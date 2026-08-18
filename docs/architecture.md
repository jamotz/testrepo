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

Each banner carries its own run-out date under its copy (`DEAL_UNTIL`, one
string per deal; an empty string drops the line).

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
     sale, sort, cart[], screen}
```

`match(p)` ANDs every active facet; `results()` applies sorting.
`activeCount()` feeds the Filter pill badge. Clearing a level always clears the
deeper ones (`S.sub = null` also clears `sub2`/`sub3`).

---

## Screens

`nav(key)` toggles `.s[data-s=key]`, syncs the bottom tab via `TABMAP`, and
applies `.immersive` (hides nav) for the landing screen and the Guide Me wizard.

`landing · home · guide · method · subtype · taste · finish · shop · list ·
vape · product · cart · confirm · dealcal · edu · edutopic · account ·
acloyalty · acsettings · acorders · acrecs · acreviews · acabout`

`dealcal` maps to the `home` tab — both "See Deals Calendar" buttons live on
home, and the calendar is that page's deals seen forward in time.

The seven Account screens all map to the `account` tab via `TABMAP`, so the tab
stays lit while drilling into Loyalty Points or Settings. Their markup is static
(it mirrors the frames one-for-one); the row list, the points ledger, the order
cards, the recommendations, the reviews and the store block are rendered from
data by `renderAccount()` and `renderStores()`. Clicks are delegated from the
seven sections rather than the document, so the dynamic rows work without a
global handler. Everything is namespaced `ac*` — `.s` is a global
`display:none`.

### The deals calendar

`renderDealCal()` builds a date-led list from a **weekly pattern**, not a list
of dates. `DEALDEF` holds the three deals — each with the weekday it runs
(`dow`), the label and copy its banner carries, the size its prices quote, and
an `items()` that resolves its products out of `P`. The renderer walks the next
`DEALCAL_DAYS` (30) days from *today*, emits a section for each day that has at
least one deal, and orders same-day deals by `DEALCAL_ORDER`.

| Piece | What it is |
|---|---|
| `.dcdate` | the day — the section title. Today/Tomorrow prefix in orange |
| `.deal-banner` | the deal's title, the same component the home page uses (`dealBanner`), minus the "Until" line the date makes redundant |
| `.dctog` | the dropdown control: "See the N products", chevron flips on open |
| `.dcpanel` | the products, shown by a `dcopen` class on the wrapper |
| `.dcp` | one product row — photo, name, brand · size, price, lifestyle border. Tapping opens the product page |

Prices come from `priceFor` like everywhere else. The two flower deals are live
in pricing, so their rows show the struck regular price beside the deal price;
the 30%-off brand deal isn't modelled in `priceFor`, so its rows show today's
price and its panel says so in a note rather than inventing a second discount
path.

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

**Lifestyle is `st` renamed** — one axis, two vocabularies, kept one-to-one so a
settings toggle can swap them for advanced users:

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

**Styling:** every weight on a product tile is `#D2DBBC` with `--olive` text —
deliberately a few steps darker than the CBD bubble's `#ECF1E6`, which it was
otherwise indistinguishable from. Deal cards keep the solid fill, because they
show a row of sizes where one is selected.

---

## The size sheet

Tiles show one size and a **See more sizes** control instead of Add to Cart. The
sheet slides up over the whole card: size/price pill buttons (white outlined,
solid orange when selected), a chevron to drop it back, and Add to Cart at the
bottom that becomes the product page's quantity stepper.

Products with a single size (edibles, concentrates, topicals) keep Add to Cart —
there's nothing to open. Sheet classes live in the `fs*` namespace because `.s`
is a global `display:none` rule.
