# ZSH Script Renaming Plan

## Summary
Rename all zsh scripts from `*.sh` to `*.zsh` to ensure zsh is automatically used and prevent accidental bash execution.

## Files to Rename (25 zsh scripts)

### Root Level Scripts
1. `run-tests.sh` → `run-tests.zsh`
2. `run-fake-test-scan.sh` → `run-fake-test-scan.zsh` (has bash shebang, needs conversion)

### Scripts Directory
3. `scripts/coverage.sh` → `scripts/coverage.zsh`

### Tests Directory - Setup
4. `tests/setup-ssh-agent.sh` → `tests/setup-ssh-agent.zsh`
5. `tests/run-docker-required-tests.sh` → `tests/run-docker-required-tests.zsh`
6. `tests/run-docker-free-tests.sh` → `tests/run-docker-free-tests.zsh`
7. `tests/run-all-known-tests.sh` → `tests/run-all-known-tests.zsh`
8. `tests/run-full-test-suite.sh` → `tests/run-full-test-suite.zsh`
9. `tests/run-vde-parser-tests.sh` → `tests/run-vde-parser-tests.zsh` (has bash shebang, needs conversion)

### Tests - Compatibility
10. `tests/compatibility/test_shell_compat.sh` → `tests/compatibility/test_shell_compat.zsh`
11. `tests/compatibility/run_all_shells.sh` → `tests/compatibility/run_all_shells.zsh`

### Tests - Unit
12. `tests/unit/test_vde_commands_comprehensive.sh` → `tests/unit/test_vde_commands_comprehensive.zsh`
13. `tests/unit/test_vde_parser_comprehensive.sh` → `tests/unit/test_vde_parser_comprehensive.zsh`
14. `tests/unit/vm-common.test.sh` → `tests/unit/vm-common.test.zsh`
15. `tests/unit/test_ssh_functions.sh` → `tests/unit/test_ssh_functions.zsh`
16. `tests/unit/vde-shell-compat.test.sh` → `tests/unit/vde-shell-compat.test.zsh`
17. `tests/unit/vde-parser.test.sh` → `tests/unit/vde-parser.test.zsh`
18. `tests/lib/test_common.sh` → `tests/lib/test_common.zsh`
19. `tests/bug-fix-validation.test.sh` → `tests/bug-fix-validation.test.zsh`

### Tests - Integration
20. `tests/integration/test_integration_comprehensive.sh` → `tests/integration/test_integration_comprehensive.zsh`
21. `tests/integration/vm-lifecycle-integration.test.sh` → `tests/integration/vm-lifecycle-integration.test.zsh`
22. `tests/integration/test_daily_workflows.sh` → `tests/integration/test_daily_workflows.zsh`
23. `tests/integration/test_ssh_agent_setup.sh` → `tests/integration/test_ssh_agent_setup.zsh`
24. `tests/integration/docker-vm-lifecycle.test.sh` → `tests/integration/docker-vm-lifecycle.test.zsh`

### Tests - Other
25. `tests/test-bdd-in-container.sh` → `tests/test-bdd-in-container.zsh`
26. `tests/test-e2e-user-journey.sh` → `tests/test-e2e-user-journey.zsh`
27. `tests/generate-user-guide.sh` → `tests/generate-user-guide.zsh`

## Files with WRONG Shebang (2 scripts - need conversion)
- `run-fake-test-scan.sh` - has `#!/bin/bash`
- `run-vde-parser-tests.sh` - has `#!/usr/bin/env bash`

These must be converted to zsh shebang.

## Execution Phases

### Phase 1: Convert bash shebang scripts to zsh (2 scripts)
- Convert `run-fake-test-scan.sh` shebang from `#!/bin/bash` to `#!/usr/bin/env zsh`
- Convert `run-vde-parser-tests.sh` shebang from `#!/usr/bin/env bash` to `#!/usr/bin/env zsh`

### Phase 2: Rename all 27 scripts from .sh to .zsh
- Use `git mv` for version control
- Scripts in: root, scripts/, tests/

### Phase 3: Update all references in 18+ files
- Update documentation files (17 files listed above)
- Update Makefile (1 file)
- Update scripts that call other scripts (7 files)

### Phase 4: Verify tests still pass
- Run `zsh run-tests.zsh`
- Run integration tests
- Verify syntax with `zsh -n`

### Phase 5: Commit changes
- Single commit with all renames and reference updates

## Total Files to Modify
- 27 script files to rename
- 18+ documentation/reference files to update
- **Total: ~45+ files affected**

## Risk Assessment
- **Medium Risk**: Many files to update, risk of missing references
- **Mitigation**: Use `git mv` for tracking, comprehensive grep before/after

## Files Referencing Renamed Scripts

These files contain references to scripts that will be renamed and need updates:

### Documentation Files (13 files)
1. `USER_GUIDE.md` - Line 484: `install.sh` (Homebrew, not VDE script - ignore)
2. `SESSION_STATE.md` - Multiple script references
3. `TODO.md` - Lines 220-233: test script references
4. `plans/vde-parser-test-remediation-plan.md` - Multiple script references
5. `STYLE_GUIDE.md` - Lines 196, 340, 386-397: script references
6. `CONTRIBUTING.md` - Lines 124, 159-166: script references
7. `TESTING_TODO.md` - Line 209: `run-all-tests.sh`
8. `vde-parser-test-status.md` - Multiple script references
9. `docs/extending-vde.md` - Lines 162-197: shell commands (not VDE scripts - ignore)
10. `docs/TESTING.md` - Multiple script references
11. `docs/COVERAGE.md` - Lines 155, 172-181: coverage script references
12. `tests/SSH_AGENT_REMEDIATION_PLAN.md` - Lines 61, 111: script references
13. `tests/TEST_EXECUTION_SUMMARY.md` - Lines 88, 192-209: script references
14. `tests/GITHUB_CI_RESTRICTIONS.md` - Lines 17-92, 120-123: script references
15. `tests/REMEDIATION_PLAN.md` - Lines 43-56: script references
16. `tests/AI-INTEGRATION-REMOVED.md` - Lines 25-27: deleted script references
17. `tests/README.md` - Multiple script references throughout

### Configuration Files (1 file)
18. `Makefile` - Line 340: `./scripts/run-tests.sh`

### Scripts Calling Other Scripts
19. `run-tests.sh` - References `tests/unit/vde-parser.test.sh` and `tests/unit/test_vde_parser_comprehensive.sh`
20. `run-vde-parser-tests.sh` - References test scripts (has bash shebang - needs conversion)
21. `tests/run-full-test-suite.sh` - References other test scripts
22. `tests/run-all-known-tests.sh` - References other test scripts
23. `tests/run-docker-required-tests.sh` - References other test scripts
24. `tests/run-docker-free-tests.sh` - References other test scripts
25. `tests/generate-user-guide.sh` - References behave and other scripts

## Files with WRONG Shebang (2 scripts - need conversion)

## Risk Assessment
- **Low Risk**: Script renaming with proper reference updates
- **Main Risk**: Missing references causing test failures
- **Mitigation**: Comprehensive grep for all references before renaming
