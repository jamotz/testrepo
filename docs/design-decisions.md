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

- **2 for $50** → $25/eighth on the four deal flowers, **pairs only**, mixed and
  matched across the bag. Odd units stay at regular price. Jack asked for this
  explicitly.
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

### The deal banner keeps its copy on top and dates itself underneath
Jack, 2026-08-17. The offer line stays where it was — top line, right side — and
the run-out date sits under it a step smaller and lighter, so the deal still
reads first and the date answers the question it raises. The date comes from
`dealUntil(key)`; `DEAL_UNTIL` can pin one, and an empty string there means
"work it out" (see *Every banner carries its run's end date*).

**The copy holds one line and the block centres in the space beside the label.**
It used to wrap to two ragged right-aligned lines, which put each banner's text
in a different place. `.bs` is now a `flex:1` column, centred on both axes, with
`white-space:nowrap`; the label is `flex:none` so it never gives ground. The
longest of the three strings sets the ceiling — at the copy's original 11px it
measures 219px in the 233px the "2 For $50" label leaves, about 14px of slack.
**A longer line will overflow rather than wrap**; shorten the copy or drop the
type a step.

### The deals calendar runs on a weekly pattern, not typed dates
Jack, 2026-08-18: a date-oriented page a month out, the date as the section
title, the orange banner as the deal's title, and a dropdown for the products.

**The schedule is a rota, not typed dates.** `DEALDEF` gives each deal the
weekday it runs on and the renderer walks the next 30 days from *whenever the
app is opened*. Typed dates would have made the case study open on a page of
expired deals a fortnight after it was built — the one thing a "what's coming
up" screen must never do. The cost is that the calendar can't express a one-off;
add a day-offset field the same way if a one-off is ever needed. Either way the
schedule is **authored** and Jack's to set: seven keys in one table.

**Two deals a week, on a four-week cycle** (Jack, 2026-08-18: "there is rarely a
deal a day going on at shops… please keep the variance"). The first cut ran all
seven every week — a deal every single day, which no shop does. Each deal now
holds a `week` slot in a four-week rota as well as its `dow`, so a 30-day view
shows **eight deal days instead of thirty**, and every shelf still comes round
inside the month:

| Week | | |
|---|---|---|
| 0 | Tue — 30% off Wyld (edibles) | Fri — 2 For $50 (flower) |
| 1 | Thu — BOGO $40 (concentrates) | Sun — 40% Off (flower) |
| 2 | Tue — 25% off (pre-rolls) | Fri — 2 For $50 (flower) |
| 3 | Mon — 30% off (concentrates) | Sat — 30% Off brands (flower) |

Each week pairs the flower anchor with one other shelf, and the two days sit
apart, so the month reads as a steady drip rather than two deals and a
fortnight of nothing. **2 For $50 is the only deal with two slots** — it's the
store's signature offer, so it runs fortnightly while the rest come round
monthly.

`dcWeek(date)` takes the cycle position from the **date itself** — whole weeks
since the epoch, shifted so a cycle turns over on a Sunday — rather than from a
counter, so it stays continuous across months, renders and sessions.
`dealNextRun()` scans the whole cycle now, since a deal can be up to four weeks
out. It is only a fallback for the home banners' dates — those read the live run
first; see *Running now, then upcoming*.

**Running now, then upcoming** (Jack, 2026-08-18). The page led with the next
deal to *start*, which hid the ones a shopper could actually use: a run lasts
3–7 days, so a deal that began on Monday is still on when they open the app on
Wednesday. `dcOccurrences()` therefore scans a week **backwards** as well as
forward and marks each occurrence live or not; the live ones head the page under
*Running now*, ordered by which ends soonest, and everything else follows under
*Upcoming*. Two deals surfaced on the first render that the old page couldn't
show at all.

A live deal is headed by the day it **started** — its end date is already on the
banner, so repeating it would be the only thing on the card said twice. An empty
*Running now* is dropped rather than announced; *Upcoming* then explains itself.

**Home reads the same occurrence list.** `dealUntil()` used to take the next
*start* and date its end, so a home banner could say "Until 9/3" while the
calendar said the running deal ends 8/20. It now takes the first occurrence of
that deal from `dcOccurrences()` — the live run if there is one, the next
otherwise — so the two screens cannot name different days for the same deal.

**The banner is the deal's title and its toggle.** Reusing `dealBanner()` means
a deal looks identical on the home page and in the calendar, which is the whole
point of a calendar — you recognise what you're being promised. The expand
control sits *under* the banner rather than inside it, as a chevron row, because
putting it inside would have pushed the copy off the centre Jack had just asked
for.

**Every banner carries its run's end date** (Jack, 2026-08-18). The date heading
says when a deal starts, the banner's "Until" says when that run ends, so the
two dates answer different questions rather than arguing. The dates are
**generated, not typed**: a run ends 3–7 days after it starts, chosen by hashing
the deal key and the date. Hashing rather than `Math.random()` is the point —
the same occurrence must show the same date every render, or the calendar
reshuffles itself under the reader.

**Home takes its date from the same generator.** `dealUntil(key)` returns the
end of that deal's current run, so home and the calendar can't disagree about
when one deal ends. `DEAL_UNTIL` survives as a **pin**: a non-empty string wins,
for when Jack wants a fixed date on a specific deal. The old `Until 12/25`
placeholders are gone — they contradicted "typically ends within a week".

**Nothing in the calendar restates the catalog.** Each deal resolves its own
products through `items()`, so a re-flagged or renamed product follows
automatically — the same rule the Account screens follow.

**The 30%-off rows show today's price, and say so.** That deal is defined on
brands, and `priceFor` doesn't model it — the home page only ever showed brand
tiles. Rather than open a second discount path (the exact divergence that once
had the shop showing $174 and the home deal $58 for one product), the panel
carries one line: the four brands, then "30% comes off in store on the day, so
the prices below are today's."

Brands are matched as a **prefix**, because the tiles say "Royal Tree" and the
catalog says "Royal Tree Gardens". Freddy's has no flower in the catalog at all,
so it contributes nothing to the 18 rows — the note still names it, which is why
the note lists the brands rather than leaving the row list to imply them.

### Every shelf gets a deal, and the line-ups are ranked, not typed
Jack, 2026-08-18, once the calendar existed. Seven deals, one per weekday:

| Day | Deal | Shelf | Line-up |
|---|---|---|---|
| Mon | 30% Off | Concentrates | the 4 most expensive |
| Tue | 30% Off | Edibles | one whole brand (Wyld) |
| Wed | 30% Off | Flower | four brands' top shelf |
| Thu | BOGO $40 | Concentrates | the 4 cheapest, two grams for $40 |
| Fri | 2 For $50 | Flower | the four `sale:1` flowers |
| Sat | 25% Off | Pre-Rolls | the 5 most expensive |
| Sun | 40% Off | Flower | the same four flowers, 14 g / 28 g |

**Where Jack described a rank, the code ranks** — `dcRank(type, dir, n)` sorts
the shelf by price and takes the top or bottom N. Typing out "the 4 cheapest
concentrates" would have been four names that quietly stop being the four
cheapest the next time a sheet is re-exported. The edible deal is the exception
by design: "an entire brand, just one" is a name, so it is one — `edbrand.brand`.

**None of the five new deals is modelled in `priceFor`, deliberately.** They run
on future dates; making them live in pricing would discount the shop today. So
their rows quote today's price and each panel carries one line saying the
discount comes off on the day. Only the two flower deals — which *are* live —
show a struck price.

Ranking by `pr` has one wrinkle worth knowing: on pre-rolls `pr` is the pack
price, so "most expensive" is topped by the 20-packs. That is the right answer
for a deal (they're the priciest things on the shelf), but the rows use the
tiles' own `servTotal` slot so a 20-pack reads `0.5G EACH` rather than a bare
`0.5G` beside $79.99.

### Brand tiles are product tiles, measured not guessed
Jack, 2026-08-18: the brand row should be exactly the size of the product row —
**the shop's product tile is the reference**, not a size of its own. They were
160×176 against the cards' 218-wide; both rows now use the same width and the
same `zoom:.9`, and `sizeDealRows()` measures a rendered product tile rather
than pinning a number in CSS, because a card's height moves whenever its
contents do (the tinted weight pill, a second line of name).

**Two traps, both live in the first attempt — 222 px tiles shipped at 263:**

1. **A fixed height on a brand or See All card makes it the tallest thing in a
   flex row, and every product card stretches up to meet it.** `.dealrow` is a
   flex row at default `align-items:stretch`, so a 300 px `.dseeall` dragged
   every deal tile up with it. That was the whole of the visible bug. Neither
   `.btile` nor `.dseeall` carries a height at all now — in a `.dealrow` they
   stretch to the product tiles, and only the **brand row**, which has no
   product card in it, gets a measured height.
2. **A hidden screen measures zero.** `renderHome()` runs at load, while the app
   is still on the landing screen, so every rect is 0 and `sizeDealRows()`
   bailed — which is why the brand tiles sat at their natural 204 px and looked
   like a failed measurement. `nav("home")` calls it again when the screen is
   actually on, and a `load` listener re-runs it once the webfonts have settled
   the text height.

The height is applied as a **ratio** — the value `style.height` uses, scaled by
(target rect ÷ current rect) — rather than by assigning the card's
`offsetHeight` directly. Both give the same answer today (both elements are
`zoom:.9` inside the same frame, so `offsetHeight` 254 → 222.4 rendered for
either). The ratio is defensive, not a fix: it survives the two rows ever
carrying different zooms. *An earlier version of this note claimed the direct
assignment applied the zoom twice and landed 10% short. It doesn't — that 204 px
was trap 2, not a zoom problem.*

Measured after the fix: the tile's own box is 253.9 px, 228.5 px after its
`zoom:.9`, and **222.4 px on screen** — the same three numbers as a shop tile.

The brand logos were capped at 98px tall inside the old short tile. The cap is
now `max-height:100%` — the logo fits whatever height the tile ends up at, so a
number here can't fight the measurement either.

### Freddy's out, Torus in
Jack supplied a Torus logo (2026-08-18) — uploaded to the superseded
`4b84p7` branch, so it was cherry-picked across. Freddy's was the one brand in
that row with **no flower in the catalog at all**, so the 30%-off deal resolved
26 products across three brands while advertising four. Torus has eight, and the
row now matches what the deal actually contains. `Freddy's Main Logo.png` stays
in the repo; only the `M` entry in `asm_app.py` moved.

### "See All" opens a deal, which needed a filter that isn't a product property
Jack, 2026-08-18. Every deal row ends with a tile-sized card that opens the
whole deal in the shop list. The two flower rows already showed all four of
their products, so this earns its place mainly on the brand row, which shows
four logos over 26 products — but it's on all three, because a row that
sometimes ends in a card and sometimes doesn't reads as a bug.

`S.deal` holds a `DEALDEF` key and `match()` tests membership of that deal's
resolved product set. Every other facet is a property of the product itself
(`p.sub`, `p.st`), so this one resolves through the deal and memoises the answer
in `DEALSETS` — `P` never changes at runtime, and without the memo `match()`
would rebuild an 18–26 item list once per product per render.

In deal mode the shelf bubbles are hidden (they have nothing to filter inside one
deal) and the deal's own banner heads the list, so the promise that got you there
is still on screen next to the prices. `S.deal` clears on every path that re-aims
the list — the shop circles, the drawer's type buttons, Guide Me's finish, and
Clear — because a stale deal filter would silently subtract products from an
unrelated shelf.

### The "2 for $50" label is permanent
It stays visible on eligible eighths at every quantity, as the deal's label
rather than a temporary prompt. The 40%-off items carry an equivalent line.

### Every screen wears the same brown title bar
Jack, 2026-08-18: Shop and Cart were the only screens without one. Shop and the
product list had their own white `.shophead`; the cart had no header at all.
Both now use `.sbar`, the component Account and Origins U already use — one
title bar in the app rather than three treatments — and the dead `.shophead`
rules are gone. The cart's bar reads **Your Cart** (was "Your bag" / "Shopping
Cart" in the body), and the body headings came out with it: with the bar
carrying the title, an in-page `<h2>` said it twice.

### The trolley belongs over Cart
The tab bar had a shopping trolley over *Shop* and a tote over *Cart*. Swapped
(Jack, 2026-08-18: "one is literally a cart"). The badge wrapper stays on the
Cart button, so the count still sits on the trolley.

### Filter and Sort are a pair: olive and orange
`.fbtn` is olive everywhere in the app, but `.shopfrow .fbtn` overrode it to
white-on-orange, which made the filter the loudest thing on the shop page. The
override is gone. Sort was a small bordered white box beside it — it now mirrors
the filter pill exactly (same radius, padding, type, 47 px tall) in the brand
orange, so the two read as one control pair. The `<select>` keeps its native
behaviour; only its own chrome is replaced, with a white chevron and dark
options for the OS menu.

### Origins U had no photos because its image keys were never wired
The hub and topic banners have always read `IMG[c.img]`, but six of the eight
keys — `flower`, `rosin`, `gummy`, `topical`, `badder`, `thca` — were never in
`asm_app.py`'s asset map, so those cards rendered `<img src="">`. Only
`growbud` resolved.

Rather than add six new asset entries, the `EDU` table now points at **images
the app already embeds**: `growbud` (the "Full Bud – educational" shot),
`cro_live`, `ed_gum_purple`, `top_balm`, `fl_universal` for Forms of CBD (the
image the CBD flowers themselves use) and `clr_diamonds` for Types of
Cannabinoids (diamonds being THCA). No new files, nothing to go missing, and
the hub matches the shop's own category circles. Lifestyles keeps its strip of
six logos and never used `img`.

The two categories added on 2026-08-20 follow the same rule: Liquid Edibles
takes `drink` (the orange bottle, the shop's own Drinks circle) and Vapes takes
`clr_badder` — a cartridge is full of concentrate, so a concentrate shot is the
honest picture. Both were checked against the built `IMG` before being written
in, which is the check this section exists to demand.

**`vape` is not an image key.** The shop's Vapes category circle asks for
`IMG["vape"]`, which `asm_app.py` has never carried — the circle has been
rendering in its `noimg` fallback state the whole time. It degrades quietly
(that's what `noimg` is for), so it looks deliberate. Supply a `vape.png` and
it wires itself up; until then don't reference the key from anywhere new.

### Origins U covers the shelves, and every link lands on its own page
Jack, 2026-08-20. Drinks used to open the **Edibles** page and vapes the
**Concentrate** page, so two shelves were being taught under another shelf's
name. Both now have their own category — **Liquid Edibles** and **Vapes** —
taking the hub from eight cards to ten, five clean rows of two.

The order is product shelves first (Flower, Concentrate, Edibles, Liquid
Edibles, Topicals, Vapes), then the concept pages (Lifestyles, Forms of CBD,
Growing Process, Types of Cannabinoids).

**Two routes stay pointed at another category on purpose:**

- **Pre-rolls → Flower.** A pre-roll is flower, or flower infused with a
  concentrate; it has no education of its own to give (Jack's call). Don't add
  a Pre-Rolls card.
- **Tinctures → Forms of CBD.** That page already covers tinctures, and nothing
  in the catalog is one.

The vape dead-end's *Learn about the Differences* link used to call
`renderEduTopic("concentrate", 0)` directly, bypassing `EDUMAP`. It goes through
`openEduFor("vape", 0)` now, so **`EDUMAP` is the single routing table** and a
future re-pointing happens in one place.

Topic copy for both new categories is **authored**, flagged `AUTHORED` in the
table — the same standing as the rest of Origins U's copy, none of which comes
from a sheet.

### The Origins U tile is the shop's product tile, framed in olive
Jack picked **option A3** (2026-08-20, after a first pass at option C). The card
was a flat `#D9A87C` peach — a colour that appears nowhere else in the palette,
not `--cream`, not `--tan` — which is most of why Origins U read as a different
app bolted on.

It now uses the `.fcard` shell — white, 12px radius, the same shadow — with two
deliberate departures from a product tile:

- **No label bar.** The category name is `--olive` text under the photo, the way
  a product tile names itself, over a neutral `#E1DBCD` rule.
- **The border is `--olive`, not the tile's neutral `#E1DBCD`.** With the bar
  gone, the border is the only thing carrying brand colour on these cards, so it
  takes that job rather than leaving them as white rectangles.

**The two lines are deliberately different weights.** Olive frames the card;
neutral grey divides photo from label. Running both in olive (variant A1) read
as more enclosed than the shelf needs, and dropping the rule entirely (A2) left
the label unanchored — the original argument for keeping a bar at all.

The route here matters more than the endpoint: an earlier pass shipped **option
C**, which kept the bar and put it in `--olive` with cream text. That was a fine
card in isolation; eight of them stacked still read as a row of coloured slabs
under a brown `.sbar`. Also rejected: the bar in `--brown` on the new card (B),
and the photo in an `#EDEFE1` tinted well (D), which keeps the grouping the
peach gave but adds a second surface colour per card.

**The Lifestyles tile is the odd one out** and now visibly so: it is six black
wordmark glyphs where its nine neighbours are product photography. The peach
disguised that; white doesn't, and A3 makes it plainer still — with no bar to
balance the weight, the glyphs sit alone inside an olive frame. Not addressed
here; it needs its own treatment rather than a tweak folded into a card change.

### The button family is outlined: coloured border, white interior, coloured text
Jack, 2026-08-18. Filter and Sort set the pattern, and Origins U's Search and
Continue, and Account's Logout, follow it. The two shop controls **don't have to
match sizes** — Jack said so explicitly; they read as a pair through colour and
shape, not by being twins. Sort's label is just `Sort:`, and its value sits at
the same size as the label rather than a step down.

Filter is `--olive` `#555624` — **the same olive as Origins U's Search pill**
(Jack, 2026-08-20). The app's two outlined non-orange controls are one colour,
so the family reads as a family rather than as two greens that nearly match.

*Superseded:* Filter was the lighter Holistic green `--hol` `#7E9A5B` from
2026-08-18. That measured **3.15:1** on white — fine for large text, short of
AA's 4.5:1 for its 16px label — and was carried as an open question with
`#5C7540` (5.16:1) earmarked as the drop-in. Matching Search settles it
instead: `#555624` is **7.66:1**, clearing AA and AAA, so the question is
closed and `#5C7540` is not needed. **Don't "restore" the lighter green** — it
was a colour choice that also happened to fail a contrast threshold, and both
reasons for moving it still hold.

The knock-on: solid fills now mean something. Add to Cart on a tile, Checkout
and the hero's three buttons are the only filled orange left, so the app has one
primary weight instead of six.

### Hero buttons were set two sizes too small
12.5px inside an 80%-wide pill read as a caption in a button. They now use the
app's own button type — 1rem, `.06em`, the same as Filter and the account
buttons — so the hero stops under-setting itself (Jack, 2026-08-18).

### Logout is a settings button, not a shout
It was solid orange at 1.32rem while every button on Account Settings is an
outlined .95rem pill. Both screens now draw the same button (Jack, 2026-08-18).

### One weight pill, everywhere
Jack picked **option B** for the product page (2026-08-18): size pills join the
outlined family, Add to Cart stays the one filled thing on the screen. The same
pill then went app-wide — tiles, deal cards and the product page had three
different treatments between them:

- **outlined olive** = a size you could pick
- **solid olive, cream text** = the size you are on
- **tinted `#EDEFE1`** = serving/total, which is a *fact* about the product, not
  a size you can choose, so it deliberately stays out of the pair

Type went up a step with it (tiles 10 → 11px, product page 12.5 → 13.5px). This
retires two earlier rules: the tinted `#D2DBBC` tile pill from 2026-08-14, and
the brown/cream deal-card override that had to exist because the tinted rule
made its selected pill olive-on-olive. One language now, so neither special case
is needed.

### Advanced Settings sits inside Account Settings
Jack asked for somewhere to put a toggle that swaps lifestyle names for strain
names, plus accessibility options, and was open on placement. It leads the **lower button group on Account Settings**, with Privacy Policy and
Terms paired beneath it in the same two-up `.acmini` format the Account page
uses (Jack, 2026-08-18) — settings belong with settings, the gear on Account
already leads there, and it stays out of a shopper's way without being hidden.

Four switches, all of them real rather than decorative:

| Switch | What it does |
|---|---|
| Use product type | Swaps the six lifestyle words for Sativa / Sativa Hybrid / Hybrid / Indica Hybrid / Indica / CBD, everywhere |
| Enlarged view | **Placeholder.** The switch moves, the app doesn't |
| Reduce motion | Kills every transition and animation |

**Enlarged view is deliberately inert** (Jack, 2026-08-18): "don't add that
functionality yet, just a placeholder". It replaced two narrower switches —
larger tiles and bigger text — because what he wants is the *whole app* scaled
proportionately, which is a frame-scale job rather than a list of font sizes,
and worth doing once. The row carries a **Coming soon** tag and the switch
toasts, so nobody demos it expecting a result. `tiles-compact` stays on `#view`
untouched, ready for that work.

**The product-type toggle is a label lookup, not a data migration** — exactly as
planned when lifestyle became "the strain, renamed". Every printed label goes
through `lifeLabel(key)`, which returns `FEEL[key]` or `STRAINNAME[key]`; `P` is
untouched. `setAdv()` re-renders whatever is on screen, because labels are baked
in at render time.

**One place needed more than a lookup.** The Guide Me wizard shows each
lifestyle as a *wordmark image*, which can't be re-lettered, so each option also
carries a text twin that `#scr.strainnames` swaps in.

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

**Almost nothing is authored any more.** Jack's sheets supply brand, name,
category, prices, copy, the strain — which is also the lifestyle — the potency,
and the three terpenes that produce the feelings and smell/taste chips.

Two things were on this list and should never have been. **Lifestyle** left on
2026-08-12: every catalog stated the strain outright and four generators derived
it anyway, each with a different invented rule, and all four disagreed with their
own sheet. **Terpene** left on 2026-08-14, when the rebuilt catalogs added
`Terp 1/2/3` and the per-generator flavour tables came out.

> **Before writing a table that assigns something per strain, check the source
> for a column that already says it.** That has now cost two rewrites.

What is still authored, all flagged where it lives:

- **The 10 Kief/RSO rows** appended to the concentrate sheet on 2026-08-14. The
  strains all exist in the flower catalog, so their Type and terpenes are copied
  from there — `gen_concentrates` asserts the copied Type still matches — and
  potency and price follow Jack's own earlier Kief/RSO rows. Only brand, size
  and the description text are written.
- **Flower's star rating and review count** — `gen_catalog_products.stable()`
  hashes the strain name. No sheet states either, and they're display-only.
- **The Account block** in `origins-app.src.html`: Noelle's orders and reviews,
  and Seattle's opening hours.
- **Edible and topical feelings/taste**, until those sheets gain terpenes or
  their flavour/effect columns are mapped onto the 30 terms.

*Superseded:* the `AUTHORED`/`EXTRA` blocks in `gen_concentrates.py` (Kief rows
51–56, syringe rows 57–60) are gone — those products live in the sheet now. So
is the authored edible price table; the curated sheet carries real WA retail
prices ($18–$30).

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
treatment** rather than the solid fill.

**Superseded 2026-08-14:** every weight on a product tile now uses that tinted
treatment — pale green ground (`#EDEFE1`), dark olive text (`--olive`) — not
just the serving/total ones. Jack asked for the whole shelf to match the
multi-pack "0.5G EACH" pill.

That drops the distinction this section used to draw, where a solid fill meant
*the selected size* and a tint meant *a fact about the product*. On a product
tile there is only ever one weight shown, so nothing is being selected and the
distinction had nothing to carry. **Deal cards keep the solid fill**, because
they do show a row of sizes with one selected — `.fcard.dcard .fsz.sel` outranks
the new rule on specificity. The product-info page is unchanged for now.

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

### The bezel needs its own width, or the page box strangles it
`fitFrame()` sizes `#phonebox` to the **scaled** footprint so the page flow stays
tight around a transformed element — `transform` doesn't change layout size, so
without that the page reserves the full unscaled 474px. Correct, but `.phone` is
an ordinary block child of `#phonebox`, so it inherited that smaller number as
its own width while `.scr` stayed a hard `width:452px`.

The result: the black bezel was drawn **94px narrower than the screen it wraps**
at k=0.8 — 380px against 452 — so the screen overflowed its right edge and the
right-hand bezel and both right rounded corners simply weren't there. Every
screen had it; the Guide Me wizard showed it worst, because its options are
full-width colour bars that get sliced, and `.immersive` hides the tab bar so
there's no bottom edge left to make the frame read as a frame.

`.phone` now carries `width: DESIGN_W + bez` explicitly, set in `fitFrame()`
beside the transform. Verified symmetric at 1366×768, 1440×900, 1920×1080,
1440×1200 and 393×852, framed and full screen — the left and right gaps match
the 11px padding in framed mode and are 0 in full screen, where the padding is.

**The general trap:** an element you scale with `transform` and an element whose
layout box you pin to the scaled size cannot be the same element, and they
cannot be parent and child either unless the child's width is stated. A fixed-
width grandchild will quietly overflow instead of resizing.

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
Two 50-row drinks catalogs were uploaded together. Use
`..._Source_Inspired_Unique_Descriptions.xlsx`; the other,
`..._Final_CBG_Fix.xlsx`, has since been deleted. It was **identical except for
the Description and Source columns** — the CBG data it was named for was the
same in both — and 17 of its 50 descriptions were truncated mid-word. Noted in
case it reappears.

### The bubble path, built from the IA (2026-08-17)
`WA_Drinks_IA_Condensed.xlsx` states the whole path: **Drinks → THC / CBD /
Blend → Drink / Shot / Seltzer / Sorbet / Honey**, and it stops there. The data
already carried it — `sub` the branch, `sub2` the type — so this was a
`renderList` branch, not a data change. It reuses the pre-roll bubbles
wholesale: same `.cc` + `.ring` component, same far-left filled back bubble,
same first-photo-not-yet-claimed trick (the three branches sell the same
vessels, so taking each branch's first product would have put the same bottle in
all three rings).

**Two levels, because the IA rules out the obvious third ones.** It names each
exclusion outright: size is never a filter, dose is never a navigation layer,
ratios are metadata. So the shelf ends at the type.

**Size stays in the drawer, though** — Jack overruled that one line the same day:
"it ain't hurting no one. All available sizes are in the names of the drinks."
The facet had been offering the edible mg list, which no drink's own `szs`
contains, so every pick returned nothing. `SIZES.drink` is now derived from the
catalog at load — the distinct volumes, sorted numerically (2 / 4 / 6.7 / 12 /
16 oz) — so it can't drift from the products the way a typed list would. Prices
are untouched by this: every drink carries an explicit `pz` per size, so the
`sizeMult` fallback (which indexes into `SIZES`) is never reached.

**One deviation from the other shelves, and the IA asked for it.** Concentrates,
edibles and pre-rolls *dim* an option with no products; the drinks IA says
"only show product types that exist for the selected cannabinoid category", so
an empty type is dropped instead. All 15 branch × type combinations are stocked,
so the two behaviours are identical today — the rule only bites when a shelf
runs out.

The breadcrumb mirrors the filter the way pre-rolls do (`THC › Shot`), rather
than repeating the category the tab already names.

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

---

## Terpenes drive the feelings and scents

**Landed 2026-08-14.** Jack's rebuilt catalogs name three terpenes per product
(`Terp 1/2/3`). `cannabis_terpene_mapping.xlsx` maps every terpene to three
(Feeling, Smell & Taste) pairs ranked Primary / Secondary / Tertiary, and
`terpmap.py` is the bridge. **Nothing is authored in a generator any more.**

### Each terpene contributes its Primary pair
Not "Terp 1 -> Primary, Terp 2 -> Secondary, Terp 3 -> Tertiary". That reading
looks reasonable and is wrong: it repeats a feeling inside the same tile on
**56%** of products. Taking each terpene's Primary pair in Terp 1/2/3 order
yields three distinct feelings and three distinct scents on **all 160** products
across the three smokeable catalogs — zero collisions, which is what shows the
sheets were authored for it.

Secondary and Tertiary aren't dead: they're the fallback when a product names
fewer than three terpenes, which nothing else could supply.

`terpmap.check()` runs on every generation and refuses to emit if a terpene is
missing from the mapping, if a product's terms collapse to fewer than three, or
if any emitted term falls outside the 30 in `cannabis_feelings.xlsx` /
`cannabis_smell_taste.xlsx` — the 30 that have icons.

### One reader, in one place
`xlsxread.py` now holds the xlsx reader all six generators share. It used to be
copy-pasted per generator, which is how the self-closing-cell bug survived in
four copies at once.

### Pre-roll multi-packs read "0.5 G EACH"
**Jack, 2026-08-14.** A 3-pack of 0.5 g joints states the size of one joint, not
the total: `0.5G EACH`, not `0.5G / 1.5G`. The pack count is already in the
product name and nobody shops on total gram weight.

The stored size stays **bare**. Jack's sheet writes "0.5 g each" on multi-packs,
but `szs`/`pz` strip it so the Filter drawer keeps the IA's three size options
instead of growing to six. The tile re-adds "each" from `pk`. Note `feedPill()`
strips the word itself, so it has to be appended *outside* that call.

### Kief and RSO are on the sheet — the note that said otherwise was wrong
**Corrected 2026-08-17 (Jack).** This section used to claim the "Final"
concentrate sheet covered only Live Resin, Rosin, Hash and Distillate, and that
the Kief and RSO rows were an authored `EXTRA` block that couldn't survive the
move to terpene-driven chips.

The sheet has all 60 rows, Kief (6) and RSO (4) included, each with its three
terpenes. `gen_concentrates.py` maps every one of them in `JOIN`, and re-running
it emits **byte-identical rows to the ones already in the app** — so both
bubbles have products behind them (Loose / Dry Sift / Infused Kief, RSO Oil
Syringe / Applicator, two products each) and their chips are terpene-driven like
every other smokeable.

What remains true is the narrower note under *Content authored vs. supplied*:
those ten rows were **written onto the sheet** on 2026-08-14 rather than coming
from a vendor catalog, with strains and terpenes copied from the flower catalog
and only brand, size and copy composed. Authored-into-the-sheet is not the same
as absent from it, and this section conflated the two.

This is the second time a "the sheet is missing/malformed" note has outlived the
thing it described — see *The sheet was never broken — the reader was*. Re-check
the sheet before writing code, or a doc line, around a claim like this.

**Still genuinely empty** (photos and bubbles, no products): `Rosin Coins`,
`Full Melt Hash`, `Distillate Syringe`, `Dab Applicator`. Those four are one
level down inside Rosin, Hash and Distillate — nothing to do with Kief or RSO.

### Flower is regenerated from a sheet now, and nothing about it is authored
The "Final pt2" flower catalog added **THC %, CBD % and Grow Method** to the
columns the first Final sheet had. Those were the three fields the old generator
invented with a seeded RNG because the original `.docx` carried none of them.
All three inventions are gone; every value on a flower tile comes from the
sheet or from the terpene mapping.

**The "don't regenerate flower" warning is retired.** It existed because photos
were drawn sequentially from a shuffled pool, so inserting one product
reshuffled the photo of every product after it. Photos are now chosen by
hashing the strain name against a pool *scoped to that strain's type* — an
Indica draws from the indica shots. A strain keeps its photo across rebuilds,
and row order no longer matters. Star rating and review count are derived the
same way; they are the only two display fields no sheet supplies.

Flower went 34 -> 50 products. The four legacy mock rows are gone with the
rest — they predated every catalog and carried no terpenes.

### The four deal flowers, and where the nomination lives
Jack nominated **two Passion Flower and two Lifestyles** flowers (2026-08-17).
The sheet has no deal column, so the four are named in `DEALS` in
`gen_catalog_products.py` rather than hand-flagged in the spliced rows — a
regeneration would otherwise clear the deal silently. The generator refuses to
emit if a nomination stops matching exactly one row, or if a nominated eighth is
at or under $25, which would advertise a discount that is really a markup (the
two CBD flowers on these brands sit at $24–25, so this is not hypothetical).

Jack named the brands; the strains inside them were picked to spread the row
across four lifestyles, and each is one line in `DEALS` to swap:

| Brand | Strain | Strain type / lifestyle | Eighth |
|---|---|---|---:|
| Passion Flower | Northern Lights | Indica · Nightlife | $35 |
| Passion Flower | Pineapple Express | Sativa Hybrid · Adventurous | $34 |
| Lifestyles | Gelato Cake | Indica Hybrid · Unwind | $35 |
| Lifestyles | Jack Herer | Sativa · Discovery | $32 |

`renderHome()` still skips a deal section whose row would be empty, so the app
degrades the same way if the four are ever un-flagged. The 30% Off brand row is
unaffected either way — it renders from a brand list, not from `sale`.

### 2-for-$50 pairs across the bag, not within a line
The rule used to pair *within one cart line*: two of the same strain hit $50,
one of each of two deal strains did not, even though the banner said mix &
match. `dealAlloc()` now pools every deal eighth in the bag, pairs
`floor(pool / 2)` of them at $25, and leaves the odd one at its regular price.

**The odd one out is the cheapest eighth in the pool.** Units are sorted
dearest-first before pairing, so three eighths at $35 / $35 / $32 pay
$25 + $25 + $32, not $25 + $25 + $35. A shopper who adds a fourth expects the
new one to be the one that was "left over", and any other choice quietly hands
them a smaller discount than the pool allows.

Each checkout is its own pool — the bag, or one past order in Order History —
so history re-prices against the lines that were actually bought together.

The product page can't state a unit price from the product alone any more, so it
asks the live pairing: with deal eighths in the bag it reports what they
actually cost, and with none it shows $25 only when the pool is odd (one more
completes a pair). The hint line switches to *one more deal eighth pairs the
last one* whenever something is unpaired, on the product page and above the cart
totals.

### The deal card's selected size pill needed its cream text back
`.fcard .fsz.sel` sets olive text for the tinted `#D2DBBC` ground (2026-08-14).
Deal cards keep the solid **olive** fill to mark the selected size, so they
inherited olive-on-olive and the weight vanished. It only became visible when a
flower carried `sale:1` again and the deal rows rendered for the first time
since — a reminder that the deal rows are a rendering path nothing else
exercises.

### The 30 icons are keyed by their own term
`pIcon("Relaxed")` resolves to `IMG["relaxed"]` — no lookup table. The icons are
registered in `asm_app.py` as bare lowercase terms (checked: none of the 30
collides with an existing image key), and the terpene mapping only ever emits
those 30 terms, so flower, concentrates and pre-rolls always hit.

They go through **`embed_rgba` at 128px, not `embed_glyph`**. `embed_glyph`
repaints its input black, which would throw away the orange/olive palette; the
default path would flatten the alpha onto white and box each icon. The dispatch
keys off the asset folder rather than a key prefix, so the term stays clean.

Edibles, topicals and drinks still carry the old vocabulary and fall through to
the generated SVGs. Across the catalog **1288 chips resolve to a supplied icon
and 284 fall back** — the 284 are exactly those three shelves.

