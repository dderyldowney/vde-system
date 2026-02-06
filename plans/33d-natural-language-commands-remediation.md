# Plan 33d: Natural Language Commands Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Priority**: HIGH (Tier 2)  
**Created**: 2026-02-06  
**Status**: Not Started

---

## Overview

This plan addresses the Natural Language Commands feature, which enables users to interact with VDE using conversational commands. The vde-parser library translates natural language into structured commands.

**Feature File**: `tests/features/docker-required/natural-language-commands.feature`

---

## Current State

### Statistics
- **Total Scenarios**: 15
- **Undefined Steps**: ~35
- **Current Pass Rate**: 0% (all scenarios untested)
- **Target Pass Rate**: ≥80% (12/15 scenarios)

### Key Areas
- Intent detection (list, create, start, stop, restart, status, connect, help)
- VM name extraction from natural language
- Multiple VM handling
- Rebuild and no-cache flags
- Alias resolution
- Command execution
- Error handling for ambiguous input

---

## Phase 3: Implementation Iterations

### Iteration 1: Basic Intent Detection (5 scenarios)
**Steps**: ~10 - Intent parsing, basic commands

### Iteration 2: VM Name Extraction (4 scenarios)
**Steps**: ~8 - Entity extraction, VM identification

### Iteration 3: Advanced Parsing (3 scenarios)
**Steps**: ~8 - Multiple VMs, flags, aliases

### Iteration 4: Error Handling (3 scenarios)
**Steps**: ~9 - Ambiguous input, suggestions

---

## Estimated Effort

**Total**: 5-7 hours

---

## Dependencies

- **Required**: vde-parser library
- **Related**: Plans 33a (Docker Operations), 33c (Daily Workflow)

---

## References

- [VDE Parser Technical Deep Dive](../docs/VDE-PARSER-Technical-Deep-Dive.md)
- [VDE Parser Library](../scripts/lib/vde-parser)
