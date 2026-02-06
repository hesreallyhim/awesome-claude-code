# X (Twitter) Navigation Skill

## Purpose
Navigate and post on X.com using browser automation via CDP (Chrome DevTools Protocol).
No API keys required — uses a logged-in Chrome session.

## Prerequisites
- Chrome browser with an active X.com session (logged in)
- Puppeteer / browser.js loaded
- Dedicated X account for automation (recommended)

## Selectors Reference

### Compose Tweet
- **New Tweet button**: `a[data-testid="SideNav_NewTweet_Button"]`
- **Tweet text area**: `div[data-testid="tweetTextarea_0"]`
- **Post button**: `div[data-testid="tweetButtonInline"]`
- **Media upload**: `input[data-testid="fileInput"]`

### Timeline
- **Tweet articles**: `article[data-testid="tweet"]`
- **Tweet text**: `div[data-testid="tweetText"]`
- **Username**: `div[data-testid="User-Name"]`

### Navigation
- **Home**: `a[data-testid="AppTabBar_Home_Link"]`
- **Search**: `a[data-testid="AppTabBar_Explore_Link"]`
- **Notifications**: `a[data-testid="AppTabBar_Notifications_Link"]`
- **Messages**: `a[data-testid="AppTabBar_DirectMessage_Link"]`

## Workflows

### Post a Tweet
```
1. Navigate to https://x.com/compose/post (or click new tweet button)
2. Wait for selector: div[data-testid="tweetTextarea_0"]
3. Click on the text area
4. Inject text using CDP:
   - Use injectText(page, 'div[data-testid="tweetTextarea_0"]', tweetContent)
   - OR use page.keyboard.type(tweetContent) for character-by-character
5. If attaching media:
   - Click the media button
   - Upload file via input[data-testid="fileInput"]
   - Wait for upload to complete (look for thumbnail preview)
6. Click post button: div[data-testid="tweetButtonInline"]
7. Wait 2 seconds for confirmation
8. Verify post appeared in timeline
```

### Post a Tweet with Image
```
1. Follow "Post a Tweet" steps 1-4
2. Find the file input: input[accept="image/jpeg,image/png,image/webp,image/gif,video/mp4,video/quicktime"]
3. Upload file: await input.uploadFile('/path/to/image.png')
4. Wait for preview to appear
5. Click post button
```

### Read Timeline
```
1. Navigate to https://x.com/home
2. Wait for: article[data-testid="tweet"]
3. Extract tweets:
   const tweets = await page.$$eval('article[data-testid="tweet"]', articles =>
     articles.map(a => ({
       text: a.querySelector('[data-testid="tweetText"]')?.textContent,
       user: a.querySelector('[data-testid="User-Name"]')?.textContent,
     }))
   );
4. Scroll for more: await page.evaluate(() => window.scrollBy(0, 1000))
5. Wait 1 second, repeat extraction
```

### Search and Engage
```
1. Navigate to https://x.com/search?q=SEARCH_TERM&src=typed_query
2. Wait for results to load
3. Extract tweet content
4. To like: click svg[data-testid="like"] within tweet article
5. To retweet: click div[data-testid="retweet"] then confirm
6. To reply: click div[data-testid="reply"], type text, submit
```

## JavaScript Snippets

### Post Tweet via CDP
```javascript
async function postTweet(page, content) {
  await page.goto('https://x.com/compose/post', { waitUntil: 'networkidle2' });
  await page.waitForSelector('div[data-testid="tweetTextarea_0"]', { timeout: 10000 });
  await page.click('div[data-testid="tweetTextarea_0"]');
  await page.keyboard.type(content, { delay: 30 });
  await new Promise(r => setTimeout(r, 1000));
  await page.click('div[data-testid="tweetButtonInline"]');
  await new Promise(r => setTimeout(r, 2000));
  console.log('Tweet posted successfully');
}
```

### Extract Timeline
```javascript
async function readTimeline(page, count = 10) {
  await page.goto('https://x.com/home', { waitUntil: 'networkidle2' });
  await page.waitForSelector('article[data-testid="tweet"]');
  const tweets = [];
  while (tweets.length < count) {
    const newTweets = await page.$$eval('article[data-testid="tweet"]', articles =>
      articles.map(a => ({
        text: a.querySelector('[data-testid="tweetText"]')?.textContent || '',
        user: a.querySelector('[data-testid="User-Name"]')?.textContent || '',
      }))
    );
    for (const t of newTweets) {
      if (!tweets.find(e => e.text === t.text)) tweets.push(t);
    }
    if (tweets.length >= count) break;
    await page.evaluate(() => window.scrollBy(0, 800));
    await new Promise(r => setTimeout(r, 1500));
  }
  return tweets.slice(0, count);
}
```

## Troubleshooting

- **Login required**: Ensure Chrome profile is already logged in
- **Rate limiting**: Add delays between actions (2-5 seconds)
- **Selector changes**: X updates their DOM frequently; verify selectors
- **Content policy**: Text input sometimes requires keyboard.type instead of injectText
