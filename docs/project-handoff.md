# Origins App — Project Handoff

**Last updated:** 2026-09-03 · branch `claude/accessibility-handoff-review-dhabtz`
**Live prototype:** https://claude.ai/code/artifact/ff102055-8262-4b48-a681-8d77f802c968

Hi-fi clickable prototype of the **Origins** cannabis retail app, built for Jack
Motzkin's UX portfolio case study. Everything is a single self-contained HTML
file assembled from a source file plus image assets.

---

## Where this sits

The **portfolio website** (`site/`, Astro) is the overall project. Origins is one
case study inside it, and this prototype is what its case page will show. The
root `HANDOFF.md` covers the site; this folder covers the app.

**The `main` branch is unrelated.** It holds old coursework — Jupyter notebooks,
`firstpython.py` — and none of this project. GitHub shows it by default, so a
browse that "can't find the files" is almost always looking at `main`. All work
lives on the `claude/*` branches.

**Only the branch named at the top of this file is current.** Superseded
`claude/project-docs-review-*` branches stay on origin and look plausible —
`sz8jwv` predates the pre-rolls and every Account screen, and `4b84p7` stops
before the deals, the calendar and everything after. `os7hx4` is the most
recent of these and the easiest to mistake for current: it holds every screen
and reads as complete, and it is behind by exactly the phone-bezel fix. Check
this line against `git log` before trusting a branch, and update it here when
the work moves.

---

## Start here (new session)

```bash
git fetch origin claude/accessibility-handoff-review-dhabtz
git checkout -B claude/accessibility-handoff-review-dhabtz origin/claude/accessibility-handoff-review-dhabtz
python3 -m pip install --quiet Pillow          # recycles remove it
python3 reference/origins/hifi-build/asm_app.py
```

The build prints `wrote <path> (NNNN KB); imgs=142; markers left=0` and a `WARN`
line for any asset it can't resolve. If you are touching Enlarged view, add:

```bash
python3 reference/origins/hifi-build/standard-guard.py        # must print PASS
``` **Containers are ephemeral — commit and
push often.**

Rendering/screenshots use the preinstalled Chromium via Playwright:
`/opt/pw-browsers/chromium-*/chrome-linux/chrome` (path moves after recycles;
`require('/opt/node22/lib/node_modules/playwright/index.js')`).

Publishing: republish to the **same artifact URL** above, or the link Jack has
already shared stops being the live one. Pass the URL as `url=` — publishing
without it mints a separate artifact. **The live link is current as of
`470e2b5`** (republished 2026-09-03, all four guards green) — the Final/pt2 catalogs, terpene-driven
feelings and scents rendered with Jack's icon set, drinks with their IA bubbles,
the four deal flowers with bag-wide mix & match, the Deals Calendar (two-a-week
rota, running-now first), the brown title bar on every screen, the outlined
button family with one weight pill, and Advanced Settings. Since 2026-08-20 it
also carries the phone bezel taking its own unscaled width (the black frame
wraps the screen evenly at every window size), Filter in Origins U's Search
olive, and Origins U on the shop's own card — olive border, no label bar — with
Liquid Edibles and Vapes as their own categories and the Lifestyles tile on its
six colours, and Enlarged view as a token-driven accessibility layer with the full type
scale — every font-size in the app is a token, and the curve is anchored to the
one-card-across layout rather than tuned on its own, then flattened to a
near-uniform ~22px on Jack's call that legibility beats hierarchy in this mode,
then both rounds of his punch list on top of it (hours, tab bar, Filter/Sort row,
strain name at 32px, and the cart badge as option B's soft pill).
**Standard is untouched by all of it** — but that had to be *fixed*, not just
claimed: flattening the scale wrote six enlarged values into Standard for one
build (see below, and `design-decisions.md`). Bump this line whenever you
republish; it's the only way a new session can tell whether the link is behind
the branch.

Since 42f2956 it also carries the two controls Enlarged used to miss: the
product page's back button (52px, up from a hard-coded 26px) and the vape
screen's back button, whose inline `font-size` put it outside the token system
altogether (24px/52px in Enlarged, up from 14.4px/29px in both modes) — plus the
full-screen exit strip growing 48 → 68px in Enlarged so the EXIT chip stops
sitting on the mood chip bar, and the vape screen finally wearing the shop
chrome (`.sbar` + white chipbar) like every other shop page.

**Write the hash *after* the commit exists, not the one you expect to get.** An
earlier value of this line, `4b1e0c9`, was never a commit on this branch —
`git cat-file -t` doesn't resolve it — so the line pointed at nothing.

If the publish is refused with *"hasn't viewed the latest version"*, another
session republished since. `WebFetch` the artifact URL first — it **is**
fetchable despite the claude.ai login, and it saves the full HTML locally so
you can diff the live body against your build before deciding. Only use
`force:true` if Jack says to discard the other version.

The build carries **no `<title>` tag** (it is a fragment), so the artifact takes
its name from the `title` parameter — pass `Origins — App Prototype` on every
republish or the gallery entry renames itself. Favicon 🌿; keep it, a changed
icon reads as a different tab.



---

## Working rules (Jack's, non-negotiable)

1. **Stay true to Jack's frames by default.** Deviate only when he says so.
2. **One screen at a time** — build, screenshot, get sign-off, then move on.
3. **Ask clarifying questions before building anything non-trivial.** Wrong
   guesses on structure cost real rework (see `design-decisions.md`).
4. **Never invent product data** that contradicts his sheets. Authored filler is
   fine when he's asked for it, but mark it clearly. As of 2026-08-14 almost
   nothing is authored: the generators' invented tables are gone and the sheets
   supply strain, lifestyle, potency, prices, copy and the terpenes that drive
   feelings and scents. What remains, all flagged in place:
   - the 10 Kief/RSO rows written onto the concentrate sheet — strains, types
     and terpenes copied from the flower catalog; only brand, size and copy
     composed. They **are** on the sheet and in the app (6 Kief, 4 RSO); only
     their provenance is authored
   - flower's star rating and review count (`gen_catalog_products.stable()`) —
     no sheet states them
   - the Account block in `origins-app.src.html`: Noelle's orders and reviews,
     and Seattle's opening hours
   - which four flowers carry the deal (`DEALS` in `gen_catalog_products.py`) —
     Jack named the two brands, the strains within them are a first pass
   - the deals calendar's schedule (`DEALDEF`) — seven deals on a four-week
     rota, two a week, and the edible deal's brand (Wyld). The **line-ups aren't authored**: each
     deal resolves its products from the catalog, by price rank where Jack
     described one ("the 4 cheapest", "the 5 most expensive")
   - run-out dates are generated (3–7 days after a run starts, hashed so they
     don't move between renders). `DEAL_UNTIL` pins one if Jack wants a fixed
     date
   - topical and edible feelings/taste, until those sheets catch up

   **Before writing a table that assigns something per strain, check the source
   for a column that already says it.** That mistake has been made twice — once
   with lifestyle, once with terpenes.
5. **Say what isn't built, in the UI as well as here.** When *Enlarged view*
   was a placeholder it carried a "Coming soon" tag and toasted, rather than
   quietly doing nothing. It is built now (2026-08-20) and the tag is gone —
   the rule stands, the example is just retired. Origins U's *Search* pill is
   the live one: it toasts "coming soon" because there is no search behind it.

---

## Current state

**308 products** across six types:

| Type | Count | Source | Photos |
|---|---:|---|---|
| Flower | 50 | `Flower Final pt2 Product List for WA.xlsx` | by strain type ✓ |
| Concentrate | 60 | `Concentrate Final Product List for WA.xlsx` (all 60 rows, Kief and RSO included) | per consistency ✓ |
| Edible | 50 | `WA_Edibles_By_Brand_Final_Curated_Normalized.xlsx` | by form + name ✓ |
| Pre-roll | 60 | `Pre-roll pt2 Product List Final for WA.xlsx` | by type + pack count ✓ |
| Topical | 38 | `WA_Topicals_Product_Catalog_Final.xlsx` (sheet 2) + 3 authored | one per form ✓ |
| Drink | 50 | `WA_Drinks_50_Product_List_Source_Inspired_Unique_Descriptions.xlsx` | by type + flavour colour ✓ |

**87 Holistic products**; **62 carry a cannabinoid ratio** (pre-rolls carry
none by design — see `design-decisions.md`).

**Feelings and scents come from the terpenes** on flower, concentrates and
pre-rolls (170 products) via `terpmap.py` — nothing authored. Edibles, topicals
and drinks still carry the old placeholders and are the remaining work.

**Lifestyle is the strain, renamed** (Jack, 2026-08-12) — Sativa/Sativa
Hybrid/Hybrid/Indica Hybrid/Indica/CBD = Discovery/Adventurous/Social/Unwind/
Nightlife/Holistic, one-to-one. Every catalog states the strain, so **no
generator authors a lifestyle** — read the column, don't invent a rule. Four
generators each had their own invented rule until this landed; all four
disagreed with their sheets. Topicals are uniformly Holistic (nothing there is
psychoactive).

The **Use product type** switch in Advanced Settings swaps the two vocabularies
app-wide (2026-08-18). It is a label lookup, not a data change: `lifeLabel(key)`
is the only place a lifestyle word is printed — **use it, or your new screen
won't follow the toggle**.

**Screens built:** landing (store picker) · home/deals · Guide Me wizard
(feel → method → sub-type → taste → recommendations) · shop feed · product list
with filters · product info · cart · order confirmation · Origins U (education
hub + 10 topic pages) · vape dead-end · Deals Calendar (running now, then a
month of upcoming) · Account · Loyalty Points · Account Settings · Advanced
Settings · Order History · Recommended Products · Past Reviews · About Us.

**Every frame in Jack's `hifi-final/` set is now built.** The Deals Calendar and
Advanced Settings have no frames behind them either — Jack specified both in
chat, the way the four unframed Account pages were specified. What's left is
polish and the open questions below.

**The visual language settled on 2026-08-18** and is worth reading in
`design-decisions.md` before adding a control:

- **Buttons are outlined** — coloured border, white interior, coloured text.
  Filter and Origins U's Search share one olive; Sort/Continue/Logout orange. A
  **solid fill now means the primary action** (Add to Cart, Checkout, the hero).
- **One weight pill everywhere** — outlined olive for a size you could pick,
  solid olive for the one you are on, tinted chip for serving/total, which is a
  fact rather than a choice.
- **Every screen wears the brown `.sbar` title bar.**
- **Cards are the shop's product tile** — white, 1.5px `#E1DBCD` border, 12px
  radius, one shadow. Origins U's tiles joined it on 2026-08-20, dropping a
  `#D9A87C` peach that was in no other screen. They keep one departure: no
  label bar (the name is olive text under the photo) and an `--olive` border,
  since with the bar gone the border is what carries the colour.

---

## Immediate next steps

1. **General touch-ups** — Jack is doing a pass across the app, screen by
   screen. Home, shop, cart, Origins U and the account screens have each been
   through a round (see `design-decisions.md` for what was decided and why).
2. **Enlarged view is built and is now a token layer, not a zoom.** The
   `--enlarge: 1.25` / `zoom` description that stood here is retired — it was
   replaced on 2026-08-20 and the rest of this file, `architecture.md` and
   `design-decisions.md` now describe the token system. In short: every
   `font-size` in the app is a `--fs-*` token whose Standard value is the
   original literal; `#scr.enlarged` overrides the tokens once. To make the mode
   stronger or weaker, **move the token values, and re-run the guard** — don't
   add per-rule font sizes, and don't reach for `zoom` again (why it lost is in
   `design-decisions.md`).

   **Run the Standard guard after every change to this layer:**

   ```bash
   python3 reference/origins/hifi-build/standard-guard.py     # PASS / FAIL, exit 0 / 1
   ```

   It resolves every token back to its literal, drops every rule scoped to
   `#scr.enlarged`, and compares what's left against the stylesheet as it was
   *before any Enlarged work existed* — 214 Standard font-size declarations,
   which must match exactly. It takes about a second, needs no build, no
   browser and no assets, so there is no excuse for skipping it.

   **`snapshot-guard.js` re-baselined to `470e2b5` on 2026-09-03.** It was
   `cc6edad`; it moved when Standard started changing for reasons unrelated to
   Enlarged (the vape screen taking the shop chrome). That is a real change to
   what Standard renders, so it is not an accepted delta — those are for
   differences that move nothing on screen — and the documented answer to a
   legitimate Standard change is to re-baseline deliberately. The cost, stated
   plainly: this guard now measures against the last verified state, not against
   pre-Enlarged. **`standard-guard.py` still runs against `cc6edad` with zero
   exceptions, 214 = 214**, so the pre-Enlarged anchor survives where it matters
   most — every font-size in the app. Re-baseline again only after a run whose
   every difference you have read and can name.

   **The baseline is a commit, not a captured file.** `cc6edad` is the last
   commit before the Enlarged work began (verified: zero `--fs-*` tokens, zero
   `#scr.enlarged` rules), and the guard reads its source straight out of git.
   This matters more than it looks: a baseline captured from the *current* file
   would certify whatever regression is already sitting in it. If you ever
   rewrite this guard, keep that property.

   **A legitimate change to Standard will fail this guard, and should.** If Jack
   asks for a different size in *normal* view, Standard has moved and the guard
   says so. Re-baseline deliberately: point `BASELINE` at the commit that made
   the change, in a commit that says what moved and why. **Don't** widen the
   guard, add per-selector exceptions, or drop declarations from the comparison
   to get it green — that trades the whole check for the one change in front of
   you. Telling the two cases apart from the FAIL output: a regression shows
   Standard taking recognisably *enlarged* values (22px, 24px, 1.8rem) on
   selectors you never meant to touch, usually several at once; a deliberate
   change shows the value you intended, on the selector you intended, usually
   alone. When it isn't obvious, assume regression.

   **The heavier check is `snapshot-guard.js`** — run it before publishing, and
   after any change that could move layout rather than just type. It walks all
   24 screens in Chromium and compares **computed** styles (5,582 elements),
   which catches what the text guard cannot: a rule that wins on specificity, an
   `#scr.enlarged` rule that lost its class scope, a size set from JS, or a
   token that moves a layout property. It needs a build of both sides, so budget
   ~2 min each:

   ```bash
   SP=<scratchpad>
   git worktree add -f $SP/base cc6edad
   python3 -m pip install --quiet Pillow
   python3 reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/cur.html
   python3 $SP/base/reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/base.html
   node reference/origins/hifi-build/snapshot-guard.js $SP/base.html $SP/cur.html
   ```

   `asm_app.py` writes to the same scratchpad path both times — **move the first
   output before building the second** or the second silently overwrites it.

   It carries a short **accepted-deltas** list: differences from the baseline
   that are known and intended, each with a reason, and the run prints how many
   it applied so they stay visible. Today there are 5 — `.fbtn` and `.edusearch`
   taking `min-height:47px` from `--control-height` in the token refactor
   (visually inert: both already rendered at 50px), and the `span.advsoon`
   "Coming soon" tag removed when Enlarged shipped. **Never add an entry to turn
   a red run green** — an entry means someone checked that the change to
   Standard was deliberate. If the list starts growing, the baseline is wrong,
   not the app.

   **Both of those guard Standard.** Neither says anything about whether
   Enlarged itself works. Two more cover that side:

   ```bash
   node reference/origins/hifi-build/ratio.js         <built.html>   # the curve
   node reference/origins/hifi-build/enlarged-check.js <built.html>  # the mode
   ```

   **Neither Enlarged check sees the full-screen chrome.** `enlarged-check.js`
   walks elements inside `.s[data-s="<screen>"]`, and `#fsexit`, the status bar
   and the island all live *outside* that root — so the exit chip covering the
   mood chip bar in Enlarged went unnoticed by all four checks and was found by
   looking at a screenshot. If you widen anything here, widen this: the chrome
   layer has no coverage at all.

   `ratio.js` prints each element as a percentage of its card in both modes —
   the check for whether the curve is still anchored to its container.
   `enlarged-check.js` turns the mode on and walks all 24 screens looking for
   the toggle failing to round-trip, page-level horizontal scrolling
   (WCAG 1.4.10), content spilling past the app frame, and tap targets under
   24px (WCAG 2.5.8). Note its carousel exception: deal rows and chip rows
   scroll horizontally, so their children sit outside the frame legitimately —
   without that exception the spill check reports five screens of false
   positives.

   It sweeps **4 viewports** (1440×900 and 1366×768 framed, 393×852 and
   320×568 full screen), because a single viewport proves very little here: the
   app always lays out at 452px and is transform-scaled by `k`, so what a reader
   actually gets is `design px × k`.

   Verified on a build of `1ca26e4`: round-trip clean at every viewport (name
   14→32→14px, nav 9→15→9, tab icon 21→34→21), no horizontal overflow, nothing
   spilling the frame, **0 findings across 4 viewports × 24 screens**.

   **The relative gain is scale-invariant — exactly ×2.32 on body text at every
   viewport, framed and full.** Both modes scale by the same `k`, so Enlarged
   always delivers its full benefit; what changes is the absolute size. Framed
   mode floors at `k=0.5`, so on a 1280×600 window Standard body renders at
   4.8px and Enlarged at 11.0px — the mode is working, the stage is just small.
   **Review the mode in full screen**, where a real phone puts it: 393×852 full
   gives 8.3 → 19.1px, 320×568 full gives 6.7 → 15.6px.

   The check separates a target under 24px **by design** (a real defect) from
   one that only falls under once `k` shrinks it (a property of the preview
   stage). Don't conflate them — measuring `getBoundingClientRect` alone reports
   9 false findings at these viewports.

   **The regression it exists to catch has already happened once.** Flattening
   the Enlarged type scale used `re.sub(..., count=1)` on six semantic tokens.
   `count=1` replaces the *first* match in the file, which is `:root` — the
   **Standard** block — not the `#scr.enlarged` one below it, so Standard
   silently took the enlarged values (`--text-body` 13px → 22px, `--text-nav`
   9px → 22px, and four more): the nav bar, product card text, weights and
   filter labels all read as enlarged in normal view. Fixed in `25c88fe` by
   anchoring each rewrite on the actual `:root{…}` and `#scr.enlarged{…}` spans
   instead of on match order. **Any script that edits one of the two blocks must
   anchor on the block, never on ordinal position.**

3. **Feelings and scents on edibles, topicals and drinks — parked** (Jack,
   2026-08-17: "ignore for now"). Don't pick this up without him. The other
   three shelves are done; these 138 products still carry the old vocabulary, so
   their chips fall back to generated SVGs while flower/concentrate/pre-roll
   show Jack's icons. The mismatch is visible side by side. Three separate
   problems:
   - **topicals use their own *form* as a taste** — `Roll-On`, `Lotion`,
     `Balm / Salve`. Always wrong; just never noticed. A topical arguably
     shouldn't carry a taste at all.
   - **drinks use the whole flavour string** as one value (`Blackberry Lemonade`,
     `Mojo-Rita`) — product names, not descriptors.
   - **edibles use raw flavour words** (Cream, Gas, Candy, Lemon), most of which
     map cleanly onto the 16.

   These sheets have no terpene columns, so they can't use `terpmap`. Either add
   terpenes, or map their existing flavour/effect columns onto the 30 terms.
   Offered but not built: a remapping sheet listing all ~120 old values with a
   proposed new term and product counts, so Jack reviews 120 rows instead of 138
   products.
4. **The drawer's Brands facet matches almost nothing.** `BRANDS` lists
   `Artizen · Freddy's · Royal Tree · Saints · Skörd · St. Ideal` and `match()`
   compares it to `p.b` exactly, but the catalog says `Royal Tree Gardens` and
   `Skord` (no umlaut), and carries no `Freddy's` or `St. Ideal` at all — so
   four of the six return zero products. (Freddy's is out of the home brand row
   as of 2026-08-18, but the drawer still offers it.) Found while wiring the
   calendar, which matches the same labels as a **prefix** and resolves 26
   flowers from three brands. Fix is either a prefix match in `match()` or a
   `BRANDS` list taken from the catalog; needs Jack's call on which brands
   should be offered.
5. **Four sub-bubbles have photos but no products**: `Rosin Coins`,
   `Full Melt Hash`, `Distillate Syringe`, `Dab Applicator` — one level down
   inside Rosin, Hash and Distillate. Every category itself is stocked,
   **Kief (6) and RSO (4) included** — an earlier note claiming those two were
   empty was wrong (Jack, 2026-08-17; see `design-decisions.md`).
6. **The product page's back button is the one control Enlarged misses.**
   Found by `enlarged-check.js` on 2026-09-03; **not fixed — Jack's call.**

   `#scr.enlarged` carries an explicit list of small icon controls that take
   `min-height/min-width: var(--target-size)` in Enlarged — `.tabs button`,
   `.sbar .bk`, `.qty button`, `.fsclose`, `.sw`, `.acav`, `.fcard .fsz`,
   `.fszs button`. **`.pihead .pihback` is not in it**, and has no
   `#scr.enlarged` rule anywhere, so it stays at its hard-coded
   `width:26px;height:26px` in both modes while the screen around it doubles.
   Its sibling `.sbar .bk` grows 24 → 30.7px.

   Consequence: on a 393×852 phone in full screen it renders at **23px**, under
   WCAG 2.5.8's 24px minimum — the only control in the app that misses it — and
   on the product screen in Enlarged it is visibly the one thing that didn't
   grow. The fix is to add it to that enumeration (its comment already states
   the intent: small icon controls get the target size in Enlarged). Left
   unapplied because it changes the app and needs a rebuild, both guards, and a
   republish.

7. **One open question for Jack**, flagged where it lives: the **four deal
   flowers** are his brands but my strain picks (`DEALS` in
   `gen_catalog_products.py`, one line each to swap).

   *The Filter-pill contrast question is closed* (2026-08-20): Filter now uses
   Origins U's Search olive `#555624` at 7.66:1, clearing AA and AAA. The
   `#5C7540` drop-in that was earmarked for it is no longer needed.

### Done in this pass (2026-08-17 → 18)

| | |
|---|---|
| Home deals | Four flowers nominated in `DEALS`; 2-for-$50 mixes and matches across the whole bag; brand tiles matched to the product tiles; Torus replaced Freddy's; a See All card per row opens the whole deal |
| Deals Calendar | New screen from both hero buttons — seven deals on a four-week rota, two a week, **running now** then a month of upcoming, each with a generated run-out date and a product dropdown |
| Drinks | Bubble path built from `WA_Drinks_IA_Condensed.xlsx`; the size facet lists real volumes derived from the catalog |
| Kief / RSO | The "no products" note was wrong — the sheet has all 60 concentrate rows |
| Chrome | Brown title bar on every screen; trolley icon over Cart; "Your Cart"; Origins U photos wired to images the build actually embeds |
| Buttons | The outlined family, one weight pill app-wide, hero type at the app's own size, Logout matched to Account Settings |
| Advanced Settings | New screen: **Use product type**, **Enlarged view** and **Reduce motion** — all three working (Enlarged view landed 2026-08-20) |

*Size as a navigation step was considered and rejected* (Jack, 2026-08-12):
size lives in the product tile, not the filter path. Don't re-propose it.

### Done since (2026-08-20 → 09-02) — the accessibility pass

| | |
|---|---|
| Enlarged view | Rebuilt from `zoom:1.25` into a **token layer**: 49 distinct font sizes, 204 declarations, all `--fs-*` tokens, overridden once in `#scr.enlarged`. Reflow rules sit beside them — one card across, names wrap, metadata stacks |
| The curve | Anchored to the container, not chosen in isolation: a card goes 198→409px, so a type curve tuned on its own shrinks everything *relative to its card*. `ratio.js` measures each element as a % of its card in both modes |
| Flattening | Then flattened to a near-uniform ~22px (Jack's call: in this mode legibility beats hierarchy). Hierarchy now comes from weight and colour, not size |
| Punch list r1 | Lifestyle badge, bell/gear rings, the Advanced Settings switch itself (not just its hit box), Origins U title/Search/tiles |
| Punch list r2 | Hours spans sized to their content, tab bar (icons 34px, label 15px, one line), Filter/Sort back on one row at 20px, strain name 32px |
| Cart badge | Option B, the soft pill — rounded rect with a white keyline, lifted clear of the trolley. Enlarged only; Standard keeps its 16px circle |
| Standard regression | Six enlarged values leaked into `:root` via `re.sub(count=1)`; fixed by anchoring on the blocks. See next steps §2 |

*`zoom` was tried first and lost* (2026-08-20): it magnified decoration along
with content, grew every gap equally whether it needed it, and shrank the
layout's coordinate space exactly when the content got bigger. Don't re-propose
it.

---

## Repo layout

```
reference/origins/
├── hifi-build/
│   ├── origins-app.src.html      ← THE app (markup + CSS + JS + product data)
│   ├── asm_app.py                ← build: inlines fonts + images -> one HTML file
│   ├── gen_catalog_products.py   ← flower products from the .xlsx
│   ├── gen_drinks.py             ← drinks from the .xlsx + drinks IA
│   ├── terpmap.py                ← terpenes -> feelings + scents
│   ├── ratio.js                  ← Enlarged guard: each element as a % of its card
│   ├── standard-guard.py         ← Enlarged guard: Standard must not move (run it)
│   ├── snapshot-guard.js         ← Enlarged guard: same, from computed styles
│   ├── enlarged-check.js         ← does Enlarged itself work (overflow/targets)
│   ├── xlsxread.py               ← the one xlsx reader they all share
│   ├── gen_concentrates.py       ← concentrates from the .xlsx
│   ├── gen_edibles.py            ← edibles from the .xlsx + filter IA
│   ├── gen_prerolls.py           ← pre-rolls from the .xlsx
│   ├── gen_topicals.py           ← topicals from the .xlsx (+ 3 authored rows)
│   ├── gen_holistic_logo.py      ← generates the Holistic lifestyle logo
│   └── origins-case.src.html     ← case-study page, built by asm_case.py
├── product info/                 ← Jack's source data (.docx/.xlsx)
├── assets/
│   ├── product assets/           ← photos by category (Concentrate has sub-folders)
│   ├── Lifestyle logos/          ← the six lifestyle logos
│   ├── Various Brand Logos/      ← Royal Tree, Saints, Torus, Skord (+ Freddy's, unused)
│   └── origins logos/, scents assets/, …
├── hifi-final/                   ← Jack's Figma frames (the source of truth)
└── HANDOFF.md                    ← older handoff, still has useful frame notes
site/                             ← the Astro portfolio site (the umbrella project)
docs/                             ← you are here
```

`origins-app.src.html` is one big file by design — it assembles into a single
portable HTML artifact with no external requests.

---

## Regenerating product data

Each generator prints rows to stdout; splice them over the matching block in
`origins-app.src.html`, then rebuild. The rows for one type are contiguous.

```bash
python3 reference/origins/hifi-build/gen_topicals.py > /tmp/topicals.txt
# replace the {t:"topical"…} lines in origins-app.src.html, then:
python3 reference/origins/hifi-build/asm_app.py
```

**Flower regenerates like everything else now** — the old "don't regenerate
flower" warning is retired. It existed because photos were drawn sequentially
from a shuffled pool, so inserting one product reshuffled every photo after it.
Photos are now chosen by hashing the strain name against a pool scoped to that
strain's type, so a strain keeps its photo across rebuilds and row order doesn't
matter.

**Regenerating flower is in fact how you change the deal line-up**: `DEALS` in
`gen_catalog_products.py` decides which four rows carry `sale:1`, and the
generator refuses to emit if a nomination stops matching exactly one row, or if
a nominated eighth is at or under the $25 deal price.

---

## Gotchas

- **The artifact URL is stable.** Republish with `url=` to keep it; a new path
  mints a new URL.
- **Empty cells shift rows two different ways.** Excel omits some empty cells
  entirely (a reader appending in document order shifts every column after a
  blank — this is why a sheet once parsed with `Cannabinoid Combo` landing in
  `Effect Filter`), *and* writes others self-closing, `<c r="E2" s="29"
  t="str"/>`. A cell regex that tries the open-tag branch before the
  self-closing one reads `<c …/>` as an open tag and swallows the next cell's
  value — the same shift, but silent even when you address by column letter.
  Address by letter **and** match the self-closing branch first. Copy the reader
  in `gen_prerolls.py`; the other three now match it.
- **Sectioned sheets carry `=== SECTION ===` rows.** Filter them out or they
  parse as products.
- **Don't trust a "this sheet is malformed" note without re-checking it.** The
  pre-roll catalog was documented for two days as having columns that didn't
  match its own header. It doesn't — that was the self-closing-cell bug above,
  and `gen_prerolls.py` had been written to compensate for it. Both are fixed
  and the emitted products never changed. If a sheet looks shifted, parse it
  with `xml.etree` first and compare before writing code around it.
- **Don't publish with missing photos.** The build still succeeds when assets are
  gone (WARN + blank tiles) — check the WARN lines before publishing.
- **Jack sometimes uploads an older `origins-app.src.html`** alongside his data
  files via the GitHub web UI, which silently reverts work. Diff before rebasing;
  it happened once and was caught.
- **Copy address can't be verified from a build container.** The About Us copy
  control tries `navigator.clipboard` and falls back to an offscreen textarea +
  `execCommand`; both branches are tested locally (including with the Clipboard
  API removed and with `writeText` rejecting), but which one the *published*
  artifact takes depends on the iframe's permission policy, which isn't visible
  from outside the frame. The published page can't be clicked from here — it's
  behind claude.ai auth and WebFetch only reads HTML. Ask Jack to tap it once.
  If the toast shows the address instead of "Address copied", both branches were
  blocked and the fallback is to render the address in a selectable `<input>`.
- **Git drops empty directories.** Every asset folder has a `README.md` so the
  structure survives deleting its photos (learned the hard way with `Rosin/`).
- **A lifestyle word is only ever printed by `lifeLabel(key)`.** Print `FEEL[k]`
  directly and Advanced Settings' *Use product type* switch won't reach your
  screen. The Guide Me wizard is the exception that proves it: its lifestyle
  words are *wordmark images*, so each option carries a text twin that CSS swaps
  in.
- **A fixed height inside a `.dealrow` stretches every product tile in it.**
  Flex rows default to `align-items:stretch`, so a brand or See All card with
  its own height drags the tiles up to meet it — that shipped once, 40px too
  tall. Let them stretch; only the brand row, which has no product tile to set
  the height, is measured.
- **A hidden screen measures zero.** Anything that sizes itself from a rendered
  element has to run when its screen is actually on (`nav()`), not at load.
- **`.s` and `.empty` are global CSS classes** — `.s{display:none}` in
  particular. Namespace anything new (the size sheet uses `fs*`), or it vanishes
  silently.
- **Build takes ~2 min** since the WebP encode; run it in the background.
- **`re.sub(pattern, repl, css, count=1)` edits the wrong block.** The Standard
  tokens (`:root`) come *first* in the stylesheet and the Enlarged overrides
  (`#scr.enlarged`) second, so a first-match rewrite aimed at Enlarged lands on
  Standard. Anchor on the block's own `{…}` span. This shipped once; six
  Standard font sizes silently took enlarged values.
- **A tooling script that isn't committed is gone.** Containers are reclaimed,
  and `standard-guard.py`, `std_before.json`, `snapshot.js` and `coverage.js`
  were written, used, documented as required — and never added to git.
  Both have since been rewritten and committed as `standard-guard.py` and
  `snapshot-guard.js`, each deriving its baseline from `cc6edad` rather than
  from a captured file, so neither can be lost that way again. Commit any guard
  you write, and prefer a baseline git can regenerate over one you store.
- **A verification claim in these docs is only as good as the script behind
  it.** "Standard is provably untouched" was written from a snapshot run whose
  script no longer exists, and the regression above landed after it. Re-run the
  check yourself before repeating the claim.
- **The cart badge is not an icon.** It was swept into the generated
  icon-scaling pass *and* the round-1 punch list, so two rules fought over it
  and it grew to 34px, sitting on top of the trolley it belongs to. It is sized
  on its own rule now; keep it out of any bulk icon selector.
