#!/usr/bin/env python3
"""Create a PR adding an approved resource: append CSV → regenerate README → open PR.

Called by the handle-resource-submission-commands workflow after a maintainer
/approve.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import generate_readme  # noqa: E402
from resources.ids import generate_resource_id  # noqa: E402
from resources.resource_utils import append_to_csv, generate_pr_content  # noqa: E402

ALLOWED_CHANGES = {"README.md", "THE_RESOURCES_TABLE_NEW.csv"}
IGNORED_CHANGES = {"resource_data.json", "validation_result.json", "pr_result.json"}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def validate_changes(status_stdout: str) -> None:
    if not (REPO_ROOT / "README.md").is_file():
        raise RuntimeError("Missing generated README.md")
    if not (REPO_ROOT / "THE_RESOURCES_TABLE_NEW.csv").is_file():
        raise RuntimeError("Missing THE_RESOURCES_TABLE_NEW.csv")
    unexpected = []
    for line in status_stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].split(" -> ", 1)[-1]
        if path not in ALLOWED_CHANGES and path not in IGNORED_CHANGES:
            unexpected.append(path)
    if unexpected:
        raise RuntimeError(f"Unexpected changes outside generated outputs: {', '.join(unexpected)}")


def write_step_outputs(outputs: dict[str, str]) -> None:
    import os

    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as f:
        for key, value in outputs.items():
            value_str = str(value or "")
            if "\n" in value_str:
                f.write(f"{key}<<EOF\n{value_str}\nEOF\n")
            else:
                f.write(f"{key}={value_str}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create PR from approved resource submission")
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--resource-data", required=True, help="Path to parsed resource JSON")
    args = parser.parse_args()

    payload = json.loads(Path(args.resource_data).read_text(encoding="utf-8"))
    data = payload.get("data", payload) if isinstance(payload, dict) else payload

    resource = {
        "id": generate_resource_id(),
        "display_name": data["display_name"],
        "category": data["category"],
        "subcategory": data.get("subcategory", ""),
        "link": data["link"],
        "author_name": data["author_name"],
        "author_link": data["author_link"],
        "description": data["description"],
    }

    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in data["display_name"].lower())
    safe = safe.strip("-")[:50]
    branch = f"add-resource/{safe}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    result: dict[str, object] = {"success": False}
    try:
        run(["git", "checkout", "main"])
        run(["git", "pull", "origin", "main"])
        run(["git", "checkout", "-b", branch])

        if not append_to_csv(resource):
            raise RuntimeError("Failed to append resource to CSV")

        with contextlib.redirect_stdout(sys.stderr):  # keep stdout clean for the JSON result
            generate_readme.main()

        status = run(["git", "status", "--porcelain"]).stdout
        validate_changes(status)

        run(["git", "add", "--", "THE_RESOURCES_TABLE_NEW.csv", "README.md"])
        message = (
            f"Add resource: {resource['display_name']}\n\n"
            f"Category: {resource['category']}\n"
            f"Author: {resource['author_name']}\n"
            f"From issue: #{args.issue_number}"
        )
        run(["git", "commit", "-m", message])
        run(["git", "push", "origin", branch])

        pr_body = generate_pr_content(resource) + f"\n---\n\nResolves #{args.issue_number}"
        pr = run(
            ["gh", "pr", "create", "--title", f"Add resource: {resource['display_name']}",
             "--body", pr_body, "--base", "main", "--head", branch]
        )
        result = {
            "success": True,
            "pr_url": pr.stdout.strip(),
            "branch_name": branch,
            "resource_id": resource["id"],
        }
    except Exception as e:  # noqa: BLE001 - report any failure back to the workflow
        import traceback

        traceback.print_exc(file=sys.stderr)
        result = {"success": False, "error": str(e), "branch_name": branch}

    write_step_outputs(
        {
            "success": "true" if result.get("success") else "false",
            "pr_url": str(result.get("pr_url", "")),
            "branch_name": str(result.get("branch_name", "")),
            "resource_id": str(result.get("resource_id", "")),
            "error": str(result.get("error", "")),
        }
    )
    print(json.dumps(result))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
