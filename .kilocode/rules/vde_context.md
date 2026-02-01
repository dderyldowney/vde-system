# VDE PROJECT CONTEXT
**Working Directory:** `/Users/dderyldowney/dev` | **Project:** VDE (Virtual Development Environment) — Docker-based container orchestration for 19+ language VMs with shared services.
## Critical Architecture
- `scripts/lib/` — Core libraries (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser) | `scripts/data/vm-types.conf` — VM definitions (data-driven, single-line additions) | `tests/features/` — BDD tests
## Shell Requirements
- **ZSH ONLY** - `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **FORBIDDEN**: `/bin/sh` and `/usr/bin/env sh` are not allowed
- Features: associative arrays, process substitution, zsh 5.x
## User Model
devuser with passwordless sudo, SSH key auth only, neovim/LazyVim
