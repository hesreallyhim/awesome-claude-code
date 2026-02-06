---
name: post-x
description: Post content to X (Twitter) using browser automation. Supports text, images, and video uploads.
disable-model-invocation: true
---

# Post to X (Twitter)

Post content to X using Chrome CDP browser automation.

## Arguments
`$ARGUMENTS` = the tweet content to post

## Prerequisites
- Chrome must be logged into X.com
- browser.js module available

## Process

1. **Read the X skill**: `cat skills/x-skill.md`

2. **Launch browser and navigate**:
   ```javascript
   const b = require('./scripts/browser');
   const browser = await b.launchBrowser();
   const page = (await browser.pages())[0];
   await b.navigateTo(page, 'https://x.com/compose/post');
   ```

3. **Type the tweet**:
   ```javascript
   await page.waitForSelector('div[data-testid="tweetTextarea_0"]', { timeout: 10000 });
   await page.click('div[data-testid="tweetTextarea_0"]');
   await page.keyboard.type('$ARGUMENTS', { delay: 30 });
   ```

4. **Attach media** (if available):
   ```javascript
   // For images/video:
   const fileInput = await page.$('input[data-testid="fileInput"]');
   if (fileInput && mediaPath) {
     await fileInput.uploadFile(mediaPath);
     await new Promise(r => setTimeout(r, 3000)); // Wait for upload
   }
   ```

5. **Post**:
   ```javascript
   await page.click('div[data-testid="tweetButtonInline"]');
   await new Promise(r => setTimeout(r, 2000));
   ```

6. **Verify**: Take a screenshot to confirm the post appeared

## Tips
- Keep tweets under 280 characters
- Post video natively (not as a YouTube link) for better reach
- Add hashtags: #AI #coding #opensource
- Post GitHub link in a reply to avoid link preview replacing video
