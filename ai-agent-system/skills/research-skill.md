# Web Research Skill

## Purpose
Research trending topics across platforms, brainstorm project ideas, and identify content opportunities.

## Workflows

### Scan X Trending
```
1. Navigate to https://x.com/explore/tabs/trending
2. Wait for trends to load
3. Extract:
   page.$$eval('[data-testid="trend"]', items =>
     items.map(item => ({
       topic: item.querySelector('span')?.textContent,
       count: item.querySelector('[data-testid="trendMetadata"]')?.textContent,
     }))
   )
4. Filter for tech/AI/coding topics
5. Return top 10
```

### Scan GitHub Trending
```
1. Navigate to https://github.com/trending?spoken_language_code=en
2. Filter by language if needed: &language=python
3. Extract:
   page.$$eval('article.Box-row', items =>
     items.map(item => ({
       name: item.querySelector('h2 a')?.textContent?.trim(),
       description: item.querySelector('p')?.textContent?.trim(),
       stars: item.querySelector('.octicon-star')?.parentElement?.textContent?.trim(),
       language: item.querySelector('[itemprop="programmingLanguage"]')?.textContent,
     }))
   )
4. Return top 10
```

### Scan Hacker News
```
1. Navigate to https://news.ycombinator.com/
2. Extract:
   page.$$eval('.athing', items =>
     items.map(item => ({
       title: item.querySelector('.titleline a')?.textContent,
       link: item.querySelector('.titleline a')?.href,
       score: item.nextElementSibling?.querySelector('.score')?.textContent,
     }))
   )
3. Filter for relevant topics
4. Return top 10
```

### Cross-Reference Analysis
```
1. Run all three scans above
2. Find topics appearing on 2+ platforms
3. Score by:
   - Multi-platform presence (x2 if on 2+)
   - Recency (higher if today)
   - Engagement (stars, score, tweet count)
```

### Brainstorm Ideas
```
For each hot topic:
1. Simple idea (1-2 hours, great demo)
2. Medium idea (half day, more features)
3. Complex idea (full day, production quality)

Score each:
- Viral potential (1-10)
- Feasibility (1-10)
- Visual appeal (1-10)
```

## Output Template

```markdown
# Research Report — [Date]

## Trending Topics
1. **[Topic]** — [Why trending] (Sources: X, GH, HN)
   - Score: X/10

## Recommended Project
**[Name]**: [Description]
- Stack: [Technologies]
- Effort: [Hours]
- Viral Score: X/10
- Why: [Justification]

## Alternatives
1. [Idea] — [Score]
2. [Idea] — [Score]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Rate limited | Add 3-5s delays between requests |
| Content blocked | Use real Chrome profile |
| Dynamic content | Wait for JS rendering before extracting |
| Stale data | Trends change hourly; always check dates |
