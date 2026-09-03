# Portfolio Redesign — Handoff / Continuation Notes

> **⚠ This file is the portfolio *site* handoff, and it is behind.**
> The branch it names below, `claude/portfolio-redesign-81crin`, is **superseded** —
> checking it out loses every later round of work. Current branch:
> **`claude/accessibility-handoff-review-dhabtz`**.
>
> Active work is the **Origins app prototype**, and its handoff is
> **[`docs/project-handoff.md`](docs/project-handoff.md)** — start there, with
> [`docs/architecture.md`](docs/architecture.md) and
> [`docs/design-decisions.md`](docs/design-decisions.md) beside it.
> What follows is still accurate about the Astro site's design direction and the
> case-study structure; treat its branch name and "Next steps" as history.

Quick-start for a new session. Read this, then continue. Everything described as
"built" is committed on branch `claude/portfolio-redesign-81crin` under `site/`.

## Project
Redesign of Jack Motzkin's UX portfolio (jackmotzkin.com, hosted on Hostinger).
Owner is a junior **UX Researcher & Designer** looking to get hired.

## Design direction — "Kinetic Oversized"
- **Dark-first**, technical/editorial. Cursor-reactive **background grid** that lights
  up a gold "lantern" ~40px around the pointer (canvas, `src/scripts/motion.js`).
- Oversized **Space Grotesk** display; **IBM Plex Sans** body; **IBM Plex Mono** labels
  (mono nods to his IBM Data Science cert). Self-hosted woff2 in `site/public/fonts`.
- Real **MOTZ wave logo** in `site/public/brand/` (+ `favicon.svg`).
- **Light/dark toggle** in nav (sun/moon), dark is the default, persisted via
  `localStorage['motz-theme']`, no-flash inline script in `Base.astro`.
- Landing-page accent = **gold**. Each case-study page uses its **own accent** via
  `<Base accent="oxfam|origins|premier">` → `data-accent` on `<html>` → token overrides
  in `global.css`. Oxfam=green, Origins=amber, Premier=blue (light + dark variants defined).

## Stack / build / deploy
- **Astro + GSAP + Lenis**, static output. `cd site && npm install && npm run build`
  → `site/dist/`. Upload `dist/` contents to Hostinger `public_html/`.
- Contact form: client validation + **mailto fallback** (upgrade to Web3Forms — see
  `Contact.astro` comment). Owner is fine keeping a simple "Get in touch" button.

## Built & pushed
- Landing page: `Nav`, `Hero`, `Work` (3 project cards), `About`, `Contact`, `Footer`.
- Light/dark toggle across the system.
- `/work/oxfam` case-study page (green accent) — CURRENT version uses an OLD section
  order; see "Next steps" to update it to the recruiter-optimized spine below.

## Case-study structure — AGREED (recruiter-optimized)
Order to build every case page in:
1. **Summary** — title, **My role** (explicit), **Outcome in one line + "See results ↓"**
   jump link, meta (role/client/location/engagement), hero image slot.
2. **Problem overview**
3. **Research approach** (method cards)
4. **Design decisions** (+ IA/artifact image)
5. **Design format & iteration** (wireframes → v2 → visual; image slots)
6. **Testing insights**
7. **Results** (metrics OR before/after + quotes — both count for a junior)
8. **Reflection** (learned / would change / growing — maturity signal)
9. **High-fidelity prototype** — embed slot for a **Figma** prototype (owner may want an
   interactive "site-within-a-site"; iframe embed or clickable image walkthrough).

Reference for the exact static templates (both themes) — all three case studies
share this 9-section spine:
- Oxfam (green): https://claude.ai/code/artifact/0ee77719-44c0-4936-9399-f4694ca3c675
- Origins (amber): https://claude.ai/code/artifact/4276cca8-22bc-4ba0-b536-a5fa21d82dc3
- Premier (blue): https://claude.ai/code/artifact/e57494f4-247e-4b18-9d66-430e0bba60c0

### Per-project variation (approved: "same bones, project-appropriate details")
Keep the 9-section spine identical for scannability; vary texture by project type:
- **Oxfam** (charity, web/portal) & **Origins** (cannabis app) use the default labels;
  Origins' section 9 prototype is a **phone/app frame**.
- **Premier** is a **CX / service** engagement — no app. It relabels section 4
  "Design decisions" -> **Recommendations**, section 5 -> **Service improvements**, and
  section 9 -> **Journey map & deliverable** (a Pack -> Store -> Clean -> Pack-back ->
  Return journey strip instead of a Figma prototype).

## Next steps (in order)
1. Fold the recruiter-optimized 9-section structure into the real Astro page
   `site/src/pages/work/oxfam.astro` (it currently has the earlier order).
2. Wire landing **Work cards → `/work/<slug>`** (currently they point to `#contact`)
   so page-to-page navigation works.
3. Replicate for **Origins** (`accent="origins"`, amber) and **Premier**
   (`accent="premier"`, blue) at `/work/origins`, `/work/premier`. Static templates
   for both already exist (see artifact links above) — port their content/labels into
   Astro. Premier keeps its CX relabels (Recommendations / Service improvements /
   Journey map & deliverable).
4. Drop in **real images**: owner will commit their downloaded site (or images) into
   a `reference/` folder; use those in hero/gallery/prototype slots.
5. Embed the **Figma prototype** in section 9 once the owner provides the link.
6. Replace `[Draft — …]` copy and metric placeholders with the owner's real content.

## Content source
Use content from the current site (captured from screenshots earlier: About/Brief/
Role/Client/Location per project + the bio/"My Background/Goals/Work" section). Owner
will provide images and any deeper copy. Do NOT invent metrics — use real evidence.

## Live reference artifacts (persist across sessions)
- Landing page (Kinetic, canonical): https://claude.ai/code/artifact/fb62ff96-edb1-4670-b9a0-28a104581b23
- Oxfam case-study template (recruiter-optimized): https://claude.ai/code/artifact/0ee77719-44c0-4936-9399-f4694ca3c675

## Environment note
Containers are ephemeral and reclaim on inactivity — **commit and push often**; don't
rely on `/tmp` or un-pushed files surviving between turns.

## Reference assets — UPLOADED (as of this note)
Oxfam source material is staged in `reference/oxfam/`:
- Button pages map top->bottom: page-01 FAQ, page-02 Feedback, page-03 MyOxfam,
  page-04 Fundraising, page-05 Media, page-06 Report (each folder has the page screenshot).
- Flow: Landing -> each button -> its page. Only tertiary: Landing -> MyOxfam ->
  MyOxfam Portal (Portal screenshot goes in page-03).
- `reference/oxfam/process/` — 26 mixed items (lo/mid-fi prototypes, stock photos,
  assets, Oxfam logos). Not pre-sorted; classify + place while building (view once).
- `reference/current-site/` — 6 screenshots of the existing jackmotzkin.com homepage
  (Top #1 -> Bottom #6).
Next: build /work/oxfam from the recruiter-optimized 9-section template, wire the
Landing->6-buttons->(MyOxfam Portal) flow as a clickable prototype in section 9,
place real images, and tighten copy to the layered/scannable format.
