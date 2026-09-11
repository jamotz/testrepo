/* Audits every option the filter drawer offers by driving the app's own
 * match() against it, so the counts are what a shopper would actually see
 * rather than what the code looks like it does.
 *
 *   node filter-audit.js <built-app.html>
 *
 * It prints every facet option with its product count, flags any that match
 * NOTHING, lists catalog brands the drawer fails to offer, and ends with the
 * share of the catalog reachable through the Brands facet.
 *
 * WHY IT EXISTS
 * The hand-written BRANDS list had drifted until four of its six options
 * matched zero products and 43 of the catalog's 45 brands were unreachable --
 * 15 of 308 products, 5%. Nothing caught it because nothing was counting.
 * Reading the code would not have found it either: every option looked
 * plausible. Only running the real match() over the real catalog showed it.
 *
 * Run it after any change to the catalog, to match(), or to a facet's options.
 *
 * A NOTE ON ITS OWN FRAGILITY, LEARNED THE HARD WAY
 * This script reaches into app globals (P, S, match, TYPES, FEEL, brandList).
 * When BRANDS became brandList() the script threw ReferenceError -- and the
 * shell pipeline that grepped its output for "MATCHES NOTHING" then reported
 * "none", a clean bill of health from a script that had crashed. If you wrap
 * this in a pipeline, check the exit status, not just the text.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');
const path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
 const ctx=await b.newContext(); const p=await ctx.newPage();
 await p.goto('file://'+path.resolve(process.argv[2])); await p.waitForTimeout(2200);
 const out=await p.evaluate(()=>{
   const reset=()=>{S.type=null;S.strain=null;S.sub=null;S.sub2=null;S.sub3=null;
     S.eform=null;S.mood=null;S.brands=[];S.sale=false;S.size=null;S.thc=null;S.deal=null;};
   const count=()=>{reset.call?0:0; return P.filter(match).length;};
   const r={total:P.length, facets:{}, catalogBrands:{}};
   P.forEach(x=>{r.catalogBrands[x.b]=(r.catalogBrands[x.b]||0)+1;});

   reset(); r.facets.BRANDS=brandList().map(bn=>{reset();S.brands=[bn];return [bn,P.filter(match).length];});
   reset(); r.facets.FEELING=Object.keys(FEEL).map(k=>{reset();S.mood=k;return [k,P.filter(match).length];});
   reset(); r.facets.TYPE=Object.keys(TYPES).map(k=>{reset();S.type=k;return [TYPES[k],P.filter(match).length];});
   reset(); r.facets.THC=[["low"],["mod"],["high"],["cbd"]].map(o=>{reset();S.thc=o[0];return [o[0],P.filter(match).length];});
   reset(); r.facets.EFORM=(typeof EFORMS!=='undefined'?EFORMS:[]).map(x=>{reset();S.type="edible";S.eform=x;return [x,P.filter(match).length];});
   reset(); S.sale=true; r.facets.SALE=[["on sale",P.filter(match).length]];
   // sizes offered for each type
   r.sizes={};
   Object.keys(TYPES).forEach(t=>{
     const set={};
     P.filter(x=>x.t===t).forEach(x=>(sizesFor(x)||[]).forEach(s=>set[s]=1));
     r.sizes[t]=Object.keys(set).map(s=>{reset();S.type=t;S.size=s;return [s,P.filter(match).length];});
   });
   reset();
   return r;
 });
 await b.close();

 console.log(`catalog: ${out.total} products\n`);
 const show=(name,rows)=>{
   console.log(`── ${name} ──`);
   rows.forEach(([k,n])=>console.log(`   ${String(n).padStart(4)}  ${k}${n===0?'   <-- MATCHES NOTHING':''}`));
   console.log();
 };
 show('BRANDS facet', out.facets.BRANDS);
 show('FEELING facet', out.facets.FEELING);
 show('PRODUCT TYPE facet', out.facets.TYPE);
 show('THC facet', out.facets.THC);
 if(out.facets.EFORM.length) show('EDIBLE FORM facet (type=edible)', out.facets.EFORM);
 show('ON SALE', out.facets.SALE);
 for(const [t,rows] of Object.entries(out.sizes)) if(rows.some(r=>r[1]===0)) show(`SIZE facet — ${t} (only zero-rows shown)`, rows.filter(r=>r[1]===0));

 const offered=new Set(out.facets.BRANDS.map(r=>r[0]));
 const missing=Object.entries(out.catalogBrands).filter(([b])=>!offered.has(b)).sort((a,b)=>b[1]-a[1]);
 console.log(`── brands IN THE CATALOG but NOT offered in the drawer (${missing.length}) ──`);
 missing.forEach(([b,n])=>console.log(`   ${String(n).padStart(4)}  ${b}`));
 const reach=out.facets.BRANDS.reduce((a,r)=>a+r[1],0);
 console.log(`\nreachable via the Brands facet: ${reach} of ${out.total} products (${(100*reach/out.total).toFixed(0)}%)`);
})();
