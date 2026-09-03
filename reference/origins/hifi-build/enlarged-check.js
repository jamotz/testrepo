/* Functional check of ENLARGED view. The other two guards are the mirror of
 * this one: standard-guard.py and snapshot-guard.js both prove that STANDARD
 * did not move, and neither one looks at whether Enlarged itself works. This
 * does, by turning the mode on and walking every screen.
 *
 *   node enlarged-check.js <built-app.html>
 *
 * It reports rather than exits non-zero: "correct" here is partly a judgement
 * (see the carousel note below), so read the output.
 *
 * WHAT IT CHECKS
 *  1. The toggle round-trips. Standard -> Enlarged -> Standard must return the
 *     original computed sizes exactly. Expected: name 14px / nav 9px / icon
 *     21px, on gives 32 / 15 / 34, off returns to 14 / 9 / 21. This is the
 *     check that would have caught the count=1 regression from the app's side.
 *  2. No page-level horizontal scrolling on any screen (WCAG 1.4.10 Reflow).
 *  3. Nothing spills past the app frame -- the failure mode of most Enlarged
 *     bugs, where a fixed width sized for 13px text is overrun at 22px.
 *  4. No interactive element under 24px tall (WCAG 2.5.8 Target Size).
 *
 * THE CAROUSEL EXCEPTION, WHICH IS WHY 3 NEEDS CARE
 * The deal rows, the browse carousels and the mood chip rows scroll
 * horizontally, so their children legitimately sit outside the frame. A naive
 * spill check flags all of them -- it reported 5 screens of false positives on
 * first run. Anything with a horizontally-scrollable ancestor is therefore
 * skipped. If you widen this check, keep that exception or the output becomes
 * noise nobody reads.
 *
 * Last run (build of 1ca26e4): round-trip CLEAN, 24 screens, 0 findings.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');
const APP = process.argv[2];

const SCREENS = [
  ['landing','renderStores()'],['home','renderHome()'],['shop','renderShop()'],
  ['list','S.type="flower"; renderList()'],['product','openProduct(0)'],
  ['cart','addToCart(0, sizesFor(P[0])[0]||"1 g"); renderCart()'],
  ['confirm','renderConfirm()'],['dealcal','renderDealCal()'],
  ['guide','renderFeel()'],['method','G.feels=["social"]; renderMethod()'],
  ['subtype','G.method="flower"; renderSub()'],
  ['taste','G.subs=(SUBS["flower"]||[]).slice(0,1); renderTaste()'],
  ['finish','renderFinish()'],['edu','renderEduHub()'],
  ['edutopic','renderEduHub(); renderEduTopic(EDU_ORDER[0],0)'],['vape',''],
  ['account','renderAccount()'],['acloyalty','renderAccount()'],
  ['acorders','renderAccount()'],['acrecs','renderAccount()'],
  ['acreviews','renderAccount()'],['acsettings','renderAccount()'],
  ['acadv','renderAccount()'],['acabout','renderAccount()'],
];

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 900, height: 1200 } });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(APP));
  await page.waitForTimeout(2400);

  // ---- 1. toggle round-trip -------------------------------------------------
  const trip = await page.evaluate(async () => {
    const read = () => {
      const g = s => { const e = document.querySelector(s); return e ? getComputedStyle(e).fontSize : null; };
      const icon = document.querySelector('.tabs button svg');
      return { name: g('.fcard .fnm'), nav: g('.tabs button'),
               icon: icon ? getComputedStyle(icon).width : null };
    };
    S.type = 'flower'; renderList(); nav('list');
    await new Promise(r => setTimeout(r, 200));
    const before = read();
    setAdv('enlarged', true);  renderList(); await new Promise(r => setTimeout(r, 250));
    const on = read();
    setAdv('enlarged', false); renderList(); await new Promise(r => setTimeout(r, 250));
    const after = read();
    return { before, on, after };
  });

  // ---- 2. per-screen checks in ENLARGED ------------------------------------
  const results = [];
  for (const [screen, setup] of SCREENS) {
    const r = await page.evaluate(async ([screen, setup]) => {
      try { setAdv('enlarged', true); if (setup) eval(setup); nav(screen); }
      catch (e) { return { error: String(e && e.message || e) }; }
      await new Promise(r => setTimeout(r, 200));
      const root = document.querySelector('.s[data-s="' + screen + '"]');
      const view = document.getElementById('view') || root;
      if (!root) return { error: 'no screen' };

      // horizontal overflow of the scrolling view
      const viewOverflow = Math.max(0, view.scrollWidth - view.clientWidth);

      // elements whose box runs past the app frame
      const frame = root.getBoundingClientRect();
      const spill = [];
      const small = [];
      for (const el of root.querySelectorAll('*')) {
        if (el.tagName === 'SVG' || el.closest('svg')) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        const b = el.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) continue;
        /* An element inside a horizontal carousel is SUPPOSED to sit past the
           frame edge -- that is what the scroller is for. Only count spill that
           has no horizontally-scrollable ancestor. */
        let inScroller = false;
        for (let a = el.parentElement; a && a !== root; a = a.parentElement) {
          const ox = getComputedStyle(a).overflowX;
          if ((ox === 'auto' || ox === 'scroll') && a.scrollWidth > a.clientWidth + 1) { inScroller = true; break; }
        }
        const over = Math.round(Math.max(b.right - frame.right, frame.left - b.left));
        if (over > 1 && !inScroller) {
          const cls = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).join('.');
          spill.push((el.tagName.toLowerCase() + (cls ? '.' + cls : '')) + ' +' + over + 'px');
        }
        // tap targets: anything clickable
        if (el.matches('button,a,[data-nav],[data-p],[data-add],.tap')) {
          if (b.height > 0 && b.height < 24) {
            const cls = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).join('.');
            small.push((el.tagName.toLowerCase() + (cls ? '.' + cls : '')) + ' ' + Math.round(b.height) + 'px');
          }
        }
      }
      const uniq = a => [...new Set(a)];
      return { viewOverflow, spill: uniq(spill), small: uniq(small),
               frameW: Math.round(frame.width) };
    }, [screen, setup]);
    results.push([screen, r]);
  }
  await b.close();

  console.log('── toggle round-trip (.fcard .fnm / .tabs button / tab icon) ──');
  console.log('  Standard before :', JSON.stringify(trip.before));
  console.log('  Enlarged on     :', JSON.stringify(trip.on));
  console.log('  Standard after  :', JSON.stringify(trip.after));
  const same = JSON.stringify(trip.before) === JSON.stringify(trip.after);
  console.log('  round-trip      :', same ? 'CLEAN' : '*** DID NOT RETURN ***');

  console.log('\n── per-screen, ENLARGED on ──');
  let bad = 0;
  for (const [screen, r] of results) {
    if (r.error) { console.log(`  ERROR ${screen}: ${r.error}`); bad++; continue; }
    const flags = [];
    if (r.viewOverflow > 1) flags.push(`h-overflow ${r.viewOverflow}px`);
    if (r.spill.length)     flags.push(`spill: ${r.spill.slice(0,4).join(', ')}`);
    if (r.small.length)     flags.push(`target<24px: ${r.small.slice(0,4).join(', ')}`);
    if (flags.length) { bad++; console.log(`  FLAG  ${screen.padEnd(11)} ${flags.join(' | ')}`); }
    else console.log(`  ok    ${screen.padEnd(11)} frame ${r.frameW}px`);
  }
  console.log(`\n${results.length} screens, ${bad} with findings`);
})();
