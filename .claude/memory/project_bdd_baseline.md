---
name: VDE BDD fast-suite baseline
description: Current BDD test baseline after Phase N — fast suite stats, what's in each bucket, and how to run
type: project
---

Fast test baseline as of 2026-03-28 (all 8 phases O-1–O-8 complete, all audit fixes committed):

```
python3 -m behave tests/features/ --tags="not @integration" -q
268 passed, 0 failed, 187 skipped
Runtime: ~2m35s
```

Confirmed on 2026-03-28. Never let this regress.

**Why:** 187 @integration scenarios require Docker and are skipped in fast suite. 268 is the confirmed non-Docker baseline after O-8 (productivity.feature step defs + all audit fixes applied in 23914c3 + 4dfbaf9).

**How to apply:**
- Fast (no Docker): `python3 -m behave tests/features/ --tags="not @integration" -q` — should pass in ~2.5 min
- Integration (requires Docker): `python3 -m behave tests/features/ --tags="@integration" -q`
- Dry-run to check step defs: `python3 -m behave --dry-run tests/features/core-infrastructure/<feature>.feature`
