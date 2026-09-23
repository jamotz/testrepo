# oxfam wizard build

Builds the Contact-Us wizard prototype from Jack's own lo-fi mockups
(`../lofi`, `../photos`, `../logos`) — separate from `../hifi-build`, which is
a carbon-copy recreation of the real Oxfam Australia site for the case study.

**One file, one artifact.** `wizard.src.html` holds every built screen as
`<section class="screen" data-screen="...">` blocks, toggled by `nav(id)` in
the bottom `<script>` -- not separate files/artifacts. Add a new screen by
appending another `.screen` section and wiring its Quick Link / nav entry
point to `nav('newid')` instead of `toast('Coming soon')`.

Built screens (`data-screen` id): `landing` (Contact Us), `faq`, `feedback`,
`fundraising`, `media`, `report`, `myoxfam-signin`, `portal`. `myoxfam-signin`
has no lo-fi mockup behind it -- built to match the established panel
language (green side + white form, same shape as Contact Us Directly)
rather than copied from a frame; mock-authenticates straight into `portal`
on submit, and `portal`'s "Log out" returns to it.

- `wizard.src.html` -- markup + CSS + JS for every screen, with %%HERO_IMG%%,
  %%MAP_IMG%%, %%FAQ_IMG%%, %%FEEDBACK_IMG%%, %%YOUTUBE_IMG%%, %%EVENT1_IMG%%,
  %%EVENT2_IMG%%, %%FB_COVER_IMG%%, %%FB_AVATAR_IMG%%, %%EXPERTS_IMG%%,
  %%CONTACT_IMG%%, %%REPORT_IMG%%, %%PORTAL_IMG%%, <!--LOGO--> and /*FONTS*/
  markers
- `asm_wizard.py` -- embeds fonts, photos, and the traced logo SVG once each
  (some via `embed_crop`/`embed_crop_square` -- a few source photos, e.g. the
  Facebook cover, bake in more than the mockup wants shown, so the build
  crops rather than the whole file); needs Pillow. Run from repo root:
  `python3 reference/oxfam/wizard-build/asm_wizard.py`
- `fontcache/` -- Oswald + Open Sans woff2s, fetched once so later builds work
  offline

Media Contacts (on `media`) reuses the same headshot photo for both Lily
Partland and Lucy Brown -- only one was ever supplied despite asking; swap in
a second via `%%CONTACT_IMG%%`'s second use in `wizard.src.html` if one shows
up.

Anything that links to a screen that isn't built yet calls `toast('Coming
soon')` (top nav, Donate, social icons, most footer links, FAQ's Quick
Links/Popular Topics, Fundraising's buttons/events/Follow Us, Media's topic
pills/Our Experts, Report's policy buttons, Portal's account rows/tiles)
rather than doing nothing silently -- flip it to `nav('id')` once that
screen exists. Header logo, Login, FAQs/Media/Contact-us footer links, and
every landing Quick Link that has a built destination already route through
`nav()`.

Each screen still gets built and signed off one at a time, same as the
Origins prototype -- it just lands in this one file instead of a new one.
Dynamic interactions beyond screen-to-screen nav (dropdowns, FAQ accordion,
a real chat panel, portal accordions actually collapsing) come later.
