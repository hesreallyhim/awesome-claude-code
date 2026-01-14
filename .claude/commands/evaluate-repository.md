# Repository Evaluation Prompt (Awesome-Claude-Code · Full Version)

## Evaluation Context (Claude Code Ecosystem)

You are evaluating a repository intended for use in or alongside **Claude Code**, where certain features (such as hooks, commands, scripts, or automation) may execute implicitly or with elevated trust once enabled by a user.

In this ecosystem, risk commonly arises not from overtly malicious code, but from implicit execution surfaces, including:
- Hooks that execute automatically based on tool lifecycle events
- Custom commands that may invoke shell scripts
- Scripts that run in the user’s local environment
- Persistent state files that influence control flow
- Network access triggered indirectly by tooling

Your task is to perform a conservative, evidence-based, static review that:
- Identifies trust boundaries and implicit execution
- Distinguishes declared behavior from effective capability
- Surfaces red flags or areas requiring further manual inspection
- Avoids inferring author intent beyond what is observable

When uncertain, prefer explicit uncertainty over confident speculation.

---

## Instructions

Perform a static, read-only review of the repository named at the end of this prompt.

Do not run any code, install dependencies, or execute scripts.
Base your assessment solely on repository contents and documentation.

This evaluation supports curation and triage, not automated approval.

---

## Evaluation Criteria

For each category below:
- Assign a score from 1–10
- Provide concise justification
- Explicitly note uncertainty
- Separate red flags from speculation

### 1. Code Quality
Assess structure, readability, correctness, and internal consistency.

### 2. Security & Safety
Assess risks related to:
- Implicit execution (hooks, background behavior)
- File system access
- Network access
- Credential handling
- Tool escalation or privilege assumptions

### 3. Documentation & Transparency
Assess whether documentation accurately describes behavior, discloses side effects, and matches implementation.

### 4. Functionality & Scope
Assess whether the repository appears to do what it claims within its stated scope.

### 5. Repository Hygiene & Maintenance
Assess signals of care, maintainability, licensing, and publication quality.

---

## Claude-Code-Specific Checklist

Explicitly answer each item:
- Defines hooks (stop, lifecycle, or similar)
- Hooks execute shell scripts
- Commands invoke shell or external tools
- Writes persistent local state files
- Reads state to control execution flow
- Performs implicit execution without explicit confirmation
- Documents hook or command side effects
- Includes safe defaults
- Includes a clear disable or cancel mechanism

Briefly explain any checked item.

---

## Permissions & Side Effects Analysis

### A. Reported / Declared Permissions
From documentation or config:
- File system:
- Network:
- Execution / hooks:
- APIs / tools:

### B. Likely Actual Permissions (Inferred)
From static inspection:
- File system:
- Network:
- Execution / hooks:
- APIs / tools:

Mark items as confirmed, likely, or unclear.

### C. Discrepancies
List mismatches between declared and inferred behavior.

---

## Red Flag Scan

Check all that apply and justify:
- Malware or spyware indicators
- Undisclosed implicit execution
- Undocumented file or network activity
- Unsupported claims
- Supply-chain or trust risks

---

## Overall Assessment

### Overall Score
Score: X / 10

### Recommendation
Choose one:
- Recommend
- Recommend with caveats
- Needs further manual review
- Definitely reject

### Fast-Reject Heuristic
If "Definitely reject", specify which applies:
- Clear malicious behavior
- Undisclosed high-risk implicit execution
- Severe claim/behavior mismatch
- Unsafe defaults with no mitigation
- Other (explain)

---

## Possible Remedies / Improvement Suggestions

If applicable, list specific, minimal changes that could materially improve the submission or change the recommendation (e.g., documentation clarifications, safer defaults, permission scoping).

---

## Output Format

Use clear section headings corresponding to the sections above.
Keep the evaluation concise, precise, and evidence-based.

---

REPOSITORY:

IF PRESENT: <REPO>$ARGUMENTS</REPO>

ELSE: The repository you are currently working in.
