# Cooldown Enforcement

Automated rate-limiting for resource submissions. Applies to both issues and pull requests.

## How it works

Every submission is checked against a state file (`cooldown-state.json`) stored in the private ops repo. The state tracks each user's cooldown level, active cooldown expiry, and ban status.

**Violations** (each starts or extends a cooldown):

| Violation | Trigger |
|---|---|
| Missing form label | Issue opened without using the submission template |
| Repo too young | Linked repository is less than 7 days old |
| Submitted as PR | Pull request classified as a resource submission by Claude |
| Submitted during cooldown | Any submission while an active cooldown is in effect |

**Escalation** — each violation doubles the cooldown period:

| Level | Duration |
|---|---|
| 0 → 1 | 24 hours |
| 1 → 2 | 48 hours |
| 2 → 3 | 4 days |
| 3 → 4 | 8 days |
| 4 → 5 | 16 days |
| 5 → 6 | 32 days |
| 6 | Permanent ban |

Submitting during an active cooldown is itself a violation — the cooldown extends and the level increments. Persistence is counterproductive.

## Maintainer controls

- **`excused` label** — apply to any issue to bypass cooldown checks entirely. The workflow skips enforcement and proceeds directly to validation.
- **Manual state edits** — the state file lives in the private repo file `cooldown-state.json`. You can edit it directly to reduce a user's level, clear their cooldown, or remove a ban. Each entry looks like:

```json
{
  "username": {
    "active_until": "2026-02-24T12:00:00.000Z",
    "cooldown_level": 2,
    "last_violation": "2026-02-22T12:00:00.000Z",
    "last_reason": "repo-too-young"
  }
}
```

To unban someone, delete their entry or set `banned: false` and `cooldown_level: 0`.

## PR classification

Pull requests are classified by Claude (Haiku) as either `resource_submission` or `not_resource_submission` with a confidence level. Resource submissions are closed with a redirect to the issue template and trigger a cooldown violation. Non-resource PRs with low confidence get a `needs-review` label. API failures fail open — the PR stays untouched.

## Concurrency

Runs are serialized per-user (concurrent submissions from the same user queue). Different users process in parallel. The ops repo file uses optimistic locking (SHA-based) — if two concurrent writes race, the loser's violation isn't recorded but will be caught on the next submission.
