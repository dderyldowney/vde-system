# USER GUIDE GENERATION
The `USER_GUIDE.md` documents the COMPLETE user experience. Users will use Docker, so scenarios requiring Docker MUST be included.
## Generation Workflow
**1. Run FULL test suite locally (Docker required):** `./tests/run-full-test-suite.zsh`
**2. Generate Behave JSON results:** `behave --format json -o tests/behave-results.json tests/features/`
**3. Generate the User Guide:** `python3 tests/bin/generate_user_guide.py`
## What Gets Committed
| File | Tracked? | Reason |
|------|----------|--------|
| `USER_GUIDE.md` | ✅ YES | The documentation users see |
| `tests/bin/generate_user_guide.py` | ✅ YES | The generator script |
| `tests/behave-results.json` | ❌ NO | Build artifact, in `.gitignore` |
