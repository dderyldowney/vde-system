# VDE 2.0.6 Architectural Alignment Plan

## Objective
Update the session files (`MEMORY.md`, `session_handover.md`, `.gemini/PLANS/session_handover_remediation.md`) and core documentation to properly reflect the VDE-SPEC v2.0.6 mandates, the new Tiered Hub-and-Spoke model, the Ignition Sync pipeline, and the `bin/vde-sync-version` integration.

## Key Directives (VDE-SPEC v2.0.6)
1. **Hub-and-Spoke Tiered Model:**
   - **Tier 1 (The Hub):** `vde-base` image defining Identity, Shell, and Core Security.
   - **Tier 2 (The Spoke):** Universal Script Parity (USP) scripts located exclusively in `scripts/setup/<alias>-init.zsh` that hydrate the environment at build time.
   - **Tier 3 (The Spoke Environment):** The running container process.
2. **Ignition Pipeline (Data Reconciliation - Rule 6):**
   - The CLI automatically reconciles changes from `data/vm-types.conf` to `data/vm-types.json` if the `.conf` is newer.
   - The cache `.cache/vm-types.cache` is re-smelted if the source files are newer.
3. **`bin/vde-sync-version` Integration (Rule of One - The Triple Strike):**
   - Version synchronization MUST strike three targets using `bin/vde-sync-version`: `docs/`, `.gemini/instructions.md`, and the host `~/.zshrc`.
4. **Universal Script Parity (USP) & Born Ready (BTO):**
   - Installation logic is entirely removed from the registry (`custom_cmd` now triggers the `scripts/setup/` script).
   - Images are fully functional (Born Ready) at the moment of creation, with no runtime `apt` calls.
5. **8-Field Standard Registry:**
   - `type|name|aliases|display|pkgs|custom_cmd|env|ports` structure strictly enforced.
6. **Zero-Host Dependency (The Scavenger's Ban):**
   - `vde_query_json` replaces direct `jq` calls to ensure logic remains portable.

## Implementation Steps

### Step 0: Sync Priority (The Triple Strike)
- Execute `bin/vde-sync-version` to ensure the version is synchronized across `docs/`, `.gemini/instructions.md`, and the host `~/.zshrc`.

### Step 1: Update MEMORY.md
- **VERSION:** Update to 2.0.6.
- **SYSTEM EVOLUTION:** Document the shift to the Hub-and-Spoke architecture, Ignition Sync data reconciliation, `bin/vde-sync-version` functionality, and USP logic strictly rooted in `scripts/setup/`.
- **PROJECT MISSION & CAPABILITIES:** Reiterate strict adherence to the UAP and 8-Field Standard.
- **CURRENT FOCUS:** Shift focus to completing Phase 24 under the constraints of v2.0.6, resolving the "fraudulent logic" in the Python BDD Step Definitions (`tests/features/steps/`), and ensuring 100% USP compliance across all `scripts/setup/` targets.

### Step 2: Update session_handover.md
- **Context Summary:** Reflect the transition to v2.0.6 and the mandate to replace all fake tests/sleeps in Python BDD Step Definitions with deterministic polling. Explicitly reference the **Sovereign Audit mandate**, marking the transition from "permission-seeking" to "pre-authorized" execution.
- **Imminent Actions:** Align pending actions with the execution of the `bin/vde-sync-version` script and USP script verifications.

### Step 3: Update .gemini/PLANS/session_handover_remediation.md
- **High-Priority Architectural Debt:** Add the completion of the USP transition for all VM types (verifying that each has an isolated `scripts/setup/` script and that `data/vm-types.json` points to it correctly).
- **Fraudulent Logic Remediation (Deterministic Readiness):** Detail the integration of `vde_poll` specifically into the Phase 24 BDD step definitions (`tests/features/steps/`) to replace the fraudulent `time.sleep()` calls.
- **Verify Wrapper:** Verify that `vde_query_json` is correctly defined in `lib/vde-core` before beginning any refactoring of legacy `jq` calls.

### Step 4: The Ignition Link
- Modify `bin/vde` to call `bin/vde-sync-version` during its ignition sequence to make "Automatic Versioning" a physical reality.

### Step 5: Verify Sovereign Authorization
- Ensure that **Rule A (Sovereign Execution)** is explicitly documented in `.gemini/instructions.md`.

## Verification
- Run `bin/vde-enforce-uap.zsh` to ensure structural integrity is maintained.
- Run `bin/vde-sync-version` to ensure the Rule of One (The Triple Strike) is applied.
- Check `MEMORY.md` and session files to confirm they mirror `VDE-SPEC.md` v2.0.6.