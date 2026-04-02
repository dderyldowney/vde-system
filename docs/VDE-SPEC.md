# VDE Technical Specification (Condensed)

**Document Type:** Authoritative Technical Specification
**Version:** 1.7.2
**Status:** ACTIVE
**Last Updated:** 2026-04-02T11:00:00Z

## 1. Core Mandates
- **ZSH-ONLY**: All scripts (`bin/`) and libraries (`lib/`) MUST use `#!/usr/bin/env zsh`.
- **UAP Compliance**: All agent actions must follow the Universal Agent Protocol (Startup → Plan → Implementation → Audit → Review → Finalization).
- **TDD Requirement**: Failing tests MUST be written before implementation. No fake tests (`assert True`).
- **Enforcer Supervision**: All file edits and shell commands MUST run under `bin/vde-enforce-uap.zsh`.

## 2. Directory Structure (Summary)
- `bin/`: CLI entry points (`vde`, `list-vms`, `create-virtual-for`, etc.)
- `lib/`: Sourced ZSH libraries (naming, security, constants, etc.)
- `configs/docker/`: Per-VM Docker Compose configurations.
- `data/`: VM type definitions and authoritative port registry.
- `templates/`: Compose and SSH config templates.
- `projects/`: User workspace mounted to containers.

## 3. SSH Architecture
- All VDE SSH assets are isolated in `~/.ssh/vde/`.
- Private/Public key pair: `id_ed25519` / `id_ed25519.pub`.
- Authoritative config: `~/.ssh/vde/config`.

## 4. Universal Agent Protocol (UAP)
1. **Startup**: Complete 8-step checklist (Read @MEMORY.md, @session_handover.md, etc.).
2. **Planning**: Design TDD strategy with explicit failing tests.
3. **Implementation**: Main Agent as orchestrator; Swarms for >1 file edits.
4. **Audit**: Automated verification via Enforcer.
5. **Review**: Dual approval (Agent + User).
6. **Finalization**: Final test run and handover update.

*End of Condensed Specification*
