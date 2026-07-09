import { defineConfig } from "astro/config";

// Static build → outputs to ./dist, which you upload to Hostinger's public_html.
export default defineConfig({
  site: "https://jackmotzkin.com",
  build: { inlineStylesheets: "auto" },
  compressHTML: true,
});
