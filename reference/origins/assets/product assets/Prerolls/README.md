# Prerolls

Pre-roll photos, one per type family × pack count.

## Image keys used by the app
| Image key | What it is | File |
|---|---|---|
| `preroll` | generic joint — category circle + Guide Me method icon | `Pre-roll Flower Single Background Removed.png` |
| `pr_flower` | flower joint, 1-pack | `Pre-roll Flower Single Background Removed.png` |
| `pr_flower_2pk` | flower joints, 2-pack | `Pre-roll Flower 2-pack.webp` |
| `pr_flower_3pk` | flower joints, 3-pack — **wired but unused** | `Pre-roll Flower 3-pack Background Removed.png` |
| `pr_flower_20pk` | flower joints, 20-pack | `Pre-roll flower 20-pack.webp` |
| `pr_infused` | infused joint, 1-pack | `Pre-roll infused Single Background Removed.png` |
| `pr_infused_2pk` | infused joints, 2-pack | `Pre-roll infused 2-pack Background Removed.png` |
| `pr_trifecta` | trifecta joint | `Pre-roll Trifecta Single Background Removed.png` |

`pr_flower_3pk` has no product in the current catalog — nothing in the 50 is a
3-pack — but it stays mapped so a 3-pack product picks it up with no code change.

These filenames don't match the `<image key>.png` convention, so they're listed
explicitly in the `M` and `NOBG` maps in
`reference/origins/hifi-build/asm_app.py`. Every one of them carries alpha
(including the two `.webp` files), so they all take the `embed_rgba` path.

**Naming:** name a file exactly `<image key>.png` and the build picks it up
automatically — no code change. Anything else needs pointing at in the `M` /
`NOBG` maps.

Background-free cut-outs are preferred; a white-background original works as
a fallback.

---
*Keep this README — it's what keeps the folder in git. An empty folder disappears from GitHub.*
