# Remediation Plan: VDE 1.5.1 Pre-Production Certification
# @forge (Remediation Plan)

## 1. Fracture Analysis (The Sovereign Reason)
The Controlled Matrix Audit revealed systemic failures in Spoke ignition, auto-rebuilding, and cluster management. These fractures prevent the "Naked machine" portability promised by the Sovereign Baseline.

### Showstoppers:
1. **S01: Auto-Rebuild Logic Failure**: `bin/vde` incorrectly passes VM categories (e.g., "language") to `vde-rebuild`, causing all missing image auto-builds to fail.
2. **S02: Cluster Resolution Inconsistency**: `bin/vde` uses raw names for `jq` queries while the registry uses normalized names, causing cluster lookups (e.g., `lamp`, `mean`) to crash.
3. **S03: Matrix Incompleteness**: 70% of Spoke images are missing from the Hub, and the system fails to auto-recover due to S01.
4. **S04: Broken Stack Definitions**: `lamp` and `mean` are incorrectly identified as clusters or missing their unit definitions.

## 2. The Reforging (Implementation Plan)

### Step 1: Fix `bin/vde` Orchestrator (Orchestrator Hardening)
- [ ] Correct the `vde start` logic to pass `${BASE_NAME}` or `${CANONICAL_NAME}` to `vde-rebuild`.
- [ ] Align cluster expansion logic to use `${name}` from `vde_cluster_exists` for the `jq` path.

### Step 2: Re-Smelt the Pure Beskar (Registry Parity)
- [ ] Execute `bin/vde-rebuild-cache` to ensure `.json` and `.conf` are perfectly synced.
- [ ] Verify `vm-types.json` schema compliance.

### Step 3: Mass Matrix Re-forging (The Great Rebuild)
- [ ] Execute `bin/vde-matrix-rebuild.zsh` to build all 32 Spoke images.
- [ ] This must be done sequentially to avoid resource exhaustion.

### Step 4: Final Certification (The Gauntlet)
- [ ] Re-run the Controlled Matrix Audit (`plans/scripts/controlled-matrix-audit.zsh`).
- [ ] Goal: 100% PASS across all 32 Spokes.

## 3. The Beskar Set (Affected Files)
- `bin/vde`
- `data/vm-types.json`
- `lib/vde-cluster-utils`
- `bin/vde-matrix-rebuild.zsh`

---
*Mandalorian Creed: This is the Way.*
