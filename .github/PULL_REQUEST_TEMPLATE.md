# Pull Request

<!-- IMPORTANT: Submit only ONE resource per pull request. If you have multiple resources, please create separate PRs. -->

## Type of Contribution

<!-- Select ONE by marking with an [x] -->

- [ ] **New Resource** - Adding a new resource to the list (ONE per PR)
- [ ] **Update Resource** - Updating existing resource information (e.g., broken link, license info)
- [ ] **Repository Improvement** - Improving the repository itself (not adding resources)

---

## For New Resources

<!-- If you used the script, paste the generated content from .pr_template_content.md here -->
<!-- If you're manually adding a resource, complete all fields below -->

### Resource Information

- **Display Name**: <!-- e.g., "Claude Task Manager" or "/commit" -->
- **Category**: <!-- Select from: Workflows & Knowledge Guides, Tooling, Hooks, Slash-Commands, CLAUDE.md Files, Official Documentation -->
- **Sub-Category** (if applicable): <!-- e.g., "Version Control & Git", "Code Analysis & Testing" -->
- **Primary Link**: <!-- The main URL for the resource -->
- **Author Name**: <!-- Creator/maintainer name -->
- **Author Link**: <!-- Link to author's profile -->
- **License** (if known): <!-- e.g., MIT, Apache-2.0, GPL-3.0 -->

### Description

<!-- 1-2 sentences describing what the resource does and why it's valuable to Claude Code users -->

### Automated Notification

<!-- Check if applicable -->
- [ ] This is a GitHub-hosted resource and will receive an automatic notification issue when merged

### Checklist for New Resources

<!-- All items must be checked -->

- [ ] Used `make add-resource` or `python scripts/add_resource.py` to add the resource
- [ ] OR manually added entry to `THE_RESOURCES_TABLE.csv`
- [ ] Ran `make generate` to update README.md
- [ ] Verified link works and points to correct resource
- [ ] Description is concise (1-2 sentences max)

---

## For Resource Updates

### What Changed?

<!-- Describe what you're updating -->

- **Resource Name**:
- **Change Type**: <!-- e.g., Fix broken link, Update license, Update description -->
- **Details**:

### Checklist for Updates

- [ ] Updated entry in `THE_RESOURCES_TABLE.csv`
- [ ] Ran `make generate` to update README.md
- [ ] Verified new information is correct

---

## For Repository Improvements

### Description of Changes

<!-- Describe what you're improving and why -->

### Checklist for Repository Changes

- [ ] Changes follow existing code style
- [ ] Updated relevant documentation
- [ ] Tested changes locally
- [ ] Pre-commit hooks pass

---

## Additional Notes

<!-- Any additional context that would help reviewers -->
<!-- Remember: Only ONE resource per PR. Multiple resources require separate pull requests. -->

## Questions?

- See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines
- Use `make add-resource` for guided resource submission
- The CSV approach ensures consistent formatting - never edit README.md directly!
