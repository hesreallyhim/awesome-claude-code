# Path Resolution Migration Plan

This plan describes the concrete work needed to migrate README generation to the
final path-resolution strategy (relative asset paths resolved per output file).

## Scope

- Keep style-specific templates intact (extra/classic/awesome/flat).
- Remove all path-specific assumptions from templates and markup.
- Centralize asset path resolution in the generator.

## Plan

1. **Audit templates and markup**
   - Inventory all occurrences of `{{ASSET_PREFIX}}`, `{{ASSET_PATH(...)}}`, `assets/`, `../assets`, `/assets`.
   - Identify every generator/markup call site that injects or assumes a prefix.
   - Map all output locations (root README, README_ALTERNATIVES, .github, etc.).

2. **Introduce a single asset token scheme**
   - Choose one token format (e.g., `asset:foo.png` or `{{ASSET_PATH('foo.png')}}`).
   - Implement a resolver that:
     - finds `repo_root` via `pyproject.toml`
     - computes a relative path from the output file’s directory to `/assets`
     - replaces tokens with correct POSIX paths
   - Remove `ASSET_PREFIX` and `is_root_readme` assumptions from templates.

3. **Wire the resolver into generation**
   - Apply the resolver after template substitution but before writing files.
   - Update markup helpers to emit tokenized asset references instead of prefixes.
   - Ensure style selector and repo ticker resolve through the same mechanism.

4. **Add generated-file header**
   - Insert `<!-- GENERATED FILE: do not edit directly -->` into all outputs.
   - Ensure templates or generator handle this consistently.

5. **Update tests and docs**
   - Add/adjust tests to validate asset paths for all output locations.
   - Ensure `test-regenerate` remains the canonical drift check.
   - Update docs to reflect the new token scheme and remove obsolete guidance.

## Completion Criteria

- No templates or markup contain concrete asset prefixes.
- Outputs render correctly in-place and on GitHub across all locations.
- `make test-regenerate` passes with a clean working tree.
