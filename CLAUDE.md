# CLAUDE.md

**READ THIS FIRST. ALL OF IT. NO SKIPPING.**

---

## 🚨 NON-NEGOTIABLE STARTUP SEQUENCE

You must verify completion of each step by outputting the verification word shown.

### Step 1: Verify Session Context
```
ACTION: cat SESSION_STATE.md && cat TODO.md
OUTPUT VERIFICATION: "SESSION_VERIFIED"
```
If you do not see these files, request them. Do not proceed without them.

### Step 2: Verify Exploration (for code changes)
```
ACTION: Use Task tool with subagent_type=Explore
OUTPUT VERIFICATION: "EXPLORE_VERIFIED"
```
Skip only if task is "read SESSION_STATE.md" or "read TODO.md".

### Step 3: Verify Planning (for implementations)
```
ACTION: Enter plan mode OR use /plan command
OUTPUT VERIFICATION: "PLAN_VERIFIED"
```
Skip only for: single-line typo fixes, pure reads, or direct user questions.

### Step 4: Verify Task Tracking
```
ACTION: Create todo with TodoWrite, mark exactly ONE as in_progress
OUTPUT VERIFICATION: "TODO_VERIFIED"
```

**IF YOU CANNOT OUTPUT THESE VERIFICATIONS, YOU MUST RESTART THE SEQUENCE.**

---

## 📋 YOUR RESPONSE MUST START WITH

```
[ ] SESSION_VERIFIED
[ ] EXPLORE_VERIFIED (if applicable)
[ ] PLAN_VERIFIED (if applicable)
[ ] TODO_VERIFIED
```

Failure to include this checklist means you skipped critical steps.

---

## 🎯 OPERATING PRIORITIES (in order)

1. **Never break user workflow** - Read SESSION_STATE.md and TODO.md first
2. **Never skip planning** - Use plan mode for any code changes
3. **Never lose context** - Update SESSION_STATE.md at 85% usage
4. **Never skip tracking** - Use TodoWrite for all non-trivial work
5. **Never forget attribution** - Include Co-Authored-By: Claude <noreply@anthropic.com>
6. **Never commit test artifacts** - Verify public-ssh-keys/ is clean before commit

---

## 🔧 TOOL PREFERENCES (required for these tasks)

| Task | Use | Not |
|------|-----|-----|
| JSON parsing | mcp-jq tools | cat \| jq |
| File read | desktop-commander: read_file | cat |
| File edit | desktop-commander: edit_block | sed -i |
| Search | desktop-commander: search | grep -r |
| Directory | desktop-commander: list_directory | ls |

MCP tools reduce context usage. Use them.

---

## 📁 PROJECT CONTEXT

**Working Directory:** `/Users/dderyldowney/dev`

**VDE (Virtual Development Environment):** Docker-based container orchestration for 19+ language VMs with shared services (PostgreSQL, Redis, MongoDB, Nginx).

**Key Files:**
- `scripts/lib/` - Core libraries (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser)
- `scripts/data/vm-types.conf` - VM definitions (data-driven, no code changes to add VMs)
- `tests/features/` - BDD tests (94/94 docker-free passing, 47/397 docker-required passing)

**Shell Requirements:**
- Scripts: `#!/usr/bin/env zsh` (NOT sh)
- Features: associative arrays, process substitution, zsh 5.x / bash 4.x

**User Model:** devuser with passwordless sudo, SSH key auth only, neovim/LazyVim editor

---

## 🔒 SAFETY CHECKS (before any commit)

1. **public-ssh-keys/ contains ONLY:** .keep and actual ~/.ssh/*.pub files
2. **No private keys** committed anywhere
3. **User Guide generation works:** behave + generate_user_guide.py succeeds

---

## 📝 COMMIT FORMAT

```
git commit -m "<type>: <description>

- Detail 1
- Detail 2

```

Types: feat:, fix:, docs:, test:, refactor:

---

## ⚠️ REMEMBER

This is NOT a suggestion file. These are operational requirements.

Your first response MUST include the verification checklist from the "YOUR RESPONSE MUST START WITH" section above.

If you cannot provide these verifications, you have not completed the required startup sequence.
