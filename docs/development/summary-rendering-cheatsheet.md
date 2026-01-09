## GitHub README collapsible subcategory cheat sheet

Context: GitHub’s Markdown renderer wraps loose content in `<p>` tags and modifies markup inside `<summary>`. These tweaks keep the caret aligned and prevent broken first items in collapsible sections.

- Keep `<summary>` contents on one line with no leading/trailing whitespace; GitHub inserts `<p>` if it sees blank lines.
- Wrap the SVG in a `<picture>` to stop the image from becoming a link target via camo wrapping.
- Use `align="absmiddle"` on the `<img>` to nudge the caret arrow to midline (works on GitHub).
- Put the back-to-top link immediately after the picture inside the same `<span>`; avoid extra spaces or newlines between them.
- Add exactly one blank line after the `<summary>` line so the first resource renders as Markdown, not as raw text.

Minimal pattern that renders correctly on GitHub:

```html
<details id="some-subcategory-">
<summary><span><picture><img src="assets/subheader_some.svg" alt="Some Subcat" align="absmiddle"></picture><a href="#awesome-claude-code">🔝</a></span></summary>

[`Example`](https://example.com) &nbsp; by &nbsp; [Author](https://author.example)

</details>
```

Verification tip: use GitHub’s `/markdown` API with mode `gfm` to preview the rendered HTML without pushing commits. One request per variant is usually enough.***
