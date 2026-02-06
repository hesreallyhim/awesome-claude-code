# X (Twitter) Skill

## Purpose
Navigate and post on X.com using browser automation via CDP. No API keys required.

## Prerequisites
- Chrome with active X.com session (logged in)
- `scripts/browser.js` loaded
- Dedicated automation account recommended

## Selectors Reference

| Element | Selector |
|---------|----------|
| New Tweet button | `a[data-testid="SideNav_NewTweet_Button"]` |
| Tweet textarea | `div[data-testid="tweetTextarea_0"]` |
| Post button | `div[data-testid="tweetButtonInline"]` |
| Media input | `input[data-testid="fileInput"]` |
| Tweet articles | `article[data-testid="tweet"]` |
| Tweet text | `div[data-testid="tweetText"]` |
| Username | `div[data-testid="User-Name"]` |
| Like button | `button[data-testid="like"]` |
| Retweet button | `button[data-testid="retweet"]` |
| Reply button | `button[data-testid="reply"]` |
| Home link | `a[data-testid="AppTabBar_Home_Link"]` |
| Explore link | `a[data-testid="AppTabBar_Explore_Link"]` |

## Workflows

### Post a Tweet
```
1. Navigate to https://x.com/compose/post
2. Wait: div[data-testid="tweetTextarea_0"] (timeout 10s)
3. Click the textarea
4. Type content: page.keyboard.type(content, { delay: 30 })
5. Wait 1 second
6. Click: div[data-testid="tweetButtonInline"]
7. Wait 2 seconds for confirmation
8. Take screenshot to verify
```

### Post with Image
```
1. Follow "Post a Tweet" steps 1-4
2. Find file input: input[accept*="image/jpeg"]
3. Upload: await input.uploadFile('/path/to/image.png')
4. Wait 3 seconds for upload/preview
5. Click post button
```

### Post with Video
```
1. Follow "Post a Tweet" steps 1-4
2. Upload video via file input (MP4, max 512MB, max 2:20)
3. Wait for processing (10-30 seconds)
4. Click post button
5. Post GitHub link as reply (to preserve video preview)
```

### Read Timeline
```
1. Navigate to https://x.com/home
2. Wait: article[data-testid="tweet"]
3. Extract:
   page.$$eval('article[data-testid="tweet"]', articles =>
     articles.map(a => ({
       text: a.querySelector('[data-testid="tweetText"]')?.textContent,
       user: a.querySelector('[data-testid="User-Name"]')?.textContent,
     }))
   )
4. Scroll: window.scrollBy(0, 800)
5. Wait 1.5s, repeat
```

### Search
```
1. Navigate to https://x.com/search?q=QUERY&src=typed_query
2. Wait for results
3. Extract tweet data
4. Scroll for more results
```

## Code Snippets

### Post Tweet
```javascript
const b = require('./scripts/browser');
async function postTweet(content) {
  const browser = await b.launchBrowser();
  const page = (await browser.pages())[0];
  await b.navigateTo(page, 'https://x.com/compose/post');
  await b.waitFor(page, 'div[data-testid="tweetTextarea_0"]');
  await page.click('div[data-testid="tweetTextarea_0"]');
  await page.keyboard.type(content, { delay: 30 });
  await b.sleep(1000);
  await page.click('div[data-testid="tweetButtonInline"]');
  await b.sleep(2000);
  await b.screenshot(page, 'tweet-posted.png');
  await browser.close();
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Ensure Chrome profile is logged in before running |
| Rate limited | Add 3-5s delays between actions |
| Selector not found | X updates DOM frequently; verify in DevTools |
| Text not appearing | Use keyboard.type() instead of injectText() |
| Video upload stuck | Check format: MP4/MOV, max 512MB, max 2:20 |
