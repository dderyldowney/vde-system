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

## Current State (2026-03-16)

**Status: ✅ Core Infrastructure Remediation COMPLETE**

**Unit tests: 292/292 pass** | **Cache System BDD: 19/19 scenarios, 84/84 steps pass**

### This Session's Achievements (2026-03-16)

1. **Port Range Constant Fix**:
    - Corrected `VDE_LANG_PORT_END` from `2399` → `2299` to match spec (2200-2299 for languages).
    - Updated unit test to expect correct value.
2. **Port Registry Architecture**:
    - Fixed `verify_port_registry` to use `vm-types.conf/json` as source of truth (not compose files).
    - Updated cache-system BDD tests to reflect correct architecture.
    - Removed `@wip` tag from "Rebuild port registry" scenario - now fully passing.
3. **list-vms Categorization**:
    - Updated `list-vms` to display VMs categorized by type (Language/Service sections).
    - Fixed `--lang` and `--svc` flags to show only the requested type.
4. **Configuration Test Fix**:
    - Fixed `step_vm_boot_start` to check `context.restart_set` attribute before output fallback.
5. **Fake Test Remediation** (cache_steps.py):
    - Replaced 6 `assert True` with real verification logic.
    - Steps now verify: cache mtime, port file existence, valid port ranges, command execution.
6. **Knowledge Base Refresh**:
    - Updated syntax/semantics for ZSH, Python, YAML, JSON, Docker via context7 MCP.

### Key Architecture Decisions
- **Port Registry Source of Truth**: `vm-types.conf` and `vm-types.json` (column 7 / `ssh_port` field).
- **SSH Config**: Generated from vm-types, only changes when VM types are added/removed.
- **No compose file scanning**: Compose files are templates, not authoritative for port data.

### Agent Governance
- Established "No Circular Delegation" mandate in `AGENTS.md`.
- Created specialized agent definitions in `agents/` (Scout, Coder, etc.).
- Created root-level `GEMINI.md` to strictly enforce `AGENTS.md` protocols.

---

## Historical State (2026-03-11)

**Shell/Zsh Tests: 360 passing** | **Unit tests (isolated): 18/18 pass**

... [rest of file remains same] ...
