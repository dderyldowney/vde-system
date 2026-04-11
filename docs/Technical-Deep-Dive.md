# VDE: Technical Deep-Dive (v1.2.3 Sovereign)

## 1. The Rule Spine (UAP Enforcement)

The core of VDE is supervised by `bin/vde-enforce-uap.zsh`. This script audits the workspace for compliance with the **Resol’nare** (Supreme Prohibitions).

### Compliance Checks:
- **ZSH-Native Flags**: Detects "Fake ZSH" by searching for `${(` parameter expansion patterns in scripts >30 lines.
- **Shebang Purity**: Ensures `#!/usr/bin/env zsh` is universal.
- **Ghost Detection**: Verifies that `apt` artifacts and temporary debris are purged.

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE uses a reactive synchronization mechanism to ensure the runtime environment matches the configuration source.

1.  **Manual Strike**: User edits `data/vm-types.conf`.
2.  **The Translator**: Pure ZSH parsing (Rule G) hammers `.conf` into the atomic 8-field `.json` registry.
3.  **The Smelt**: If `.json` is newer than `.cache`, the system re-smelts the tracking fob for O(1) runtime lookup.
4.  **Ignition**: The `bin/vde` orchestrator verifies the cache before spawning any VM.

## 3. Concurrency & Atomic Stewardship

VDE manages high-concurrency operations through a **Lock-Queue Model** (Phase 25).

### Atomic File Locking (`lib/vm-lock`)
Uses kernel-level `mkdir` atomicity to manage:
- **VM Locking**: `.locks/vms/<name>.lock` prevents race conditions during builds.
- **Global Mutex**: `.locks/global-config.lock` protects the Beskar Registry.
- **Heartbeat Proof**: Locks record `PID:PGID:TIMESTAMP` to allow deterministic recovery from hung processes.

### Port Registry (`.cache/port-registry/`)
Uses `<port>.lock` files to reserve SSH and service ports before assignment, preventing double-allocation in parallel ignitions.

## 4. Universal Script Parity (USP)

Hydration logic is decoupled from Docker build-args. Every VM type has a corresponding ritual in `scripts/setup/`.

- **Build Context**: The entire VDE root is the build context.
- **Hydration**: The `vde-base` Dockerfile triggers the setup script: `zsh /vde/scripts/setup/<name>-init.zsh`.
- **Hygiene**: Scripts MUST end with `apt-get clean && rm -rf /var/lib/apt/lists/*`.

## 5. Cognitive Sovereignty (Section 13)

VDE operations follow the **Mandalorian Sequence**:
1.  **Kov'nyn (Think First)**: Strategic hypothesis and reasoning budget expenditure.
2.  **Recon (Scout Deployment)**: Factual "Raw Ore" gathering via research tools.
3.  **Forge Integration**: Internalizing facts into the strategy.
4.  **Synthesis (Strike the Beskar)**: Minimal implementation derived from first principles.
5.  **Ret'lini (Self-Critique)**: Validation against the Rule Spine.

## 6. Security & Privacy Model

- **Identity Isolation**: The `vde_student` key is isolated to `~/.ssh/vde/`.
- **Input Sanitization**: All user-supplied names are struck through `vde_normalize_name` (alphanumeric + dash whitelist) before touching the FS or `eval` sinks.
- **Container Sovereignty**: The `vde-net` provides bridge isolation. The Docker socket is bridged via secure group-id alignment in `vde-entrypoint.zsh`.

---
Version: 1.2.3
Status: Hardened
