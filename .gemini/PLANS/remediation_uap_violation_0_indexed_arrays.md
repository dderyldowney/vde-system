# Remediation Plan: UAP Violation - 0-indexed Arrays
<!-- @forge (Agent Logic) -->

**Violation**: The Enforcer detected 0-indexed arrays in `bin/vde` and `bin/shutdown-all`.
**Mandate**: Mandate 14 (ZSH-native only, 1-indexed arrays).

## Violations
- `bin/vde`: Uses `${BASH_SOURCE[0]:-${0}}` (0-indexed array).
- `bin/shutdown-all`: Uses `${BASH_SOURCE[0]:-${0}}` (0-indexed array).

## Remediation Strategy
Replace the bash-style portable directory logic with ZSH-native, 1-indexed compliant logic that achieves the same result (absolute path to project root).

### Task List
1. [ ] **Remediate `bin/vde`**: Replace `VDE_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${0}}")" && cd .. && pwd)"` with ZSH-native `VDE_ROOT_DIR="${${0:A}:h:h}"`.
2. [ ] **Remediate `bin/shutdown-all`**: Replace `export VDE_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${0}}")" && cd .. && pwd)"` with ZSH-native `export VDE_ROOT_DIR="${${0:A}:h:h}"`.
3. [ ] **Verify**: Run `bin/vde-enforce-uap.zsh` to ensure compliance.
4. [ ] **Test**: Run `tests/verify_infra_fixes.zsh` to ensure functionality.

## Request for Approval
Please approve this remediation plan to satisfy the ZSH-only mandate and resolve the UAP failure.
