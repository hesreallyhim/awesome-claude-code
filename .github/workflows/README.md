# Repository Health Check

This directory contains a GitHub Action workflow that monitors the health of active repositories listed in `THE_RESOURCES_TABLE.csv`.

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
