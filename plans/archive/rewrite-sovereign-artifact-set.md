# Implementation Plan: Sovereign Artifact Set Rewrite (1.3.0)

## Objective
To strictly enforce the Sovereign Artifact Set Mandate by completely rewriting `docs/VDE-SPEC.md`, `docs/ARCHITECTURE.md`, and `docs/Technical-Deep-Dive.md` from scratch. This ensures no vestiges of outdated documentation remain and that the documentation deeply and accurately represents the physical reality of the 1.3.0 codebase.

## Scope & Impact
1.  **`docs/VDE-SPEC.md` (The Absolute Authority)**: Will be rewritten to explicitly detail the verified Universal Agent Protocol (UAP) rules, the 8-Field Registry Standard (`type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`), the Directory Structure, and the Sovereign Artifact Set Mandate itself.
2.  **`docs/ARCHITECTURE.md` (The High-Level Design)**: Will be rewritten to accurately describe the Hub-and-Spoke Tiered Model, the Ignition Pipeline (Smelting Ritual), the FIFO Lock-Queue Model, Port Stewardship, the Deterministic Error Engine, and the Sovereign Bridge (SSH Agent Forwarding via `socat`).
3.  **`docs/Technical-Deep-Dive.md` (The Low-Level Mechanics)**: Will be rewritten to provide precise technical details found in the audit:
    - **UAP Enforcement**: Explicitly listing the checks for `#!/usr/bin/env zsh`, forbidden `sleep` calls, Bash-isms (`[ `), 0-indexed arrays (`[0]`), and the "Fake ZSH" parameter expansion check (`\${(`).
    - **FIFO Locking**: Detailing the ticket generation (`${EPOCHREALTIME}-$$`), the atomic `mkdir` gate, and the ZSH-native jitter calculation `0.1 + (RANDOM / 32768.0 * 0.4)`.
    - **Port Stewardship**: Detailing the `vde-port-probe-${port}` container handshake and `STALE_HOST` marking.
    - **Sovereign Bridge**: Detailing the Docker socket GID mapping and the `socat` UNIX-listen proxy for the SSH auth socket.

## Implementation Steps
1. Use the `write_file` tool to overwrite `docs/VDE-SPEC.md` with the new, deeply accurate content.
2. Use the `write_file` tool to overwrite `docs/ARCHITECTURE.md` with the new, deeply accurate content.
3. Use the `write_file` tool to overwrite `docs/Technical-Deep-Dive.md` with the new, deeply accurate content.
4. Verify `RELEASE_NOTES.md` accurately points to the current baseline.

## Verification & Testing
Execute `bin/vde-sync-version` to ensure the new artifacts are perfectly synchronized and that the baseline is formally certified.