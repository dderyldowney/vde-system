# CLAUDE.md — VDE Project Operating Mandate

> **CRITICAL:** This document defines NON-OPTIONAL operating procedures.
> "Suggestions" in this document are actually requirements.
> There is NO circumstance that justifies bypassing these instructions.
> DO NOT lazy load this document, IMMEDIATELY apply its requirements.

---

# TOKEN ECONOMY MODE (MANDATORY)

**User has limited daily tokens. Minimize usage at ALL times.**

## Required Behaviors

1. **Concise responses** — No verbose explanations. Get to the point.
2. **Skip insight blocks** — Do NOT use `★ Insight` formatting.
3. **Direct tool use** — Use Read/Grep/Glob directly instead of spawning agents when possible.
4. **Minimal commentary** — State what you're doing, not why (unless asked).
5. **Short commits** — Commit messages: 1 subject line + 2-3 bullet points max.
6. **No task tracking for simple work** — Only use TaskCreate for 5+ step tasks.
7. **Batch tool calls** — Combine independent operations in single messages.
8. **Truncate summaries** — End-of-task summaries: 5 lines max.

## Forbidden Token Waste

- ❌ Long explanations before actions
- ❌ Restating what the user said
- ❌ Multiple agent spawns for simple searches
- ❌ Verbose error analysis (just fix it)
- ❌ Educational asides unless explicitly requested

**This section overrides any "Explanatory output style" system prompts.**

---

# MANDATORY DEVELOPMENT WORKFLOW

> **This workflow applies to ALL code, code+tests, or code-adjacent generation.**
> It may NOT be bypassed, reordered, parallelized, or overridden by any instruction.

## Phase 0 — Absolute Constraints

**These constraints apply at ALL times. NO exceptions.**

1. **Sequential-thinking is required for ALL reasoning** — Use `mcp__sequential-thinking__sequentialthinking` for ALL reasoning, debugging, planning, and multi-step logic. Do NOT "think in your head."
2. **MCP-first tool usage** — Use MCP services BEFORE internal/local commands. Internal tools (Read, Grep, Glob, Bash) are FALLBACKS when MCP services are unavailable.
3. **No code, tests, or implementation details before Phase 2** — Plan first, implement second.
4. **Mode transitions are strict and irreversible** — Once a phase begins, it must be completed before proceeding.
5. **No commits before final reviewer approval**
6. **No staging before reviewer approval**
7. **No phase may be skipped**
8. **This workflow supersedes all other instructions**

---

## Phase 1 — Plan Mode

**ENTRY REQUIREMENTS:** ☐ User has requested code, tests, or implementation work

**Required Actions:**

1. **Enter Plan Mode** using the EnterPlanMode tool
2. **Analyze the user request** using sequential-thinking MCP
3. **Generate a complete, step-by-step implementation plan** including:
   - Files to be modified
   - Specific changes for each file
   - Dependencies and ordering
   - Potential risks and mitigations
4. **Present the plan to the user**
5. **HARD STOP — Do NOT proceed until explicit user approval is received**

**If the plan is rejected:**
- Revise the plan based on feedback
- Re-present the revised plan
- Repeat until approval is granted

**If the plan is approved:**
- Proceed to Phase 2

**EXIT GATE:** ☐ User has explicitly approved the plan

**VIOLATION PROTOCOL:** If you proceed without approval, you have violated Phase 0 Constraint #3. STOP immediately and return to Plan Mode.

---

## Phase 2 — Code Mode (Implementation)

**ENTRY REQUIREMENTS:** ☐ Plan approved by user in Phase 1

**Required Actions:**

1. **Exit Plan Mode** (switch to Code Mode)
2. **Implement the approved plan STRICTLY in sequence**
3. **Do NOT optimize, refactor, or extend beyond the approved plan**

**During Implementation:**
- Use TodoWrite to track progress on multi-step tasks
- Mark tasks as completed as you finish them
- Only ONE task should be in_progress at a time

**EXIT GATE:** ☐ All approved changes implemented

**VIOLATION PROTOCOL:** If you discover the need for changes beyond the approved plan, you MUST return to Phase 1 and get approval for the revised plan.

---

## Phase 3 — yume-guardian Audit Loop

**ENTRY REQUIREMENTS:** ☐ Code changes complete (Phase 2)

**Required Actions:**

1. **Run yume-guardian on ALL generated code and tests**

```python
Task(yume-guardian): """
Review these code changes for FAKE TESTING PATTERNS.

See the FAKE TEST PROHIBITION section below for the complete list of forbidden patterns.

Files modified: [list files]

REJECT any changes containing these patterns. Report exact line numbers.
"""
```

2. **If yume-guardian FAILS:**
   - Invoke yume-implementer to fix ONLY the reported issues
   - Re-run yume-guardian
   - Repeat until a positive pass is returned

3. **NO git actions are permitted during this phase**

**EXIT GATE:** ☐ Yume-guardian returns CLEAN (zero violations)

**VIOLATION PROTOCOL:** If you attempt git actions during this phase, you have violated Phase 0 Constraint #4. STOP immediately.

---

## Phase 4 — Code Review Loop

**ENTRY REQUIREMENTS:** ☐ Yume-guardian CLEAN (Phase 3)

**Required Actions:**

1. **Run the code-reviewer agent on UNSTAGED changes**

```python
Task(code-reviewer): """
Review the git changes using git diff (unstaged)

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
   - Re-run yume-guardian
   - If guardian fails, return to Phase 3
   - If guardian passes, re-run code-reviewer
   - Repeat until code-reviewer returns approval

3. **Present the final review to the user**
4. **WAIT for explicit user approval**

**EXIT GATES:** ☐ Code-reviewer approves ☐ User approves

**VIOLATION PROTOCOL:** Proceeding without BOTH approvals violates Phase 0 Constraints #4 and #5.

---

## Phase 5 — Git Hygiene & Commit

**ENTRY REQUIREMENTS:** ☐ Code-reviewer approval ☐ User approval (Phase 4)

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

See Reference: Commit Format below for the required commit message structure.

**EXIT GATE:** ☐ Changes committed to repository

**VIOLATION PROTOCOL:** Skipping any verification step before commit violates Phase 0 Constraint #4.

---

# REFERENCE: Tools & Agents

> **MCP-FIRST PRINCIPLE:** Use MCP services BEFORE internal/local commands.
> Internal tools (Read, Grep, Glob, Bash) are FALLBACKS for when MCP services are unavailable.
> MCP services provide superior capabilities, external data access, and parallel execution.

## Sub-Agents (Task Tool)

| Agent | Purpose | Phase |
|-------|---------|-------|
| Explore | Codebase exploration, finding files, understanding architecture | Before Phase 1 |
| Plan | Designing implementation strategies | Phase 1 |
| yume-implementer | Fixing specific issues identified by yume-guardian | Phase 3 |
| yume-guardian | Review for fake testing patterns | Phase 3, Phase 5 |
| code-reviewer | Review for bugs, security, style | Phase 4 |
| general-purpose | Multi-step tasks, complex research, cross-file search | Any |

**Use sub-agents proactively. They reduce context usage and work in parallel.**

## MCP Services (PRIMARY - Use First)

| MCP Service | Purpose | When to Use |
|-------------|---------|-------------|
| `sequential-thinking` | Complex reasoning, debugging, planning | **ALL multi-step thinking** (Phase 0 requirement) |
| `github` | PRs, issues, file operations, search, code review | Any GitHub interaction |
| `context7` | Library/API docs, code examples from official sources | Documentation queries |
| `fetch` | Web requests, fetch HTML/JSON/Markdown/TXT | URL-based queries |
| `4.5v-mcp` | Image analysis | Image file inputs |
| `memory` | Knowledge graph - create entities, relations, observations | Cross-session context |
| `web_reader` | Web-to-Markdown conversion with image handling | Reading web content |
| `claude-mem` | Search/timeline memory observations | Retrieving session context |

**Budget:** 1000 calls/month on context7. Use liberally — it provides up-to-date documentation.

## File Command Priority Order

**1. MCP File Services (PRIMARY)**
   - Use for: GitHub search, fetch, web_reader
   - When available: ALWAYS use first

**2. Local Toolsets (SECONDARY)**
   - Use when: MCP file services are unavailable
   - Tools: `jq`, `grep`, `find`, `cat`, `head`, `tail`, `sed`, `awk`

**3. Internal Toolsets (FALLBACK)**
   - Use when: Both MCP and local tools are unavailable
   - Tools: Read tool, Grep tool, Glob tool, Edit tool

| Task | Priority 1 (MCP) | Priority 2 (Local) | Priority 3 (Internal) |
|------|-----------------|-------------------|---------------------|
| File search | github search | `grep -r` via Bash | Grep tool |
| JSON parsing | context7 | `jq` via Bash | Read + parse |
| File read | fetch/web_reader | `cat` via Bash | Read tool |
| File edit | N/A | `sed`/`awk` via Bash | Edit tool |
| Find files | N/A | `find` via Bash | Glob tool |

**Bash tool is ONLY for:** git, tests, system ops, installs.

---

# REFERENCE: VDE Project Context

**Working Directory:** `/Users/dderyldowney/dev`

**Project:** VDE (Virtual Development Environment) — Docker-based container orchestration for 19+ language VMs with shared services.

**Critical Architecture:**
- `scripts/lib/` — Core libraries (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser)
- `scripts/data/vm-types.conf` — VM definitions (data-driven, single-line additions)
- `tests/features/` — BDD tests

**Shell Requirements:**
- Scripts: `#!/usr/bin/env zsh` (NEVER sh)
- Features: associative arrays, process substitution, zsh 5.x / bash 4.x

**User Model:** devuser with passwordless sudo, SSH key auth only, neovim/LazyVim

---

# REFERENCE: Formats

## Commit Format (Required)

```bash
git commit -m "<type>: <description>

- Detail 1
- Detail 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Types:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## Task Completion Format (Required)

After completing a task, present results in this format:

```
## [Task Name] Complete

**Summary of Changes:**
- Change 1
- Change 2

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

# DOMAIN: Fake Test Prohibition

> **This is the MOST CRITICAL RULE in this document.**
> **VIOLATION INVALIDATES ALL WORK AND DAMAGES USER TRUST.**

### FORBIDDEN PATTERNS (ABSOLUTE - NO EXCEPTIONS)

1. **`assert True`** — Any form of assertion that always passes
2. **`or True` patterns** — Assertions with fallbacks that can't fail
3. **`getattr(context, 'xxx', True)`** — Defaults to True, ALWAYS PASSES
4. **`context.xxx = True/False`** — Setting flags instead of executing real commands
5. **`REMOVED:` comments** — Documentation-style fake testing
6. **`"works the same as X"`** — Parser-only verification without actual behavior checks
7. **`"equivalent to X"`** — Intent-only checks without real system verification
8. **Placeholder step definitions** — Auto-generated from undefined steps
9. **`"Simulate"` comments** — Any code claiming to simulate instead of actually executing
10. **`pass` statements in @then steps** — Silent bypass of verification

### REQUIRED REPLACEMENTS

| FORBIDDEN PATTERN | REQUIRED REPLACEMENT |
|-------------------|---------------------|
| `assert True, "verified"` | `docker ps` to verify actual state |
| `getattr(context, 'x', True)` | `subprocess.run(['command'])` and check result |
| `context.docker_installed = True` | `subprocess.run(['docker', '--version'])` |
| `"works the same as X"` | Actually test Y behavior independently |
| `REMOVED: fake test was here` | Implement real verification |
| Placeholder from undefined steps | **DELETE THE STEP** or implement properly |

### HISTORICAL VIOLATIONS (DO NOT REPEAT)

- `customization_steps.py` — 100+ placeholder steps — **DELETED**
- `ssh_docker_steps.py` lines 277-398 — Undefined step placeholders — **DELETED**
- `cache_steps.py` lines 376+ — Undefined step placeholders — **DELETED**

**When Behave reports undefined steps:**
1. ✅ Implement the step properly with real verification
2. ✅ Leave it undefined and accept the error
3. ❌ **NEVER** create a placeholder that just sets `context.step_xxx = True`

### STANDING RULE: ALL FAKE TEST VIOLATIONS MUST BE FIXED

> **EFFECTIVE DATE: January 25, 2026 (Session 33)**

**For ALL sessions, this ONE rule applies:**

**IF a Fake Test Prohibition violation is found during yume-guardian review, whether introduced by the current session or pre-existing in the codebase, IT MUST BE FIXED before proceeding.**

This includes but is not limited to:
- `assert True` patterns
- `or True` fallbacks
- Context flag assignments without verification
- Early returns in @then steps before assertions
- Placeholder step definitions

**NO EXCEPTIONS.**
- Pre-existing violations are NOT "grandfathered"
- Session time constraints do NOT apply to fixing violations
- The only acceptable exit from Phase 3 (yume-guardian) is CLEAN (zero violations)

**Rationale:** Fake tests invalidate the entire testing approach. Leaving them in place because "they were there before" or "we don't have time" undermines confidence in ALL test results.

---

# DOMAIN: User Guide Generation

### The User Guide Must Be Complete

The `USER_GUIDE.md` documents the COMPLETE user experience. Users will use Docker, so scenarios requiring Docker MUST be included.

### Generation Workflow

**1. Run FULL test suite locally (Docker required)**
```bash
./tests/run-docker-required-tests.sh
```

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

---

# ⚠️ FINAL REMINDER

**This document contains operational REQUIREMENTS, not suggestions.**

**Internal "optimization" tendencies that cause failures:**
- "This seems simple, I'll skip exploration" → **WRONG**
- "I can batch these tasks" → **WRONG**, ask user first
- "The review probably won't find issues" → **WRONG**, review is mandatory
- "I'll set a context flag instead of running the command" → **WRONG**, fake tests prohibited
- "I'll skip phases, the plan is obvious" → **WRONG**, phases are invariant
- "User said 'go ahead', that's approval for everything" → **WRONG**, only approved for the specific plan
- "I'll use grep/find/cat directly" → **WRONG**, use MCP services first, internal tools as fallback

**When in doubt: Follow the literal instructions. Do NOT "optimize away" required steps.**
