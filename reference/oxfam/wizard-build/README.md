# oxfam wizard build

Builds the Contact-Us wizard prototype from Jack's own lo-fi mockups
(`../lofi`, `../photos`, `../logos`) — separate from `../hifi-build`, which is
a carbon-copy recreation of the real Oxfam Australia site for the case study.

**One file, one artifact.** `wizard.src.html` holds every built screen
(Landing/Contact Us, FAQ, Feedback) as `<section class="screen" data-screen="...">`
blocks, toggled by `nav(id)` in the bottom `<script>` -- not three separate
files/artifacts. Add a new screen by appending another `.screen` section and
wiring its Quick Link / nav entry point to `nav('newid')` instead of
`toast('Coming soon')`.

- `wizard.src.html` -- markup + CSS + JS for every screen, with %%HERO_IMG%%,
  %%MAP_IMG%%, %%FAQ_IMG%%, %%FEEDBACK_IMG%%, <!--LOGO--> and /*FONTS*/ markers
- `asm_wizard.py` -- embeds fonts, photos, and the traced logo SVG once each;
  needs Pillow. Run from repo root:
  `python3 reference/oxfam/wizard-build/asm_wizard.py`
- `fontcache/` -- Oswald + Open Sans woff2s, fetched once so later builds work
  offline

Anything that links to a screen that isn't built yet calls `toast('Coming
soon')` (header nav, Donate/Login, social icons, most footer links, FAQ's
Quick Links/Popular Topics) rather than doing nothing silently -- flip it to
`nav('id')` once that screen exists. Header logo click and footer's
FAQs/Contact us links already route through `nav()`.

Each screen still gets built and signed off one at a time, same as the
Origins prototype -- it just lands in this one file instead of a new one.
Dynamic interactions beyond screen-to-screen nav (dropdowns, FAQ accordion,
a real chat panel) come later.
