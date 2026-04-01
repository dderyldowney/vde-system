# /vde-plan Command (UAP Edition)

Plan a VDE feature or fix following the Phase 0-1 UAP mandates.

## Usage
/vde-plan <description>

## Execution Flow

### Phase 0: Discovery (Swarm)
The Main Agent MUST spawn a scout swarm simultaneously to establish ground truth:
- Scout Agent: Explore codebase for DRY reuse opportunities.
- Memory MCP: Query cross-session context.
- sequential-thinking MCP: Analyze requirements against VDE-SPEC.md.

### Phase 1: Plan Construction
Using swarm results, the Planner Agent designs a strategy that includes:
1.  **TDD Plan**: Explicit identification of failing test scenarios.
2.  **DRY Analysis**: List of existing functions to extend vs. new parameterized ones.
3.  **Swarm Config**: Identification of implementation swarm for Phase 2 (if >1 file).

## Exit Gate (MANDATORY)
**HARD STOP**: Present the plan and wait for explicit **User Approval** before proceeding to Phase 2 (Implementation).
