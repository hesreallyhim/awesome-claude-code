# Strategy: Generated, Location-Correct Relative Asset Paths

This repo treats all Markdown READMEs as generated artifacts. The generator is responsible for making every output Markdown file render correctly both (a) on GitHub when viewed in-place and (b) in local Markdown previews that expect standard relative paths.

## Goals

- Any generated file like `/README.md`, `/foo/bar/README.md`, `/.github/README.md`, `README_ALTERNATIVES/*.md` renders correctly in its own directory.
- Local preview works without special editor configuration.
- GitHub rendering works without relying on repo-root /assets/... semantics.
- “Swaps” never copy pre-generated Markdown between locations; they regenerate for the destination path.

---

## Rules

### Rule 1: Single source of truth for assets

- Assets live only in: /assets/*
- No duplicated asset directories are required for this strategy.

### Rule 2: Templates never contain concrete relative prefixes

Templates must not hardcode ./assets, ../assets, /assets, etc.

Instead, templates use one of:

- a placeholder token: {{ASSET_PATH("foo.png")}} (single quotes are also supported)
- or a canonical pseudo-URL: asset:foo.png

Only the generator resolves these into real paths.

### Rule 3: Generator anchors on repo root

The generator must discover repo_root deterministically by walking upward from the executing script (or from the template file) until it finds pyproject.toml.

Definition:

- repo_root is the directory containing pyproject.toml.

### Rule 4: Resolve assets relative to each output file

For each output Markdown file at path out_md:

- Let base_dir = out_md.parent
- Let assets_dir = repo_root / "assets"
- Compute rel_assets = relative_path(from=base_dir, to=assets_dir) using POSIX separators (/) for Markdown
- Emit image references as: rel_assets + "/<asset-file>"

Examples:

- Output /README.md → assets/foo.png
- Output /.github/README.md → ../assets/foo.png
- Output /foo/bar/README.md → ../../assets/foo.png

### Rule 5: Swaps are selection + generation, never copying contents

A “swap” means:

- Choose a variant/source template (e.g. language/style)
- Regenerate the destination file(s) in their final location(s)

Never:

- Copy or move pre-generated Markdown from one directory to another (paths will break).

### Rule 6: Generated files are not manually edited

- Generated READMEs must carry a header comment like:

```markdown
<!-- GENERATED FILE: do not edit directly -->
```

- Manual edits go into the template/source inputs only.

### Rule 7: CI validates generation is up-to-date

CI must:

	1.	run the generator
	2.	fail if the working tree changed

Canonical check:

- git diff --exit-code

This ensures no drift between committed generated READMEs and what templates would produce.

---

## Operational Guidance

### Editing Files

- Edit: templates + data inputs only
- Do not edit: generated Markdown outputs
- Assume: manual changes to Markdown files will be overridden by the generators 

### Link checking

Run link/image checks only on:

- the generated Markdown outputs (post-generation) not on templates or source markdown fragments.

---

## Summary

This strategy makes local preview easy by using standard relative paths, while keeping GitHub rendering correct everywhere. The generator is the only component allowed to decide how assets/ is referenced, and swaps are implemented exclusively as “regenerate for destination path,” not file copying.
