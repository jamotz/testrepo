# Product assets

Product photos, filed by category. **Concentrate is the only folder with
sub-folders** (one per category from the "Concentrate Categories and filters"
doc); everything else is flat.

```
product assets/
├── Concentrate/
│   ├── Distillate/
│   ├── Live Resin/     (incl. badder, sugar and diamond/THC-A shots)
│   ├── Rosin/
│   ├── Kief/
│   ├── Hash/
│   ├── RSO/            (empty — no assets yet)
│   └── Concentrate Multi.jpeg   (general shot, no single category)
├── Flower/
├── Edibles/
├── Prerolls/
├── Topicals/
└── Vapes/
```

## Background-free photos
Cut-out photos sit **next to** their originals in the same category folder,
named `… Background Removed.png`, so both versions of a product live together.
The app prefers the background-free version wherever one exists and falls back
to the white-background original.

## Adding photos
Drop the file into the right category folder, then point the product key at it
in `reference/origins/hifi-build/asm_app.py`:

- **`M`** — source path per image key (the white-background original).
- **`NOBG`** — the background-free file for that key, preferred when present.
  A file named exactly `<key>.png` anywhere in this tree is picked up
  automatically with no code change.

Re-run `python3 reference/origins/hifi-build/asm_app.py` after any change — it
prints a `WARN` line for any path it can't resolve.

## Notes
- `Flower/Full Bud No background.webp` is the **Growing Process** education card
  (`growbud`); `Flower/No bg - Flower bud …` is the `gdp` product photo.
- The four `bud1`–`bud4` photos in `Flower/` are spread at random across the
  catalog's flower products.
- Cut-outs should have a real alpha channel and be trimmed to the product edge —
  leftover white halos are the thing to avoid. Any resolution is fine; the build
  downsizes to ~400px wide.
