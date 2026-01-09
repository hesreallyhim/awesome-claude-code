# README Tree Utility

This utility keeps the file tree in `docs/README-GENERATION.md` up to date using a
YAML configuration file. It updates only the section between `<!-- TREE:START -->`
and `<!-- TREE:END -->`.

## Usage

Update the tree block:

```bash
python tools/readme_tree/update_readme_tree.py
```

Check for drift (CI-friendly):

```bash
python tools/readme_tree/update_readme_tree.py --check
```

## Config

The configuration lives in `tools/readme_tree/config.yaml`.

Key fields:
- `doc_path`: Target document with the tree markers.
- `marker_start`, `marker_end`: Marker strings for insertion.
- `include`: Root-relative paths to include in the tree.
- `ignore`: Patterns to ignore.
- `prune`: Paths to include but not descend into.
- `max_depth`: Maximum depth for traversal.
- `entries`: Map of path → comment strings.
- `virtual_entries`: Map of path → comment for paths that don't exist on disk.
- `order`: Map of directory → ordered child patterns.
- `respect_gitignore`: When true (default), .gitignore patterns are applied.

### Notes on Patterns

When `respect_gitignore` is true, the script uses `git check-ignore` to exclude
ignored paths. The `ignore` patterns in the config are a simple glob-style filter
with support for `!` negation, leading `/` anchors, and trailing `/` directory
rules.

## Make Targets

```bash
make docs-tree        # Update the tree block
make docs-tree-check  # Fail if the tree block is out of date
```
