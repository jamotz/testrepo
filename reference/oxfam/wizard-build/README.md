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
`fundraising`, `media`, `report`, `myoxfam-signin`, `portal`,
`create-account`. `create-account` mirrors its lo-fi mockup (`../lofi/Create
an Account.png`) -- title bar + green-side bullet list + white form. Only
`myoxfam-signin` has no mockup behind it; it was built to match the
established panel language (green side + white form, same shape as Contact
Us Directly) rather than copied from a frame. Both mock-authenticate
straight into `portal` on submit; `portal`'s "Log out" returns to
`myoxfam-signin`, and its "Create one" link goes to `create-account`.

- `wizard.src.html` -- markup + CSS + JS for every screen, with %%HERO_IMG%%,
  %%MAP_IMG%%, %%FAQ_IMG%%, %%FEEDBACK_IMG%%, %%YOUTUBE_IMG%%, %%EVENT1_IMG%%,
  %%EVENT2_IMG%%, %%FB_COVER_IMG%%, %%FB_AVATAR_IMG%%, %%EXPERTS_IMG%%,
  %%CONTACT1_IMG%%, %%CONTACT2_IMG%%, %%REPORT_IMG%%, %%PORTAL_IMG%%,
  %%ACCOUNT_IMG%%, <!--LOGO-->, <!--SIGNIN_LOGO--> and /*FONTS*/ markers
- `asm_wizard.py` -- embeds fonts, photos, and the traced logo SVG once each
  (some via `embed_crop`/`embed_crop_square` -- a few source photos, e.g. the
  Facebook cover, bake in more than the mockup wants shown, so the build
  crops rather than the whole file); needs Pillow. Run from repo root:
  `python3 reference/oxfam/wizard-build/asm_wizard.py`. Besides the artifact
  fragment, it writes the same build as a standalone page to
  `site/public/work/oxfam/proto.html` -- the portfolio case study's
  "Explore the prototype" iframe -- so rebuild the site (`cd site && npm ci &&
  npm run build`) and commit `site/dist/` after any wizard change
- `fontcache/` -- Oswald + Open Sans woff2s, fetched once so later builds work
  offline

MyOxfam Sign In, Create an Account and Report have no hero -- just their
cards under the header (Create an Account's Submit is centered). Report puts
its form first, with the whistleblower-protection paragraph in the green
side, and the "Why Do We Want to Know?" policy band below it. `%%ACCOUNT_IMG%%` (`Create an account.jpeg`) now backs Media
Inquiries' split photo hero instead; `#screen-media .hero .txt` is narrowed
to 38% so its longer subtitle stays inside the green wedge.

Media Contacts (on `media`) now uses two distinct headshots -- Lily Partland
(left, `%%CONTACT1_IMG%%`) gets `Media Contact Headshot 1.png`, Lucy Brown
(right, `%%CONTACT2_IMG%%`) keeps `Media Contact Headshot 2.png`.

MyOxfam Sign In's card is a plain flex column (`.signin .form{display:flex;
flex-direction:column}`), not a grid -- the `.contact .form` grid this panel
otherwise reuses has `.submit{grid-column:2}` for its landing/feedback/report
layout, and mixing that grid-column with a 1-column grid-template silently
creates a 2nd implicit column (fields end up side by side) with no visual
cue why. Flex sidesteps it entirely: email, password, the Sign In button,
and the "Create one" link stack top to bottom in DOM order, with
`.signin .form .submit{align-self:center}` centering the button (overriding
the `align-self:end` it would otherwise inherit from `.contact .form
.submit`, which still applies in flex) instead of stretching it full width. This
screen has no hero -- just the card, centered under the header -- and its
green `.side` leads with the white-recolored stacked Oxfam logo
(`<!--SIGNIN_LOGO-->`, built from `oxfam-logo-stacked.svg` with its fill
swapped to `#ffffff` at build time -- see `asm_wizard.py`) above "Welcome
Back".

Anything that links to a screen that isn't built yet calls `toast('Coming
soon')` (most header dropdown items, Donate, social icons, most footer
links, FAQ's Quick Links, Fundraising's buttons/events/Follow Us, Media's
topic pills/Our Experts, Report's policy buttons, Portal's individual
account/donation/event links) rather than doing nothing silently -- flip it
to `nav('id')` once that screen exists. Header logo, Login, a few header
dropdown items, FAQs/Media/Contact-us footer links, and every landing Quick
Link that has a built destination already route through `nav()`.

**Dynamic interactions (built):**
- Header nav dropdowns (`.nav-item`/`.dropdown`, `toggleDropdown()`) -- one
  open at a time, closes on an outside click or on `nav()`
- FAQ Popular Topics accordion (`.topic-row`, `toggleTopic()`) -- any number
  open at once, answers cross-link to other screens via `nav()`
- Chat panel (`#chatPanel`, `toggleChat()`/`sendChatMessage()`) -- a real
  mock conversation: greeting on open, typed messages get a canned reply
  after a short delay
- Portal's My Account/Donations/Volunteering groups (`.pgroup`,
  `togglePortalGroup()`) -- each collapses/expands independently, open by
  default to match the mockup

Each screen still gets built and signed off one at a time, same as the
Origins prototype -- it just lands in this one file instead of a new one.

**Visual-polish pass (large edit list, done in one go):** header logo
recolored to `--green` (`#4d5a2b`, was a bright placeholder `#75C044`);
every text-entry/account box (`.contact` and its `.signin`/`.acct-card`
variants, `.newsletter`, `.portal-body`) now carries a 2px `--green`
outline; the FAQ newsletter panel and Fundraising's "How to Get Started"
block had their one-off extra margins removed so section spacing is
consistent everywhere; `.title-band` (the plain-text hero used by FAQ,
Fundraising, Media, Report, MyOxfam Sign In) is now sized and colored to
match the photo heroes, with centered white text. Per-page: landing's
Contact Us Directly panel got the required privacy disclaimer; Feedback's
hero photo is recentered so faces aren't cropped out; MyOxfam Sign In is
now a single narrow vertical card instead of a wide side-by-side split;
Create Account's hero text box was narrowed so it no longer runs outside
the green wedge onto the photo; Fundraising's Learn More button lost its
force-stretched full-width style, its video thumbnail now shows with
`object-fit:contain` instead of being cropped, and the block got top/bottom
divider lines; Media's topic pills are all one fixed height, "Australian
Government"/"Obama and Yemen" were renamed to "AUS Government"/"Climate
Change", Our In-House Experts was pushed further down to match the MVP's
layout, and the two Media Contacts headshots are now distinct people
(`Media Contact Headshot 1.png` / `Media Contact Headshot 2.png`).
