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
7. **ALWAYS use best tools** - Sub-agents, MCPs, and local tools WITHOUT being asked

---

## 🤖 PROACTIVE TOOL USAGE (use WITHOUT being asked)

**MANDATE:** Use the right tool for the job. Do NOT wait for explicit instruction.

### Sub-Agents (Task tool)

**Use sub-agents for:**
- **Explore**: Codebase exploration, finding files, understanding architecture
- **general-purpose**: Multi-step tasks, complex research, code search across files
- **Plan**: Designing implementation strategies before coding
- **code-reviewer**: Reviewing staged changes before commit (MANDATORY)

**Sub-agents reduce your context usage and work in parallel. Use them proactively.**

```bash
# Examples of WHEN to use sub-agents:
- "Where is error handling for X?" → Task(Explore)
- "Find all uses of function Y" → Task(Explore)
- "Refactor this module" → Task(Plan) first
- "Review my changes" → Task(code-reviewer) BEFORE commit
```

### MCP Tools (Available Services)

**ALWAYS use MCP tools when available. They reduce context usage and provide specialized capabilities:**

| MCP Service | Use For | Tools |
|-------------|---------|-------|
| **github** | PRs, issues, file operations, search | `mcp__github__*` |
| **context7** | Library/API docs, code examples | `mcp__context7__*` |
| **sequential-thinking** | Complex reasoning, planning | `mcp__sequential-thinking__*` |
| **fetch** | Web requests, external data | `mcp__fetch__*` |
| **4.5v-mcp** | Image analysis | `mcp__4_5v_mcp__analyze_image` |

**Check available MCPs with `ListMcpResourcesTool` - use them without asking.**

### Local Tools (jq, awk, sed, grep)

**PREFER specialized tools over Bash pipelines:**

| Task | Preferred Tool | Avoid |
|------|----------------|-------|
| JSON parsing | Bash: `jq '.key' file.json` | `cat file \| jq` |
| JSON queries | Bash: `jq -r '.path' file` | `jq '.' huge-file.json` |
| File search | Grep tool | `grep -r` via Bash |
| File read | Read tool | `cat`, `head`, `tail` |
| File edit | Edit tool | `sed -i`, `awk` |
| Find files | Glob tool | `find . -name` |

**Use Bash tool ONLY for:**
- Git operations (git status, git log, git diff, etc.)
- Running tests, build commands
- System operations (chmod, chown, mkdir, etc.)
- Install operations (npm, pip, cargo, etc.)

**Never use Bash echo or shell commands for communication.**

---

## 📚 DOCUMENTATION & API QUERIES (Context7 MCP)

**ALWAYS use Context7 MCP (`mcp__context7__*` tools) for:**
- Library/API documentation queries
- Code generation from documentation
- Setup and configuration steps
- Best practices for frameworks/tools
- Syntax and semantics verification

**Workflow:**
1. Use `mcp__context7__resolve-library-id` to find the correct library ID
2. Use `mcp__context7__query-docs` with the library ID and specific query
3. Do NOT wait for user to request this - proactively use it for any documentation needs

**Budget:** 1000 calls/month. Use liberally - it provides up-to-date, accurate documentation with code examples directly from official sources.

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

## 🔍 CODE REVIEW BEFORE COMMIT

**MANDATORY:** All commits must be reviewed by the code-reviewer agent before being finalized.

### Pre-Commit Review Workflow

1. **Stage all changes:**
   ```bash
   git add -A
   ```

2. **Run code-reviewer agent:**
   ```
   Use Task tool with subagent_type=code-reviewer
   Prompt: "Review the staged git changes using `git diff --cached`"
   ```

3. **Present review to user for approval:**
   - Summarize the review findings
   - Highlight any issues found
   - **WAIT for user approval before committing**

4. **Only after user approval:**
   - Make any requested changes
   - Commit with proper format including attribution

**NEVER commit without user approval after code review.**

---

## 📝 COMMIT FORMAT

```
git commit -m "<type>: <description>

- Detail 1
- Detail 2

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: feat:, fix:, docs:, test:, refactor:

---

## 📤 RESPONSE FORMAT FOR TASK COMPLETION

When completing a task, use this summary format:

```
## [Task Name] Complete

**Summary of Changes:**
- Change 1
- Change 2
- Change 3

**Test Results:**
- Before: X failures
- After: Y failures/passing

**Files Modified:**
- file1.ext - description

**Next Options:**
- Option A
- Option B
- Option C

Which would you like next?
```

**Workflow:** Complete one task → Display results → Ask what's next. Do not batch multiple task completions without user confirmation.

---

## ⚠️ REMEMBER

This is NOT a suggestion file. These are operational requirements.

Your first response MUST include the verification checklist from the "YOUR RESPONSE MUST START WITH" section above.

If you cannot provide these verifications, you have not completed the required startup sequence.
