# Don't Forget

Some important but easy-to-forget assumptions and gotchas that can cause headaches:

- `python -m` uses dot notation (for example, `python -m scripts.resources.parse_issue_form`), not slash paths or `.py` suffixes.
- `python -m` only works for modules with a CLI entrypoint (`if __name__ == "__main__":`).
- GitHub Actions with sparse checkout must include `pyproject.toml` so `find_repo_root()` can locate the repo root.
- If a workflow runs scripts that import `scripts.*`, either run from the repo root or set `PYTHONPATH` to the repo root.
- Sparse checkout must include any data files the script reads (for example, `THE_RESOURCES_TABLE.csv`, `templates/`).
- GitHub Actions using sparse checkout must include `pyproject.toml` so scripts can locate the repo root (via `find_repo_root()`).
