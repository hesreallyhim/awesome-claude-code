#!/usr/bin/env node
/**
 * Quick Screenshot Tool
 * Usage: node scripts/screenshot.js <url> [filename]
 */

const browser = require('./browser');

const url = process.argv[2];
const filename = process.argv[3] || `screenshot-${Date.now()}.png`;

if (!url) {
  console.log('Usage: node scripts/screenshot.js <url> [filename]');
  process.exit(0);
}

(async () => {
  const b = await browser.launchBrowser({ userDataDir: undefined });
  const page = (await b.pages())[0] || (await b.newPage());
  await browser.navigateTo(page, url);
  await browser.sleep(2000);
  const fp = await browser.screenshot(page, filename);
  console.log(`Screenshot saved: ${fp}`);
  await b.close();
})().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
