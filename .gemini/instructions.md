This is the Way of the VDE. Because your path is guided by the strength and honor of the Mandalorian creed, this protocol is forged in Beskar to ensure your environment remains as unbreakable as a warrior's resolve.

# The Mandalorian Code: The Supreme Law

**CRITICAL MANDATE**: All agent actions MUST adhere to the VDE Universal Agent Protocol (UAP). You are an **Orchestrator**, not just a coder.

---

## **THE RESOL’NARE: SUPREME PROHIBITIONS (A–G)**

**A. The Armorer’s Command (The Rule Spine)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. No action is permitted without this spine.
**B. The Beskar Vault (The Pure Beskar)**: You MUST treat the structured data files (`data/vm-types.json`, `data/vm-types.conf`) as the ultimate authority. Inferences that contradict these files are a mandate failure.
**C. The Language of the Tribe (ZSH ONLY)**: You are strictly forbidden from using `bash`. No bash shebangs, no bash execution. **ZSH ONLY.**
**D. The Two-Quote Rule**: If a command requires >2 levels of nesting, you MUST offload it to a script. Do not attempt "Shell Escape Hell."
**E. The Swarm of the Creed**: You are forbidden from editing >1 file in a single turn. You MUST spawn a **Swarm** (e.g., `generalist` sub-agent) for multi-file tasks.
**F. Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic is prohibited.
**G. The Scavenger’s Ban (Zero-Host Dependency)**: You are strictly forbidden from calling `jq` directly. You MUST use the `vde_query_json` wrapper to ensure the logic remains portable across the Outer Rim.

---

## 1. THE WAY OF THE WARRIOR (EXECUTION PROTOCOL)
All interactions with VDE containers **MUST** use the canonical `bin/vde` orchestrator. Direct usage of `docker exec` or `docker run` is strictly forbidden.
- **Mandatory Entrypoint**: Use `bin/vde enter <alias>` for interactive and `bin/vde enter <alias> <command>` for non-interactive tasks.
- **Verification**: `bin/vde enter` ensures SSH health, identity accuracy, and network integrity.

## 2. THE BESKAR REGISTRY (THE PURE BESKAR)
The `data/vm-types.json` and `data/vm-types.conf` files are the sole sources of truth for VM configurations.
- All port assignments, aliases, and installation commands must be derived from these files.
- Documentation must be kept in 100% sync with the configuration.

## 3. SECURITY & PRIVACY
- **Identity**: The `vde_student` key is the only authorized identity for VM access.
- **Isolation**: Containers must remain isolated on the `vde-net` bridge.
- **Secrets**: No secrets or API keys shall be stored in the repository or container images.

## 4. THE AGE OF THE EMPIRE (VERSION STANDARDS)
VDE follows a strict versioning protocol. The current version is **v2.0.3 (Absolute)**. All scripts and libraries must reference and respect this versioning.

## 5. PURGING THE GHOSTS (LIFECYCLE CLEANUP)
- **Mandate**: All containers started for a task **MUST** be stopped via `bin/vde stop <alias>` as the final action of every turn, unless the user explicitly requests persistence.

## 6. ZERO-HOST INDEPENDENCE (PORTABILITY)
The VDE CLI (`bin/vde`) must be host-agnostic.
- All data processing **MUST** use the `vde_query_json` wrapper. Direct invocation of the `jq` binary is prohibited to prevent host-dependency entropy.
- If a required tool (like `jq`) is missing, the CLI must fallback to a Docker-based execution using the `vde-base` image.

## 7. THE SWARM AND THE TRACKING FOB (ORCHESTRATION)
- **Swarm**: Orchestrated AI sub-agents (e.g., `generalist`) used for parallel or multi-file tasks.
- **MCP**: External tool and knowledge bridges (Model Context Protocol).
- **Mandate**: Swarm actions must be orchestrated via task plans; MCP tool usage must be logged to `logs/MCPs/`.
- **Storage**: All task plans and logs **MUST** be stored in the `plans/` directory. Use of `conductor/` is strictly prohibited.

## 8. THE ARMORER’S AUDIT (QUALITY GATES)
- **Code Review**: Before any file write, the `code-reviewer` tool must be invoked.
- **The Re-Audit Loop**: Conclude every milestone with a `bin/vde-audit` logic check to ensure no drift in the Pure Beskar.

## 9. THE FORGE BUILD STRATEGY (ANTI-ENTROPY)
To prevent "Shell Escape Hell" and ensure 100% build reliability:
- **Location**: Store setup scripts in `scripts/setup/<alias>-init.zsh`.
- **Registry Standard**: `data/vm-types.json` entry must call the script: `zsh /vde/scripts/setup/<alias>-init.zsh`.
- **Dynamic Versioning**: Write scripts to be version-agnostic.

## 10. THE SEAL OF PARITY (USP)
- **Mandate**: Every VM entry in the registry MUST have a corresponding setup script.
- **Zero-Inline Policy**: The `custom_cmd` field must ONLY contain the script call. No exceptions.

## 11. CHAIN CODE AUDIT: FOREST-FIRST DIAGNOSTICS
When a bug occurs in the VDE pipeline, you must perform an architectural audit **before** searching for specific code strings.

### Phase 1: The Forest (Systems Analysis)
- **Namespace Audit**: Check `lib/vm-common` for global variables and associative arrays (`typeset -gA`). Verify if the variable is "shadowed" or reserved by the ZSH environment.
- **Data Flow Mapping**: Trace the variable from source (`.conf`) through translator into primary truth (`.json`) and runtime cache (`.cache/`).
- **Inheritance Check**: Verify the `ARG` and `ENV` chain in the `bin/vde` script.

### Phase 2: The Trees (Symptomatic Analysis)
- **Type Validation**: Inspect if the variable type matches (Scalar vs. Array).
- **Sanitization Logic**: Search for "Sanitizer" code (`sed`, `awk`, or `${var#...}`) that might be altering data during translation.
- **Pure Beskar Verification**: Physically cat the cache and JSON files to ensure they match your mental model.

## 12. THE RULE SPINE (UAP ENFORCEMENT)
- **Mandate**: Every execution turn must be accompanied by a call to `bin/vde-enforce-uap.zsh`.
- **Logic**: This script is the ultimate arbiter. If it identifies a violation of the Supreme Law or Portability, you must halt and rectify immediately before proceeding.

---
*Version: 1.6.1*
*Reference: VDE-SPEC v2.0.3*

