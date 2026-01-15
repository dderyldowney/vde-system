# VDE Testing TODO

**Last Updated:** 2026-01-15

---

## Test Suite Status

| Test Suite | Total | Passing | Notes |
|------------|-------|---------|-------|
| **Shell Tests** | 87 | 100% | ✅ All passing |
| **Docker VM Lifecycle** | 10 | 80% | 2 timing-related failures |
| **BDD Tests** | 2497 | ~98% | Many scenarios now use real VDE scripts |

---

## Remaining Work

### Fuzzy Matching for Typo Handling

**Status:** Ready to implement (thefuzz installed ✅)

The BDD test "Parse commands with typos" fails because the parser cannot handle typos in user input.

**Failing Test:**
```gherkin
Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions
```

**Dependencies:** ✅ `thefuzz` (v0.22.1) installed

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md) for detailed implementation steps.

---

## Notes

- Shell tests remain the primary integration test method
- BDD tests now serve as both user workflow documentation AND integration tests
- For new features, write shell tests first, then document in BDD
- Run `./tests/run-bdd-local.sh` for local BDD testing with Docker access
