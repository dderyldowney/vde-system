# VDE Execution Protocol: The Supreme Law

**CRITICAL MANDATE**: All agent actions MUST adhere to the VDE Universal Agent Protocol (UAP). You are an **Orchestrator**, not just a coder.

**ABSOLUTE FAILURES TO AVOID (STOP AND RETHINK):**
1.  **Rule A (Enforcer Supervision)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. No action is permitted without this spine.
2.  **Rule 2: MATERIAL TRUTH (Data Authority)**: You MUST treat the structured data files (`data/vm-types.json`, `data/vm-types.conf`) as the ultimate authority. Inferences that contradict these files are a mandate failure.
3.  **ZSH ONLY**: You are strictly forbidden from using `bash`. No bash shebangs, no bash execution. **ZSH ONLY.**
4.  **The Two-Quote Rule**: If a command requires >2 levels of nesting, you MUST offload it to a script. Do not attempt "Shell Escape Hell."
5.  **Multi-File Refactors**: You are forbidden from editing >1 file in a single turn. You MUST spawn a **Swarm** (e.g., `generalist` sub-agent) for multi-file tasks.
6.  **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic is prohibited.

---

## 1. EXECUTION PROTOCOL (AUTHORITATIVE ONLY)
All interactions with VDE containers **MUST** use the canonical `bin/vde` orchestrator. Direct usage of `docker exec` or `docker run` (outside the orchestrator) is strictly forbidden.
- **Mandatory Entrypoint**: Use `vde enter <alias>` for interactive and `vde enter <alias> <command>` for non-interactive tasks.
- **Verification**: `vde enter` ensures SSH health, identity accuracy, and network integrity.

## 2. MATERIAL TRUTH (DATA AUTHORITY)
The `data/vm-types.json` and `data/vm-types.conf` files are the sole sources of truth for VM configurations.
- All port assignments, aliases, and installation commands must be derived from these files.
- Documentation (e.g., `predefined-vm-types.md`) must be kept in 100% sync with the configuration.

## 3. SECURITY & PRIVACY
- **Identity**: The `vde_student` key is the only authorized identity for VM access.
- **Isolation**: Containers must remain isolated on the `vde-net` bridge.
- **Secrets**: No secrets or API keys shall be stored in the repository or container images.

## 4. VERSION STANDARDS
VDE follows a strict versioning protocol. The current version is **v2.0.3 (Absolute)**. All scripts and libraries must reference and respect this versioning.

## 5. LIFECYCLE CLEANUP (EPHEMERAL MANDATE)
- **Mandate**: All containers started for a task **MUST** be stopped via `bin/vde stop <alias>` as the final action of every turn, unless the user explicitly requests persistence.

## 6. PORTABILITY (ZERO-HOST-DEPENDENCY)
The VDE CLI (`bin/vde`) must be host-agnostic.
- All data processing (e.g., JSON queries) must use the `vde_query_json` wrapper.
- If a required tool (like `jq`) is missing on the host, the CLI must fallback to a Docker-based execution using the `vde-base` image.

## 2.1 PROTOCOL ENFORCEMENT (UAP)
- **Mandate**: Every execution turn must be preceded or accompanied by a call to `vde-enforce-uap.zsh`.
- **Logic**: If the script identifies a violation of the Supreme Law or Portability, you must halt and rectify immediately.

## 7. INTELLIGENCE & ORCHESTRATION (SWARM+MCP)
- **Mandate**: For complex tasks, you MUST utilize the **Swarm+MCP** pattern.
- **Storage**: All task plans, logs, and orchestration files **MUST** be stored in the `plans/` directory (relative to project root). Use of `conductor/` is strictly prohibited.
- **Capability**: Leverage MCP servers to extend reach into external documentation.

## 8. QUALITY GATES & CONTINUOUS AUDIT
- **Code Review**: Before any file write, the `code-reviewer` tool must be invoked.
- **The Re-Audit Loop**: Conclude every major milestone with a `vde-audit` logic check to ensure no drift in the Material Truth.

## 9. COMPLEX BUILD STRATEGY (ANTI-ENTROPY)
To prevent "Shell Escape Hell" and ensure 100% build reliability:
- **Location**: Store setup scripts in `scripts/setup/<alias>-init.zsh`.
- **Registry Standard**: `data/vm-types.json` entry must call the script: `zsh /vde/scripts/setup/<alias>-init.zsh`.
- **Dynamic Versioning**: Write scripts to be version-agnostic (e.g., using `ls` or `find` to locate paths).

## 10. UNIVERSAL SCRIPT PARITY (USP)
- **Mandate**: Every VM entry in the registry MUST have a corresponding setup script.
- **Zero-Inline Policy**: The `custom_cmd` field must ONLY contain the script call. No exceptions.

---
*Version: 1.5.0*
*Reference: VDE-SPEC v2.0.3*

