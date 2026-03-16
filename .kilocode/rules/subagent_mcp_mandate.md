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

## Standing Rule

**IF you are about to execute a task directly, STOP and ask: "Can I delegate this to a sub-agent or MCP service?"**

If the answer is YES, you MUST delegate.
