const {chromium}=require('/opt/node22/lib/node_modules/playwright/index.js');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const enl of [false,true]){
 const ctx=await b.newContext({viewport:{width:900,height:1200}});const p=await ctx.newPage();
 await p.goto('file://'+path.resolve(process.argv[2]));await p.waitForTimeout(2400);
 console.log(`\n== ${enl?'ENLARGED':'STANDARD'} ==`);
 console.log(await p.evaluate(async(enl)=>{
  setAdv('enlarged',enl);nav('home');await new Promise(r=>setTimeout(r,400));
  const out=[];
  const rows=[...document.querySelectorAll('#deals .hrow')];
  for(const[i,h]of rows.entries()){
   const r=h.firstElementChild;
   const arr=h.querySelector('.rowarr.next'),ab=arr.getBoundingClientRect();
   const k=r.getBoundingClientRect().width/r.clientWidth;
   out.push(` row ${i+1} (${r.className}) scrollW ${r.scrollWidth} clientW ${r.clientWidth}  can-next:${h.classList.contains('can-next')} can-prev:${h.classList.contains('can-prev')}  arrow ${(ab.width/k).toFixed(0)}px`);
   // tap next, then check state flips
   arr.click();await new Promise(r2=>setTimeout(r2,700));
   out.push(`   after tap: scrollLeft ${Math.round(r.scrollLeft)}  can-prev:${h.classList.contains('can-prev')} can-next:${h.classList.contains('can-next')}`);
  }
  // the documented trap: an element with its own height inside .dealrow stretches every tile
  const hs=[...document.querySelectorAll('#deals .dealrow .fcard')].map(c=>+c.getBoundingClientRect().height.toFixed(1));
  const bt=[...document.querySelectorAll('#deals .brandrow .btile')].map(c=>+c.getBoundingClientRect().height.toFixed(1));
  out.push(` deal tile heights: ${[...new Set(hs)].join(', ')}   brand tile heights: ${[...new Set(bt)].join(', ')}`);
  return out.join('\n');
 },enl));
 await ctx.close();
}
await b.close();})();
