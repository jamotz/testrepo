# Drinks

Drop drink photos here. **Nothing lives in this folder yet** — the catalog
(`WA_Liquid_Edibles_50_Product_List_With_Strain_Type.xlsx`, 50 products across 7
brands) is in, so photos are the last thing drinks need before they can be built.

Until then the one legacy drink in the app reuses a gummy shot (`img:"gummy2"`),
which is why the shelf can't ship as-is.

## Image keys used by the app

One photo per **Type**, which is the IA's second filter level. Counts are what
the catalog actually contains:

| Image key | What it is | Products |
|---|---|---:|
| `drink` | generic beverage — the Drinks **category circle** on the shop screen | — |
| `dr_drink` | full-size beverage / bottle (12 oz, 16 oz) | 20 |
| `dr_shot` | small dose shot (2 oz) | 11 |
| `dr_seltzer` | can, sparkling (12 oz) | 8 |
| `dr_sorbet` | frozen sorbet tub | 6 |
| `dr_honey` | honey jar or squeeze bottle | 5 |

`drink` is the only one the app already asks for — it's in the `circles` list in
`origins-app.src.html`. The five `dr_*` keys are what the generator will reach
for once it exists.

## The IA these come from

`WA_Drinks_IA_Condensed.xlsx`: **Drinks → THC / CBD / Blend → Drink / Shot /
Seltzer / Sorbet / Honey.** The cannabinoid branch is the same first level the
pre-rolls use, so drinks reuse the same bubble component; the second level is
the Type, which is what these photos key on.

Size is a Filter-drawer facet, not a bubble level — the catalog runs 2 oz,
4 oz, 6.7 oz, 12 oz and 16 oz, and no product exists in more than one.

**One photo per Type is enough.** Don't shoot per flavour: the catalog carries
42 distinct flavours across 50 products, and the tile already states the flavour
in the product name. This mirrors how Prerolls works — one shot per type family,
not per strain.

## Naming

Name a file exactly `<image key>.png` and the build picks it up automatically —
no code change. Anything else needs pointing at in the `M` / `NOBG` maps in
`reference/origins/hifi-build/asm_app.py`.

Background-free cut-outs are preferred; a white-background original works as a
fallback. Photos with real alpha take the `embed_rgba` path (WebP q86), so a
`.webp` is fine here too.

---
*Keep this README — it's what keeps the folder in git. An empty folder disappears from GitHub.*
