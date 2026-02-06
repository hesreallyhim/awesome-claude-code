---
name: post-linkedin
description: Post content to LinkedIn using browser automation. Creates professional posts with media attachments.
disable-model-invocation: true
---

# Post to LinkedIn

Post professional content to LinkedIn using Chrome CDP browser automation.

## Arguments
`$ARGUMENTS` = the post content

## Prerequisites
- Chrome must be logged into LinkedIn.com
- browser.js module available

## Process

1. **Read the LinkedIn skill**: `cat skills/linkedin-skill.md`

2. **Launch browser and navigate**:
   ```javascript
   const b = require('./scripts/browser');
   const browser = await b.launchBrowser();
   const page = (await browser.pages())[0];
   await b.navigateTo(page, 'https://www.linkedin.com/feed/');
   ```

3. **Open post composer**:
   ```javascript
   await page.waitForSelector('button.share-box-feed-entry__trigger', { timeout: 10000 });
   await page.click('button.share-box-feed-entry__trigger');
   await new Promise(r => setTimeout(r, 1500));
   ```

4. **Type the post**:
   ```javascript
   await page.waitForSelector('div.ql-editor', { timeout: 5000 });
   await page.click('div.ql-editor');
   await page.keyboard.type('$ARGUMENTS', { delay: 20 });
   ```

5. **Post**:
   ```javascript
   await page.click('button.share-actions__primary-action');
   await new Promise(r => setTimeout(r, 3000));
   ```

6. **Verify**: Take a screenshot to confirm

## LinkedIn Post Tips
- Open with a personal hook (not "I'm excited to announce...")
- Use line breaks for readability (LinkedIn loves white space)
- Include a call-to-action (question or ask for feedback)
- Add 3-5 relevant hashtags at the bottom
- Best posting times: Tuesday-Thursday, 8-10 AM
