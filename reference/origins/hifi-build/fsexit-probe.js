/* Measures the full-screen EXIT chip against the strip reserved for it.
 *
 * #fsexit lives OUTSIDE .s[data-s="..."], so enlarged-check.js, ratio.js and
 * snapshot-guard.js all miss it -- the documented chrome-layer blind spot. This
 * is the measurement for that layer.
 *
 *   node fsexit-probe.js <built.html>
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const fs = require('fs');
const CHROME = fs.existsSync('/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
  ? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
  : fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-'))
      .map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`).find(fs.existsSync);

/* Phone-shaped viewports: full screen is what a phone actually gets. */
const VIEWPORTS = [[393, 852], [320, 568]];

(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  const out = {};
  for (const [w, h] of VIEWPORTS) {
    for (const enlarged of [false, true]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h } });
      const page = await ctx.newPage();
      await page.goto('file://' + path.resolve(process.argv[2]));
      await page.waitForTimeout(2200);
      const r = await page.evaluate(async (enlarged) => {
        setAdv('enlarged', enlarged);
        nav('vape');                 // the screen the overlap was found on
        setFull(true);
        await new Promise(r => setTimeout(r, 300));
        const chip = document.getElementById('fsexit');
        const scr = document.getElementById('scr');
        const cs = getComputedStyle(chip);
        const cr = chip.getBoundingClientRect();
        const sr = scr.getBoundingClientRect();
        /* Everything is reported in the app's own design px: the frame is
           transform-scaled by k, so raw rects would measure the stage, not the
           layout -- the same trap that gave enlarged-check.js 9 false findings. */
        const k = sr.width / scr.offsetWidth;
        const stripPx = parseFloat(getComputedStyle(scr).paddingTop);
        return {
          top_css: cs.top,
          chip_top: +(cr.top / k).toFixed(1),
          chip_height: +(cr.height / k).toFixed(1),
          chip_bottom: +((cr.top + cr.height) / k).toFixed(1),
          strip: +stripPx.toFixed(1),
          clearance: +(stripPx - (cr.top + cr.height) / k).toFixed(1),
        };
      }, enlarged);
      out[`${w}x${h} ${enlarged ? 'enlarged' : 'standard'}`] = r;
      await ctx.close();
    }
  }
  await b.close();
  for (const [k, v] of Object.entries(out)) {
    console.log(`${k.padEnd(22)} top:${v.top_css.padEnd(7)} chip ${v.chip_top}→${v.chip_bottom} (h${v.chip_height})  strip ${v.strip}  clearance ${v.clearance > 0 ? '+' : ''}${v.clearance}`);
  }
})();
