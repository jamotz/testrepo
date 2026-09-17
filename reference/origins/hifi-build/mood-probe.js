/* What actually happens when a lifestyle chip is tapped, from each screen that
 * carries one, in both display modes.
 *   node mood-probe.js <built.html>
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const CASES = [
  ['shop, nothing filtered',      'S.type=null;S.sub=null;renderShop();nav("shop")',            '#moodbar'],
  ['list, drilled into Flower',   'S.type="flower";S.sub="Indoor";renderList();nav("list")',    '#moodbar2'],
  ['list, inside a deal',         'S.deal="pair";renderList();nav("list")',                  '#moodbar2'],
  ['vape dead-end',               'nav("vape")',                                                '#moodbar3'],
];

(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  for (const enlarged of [false, true]) {
    console.log(`\n══ ${enlarged ? 'ENLARGED' : 'STANDARD'} ${'─'.repeat(40)}`);
    for (const [label, setup, bar] of CASES) {
      const ctx = await b.newContext({ viewport: { width: 900, height: 1200 } });
      const page = await ctx.newPage();
      await page.goto('file://' + path.resolve(process.argv[2]));
      await page.waitForTimeout(2200);
      const r = await page.evaluate(async ([setup, bar, enlarged]) => {
        setAdv('enlarged', enlarged);
        eval(setup);
        await new Promise(r => setTimeout(r, 150));
        const before = { screen: S.screen, type: S.type, sub: S.sub, deal: S.deal, mood: S.mood };
        const chip = document.querySelector(bar + ' [data-mood]');       // first chip = Discovery
        if (!chip) return { error: 'no chip in ' + bar };
        const want = chip.dataset.mood;
        chip.click();
        await new Promise(r => setTimeout(r, 250));
        const shown = document.querySelectorAll('#grid .fcard').length;
        /* what the list would hold if the lifestyle were the ONLY filter */
        const global = P.filter(p => p.f.indexOf(want) > -1).length;
        return {
          before, want,
          after: { screen: S.screen, type: S.type, sub: S.sub, deal: S.deal, mood: S.mood },
          title: (document.getElementById('ltitle') || {}).textContent,
          shown, global,
        };
      }, [setup, bar, enlarged]);
      if (r.error) { console.log(`  ${label}: ${r.error}`); await ctx.close(); continue; }
      const b4 = r.before, af = r.after;
      console.log(`  ${label}`);
      console.log(`    tap "${r.want}"  screen ${b4.screen} → ${af.screen}   type ${b4.type} → ${af.type}   sub ${b4.sub} → ${af.sub}   deal ${b4.deal} → ${af.deal}`);
      console.log(`    mood ${b4.mood} → ${af.mood}   title "${r.title}"   showing ${r.shown} of ${r.global} products in that lifestyle`);
      await ctx.close();
    }
  }
  await b.close();
})();
