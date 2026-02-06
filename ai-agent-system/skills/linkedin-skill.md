# LinkedIn Skill

## Purpose
Post content, send messages, and manage connections on LinkedIn via browser automation.

## Prerequisites
- Chrome with active LinkedIn session (logged in)
- `scripts/browser.js` loaded
- Dedicated automation account recommended

## Selectors Reference

| Element | Selector |
|---------|----------|
| Start a post | `button.share-box-feed-entry__trigger` |
| Text editor | `div.ql-editor[data-placeholder*="talk about"]` |
| Post button | `button.share-actions__primary-action` |
| Add photo | `button[aria-label="Add a photo"]` |
| Media input | `input.image-sharing-detour-container__file-input` |
| Post containers | `div.feed-shared-update-v2` |
| Post text | `span.break-words` |
| Like button | `button[aria-label*="Like"]` |
| Comment button | `button[aria-label*="Comment"]` |
| New message | `button.msg-overlay-bubble-header__control--new-convo-btn` |
| Message input | `div.msg-form__contenteditable` |
| Send button | `button.msg-form__send-button` |

## Workflows

### Create a Post
```
1. Navigate to https://www.linkedin.com/feed/
2. Click: button.share-box-feed-entry__trigger
3. Wait 1.5s for modal
4. Click: div.ql-editor
5. Type content: page.keyboard.type(content, { delay: 20 })
6. If attaching media:
   a. Click "Add a photo" button
   b. Upload file via file input
   c. Wait 3s for preview
7. Click: button.share-actions__primary-action
8. Wait 3s for confirmation
```

### Send a Direct Message
```
1. Navigate to https://www.linkedin.com/messaging/
2. Click new message button
3. Type recipient name in search
4. Wait 2s for suggestions
5. Click correct contact
6. Click message input: div.msg-form__contenteditable
7. Type message
8. Click send: button.msg-form__send-button
```

### Connect with Someone
```
1. Navigate to person's profile
2. Click: button[aria-label*="connect" i]
3. Optional: Click "Add a note", type personalized message
4. Click "Send"
```

## Code Snippets

### Post on LinkedIn
```javascript
const b = require('./scripts/browser');
async function postLinkedIn(content) {
  const browser = await b.launchBrowser();
  const page = (await browser.pages())[0];
  await b.navigateTo(page, 'https://www.linkedin.com/feed/');
  await b.waitFor(page, 'button.share-box-feed-entry__trigger');
  await page.click('button.share-box-feed-entry__trigger');
  await b.sleep(1500);
  await b.waitFor(page, 'div.ql-editor');
  await page.click('div.ql-editor');
  await page.keyboard.type(content, { delay: 20 });
  await b.sleep(1000);
  await page.click('button.share-actions__primary-action');
  await b.sleep(3000);
  await b.screenshot(page, 'linkedin-posted.png');
  await browser.close();
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login wall | Ensure Chrome profile has active LinkedIn session |
| Rate limited | LinkedIn is aggressive; 3-5s delays minimum |
| Selector changed | LinkedIn updates frequently; verify in DevTools |
| Connection limit | ~100 requests/week; track count |
| Post not visible | Check for spam trigger words |
