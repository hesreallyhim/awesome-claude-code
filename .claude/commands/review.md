# Code Review

Review the specified code, file, or changes: $ARGUMENTS

## Checklist

### Correctness
- Does it do what it claims?
- Logic errors or off-by-one bugs?
- Edge cases handled?

### Security
- Input sanitized for SQL, shell, HTML?
- No hardcoded secrets?
- Auth checks in place?

### Simplicity
- Unnecessary complexity?
- Could be done with less code?
- Premature abstractions?

### Maintainability
- Readable without extensive comments?
- Clear naming?
- Appropriate error handling?

## Output

- **Must fix**: Issues blocking merge
- **Consider**: Improvements worth making
- **Nitpicks**: Minor style preferences (optional)

Be direct. Skip praise for things that are simply correct.
