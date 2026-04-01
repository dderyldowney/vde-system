# VDE Root Instructions

MANDATE: All agents (Gemini, Claude, Kilo, etc.) MUST adhere to the **VDE Universal Agent Protocol (UAP)** defined in [AGENTS.md](AGENTS.md).

There is NO WAY to bypass these instructions. All task executions, tool usage, and agent behaviors MUST conform to the Phase 0-5 lifecycle, Swarm Orchestration, and core quality mandates (TDD, DRY, Audit) established in the UAP.

Key Mandates from AGENTS.md:
- Strictly follow [docs/VDE-SPEC.md](docs/VDE-SPEC.md).
- MCP-First: Use MCP services before local or internal tools.
- Pre-Edit Gate: Touch only 1 file at a time; >1 requires a swarm.
- Dual Approval Gate: Reviewer AND User approval required before commit.
- No Circular Delegation: Sub-agents cannot spawn other agents.
- Systematic Debugging: Find root cause before fixing.
- Document progress in `MEMORY.md` and session handover files.
