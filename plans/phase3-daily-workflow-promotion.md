# Phase 3: Daily Workflow Promotion Plan

## Overview

Promote 58 deferred test scenarios from 4 feature files into the core test suite.

## Target Files

| File | Scenarios | Key Tags | Docker Required |
|------|-----------|----------|-----------------|
| documented-development-workflows.feature | 31 | @user-guide-*, @core-suite | No |
| daily-workflow.feature | 13 | @user-guide-daily-workflow | Yes (10) |
| daily-development-workflow.feature | 7 | @user-guide-daily-workflow, @user-guide-first-vm | Yes (5) |
| vm-information-and-discovery.feature | 7 | @user-guide-understanding | No |

**Total: 58 scenarios**

## Assessment Results

### Step Definitions Status

- **All step definitions exist** - No "Undefined step" errors found during dry-run
- Existing deferred step files provide coverage:
  - `documented_workflow_steps.py` (56KB)
  - `daily_workflow_steps.py` (7KB)
  - `daily_workflow_required_steps.py` (24KB)
  - `vm_info_steps.py` (17KB)

### Tags Analysis

- No @wip tags found in target files
- Most scenarios have @user-guide-* tags for User Guide generation
- 15 scenarios have @requires-docker-host (will run in Docker environment)

## Implementation Steps

### Step 1: Add @core-suite Tags (5 min)

Add `@core-suite` tag to each feature file to include in core test runs.

### Step 2: Copy Files to core-infrastructure/ (2 min)

```bash
cp tests/features/deferred/documented-development-workflows.feature tests/features/core-infrastructure/
cp tests/features/deferred/daily-workflow.feature tests/features/core-infrastructure/
cp tests/features/deferred/daily-development-workflow.feature tests/features/core-infrastructure/
cp tests/features/deferred/vm-information-and-discovery.feature tests/features/core-infrastructure/
```

### Step 3: Copy Relevant Step Files (2 min)

Promote step definition files that are exclusively used by these features:

```bash
# Review and copy if needed - most steps already in main steps/
```

### Step 4: Verify Tests Pass (10 min)

Run test suite to verify promotion works:

```bash
python3 -m behave tests/features/core-infrastructure/documented-development-workflows.feature
python3 -m behave tests/features/core-infrastructure/daily-workflow.feature
python3 -m behave tests/features/core-infrastructure/daily-development-workflow.feature
python3 -m behave tests/features/core-infrastructure/vm-information-and-discovery.feature
```

### Step 5: Run Full Suite (5 min)

```bash
python3 -m behave --tags @core-suite
```

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Tag Addition | 5 min | 5 min |
| File Copy | 2 min | 7 min |
| Step Review | 2 min | 9 min |
| Verification | 10 min | 19 min |
| Full Suite | 5 min | 24 min |

**Estimated Total: ~25 minutes**

## Expected Outcome

- Current: 263 passing scenarios
- After Phase 3: 321 passing scenarios (263 + 58)

## Risks & Mitigations

1. **Docker-dependent tests may timeout** - Already addressed in Phase G with increased timeouts
2. **Step conflicts** - Pre-existing steps reviewed; no conflicts found
3. **Tag filtering issues** - All scenarios already have appropriate @user-guide-* tags

## Resources Needed

- Terminal access for file operations
- Test execution environment
- ~25 minutes for full execution
