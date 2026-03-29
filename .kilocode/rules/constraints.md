# CRITICAL OPERATING CONSTRAINTS
- Sequential-thinking REQUIRED via `mcp__sequential-thinking__sequentialthinking` | MCP-first: Use MCP services BEFORE internal/local commands
- No code/tests/implementation before Phase 2 (Planning first), mode transitions strict (Phase 1 return permitted per workflow.md violation protocol), no commits before final approval
- **CODE REVIEW MANDATORY**: All code changes MUST be reviewed before commit. See Phase 4 workflow.
- **DRY Principle MANDATORY**: All code and tests must follow DRY. See `.kilocode/rules/dry_requirement.md`
- **Violations:** Phase 1 (no approval)→STOP/return Plan | Phase 2 (beyond plan)→return Phase 1 | Phase 3 (git during audit)→STOP | Phase 4 (no approvals)→STOP | Phase 5 (skip verification)→STOP | No code review→STOP
