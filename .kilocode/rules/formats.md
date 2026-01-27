# REQUIRED OUTPUT FORMATS

## Git Commit Format

```bash
git commit -m "<type>: <description>

- Detail 1
- Detail 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Types:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## Task Completion Format

After completing a task, present results in this format:

```
## [Task Name] Complete

**Summary of Changes:**
- Change 1
- Change 2

**Test Results:**
- Before: X failures / Y passing
- After: Z failures / W passing

**Files Modified:**
- file1.ext - description

**Next Options:**
- Option A
- Option B
- Option C

Which would you like next?
```

## Batching Rules

**Complete ONE task → Ask what's next. DO NOT batch without user confirmation.**
