---
name: browse
description: Open a URL in the automated browser, take a screenshot, and optionally interact with the page. Uses Chrome CDP via Puppeteer.
disable-model-invocation: true
---

# Browser Navigation

Navigate to a URL using the automated browser and capture the result.

## Arguments
`$ARGUMENTS` = URL to navigate to

## Process

1. **Quick check**: Ensure Chrome/Chromium is available
   ```bash
   which google-chrome || which chromium-browser || echo "Chrome not found"
   ```

2. **Navigate**: Use the browser module
   ```bash
   node scripts/browser.js "$ARGUMENTS"
   ```
   This will:
   - Launch Chrome with the saved user profile
   - Navigate to the URL
   - Take a screenshot → `output/screenshots/`
   - Print the page title
   - Close the browser

3. **Read the screenshot**: Display or report what was found

4. **Interact** (if follow-up needed):
   Write a temporary script using the browser API:
   ```javascript
   const browser = require('./scripts/browser');
   (async () => {
     const b = await browser.launchBrowser();
     const page = (await b.pages())[0];
     await browser.navigateTo(page, '$ARGUMENTS');
     // Custom interactions here:
     // await browser.clickElement(page, 'button.submit');
     // await browser.typeText(page, 'input#search', 'query');
     await browser.takeScreenshot(page, 'result.png');
     await b.close();
   })();
   ```

## Important
- Browser must be logged into the target site for authenticated pages
- Add 2-3 second delays between interactions to avoid rate limits
- Screenshots are saved to `output/screenshots/`
