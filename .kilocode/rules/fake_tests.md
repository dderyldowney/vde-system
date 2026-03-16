# FAKE TEST PROHIBITION - COMPREHENSIVE TAXONOMY
> **MOST CRITICAL RULE: VIOLATION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**

## Definition
**Fake Tests** (also known as "toxic tests", "pink tests", "placeholder tests") are test implementations that appear to verify behavior but provide no meaningful validation, create false confidence, or mask real defects.

---

## FORBIDDEN PATTERNS (ABSOLUTE - NO EXCEPTIONS)

### CRITICAL SEVERITY (0% verification, always passes)

| # | Pattern | Example | Detection Regex |
|---|---------|---------|-----------------|
| 1 | **Tautological Assertion** | `assert True`, `assert x == x` | `assert\s+True`, `assert\s+(\w+)\s*==\s*\1` |
| 2 | **Context Flagging** | `context.docker_installed = True` | `context\.\w+\s*=\s*(True\|False)\s*$` |
| 3 | **Placeholder Step** | `def step_impl(context): pass` | `def\s+\w+\([^)]*\):\s*\n\s*pass\s*$` |
| 4 | **Fallback Truth** | `getattr(context, 'x', True)` | `getattr\s*\([^,]+,\s*['"][^'"]+['"]\s*,\s*True\s*\)` |

### HIGH SEVERITY (May pass on failure)

| # | Pattern | Example | Detection Regex |
|---|---------|---------|-----------------|
| 5 | **Removed Comment** | `# REMOVED: fake test was here` | `#\s*REMOVED:?`, `#\s*Deleted`, `#\s*Fake test` |
| 6 | **Equivalence Claim** | `# works the same as X` | `#\s*(works?\s+the\s+same\s+as\|equivalent\s+to)` |
| 7 | **Simulation Claim** | `# Simulate timeout` then `pass` | `#\s*Simulate`, `with\s+mock\.patch.*:\s*\n\s*pass` |
| 8 | **Or-True Pattern** | `assert cond or True` | `\s+or\s+True` |

### MEDIUM SEVERITY (Code runs but unverified)

| # | Pattern | Example | Detection Regex |
|---|---------|---------|-----------------|
| 9 | **Incidental Coverage** | Function call without assertion | Test function with no `assert`/`expect`/`should` |
| 10 | **Unknown Test** | Calculations with no assertion | Test function body without verification |
| 11 | **Sleepy Test** | `time.sleep(5); assert True` | `time\.sleep\s*\(`, `Thread\.sleep` |

### LOW SEVERITY (Maintainability issues)

| # | Pattern | Example | Detection Regex |
|---|---------|---------|-----------------|
| 12 | **Magic Number Assertion** | `assert result == 42` | `assert\s+\w+\s*==\s*\d+\s*$` |
| 13 | **Redundant Print** | `print(result)` no assertion | `print\s*\(` in test without `assert` |

---

## REQUIRED REPLACEMENTS

| FORBIDDEN | REQUIRED |
|-----------|----------|
| `assert True, "verified"` | `subprocess.run(['docker', 'ps'])` and check output |
| `getattr(context, 'x', True)` | `assert hasattr(context, 'x'); assert context.x` |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Delete the test OR implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |
| `time.sleep(N); assert True` | Poll with timeout + actual state check |
| `pass` in @then step | Implement verification or delete scenario |

---

## PROGRAMMATIC DETECTION SUITE

```python
FAKE_TEST_PATTERNS = {
    'tautological_assertion': [
        r'assert\s+True',
        r'assert\s+\w+\s*==\s*\1',
        r'assertTrue\s*\(\s*true\s*\)',
    ],
    'fallback_truth': [
        r'getattr\s*\([^,]+,\s*[\'"][^\'"]+[\'"]\s*,\s*True\s*\)',
        r'\.get\s*\(\s*[\'"][^\'"]+[\'"]\s*,\s*True\s*\)',
    ],
    'context_flagging': [
        r'context\.\w+\s*=\s*(True|False)\s*$',
    ],
    'placeholder_step': [
        r'def\s+\w+\([^)]*\):\s*\n\s*pass\s*$',
        r'@\w+.*skip',
        r'@Ignore',
    ],
    'equivalence_claim': [
        r'#\s*(works?\s+the\s+same\s+as|equivalent\s+to)',
        r'#\s*Verified by',
    ],
    'removed_comment': [
        r'#\s*REMOVED:?',
        r'#\s*Deleted',
        r'#\s*Fake test',
    ],
    'simulation_claim': [
        r'#\s*Simulate',
        r'with\s+mock\.patch.*:\s*\n\s*pass',
    ],
    'sleepy_test': [
        r'time\.sleep\s*\(',
        r'Thread\.sleep',
    ],
    'or_true_pattern': [
        r'\s+or\s+True',
    ],
}
```

---

## STANDING RULE: ALL FAKE TEST VIOLATIONS MUST BE FIXED

> **EFFECTIVE DATE: January 25, 2026 (Session 33)**

**IF a Fake Test Prohibition violation is found during yume-guardian review, whether introduced by the current session or pre-existing in the codebase, IT MUST BE FIXED before proceeding.** NO EXCEPTIONS. Pre-existing violations are NOT "grandfathered". Session time constraints do NOT apply to fixing violations. The only acceptable exit from Phase 3 (yume-guardian) is CLEAN (zero violations).

---

## SEVERITY-BASED REMEDIATION PRIORITY

1. **CRITICAL** → Fix immediately, blocks all other work
2. **HIGH** → Fix within current session
3. **MEDIUM** → Fix before next release
4. **LOW** → Fix during code cleanup sprints
