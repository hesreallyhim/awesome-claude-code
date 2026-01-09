# Testing & Coverage

This document covers how to run the test suite and generate coverage reports.

## Setup

Install dev dependencies:

```bash
make install
```

## Running Tests

Run all tests with pytest:

```bash
make test
```

Note: Tests that exercise path resolution with temporary directories should create a
minimal `pyproject.toml` in the temp repo root so repo-root discovery works as expected.

## Comprehensive Checks

Run formatting checks, mypy, and pytest:

```bash
make ci
```

Run type checks only:

```bash
make mypy
```

## Docs Tree Check

Verify the README generation file tree is up to date:

```bash
make docs-tree-check
```

Update the tree block:

```bash
make docs-tree
```

## Regeneration Cycle

Run the full regeneration integration check (root style + selector order changes):

```bash
make test-regenerate-cycle
```

This target runs `make test-regenerate` first, then exercises config changes using
`make test-regenerate-allow-diff`, and finally restores the original config and reruns
`make test-regenerate`.

Note: This integration test requires a clean working tree and will rewrite
`acc-config.yaml` during the run before restoring it.
Note: If the local date changes during the run (near midnight), regenerated READMEs
may update their date stamps and cause a diff; rerun when the clock is stable.

## Coverage

Generate coverage reports (terminal + HTML + XML):

```bash
make coverage
```

Outputs:
- `htmlcov/` for the HTML report
- `coverage.xml` for CI integrations
- Terminal summary via `term-missing`

Note: `scripts/archive/` is excluded from test discovery and coverage.
