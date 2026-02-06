#!/usr/bin/env node
/**
 * Browser Automation Module
 * =========================
 * Controls Chrome via CDP (Chrome DevTools Protocol) using puppeteer-core.
 * Pre-existing Chrome user profiles preserve login sessions.
 *
 * Usage:
 *   node scripts/browser.js <url>               # Navigate + screenshot
 *   const b = require('./scripts/browser');      # Use as module
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

// Load env if available
try { require('dotenv').config({ path: path.join(__dirname, '..', 'config', '.env') }); } catch {}

const CONFIG = {
  chromePath: process.env.CHROME_PATH || findChrome(),
  userDataDir: process.env.CHROME_USER_DATA || path.join(process.env.HOME || '/root', '.config/chromium'),
  screenshotDir: path.join(__dirname, '..', 'output', 'screenshots'),
  headless: process.env.HEADLESS === 'true',
  defaultTimeout: 30000,
  viewport: { width: 1920, height: 1080 },
};

function findChrome() {
  const candidates = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return 'google-chrome'; // fallback — let PATH resolve it
}

// Ensure output dirs exist
fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });

// ─── Core Functions ───────────────────────────────────────────────

async function launchBrowser(options = {}) {
  const browser = await puppeteer.launch({
    headless: options.headless ?? CONFIG.headless,
    executablePath: options.chromePath || CONFIG.chromePath,
    userDataDir: options.userDataDir || CONFIG.userDataDir,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      `--window-size=${CONFIG.viewport.width},${CONFIG.viewport.height}`,
    ],
    defaultViewport: CONFIG.viewport,
  });
  console.log('[browser] launched');
  return browser;
}

async function navigateTo(page, url, waitUntil = 'networkidle2') {
  console.log(`[browser] navigating → ${url}`);
  await page.goto(url, { waitUntil, timeout: CONFIG.defaultTimeout });
  console.log(`[browser] loaded: ${await page.title()}`);
}

async function waitFor(page, selector, timeout = CONFIG.defaultTimeout) {
  await page.waitForSelector(selector, { timeout });
}

async function click(page, selector) {
  await waitFor(page, selector);
  await page.click(selector);
  console.log(`[browser] clicked: ${selector}`);
}

async function type(page, selector, text, options = {}) {
  await waitFor(page, selector);
  await page.click(selector);
  if (options.clear) {
    await page.evaluate((s) => { const el = document.querySelector(s); if (el) el.value = ''; }, selector);
  }
  await page.type(selector, text, { delay: options.delay || 50 });
  console.log(`[browser] typed into: ${selector}`);
}

async function injectText(page, selector, text) {
  await page.evaluate((s, t) => {
    const el = document.querySelector(s);
    if (!el) return;
    if (el.contentEditable === 'true') {
      el.textContent = t;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      const setter =
        Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set ||
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
      if (setter) setter.call(el, t);
      else el.value = t;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }, selector, text);
  console.log(`[browser] injected text into: ${selector}`);
}

async function screenshot(page, filename) {
  const fp = path.join(CONFIG.screenshotDir, filename || `shot-${Date.now()}.png`);
  await page.screenshot({ path: fp, fullPage: false });
  console.log(`[browser] screenshot → ${fp}`);
  return fp;
}

async function fullScreenshot(page, filename) {
  const fp = path.join(CONFIG.screenshotDir, filename || `full-${Date.now()}.png`);
  await page.screenshot({ path: fp, fullPage: true });
  console.log(`[browser] full screenshot → ${fp}`);
  return fp;
}

async function extractText(page, selector) {
  return page.evaluate((s) => {
    if (s) {
      return Array.from(document.querySelectorAll(s))
        .map((el) => el.textContent?.trim())
        .filter(Boolean);
    }
    return [document.body.textContent?.trim()];
  }, selector);
}

async function scrollDown(page, px = 500) {
  await page.evaluate((n) => window.scrollBy(0, n), px);
}

async function scrollToBottom(page) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
}

async function getLinks(page, selector = 'a') {
  return page.evaluate((s) =>
    Array.from(document.querySelectorAll(s)).map((a) => ({
      href: a.href,
      text: a.textContent?.trim(),
    })), selector);
}

async function exists(page, selector) {
  return (await page.$(selector)) !== null;
}

async function uploadFile(page, selector, filePath) {
  const input = await page.$(selector);
  if (input) {
    await input.uploadFile(filePath);
    console.log(`[browser] uploaded: ${filePath}`);
  }
}

async function exec(page, fn, ...args) {
  return page.evaluate(fn, ...args);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

// ─── Exports ──────────────────────────────────────────────────────

module.exports = {
  launchBrowser, navigateTo, waitFor, click, type, injectText,
  screenshot, fullScreenshot, extractText, scrollDown, scrollToBottom,
  getLinks, exists, uploadFile, exec, sleep, CONFIG,
};

// ─── CLI Mode ─────────────────────────────────────────────────────

if (require.main === module) {
  const url = process.argv[2];
  if (!url) {
    console.log('Usage: node scripts/browser.js <url>');
    console.log('  Opens Chrome, navigates to <url>, takes a screenshot');
    process.exit(0);
  }
  (async () => {
    const browser = await launchBrowser({ userDataDir: undefined });
    const page = (await browser.pages())[0] || (await browser.newPage());
    await navigateTo(page, url);
    const title = await page.title();
    console.log(`[browser] title: ${title}`);
    await screenshot(page, 'browse-result.png');
    await browser.close();
  })().catch((err) => {
    console.error('[browser] error:', err.message);
    process.exit(1);
  });
}
