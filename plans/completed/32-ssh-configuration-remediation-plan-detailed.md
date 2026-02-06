# Plan 32: SSH Configuration Remediation - Detailed Implementation

## Executive Summary

**Status:** PENDING - Infrastructure Fixed by Plan 31
**Feature:** `tests/features/docker-required/ssh-configuration.feature`
**Scope:** 108 undefined steps + 7 errors (LARGEST)

## Overview

This plan details the granular steps to fix the SSH Configuration test suite with 28 scenarios containing 108 undefined steps and 7 errors.

## Granular Implementation Steps

### Phase 1: Discovery & Consolidation

1. **1.1** Run dry-run to identify exact undefined steps
2. **1.2** List all SSH-related patterns in pattern_steps.py
3. **1.3** Check for AmbiguousStep conflicts between files

### Phase 2: Add Missing GIVEN Steps

4. **2.1** Add step: `~/.ssh/ contains SSH keys`
5. **2.2** Add step: `both "id_ed25519" and "id_rsa" keys exist`
6. **2.3** Add step: `~/.ssh/config exists with existing host entries`
7. **2.4** Add step: `~/.ssh/config exists with custom settings`
8. **2.5** Add step: `~/.ssh/config contains python-dev configuration`
9. **2.6** Add step: `~/.ssh/config exists with comments and formatting`
10. **2.7** Add step: `~/.ssh/config does not exist`
11. **2.8** Add step: `~/.ssh directory does not exist`
12. **2.9** Add step: `VM "postgres" is created with SSH port "2400"`
13. **2.10** Add step: `~/.ssh/known_hosts contains "[localhost]:2400"`

### Phase 3: Add Missing WHEN Steps

14. **3.1** Add step: `detect_ssh_keys runs`
15. **3.2** Add step: `primary SSH key is requested`
16. **3.3** Add step: `merge_ssh_config_entry starts but is interrupted`
17. **3.4** Add step: `new SSH entry is merged`
18. **3.5** Add step: `I create VM "python" with SSH port "2200"`
19. **3.6** Add step: `I remove VM for SSH cleanup "python"`
20. **3.7** Add step: `VM with port "2200" is removed`

### Phase 4: Add Missing THEN Steps

21. **4.1** Add step: `"id_ed25519" keys should be detected`
22. **4.2** Add step: `"id_rsa" keys should be detected`
23. **4.3** Add step: `"id_ed25519" should be returned as primary key`
24. **4.4** Add step: `~/.ssh/config should still contain "Host github.com"`
25. **4.5** Add step: `new "Host python-dev" entry should be appended to end`
26. **4.6** Add step: `~/.ssh/config should contain new "Host rust-dev" entry`
27. **4.7** Add step: `error should indicate entry already exists`
28. **4.8** Add step: `~/.ssh/config should either be original or fully updated`
29. **4.9** Add step: `temporary file should be created first`
30. **4.10** Add step: `atomic mv should replace original config`
31. **4.11** Add step: `~/.ssh/config should be created with permissions "600"`
32. **4.12** Add step: `~/.ssh directory should be created`
33. **4.13** Add step: `blank lines should be preserved`
34. **4.14** Add step: `no entries should be lost`
35. **4.15** Add step: `backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"`
36. **4.16** Add step: `merged entry should contain "HostName localhost"`
37. **4.17** Add step: `merged entry should contain "User devuser"`
38. **4.18** Add step: `~/.ssh/known_hosts should NOT contain entry for "[::1]:2200"`
39. **4.19** Add step: `known_hosts backup file should exist at "~/.ssh/known_hosts.vde-backup"`
40. **4.20** Add step: `command should succeed without error`
41. **4.21** Add step: `SSH connection should succeed without host key warning`

### Phase 5: Fix 7 Error Scenarios

42. **5.1** Fix "Sync public keys to VDE directory" ERROR
43. **5.2** Fix "Atomic SSH config update prevents corruption" ERROR
44. **5.3** Fix remaining 5 error scenarios
45. **5.4** Verify all error scenarios resolved

### Phase 6: Validation

46. **6.1** Run full ssh-configuration.feature test suite
47. **6.2** Verify all 28 scenarios pass
48. **6.3** Document any remaining issues

## Files Involved

- `tests/features/docker-required/ssh-configuration.feature`
- `tests/features/steps/ssh_config_steps.py`
- `tests/features/steps/pattern_steps.py`
- `tests/features/steps/documented_workflow_steps.py`

## Test Commands

```bash
# Dry run to see undefined steps
python3 -m behave tests/features/docker-required/ssh-configuration.feature --dry-run

# Full run with verbose
python3 -m behave tests/features/docker-required/ssh-configuration.feature -v

# Check for AmbiguousStep
python3 -m behave tests/features/docker-required/ssh-configuration.feature 2>&1 | grep -i ambiguous
```

## Expected Outcome

After completion:
- 108 undefined → 0 undefined
- 7 errors → 0 errors
- 28 scenarios passing
