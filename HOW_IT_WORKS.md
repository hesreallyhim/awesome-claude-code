# How Awesome Claude Code Works

This document provides technical details about the repository structure, automated systems, and processes that power Awesome Claude Code.

## Repository Architecture

### Core Files

- **`THE_RESOURCES_TABLE.csv`** - The single source of truth for all resources
- **`README.md`** - Generated automatically from the CSV and templates
- **`templates/`** - Contains templates for README generation
  - `README.template.md` - Main template structure
  - `readme-structure.yaml` - Defines sections and categories
  - `resource-overrides.yaml` - Manual overrides for specific resources

### Scripts Directory

The `scripts/` directory contains all automation:

- **`parse_issue_form.py`** - Parses GitHub issue form submissions
- **`create_resource_pr.py`** - Creates PRs from approved submissions
- **`generate_readme.py`** - Generates README from CSV data
- **`validate_single_resource.py`** - Validates individual resources
- **`validate_links.py`** - Bulk validation of all resources
- **`badge_issue_notification.py`** - Creates notification issues on featured repos
- **`quick_id.py`** - Generates unique resource IDs

### GitHub Actions Workflows

Located in `.github/workflows/`:

- **`validate-resource-submission.yml`** - Runs on issue creation/edit
- **`approve-resource-submission.yml`** - Runs on maintainer commands
- **`protect-labels.yml`** - Prevents unauthorized label changes
- **`validate-links.yml`** - Scheduled validation of all resource links
- **Additional workflows for CI/CD and maintenance**

### GitHub Labels

The submission system uses several labels to track issue state:

#### Resource Submission Labels

- **`resource-submission`** - Applied automatically to issues created via the submission form
- **`validation-passed`** - Applied when submission passes all validation checks
- **`validation-failed`** - Applied when submission fails validation
- **`approved`** - Applied when maintainer approves submission with `/approve`
- **`pr-created`** - Applied after PR is successfully created
- **`error-creating-pr`** - Applied if PR creation fails
- **`rejected`** - Applied when maintainer rejects with `/reject`
- **`changes-requested`** - Applied when maintainer requests changes with `/request-changes`

#### Other Labels

- **`broken-links`** - Applied by scheduled link validation when resources become unavailable
- **`automated`** - Applied alongside `broken-links` to indicate automated detection

#### Label Protection

All submission-related labels are protected from unauthorized changes. The `protect-labels.yml` workflow automatically reverts any label changes made by non-maintainers (users without OWNER, MEMBER, or COLLABORATOR permissions).

#### Label State Transitions

1. New submission → `resource-submission`
2. After validation → adds `validation-passed` OR `validation-failed`
3. If changes requested → adds `changes-requested`
4. When user edits and validation passes → removes `changes-requested`
5. On approval → adds `approved` + `pr-created` (or `error-creating-pr`)
6. On rejection → adds `rejected`

## The Submission Flow

### 1. User Submits Issue

When a user submits a resource via the issue form:

```yaml
# .github/ISSUE_TEMPLATE/submit-resource.yml
- Structured form with all required fields
- Auto-labels with "resource-submission"
- Validates input formats
```

### 2. Automated Validation

The validation workflow triggers immediately:

```python
# Simplified validation flow
1. Parse issue body → extract form data
2. Validate required fields
3. Check URL accessibility
4. Verify no duplicates exist
5. Post results as comment
6. Update issue labels
```

**Validation includes:**
- URL validation (200 OK response)
- License detection from GitHub API
- Duplicate checking against existing CSV
- Field format validation

### 3. Maintainer Review

Once validation passes, maintainers can:

- `/approve` - Triggers PR creation
- `/request-changes [reason]` - Asks for modifications
- `/reject [reason]` - Closes the submission

**Notification System:**
- When changes are requested, the maintainer is @-mentioned in the comment
- When the user edits their issue, the maintainer receives a notification if:
  - It's the first edit after requesting changes
  - The validation status changes (pass→fail or fail→pass)
- Multiple rapid edits won't spam the maintainer with notifications

### 4. Automated PR Creation

Upon approval:

```bash
1. Checkout fresh main branch
2. Create unique branch: add-resource/category/name-timestamp
3. Add resource to CSV with generated ID
4. Run generate_readme.py
5. Commit changes
6. Push branch
7. Create PR via GitHub CLI
8. Link back to original issue
9. Close submission issue
```

### 5. Final Steps

- Maintainer merges PR
- Badge notification system runs (if enabled)
- Submitter receives GitHub notifications

## Resource ID Generation

IDs follow the format: `{prefix}-{hash}`

```python
prefixes = {
    "Slash-Commands": "cmd",
    "Workflows & Knowledge Guides": "wf",
    "Tooling": "tool",
    "CLAUDE.md Files": "claude",
    "Hooks": "hook",
    "Official Documentation": "doc",
}

# Hash is first 8 chars of SHA256(display_name + primary_link)
```

## CSV Structure

| Field | Description | Required | Auto-populated |
|-------|-------------|----------|----------------|
| ID | Unique identifier | Yes | Yes |
| Display Name | Resource name | Yes | No |
| Category | Main category | Yes | No |
| Sub-Category | Optional subcategory | No | No |
| Primary Link | Main URL | Yes | No |
| Secondary Link | Additional URL | No | No |
| Author Name | Creator name | Yes | No |
| Author Link | Creator profile | Yes | No |
| Active | TRUE/FALSE status | Yes | Yes (via validation) |
| Date Added | Addition date | No | Yes |
| Last Modified | GitHub last commit | No | Yes (from API) |
| Last Checked | Validation timestamp | Yes | Yes |
| License | SPDX identifier | Recommended | Yes (from GitHub) |
| Description | Brief description | Yes | No |

## README Generation

The README is generated from templates using:

```yaml
# templates/readme-structure.yaml
sections:
  - title: "Workflows & Knowledge Guides"
    category: "Workflows & Knowledge Guides"
    icon: "🧠"
    source: csv
    
  - title: "Tooling"
    category: "Tooling"
    icon: "🧰"
    subsections:
      - title: "IDE Integrations"
        sub_category: "IDE Integrations"
```

Generation process:
1. Load CSV data
2. Apply any overrides from `resource-overrides.yaml`
3. Group by category/subcategory
4. Format using templates
5. Write final README

## Validation System

### Link Validation

- Checks HTTP status (200-299 = valid)
- Handles redirects
- Respects rate limits
- Caches results for efficiency

### GitHub-Specific Features

For GitHub links:
- Fetches repository metadata
- Extracts license information
- Gets last commit date
- Checks if repository exists/is public

### Override System

The `templates/resource-overrides.yaml` allows:
- Locking specific fields from updates
- Skipping validation for special cases
- Manual corrections to auto-detected data

## Security Considerations

1. **Input Validation** - All user input is sanitized
2. **URL Validation** - Only HTTPS URLs accepted
3. **GitHub Token Scoping** - Minimal permissions required
4. **Review Process** - Human review before code changes
5. **Automated Checks** - No direct CSV manipulation by users

## Environment Variables

- `GITHUB_TOKEN` - For API access (provided by Actions)
- `AWESOME_CC_PAT_PUBLIC_REPO` - For creating notification issues
- `CREATE_ISSUES` - Enable/disable notification system

## Local Development

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Test validation
python scripts/validate_single_resource.py "https://example.com"

# Generate README
python scripts/generate_readme.py

# Parse a test issue
ISSUE_BODY="..." python scripts/parse_issue_form.py --validate
```

## Maintenance Tasks

### Regular Tasks

- Monitor validation failures
- Update templates as needed
- Review and merge PRs
- Handle edge cases with overrides

### Bulk Operations

```bash
# Validate all links
make validate

# Sort resources
make sort

# Regenerate README
make generate
```

## Contributing to the System

To improve the automation:

1. Test changes locally first
2. Update relevant documentation
3. Consider backward compatibility
4. Add tests if applicable
5. Submit PR with clear description

---

For questions about the technical implementation, please open an issue with the "enhancement" label.
