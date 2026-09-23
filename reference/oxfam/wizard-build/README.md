# oxfam wizard build

Builds the Contact-Us wizard prototype from Jack's own lo-fi mockups
(`../lofi`, `../photos`, `../logos`) — separate from `../hifi-build`, which is
a carbon-copy recreation of the real Oxfam Australia site for the case study.

- `landing.src.html` — markup + CSS for the landing screen, with %%HERO_IMG%%,
  %%MAP_IMG%%, <!--LOGO--> and /*FONTS*/ markers
- `asm_landing.py` — embeds fonts, photos, and the traced logo SVG; needs
  Pillow. Run from repo root:
  `python3 reference/oxfam/wizard-build/asm_landing.py`
- `fontcache/` — Oswald + Open Sans woff2s, fetched once so later builds work
  offline

Each screen gets built one at a time and signed off before moving to the
next, same as the Origins prototype. Dynamic interactions (nav dropdowns,
FAQ accordion, chat panel) come after every screen is built as a static
page.
