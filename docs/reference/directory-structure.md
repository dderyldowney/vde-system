# Directory Structure
<!-- @shared-law (Sovereign Law) -->

The complete directory layout of the **Sovereign Baseline (1.5.6)** installation.

[← Back to README](../../README.md)

---

## Root Structure

```
VDE_ROOT/
├── .agents/            # Antigravity native skills (symlinks to .gemini/SKILLS and .gemini/COMMANDS)
│   └── skills/         # One folder per skill or /vde-* command, each holding a SKILL.md symlink
├── .cache/             # Persistent associative array caches and port registry
├── .docker-state/      # Real-time container state archives for status tracking
├── .gemini/            # Agent instructions, commands, and strike plans
│   ├── COMMANDS/
│   ├── PLANS/
│   ├── RULES/
│   ├── SKILLS/
│   ├── STATE/
│   │   ├── MEMORY.md           # Sovereign session record and mission history
│   │   └── session_handover.md # Current session goals and constraints
│   └── instructions.md
├── .gemini_security/   # Security remediation plans and vulnerability audits
├── .git/               # The Chronicler's archive (Git repository)
├── .locks/             # FIFO ticket-based concurrency locks (global and per-VM)
├── backup/             # Automated backups of SSH keys and system states
├── bin/                # Unified CLI orchestrator and binary rituals
├── conductor/          # Strike orchestration and mass tagger logic
├── configs/            # Docker Compose and service-specific configurations
├── data/               # Beskar Registry (vm-types) and service persistence
├── docs/               # The Gospel of the Forge (Sovereign Artifact Set)
├── env-files/          # Per-Spoke environment variables and DNS aliases
├── githooks/           # Pre-strike sentinels and lifecycle gates
├── lib/                # Standard Library (stdlib) Zsh modules
├── logs/               # Per-Spoke application logs and audit trails
├── plans/              # Implementation plans, task logs, and staging artifacts
├── projects/           # Foundling workspace (Source code mounts for language VMs)
├── public-ssh-keys/    # SSH public keys for authorized container injection
├── scripts/            # Hydration rituals (setup) and Spoke ignition logic
├── templates/          # Blueprints including forge-mythos rituals
├── tests/              # BDD Feature specifications and empirical proofs
└── README.md           # Entry point and high-level mission overview
```

---

## Key Directories Explained

### `.agents/`
A hidden folder that holds only `skills/`. Each `.agents/skills/<name>/SKILL.md` is a relative symlink to a skill document in `.gemini/SKILLS/` or a command document in `.gemini/COMMANDS/`, so Antigravity discovers them natively as skills and `/vde-*` slash commands. There are 19 such symlinks.

Other local files under `.agents/` stay git-ignored. Every other agent reads the same documents by their `.gemini/` path.

### `.gemini/`
Agent instructions, commands, rules, skills, and strike plans. Every agent (Claude, Gemini, Kilo and others) reads project state from `.gemini/STATE/` at session start:

- `.gemini/STATE/MEMORY.md`: Sovereign session record and mission history.
- `.gemini/STATE/session_handover.md`: Current session goals and constraints.

Only the tool-mandated entry points (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `kilo.json`) and the certified status record `PROJECT_STATUS.md` stay at the repository root.

### `.locks/`
VDE uses a deterministic FIFO locking model to manage concurrency.
- `global-config.lock`: Serializes modifications to the Beskar Registry.
- `vms/`: Per-Spoke locks for parallel builds and mass ignitions.
- `ports/`: Atomic reservations for SSH and service ports.

### `.docker-state/`
Contains JSON archives reflecting the real-time status of VDE containers. This directory ensures that `vde status` and `vde vision` remain accurate without polling the Docker daemon excessively.

### `bin/`
The unified command surface. **Mandate 10** requires all operations to flow through `bin/vde`.
- `vde`: The canonical command router (The Way).
- `vde-enforce-uap.zsh`: The Rule Spine sentinel (Governance).
- `vde-init`: The Initialization Ritual logic.
- `vde-path-of-the-foundling`: Interactive student onboarding.

### `lib/` (Standard Library)
Modular Zsh 5.0+ libraries following the **ZSH ONLY** mandate.
- `vm-common`: High-level Spoke orchestration.
- `vde-core`: Pathing, versioning, and deterministic execution.
- `vde-ssh`: The Sovereign Bridge (SSH management).
- `vde-docker`: Container lifecycle management.

### `projects/` (The Projects Base)
The primary workspace for language Spokes. By default the Projects base is
`projects/` under the repository root, but it is **configurable** via the
`VDE_PROJECTS_DIR` environment / `.env` key to any directory the student controls,
inside or outside the repo (e.g. `$HOME/Projects`).

Each Spoke alias gets its own subfolder in the `<base>/<alias>` layout, which is
mounted into the corresponding container at `/home/devuser/workspace`. Re-point the
base at any time with `vde set-projects-dir`, or set it during `vde init --projects-dir <path>`.

The Projects base is **preserved by `vde nuke`** — it is never deleted, in-tree or
external (nuke offers to move it to a safe location first).

### `data/`
Persistent storage for service Spokes (e.g., PostgreSQL databases, Redis dumps) and
the authoritative **Beskar Registry** (`vm-types.json`). Like the Projects base, the
database `data/` directory is **preserved by `vde nuke`** and never deleted.

### `env-files/`
Configuration payloads sourced by Docker Compose. These files contain the **Phase 31 DNS aliases** and Spoke-specific metadata.

---

[← Back to README](../../README.md)
