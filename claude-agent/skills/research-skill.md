# Web Research Skill

## Purpose
Conduct web research to find trending topics, gather information, and analyze content
for brainstorming and content creation.

## Workflows

### Research Trending Topics on X
```
1. Navigate to https://x.com/explore/tabs/trending
2. Wait for trends to load
3. Extract trending topics:
   const trends = await page.$$eval('[data-testid="trend"]', items =>
     items.map(item => ({
       topic: item.querySelector('span')?.textContent,
       tweetCount: item.querySelector('[data-testid="trendMetadata"]')?.textContent,
     }))
   );
4. Filter for tech/AI/coding related topics
5. Return top 10 relevant trends
```

### Research GitHub Trending
```
1. Navigate to https://github.com/trending
2. Filter by language if needed: ?spoken_language_code=en&language=python
3. Extract trending repos:
   const repos = await page.$$eval('article.Box-row', items =>
     items.map(item => ({
       name: item.querySelector('h2 a')?.textContent?.trim(),
       description: item.querySelector('p')?.textContent?.trim(),
       stars: item.querySelector('.octicon-star')?.parentElement?.textContent?.trim(),
       language: item.querySelector('[itemprop="programmingLanguage"]')?.textContent?.trim(),
     }))
   );
4. Return top 10 repos with descriptions
```

### Research Hacker News
```
1. Navigate to https://news.ycombinator.com/
2. Extract top stories:
   const stories = await page.$$eval('.athing', items =>
     items.map(item => ({
       title: item.querySelector('.titleline a')?.textContent,
       link: item.querySelector('.titleline a')?.href,
       score: item.nextElementSibling?.querySelector('.score')?.textContent,
     }))
   );
3. Filter for relevant topics
4. Return top 10 stories
```

### Research Product Hunt
```
1. Navigate to https://www.producthunt.com/
2. Extract today's top products
3. Focus on AI/developer tools category
4. Return names, descriptions, and upvote counts
```

### Comprehensive Topic Research
```
1. Identify the topic to research
2. Search multiple sources:
   - X trending
   - GitHub trending
   - Hacker News
   - Product Hunt
   - Reddit (r/programming, r/artificial, etc.)
3. Cross-reference findings
4. Identify common themes and hot topics
5. Generate summary with:
   - Top 5 trending topics
   - Why they're trending
   - Potential project ideas for each
   - Estimated audience interest level
```

### Brainstorm Project Ideas
```
1. Run "Comprehensive Topic Research"
2. For each trending topic, generate:
   - 3 project ideas (simple, medium, complex)
   - Tech stack suggestion
   - Estimated effort (hours)
   - Viral potential score (1-10)
3. Select the best idea based on:
   - Relevance to audience
   - Technical feasibility
   - Content potential (video-worthy)
   - Uniqueness
```

## Output Format

### Research Report Template
```markdown
# Research Report: [Date]

## Trending Topics
1. **Topic Name** - Description (Source: X/GitHub/HN)
   - Relevance: High/Medium/Low
   - Potential: Description of why it matters

## Top Project Ideas
1. **Project Name** - Brief description
   - Stack: Technology choices
   - Effort: X hours
   - Viral Score: 8/10

## Recommended Action
Based on research, the best project to build is [X] because [Y].
```

## Troubleshooting

- **Rate limited**: Add delays between requests (3-5 seconds)
- **Content blocked**: Some sites block automation; use real Chrome profile
- **Dynamic content**: Wait for JavaScript to render before extracting
- **Stale data**: Always check dates; trending data changes hourly
