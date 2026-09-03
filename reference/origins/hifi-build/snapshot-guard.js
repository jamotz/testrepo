/* Standard-mode snapshot guard for the Enlarged view accessibility layer.
 *
 * WHY THIS EXISTS ALONGSIDE standard-guard.py
 * standard-guard.py reads the stylesheet TEXT: it resolves every token back to
 * its literal, drops the #scr.enlarged rules, and compares what is left to the
 * pre-Enlarged baseline. That catches a value written into the wrong block --
 * the count=1 bug -- in 0.06s, and it is the one you run constantly.
 *
 * It cannot see what the BROWSER resolved. A rule can be correct in the text
 * and still change Standard through:
 *   - specificity or source order deciding a different winner
 *   - an #scr.enlarged rule that is missing the class scope, so it applies always
 *   - a size set from JS at runtime
 *   - a token that changes a LAYOUT property rather than a font-size
 * This walks the real app in Chromium and compares computed styles instead.
 *
 *   node snapshot-guard.js <baseline.html> <current.html>
 *   node snapshot-guard.js <baseline.html> <current.html> --verbose
 *
 * Exit 0 on PASS, 1 on FAIL.
 *
 * BUILDING THE TWO SIDES (~2 min each; that cost is why the cheap guard exists)
 *   SP=<scratchpad>
 *   git worktree add -f $SP/base 470e2b5          # see THE BASELINE MOVED below
 *   python3 -m pip install --quiet Pillow
 *   python3 reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/cur.html
 *   python3 $SP/base/reference/origins/hifi-build/asm_app.py && mv $SP/origins-app.html $SP/base.html
 *   node reference/origins/hifi-build/snapshot-guard.js $SP/base.html $SP/cur.html
 * asm_app.py writes to the same scratchpad path both times, so move the first
 * output before building the second or the second silently overwrites it.
 *
 * WHAT IT COMPARES
 * Standard only. It never turns Enlarged on: the question is whether the
 * default mode moved, and Enlarged is expected to differ.
 *
 * Elements are keyed by screen + tag + class signature, NOT by DOM order, and
 * counted as a multiset. Order is not stable enough to diff positionally (the
 * deals rota and the calendar are generated against today's date), and a
 * positional diff reports one insertion as every element after it. Keying by
 * signature means a real change names the element it happened to.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path = require('path');

const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

/* Properties worth guarding: type, the box a control makes around it, and
 * colour. Deliberately not every computed property -- most never move, and a
 * wide net makes a failure hard to read. */
const PROPS = ['fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'color',
               'minHeight', 'height', 'width', 'paddingTop', 'paddingLeft',
               'gap', 'borderRadius'];

/* Every screen, with whatever has to be called to populate it first. nav()
 * itself renders list/cart/dealcal; the rest need their render call. A hidden
 * screen measures zero, so each is navigated to before being read. */
const SCREENS = [
  ['landing',    'renderStores()'],
  ['home',       'renderHome()'],
  ['shop',       'renderShop()'],
  ['list',       'S.type="flower"; renderList()'],
  ['product',    'openProduct(0)'],
  ['cart',       'addToCart(0, sizesFor(P[0])[0] || "1 g"); renderCart()'],
  ['confirm',    'renderConfirm()'],
  ['dealcal',    'renderDealCal()'],
  /* The wizard reads G. Left at its defaults, subtype/taste/finish render
     near-empty and compare clean while covering almost nothing, so G is filled
     in first -- identically on both sides. */
  ['guide',      'renderFeel()'],
  ['method',     'G.feels=["social"]; renderMethod()'],
  ['subtype',    'G.method="flower"; renderSub()'],
  ['taste',      'G.subs=(SUBS["flower"]||[]).slice(0,1); renderTaste()'],
  ['finish',     'renderFinish()'],
  ['edu',        'renderEduHub()'],
  ['edutopic',   'renderEduHub(); renderEduTopic(EDU_ORDER[0], 0)'],
  ['vape',       ''],
  ['account',    'renderAccount()'],
  ['acloyalty',  'renderAccount()'],
  ['acorders',   'renderAccount()'],
  ['acrecs',     'renderAccount()'],
  ['acreviews',  'renderAccount()'],
  ['acsettings', 'renderAccount()'],
  ['acadv',      'renderAccount()'],
  ['acabout',    'renderAccount()'],
];

/* Each side gets its own browser context. The app persists display mode in
   localStorage["origins.display.v1"], and a shared context would carry it (and
   anything else stored) from the first file into the second -- the guard would
   then be comparing two runs that did not start from the same state. */
async function snapshot(browser, file) {
  const ctx = await browser.newContext({ viewport: { width: 900, height: 1200 } });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(file));
  await page.waitForTimeout(2400);
  const out = {};
  for (const [screen, setup] of SCREENS) {
    const rows = await page.evaluate(async ([screen, setup, PROPS]) => {
      try {
        if (typeof setAdv === 'function') setAdv('enlarged', false);   // Standard, always
        if (setup) eval(setup);
        nav(screen);
      } catch (e) {
        return { error: String(e && e.message || e) };
      }
      await new Promise(r => setTimeout(r, 120));
      const root = document.querySelector('.s[data-s="' + screen + '"]');
      if (!root) return { error: 'screen not found' };
      const seen = [];
      for (const el of root.querySelectorAll('*')) {
        if (el.tagName === 'SVG' || el.closest('svg')) continue;   // path soup
        const cs = getComputedStyle(el);
        if (cs.display === 'none') continue;
        const cls = (el.getAttribute('class') || '').trim().split(/\s+/)
                      .filter(c => c && c !== 'on').sort().join('.');
        const key = el.tagName.toLowerCase() + (cls ? '.' + cls : '');
        seen.push(key + ' ‖ ' + PROPS.map(p => cs[p]).join(' | '));
      }
      return { rows: seen };
    }, [screen, setup, PROPS]);
    out[screen] = rows;
  }
  await ctx.close();
  return out;
}

function counter(list) {
  const m = new Map();
  for (const x of list) m.set(x, (m.get(x) || 0) + 1);
  return m;
}
function diff(ca, cb) {                   // multiset ca - cb, both Maps
  const out = [];
  for (const [k, n] of ca) {
    const extra = n - (cb.get(k) || 0);
    for (let i = 0; i < extra; i++) out.push(k);
  }
  return out;
}

/* ── THE BASELINE MOVED (2026-09-03) ──────────────────────────────────────
 * It was cc6edad, the last pre-Enlarged commit, to prove the Enlarged work
 * never disturbed Standard. It is now 470e2b5, and the reason is that Standard
 * started changing for reasons that have nothing to do with Enlarged: the vape
 * screen took the shop chrome (.sbar + white chipbar, orange in-body back
 * button removed). That is a real, intended change to what Standard renders,
 * so it is NOT an accepted delta -- those are for differences that do not move
 * anything on screen. The documented response to a legitimate Standard change
 * is to re-baseline deliberately, and this is that.
 *
 * What the move costs, stated plainly: this guard no longer measures against
 * pre-Enlarged. It measures against the last verified state. Anyone trusting
 * 470e2b5 as a baseline is trusting that the run which blessed it was read
 * properly -- the cc6edad comparison at that commit showed the vape screen's
 * intended diff and the five accepted deltas, and nothing else.
 *
 * What the move does NOT cost: standard-guard.py still runs against cc6edad
 * with ZERO exceptions, 214 = 214. The pre-Enlarged anchor survives where it
 * matters most -- every font-size in the app -- and that is the check that
 * catches the count=1 class of bug.
 *
 * Re-baseline again the same way: only after a run whose every difference you
 * have read and can name, and say here what moved and why.
 *
 * ── Accepted deltas ──────────────────────────────────────────────────────
 * Differences from the baseline that are known, reviewed and intended. Each
 * needs a reason, and the run PRINTS how many it applied, so this list stays
 * visible rather than quietly swallowing failures. Keep it short: if it starts
 * growing, the baseline is wrong, not the app.
 *
 * Empty as of the re-baseline: the five entries it held (min-height on .fbtn
 * and .edusearch, and the removed span.advsoon) are all part of 470e2b5, so
 * they are in the baseline now rather than exceptions to it.
 *
 * Do NOT add an entry to make a red run green. An entry means "this change to
 * Standard was deliberate and someone checked it"; anything else is the bug
 * this guard exists to find. */
const ACCEPTED_RETIRED_AT_REBASELINE = [
  { key: 'button.fbtn', prop: 'minHeight', from: 'auto', to: '47px',
    why: 'Filter took min-height:var(--control-height) in the token refactor. ' +
         'Standard --control-height is 47px, under the 50px the button already ' +
         'rendered at, so nothing moves.' },
  { key: 'button.edusearch.tap', prop: 'minHeight', from: '0px', to: '47px',
    why: "Origins U's Search, same rule and same reasoning as .fbtn." },
  { key: 'span.advsoon', gone: true,
    why: 'The "Coming soon" tag on Enlarged view in Advanced Settings. Removed ' +
         'on purpose when the mode shipped (2026-08-20); see project-handoff.md.' },
];
/* Kept above only as a record of what the old cc6edad baseline needed. The live
   list is empty; nothing is excepted from the 470e2b5 baseline. */
const ACCEPTED = [];

function isAccepted(n) {
  return ACCEPTED.some(a =>
    a.key === n.key &&
    (a.gone ? !!n.gone
            : (!n.gone && !n.added && a.prop === n.prop &&
               a.from === n.from && a.to === n.to)));
}

(async () => {
  const [baseFile, curFile] = process.argv.slice(2).filter(a => !a.startsWith('--'));
  const verbose = process.argv.includes('--verbose');
  if (!baseFile || !curFile) {
    console.error('usage: node snapshot-guard.js <baseline.html> <current.html> [--verbose]');
    process.exit(2);
  }

  const b = await chromium.launch({ executablePath: CHROME });
  console.log('baseline: ' + baseFile);
  const base = await snapshot(b, baseFile);
  console.log('current:  ' + curFile);
  const cur = await snapshot(b, curFile);
  await b.close();

  let failed = 0, compared = 0, skipped = [], accepted = 0;
  for (const [screen] of SCREENS) {
    const B = base[screen], C = cur[screen];
    if (B.error || C.error) {
      skipped.push(screen + ' (' + (B.error || C.error) + ')');
      continue;
    }
    compared++;
    const bc = counter(B.rows), cc = counter(C.rows);
    const lost = diff(bc, cc), gained = diff(cc, bc);
    if (!lost.length && !gained.length) {
      if (verbose) console.log(`  ok    ${screen.padEnd(11)} ${B.rows.length} elements`);
      continue;
    }

    /* Pair lost and gained on the element key so a CHANGED value reads as one
       line naming the property, instead of two opaque tuples the reader has to
       diff by eye. What is left over is a genuine add or removal. */
    const byKey = new Map();
    const put = (row, side) => {
      const [key, vals] = row.split(' ‖ ');
      if (!byKey.has(key)) byKey.set(key, { lost: [], gained: [] });
      byKey.get(key)[side].push(vals.split(' | '));
    };
    lost.forEach(r => put(r, 'lost'));
    gained.forEach(r => put(r, 'gained'));

    const notes = [];
    for (const [key, g] of byKey) {
      const n = Math.min(g.lost.length, g.gained.length);
      for (let i = 0; i < n; i++) {                       // changed values
        PROPS.forEach((prop, pi) => {
          const from = g.lost[i][pi], to = g.gained[i][pi];
          if (from !== to) notes.push({ screen, key, prop, from, to });
        });
      }
      for (let i = n; i < g.lost.length; i++)   notes.push({ screen, key, gone: true });
      for (let i = n; i < g.gained.length; i++) notes.push({ screen, key, added: true });
    }

    const unexplained = notes.filter(n => !isAccepted(n));
    accepted += notes.length - unexplained.length;
    if (!unexplained.length) {
      if (verbose) console.log(`  ok*   ${screen.padEnd(11)} ${B.rows.length} elements ` +
                               `(${notes.length} accepted)`);
      continue;
    }
    failed++;
    console.log(`\nFAIL  ${screen}`);
    const seen = new Set();
    for (const n of unexplained) {
      const line = n.gone  ? `   removed  ${n.key}`
                 : n.added ? `   added    ${n.key}`
                 : `   ${n.key}  ${n.prop}: ${n.from} -> ${n.to}`;
      if (seen.has(line)) continue;                        // collapse repeats
      seen.add(line);
      console.log(line);
    }
  }

  console.log(`\n${compared} screens compared` +
              (accepted ? `, ${accepted} accepted delta(s)` : '') +
              (skipped.length ? `, ${skipped.length} skipped` : ''));
  for (const s of skipped) console.log('  skipped: ' + s);
  if (failed) {
    console.log(`\nFAIL — Standard moved on ${failed} screen(s).`);
    console.log('A "-" and "+" pair on the same key is a changed value; check ' +
                'whether an #scr.enlarged rule lost its scope, or a token moved in :root.');
    process.exit(1);
  }
  if (skipped.length) {
    console.log('\nINCOMPLETE — no differences, but some screens could not be read.');
    process.exit(1);
  }
  console.log(accepted
    ? `\nPASS — Standard matches the baseline, with ${accepted} accepted delta(s).`
    : '\nPASS — Standard computes identically to the baseline.');
})();
