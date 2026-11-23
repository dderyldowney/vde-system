---
# @forge (Governance Sentinel)
name: vde-spec
description: "Compare implementation against docs/governance/vde-spec.md to find gaps and violations. Takes a section name, feature name, or full for a complete audit."
---
# VDE-SPEC
<!-- @forge (Governance Sentinel) -->

> **Security (binding):** every action here is bound by [.gemini/RULES/security-preamble.md](../RULES/security-preamble.md). NO AID TO THE ENEMY: nothing public about unfixed weaknesses; when unsure, keep it private.

Compare implementation against docs/governance/vde-spec.md — find gaps and violations.

## Usage
/vde-spec $ARGUMENTS

`$ARGUMENTS` = section name, feature name, or `full` for complete audit.

## Execution

**Step 1: Load Spec Context**

Read `docs/governance/vde-spec.md`. Focus on `$ARGUMENTS` section if specified; otherwise audit all sections.

**Step 2: Compliance Swarm (spawn simultaneously per spec section)**

- Agent A: Extract required function signatures, behaviors, error codes from spec section
- Agent B: Grep `lib/` for matching implementations → compare signatures against spec
- Agent C: Grep `tests/features/` → verify each spec requirement has a test scenario

**Step 3: Gap Classification**

For each spec requirement:
- **IMPLEMENTED + TESTED** — compliant
- **IMPLEMENTED, NO TEST** — gap (add test)
- **SPEC-ONLY** — not implemented (flag for planning)
- **IMPLEMENTATION DIFFERS** — violation (fix code OR request spec update with user auth)

**Step 4: Report**

```
SPEC VERSION: <from docs/governance/vde-spec.md header>
SCOPE: <section audited>

COMPLIANT: <N requirements>
GAPS (no test): <list>
MISSING (not implemented): <list>
VIOLATIONS (differs from spec): <list with file:line>

RECOMMENDATION: <prioritized action list>
```

NOTE: Spec modifications require explicit user authorization. Report gaps; do not silently change docs/governance/vde-spec.md.