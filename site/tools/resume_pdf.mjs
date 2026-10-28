// Print the built /resume page to a one-page Letter PDF.
// Run after `npm run build`:  node tools/resume_pdf.mjs
// Writes public/resume/jack-motzkin-resume.pdf (and the same file into dist/resume/),
// and fails if the résumé runs onto a second page.
import { createServer } from 'node:http';
import { readFile, mkdir, copyFile } from 'node:fs/promises';
import { extname, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const SITE = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(SITE, 'dist');
const OUT = join(SITE, 'public/resume/jack-motzkin-resume.pdf');
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.png': 'image/png' };
const server = createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (path.endsWith('/')) path += 'index.html';
  try { res.writeHead(200, { 'content-type': types[extname(path)] || 'application/octet-stream' }); res.end(await readFile(join(DIST, path))); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage();
// print from the light theme (the dark one tints the page margins)
await page.addInitScript(() => { try { localStorage.setItem('motz-theme', 'light'); } catch (e) {} });
await page.emulateMedia({ media: 'print', reducedMotion: 'reduce' });
await page.goto(`http://localhost:${port}/resume/`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await mkdir(dirname(OUT), { recursive: true });
const pdf = await page.pdf({ path: OUT, preferCSSPageSize: true, printBackground: true, tagged: true, outline: false });
const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
await browser.close();
server.close();
await mkdir(join(DIST, 'resume'), { recursive: true });
await copyFile(OUT, join(DIST, 'resume/jack-motzkin-resume.pdf'));
console.log(`${OUT}  ${Math.round(pdf.length / 1024)} KB, ${pages} page(s)`);
if (pages !== 1) { console.error('The résumé no longer fits on one page: tighten src/data/resume.js.'); process.exit(1); }
