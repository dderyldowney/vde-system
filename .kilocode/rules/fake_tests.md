# FAKE TEST PROHIBITION
> **MOST CRITICAL RULE: VIOLATION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**
## FORBIDDEN PATTERNS (ABSOLUTE - NO EXCEPTIONS)
1. `assert True` — Any form of assertion that always passes | 2. `or True` patterns — Assertions with fallbacks that can't fail | 3. `getattr(context, 'xxx', True)` — Defaults to True, ALWAYS PASSES | 4. `context.xxx = True/False` — Setting flags instead of executing real commands | 5. `REMOVED:` comments — Documentation-style fake testing | 6. `"works the same as X"` — Parser-only verification without actual behavior checks | 7. `"equivalent to X"` — Intent-only checks without real system verification | 8. Placeholder step definitions — Auto-generated from undefined steps | 9. `"Simulate"` comments — Any code claiming to simulate instead of actually executing | 10. `pass` statements in @then steps — Silent bypass of verification
## REQUIRED REPLACEMENTS
| FORBIDDEN | REQUIRED |
|-----------|----------|
| `assert True, "verified"` | `docker ps` to verify actual state |
| `getattr(context, 'x', True)` | `subprocess.run(['command'])` and check result |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |
## STANDING RULE: ALL FAKE TEST VIOLATIONS MUST BE FIXED
> **EFFECTIVE DATE: January 25, 2026 (Session 33)**
**IF a Fake Test Prohibition violation is found during yume-guardian review, whether introduced by the current session or pre-existing in the codebase, IT MUST BE FIXED before proceeding.** NO EXCEPTIONS. Pre-existing violations are NOT "grandfathered". Session time constraints do NOT apply to fixing violations. The only acceptable exit from Phase 3 (yume-guardian) is CLEAN (zero violations).
