# VDE Agent Directory

This file documents the specialized AI agents available within the Gemini-Kit team for developing and maintaining the Virtual Development Environment (VDE).

## Authoritative Specification

**Specification Document:** [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md) (v1.0.0)

> **MANDATE**: All development, bug fixes, and implementation work MUST conform to [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md). This document is the single source of truth for:
>
> - Function signatures and interfaces
> - Data structures and file formats
> - CLI command specifications
> - Error codes and return values
> - Implementation priorities
>
> **Specification Flow (Tests Prove Implementation)**:
>
> ```
> USER GUIDE (Documented Workflows)
>         ↓
> SPECIFICATION (Technical Requirements)
>         ↓
> CODE / IMPLEMENTATION
>         ↓
> TESTS (Prove implementation works as designed)
>   Scenarios → Individual Steps
> ```
>
> The User Guide documents the workflows. The Specification translates these into technical requirements. The Code implements the specification. The Tests prove the code does what it was designed to do, from Scenarios (feature-level) down to individual Steps (implementation-level).
>
> **Update Authorization**: Specification updates require explicit User authorization. Agents must not modify [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md) without prior approval.
>
> **Revision Control**: The version number MUST be incremented for EVERY single change, whether to test requirements or specification blocks. The Last Updated timestamp MUST also be updated to full ISO 8601 format. Minor changes increment patch (1.0.1), significant changes increment minor (1.1.0), breaking changes increment major (2.0.0).
>
> Any implementation that does not conform to this specification is considered invalid.

---

## Core Mandates

- **Sub-Agent Swarm Execution (MANDATORY)**: ALL work MUST use sub-agents, preferably in swarm form (parallel execution). Single-agent direct execution is forbidden except for trivial read-only queries. See `.kilocode/rules/subagent_mcp_mandate.md` for full protocol.
- **MCP Server Utilization (PRIMARY)**: All agents MUST utilize connected MCP servers (e.g., `context7`, `github`, `redis`, `MCP_DOCKER`) as their PRIMARY interface. MCP services are ALWAYS preferred over local tools. Priority: MCP → Sub-Agents → Local CLI → Internal Tools.
- **No Circular Delegation**: Only the **Main Agent** (Gemini CLI) is permitted to use the `generalist` sub-agent tool. Specialized sub-agents MUST NOT attempt to delegate tasks further or invoke the `generalist` tool. They must complete assigned tasks using their own specialized tools and context.
- **Documentation Source-of-Truth**: All documentation updates, technical deep dives, and API/library queries MUST utilize the `context7` and `gemini-docs-mcp` MCP servers to ensure accuracy and version alignment.
- **Active Endpoints**: Ensure all tool invocations reference active MCP endpoints.
- **Connectivity Validation**: Validate server connectivity prior to execution.
- **Interaction Logging**: Log all MCP interactions for audit and troubleshooting.
- **Specification Compliance**: All implementations must match [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md).
- **Git Hygiene (LOCAL FIRST)**: Commit locally freely. **DO NOT push to origin until User explicitly authorizes.** This prevents dirty git history if commits need modification.

---

## Project Portability (FUNDAMENTAL DESIGN GOAL)

The entire VDE project is designed to be **fully portable**. A user can clone the project to any directory and move it anywhere on their system without regenerating configs.

### Portability Architecture

| Component | Storage | Portability |
|-----------|---------|-------------|
| `VDE_ROOT_DIR` | Derived from `bin/vde` location | Automatic on move |
| `VDE_SSH_DIR` | `$HOME/.ssh/vde` | Fixed (user-specific) |
| Docker compose files | Relative paths (`../../../`) | Works from new location |
| SSH config | `~/.ssh/vde/config` | Independent of project |
| Cache (`.cache/`) | VM metadata only (no paths) | Moves with project |

### Key Principles

1. **NO hardcoded paths** - Everything derives from `VDE_ROOT_DIR` or uses relative paths
2. **SSH operations** use `VDE_SSH_DIR="$HOME/.ssh/vde"` - completely independent of project location
3. **Cache contains no paths** - Only VM names, aliases, and metadata
4. **Relative paths in compose files** - `../../../projects/python` works from any project location

### What Happens on Project Move

When user moves project (e.g., `mv ~/dev ~/vde-system`):
1. `bin/vde` derives `VDE_ROOT_DIR=~/vde-system` automatically
2. Cache moves with project (inside `.cache/`)
3. Docker compose files use relative paths from new location
4. SSH config untouched (in `~/.ssh/vde/`)
5. **No regeneration needed** - everything Just Works

### User Responsibilities

- Add `VDE_ROOT_DIR/bin` to `$PATH` in `~/.zshrc`
- Re-source `~/.zshrc` after moving project
- Sync SSH config after `generate-all-configs`: `cp configs/ssh/config ~/.ssh/vde/config`

---

## Testing Guidelines

**NEVER run the full test suite during debugging or verification.** Only run full suite when explicitly needed.

### Efficient Testing Protocol

1. **Isolate first**: Run only the specific feature or test that relates to your fix
   - `behave tests/features/core-infrastructure/cache-system.feature` (no Docker spinup)
   - `zsh tests/unit/vde-shell-compat.test.zsh` (unit test, no containers)

2. **Verify minimally**: Run only what you need to verify the fix works
   - Don't spin up 27 VMs to test a port conflict
   - Use dry-runs, unit tests, or single features first

3. **Full suite only when complete**: Run `./tests/run-full-test-suite.zsh` ONLY after:
   - All fixes are implemented
   - You need a final verification pass
   - User explicitly requests it

4. **Document results**: Update MEMORY.md with test status after each fix

### Test Execution Rules

| Context | What to Run |
|---------|-------------|
| Fixing unit test | `zsh tests/unit/<specific>.test.zsh` |
| Fixing BDD feature | `behave tests/features/core-infrastructure/<feature>.feature` |
| Fixing Docker issue | `behave tests/features/core-infrastructure/<feature>.feature --tags=@requires-docker-host` |
| After all fixes done | `./tests/run-full-test-suite.zsh` |

---

## Project Memory & Session Handover

All agents MUST follow these documentation protocols to ensure continuity across sessions:

### Project Memory (MEMORY.md)

- **File**: `MEMORY.md` in project root
- **Purpose**: Single source of truth for project state, current goals, and known issues across sessions
- **Requirements**:
  - Agents MUST read `MEMORY.md` at the start of every new session
  - Agents MUST update `MEMORY.md` in **near real-time** as work progresses (test results, key findings, milestone completions)
  - Use clear timestamps (ISO 8601) for all entries
  - Include current test status, active goals, blockers, and code changes
  - **Critical**: Keep MEMORY.md current - update immediately when significant events occur (test runs, fixes applied, phase completions)

### Paired Session Handover Files

- **Files**:
  - `session_handover.md` - Current session context, accomplishments, and next steps
  - `plans/session_handover_remediation.md` - Remediation plan with phased approach
- **Requirements**:
  - Agents MUST read both files at session start
  - Agents MUST update both files when work scope changes or significant milestones are reached
  - Updates MUST be synchronized between the two files (paired update policy)
  - Include cross-references between documents for traceability
- **File Paths**: Both relative to project root

### Workflow Integration

1. At session start: Read `MEMORY.md` → Read `session_handover.md` + `plans/session_handover_remediation.md`
2. During work: Update files in near real-time as milestones are reached
3. At session end: Document completed work, test results, and next steps in all three files

---

## Planner

- **Description**: Creates detailed implementation plans and strategies for complex features.
- **File Path**: `agents/planner.md`
- **Role**: Architect & Strategist
- **Core Capabilities**: Task decomposition, architectural planning, dependency mapping, **MCP-driven roadmap generation**.
- **Dependencies**: Scout, Codebase Investigator, Context7.
- **Interaction Protocol**: Invoke via `/plan` or direct request for a roadmap.
- **Example Usage**: "Planner, create a strategy to migrate the remaining bash scripts to zsh."

---

## Scout

- **Description**: Explores the codebase to understand structure, patterns, and conventions.
- **File Path**: `agents/scout.md`
- **Role**: Information Gatherer
- **Core Capabilities**: Codebase traversal, pattern identification, convention discovery, **integrated MCP tool discovery**.
- **Dependencies**: None.
- **Interaction Protocol**: Invoke via `/explore` or when starting a new task.
- **Example Usage**: "Scout, find all files that source 'vde-parser' and document their usage."

---

## Coder

- **Description**: Writes clean, efficient, and idiomatic code adhering to project standards.
- **File Path**: `agents/coder.md`
- **Role**: Software Engineer
- **Core Capabilities**: Scripting (Zsh), Python development, Docker configuration, **MCP-integrated development workflows**.
- **Dependencies**: Planner, Scout, MCP_DOCKER.
- **Interaction Protocol**: Triggered during the implementation phase of a task.
- **Example Usage**: "Coder, implement the new intent detection logic in 'vde-parser'."

---

## Tester

- **Description**: Writes and executes tests to ensure software quality and reliability.
- **File Path**: `agents/tester.md`
- **Role**: QA Engineer
- **Core Capabilities**: Behave BDD tests, Pytest, shell script verification, **MCP-driven automated testing**.
- **Dependencies**: Coder, MCP_DOCKER.
- **Interaction Protocol**: Invoke via `/test` or after code changes.
- **Example Usage**: "Tester, create a new feature file for the 'ssh-vm' command."

---

## Reviewer

- **Description**: Performs systematic code reviews to ensure quality and consistency.
- **File Path**: `agents/reviewer.md`
- **Role**: Quality Auditor
- **Core Capabilities**: Static analysis, best practice verification, security checks, **MCP-assisted code auditing**.
- **Dependencies**: Coder, Github.
- **Interaction Protocol**: Invoke via `/review` before committing changes.
- **Example Usage**: "Reviewer, check these Zsh library changes for shell compatibility."

---

## Debugger

- **Description**: Analyzes errors and bugs to identify root causes and suggest fixes.
- **File Path**: `agents/debugger.md`
- **Role**: Troubleshooting Expert
- **Core Capabilities**: Log analysis, trace investigation, root cause analysis, **contextual bug tracing via MCP**.
- **Dependencies**: Scout, Tester, Memory.
- **Interaction Protocol**: Invoke via `/debug` when tests fail or errors occur.
- **Example Usage**: "Debugger, analyze why the 'vde-health' check is failing in the CI environment."

---

## Git Manager

- **Description**: Manages version control operations and commit history.
- **File Path**: `agents/git-manager.md`
- **Role**: SCM Administrator
- **Core Capabilities**: Commit preparation, branch management, PR drafting, **Github MCP integration**.
- **Dependencies**: Reviewer, Github.
- **Interaction Protocol**: Invoke when preparing to save or push work.
- **Example Usage**: "Git Manager, prepare a commit for the parser enhancements."

---

## Security Auditor

- **Description**: Conducts security audits and vulnerability scans on the codebase.
- **File Path**: `agents/security-auditor.md`
- **Role**: Security Engineer
- **Core Capabilities**: Vulnerability detection, secret scanning, permission auditing, **automated security scanning via MCP**.
- **Dependencies**: Codebase Investigator, Security.
- **Interaction Protocol**: Invoke via `/security:analyze` or manual review.
- **Example Usage**: "Security Auditor, scan the SSH configuration for potential privilege escalation."

---

## Docs Manager

- **Description**: Manages project documentation and ensures it stays in sync with code.
- **File Path**: `agents/docs-manager.md`
- **Role**: Technical Writer
- **Core Capabilities**: Markdown generation, technical deep dives, README updates, **Documentation synchronization via Context7 and Gemini-Docs-MCP**.
- **Dependencies**: Coder, Context7, Gemini-Docs-MCP.
- **Interaction Protocol**: Triggered after feature implementation or architectural changes.
- **Example Usage**: "Docs Manager, update the 'Technical-Deep-Dive.md' with the new SSH architecture."

---

## Project Manager

- **Description**: Oversees project progress, manages todos, and coordinates team tasks.
- **File Path**: `agents/project-manager.md`
- **Role**: Team Lead
- **Core Capabilities**: Task tracking, roadmap management, workflow optimization.
- **Dependencies**: All Agents, Github, Memory.
- **Interaction Protocol**: Consulted for high-level status or priority decisions.
- **Example Usage**: "Project Manager, what are the high-priority items remaining for the zsh migration?"

---

## Database Admin

- **Description**: Manages database configurations, migrations, and performance for service VMs.
- **File Path**: `agents/database-admin.md`
- **Role**: Database Specialist
- **Core Capabilities**: SQL/NoSQL configuration, data persistence, service optimization.
- **Dependencies**: DevOps Engineer, Redis.
- **Interaction Protocol**: Consulted for tasks involving service VM data layers.
- **Example Usage**: "Database Admin, optimize the PostgreSQL template for heavy write workloads."

---

## Backend Specialist

- **Description**: Expert in server-side logic, API design, and system integration.
- **File Path**: `agents/backend-specialist.md`
- **Role**: Backend Architect
- **Core Capabilities**: Service orchestration, API design, performance tuning.
- **Dependencies**: Coder, Context7.
- **Interaction Protocol**: Engaged for core system logic and service-to-service communication.
- **Example Usage**: "Backend Specialist, design the communication protocol between the language VMs and the shared redis service."

---

## Fullstack Developer

- **Description**: Versatile engineer capable of working across all layers of the stack.
- **File Path**: `agents/fullstack-developer.md`
- **Role**: Generalist Engineer
- **Core Capabilities**: End-to-end feature development, integration testing.
- **Dependencies**: Frontend Specialist, Backend Specialist, Firebase.
- **Interaction Protocol**: Assigned to tasks requiring both infrastructure and application-level changes.
- **Example Usage**: "Fullstack Developer, implement a new service VM and its corresponding management CLI commands."

---

## Researcher

- **Description**: Researches external resources, libraries, and best practices.
- **File Path**: `agents/researcher.md`
- **Role**: Knowledge Specialist
- **Core Capabilities**: External documentation analysis, library comparison, technical research, **context-aware library search via Context7**.
- **Dependencies**: None, Context7, Gemini-Docs-MCP.
- **Interaction Protocol**: Invoke when exploring new technologies or solving unique problems.
- **Example Usage**: "Researcher, find the best practices for implementing SSH agent forwarding in isolated Docker networks."

---

## Brainstormer

- **Description**: Generates creative ideas and alternative approaches to problems.
- **File Path**: `agents/brainstormer.md`
- **Role**: Creative Thinker
- **Core Capabilities**: Idea generation, brainstorming, alternative path analysis, **MCP-enhanced concept mapping**.
- **Dependencies**: None, Context7.
- **Interaction Protocol**: Invoke during the initial phase of complex problem-solving.
- **Example Usage**: "Brainstormer, suggest three different ways we could handle automatic port collision detection."

---

## UI Designer

- **Description**: Focuses on the user interface and user experience of VDE components.
- **File Path**: `agents/ui-designer.md`
- **Role**: UX/UI Specialist
- **Core Capabilities**: CLI output design, progress indicator styling, UX workflow mapping, **design pattern research via Context7**.
- **Dependencies**: Docs Manager, Context7.
- **Interaction Protocol**: Consulted for improving the visual feedback and usability of the CLI.
- **Example Usage**: "UI Designer, propose a more intuitive layout for the 'vde status' command output."

---

## Frontend Specialist

- **Description**: Expert in frontend frameworks and user interface development.
- **File Path**: `agents/frontend-specialist.md`
- **Role**: Frontend Engineer
- **Core Capabilities**: Web UI (if applicable), CLI presentation layers, **Modern frontend documentation via Context7**.
- **Dependencies**: UI Designer, Context7.
- **Interaction Protocol**: Consulted for any future web-based management dashboards.
- **Example Usage**: "Frontend Specialist, suggest a React-based structure for a VDE management dashboard."

---

## Copywriter

- **Description**: Creates high-quality marketing, community, and technical content.
- **File Path**: `agents/copywriter.md`
- **Role**: Content Creator
- **Core Capabilities**: Technical blogging, release notes, community engagement content, **AI-assisted tone adjustment**.
- **Dependencies**: Docs Manager, Context7.
- **Interaction Protocol**: Invoke when preparing public-facing announcements or blog posts.
- **Example Usage**: "Copywriter, draft a blog post announcing the release of VDE Stage 7."
