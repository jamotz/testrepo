# Origins App — Architecture

Information architecture, data model and build pipeline.

---

## Build pipeline

```
Jack's sheets ─→ gen_catalog_products.py ─┐
                 gen_concentrates.py      ├─→ product rows, spliced by hand
                 gen_edibles.py           │   into the P array
                 gen_topicals.py         ─┘

origins-app.src.html  ──┐
assets/**             ──┼─→  asm_app.py  →  origins-app.html  →  Artifact
fontcache/oswald-*.woff2┘                    (single file, ~2.5 MB)
```

Every generator prints rows to stdout. They all share one xlsx reader that
places cells **by column letter** — Excel omits empty cells from the file, so
appending in document order shifts every column after a blank.

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
 st:"Indica", tp:"Diesel", f:["unwind"], sale:0, r:4.0, rv:11,
 fe:["Giddy","Relaxed","Hungry"], ta:["Aromatic","Skunky"], d:"…"}
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
| `st` | strain: Indica / Sativa / Hybrid / CBD |
| `f` | lifestyles — drives card border colour + monogram badge |
| `fe` `ta` | feelings, taste (product-info chips) |
| `sale` | 1 = eligible for the home flower deals |

### Filter levels per type

| Type | `sub` | `sub2` | `sub3` |
|---|---|---|---|
| Flower | Indoor / Outdoor | — | — |
| Concentrate | category (Live Resin, Rosin…) | consistency (Badder, Sauce…) | — |
| Edible | cannabinoid category | extraction *or* effect | strain (THC path only) |
| Topical | effect (Pain Relief, Recovery…) | form (Cream, Roll-On…) | — |

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
| 2 for $50 | the 4 `sale:1` flowers, 3.5 g | $25/eighth, **only in pairs** — `linePrice()` gives even units the deal price, odd stays regular |
| 40% off | same 4 flowers, 14 g / 28 g | 60% of the regular price, no quantity requirement |

`linePrice(p, size, qty)` returns `{total, regTotal}`; the cart shows the struck
`regTotal` beside `total` and a red **Discount −$X** row.

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

Both systems share the same bubble component (`.cc` + `.ring`), the far-left
filled back bubble, and dimming for zero-result options.

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
vape · product · cart · confirm · edu · edutopic`

---

## Lifestyles

Six, each with a colour and a logo: **Discovery** `#A0463C` · **Adventurous**
`#C09A64` · **Social** `#F3D390` · **Unwind** `#78A6C5` · **Nightlife** `#5D8A85`
· **Holistic** `#7E9A5B`.

Holistic was added later for CBD-forward products; its logo is generated by
`gen_holistic_logo.py` (an "H" built to match Jack's letterforms, with the
"HOLISTIC" wordmark recomposed from letters lifted out of his other logos).

Lifestyle drives the product-card border colour and the monogram badge.

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

## The size sheet

Tiles show one size and a **See more sizes** control instead of Add to Cart. The
sheet slides up over the whole card: size/price pill buttons (white outlined,
solid orange when selected), a chevron to drop it back, and Add to Cart at the
bottom that becomes the product page's quantity stepper.

Products with a single size (edibles, concentrates, topicals) keep Add to Cart —
there's nothing to open. Sheet classes live in the `fs*` namespace because `.s`
is a global `display:none` rule.
