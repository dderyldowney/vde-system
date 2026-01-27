# FAKE TEST PROHIBITION

> **MOST CRITICAL RULE: VIOLATION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**

## FORBIDDEN PATTERNS (ABSOLUTE - NO EXCEPTIONS)

1. **`assert True`** — Any form of assertion that always passes
2. **`or True` patterns** — Assertions with fallbacks that can't fail
3. **`getattr(context, 'xxx', True)`** — Defaults to True, ALWAYS PASSES
4. **`context.xxx = True/False`** — Setting flags instead of executing real commands
5. **`REMOVED:` comments** — Documentation-style fake testing
6. **`"works the same as X"`** — Parser-only verification without actual behavior checks
7. **`"equivalent to X"`** — Intent-only checks without real system verification
8. **Placeholder step definitions** — Auto-generated from undefined steps
9. **`"Simulate"` comments** — Any code claiming to simulate instead of actually executing
10. **`pass` statements in @then steps** — Silent bypass of verification

## REQUIRED REPLACEMENTS

| FORBIDDEN PATTERN | REQUIRED REPLACEMENT |
|-------------------|---------------------|
| `assert True, "verified"` | `docker ps` to verify actual state |
| `getattr(context, 'x', True)` | `subprocess.run(['command'])` and check result |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |

## HISTORICAL VIOLATIONS (DO NOT REPEAT)

- `customization_steps.py` — 100+ placeholder steps — **DELETED**
- `ssh_docker_steps.py` lines 277-398 — Undefined step placeholders — **DELETED**
- `cache_steps.py` lines 376+ — Undefined step placeholders — **DELETED**

## UNDEFINED STEPS PROTOCOL

When Behave reports undefined steps:
1. ✅ Implement the step properly with real verification
2. ✅ Leave it undefined and accept the error
3. ❌ **NEVER** create a placeholder that just sets `context.step_xxx = True`

## STANDING RULE: ALL FAKE TEST VIOLATIONS MUST BE FIXED

> **EFFECTIVE DATE: January 25, 2026 (Session 33)**

**IF a Fake Test Prohibition violation is found during yume-guardian review, whether introduced by the current session or pre-existing in the codebase, IT MUST BE FIXED before proceeding.**

This includes but is not limited to:
- `assert True` patterns
- `or True` fallbacks
- Context flag assignments without verification
- Early returns in @then steps before assertions
- Placeholder step definitions

**NO EXCEPTIONS.**
- Pre-existing violations are NOT "grandfathered"
- Session time constraints do NOT apply to fixing violations
- The only acceptable exit from Phase 3 (yume-guardian) is CLEAN (zero violations)

**Rationale:** Fake tests invalidate the entire testing approach. Leaving them in place because "they were there before" or "we don't have time" undermines confidence in ALL test results.
