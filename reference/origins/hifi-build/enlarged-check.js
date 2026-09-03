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
 *  5. All of the above at several window sizes, framed and full screen. The
 *     app always lays out at DESIGN_W=452 and is transform-scaled by k to fit,
 *     so structure is scale-invariant but worth confirming, and the EFFECTIVE
 *     on-screen type size (design px x k) is what a reader actually gets.
 *
 * READING THE EFFECTIVE SIZES
 * The relative gain is constant -- Enlarged is x2.32 on body text at every
 * viewport, in both modes, because both sides scale by the same k. What varies
 * is the absolute size, and that is a property of the phone-frame preview
 * rather than of Enlarged. Framed mode floors at k=0.5, so on a 1280x600 window
 * Standard body renders at 4.8px and Enlarged at 11.0px: the mode is working,
 * the stage is just small. Review the mode in FULL SCREEN, where a real phone
 * puts it (320x568 full: 6.7 -> 15.6px; 393x852 full: 8.3 -> 19.1px).
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

/* Framed on a desktop is the review case; full screen on a phone is the real
   one. The two framed small windows are where k hits its 0.5 floor. */
const VIEWPORTS = [
  ['1440x900 framed',  1440, 900,  false],
  ['1366x768 framed',  1366, 768,  false],
  ['393x852  full',     393, 852,  true ],
  ['320x568  full',     320, 568,  true ],
];

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
  let totalFindings = 0;

  for (const [label, vw, vh, full] of VIEWPORTS) {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh } });
    const page = await ctx.newPage();
    await page.goto('file://' + path.resolve(APP));
    await page.waitForTimeout(2000);
    await page.evaluate(f => setFull(f), full);

    // ---- toggle round-trip, and the effective on-screen sizes -------------
    const trip = await page.evaluate(async () => {
      const read = () => {
        const g = s => { const e = document.querySelector(s); return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
        const scr = document.getElementById('scr');
        return { k: scr.getBoundingClientRect().width / scr.offsetWidth,
                 name: g('.fcard .fnm'), nav: g('.tabs button'), body: g('.fcard .fbr') };
      };
      S.type = 'flower'; renderList(); nav('list');
      await new Promise(r => setTimeout(r, 250));
      const before = read();
      setAdv('enlarged', true);  renderList(); await new Promise(r => setTimeout(r, 300));
      const on = read();
      setAdv('enlarged', false); renderList(); await new Promise(r => setTimeout(r, 300));
      const after = read();
      return { before, on, after };
    });
    const same = trip.before.name === trip.after.name &&
                 trip.before.nav  === trip.after.nav &&
                 trip.before.body === trip.after.body;
    const eff = (m, key) => (m[key] * m.k).toFixed(1);

    console.log(`\n══ ${label} ${'─'.repeat(Math.max(0, 46 - label.length))}`);
    console.log(`   scale k=${trip.on.k.toFixed(3)}   round-trip: ${same ? 'CLEAN' : '*** DID NOT RETURN ***'}`);
    console.log(`   effective body  Standard ${eff(trip.before,'body')}px -> Enlarged ${eff(trip.on,'body')}px` +
                `  (x${(trip.on.body / trip.before.body).toFixed(2)})`);
    console.log(`   effective name  Standard ${eff(trip.before,'name')}px -> Enlarged ${eff(trip.on,'name')}px`);
    if (!same) totalFindings++;

    // ---- per-screen structural checks, ENLARGED on ------------------------
    let bad = 0; const shrunkNotes = [];
    for (const [screen, setup] of SCREENS) {
      const r = await page.evaluate(async ([screen, setup]) => {
        try { setAdv('enlarged', true); if (setup) eval(setup); nav(screen); }
        catch (e) { return { error: String(e && e.message || e) }; }
        await new Promise(r => setTimeout(r, 150));
        const root = document.querySelector('.s[data-s="' + screen + '"]');
        if (!root) return { error: 'no screen' };
        const view = document.getElementById('view') || root;
        const scrEl = document.getElementById('scr');
        const k = scrEl.getBoundingClientRect().width / scrEl.offsetWidth;
        const de = document.documentElement;
        const frame = root.getBoundingClientRect();
        const spill = [], small = [], shrunk = [];
        for (const el of root.querySelectorAll('*')) {
          if (el.tagName === 'SVG' || el.closest('svg')) continue;
          const cs = getComputedStyle(el);
          if (cs.display === 'none' || cs.visibility === 'hidden') continue;
          const bb = el.getBoundingClientRect();
          if (bb.width === 0 && bb.height === 0) continue;
          const name = () => {
            const c = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).join('.');
            return el.tagName.toLowerCase() + (c ? '.' + c : '');
          };
          /* An element inside a horizontal carousel is SUPPOSED to sit past the
             frame edge -- that is what the scroller is for. Only count spill
             with no horizontally-scrollable ancestor. */
          let inScroller = false;
          for (let a = el.parentElement; a && a !== root; a = a.parentElement) {
            const ox = getComputedStyle(a).overflowX;
            if ((ox === 'auto' || ox === 'scroll') && a.scrollWidth > a.clientWidth + 1) { inScroller = true; break; }
          }
          const over = Math.round(Math.max(bb.right - frame.right, frame.left - bb.left));
          if (over > 1 && !inScroller) spill.push(name() + ' +' + over + 'px');
          /* Target size, split two ways. getBoundingClientRect is POST-scale,
             so on a shrunk preview everything looks too small. The defect is a
             target under 24px in the app's own 452px design space; a target
             that only falls short once k shrinks it is a property of the stage,
             reported separately so it cannot be mistaken for a bug. */
          if (el.matches('button,a,[data-nav],[data-p],[data-add],.tap') && bb.height > 0) {
            const design = bb.height / k;
            if (design < 24) small.push(name() + ' ' + design.toFixed(0) + 'px by design');
            else if (bb.height < 24) shrunk.push(name() + ' ' + bb.height.toFixed(0) + 'px (' + design.toFixed(0) + 'px by design)');
          }
        }
        const uniq = a => [...new Set(a)];
        return { pageOverflow: Math.max(0, de.scrollWidth - de.clientWidth),
                 viewOverflow: Math.max(0, view.scrollWidth - view.clientWidth),
                 spill: uniq(spill), small: uniq(small), shrunk: uniq(shrunk) };
      }, [screen, setup]);

      if (r.error) { console.log(`   ERROR ${screen}: ${r.error}`); bad++; continue; }
      const flags = [];
      if (r.pageOverflow > 1) flags.push(`page h-overflow ${r.pageOverflow}px`);
      if (r.viewOverflow > 1) flags.push(`view h-overflow ${r.viewOverflow}px`);
      if (r.spill.length)     flags.push(`spill: ${r.spill.slice(0, 3).join(', ')}`);
      if (r.small.length)     flags.push(`target<24px: ${r.small.slice(0, 3).join(', ')}`);
      if (flags.length) { bad++; console.log(`   FLAG  ${screen.padEnd(11)} ${flags.join(' | ')}`); }
      if (r.shrunk.length) shrunkNotes.push(`${screen}: ${r.shrunk.slice(0, 3).join(', ')}`);
    }
    console.log(`   ${SCREENS.length} screens, ${bad} with findings`);
    if (shrunkNotes.length) {
      console.log(`   note: ${shrunkNotes.length} screen(s) have targets >=24px by design that ` +
                  `render under 24px at k=${trip.on.k.toFixed(2)} — stage scale, not a defect:`);
      for (const n of shrunkNotes.slice(0, 4)) console.log(`         ${n}`);
    }
    totalFindings += bad;
    await ctx.close();
  }

  await b.close();
  console.log(`\n${VIEWPORTS.length} viewports x ${SCREENS.length} screens — ` +
              `${totalFindings ? totalFindings + ' finding(s)' : 'no findings'}`);
})();
