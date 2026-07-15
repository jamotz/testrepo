# oxfam hi-fi build

Regenerates the static high-fidelity Oxfam case-study artifact.
- `oxfam-hifi.src.html` — markup + CSS with %%IMG_*%%, /*FONTS*/, <!--LOGO--> markers
- `asm_hifi.py` — resizes/base64-embeds reference images + fonts + logo (needs Pillow)
- `sheet.py` — builds labeled contact sheets of the reference images

Run from repo root: `python3 reference/oxfam/hifi-build/asm_hifi.py` (paths inside
point to /tmp scratchpad for output; adjust as needed). Then publish the HTML as an Artifact.
