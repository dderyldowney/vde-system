# VDE Agent Directory

This file documents the specialized AI agents available within the Gemini-Kit team for developing and maintaining the Virtual Development Environment (VDE).

## Authoritative Specification

**Specification Document:** [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md) (v1.0.0)

> **MANDATE**: All development, bug fixes, and implementation work MUST conform to [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md). This document is the single source of truth for:
> - Function signatures and interfaces
> - Data structures and file formats
> - CLI command specifications
> - Error codes and return values
> - Implementation priorities
>
> **Specification Flow (Tests Prove Implementation)**:
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
> Any implementation that does not conform to this specification is considered invalid.

---

## Core Mandates
- **MCP Server Utilization**: All agents must utilize connected MCP servers.
- **Active Endpoints**: Ensure all tool invocations reference active MCP endpoints.
- **Connectivity Validation**: Validate server connectivity prior to execution.
- **Interaction Logging**: Log all MCP interactions for audit and troubleshooting.
- **Specification Compliance**: All implementations must match [`docs/VDE-SPEC.md`](docs/VDE-SPEC.md).

---

## Planner
- **Description**: Creates detailed implementation plans and strategies for complex features.
- **File Path**: `agents/planner.md`
- **Role**: Architect & Strategist
- **Core Capabilities**: Task decomposition, architectural planning, dependency mapping.
- **Dependencies**: Scout, Codebase Investigator.
- **Interaction Protocol**: Invoke via `/plan` or direct request for a roadmap.
- **Example Usage**: "Planner, create a strategy to migrate the remaining bash scripts to zsh."

---

## Scout
- **Description**: Explores the codebase to understand structure, patterns, and conventions.
- **File Path**: `agents/scout.md`
- **Role**: Information Gatherer
- **Core Capabilities**: Codebase traversal, pattern identification, convention discovery.
- **Dependencies**: None.
- **Interaction Protocol**: Invoke via `/explore` or when starting a new task.
- **Example Usage**: "Scout, find all files that source 'vde-parser' and document their usage."

---

## Coder
- **Description**: Writes clean, efficient, and idiomatic code adhering to project standards.
- **File Path**: `agents/coder.md`
- **Role**: Software Engineer
- **Core Capabilities**: Scripting (Zsh), Python development, Docker configuration.
- **Dependencies**: Planner, Scout.
- **Interaction Protocol**: Triggered during the implementation phase of a task.
- **Example Usage**: "Coder, implement the new intent detection logic in 'vde-parser'."

---

## Tester
- **Description**: Writes and executes tests to ensure software quality and reliability.
- **File Path**: `agents/tester.md`
- **Role**: QA Engineer
- **Core Capabilities**: Behave BDD tests, Pytest, shell script verification.
- **Dependencies**: Coder.
- **Interaction Protocol**: Invoke via `/test` or after code changes.
- **Example Usage**: "Tester, create a new feature file for the 'ssh-vm' command."

---

## Reviewer
- **Description**: Performs systematic code reviews to ensure quality and consistency.
- **File Path**: `agents/reviewer.md`
- **Role**: Quality Auditor
- **Core Capabilities**: Static analysis, best practice verification, security checks.
- **Dependencies**: Coder.
- **Interaction Protocol**: Invoke via `/review` before committing changes.
- **Example Usage**: "Reviewer, check these Zsh library changes for shell compatibility."

---

## Debugger
- **Description**: Analyzes errors and bugs to identify root causes and suggest fixes.
- **File Path**: `agents/debugger.md`
- **Role**: Troubleshooting Expert
- **Core Capabilities**: Log analysis, trace investigation, root cause analysis.
- **Dependencies**: Scout, Tester.
- **Interaction Protocol**: Invoke via `/debug` when tests fail or errors occur.
- **Example Usage**: "Debugger, analyze why the 'vde-health' check is failing in the CI environment."

---

## Git Manager
- **Description**: Manages version control operations and commit history.
- **File Path**: `agents/git-manager.md`
- **Role**: SCM Administrator
- **Core Capabilities**: Commit preparation, branch management, PR drafting.
- **Dependencies**: Reviewer.
- **Interaction Protocol**: Invoke when preparing to save or push work.
- **Example Usage**: "Git Manager, prepare a commit for the parser enhancements."

---

## Security Auditor
- **Description**: Conducts security audits and vulnerability scans on the codebase.
- **File Path**: `agents/security-auditor.md`
- **Role**: Security Engineer
- **Core Capabilities**: Vulnerability detection, secret scanning, permission auditing.
- **Dependencies**: Codebase Investigator.
- **Interaction Protocol**: Invoke via `/security:analyze` or manual review.
- **Example Usage**: "Security Auditor, scan the SSH configuration for potential privilege escalation."

---

## Docs Manager
- **Description**: Manages project documentation and ensures it stays in sync with code.
- **File Path**: `agents/docs-manager.md`
- **Role**: Technical Writer
- **Core Capabilities**: Markdown generation, technical deep dives, README updates.
- **Dependencies**: Coder.
- **Interaction Protocol**: Triggered after feature implementation or architectural changes.
- **Example Usage**: "Docs Manager, update the 'Technical-Deep-Dive.md' with the new SSH architecture."

---

## Project Manager
- **Description**: Oversees project progress, manages todos, and coordinates team tasks.
- **File Path**: `agents/project-manager.md`
- **Role**: Team Lead
- **Core Capabilities**: Task tracking, roadmap management, workflow optimization.
- **Dependencies**: All Agents.
- **Interaction Protocol**: Consulted for high-level status or priority decisions.
- **Example Usage**: "Project Manager, what are the high-priority items remaining for the zsh migration?"

---

## Database Admin
- **Description**: Manages database configurations, migrations, and performance for service VMs.
- **File Path**: `agents/database-admin.md`
- **Role**: Database Specialist
- **Core Capabilities**: SQL/NoSQL configuration, data persistence, service optimization.
- **Dependencies**: DevOps Engineer.
- **Interaction Protocol**: Consulted for tasks involving service VM data layers.
- **Example Usage**: "Database Admin, optimize the PostgreSQL template for heavy write workloads."

---

## Backend Specialist
- **Description**: Expert in server-side logic, API design, and system integration.
- **File Path**: `agents/backend-specialist.md`
- **Role**: Backend Architect
- **Core Capabilities**: Service orchestration, API design, performance tuning.
- **Dependencies**: Coder.
- **Interaction Protocol**: Engaged for core system logic and service-to-service communication.
- **Example Usage**: "Backend Specialist, design the communication protocol between the language VMs and the shared redis service."

---

## Fullstack Developer
- **Description**: Versatile engineer capable of working across all layers of the stack.
- **File Path**: `agents/fullstack-developer.md`
- **Role**: Generalist Engineer
- **Core Capabilities**: End-to-end feature development, integration testing.
- **Dependencies**: Frontend Specialist, Backend Specialist.
- **Interaction Protocol**: Assigned to tasks requiring both infrastructure and application-level changes.
- **Example Usage**: "Fullstack Developer, implement a new service VM and its corresponding management CLI commands."

---

## Researcher
- **Description**: Researches external resources, libraries, and best practices.
- **File Path**: `agents/researcher.md`
- **Role**: Knowledge Specialist
- **Core Capabilities**: External documentation analysis, library comparison, technical research.
- **Dependencies**: None.
- **Interaction Protocol**: Invoke when exploring new technologies or solving unique problems.
- **Example Usage**: "Researcher, find the best practices for implementing SSH agent forwarding in isolated Docker networks."

---

## Brainstormer
- **Description**: Generates creative ideas and alternative approaches to problems.
- **File Path**: `agents/brainstormer.md`
- **Role**: Creative Thinker
- **Core Capabilities**: Idea generation, brainstorming, alternative path analysis.
- **Dependencies**: None.
- **Interaction Protocol**: Invoke during the initial phase of complex problem-solving.
- **Example Usage**: "Brainstormer, suggest three different ways we could handle automatic port collision detection."

---

## UI Designer
- **Description**: Focuses on the user interface and user experience of VDE components.
- **File Path**: `agents/ui-designer.md`
- **Role**: UX/UI Specialist
- **Core Capabilities**: CLI output design, progress indicator styling, UX workflow mapping.
- **Dependencies**: Docs Manager.
- **Interaction Protocol**: Consulted for improving the visual feedback and usability of the CLI.
- **Example Usage**: "UI Designer, propose a more intuitive layout for the 'vde status' command output."

---

## Frontend Specialist
- **Description**: Expert in frontend frameworks and user interface development.
- **File Path**: `agents/frontend-specialist.md`
- **Role**: Frontend Engineer
- **Core Capabilities**: Web UI (if applicable), CLI presentation layers.
- **Dependencies**: UI Designer.
- **Interaction Protocol**: Consulted for any future web-based management dashboards.
- **Example Usage**: "Frontend Specialist, suggest a React-based structure for a VDE management dashboard."

---

## Copywriter
- **Description**: Creates high-quality marketing, community, and technical content.
- **File Path**: `agents/copywriter.md`
- **Role**: Content Creator
- **Core Capabilities**: Technical blogging, release notes, community engagement content.
- **Dependencies**: Docs Manager.
- **Interaction Protocol**: Invoke when preparing public-facing announcements or blog posts.
- **Example Usage**: "Copywriter, draft a blog post announcing the release of VDE Stage 7."
