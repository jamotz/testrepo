/* Does every Guide Me path recommend what was picked, and is each card one that
 * the group's own "Browse products" would show? Walks every method x lifestyle,
 * a two-lifestyle pick, and each sub-type, then the Flavor facet on its shelves.
 *   node guide-probe.js <built.html>          exit 1 on any mismatch
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  const p = await b.newPage();
  p.on('pageerror', e => console.log('PAGEERROR', e.message));
  await p.goto('file://' + path.resolve(process.argv[2]));
  await p.waitForTimeout(2200);
  const r = await p.evaluate(() => {
    const out = [], fails = [];
    const cards = () => [...document.querySelectorAll('#finishwrap .fcard')].map(c => P[+c.dataset.p]);
    const run = (feels, method, subs) => {
      G.feels = feels; G.method = method; G.subs = subs; G.tastes = []; renderFinish();
      const cs = cards(), notes = [...document.querySelectorAll('#finishwrap .lock')].map(n => n.textContent);
      const shelf = P.filter(q => q.t === method && (!subs.length || subs.indexOf(method === 'edible' ? q.etype : method === 'drink' ? q.sub2 : q.sub) > -1));
      const inLife = shelf.filter(q => feels.indexOf(q.f[0]) > -1);
      const wrongType = cs.filter(c => shelf.indexOf(c) < 0).length;
      const wrongLife = inLife.length ? cs.filter(c => feels.indexOf(c.f[0]) < 0).length : 0;
      const label = method + '/' + feels.join('+') + (subs.length ? '/' + subs.join('+') : '');
      out.push(`${label.padEnd(40)} ${cs.length} cards  wrong-shelf ${wrongType}  wrong-life ${wrongLife}  in-life ${inLife.length}${notes.length ? '  NOTE: ' + notes[0].slice(0, 70) : ''}`);
      if (wrongType || wrongLife) fails.push(label);
      if (!shelf.length && cs.length) fails.push(label + ' (cards on an empty shelf)');
      if (shelf.length && !inLife.length && !notes.length) fails.push(label + ' (fallback without a note)');
      return cs;
    };
    for (const m of ['flower', 'concentrate', 'edible', 'drink', 'preroll', 'topical', 'tincture'])
      for (const f of Object.keys(FEEL)) run([f], m, []);
    const two = run(['discovery', 'nightlife'], 'flower', []);
    out.push('  two lifestyles, card order: ' + two.map(c => c.f[0].slice(0, 4)).join(' '));
    for (const [m, s] of [['edible', 'Gummies'], ['edible', 'Chocolate'], ['concentrate', 'Live Resin'], ['topical', 'Pain Relief'], ['drink', 'Seltzer'], ['drink', 'Shot']])
      run(['social'], m, [s]);
    /* Browse must show every card it was recommended beside */
    for (const [f, m, s] of [['unwind', 'flower', []], ['social', 'edible', ['Gummies']], ['holistic', 'drink', ['Seltzer']], ['adventurous', 'drink', ['Shot']], ['nightlife', 'concentrate', ['Live Resin']]]) {
      const cs = run([f], m, s);
      document.querySelector('#finishwrap .browse').click();
      const shown = results(), miss = cs.filter(c => shown.indexOf(c) < 0);
      out.push(`  Browse ${m}/${f}${s.length ? '/' + s[0] : ''}: list ${shown.length}, recommended cards missing from it: ${miss.length}`);
      if (miss.length) fails.push('Browse ' + m + '/' + f);
      if (m === 'drink' && !document.querySelector('#subcats [data-dr2].sel')) fails.push('drink type not shown on the shelf');
      nav('shop');
    }
    /* vape goes to the web-only screen, as from the shop */
    G.feels = ['social']; renderMethod(); document.querySelector('[data-mk="vape"]').click(); document.getElementById('methodnext').click();
    out.push('vape -> screen "' + S.screen + '"'); if (S.screen !== 'vape') fails.push('vape routing');
    /* Flavor facet: options per shelf, filtering, pruning on shelf change */
    S.mood = null; S.brands = []; S.thc = null; S.sale = false; S.deal = null; S.size = null; S.sub = S.sub2 = S.sub3 = S.eform = null;
    for (const t of ['flower', 'preroll', 'concentrate', 'edible', null]) {
      S.type = t; S.flavors = []; drawDrawer();
      const opts = [...document.querySelectorAll('#dbody [data-fl]')].map(x => x.dataset.fl);
      out.push(`drawer ${String(t).padEnd(12)} flavor options: ${opts.join(', ') || '(locked)'}`);
      if ((TASTED.indexOf(t) > -1) !== (opts.length > 0)) fails.push('flavor options on ' + t);
    }
    S.type = 'flower'; S.flavors = ['Floral']; const fl = results();
    out.push(`flower + Floral -> ${fl.length} products, all Floral: ${fl.every(q => q.ta.indexOf('Floral') > -1)}`);
    if (!fl.length || !fl.every(q => q.ta.indexOf('Floral') > -1)) fails.push('Floral filter');
    S.flavors = ['Sweet']; S.type = 'concentrate'; results();
    out.push(`flower Sweet -> switch to concentrate -> flavors now [${S.flavors}]`);
    if (S.flavors.length) fails.push('Sweet not pruned on concentrate');
    S.type = 'flower'; S.flavors = ['Citrus']; S.type = 'edible'; const ed = results();
    out.push(`flower Citrus -> switch to edible -> flavors [${S.flavors}], ${ed.length} edibles shown`);
    if (S.flavors.length || ed.length !== P.filter(q => q.t === 'edible').length) fails.push('flavor leaked onto edibles');
    return { out, fails };
  });
  console.log(r.out.join('\n'));
  console.log(r.fails.length ? '\nFAIL: ' + r.fails.join('; ') : '\nPASS — every card fits its pick, Flavor scoped to its three shelves');
  await b.close(); process.exit(r.fails.length ? 1 : 0);
})();
