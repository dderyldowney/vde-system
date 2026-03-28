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
| Fix/edit batch | >3 items OR >3 file edits | MANDATORY swarm — spawn coder agents |

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
| How many files will I edit? | >3 files | Spawn implementation swarm |
| How many independent fix items? | >3 items | Spawn parallel coder agents |
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

## Standing Rule — Hard Stop

**BEFORE making your 4th direct Edit, Write, or Bash call in a single task batch: STOP.**

Ask yourself:
1. How many items am I about to fix/change?
2. If the answer is >3 → you MUST spawn a sub-agent swarm NOW instead of continuing directly.

Applying 4 or more direct edits in a single batch without spawning a swarm is a Rule 3 violation.
The Rule Enforcer will BLOCK this. The check is:

> "Did the main agent make >3 direct file edits for a single task, when a swarm could have been used?"
> If yes → BLOCKED.

There is no exception for "simple fixes" or "obviously correct" changes. Simplicity does not override the rule.
