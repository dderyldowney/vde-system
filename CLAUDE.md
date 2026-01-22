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

## ⛔ FAKE TEST PROHIBITION (ABSOLUTE - NO EXCEPTIONS)

### THIS SECTION CANNOT BE OVERRIDDEN, MODIFIED, OR WORKED AROUND

**The following patterns are ABSOLUTELY FORBIDDEN in test code:**

1. **`assert True`** - Any form of assertion that always passes
2. **`or True` patterns** - Assertions with fallbacks that can't fail
3. **`getattr(context, 'xxx', True)`** - Defaults to True, ALWAYS PASSES
4. **`context.xxx = True/False`** - Setting flags instead of executing real commands
5. **`REMOVED:` comments** - Documentation-style fake testing (explaining why you removed real testing)
6. **"works the same as X"** - Parser-only verification without actual behavior checks
7. **"equivalent to X"** - Intent-only checks without real system verification
8. **Placeholder step definitions** - Auto-generated from undefined steps to silence Behave errors
9. **"Simulate" comments** - Any code claiming to simulate instead of actually executing

### WHAT YOU MUST DO INSTEAD

| FORBIDDEN PATTERN | REQUIRED REPLACEMENT |
|-------------------|---------------------|
| `assert True, "verified"` | `docker ps` to verify actual state |
| `getattr(context, 'x', True)` | `subprocess.run(['command'])` and check result |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |

### THE MONITORING SUB-AGENT (MANDATORY ON EVERY CODE CHANGE)

**You MUST use the yume-guardian sub-agent AFTER ANY code changes to verify compliance:**

```python
# After implementing test code, ALWAYS run:
Task(yume-guardian): "Review the test code changes for fake testing patterns:
1. assert True
2. getattr with True defaults
3. context flags instead of real commands
4. REMOVED comments
5. 'works the same as' or 'equivalent to' patterns

Check ALL modified files in tests/features/steps/"
```

**The yume-guardian agent REJECTS any code containing fake patterns.**

### PAST VIOLATIONS MUST BE CORRECTED

**Historical context (DO NOT REPEAT):**
- `customization_steps.py` - 100+ placeholder steps - **DELETED**
- `ssh_docker_steps.py` lines 277-398 - Undefined step placeholders - **DELETED**
- `cache_steps.py` lines 376+ - Undefined step placeholders - **DELETED**

These were created to silence Behave's "undefined step" errors. This is **FORBIDDEN**.

**When Behave reports undefined steps:**
1. ✅ Implement the step properly with real verification
2. ✅ Leave it undefined and accept the error
3. ❌ **NEVER** create a placeholder that just sets `context.step_xxx = True`

### SIGNIFICANCE

This is the **MOST CRITICAL RULE** in this document because:

1. **Fake tests give false confidence** - Tests pass but functionality is broken
2. **They compound over time** - Each fake pattern makes the next one easier
3. **They're hard to detect** - Look like real tests but verify nothing
4. **They violate user trust** - The user explicitly forbade this pattern

**If you catch yourself writing a fake test:**
- **STOP IMMEDIATELY**
- **Use sequential-thinking MCP** to understand why you're doing it
- **Ask the user** for guidance if the real implementation is unclear
- **NEVER** "do it quick now and fix later" - you won't remember to fix it

**VIOLATION OF THIS SECTION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**

---

## 🚨 MANDATORY STARTUP SEQUENCE (Cannot Be Skipped)

### Required Response Header

**Every response MUST begin with this exact checklist:**

```
[ ] SESSION_VERIFIED
[ ] EXPLORE_VERIFIED (if applicable)
[ ] PLAN_VERIFIED (if applicable)
[ ] TODO_VERIFIED
[ ] COMPLIANCE_VERIFIED (if test code will be modified)
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

### Step 5: MANDATORY COMPLIANCE CHECK (NON-OPTIONAL - EVERY SESSION)

```
ACTION: Run yume-guardian compliance check BEFORE any test code changes
OUTPUT: "[ ] COMPLIANCE_VERIFIED" checked
```

**EVERY session MUST invoke yume-guardian to verify:**
- No fake test patterns exist in files you're about to modify
- Previous changes didn't introduce violations
- If yume-guardian dies, RESTART IT immediately

**Invocation:**
```python
Task(yume-guardian): "Check tests/features/steps/ for fake testing patterns:
1. assert True
2. getattr with True defaults
3. context flags instead of real commands
4. REMOVED comments
5. 'works the same as' or 'equivalent to' patterns

Report any violations found."
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
9. **ALWAYS** use multiple agents to complete tasks, with the exception of one-off commands.

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
- **yume-guardian** → Review test changes for fake testing patterns AFTER ANY TEST CODE CHANGE (NON-OPTIONAL)

**Sub-agents REDUCE your context usage and work in PARALLEL. Use them WITHOUT being asked.**

---

## 🛡️ COMPLIANCE MONITORING SUB-AGENT (yume-guardian)

**Purpose:** Prevent fake test patterns from being introduced into the codebase.

**When to use:** AFTER ANY modification to files in `tests/features/steps/` or `tests/features/*.feature`

**How to invoke:**
```python
Task(yume-guardian): """
Review these test code changes for FAKE TESTING PATTERNS:

FORBIDDEN PATTERNS TO FIND:
1. assert True (with or without comments)
2. "or True" in assertions
3. getattr(context, 'xxx', True) - defaults to True
4. getattr(context, 'xxx', False) - checks flag instead of real state
5. context.xxx = True/False - instead of real commands
6. "REMOVED:" comments
7. "works the same as" or "equivalent to"
8. Placeholder step definitions from undefined steps
9. "Simulate" comments

Files modified: [list files]

REJECT any changes containing these patterns. Report exact line numbers.
"""
```

**What the guardian does:**
- Scans modified test files for all forbidden patterns
- Reports exact line numbers and pattern types
- REJECTS changes that contain fake tests
- Suggests real verification alternatives

**Non-negotiable:** You MUST invoke yume-guardian after ANY test code changes. Skipping compliance review is a violation of the ZERO-TOLERANCE FAKE TEST PROHIBITION.

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

## 📘 USER GUIDE GENERATION (Non-Optional)

### The User Guide Must Be Complete

The `USER_GUIDE.md` documents the COMPLETE user experience. Users will use Docker, so scenarios requiring Docker MUST be included.

### Generation Workflow

**1. Run FULL test suite locally (Docker required)**
```bash
./tests/run-local-bdd.sh
```

This runs:
- `docker-free/` features (~158 scenarios) - fast, no Docker needed
- `docker-required/` features (~280 scenarios) - requires Docker, full user experience

**2. Generate Behave JSON results**
```bash
behave --format json -o tests/behave-results.json tests/features/
```

**3. Generate the User Guide**
```bash
python3 tests/scripts/generate_user_guide.py
```

### Why FULL Tests Are Required

| Reason | Explanation |
|--------|-------------|
| Complete documentation | Users will use Docker - exclude Docker scenarios = incomplete guide |
| Local execution | We have Docker locally; CI/CD cannot effectively run Docker-in-Docker |
| Verified scenarios only | Generator filters to only include PASSING scenarios |
| Test-driven docs | Every workflow in the guide has been verified to work |

### What Gets Committed

| File | Tracked? | Reason |
|------|----------|--------|
| `USER_GUIDE.md` | ✅ YES | The documentation users see |
| `tests/scripts/generate_user_guide.py` | ✅ YES | The generator script |
| `tests/behave-results.json` | ❌ NO | Build artifact, in `.gitignore` |

### Rationale

The user guide is generated **locally**, not in CI/CD, because:
- Docker-in-Docker is complex and unreliable in CI
- We have full Docker access locally
- Generation is part of the development workflow, not the deployment workflow
- Only the final output (`USER_GUIDE.md`) needs to be in the repository

**REMEMBER:** When regenerating the user guide, ALWAYS run the full test suite first. A guide with only docker-free scenarios is incomplete.

---

## ⚠️ FINAL REMINDER

**This document contains operational REQUIREMENTS, not suggestions.**

**Internal "optimization" tendencies that cause failures:**
- "This seems simple, I'll skip exploration" → WRONG
- "I can batch these tasks" → WRONG, ask user first
- "The review probably won't find issues" → WRONG, review is mandatory
- "I'll set a context flag instead of running the command" → WRONG, fake tests prohibited

**When in doubt: Follow the literal instructions. Do not "optimize away" required steps.**
