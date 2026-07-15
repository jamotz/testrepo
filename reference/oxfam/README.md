# Oxfam — where to put things

**Contact landing → 6 buttons → subpages (some go one level deeper).**

- `flow/` → your **flow diagram** + any **workflow sketches** for the pages that
  have tertiary (3rd-level) pages. These are the ones Claude "reads" to wire up
  the clickable prototype.
- `page-00-landing/` → the **contact landing page**: a full screenshot + any
  images that appear on it.
- `page-01/` … `page-06/` → **one folder per button/subpage**. Put that page's
  full screenshot + its individual images inside.

### Naming (optional, helpful)
If it's easy, rename `page-01` → the real page name (e.g. `donate`, `volunteer`).
If not, no worries — just tell Claude "page-01 is the Donate page," etc., and it'll
map them from your flow diagram.

Deeper (tertiary) pages? Put their screenshots in the same button folder and note
the path in your `flow/` sketch (e.g. "Donate → One-time vs Monthly").
