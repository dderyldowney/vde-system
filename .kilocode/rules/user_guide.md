# USER GUIDE GENERATION

The `USER_GUIDE.md` documents the COMPLETE user experience. Users will use Docker, so scenarios requiring Docker MUST be included.

## Generation Workflow

**1. Run FULL test suite locally (Docker required)**
```bash
./tests/run-docker-required-tests.sh
```

**2. Generate Behave JSON results**
```bash
behave --format json -o tests/behave-results.json tests/features/
```

**3. Generate the User Guide**
```bash
python3 tests/scripts/generate_user_guide.py
```

## What Gets Committed

| File | Tracked? | Reason |
|------|----------|--------|
| `USER_GUIDE.md` | ✅ YES | The documentation users see |
| `tests/scripts/generate_user_guide.py` | ✅ YES | The generator script |
| `tests/behave-results.json` | ❌ NO | Build artifact, in `.gitignore` |
