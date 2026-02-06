# LinkedIn Navigation Skill

## Purpose
Navigate LinkedIn for networking, messaging, and content posting using browser automation.
No API keys required — uses a logged-in Chrome session.

## Prerequisites
- Chrome browser with active LinkedIn session (logged in)
- Puppeteer / browser.js loaded
- Dedicated LinkedIn account for automation (recommended)

## Selectors Reference

### Navigation
- **Home feed**: `https://www.linkedin.com/feed/`
- **My Network**: `https://www.linkedin.com/mynetwork/`
- **Messaging**: `https://www.linkedin.com/messaging/`
- **Profile**: `https://www.linkedin.com/in/me/`

### Post Creation
- **Start a post button**: `button.share-box-feed-entry__trigger`
- **Text editor**: `div.ql-editor[data-placeholder="What do you want to talk about?"]`
- **Post button**: `button.share-actions__primary-action`
- **Add photo**: `button[aria-label="Add a photo"]`
- **Media input**: `input.image-sharing-detour-container__file-input`

### Feed
- **Post containers**: `div.feed-shared-update-v2`
- **Post text**: `span.break-words`
- **Like button**: `button[aria-label*="Like"]`
- **Comment button**: `button[aria-label*="Comment"]`

### Messaging
- **New message**: `button.msg-overlay-bubble-header__control--new-convo-btn`
- **Search contacts**: `input.msg-connections-typeahead__search-field`
- **Message input**: `div.msg-form__contenteditable`
- **Send button**: `button.msg-form__send-button`

## Workflows

### Create a LinkedIn Post
```
1. Navigate to https://www.linkedin.com/feed/
2. Click: button.share-box-feed-entry__trigger
3. Wait for modal with text editor
4. Click on: div.ql-editor
5. Type post content using keyboard.type()
6. If attaching image:
   - Click "Add a photo" button
   - Upload file via file input
   - Wait for preview
7. Click the "Post" button: button.share-actions__primary-action
8. Wait 2 seconds for confirmation
```

### Send a Direct Message
```
1. Navigate to https://www.linkedin.com/messaging/
2. Click "New message" button
3. In the search field, type the recipient name
4. Wait for dropdown suggestions
5. Click on the correct contact
6. Click on the message input: div.msg-form__contenteditable
7. Type message content
8. Click send: button.msg-form__send-button
9. Verify "Sent" confirmation
```

### Connect with Someone
```
1. Navigate to the person's profile page
2. Look for "Connect" button: button[aria-label*="connect" i]
3. Click Connect
4. If "Add a note" option appears:
   - Click "Add a note"
   - Type personalized message
   - Click "Send"
5. Otherwise just confirm the connection request
```

### Read Feed
```
1. Navigate to https://www.linkedin.com/feed/
2. Wait for: div.feed-shared-update-v2
3. Extract posts:
   const posts = await page.$$eval('div.feed-shared-update-v2', items =>
     items.map(item => ({
       author: item.querySelector('.update-components-actor__name')?.textContent?.trim(),
       content: item.querySelector('span.break-words')?.textContent?.trim(),
     }))
   );
4. Scroll for more content
```

### Search for People
```
1. Navigate to https://www.linkedin.com/search/results/people/?keywords=SEARCH_TERM
2. Wait for results to load
3. Extract names and profiles
4. Click "Connect" or "Message" as needed
```

## JavaScript Snippets

### Post Content
```javascript
async function postOnLinkedIn(page, content) {
  await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.share-box-feed-entry__trigger', { timeout: 10000 });
  await page.click('button.share-box-feed-entry__trigger');
  await page.waitForSelector('div.ql-editor', { timeout: 5000 });
  await page.click('div.ql-editor');
  await page.keyboard.type(content, { delay: 20 });
  await new Promise(r => setTimeout(r, 1000));
  await page.click('button.share-actions__primary-action');
  await new Promise(r => setTimeout(r, 3000));
  console.log('LinkedIn post published');
}
```

### Send Message
```javascript
async function sendLinkedInMessage(page, recipientName, message) {
  await page.goto('https://www.linkedin.com/messaging/', { waitUntil: 'networkidle2' });
  // Click new message
  await page.click('button.msg-overlay-bubble-header__control--new-convo-btn');
  await new Promise(r => setTimeout(r, 1000));
  // Search for recipient
  const searchInput = await page.waitForSelector('input[placeholder*="Type a name"]');
  await searchInput.type(recipientName, { delay: 50 });
  await new Promise(r => setTimeout(r, 2000));
  // Select first result
  await page.click('li.msg-connections-typeahead__result-item');
  await new Promise(r => setTimeout(r, 1000));
  // Type and send message
  await page.click('div.msg-form__contenteditable');
  await page.keyboard.type(message, { delay: 20 });
  await page.click('button.msg-form__send-button');
  console.log(`Message sent to ${recipientName}`);
}
```

## Troubleshooting

- **Login wall**: Ensure Chrome profile has active LinkedIn session
- **Rate limiting**: LinkedIn aggressively limits automation; add 3-5 sec delays
- **Selector changes**: LinkedIn updates their UI frequently; verify selectors
- **Connection limits**: LinkedIn caps weekly connection requests (~100/week)
