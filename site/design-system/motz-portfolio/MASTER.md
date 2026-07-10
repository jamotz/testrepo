# Design System Master File — MOTZ Portfolio

> Generated with **ui-ux-pro-max** (`--design-system`, variance 7 / motion 8), then
> reconciled with the client-directed creative brief. The skill's structure, spacing
> scale, component patterns, motion rules, anti-patterns, and pre-delivery checklist
> are preserved; **Color, Typography, and Style are overridden below** to match the
> agreed direction (they take precedence over the skill's auto-picked defaults).

**Project:** MOTZ — Jack Motzkin, UX Researcher & Designer
**Direction:** Refined technical · dark-first · editorial-asymmetric grid · research "signal-map"
**Design Dials:** Variance 7/10 · Motion 8/10

---

## Global Rules

### Color Palette — "Day / Night" (Option 1)

Accent hue intentionally shifts between themes: **purple by day, gold by night.**
Neutrals are hue-biased (never pure #000/#fff). The three project colors are
*content* accents, scoped to case-study cards only — they are not brand colors.

| Role | ☀️ Light | 🌙 Dark | Token |
|------|----------|---------|-------|
| Background | `#FBFAFC` | `#08070C` | `--bg` |
| Surface / panel | `#FFFFFF` | `#111019` | `--surface` |
| Text | `#1A1725` | `#F3F1F6` | `--text` |
| Text soft | `#514B60` | `#B9B2C8` | `--text-soft` |
| Muted / meta | `#6C6579` | `#8C8399` | `--muted` |
| Border / grid | `#EAE7F1` | `#211E2C` | `--border` |
| **Accent** | `#6A48F0` purple | `#E7B24C` gold | `--accent` |
| Accent strong | `#5836C9` | `#F0C061` | `--accent-strong` |
| On accent | `#FFFFFF` | `#161009` | `--on-accent` |
| Signal / secondary | `#9E86FF` | `#F0C061` | `--signal` |
| Project · Oxfam | `#4E7A47` | `#7FB878` | `--oxfam` |
| Project · Origins | `#986213` | `#E7A93F` | `--origins` |

> All small-text pairs verified ≥ 4.5:1 (WCAG AA) via contrast audit; light accent/muted/Oxfam/Origins darkened from initial values to pass.
| Project · Premier | `#3A55B4` | `#7B95EA` | `--premier` |
| Destructive | `#DC2626` | `#F26D6D` | `--destructive` |

### Typography — "Developer Mono" (ui-ux-pro-max pairing)

- **Display / labels / meta:** `JetBrains Mono` (400/500/700) — technical, precise, code-adjacent; nods to the IBM Data Science cert.
- **Body / reading:** `IBM Plex Sans` (400/500/600) — humanist, highly legible at length.
- Self-hosted (no external requests). Mono set UPPERCASE with `letter-spacing: .04–.16em` for labels; body at 1.6 line-height, ≤68ch measure.
- Type scale (px): `12 · 13 · 15 · 18 · 22 · 30 · 44 · 68 · clamp hero`.

### Spacing (4/8 scale)

| Token | Value |
|-------|-------|
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 16px |
| `--space-lg` | 24px |
| `--space-xl` | 32px |
| `--space-2xl` | 48px |
| `--space-3xl` | 64px |

Radius: cards `16px`, pills `100px`, insets `10px`. Elevation is expressed with
**hairline borders + a single soft shadow**, not stacked drop-shadows.

---

## Style Guidelines — "Refined Technical" (override of skill's Cyberpunk default)

Not neon/glitch. The technical feel comes from **structure and precision**, not effects:

- **Visible grid system:** hairline column rules, a fixed left "spine" with monospace section indices (`01 · 02 · 03`), coordinate/label ticks.
- **Monospace meta everywhere:** eyebrows, locations, stats, status readouts, footer.
- **Signature interaction — Research Signal-Map:** a cursor-reactive node/edge network in the hero (nodes = data points, edges = insights). Gold on dark, purple on light, low density, GPU-cheap canvas.
- **Editorial-asymmetric layout:** offset columns, oversized indices, generous negative space, deliberate composition.
- **Micro-interactions:** magnetic buttons, 3D card tilt, custom cursor with a live coordinate readout, link underlines that draw.
- **Effects:** ambient signal glow (accent), NO glitch, NO scanlines, NO neon text-shadow.

### Page Pattern — Portfolio (skill)
Hero (name/role + signal-map) → Ethos → Selected Work (indexed) → About (terminal) → Contact → Footer.
CTA placement: project-card hover + footer contact.

---

## Motion (skill motion 8/10, adapted)

- **Smooth scroll:** Lenis (`duration ~1.1`), disabled under reduced-motion.
- **Hero intro:** staggered rise (`power3.out`), signal-map fades up, accent underline draws.
- **Scroll reveals:** IntersectionObserver, `.reveal` translate+fade, 30–50ms stagger.
- **Micro:** 150–300ms transitions, `cubic-bezier(.2,.7,.2,1)`; card tilt & magnetic buttons on `pointer:fine` only.
- **Easing tokens:** enter `power3.out` / exit faster; UI `cubic-bezier(.2,.7,.2,1)`.
- Every animation must be meaningful and interruptible; honor `prefers-reduced-motion`.

---

## Anti-Patterns (Do NOT Use)

- ❌ **Emojis as icons** — use inline SVG (Lucide-style), consistent stroke width.
- ❌ **Missing cursor:pointer** on clickable elements.
- ❌ **Layout-shifting hovers** — animate `transform`/`opacity` only.
- ❌ **Low-contrast text** — maintain ≥4.5:1 (gold on light must darken; bright gold only on dark).
- ❌ **Instant state changes** — always 150–300ms transitions.
- ❌ **Invisible focus states** — visible focus ring for keyboard nav.
- ❌ Neon glow / glitch / scanlines — off-brief for a UX researcher.

---

## Pre-Delivery Checklist

- [ ] No emojis used as icons (SVG only, one consistent set)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150–300ms)
- [ ] Light mode text contrast ≥ 4.5:1 (verify gold + purple on white)
- [ ] Dark mode contrast verified separately (gold accent on near-black)
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected (Lenis + canvas + reveals off)
- [ ] No content hidden behind the sticky navbar (scroll offset)
- [ ] Semantic landmarks + heading hierarchy (single h1)
- [ ] Desktop verified at 1440 / 1280 (mobile deferred per client)
