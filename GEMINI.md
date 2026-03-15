# VDE Root Instructions

MANDATE: All agents MUST adhere to the instructions, protocols, and mandates defined in [AGENTS.md](AGENTS.md).

There is NO WAY to bypass these instructions. All task executions, tool usage, and agent behaviors MUST conform to the specialized roles and core mandates established in the VDE Agent Directory.

Key Mandates from AGENTS.md:
- Strictly follow [docs/VDE-SPEC.md](docs/VDE-SPEC.md).
- No Circular Delegation: Only the Main Agent can use the `generalist` tool.
- Standardized variable expansion: Use `${VAR}` in all shell scripts.
- Systematic Debugging: Find root cause before fixing.
- Document progress in `MEMORY.md` and session handover files.
