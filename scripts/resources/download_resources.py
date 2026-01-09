"""
Download resources from the Awesome Claude Code repository CSV file.

This script downloads all active resources (or filtered subset) from GitHub
repositories listed in the resource-metadata.csv file. It respects rate
limiting and organizes downloads by category.

Resources are saved to two locations:
- Archive directory: All resources regardless of license (.myob/downloads/)
- Hosted directory: Only open-source licensed resources (resources/)

Note: Authentication is optional but recommended to avoid rate limiting:
    - Unauthenticated: 60 requests/hour
    - Authenticated: 5,000 requests/hour
    export GITHUB_TOKEN=your_github_token

Usage:
    python download_resources.py [options]

Options:
    --category CATEGORY     Filter by specific category
    --license LICENSE       Filter by license type
    --max-downloads N       Limit number of downloads (for testing)
    --output-dir DIR        Custom archive directory (default: .myob/downloads)
    --hosted-dir DIR        Custom hosted directory (default: resources)
"""

import argparse
import csv
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml  # type: ignore[import-untyped]
from dotenv import load_dotenv

from scripts.utils.github_utils import parse_github_resource_url
from scripts.utils.repo_root import find_repo_root

# Load environment variables from .myob/.env
load_dotenv()

# Constants
USER_AGENT = "awesome-claude-code Downloader/1.0"
REPO_ROOT = find_repo_root(Path(__file__))
CSV_FILE = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
DEFAULT_OUTPUT_DIR = ".myob/downloads"
HOSTED_OUTPUT_DIR = "resources"

# Setup headers with optional GitHub token
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/vnd.github.v3.raw",
    "X-GitHub-Api-Version": "2022-11-28",
}
github_token = os.environ.get("GITHUB_TOKEN")
if github_token:
    # Use Bearer token format as per GitHub API documentation
    HEADERS["Authorization"] = f"Bearer {github_token}"
    print("Using authenticated requests (5,000/hour limit)")
else:
    print("Using unauthenticated requests (60/hour limit)")

# Open source licenses that allow hosting
OPEN_SOURCE_LICENSES = {
    "MIT",
    "MIT+CC",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "GPL-2.0",
    "GPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "MPL-2.0",
    "ISC",
    "0BSD",
    "Unlicense",
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "AGPL-3.0",
    "EPL-2.0",
    "BSL-1.0",
}

# Category name mapping - removed to use sanitized names for both directories
# Keeping the mapping dict empty for now in case we need it later
_CATEGORY_MAPPING: dict[str, str] = {}


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Replace spaces with hyphens and remove/replace problematic characters
    # Added commas and other special chars that could cause issues
    name = re.sub(r'[<>:"/\\|?*,;]', "", name)
    name = re.sub(r"\s+", "-", name)
    name = name.strip("-.")
    return name[:255]  # Max filename length


def download_github_file(
    url_info: dict[str, str], output_path: str, retry_count: int = 0, max_retries: int = 3
) -> bool:
    """
    Download a file from GitHub using the API.
    Returns True if successful, False otherwise.
    """
    response: requests.Response | None = None
    try:
        if url_info["type"] == "file":
            # Download single file
            api_url = (
                f"https://api.github.com/repos/{url_info['owner']}/"
                f"{url_info['repo']}/contents/{url_info['path']}?ref={url_info['branch']}"
            )
            response = requests.get(api_url, headers=HEADERS, timeout=30)

            # Log response details
            if response.status_code != 200:
                print(f"    API Response: {response.status_code}")
                print(
                    "    Headers: X-RateLimit-Remaining"
                    f"={response.headers.get('X-RateLimit-Remaining', 'N/A')}"
                )
                print(f"    Response: {response.text[:300]}...")

            if response.status_code == 200:
                # Create directory if needed
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Write file content
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"    Failed to get file content - Status: {response.status_code}")

        elif url_info["type"] == "dir":
            # List directory contents
            api_url = (
                f"https://api.github.com/repos/{url_info['owner']}/{url_info['repo']}/contents/"
                f"{url_info['path']}?ref={url_info['branch']}"
            )
            # Update headers to use proper Accept header for directory listing
            dir_headers = HEADERS.copy()
            dir_headers["Accept"] = "application/vnd.github+json"
            response = requests.get(api_url, headers=dir_headers, timeout=30)

            # Log response details
            if response.status_code != 200:
                print(f"    API Response: {response.status_code}")
                print(
                    f"    Headers: X-RateLimit-Remaining="
                    f"{response.headers.get('X-RateLimit-Remaining', 'N/A')}"
                )
                print(f"    Response: {response.text[:300]}...")

            if response.status_code == 200:
                # Create directory
                os.makedirs(output_path, exist_ok=True)

                # Download each file in the directory
                items = response.json()
                for item in items:
                    if item["type"] == "file":
                        file_path = os.path.join(output_path, item["name"])
                        # Download the file content
                        file_response = requests.get(
                            item["download_url"], headers=HEADERS, timeout=30
                        )
                        if file_response.status_code != 200:
                            print(
                                f"      File download failed: {item['name']} - "
                                f"Status: {file_response.status_code}"
                            )
                        if file_response.status_code == 200:
                            with open(file_path, "wb") as f:
                                f.write(file_response.content)
                return True

        elif url_info["type"] == "gist":
            # Download gist
            api_url = f"https://api.github.com/gists/{url_info['gist_id']}"
            # Update headers to use proper Accept header for gist API
            gist_headers = HEADERS.copy()
            gist_headers["Accept"] = "application/vnd.github+json"
            response = requests.get(api_url, headers=gist_headers, timeout=30)

            # Log response details
            if response.status_code != 200:
                print(f"    API Response: {response.status_code}")
                print(
                    f"    Headers: X-RateLimit-Remaining="
                    f"{response.headers.get('X-RateLimit-Remaining', 'N/A')}"
                )
                print(f"    Response: {response.text[:300]}...")

            if response.status_code == 200:
                gist_data = response.json()
                # Create directory for gist
                os.makedirs(output_path, exist_ok=True)

                # Download each file in the gist
                for filename, file_info in gist_data["files"].items():
                    file_path = os.path.join(output_path, filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(file_info["content"])
                return True

        # Handle rate limiting
        if response and response.status_code == 429:
            reset_time = response.headers.get("X-RateLimit-Reset")
            if reset_time:
                reset_datetime = datetime.fromtimestamp(int(reset_time))
                print(
                    f"    Rate limit will reset at: {reset_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            raise requests.exceptions.HTTPError("Rate limited")

        return False

    except Exception as e:
        if retry_count < max_retries:
            wait_time = (2**retry_count) + random.uniform(1, 2)
            print(f"  Retry in {wait_time:.1f}s... (Error: {str(e)})")
            time.sleep(wait_time)
            return download_github_file(url_info, output_path, retry_count + 1, max_retries)

        print(f"  Failed after {max_retries} retries: {str(e)}")
        return False


def load_overrides() -> dict[str, Any]:
    """Load resource overrides from template directory."""
    template_dir = REPO_ROOT / "templates"
    override_path = os.path.join(template_dir, "resource-overrides.yaml")
    if not os.path.exists(override_path):
        return {}

    with open(override_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("overrides", {})


def apply_overrides(row: dict[str, str], overrides: dict[str, Any]) -> dict[str, str]:
    """Apply overrides to a resource row.

    Override values are applied for resource downloading. Any field set in
    the override configuration is automatically locked by validation scripts.
    """
    resource_id = row.get("ID", "")
    if not resource_id or resource_id not in overrides:
        return row

    override_config = overrides[resource_id]

    # Apply overrides (excluding control/metadata fields and legacy locked flags)
    for field, value in override_config.items():
        # Skip special control/metadata fields
        if field in ["skip_validation", "notes"]:
            continue

        # Skip any legacy *_locked flags (no longer needed)
        if field.endswith("_locked"):
            continue

        # Apply override values
        if field == "license":
            row["License"] = value
        elif field == "active":
            row["Active"] = value
        elif field == "description":
            row["Description"] = value

    return row


def process_resources(
    category_filter: str | None = None,
    license_filter: str | None = None,
    max_downloads: int | None = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    hosted_dir: str = HOSTED_OUTPUT_DIR,
) -> None:
    """
    Process and download resources from the CSV file.
    """
    start_time = datetime.now()
    print(f"Starting download at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Archive directory (all resources): {output_dir}")
    print(f"Hosted directory (open-source only): {hosted_dir}")

    # Check rate limit status
    try:
        rate_check = requests.get("https://api.github.com/rate_limit", headers=HEADERS, timeout=10)
        if rate_check.status_code == 200:
            rate_data = rate_check.json()
            core_limit = rate_data.get("rate", {})
            print("\nGitHub API Rate Limit Status:")
            print(
                f"  Remaining: {core_limit.get('remaining', 'N/A')}/"
                f"{core_limit.get('limit', 'N/A')}"
            )
            if core_limit.get("reset"):
                reset_time = datetime.fromtimestamp(core_limit["reset"])
                print(f"  Resets at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Could not check rate limit: {e}")

    # Load overrides
    overrides = load_overrides()
    if overrides:
        print(f"\nLoaded {len(overrides)} resource overrides")

    # Track statistics
    total_resources = 0
    downloaded = 0
    skipped = 0
    failed = 0

    # Read CSV
    with open("./THE_RESOURCES_TABLE.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Apply overrides to the row
            row = apply_overrides(row, overrides)
            # Check if we've reached the download limit
            if max_downloads and downloaded >= max_downloads:
                print(f"\nReached download limit ({max_downloads}). Stopping.")
                break

            # Skip inactive resources
            if row["Active"].upper() != "TRUE":
                continue

            total_resources += 1

            # Apply filters
            if category_filter and row["Category"] != category_filter:
                continue

            if license_filter and row.get("License", "") != license_filter:
                continue

            # Get the URL (prefer primary link)
            url = row["Primary Link"].strip() or row["Secondary Link"].strip()
            if not url:
                continue

            display_name = row["Display Name"]
            original_category = row["Category"]
            category = sanitize_filename(original_category.lower().replace(" & ", "-"))

            # Use same sanitized category name for both directories
            resource_license = row.get("License", "NOT_FOUND").strip()

            print(f"\n[{downloaded + 1}] Processing: {display_name}")
            print(f"  URL: {url}")
            print(f"  Category: {original_category} -> '{category}'")

            # Parse GitHub URL
            url_info = parse_github_resource_url(url)
            if not url_info:
                print("  Skipped: Not a GitHub URL")
                skipped += 1
                continue

            # Determine output paths
            safe_name = sanitize_filename(display_name)
            print(f"  Sanitized name: '{display_name}' -> '{safe_name}'")

            # Primary path for archive (all resources)
            if url_info["type"] == "gist":
                resource_path = os.path.join(output_dir, category, f"{safe_name}-gist")
                hosted_path = (
                    os.path.join(hosted_dir, category, safe_name)
                    if resource_license in OPEN_SOURCE_LICENSES
                    else None
                )
            elif url_info["type"] == "repo":
                resource_path = os.path.join(output_dir, category, safe_name)
                print("  Skipped: Full repository downloads not implemented")
                skipped += 1
                continue
            elif url_info["type"] == "dir":
                resource_path = os.path.join(output_dir, category, safe_name)
                hosted_path = (
                    os.path.join(hosted_dir, category, safe_name)
                    if resource_license in OPEN_SOURCE_LICENSES
                    else None
                )
            else:  # file
                # Extract filename from path
                filename = os.path.basename(url_info["path"])
                resource_path = os.path.join(output_dir, category, safe_name, filename)
                hosted_path = (
                    os.path.join(hosted_dir, category, safe_name, filename)
                    if resource_license in OPEN_SOURCE_LICENSES
                    else None
                )

            # Download the resource to archive
            print(f"  Downloading to archive: {resource_path}")
            print(f"  License: {resource_license}")
            if hosted_path:
                print(f"  Will copy to hosted: {hosted_path}")

            download_success = download_github_file(url_info, resource_path)

            if download_success:
                print("  ✅ Downloaded successfully")
                downloaded += 1

                # If open-source licensed, also copy to hosted directory
                if hosted_path and resource_license in OPEN_SOURCE_LICENSES:
                    print(f"  📦 Copying to hosted directory: {hosted_path}")
                    try:
                        import shutil

                        os.makedirs(os.path.dirname(hosted_path), exist_ok=True)

                        if os.path.isdir(resource_path):
                            print(
                                f"     Source is directory with "
                                f"{len(os.listdir(resource_path))} items"
                            )
                            shutil.copytree(resource_path, hosted_path, dirs_exist_ok=True)
                        else:
                            print("     Source is file")
                            shutil.copy2(resource_path, hosted_path)
                        print("  ✅ Copied to hosted directory")
                    except Exception as e:
                        print(f"  ⚠️  Failed to copy to hosted directory: {e}")
                        print(f"     Error type: {type(e).__name__}")
                        import traceback

                        print(f"     Traceback: {traceback.format_exc()}")
            else:
                print("  ❌ Download failed")
                failed += 1

            # Rate limiting delay
            time.sleep(random.uniform(1, 2))

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n{'=' * 60}")
    print(f"Download completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {duration}")
    print("\nSummary:")
    print(f"  Total resources found: {total_resources}")
    print(f"  Downloaded: {downloaded}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    print(f"{'=' * 60}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download resources from awesome-claude-code CSV")
    parser.add_argument("--category", help="Filter by specific category")
    parser.add_argument("--license", help="Filter by license type")
    parser.add_argument("--max-downloads", type=int, help="Limit number of downloads")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Archive output directory")
    parser.add_argument(
        "--hosted-dir",
        default=HOSTED_OUTPUT_DIR,
        help="Hosted output directory for open-source resources",
    )

    args = parser.parse_args()

    # Create output directories if needed
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.hosted_dir).mkdir(parents=True, exist_ok=True)

    # Process resources
    process_resources(
        category_filter=args.category,
        license_filter=args.license,
        max_downloads=args.max_downloads,
        output_dir=args.output_dir,
        hosted_dir=args.hosted_dir,
    )


if __name__ == "__main__":
    main()
