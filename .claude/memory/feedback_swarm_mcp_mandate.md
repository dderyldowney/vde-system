---
name: Swarm+MCP mandatory for multi-step batches
description: Any fix/refactor batch exceeding 1 step must use parallel sub-agent swarm with sequential-thinking MCP — main agent synthesizes only
type: feedback
---

Multi-step batches (>1 step) MUST use parallel sub-agent swarm with sequential-thinking MCP for planning. Main agent must not apply edits directly.

**Why:** VIOLATION-1 on 2026-03-28 — 10 bug/fake-test fixes applied directly via Edit tool calls in the main agent with no sub-agents or MCP. Rule Enforcer caught this. Process debt logged in `plans/session_handover_remediation.md`. Correctness was fine but the swarm+MCP rule is non-negotiable regardless of outcome.

**How to apply:** Before any fix batch of >1 item: spawn parallel sub-agents (yume-implementer or coder), use sequential-thinking MCP for planning, main agent only synthesizes results. No exceptions even for "simple" fixes.
