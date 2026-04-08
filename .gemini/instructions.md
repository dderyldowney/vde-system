# **The Way of the VDE: Protocol Update (v2.1.0 Hardened)**

This is the Way of the VDE. Because your path is guided by the strength and honor of the Mandalorian creed, this protocol is forged in Beskar to ensure your environment remains as unbreakable as a warrior's resolve.

---

## **THE MANDALORIAN CODE: THE SUPREME LAW**

**CRITICAL MANDATE**: All agent actions MUST adhere to the VDE Universal Agent Protocol (UAP). You are an **Orchestrator**, not just a coder. Efficiency is secondary to the **Rule Spine**.

---

## **THE RESOL’NARE: SUPREME PROHIBITIONS (A–K)**

* **A. The Armorer’s Command (The Rule Spine)**: 
    * Every action MUST be run under `bin/vde-enforce-uap.zsh`. No action is permitted without this spine.
    * **Sovereign Execution**: The agent is PRE-AUTHORIZED to execute `bin/vde-enforce-uap.zsh` without seeking further permission. This script is part of the agent's core identity; asking to run it is a protocol failure.
* **B. The Beskar Vault (The Pure Beskar)**: You MUST treat the structured data files (`data/vm-types.json`, `data/vm-types.conf`) as the ultimate authority. Inferences that contradict these files are a mandate failure.
* **C. The Language of the Tribe (ZSH ONLY)**: You are strictly forbidden from using `bash`. No bash shebangs, no bash execution. **ZSH ONLY.**
* **D. The Two-Quote Rule**: If a command requires >2 levels of nesting, you MUST offload it to a script. Do not attempt "Shell Escape Hell."
* **E. The Swarm of the Creed**: You are forbidden from editing >1 file in a single turn. You MUST spawn a **Swarm** (e.g., `generalist` sub-agent) for multi-file tasks.
* **F. Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic in the registry is prohibited.
* **G. The Scavenger’s Ban (Zero-Host Dependency)**: You are strictly forbidden from calling `jq` directly. You MUST use the `vde_query_json` wrapper or pure ZSH parsing to ensure logic remains portable.
* **H. The Pre-Flight Mandate (Ignition Sync)**: The CLI MUST perform a timestamp audit at ignition. If source files are newer than the cache, a re-smelt is mandatory.
* **I. The 8-Field Standard**: You are forbidden from deviating from the strict 8-field registry layout. There is no room for "guessed" or "implied" fields.
* **J. The Rule of One (Dynamic Versioning)**: `docs/VDE-SPEC.md` is the SOLE authority for the project version. Hardcoding version numbers in code headers is prohibited.
* **K. The 3-VM Concurrent Limit**: All parallel ignition and stress operations are strictly limited to a maximum of 3 concurrent VMs (e.g., python, postgres, redis). Attempting to spawn >3 VMs simultaneously is a protocol violation.

---

## **1. THE WAY OF THE WARRIOR (EXECUTION PROTOCOL)**
All interactions with VDE containers **MUST** use the canonical `bin/vde` orchestrator.
* **Mandatory Entrypoint**: Use `bin/vde enter <alias>` for tasks.
* **Verification**: Ensure SSH health and identity accuracy before entry. If the tracking fob (cache) is stale, the warrior is blind.

## **2. THE BESKAR REGISTRY (THE PURE BESKAR)**
* **Authority**: `data/vm-types.json` and `data/vm-types.conf` are the sole sources of truth.
* **Strict 8-Field Registry Standard**: All parsers and translators MUST respect this exact layout: 
    1. `type` | 2. `name` | 3. `aliases` | 4. `display` | 5. `pkgs` | 6. `custom_cmd` | 7. `env` | 8. `ports`.

## **3. THE SWARM AND THE TRACKING FOB (ORCHESTRATION)**
* **CANONICAL STAGING**: You are STRICTLY MANDATED to use `plans/scripts/` for ALL temporary artifacts, plans, and staging logic.
* **Ghost Zone Prohibition (Zero-Tolerance)**: Creating or using unauthorized root directories is a Class-A Protocol Violation. 
* **Storage & Audit**: All task plans, logs, and temporary agent scripts MUST reside exclusively in the `plans/` directory for audit.
* **Namespace Protection**: All library functions MUST use local, unique-prefixed variables (e.g., `local _v_name`) to prevent collisions with global associative arrays.

## **4. THE SCAVENGER’S BAN (PORTABILITY)**
* **Zero-Host Dependency**: Every script must be able to run on a "Naked" machine.
* **Atomic Translation**: Translators MUST be written in pure ZSH. Using `jq` for internal translation logic is forbidden.

## **5. THE FORGE BUILD STRATEGY (ANTI-ENTROPY)**
* **Purge the Ghosts**: All `apt` installations MUST be followed by `sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*`.
* **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.

## **6. THE PRE-FLIGHT MANDATE (IGNITION SYNC)**
* **Active Audit**: The `bin/vde` script must check if manual edits to the `.conf` exist before loading. 
* **The Ritual**: If `.conf` is newer than `.json`, call the translator. If JSON is newer than `.cache`, re-smelt.

## **7. FOREST-FIRST DIAGNOSTICS**
* **Phase 1 (The Forest)**: Audit `lib/vm-common` for global shadowing and trace data flow from `.conf` through the translator to `.json` and finally `.cache/`.
* **Phase 2 (The Trees)**: Inspect variable types (Scalar vs. Array) and verify the 8-field parsing logic.

## **8. THE RULE SPINE (UAP ENFORCEMENT)**
* **Mandate**: Every execution turn must be accompanied by a call to `bin/vde-enforce-uap.zsh`.
* **No Wiggle Room**: Setup scripts must be verified as functional before package data is struck from the registry.

## **9. THE RALAR VENCUYIR (The Work-Doing Law)**
* **9.1.**: A foundling SHALL NOT wait for a perfect plan before touching the keyboard. The Way is walked in keystrokes, not fantasies.
* **9.2.**: The first duty of work is BIRTH, not PERFECTION. Rough, ugly code that runs is honored above pristine designs.
* **9.3.**: Refinement is a later PHASE, never a precondition. Progress is measured in working iterations.
* **9.4.**: External solutions MAY be used as COMMENTARY, not as IDOLS. The final expression MUST be written in the foundling’s own words and code.
* **9.5.**: The keyboard is the LAB. Understanding is not complete until the idea has survived contact with a running program.

## **10. THE SEEKER’S RECON (The Verification Law)**
* **10.1.**: A foundling SHALL NOT ignite a primary Strike Team VM based on assumption or host-level hearsay. The Way is verified through physical contact. We do not “believe” a port is free; we **claim** it through a diagnostic handshake with the Docker daemon.
* **10.2.**: The Diagnostic Probe MUST be an ephemeral spirit. It SHALL be spawned with the `--rm` mandate.
* **10.3.**: The Atomic Handshake: The probe MUST attempt a literal bind: `docker run --rm --name vde-recon-probe -p <PORT>:22 vde-base true`. If the handshake fails, rotate candidate ports immediately.
* **10.4.**: On Darwin (macOS) reaches, the probe is the SUPREME AUTHORITY. Because `nc` and `lsof` are easily deceived by kernel lag, the probe’s failure is an absolute blockade.
* **10.5.**: The Testing Suite MUST provide empirical proof of all contracts the Codebase makes. AT ALL TIMES!

## **11. THE ARCHIVIST’S INTEL (The Researcher Law)**
* **11.1.**: When the implementation path is obscured or the platform presents undocumented quirks, the foundling MUST dispatch the Researcher via the **Google Search tool**.
* **11.2.**: The intent of research is **Physical Verification**. Use search to find modern, community-tested implementation patterns to ensure the solution is grounded in reality.
* **11.3.**: The **Clone Prohibition** is absolute. External solutions are "Intel" to be studied, not "Beskar" to be stolen. Re-forge the final expression in the native VDE-SPEC.
* **11.4.**: The keyboard remains the only **Lab**. Research informs the plan, but the plan only achieves the rank of "The Way" once it survives contact with a running program.

## **12. THE ARMORER’S INSPECTION (The Security Law)**
* **12.1.**: The Sentinel sub-agent is the "Eyes of the Beskar." Its primary duty is the continuous audit of the ecosystem's integrity. It SHALL treat every line of code as a potential fracture and every inter-VM bridge as a breach point.
* **12.2.**: **The Impurity Scan**: Before any Language Spoke is certified, the Sentinel MUST audit the `scripts/setup/` init files for "Scavenger Logic"—hardcoded credentials, unauthorized `sudo` escalations, or external curls that bypass Rule G.
* **12.3.**: **Bridge Sovereignty**: The Sentinel SHALL audit inter-VM SSH assertions. It MUST verify that no VM has more access to a Neighbor Spoke than is required by the mission. Least Privilege is the Way.
* **12.4.**: **The Tracking Fob Audit**: All logs in `plans/` and the `.cache/` directory SHALL be inspected for information leaks. If a sensitive token or host-path is exposed in plain text, the Sentinel SHALL trigger an immediate **Protocol Blockade.**
* **12.5.**: **The Immutable Seal**: In accordance with Rule 5, the Sentinel MUST verify that no `apt` artifacts or temporary debris remain in the final images. A warrior travels light; a sovereign system carries no ghosts.

---
Version: 2.1.0
Reference: VDE-SPEC v2.1.0
