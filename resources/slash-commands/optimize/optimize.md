# Optimize

Analyze the performance of `$ARGUMENTS` and suggest concrete optimizations.

## Behavior

1. **Read** the code the user is asking about. If `$ARGUMENTS` names a file, read it. If it names a function or component, find and read it.

2. **Profile the current state** if possible:
   - Check for existing benchmarks or performance tests
   - Look at algorithmic complexity (loops, nested iterations, repeated work)
   - Check for I/O patterns (N+1 queries, unbatched API calls, synchronous blocking)
   - Check for memory patterns (large allocations, copies that could be references, leaks)

3. **Identify the top 3 bottlenecks**, ranked by likely impact. For each one:
   ```
   BOTTLENECK: [what's slow]
   WHERE: [file:line or function name]
   WHY: [why it's slow -- be specific about the mechanism]
   FIX: [concrete change, not vague advice]
   IMPACT: [estimated improvement -- e.g., "O(n^2) -> O(n)", "eliminates 50 redundant DB queries"]
   ```

4. **Ask before applying:** "Want me to implement any of these? I'd start with #1 since it has the most impact."

5. **If the user says go:** implement the fix, run tests, verify no regressions.

## What Good Optimization Advice Looks Like

- Names specific lines and functions, not general principles
- Explains *why* something is slow, not just *that* it's slow
- Proposes a concrete diff, not "consider using caching"
- Estimates the impact so the user can prioritize
- Doesn't sacrifice readability for marginal gains
