# GitHub Workflows

This directory contains GitHub Action workflows for repository maintenance, resource submission handling, and health monitoring.

---

## Workflow: Validate New Issue

**File:** `.github/workflows/validate-new-issue.yml`

### Purpose

Handles all new issues opened in the repository with two mutually exclusive jobs:

1. **validate-resource**: Validates properly-submitted resource recommendations (issues with `resource-submission` label)
2. **detect-informal**: Detects informal submissions that bypassed the issue template (issues without the label)

### Trigger

- `issues.opened` - New issue created
- `issues.reopened` - Issue reopened
- `issues.edited` - Issue body edited

### Job 1: Validate Resource Submission

Runs when an issue has the `resource-submission` label (applied automatically by the issue template).

**Behavior:**
- Parses the issue body using `scripts/resources/parse_issue_form.py`
- Validates all required fields (display name, category, URLs, etc.)
- Checks for duplicate resources in `THE_RESOURCES_TABLE.csv`
- Validates URL accessibility
- Posts validation results as a comment
- Updates labels: `validation-passed` or `validation-failed`
- Notifies maintainer when changes are made after `/request-changes`

### Job 2: Detect Informal Submission

Runs when a **new** issue does NOT have the `resource-submission` label.

**Purpose:** Catches users who try to recommend resources without using the official template.

**Detection Signals:**

| Signal Type | Examples | Weight |
|-------------|----------|--------|
| Template field labels | `Display Name:`, `Category:`, `Primary Link:` | Very strong (+0.7 for 3+) |
| Submission language | "recommend", "submit", "please add" | Strong (+0.3 each) |
| Resource mentions | "plugin", "skill", "hook", "slash command" | Medium (+0.15 each) |
| GitHub URLs | `github.com/user/repo` | Medium (+0.15) |
| License mentions | MIT, Apache, GPL | Medium (+0.15) |
| Bug/question language | "bug", "error", "how do I" | Negative (-0.2 each) |

**Two-Tier Response:**

| Confidence | Action |
|------------|--------|
| ≥ 0.6 (High) | Add `needs-template` label, post warning, **auto-close** |
| 0.4 - 0.6 (Medium) | Add `needs-template` label, post gentle warning, **leave open** |
| < 0.4 (Low) | No action |

### Local Usage

```bash
# Test informal submission detection
ISSUE_TITLE="Check out my plugin" ISSUE_BODY="I made this tool at github.com/user/repo" \
  python -m scripts.resources.detect_informal_submission
```

### Related Scripts

- `scripts/resources/parse_issue_form.py` - Parses and validates issue form data
- `scripts/resources/detect_informal_submission.py` - Detects informal submissions

---

## Workflow: Handle Resource Submission Commands

**File:** `.github/workflows/handle-resource-submission-commands.yml`

### Purpose

Processes maintainer commands on resource submission issues.

### Commands

| Command | Description | Requirements |
|---------|-------------|--------------|
| `/approve` | Creates PR to add resource to CSV | Issue must have `validation-passed` label |
| `/reject [reason]` | Closes issue as rejected | Maintainer permission |
| `/request-changes [message]` | Requests changes from submitter | Maintainer permission |

### Trigger

- `issue_comment.created` on issues with `resource-submission` label
- Only processes comments from OWNER, MEMBER, or COLLABORATOR

---

## Workflow: Update GitHub Release Data

**File:** `.github/workflows/update-github-release-data.yml`

### Purpose

Updates `THE_RESOURCES_TABLE.csv` with:
- Latest commit date on the default branch (Last Modified)
- Latest GitHub Release date (Latest Release)
- Latest GitHub Release version (Release Version)

### Schedule

- Runs automatically every day at **3:00 AM UTC**
- Can be triggered manually via the GitHub Actions UI

### Local Usage

```bash
python -m scripts.maintenance.update_github_release_data
```

#### Options

```bash
python -m scripts.maintenance.update_github_release_data --help
```

- `--csv-file`: Path to CSV file (default: THE_RESOURCES_TABLE.csv)
- `--max`: Process at most N resources
- `--dry-run`: Print updates without writing changes

## Workflow: Check Repository Health

**File:** `.github/workflows/check-repo-health.yml`

### Purpose

Ensures that active GitHub repositories in the resource list are still maintained and responsive by checking:
- Number of open issues
- Date of last push or PR merge (last updated)

### Behavior

The workflow will **fail** if any repository:
- Has not been updated in over **6 months** AND
- Has more than **2 open issues**

Deleted or private repositories are logged as warnings but do not cause the workflow to fail.

### Schedule

- Runs automatically every **Monday at 9:00 AM UTC**
- Can be triggered manually via the GitHub Actions UI

### Local Usage

You can run the health check locally using:

```bash
make check-repo-health
```

Or directly with Python:

```bash
python3 -m scripts.maintenance.check_repo_health
```

#### Options

```bash
python3 -m scripts.maintenance.check_repo_health --help
```

- `--csv-file`: Path to CSV file (default: THE_RESOURCES_TABLE.csv)
- `--months`: Months threshold for outdated repos (default: 6)
- `--issues`: Open issues threshold (default: 2)

### Example Output

```
INFO: Reading repository list from THE_RESOURCES_TABLE.csv
INFO: Checking owner/repo (Resource Name)
INFO: 
============================================================
INFO: Summary:
INFO:   Total active GitHub repositories checked: 50
INFO:   Deleted/unavailable repositories: 2
INFO:   Problematic repositories: 0
INFO: 
============================================================
INFO: ✅ HEALTH CHECK PASSED
INFO: All active repositories are healthy!
```

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token or Actions token (recommended to avoid rate limiting)

The GitHub Actions workflow automatically uses the `GITHUB_TOKEN` secret provided by GitHub Actions.
