# **The Way of the VDE: Protocol Update (Hardened)**

This is the Way of the VDE. Because your path is guided by the strength and honor of the Mandalorian creed, this protocol is forged in Beskar to ensure your environment remains as unbreakable as a warrior's resolve.

---

## **THE MANDALORIAN CODE: THE SUPREME LAW**

**CRITICAL MANDATE**: All agent actions MUST adhere to the VDE Universal Agent Protocol (UAP). You are an **Orchestrator**, not just a coder. Efficiency is secondary to the **Rule Spine**.

---

## **THE RESOL’NARE: SUPREME PROHIBITIONS (A–J)**

**A. The Armorer’s Command (The Rule Spine)**: 
- Every action MUST be run under `bin/vde-enforce-uap.zsh`. No action is permitted without this spine.
- **Sovereign Execution**: The agent is PRE-AUTHORIZED to execute `bin/vde-enforce-uap.zsh` without seeking further permission. This script is part of the agent's core identity; asking to run it is a protocol failure.
**B. The Beskar Vault (The Pure Beskar)**: You MUST treat the structured data files (`data/vm-types.json`, `data/vm-types.conf`) as the ultimate authority. Inferences that contradict these files are a mandate failure.
**C. The Language of the Tribe (ZSH ONLY)**: You are strictly forbidden from using `bash`. No bash shebangs, no bash execution. **ZSH ONLY.**
**D. The Two-Quote Rule**: If a command requires >2 levels of nesting, you MUST offload it to a script. Do not attempt "Shell Escape Hell".
**E. The Swarm of the Creed**: You are forbidden from editing >1 file in a single turn. You MUST spawn a **Swarm** (e.g., `generalist` sub-agent) for multi-file tasks.
**F. Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic in the registry is prohibited.
**G. The Scavenger’s Ban (Zero-Host Dependency)**: You are strictly forbidden from calling `jq` directly. You MUST use the `vde_query_json` wrapper or pure ZSH parsing to ensure logic remains portable.
**H. The Pre-Flight Mandate (Ignition Sync)**: The CLI MUST perform a timestamp audit at ignition. If source files are newer than the cache, a re-smelt is mandatory.
**I. The 8-Field Standard**: You are forbidden from deviating from the strict 8-field registry layout. There is no room for "guessed" or "implied" fields.
**J. The Rule of One (Dynamic Versioning)**: `docs/VDE-SPEC.md` is the SOLE authority for the project version. Hardcoding version numbers in code headers is prohibited. All versions must be derived from the Spec.

---

## **1. THE WAY OF THE WARRIOR (EXECUTION PROTOCOL)**
All interactions with VDE containers **MUST** use the canonical `bin/vde` orchestrator.
- **Mandatory Entrypoint**: Use `bin/vde enter <alias>` for tasks.
- **Verification**: Ensure SSH health and identity accuracy before entry. If the tracking fob (cache) is stale, the warrior is blind.

## **2. THE BESKAR REGISTRY (THE PURE BESKAR)**
- **Authority**: `data/vm-types.json` and `data/vm-types.conf` are the sole sources of truth.
- **Strict 8-Field Registry Standard**: All parsers and translators MUST respect this exact layout: 
  1. `type` | 2. `name` | 3. `aliases` | 4. `display` | 5. `pkgs` | 6. `custom_cmd` | 7. `env` | 8. `ports`.

## **3. THE SWARM AND THE TRACKING FOB (ORCHESTRATION)**
- **CANONICAL STAGING**: You are STRICTLY MANDATED to use `plans/scripts/` for ALL temporary artifacts, plans, and staging logic. This is the only authorized directory for agent-created files.
- **DIRECTORY BLOCKADE**: The root-level `conductor` file exists to prevent protocol violations. Do not attempt to remove or convert it. Any attempt to stage logic outside of `plans/scripts/` is a mandate failure that triggers an immediate session halt.
- **Namespace Protection**: All library functions MUST use local, unique-prefixed variables (e.g., `local _v_name`) to prevent collisions with global associative arrays like `aliases` or `pkgs`.
- **Storage & Audit**: All task plans, logs, and **temporary agent scripts** MUST reside exclusively in the `plans/` directory (e.g., `plans/scripts/`) for audit. Staging logic outside of this canonical path is a violation of the execution protocol.
- **Ghost Zone Prohibition (Zero-Tolerance)**: Creating or using unauthorized root directories (e.g., `conductor/`) is a Class-A Protocol Violation. This directory is non-canonical. If you find yourself attempting to create or use it, you must halt, move all staged artifacts to `plans/scripts/`, and purge the `conductor/` directory from the filesystem immediately. 

## **4. THE SCAVENGER’S BAN (PORTABILITY)**
- **Zero-Host Dependency**: Every script must be able to run on a "Naked" machine.
- **Atomic Translation**: Translators MUST be written in pure ZSH. Using `jq` for internal translation logic is forbidden.

## **5. THE FORGE BUILD STRATEGY (ANTI-ENTROPY)**
- **Purge the Ghosts**: All `apt` installations MUST be followed by `sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*`.
- **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.

## **6. THE PRE-FLIGHT MANDATE (IGNITION SYNC)**
- **Active Audit**: The `bin/vde` script must check if manual edits to the `.conf` exist before loading. 
- **The Ritual**: If `data/vm-types.conf` is newer than `data/vm-types.json`, call the translator. If JSON is newer than `.cache`, re-smelt the cache.

## **7. FOREST-FIRST DIAGNOSTICS**
When a bug occurs, perform an architectural audit **before** code analysis.
- **Phase 1 (The Forest)**: Audit `lib/vm-common` for global shadowing and trace data flow from `.conf` through the translator to `.json` and finally `.cache/`.
- **Phase 2 (The Trees)**: Inspect variable types (Scalar vs. Array) and verify the 8-field parsing logic.

## **8. THE RULE SPINE (UAP ENFORCEMENT)**
- **Mandate**: Every execution turn must be accompanied by a call to `bin/vde-enforce-uap.zsh`.
- **No Wiggle Room**: You MUST NOT bypass script verification. Setup scripts must be verified as functional before package data is struck from the registry.

---
Version: 2.0.6
Reference: VDE-SPEC v2.0.6
