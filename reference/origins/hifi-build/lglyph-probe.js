/* Measures every .lglyph in the app, in both display modes, with strain mode ON.
 *
 * The four committed guards never see these elements: .lglyph only renders when
 * Advanced Settings' "Use product type" is on, and every guard leaves it off.
 * So a change to the strain letters has no coverage at all -- this probe is the
 * evidence that tokenising them moved nothing.
 *
 *   node lglyph-probe.js <built.html> > out.json
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const fs = require('fs');
const CHROME = fs.existsSync('/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
  ? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
  : fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-'))
      .map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`).find(fs.existsSync);

const SELECTORS = [
  '.chip .lglyph',
  '.fcard .fbadge .lglyph',
  '.pimg .life .lglyph',
  '.educard .edulife .lglyph',
  '.feelchip .lglyph',
  '.oc.life .lglyph',
];

/* Each screen that can put a lifestyle word on screen, with the call that
   fills it. A hidden screen measures zero, so each is navigated to. */
const SCREENS = [
  ['home',    'renderHome()'],
  ['shop',    'renderShop()'],
  ['list',    'S.type="flower"; renderList()'],
  ['product', 'openProduct(0)'],
  ['edu',     'renderEduHub()'],
  ['guide',   'renderFeel()'],
  ['method',  'G.feels=["social"]; renderMethod()'],
  ['subtype', 'G.method="flower"; renderSub()'],
  ['taste',   'G.subs=(SUBS["flower"]||[]).slice(0,1); renderTaste()'],
  ['finish',  'renderFinish()'],
];

(async () => {
  const file = process.argv[2];
  const b = await chromium.launch({ executablePath: CHROME });
  const out = {};
  for (const enlarged of [false, true]) {
    const ctx = await b.newContext({ viewport: { width: 900, height: 1200 } });
    const page = await ctx.newPage();
    await page.goto('file://' + path.resolve(file));
    await page.waitForTimeout(2400);
    for (const [screen, setup] of SCREENS) {
      const rows = await page.evaluate(async ([screen, setup, SELECTORS, enlarged]) => {
        try {
          setAdv('strain', true);              // the letters only exist in this mode
          setAdv('enlarged', enlarged);
          if (setup) eval(setup);
          nav(screen);
        } catch (e) { return { error: String((e && e.message) || e) }; }
        await new Promise(r => setTimeout(r, 150));
        const root = document.querySelector('.s[data-s="' + screen + '"]');
        if (!root) return { error: 'screen not found' };
        const res = {};
        for (const sel of SELECTORS) {
          const els = [...root.querySelectorAll(sel)];
          res[sel] = els.map(el => {
            const cs = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return {
              text: (el.textContent || '').trim(),
              fontSize: cs.fontSize,
              height: cs.height,
              width: cs.width,
              // rendered box, rounded: catches overflow/clipping the CSS alone hides
              box: `${r.width.toFixed(1)}x${r.height.toFixed(1)}`,
            };
          });
        }
        return res;
      }, [screen, setup, SELECTORS, enlarged]);
      out[`${enlarged ? 'enlarged' : 'standard'}/${screen}`] = rows;
    }
    await ctx.close();
  }
  await b.close();
  console.log(JSON.stringify(out, null, 1));
})();
