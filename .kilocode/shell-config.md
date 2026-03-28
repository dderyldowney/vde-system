# Shell Configuration

## Required Knowledge for All AI Agents & CLIs
> **SCOPE: MAIN AGENT ONLY.** Sub-agents spawned by the main agent must NOT execute startup steps. They inherit context from the main agent and must begin their assigned task immediately.

> **Idempotent loading:** Before each step, check whether the content is already present in the current context. If it is, skip that step — never reload information already loaded this session.

**Upon session start, the main agent MUST read (skip any already in context):**

| Document | Purpose |
|----------|---------|
| [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) | Canonical VDE architecture breakdown - Control Center, Configuration Center, VM Architecture, Execution Flow |
| `.kilocode/rules/vde_context.md` | VDE project context and working directory |
| `.claude/memory/feedback_context7_language_refresh.md` | Context7 MCP refresh requirements for all implementation languages and tools |

These documents define the authoritative architecture and are required reading before any task execution.

---

## Context7 Language & Tool Refresh (MANDATORY — MAIN AGENT ONLY, ONCE PER SESSION)

At session start, refresh docs for all VDE implementation languages/tools via context7 MCP. Run all calls in parallel. Skip if already loaded in the current context:

1. `Python` — subprocess, pathlib, json, os, sys, re, unittest, pytest
2. `behave` — step defs, hooks, fixtures, context patterns
3. `PyYAML` — safe_load, safe_dump, multi-doc streams
4. `Docker` — containers, images, networking, volumes, exec
5. `docker-compose` — services, networks, volumes, build, healthcheck
6. `Zsh` — associative arrays, process substitution, parameter expansion
7. `SSH` — config, key auth, port forwarding, ssh_config directives

Full details: `.claude/memory/feedback_context7_language_refresh.md`

---

## Shell Paths for VDE Project

This project uses **zsh exclusively**. `/bin/sh` and `/usr/bin/env sh` are forbidden.

| Shell | Path | Version Notes |
|-------|------|---------------|
| zsh | `/bin/zsh` | Use this path explicitly when running zsh scripts |
| bash | `/usr/local/bin/bash` | NOT SUPPORTED - zsh only |

## Shell Version Requirements

- **zsh**: Version 5.0 or later required (5.x recommended).
- **bash**: NOT SUPPORTED - this is a zsh-only project.

## Script Shebangs

**All scripts MUST use zsh:**

- For zsh scripts: `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **FORBIDDEN**: `#!/bin/sh`, `#!/usr/bin/env sh`, `#!/bin/bash`

## Project Standards

See [STYLE_GUIDE.md](../../STYLE_GUIDE.md) for complete coding standards including:
- Zsh-only requirement (Section: Shell Scripting Standards)
- Shell prohibition policy
- Code review requirements

## Running Tests

```bash
# For zsh unit tests
/bin/zsh tests/unit/vde-shell-compat.test.sh

# Verify zsh shebang compliance
zsh ./bin/check-zsh-shebang.zsh
```
