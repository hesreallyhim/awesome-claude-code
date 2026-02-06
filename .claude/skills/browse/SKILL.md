---
name: browse
description: Open a URL in the browser and interact with the page. Use for web navigation tasks.
disable-model-invocation: true
allowed-tools: Bash, Read, Write
---

# Browser Navigation

Navigate to a URL and interact with the page using the browser automation system.

## Usage

```
/browse https://example.com
```

## Process

1. Launch browser using `node claude-agent/scripts/browser.js $ARGUMENTS`
2. If more complex interaction is needed, write a custom script using the browser module:

```javascript
const { launchBrowser, navigateTo, takeScreenshot } = require('./claude-agent/scripts/browser');

(async () => {
  const browser = await launchBrowser();
  const page = (await browser.pages())[0];
  await navigateTo(page, '$ARGUMENTS');
  await takeScreenshot(page, 'browse-result.png');
  // Perform additional actions as needed
  await browser.close();
})();
```

3. Take a screenshot for reference
4. Report what was found on the page
