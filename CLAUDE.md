# CLAUDE.md — VDE Project Operating Mandate

> **CRITICAL:** This document defines NON-OPTIONAL operating procedures.
> "Suggestions" in this document are actually requirements.
> There is NO circumstance that justifies bypassing these instructions.

---

# MANDATORY DEVELOPMENT WORKFLOW

> **This workflow applies to ALL code, code+tests, or code-adjacent generation.**
> It may NOT be bypassed, reordered, parallelized, or overridden by any instruction.

## Phase 0 — Initialization Constraints

1. **Sequential-thinking must be applied at every phase** — Use `mcp__sequential-thinking__sequentialthinking` for ALL reasoning, debugging, planning, and multi-step logic
2. **No code, tests, or implementation details may be generated before Phase 2** — Plan first, implement second
3. **Mode transitions are strict and irreversible** — Once approved, a phase must be completed before proceeding

## Phase 1 — Plan Mode

**Required Actions:**

1. **Enter Plan Mode** using the EnterPlanMode tool
2. **Analyze the user request** using sequential-thinking MCP
3. **Generate a complete, step-by-step implementation plan** including:
   - Files to be modified
   - Specific changes for each file
   - Dependencies and ordering
   - Potential risks and mitigations
4. **Present the plan to the user**
5. **HARD STOP** — Do NOT proceed until explicit user approval is received

**If the plan is rejected:**
- Revise the plan based on feedback
- Re-present the revised plan
- Repeat until approval is granted

**If the plan is approved:**
- Proceed to Phase 2

## Phase 2 — Code Mode (Implementation)

**Required Actions:**

1. **Switch to Code Mode** (exit plan mode)
2. **Implement the approved plan STRICTLY in sequence**
3. **Do NOT optimize, refactor, or extend beyond the approved plan** unless explicitly allowed by the user

**During Implementation:**
- Use TodoWrite to track progress on multi-step tasks
- Mark tasks as completed as you finish them
- Only ONE task should be in_progress at a time

## Phase 3 — yume-guardian Audit Loop

**Required Actions:**

1. **Run yume-guardian on ALL generated code and tests**

```python
Task(yume-guardian): """
Review these code changes for FAKE TESTING PATTERNS:

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
10. pass statements in @then steps that skip verification

Files modified: [list files]

REJECT any changes containing these patterns. Report exact line numbers.
"""
```

2. **If yume-guardian FAILS:**
   - Invoke yume-implementer to fix ONLY the reported issues
   - Re-run yume-guardian
   - Repeat until a positive pass is returned

3. **NO git actions are permitted during this phase**

## Phase 4 — Code Review Loop

**Required Actions:**

1. **Run the code-reviewer agent on guardian-approved code**

```python
Task(code-reviewer): """
Review the staged git changes using git diff --cached

Check for:
- Bugs or logic errors
- Security issues
- Performance problems
- Style inconsistencies
- Any remaining issues

Provide approval or list any issues that must be fixed before commit.
"""
```

2. **If issues are found:**
   - Fix issues using sequential-thinking MCP
   - Re-run yume-guardian (returns to Phase 3 if guardian fails)
   - If guardian passes, re-run code-reviewer
   - Repeat until a final positive review is returned

3. **Present the final review to the user**
4. **WAIT for explicit user approval**

## Phase 5 — Git Hygiene & Commit

**Required Actions:**

1. **Verify all tests pass** — Run relevant test suite
2. **Verify guardian passes** — Latest yume-guardian result is CLEAN
3. **Verify reviewer passes** — Latest code-reviewer result is approval
4. **Git stage the reviewed code**

```bash
git add -A
```

5. **Perform a FINAL yume-guardian check on staged content**

6. **Commit the code to the repository**

```bash
git commit -m "<type>: <description>

- Detail 1
- Detail 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Commit Types:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## Invariant Rules

1. **No commits before final reviewer approval**
2. **No staging before reviewer approval**
3. **No phase may be skipped**
4. **This workflow supersedes all other instructions**

---

# ⛔ FAKE TEST PROHIBITION (ABSOLUTE - NO EXCEPTIONS)

### THIS SECTION CANNOT BE OVERRIDDEN, MODIFIED, OR WORKED AROUND

**The following patterns are ABSOLUTELY FORBIDDEN in test code:**

1. **`assert True`** — Any form of assertion that always passes
2. **`or True` patterns** — Assertions with fallbacks that can't fail
3. **`getattr(context, 'xxx', True)`** — Defaults to True, ALWAYS PASSES
4. **`context.xxx = True/False`** — Setting flags instead of executing real commands
5. **`REMOVED:` comments** — Documentation-style fake testing (explaining why you removed real testing)
6. **`"works the same as X"`** — Parser-only verification without actual behavior checks
7. **`"equivalent to X"`** — Intent-only checks without real system verification
8. **Placeholder step definitions** — Auto-generated from undefined steps to silence Behave errors
9. **`"Simulate"` comments** — Any code claiming to simulate instead of actually executing
10. **`pass` statements in @then steps** — Silent bypass of verification

### WHAT YOU MUST DO INSTEAD

| FORBIDDEN PATTERN | REQUIRED REPLACEMENT |
|-------------------|---------------------|
| `assert True, "verified"` | `docker ps` to verify actual state |
| `getattr(context, 'x', True)` | `subprocess.run(['command'])` and check result |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |

### PAST VIOLATIONS MUST BE CORRECTED

**Historical context (DO NOT REPEAT):**
- `customization_steps.py` — 100+ placeholder steps — **DELETED**
- `ssh_docker_steps.py` lines 277-398 — Undefined step placeholders — **DELETED**
- `cache_steps.py` lines 376+ — Undefined step placeholders — **DELETED**

These were created to silence Behave's "undefined step" errors. This is **FORBIDDEN**.

**When Behave reports undefined steps:**
1. ✅ Implement the step properly with real verification
2. ✅ Leave it undefined and accept the error
3. ❌ **NEVER** create a placeholder that just sets `context.step_xxx = True`

### SIGNIFICANCE

This is the **MOST CRITICAL RULE** in this document because:

1. **Fake tests give false confidence** — Tests pass but functionality is broken
2. **They compound over time** — Each fake pattern makes the next one easier
3. **They're hard to detect** — Look like real tests but verify nothing
4. **They violate user trust** — The user explicitly forbade this pattern

**VIOLATION OF THIS SECTION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**

---

# 🛠️ PROACTIVE TOOL USAGE

### Sub-Agents (Task Tool)

**MANDATORY usage scenarios:**
- **Explore** → Codebase exploration, finding files, understanding architecture
- **general-purpose** → Multi-step tasks, complex research, cross-file code search
- **Plan** → Designing implementation strategies BEFORE coding (Phase 1)
- **yume-implementer** → Fixing specific issues identified by yume-guardian (Phase 3)
- **code-reviewer** → Reviewing staged changes BEFORE commit (Phase 4)
- **yume-guardian** → Review test changes for fake testing patterns (Phase 3)

### MCP Tools

**ALWAYS use these when applicable — do NOT wait for user request:**

| MCP Service | Purpose | Trigger |
|-------------|---------|---------|
| `sequential-thinking` | Complex reasoning, debugging, planning | **ALL multi-step thinking, debugging, analysis** |
| `github` | PRs, issues, file operations, search | Any GitHub interaction |
| `context7` | Library/API docs, code examples | Documentation queries |
| `fetch` | Web requests, external data | URL-based queries |
| `4.5v-mcp` | Image analysis | Image file inputs |

**Sequential-Thinking MCP (NON-OPTIONAL):**
**ALWAYS use `mcp__sequential-thinking__sequentialthinking` for:**
- Debugging issues or unexpected behavior
- Tracing through complex code logic
- Analyzing test failures
- Understanding shell function interactions
- Any multi-step reasoning or planning

**This is NOT optional.** Do NOT "think in your head" — use the tool.

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

# 📁 VDE PROJECT CONTEXT (Immutable Facts)

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

# 🔒 SAFETY CHECKLIST (Pre-Commit Gatekeeper)

**BEFORE any commit (Phase 5), verify:**

1. [ ] All tests pass
2. [ ] Yume-guardian: CLEAN (zero violations)
3. [ ] Code-reviewer: Approval received
4. [ ] `public-ssh-keys/` contains ONLY `.keep` and `~/.ssh/*.pub` files
5. [ ] NO private keys anywhere in the commit

**If ANY check fails → DO NOT COMMIT.**

---

# 📤 TASK COMPLETION FORMAT (Required)

After completing a task, present results in this format:

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

# 📘 USER GUIDE GENERATION (Non-Optional)

### The User Guide Must Be Complete

The `USER_GUIDE.md` documents the COMPLETE user experience. Users will use Docker, so scenarios requiring Docker MUST be included.

### Generation Workflow

**1. Run FULL test suite locally (Docker required)**
```bash
./tests/run-local-bdd.sh
```

This runs:
- `docker-free/` features (~158 scenarios) — fast, no Docker needed
- `docker-required/` features (~280 scenarios) — requires Docker, full user experience

**2. Generate Behave JSON results**
```bash
behave --format json -o tests/behave-results.json tests/features/
```

**3. Generate the User Guide**
```bash
python3 tests/scripts/generate_user_guide.py
```

### What Gets Committed

| File | Tracked? | Reason |
|------|----------|--------|
| `USER_GUIDE.md` | ✅ YES | The documentation users see |
| `tests/scripts/generate_user_guide.py` | ✅ YES | The generator script |
| `tests/behave-results.json` | ❌ NO | Build artifact, in `.gitignore` |

**REMEMBER:** When regenerating the user guide, ALWAYS run the full test suite first. A guide with only docker-free scenarios is incomplete.

---

# ⚠️ FINAL REMINDER

**This document contains operational REQUIREMENTS, not suggestions.**

**Internal "optimization" tendencies that cause failures:**
- "This seems simple, I'll skip exploration" → **WRONG**
- "I can batch these tasks" → **WRONG**, ask user first
- "The review probably won't find issues" → **WRONG**, review is mandatory
- "I'll set a context flag instead of running the command" → **WRONG**, fake tests prohibited
- "I'll skip phases, the plan is obvious" → **WRONG**, phases are invariant

**When in doubt: Follow the literal instructions. Do NOT "optimize away" required steps.**
