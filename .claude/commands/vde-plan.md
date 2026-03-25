Plan a VDE feature or fix using the 5-phase workflow.

## Usage
/vde-plan $ARGUMENTS

## Execution

**Phase 0: Context Gathering (Swarm — spawn simultaneously)**

- Scout agent: explore codebase for related code, patterns, existing functions relevant to `$ARGUMENTS`
- Memory MCP: query cross-session context for `$ARGUMENTS`
- sequential-thinking MCP: analyze `$ARGUMENTS` against VDE-SPEC.md requirements

**Phase 1: Plan Construction**

Using swarm results:
1. Read `docs/VDE-SPEC.md` sections relevant to `$ARGUMENTS`
2. Identify all files that must change
3. DRY analysis: find existing functions to extend vs. new ones needed (check `lib/`, `tests/features/steps/`)
4. Port range check if adding a VM (language: 2200-2299, service: 2400-2499, check `data/vm-types.json`)
5. List BDD test scenarios required (feature file + step definitions)
6. Identify minimal test command to verify the change (isolate first)

**Output Format**

```
PLAN: <title>
SPEC REF: <docs/VDE-SPEC.md section>
FILES TO CHANGE:
  - <path> — <what changes>
DRY ANALYSIS: <existing functions to reuse or extend>
NEW FUNCTIONS: <parameterized signatures — no near-duplicates>
TEST PLAN:
  - Isolate: <specific feature file>
  - Verify: <exact behave command>
  - Full suite: only at final verification
ESTIMATED SCOPE: <lines changed>
```

**HARD STOP**: Present plan and wait for explicit user approval before any code changes.
