#!/usr/bin/env node
/**
 * Browser Automation Module
 * Controls Chrome via CDP (Chrome DevTools Protocol) using Puppeteer.
 * Used by the AI agent to navigate web applications autonomously.
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

// Configuration
const CONFIG = {
  chromePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  userDataDir: process.env.CHROME_USER_DATA || path.join(process.env.HOME || '/root', '.config/chromium'),
  screenshotDir: path.join(__dirname, '..', 'output', 'screenshots'),
  headless: process.env.HEADLESS === 'true',
  defaultTimeout: 30000,
  viewport: { width: 1920, height: 1080 },
};

// Ensure output directories exist
if (!fs.existsSync(CONFIG.screenshotDir)) {
  fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
}

/**
 * Launch browser with pre-existing user profile (so sessions are preserved)
 */
async function launchBrowser(options = {}) {
  const browser = await puppeteer.launch({
    headless: CONFIG.headless,
    executablePath: CONFIG.chromePath,
    userDataDir: options.userDataDir || CONFIG.userDataDir,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      `--window-size=${CONFIG.viewport.width},${CONFIG.viewport.height}`,
    ],
    defaultViewport: CONFIG.viewport,
  });

  console.log('[Browser] Launched successfully');
  return browser;
}

/**
 * Navigate to a URL and wait for page load
 */
async function navigateTo(page, url, waitUntil = 'networkidle2') {
  console.log(`[Browser] Navigating to: ${url}`);
  await page.goto(url, {
    waitUntil,
    timeout: CONFIG.defaultTimeout,
  });
  console.log(`[Browser] Page loaded: ${url}`);
}

/**
 * Wait for a selector to appear on the page
 */
async function waitForSelector(page, selector, timeout = CONFIG.defaultTimeout) {
  console.log(`[Browser] Waiting for selector: ${selector}`);
  await page.waitForSelector(selector, { timeout });
  console.log(`[Browser] Found selector: ${selector}`);
}

/**
 * Click an element by CSS selector
 */
async function clickElement(page, selector) {
  await waitForSelector(page, selector);
  await page.click(selector);
  console.log(`[Browser] Clicked: ${selector}`);
}

/**
 * Type text into an input field
 */
async function typeText(page, selector, text, options = {}) {
  await waitForSelector(page, selector);
  await page.click(selector);
  if (options.clear) {
    await page.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (el) el.value = '';
    }, selector);
  }
  await page.type(selector, text, { delay: options.delay || 50 });
  console.log(`[Browser] Typed text into: ${selector}`);
}

/**
 * Inject text directly into an element using JavaScript (bypasses input restrictions)
 */
async function injectText(page, selector, text) {
  await page.evaluate(
    (sel, txt) => {
      const element = document.querySelector(sel);
      if (element) {
        // For contenteditable elements
        if (element.contentEditable === 'true') {
          element.textContent = txt;
          element.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
          // For input/textarea elements
          const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype,
            'value'
          )?.set || Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype,
            'value'
          )?.set;
          if (nativeInputValueSetter) {
            nativeInputValueSetter.call(element, txt);
          } else {
            element.value = txt;
          }
          element.dispatchEvent(new Event('input', { bubbles: true }));
          element.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
    },
    selector,
    text
  );
  console.log(`[Browser] Injected text into: ${selector}`);
}

/**
 * Take a screenshot and save it
 */
async function takeScreenshot(page, filename) {
  const filepath = path.join(CONFIG.screenshotDir, filename || `screenshot-${Date.now()}.png`);
  await page.screenshot({ path: filepath, fullPage: false });
  console.log(`[Browser] Screenshot saved: ${filepath}`);
  return filepath;
}

/**
 * Take a full-page screenshot
 */
async function takeFullPageScreenshot(page, filename) {
  const filepath = path.join(CONFIG.screenshotDir, filename || `fullpage-${Date.now()}.png`);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`[Browser] Full page screenshot saved: ${filepath}`);
  return filepath;
}

/**
 * Extract text content from the page
 */
async function extractText(page, selector) {
  const text = await page.evaluate((sel) => {
    if (sel) {
      const elements = document.querySelectorAll(sel);
      return Array.from(elements).map((el) => el.textContent?.trim()).filter(Boolean);
    }
    return [document.body.textContent?.trim()];
  }, selector);
  return text;
}

/**
 * Scroll down the page
 */
async function scrollDown(page, amount = 500) {
  await page.evaluate((px) => window.scrollBy(0, px), amount);
  console.log(`[Browser] Scrolled down ${amount}px`);
}

/**
 * Scroll to bottom of page
 */
async function scrollToBottom(page) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  console.log('[Browser] Scrolled to bottom');
}

/**
 * Wait for a specified duration
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Execute arbitrary JavaScript in the page context
 */
async function executeScript(page, scriptFn, ...args) {
  return page.evaluate(scriptFn, ...args);
}

/**
 * Get all links on the page
 */
async function getLinks(page, selector = 'a') {
  return page.evaluate((sel) => {
    const links = document.querySelectorAll(sel);
    return Array.from(links).map((a) => ({
      href: a.href,
      text: a.textContent?.trim(),
    }));
  }, selector);
}

/**
 * Check if an element exists on the page
 */
async function elementExists(page, selector) {
  const element = await page.$(selector);
  return element !== null;
}

/**
 * Upload a file to a file input
 */
async function uploadFile(page, selector, filePath) {
  const input = await page.$(selector);
  if (input) {
    await input.uploadFile(filePath);
    console.log(`[Browser] Uploaded file: ${filePath}`);
  }
}

/**
 * Close all pages except the first one
 */
async function closeExtraTabs(browser) {
  const pages = await browser.pages();
  for (let i = pages.length - 1; i > 0; i--) {
    await pages[i].close();
  }
  console.log('[Browser] Closed extra tabs');
}

// Export all functions
module.exports = {
  launchBrowser,
  navigateTo,
  waitForSelector,
  clickElement,
  typeText,
  injectText,
  takeScreenshot,
  takeFullPageScreenshot,
  extractText,
  scrollDown,
  scrollToBottom,
  sleep,
  executeScript,
  getLinks,
  elementExists,
  uploadFile,
  closeExtraTabs,
  CONFIG,
};

// CLI mode: run a quick test if called directly
if (require.main === module) {
  const url = process.argv[2] || 'https://example.com';
  (async () => {
    const browser = await launchBrowser({ userDataDir: undefined });
    const page = (await browser.pages())[0] || (await browser.newPage());
    await navigateTo(page, url);
    const title = await page.title();
    console.log(`[Browser] Page title: ${title}`);
    await takeScreenshot(page, 'test-screenshot.png');
    await browser.close();
    console.log('[Browser] Test complete');
  })().catch((err) => {
    console.error('[Browser] Error:', err.message);
    process.exit(1);
  });
}
