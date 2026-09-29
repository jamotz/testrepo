// Full-page screenshots of every wizard screen for the portfolio case study's
// MVP / Hi-Fi gallery. Run after asm_wizard.py (it reads the proto.html that
// asm_wizard.py writes): node reference/oxfam/wizard-build/case_shots.js
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/node22/lib/node_modules/playwright');

const REPO = path.resolve(__dirname, '../../..');
const OUT = path.join(REPO, 'site/public/work/oxfam');
const SCREENS = ['landing', 'faq', 'feedback', 'myoxfam-signin', 'create-account',
                 'portal', 'fundraising', 'media', 'report'];

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ viewport: { width: 1040, height: 900 } });
  await page.goto('file://' + path.join(OUT, 'proto.html'));
  for (const id of SCREENS) {
    await page.evaluate((s) => nav(s), id);
    await page.waitForTimeout(200);
    const png = path.join(OUT, `hifi-${id}.png`);
    await page.screenshot({ path: png, fullPage: true });
    // downscale + JPEG to match the other gallery images
    execFileSync('python3', ['-c',
      'import sys;from PIL import Image;im=Image.open(sys.argv[1]).convert("RGB");' +
      'w=820;im=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS);' +
      'im.save(sys.argv[2],"JPEG",quality=80,optimize=True);import os;os.remove(sys.argv[1])',
      png, png.replace(/\.png$/, '.jpg')]);
    console.log('wrote', path.relative(REPO, png.replace(/\.png$/, '.jpg')));
  }
  await browser.close();
})();
