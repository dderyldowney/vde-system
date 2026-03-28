# SUB-AGENT & MCP MANDATE (MANDATORY)

## Core Mandate

**ALL work MUST use sub-agents (preferably in swarm form) AND MCP services as the primary execution model.**

This is not optional. Single-agent direct execution is forbidden except for trivial read-only queries.

---

## Sub-Agent Swarm Protocol

### When to Use Swarms

| Task Type | Swarm Configuration |
|-----------|---------------------|
| Complex analysis | 3+ explore agents in parallel |
| Test execution | Test runner + Docker monitor + Log analyzer |
| Code changes | Coder + Reviewer + Tester |
| Research | Researcher + Context7 lookup + Web search |
| Debugging | Debugger + Log analyzer + Scout |
| Fix/edit batch | >1 item OR >1 file edit | MANDATORY swarm — spawn coder agents |

### Swarm Execution Rules

1. **Parallel Launch**: Spawn all agents in a single message block
2. **Independent Tasks**: Each agent gets isolated, non-overlapping work
3. **Result Aggregation**: Main agent synthesizes results, never does the work
4. **No Sequential Chaining**: Avoid `Agent A → Agent B` if they can run in parallel

### Example Swarm Invocation

```
Launch simultaneously:
- Agent 1: Run test suite, capture full output
- Agent 2: Monitor Docker containers during tests
- Agent 3: Analyze test structure and patterns
```

---

## MCP Service Priority (MANDATORY)

**MCP services are ALWAYS preferred over local tools.**

### Priority Order

| Priority | Tool Type | When to Use |
|----------|-----------|-------------|
| 1 | MCP Services | ALWAYS first choice |
| 2 | Sub-Agents | For complex multi-step work |
| 3 | Local CLI | Only when MCP unavailable |
| 4 | Internal Tools | Only as last resort |

### Available MCP Services

| Service | Purpose | Use Case |
|---------|---------|----------|
| `sequential-thinking` | Complex reasoning | ALL multi-step thinking |
| `github` | GitHub operations | PRs, issues, search |
| `context7` | Library/API docs | Documentation queries |
| `fetch` | Web requests | URL-based queries |
| `memory` | Knowledge graph | Cross-session context |
| `redis` | Cache/state | Fast data operations |

---

## Forbidden Anti-Patterns

| Anti-Pattern | Why Forbidden | Correct Approach |
|--------------|---------------|------------------|
| Direct `bash` for file reads | Wastes tokens, no parallelization | Use `context7` or sub-agent |
| Sequential agent calls | Slow, inefficient | Launch as swarm |
| Skipping MCP for local tools | Loses structured output | Always try MCP first |
| Main agent doing research | Context bloat | Delegate to explore agent |
| Single-agent test runs | No monitoring/context | Swarm: runner + monitor + analyzer |

---

## Pre-Task Checklist (MANDATORY before any multi-step work)

Before starting any task, answer these questions:

| Question | Threshold | Action if Exceeded |
|----------|-----------|-------------------|
| How many files will I edit? | >1 file | Spawn implementation swarm |
| How many independent fix items? | >1 item | Spawn parallel coder agents |
| How many research queries needed? | >2 queries | Spawn explore/scout agent |
| Is this a planning task? | Any | Use sequential-thinking MCP first |

If ANY threshold is exceeded, sub-agents MUST be spawned before any direct tool use begins.

---

## Workflow Integration

### Phase 0: Pre-Work (NEW)

Before any Phase 1 planning:

1. **Spawn scout swarm** to understand codebase context
2. **Query MCP services** for relevant documentation
3. **Check memory** for cross-session context

### Phase 1-5 Integration

Each phase MUST begin with:
- Sub-agent spawn for the phase's work
- MCP service queries for context
- Swarm aggregation for results

---

## Token Economy Benefits

| Approach | Token Cost | Speed | Quality |
|----------|------------|-------|---------|
| Single agent direct | HIGH | Slow | Variable |
| Sub-agent swarm | LOW (distributed) | Fast | High |
| MCP-first | LOWEST | Fastest | Consistent |

---

## Pre-Edit Gate (MANDATORY BEHAVIORAL STEP — ALL agents, ALL file-modifying actions)

Before EVERY direct Edit, Write, or Bash call that modifies files, execute this protocol:

```
PRE-EDIT GATE:
1. STATE: "I am about to make [N] direct edit(s) to [files]."
2. COUNT: Is N > 1?
   - YES → STOP. Spawn coder sub-agent swarm. Do NOT proceed.
   - NO → STATE: "1 edit. Proceeding directly." Then execute.
3. AFTER: Run /vde-enforce to verify compliance.
```

This is NOT a description of best practices — it is a mandatory behavioral step that must be executed before every file-modifying action. Skipping the gate is itself a Rule 3 violation.

**Sub-agent refusal protocol:** If a sub-agent receives a task requiring >1 file edit, it MUST respond with:
> "This task requires >1 file edit. Split into a swarm or re-assign."
It must NOT proceed. Expanding scope beyond the assigned file/item is forbidden.

**No exceptions.** "Simple" fixes, "obviously correct" changes, "just a config update" — none of these override the gate. The gate is the spine.

## Sub-Agent Compliance (ALL agents — not just main agent)

Sub-agents (coder, tester, reviewer, scout, debugger, etc.) are bound by the same threshold:

- If a sub-agent receives a task that requires >1 file edit: it MUST report back to the main agent with: **"This task requires >1 file edit. Split into a swarm or re-assign."** It must NOT proceed with multi-file edits.
- Sub-agents must NOT silently expand scope beyond the single file/item assigned to them.
- If a sub-agent discovers additional files need changes during its work, it must STOP and report back rather than editing them directly.
