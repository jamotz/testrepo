/* Behavioural test for the filter drawer's Brands section.
 *
 *   node drawer-test.js <built-app.html>
 *
 * Covers, in BOTH display modes:
 *   - the three-row clamp and that "See more" appears only when it is needed
 *   - that the button fully expands the list and then hides itself
 *   - that an active product type scopes Brands to that shelf
 *   - the stranded-selection path: pick a brand on one shelf, switch shelf,
 *     and confirm the selection is dropped rather than silently zeroing results
 *
 * WHY IT EXISTS RATHER THAN LEANING ON THE GUARDS
 * snapshot-guard.js walks .s[data-s="<screen>"] subtrees and the drawer is not
 * inside one, so it cannot see any of this -- the same scope limit that let the
 * full-screen exit chip through. Nothing else would catch a drawer regression.
 *
 * WHY THE CLAMP IS MEASURED AND NOT A COUNT
 * Standard fits 10 of 42 pills in three rows; Enlarged fits 6. A fixed count or
 * a max-height would be wrong in one mode or the other. Rows come from distinct
 * offsetTop values, which means the drawer must already be .on when
 * clampBrands() runs -- a display:none drawer reports every offsetTop as 0.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
 for (const enl of [false,true]) {
  const ctx=await b.newContext({viewport:{width:393,height:852},deviceScaleFactor:2});
  const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(process.argv[2])); await p.waitForTimeout(2100);
  const r=await p.evaluate(async(enl)=>{
    setFull(true); setAdv('enlarged',enl);
    const out={};
    const rowsOf=()=>{const w=document.querySelector('#brandopts');
      const vis=[...w.children].filter(b=>!b.classList.contains('bhide'));
      const rows=[...new Set(vis.map(b=>b.offsetTop))];
      return {visible:vis.length,total:w.children.length,rows:rows.length,
              moreShown:!document.querySelector('#brandmore').classList.contains('bhide')};};
    nav('list'); document.querySelector('#openfilter').click();
    await new Promise(r=>setTimeout(r,350));
    out.collapsed=rowsOf();
    document.querySelector('#bmorebtn').click();
    await new Promise(r=>setTimeout(r,250));
    out.expanded=rowsOf();
    // now scope by product type
    [...document.querySelectorAll('[data-ft]')].find(x=>x.dataset.ft==='drink').click();
    await new Promise(r=>setTimeout(r,300));
    out.drinkScoped=rowsOf();
    out.drinkBrands=[...document.querySelector('#brandopts').children].map(x=>x.textContent);
    // stranded-selection check: pick a drink brand, then switch to flower
    document.querySelector('[data-fb]').click();
    await new Promise(r=>setTimeout(r,200));
    out.selectedOnDrink=S.brands.slice();
    [...document.querySelectorAll('[data-ft]')].find(x=>x.dataset.ft==='flower').click();
    await new Promise(r=>setTimeout(r,300));
    out.afterSwitchToFlower=S.brands.slice();
    out.flowerResults=results().length;
    return out;
  },enl);
  console.log(`\n══ ${enl?'ENLARGED':'STANDARD'}`);
  console.log(`   collapsed : ${r.collapsed.visible}/${r.collapsed.total} pills, ${r.collapsed.rows} rows, See more shown=${r.collapsed.moreShown}`);
  console.log(`   expanded  : ${r.expanded.visible}/${r.expanded.total} pills, ${r.expanded.rows} rows, See more shown=${r.expanded.moreShown}`);
  console.log(`   type=drink: ${r.drinkScoped.total} brands -> ${r.drinkBrands.join(', ')}`);
  console.log(`   stranded  : selected ${JSON.stringify(r.selectedOnDrink)} on drinks, after switching to flower S.brands=${JSON.stringify(r.afterSwitchToFlower)}, results=${r.flowerResults}`);
  await ctx.close();
 }
 await b.close();})();
