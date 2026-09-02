const {chromium} = require('/opt/node22/lib/node_modules/playwright/index.js');
/* Guard for Enlarged view's type scale. Absolute pixel sizes are not enough:
   Enlarged puts one card across, so a card more than doubles in width, and a
   type curve tuned on its own leaves every element proportionally SMALLER than
   in Standard while every value has grown. This prints each element as a
   percentage of its card in both modes — that is the number to compare.
     node ratio.js /path/to/origins-app.html                                  */
const APP = process.argv[2] || './origins-app.html';
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
 const p=await b.newPage({viewport:{width:900,height:1200}});
 await p.goto('file://'+require('path').resolve(APP)); await p.waitForTimeout(2400);
 for(const enl of [false,true]){
   const r=await p.evaluate(async(enl)=>{
     setAdv('enlarged',enl); S.type='flower'; renderList(); nav('list');
     await new Promise(r=>setTimeout(r,300));
     const card=document.querySelector('.pgrid .fcard');
     const w=card.getBoundingClientRect().width;
     const get=s=>{const e=card.querySelector(s);return e?parseFloat(getComputedStyle(e).fontSize):null;};
     return {cardW:Math.round(w), name:get('.fnm'), brand:get('.fbr'),
             crumb:get('.fbc'), price:get('.fpr'), bub:get('.bub'),
             pill:get('.fsz'), cta:get('.fmore')||get('.fadd')};
   },enl);
   const pct=v=>v?((100*v/r.cardW).toFixed(2)+'%'):'-';
   console.log(`\n${enl?'ENLARGED':'STANDARD'}  card=${r.cardW}px`);
   console.log('  element      size    as % of card width');
   for(const k of ['name','brand','crumb','price','bub','pill','cta'])
     console.log(`  ${k.padEnd(11)} ${String(r[k]).padEnd(7)} ${pct(r[k])}`);
 }
 await b.close();})();
