# VDE PROJECT CONTEXT
**Working Directory:** `~/dev` | **Project:** VDE (Virtual Development Environment) — Docker-based container orchestration for 19+ language VMs with shared services.

## Session Startup (MANDATORY)
**Read `MEMORY.md` at session start** - before any other work. This is the single source of truth for project state, test status, and active work.

## Critical Architecture
- `lib/` — Core libraries (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser) | `data/vm-types.conf` — VM definitions (data-driven, single-line additions) | `tests/features/` — BDD tests

## Shell Requirements
- **ZSH ONLY** - `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **FORBIDDEN**: `/bin/sh` and `/usr/bin/env sh` are not allowed
- Features: associative arrays, process substitution, zsh 5.x

## User Model
devuser with passwordless sudo, SSH key auth only, neovim/LazyVim
