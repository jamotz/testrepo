# Vapes

Drop vape photos here.

## Image keys used by the app
| Image key | What it is |
|---|---|
| `vape` | Vape cartridge |

**Naming:** every key has to be registered in the `M` map in
`reference/origins/hifi-build/asm_app.py` — there is no directory scan, so a
file dropped here is invisible to the build until it is named there. (The only
auto-pickup is `nobg_file()` trying `product assets/<key>.png`, which is the
*parent* folder, not this one.) An earlier version of this note claimed naming a
file `<image key>.png` was enough; it wasn't, and the shop's Vapes circle sat
empty because of it.

Background-free cut-outs are preferred; a white-background original works as a
fallback. **A cut-out also needs an `NOBG` entry**, or it goes through `embed()`,
which flattens the alpha onto white and saves a JPEG — you lose the cut-out.
`preroll` is the worked example: it appears in both maps.

---
*Keep this README — it's what keeps the folder in git. An empty folder disappears from GitHub.*
