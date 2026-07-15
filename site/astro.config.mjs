import { defineConfig } from 'astro/config';

// Static output — build to ./dist and upload to Hostinger (File Manager / FTP).
export default defineConfig({
  site: 'https://jackmotzkin.com',
  build: { assets: 'assets' },
  compressHTML: true,
});
