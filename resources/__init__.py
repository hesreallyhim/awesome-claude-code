"""Recommendation → CSV publication pipeline (ported, lean, new-schema).

Flow: issue form → parse_issue_form (validate) → maintainer /approve →
create_resource_pr (append to THE_RESOURCES_TABLE_NEW.csv + regenerate README →
open PR). Everything flows from the CSV; the README is a build artifact.
"""
