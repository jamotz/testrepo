# Product photos — no background (transparent)

Drop **background-free (transparent PNG)** product photos here. When a file in
this folder matches a product key below, the build (`asm_app.py`) uses it
automatically **instead of** the white-background version in `../product assets/`.
Nothing here yet = the app keeps using the current images, so it's safe to add
them one at a time.

## How to name the files
Name each file exactly `<key>.png` from the table below (lowercase, `.png`).
The key is what the app maps images by — matching the name is what wires it in.

| Filename to add | Product | Currently sourced from |
|-----------------|---------|------------------------|
| `flower.png`    | Flower bud | `product assets/flower.png` |
| `gdp.png`       | Flower plant/bud — **Growing Process** card (⭐ highest priority: this one can't be auto-cut) | `product assets/Unproccessed Flower.jpeg` |
| `preroll.png`   | Pre-roll joint | `product assets/preroll.png` |
| `rosin.png`     | Rosin concentrate | `product assets/Concentrate (Rosin).png` |
| `liveresin.png` | Live resin concentrate | `product assets/Live Resin.jpeg` |
| `sugar.png`     | Sugar concentrate | `product assets/Sugar.webp` |
| `badder.png`    | Budder / butter concentrate | `product assets/Butter Concentrate.png` |
| `distillate.png`| Distillate (optional — otherwise reuses `badder`) | `product assets/Butter Concentrate.png` |
| `thca.png`      | THC-A crystals | `product assets/THC-A Crystals.png` |
| `hash.png`      | Hash | `product assets/hash.jpeg` |
| `keif.png`      | Kief | `product assets/keif.jpeg` |
| `gummy.png`     | Gummy edibles | `product assets/Gummy Edibles.png` |
| `choc.png`      | Chocolate edible | `product assets/Chocolate Edible.png` |
| `topical.png`   | Topical | `product assets/topical.png` |
| `vape.png`      | Vape cartridge | `product assets/vape.png` |

## Requirements
- **Format:** PNG with a real alpha channel (transparent background), not white.
- **Trim fully:** remove the white all the way to the product edge — leftover
  white halos are exactly what we're trying to avoid.
- **Any resolution is fine** — the build downsizes to ~400px wide.

## After adding files
Re-run the build and the new images flow through the whole app (deal cards,
product info, shop, and the Origins U cards). For the Origins U cards
specifically, a clean cutout here lets us drop the auto-removal step entirely —
tell me once files are in and I'll finish wiring that.
