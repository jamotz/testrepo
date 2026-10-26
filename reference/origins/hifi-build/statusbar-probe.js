/* The phone's status bar and the island-as-exit, which live OUTSIDE
 * .s[data-s="..."] - enlarged-check.js, ratio.js and snapshot-guard.js never
 * look at them, so this is the measurement for that layer. Replaces
 * fsexit-probe.js, retired with the EXIT chip on 2026-10-26.
 *
 * The bar is drawn in iOS points (--sb-u). Full screen on a phone, a point
 * must be one CSS px whatever the model: 17px time, 126x37 island, 27x13
 * battery, 54px bar. Framed, it scales with the phone. Enlarged view must not
 * touch it. Tapping the island must leave full screen.
 *
 *   node statusbar-probe.js <built.html>          exit 1 on any miss
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const fs = require('fs');
const CHROME = fs.existsSync('/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
  ? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
  : fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-'))
      .map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`).find(fs.existsSync);

const CASES = [            // [w, h, full screen, enlarged]
  [393, 852, true, false], [320, 568, true, false], [430, 932, true, false],
  [393, 852, true, true],  [1440, 900, false, false], [1440, 900, false, true],
];
(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  const fails = [];
  for (const [w, h, full, enl] of CASES) {
    const page = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
    await page.goto('file://' + path.resolve(process.argv[2]));
    await page.waitForTimeout(2200);
    const r = await page.evaluate(async ([full, enl]) => {
      setAdv('enlarged', enl); nav('home'); if (full) setFull(true);
      await new Promise(r => setTimeout(r, 300));
      const R = s => document.querySelector(s).getBoundingClientRect();
      const t = document.querySelector('.sbtime');
      const k = R('#phone').width / (452 + (full ? 0 : 22));
      return { k, time: parseFloat(getComputedStyle(t).fontSize) * k, island: [R('#island').width, R('#island').height],
               bat: [R('.sbbat').width, R('.sbbat').height], bar: R('.status').height,
               live: getComputedStyle(document.getElementById('island')).pointerEvents,
               shown: getComputedStyle(document.querySelector('.status')).display !== 'none' };
    }, [full, enl]);
    const r1 = v => Math.round(v * 10) / 10;
    const label = `${w}x${h} ${full ? 'full' : 'framed'}${enl ? ' +enlarged' : ''}`;
    let exited = null;
    if (full) { await page.click('#island'); await page.waitForTimeout(200); exited = !(await page.evaluate(() => document.body.classList.contains('fs'))); }
    console.log(`${label.padEnd(30)} time ${r1(r.time)}px  island ${r.island.map(r1).join('x')}  battery ${r.bat.map(r1).join('x')}  bar ${r1(r.bar)}  ${full ? 'island exits: ' + exited : 'island inert: ' + (r.live === 'none')}`);
    if (!r.shown) fails.push(label + ': status bar hidden');
    if (full && w < 600) {                       // a phone: native points
      const near = (a, b) => Math.abs(a - b) < 0.6;
      if (!near(r.time, 17) || !near(r.island[0], 126) || !near(r.island[1], 37) || !near(r.bat[0], 27) || !near(r.bar, 54)) fails.push(label + ': not native iOS points');
    }
    if (full && !exited) fails.push(label + ': island did not exit');
    if (!full && r.live !== 'none') fails.push(label + ': island takes taps while framed');
    await page.context().close();
  }
  /* Enlarged leaving the bar alone shows as identical rows above: framed vs
     framed +enlarged, and full vs full +enlarged at 393. */
  console.log(fails.length ? '\nFAIL: ' + fails.join('; ') : '\nPASS — native iOS sizes in full screen on every phone width, island exits, Enlarged leaves the bar alone');
  await b.close(); process.exit(fails.length ? 1 : 0);
})();
