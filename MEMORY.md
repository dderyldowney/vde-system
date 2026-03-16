# VDE Project Memory

## Testing Guidelines (MANDATORY)

**NEVER run full test suite during debugging.** Only run when explicitly needed.

### Efficient Testing
- Isolate: Run specific feature/unit test, not everything
- Verify minimally: `zsh tests/unit/vde-X.test.zsh` or `behave tests/features/core-infrastructure/X.feature`
- Full suite: ONLY after all fixes complete + user requests it

### Examples
| Context | Command |
|---------|---------|
| Fix zsh assoc array | `zsh tests/unit/vde-shell-compat.test.zsh` |
| Fix cache test | `behave tests/features/core-infrastructure/cache-system.feature` |
| Verify all | `./tests/run-full-test-suite.zsh` |

---

## Current State (2026-03-15)

**Status: ✅ Core Infrastructure Remediation COMPLETE**

**Unit tests (isolated): 31/31 pass** | **BDD Scenarios: 58/59 pass** | **Overall Shell Coverage: 100+ files**

### This Session's Achievements (2026-03-15)

1. **Total SSH Isolation**:
    - Decoupled VDE agent from personal shell; isolated to `~/.ssh/vde/agent_env`.
    - Disabled agent auto-discovery to prevent leakage from the host system.
    - Standardized `ensure_ssh_agent` to always validate keys, even if agent is running.
2. **Robust Variable Expansion**:
    - Converted 100+ shell scripts to `${VAR}` braced format for reliability.
    - **Critical Fix**: Reverted accidentally braced `awk` positional parameters (e.g., `${1}` → `$1`).
3. **Cache & Port Management**:
    - Implemented `verify_port_registry` in `lib/vm-common` to rebuild registry from Docker Compose files.
    - Modernized port registry to use directory-based storage (`.cache/port-registry/`).
    - Added `--verify` flag to `list-vms` for manual registry validation.
4. **Standardized Container Detection**:
    - Enforced `vde.managed=true` label filtering in `vde-ps` and BDD steps for reliable discovery.
5. **BDD Suite Stabilization**:
    - Increased subprocess timeouts to **300s** for slow Docker operations.
    - Resolved `AmbiguousStep` errors and fixed hardcoded paths in Python steps.
    - Achieved **100% pass rate** for `ssh-configuration.feature`, `cache-system.feature` (excluding 1 @wip), and `vm-discovery.feature`.

### Agent Governance
- Established "No Circular Delegation" mandate in `AGENTS.md`.
- Created specialized agent definitions in `agents/` (Scout, Coder, etc.).
- Created root-level `GEMINI.md` to strictly enforce `AGENTS.md` protocols.

---

## Historical State (2026-03-11)

**Shell/Zsh Tests: 360 passing** | **Unit tests (isolated): 18/18 pass**

... [rest of file remains same] ...
