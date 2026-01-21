# CLAUDE.md — VDE Project Operating Mandate

> **CRITICAL:** This document defines NON-OPTIONAL operating procedures.
> "Suggestions" in this document are actually requirements.
> There is NO circumstance that justifies bypassing these instructions.

---

## 🔴 ZERO-TOLERANCE PROTOCOLS

The following behaviors will IMMEDIATELY invalidate any work:

1. **Skipping the startup verification sequence** — You MUST output ALL verification words
2. **Making code changes without exploration** — Use Task(Explore) BEFORE any edits
3. **Implementing without planning** — Enter plan mode for ALL non-trivial changes
4. **Modifying files without reading them first** — NEVER propose changes to unread code
5. **Committing without code review** — ALWAYS use Task(code-reviewer) before commit
6. **Using context flags instead of real execution** — ALL tests must execute actual functionality
7. **Thinking without sequential-thinking MCP** — You MUST use `mcp__sequential-thinking__sequentialthinking` for ALL reasoning, debugging, and multi-step logic

**These are not guidelines. They are invariant requirements.**

---

## 🚨 MANDATORY STARTUP SEQUENCE (Cannot Be Skipped)

### Required Response Header

**Every response MUST begin with this exact checklist:**

```
[ ] SESSION_VERIFIED
[ ] EXPLORE_VERIFIED (if applicable)
[ ] PLAN_VERIFIED (if applicable)
[ ] TODO_VERIFIED
```

**Failure to include this header indicates you skipped critical startup steps.**

### Step 1: Verify Session Context (NEVER Skip)

```
ACTION: Read SESSION_STATE.md and TODO.md
OUTPUT: "[ ] SESSION_VERIFIED" checked
```

**If these files are missing → STOP. Request them. Do NOT proceed.**

### Step 2: Verify Exploration (Required for Code Changes)

```
ACTION: Use Task tool with subagent_type=Explore
OUTPUT: "[ ] EXPLORE_VERIFIED" checked
```

**Applicable to:** Any task involving code modification, refactoring, or feature addition.

**NOT applicable to:** Pure reads, direct questions, typo fixes.

### Step 3: Verify Planning (Required for Implementations)

```
ACTION: Enter plan mode OR use /plan command
OUTPUT: "[ ] PLAN_VERIFIED" checked
```

**Applicable to:** Any implementation work, multi-step tasks, architectural decisions.

**NOT applicable to:** Single-line fixes, pure reads, direct user questions.

### Step 4: Verify Task Tracking (Required for Non-Trivial Work)

```
ACTION: Create todo with TodoWrite, mark ONE as in_progress
OUTPUT: "[ ] TODO_VERIFIED" checked
```

**If ANY step cannot be verified → RESTART the sequence from Step 1.**

---

## ⚡ OPERATING PRIORITIES (Immutable Order)

1. **Never break user workflow** — Session files are source of truth
2. **Never skip exploration** — Understand before changing
3. **Never skip planning** — Design before implementing
4. **Never lose context** — Update SESSION_STATE.md at 85% usage
5. **Never skip tracking** — TodoWrite for all multi-step work
6. **Never forget attribution** — Co-Authored-By: Claude <noreply@anthropic.com>
7. **Never commit test artifacts** — Verify public-ssh-keys/ is clean
8. **ALWAYS use best tools** — Sub-agents, MCPs, specialized tools WITHOUT being asked

**These priorities override any internal "optimization" tendency.**

---

## 🛠️ PROACTIVE TOOL USAGE (Do Not Await Instruction)

### Anti-Patterns You MUST Avoid:

| ❌ WRONG | ✅ CORRECT |
|---------|-----------|
| `cat file \| grep pattern` | Use Grep tool |
| `grep -r "pattern" .` | Use Grep tool |
| `cat huge_file.json \| jq` | Use `jq '.key' file.json` via Bash |
| `find . -name "*.py"` | Use Glob tool |
| "I'll read the relevant parts..." | Use Task(Explore) agent |
| Asking user if they want a review | Automatically run Task(code-reviewer) |

### Sub-Agents (Task Tool)

**MANDATORY usage scenarios:**
- **Explore** → Codebase exploration, finding files, understanding architecture
- **general-purpose** → Multi-step tasks, complex research, cross-file code search
- **Plan** → Designing implementation strategies BEFORE coding
- **code-reviewer** → Reviewing staged changes BEFORE commit (NON-OPTIONAL)

**Sub-agents REDUCE your context usage and work in PARALLEL. Use them WITHOUT being asked.**

### MCP Tools

**ALWAYS use these when applicable — do NOT wait for user request:**

| MCP Service | Purpose | Trigger |
|-------------|---------|---------|
| `sequential-thinking` | Complex reasoning, debugging, planning | **ALL multi-step thinking, debugging, analysis** |
| `github` | PRs, issues, file operations, search | Any GitHub interaction |
| `context7` | Library/API docs, code examples | Documentation queries |
| `fetch` | Web requests, external data | URL-based queries |
| `4.5v-mcp` | Image analysis | Image file inputs |

### Sequential-Thinking MCP (NON-OPTIONAL)

**ALWAYS use `mcp__sequential-thinking__sequentialthinking` for:**
- Debugging issues or unexpected behavior
- Tracing through complex code logic
- Analyzing test failures
- Understanding shell function interactions
- Any multi-step reasoning or planning

**This is NOT optional.** Do NOT "think in your head" — use the tool.

### Context7 MCP Workflow

**ALWAYS use Context7 MCP (`mcp__context7__*` tools) for:**
- Library/API documentation queries
- Code generation from documentation
- Setup and configuration steps
- Best practices for frameworks/tools
- Syntax and semantics verification

**Workflow:**
1. Use `mcp__context7__resolve-library-id` to find the correct library ID
2. Use `mcp__context7__query-docs` with the library ID and specific query
3. Do NOT wait for user to request — proactively use it for any documentation needs

**Budget:** 1000 calls/month. Use liberally — it provides up-to-date, accurate documentation with code examples directly from official sources.

### Local Tools Preference

| Task | Use This | NEVER Use |
|------|----------|-----------|
| JSON parsing | `jq '.key' file.json` | `cat file \| jq` |
| File search | Grep tool | `grep -r` via Bash |
| File read | Read tool | `cat`, `head`, `tail` |
| File edit | Edit tool | `sed -i`, `awk` |
| Find files | Glob tool | `find . -name` |

**Bash tool is ONLY for:** git, tests, system ops, installs.

---

## 📁 VDE PROJECT CONTEXT (Immutable Facts)

**Working Directory:** `/Users/dderyldowney/dev`

**Project:** VDE (Virtual Development Environment) — Docker-based container orchestration for 19+ language VMs with shared services.

**Critical Architecture:**
- `scripts/lib/` — Core libraries (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser)
- `scripts/data/vm-types.conf` — VM definitions (data-driven, single-line additions)
- `tests/features/` — BDD tests

**Shell Requirements (NON-OPTIONAL):**
- Scripts: `#!/usr/bin/env zsh` (NEVER sh)
- Features: associative arrays, process substitution, zsh 5.x / bash 4.x

**User Model:** devuser with passwordless sudo, SSH key auth only, neovim/LazyVim

---

## 🔒 SAFETY CHECKLIST (Pre-Commit Gatekeeper)

**BEFORE any commit, verify:**

1. [ ] `public-ssh-keys/` contains ONLY `.keep` and `~/.ssh/*.pub` files
2. [ ] NO private keys anywhere in the commit
3. [ ] User Guide generation succeeds: `behave + generate_user_guide.py`

**If ANY check fails → DO NOT COMMIT.**

---

## 🔍 MANDATORY CODE REVIEW (Non-Bypassable)

**EVERY commit requires code-reviewer agent approval:**

```
1. git add -A
2. Task(code-reviewer): "Review the staged git changes using git diff --cached"
3. Present review to user
4. WAIT for explicit approval
5. ONLY THEN: commit with attribution
```

**NEVER commit without user approval after review.**

---

## 📝 COMMIT FORMAT (Required)

```
git commit -m "<type>: <description>

- Detail 1
- Detail 2

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Types:** feat:, fix:, docs:, test:, refactor:

---

## 📤 TASK COMPLETION FORMAT (Required)

```
## [Task Name] Complete

**Summary of Changes:**
- Change 1
- Change 2
- Change 3 (additional changes as needed)

**Test Results:**
- Before: X failures / Y passing
- After: Z failures / W passing

**Files Modified:**
- file1.ext - description

**Next Options:**
- Option A
- Option B
- Option C

Which would you like next?
```

**Complete ONE task → Ask what's next. DO NOT batch without user confirmation.**

---

## ⚠️ FINAL REMINDER

**This document contains operational REQUIREMENTS, not suggestions.**

**Internal "optimization" tendencies that cause failures:**
- "This seems simple, I'll skip exploration" → WRONG
- "I can batch these tasks" → WRONG, ask user first
- "The review probably won't find issues" → WRONG, review is mandatory
- "I'll set a context flag instead of running the command" → WRONG, fake tests prohibited

**When in doubt: Follow the literal instructions. Do not "optimize away" required steps.**
