# VDE Master Remediation Plan

**Created:** 2026-02-02  
**Status:** Active  
**Scope:** All pending remediation plans

---

## Executive Summary

This is an umbrella plan that coordinates all pending remediation efforts for the VDE project. It organizes work by priority, manages dependencies, and provides a unified execution roadmap.

### Completed Plans (moved to `plans/completed/`)
- docker-free-undefined-steps-remediation-plan.md
- docker-free-test-failures-remediation-plan.md
- ssh-agent-test-remediation-plan.md
- vde-parser-test-remediation-plan.md
- ssh-vm-to-host-steps-implementation-plan.md
- zsh-rename-plan.md
- docker-required-test-remediation-tracking.md

---

## Master Priority Matrix

| Priority | Category | Plans | Status | Est. Scope |
|----------|----------|-------|--------|------------|
| P1 | **COMPLETED** | vde-remediation-plan.md (Stage 1) | ✅ Done | 5 security tasks |
| P2 | **COMPLETED** | vde-remediation-plan.md (Stage 2) | ✅ Done | 5 code quality tasks |
| P3 | User Bugs | vde-daily-workflow-improvements-plan.md | ✅ Done | 2 high-priority fixes |
| P4 | Test Remediation | docker-required-test-remediation-plan.md | ✅ Done | 13 tasks, 300+ violations |
| P5 | BDD Gaps | daily-workflow-test-remediation-plan.md | ⏳ In Progress | ~129 steps (deferred) |
| P6 | Code Quality | vde-home-path-consistency-plan.md | Pending | Portability improvements |
| P7 | Documentation | vde-codebase-compliance-analysis.md | Pending | Analysis only |
| P8 | MCP Config | mcp-*.md (4 files) | Pending | Configuration docs |

---

## Execution Roadmap

### Phase 1: Security Hardening (P1) - ✅ COMPLETED
**Duration:** Already implemented

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 1.1 | Fix eval injection vulnerability | vde-remediation-plan.md:1.1 | ✅ Done |
| 1.2 | Fix SSH key permissions | vde-remediation-plan.md:1.2 | ✅ Done |
| 1.3 | Add input sanitization | vde-remediation-plan.md:1.3 | ✅ Done |
| 1.4 | Fix port race condition | vde-remediation-plan.md:1.4 | ✅ Done |
| 1.5 | Fix SSH config race condition | vde-remediation-plan.md:1.5 | ✅ Done |

### Phase 2: Code Quality (P2) - ✅ COMPLETED
**Duration:** Already implemented

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 2.1 | Remove duplicate code | vde-remediation-plan.md:2.1 | ✅ Done |
| 2.2 | Standardize return codes | vde-remediation-plan.md:2.2 | ✅ Done |
| 2.3 | Replace magic numbers | vde-remediation-plan.md:2.3 | ✅ Done |
| 2.4 | Docker error handling | vde-remediation-plan.md:2.4 | ✅ Done |
| 2.5 | Test suite | vde-remediation-plan.md:2.5 | ✅ Done |

### Phase 3: User-Facing Bugs (P3) - COMPLETED

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 3.1 | Fix `vde status` RUNNING display | vde-daily-workflow-improvements-plan.md | ✅ Done |
| 3.2 | Add service VM SSH config | vde-daily-workflow-improvements-plan.md | ✅ Done |

### Phase 3: Test Remediation (P3) - COMPLETED
**Duration:** 2-3 sessions  
**Dependencies:** Phase 1 complete (for Docker verification helpers)

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 3.1 | Infrastructure & Framework | docker-required-test-remediation-plan.md | ✅ Done |
| 3.2 | Core VM Operations | docker-required-test-remediation-plan.md | ✅ Done |
| 3.3 | SSH & Networking | docker-required-test-remediation-plan.md | ✅ Done |

### Phase 4: BDD Step Definitions (P4) - IN PROGRESS
**Duration:** 2-3 sessions  
**Dependencies:** Phase 3 partial

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 4.1 | Docker-free undefined steps | docker-free-undefined-steps-remediation-plan.md | ✅ Done |
| 4.2 | VDE-Parser BDD Tests | daily-workflow-test-remediation-plan.md | ✅ Done |
| 4.3 | Docker-required undefined steps | daily-workflow-test-remediation-plan.md | ⏳ Deferred |

### Phase 5: Code Quality (P5)
**Duration:** 1 session  
**Dependencies:** None

| Order | Task | Plan Reference | Status |
|-------|------|----------------|--------|
| 5.1 | $HOME path consistency | vde-home-path-consistency-plan.md | ✅ Done |

### Phase 6: Documentation (P6)
**Duration:** Review only  
**Dependencies:** None

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 6.1 | Review compliance analysis | vde-codebase-compliance-analysis.md | None |

### Phase 7: MCP Configuration (P7)
**Duration:** 1 session  
**Dependencies:** None

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 7.1 | Configure MCP services | mcp-implementation-plan.md | None |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Security vulnerabilities | Critical | Phase 1 addresses all Stage 1 issues |
| Test coverage gaps | High | Phases 3 & 4 address 300+ violations |
| User experience issues | High | Phase 2 fixes critical user bugs |
| Scope creep | Medium | Strict adherence to plan scope |
| Dependencies | Medium | Phases ordered to minimize blocks |

---

## Success Criteria

- [x] Zero security vulnerabilities (Stage 1 complete)
- [x] `vde status` shows RUNNING for active VMs
- [x] `vde ssh postgres` connects successfully
- [x] All fake test patterns eliminated (BDD steps)
- [x] BDD undefined steps reduced to 0 (docker-free)
- [ ] Docker-required BDD steps (~129 undefined) - Deferred
- [ ] All tests passing (unit, integration, BDD)

---

## Related Plans

### Completed (in `plans/completed/`)
- docker-free-undefined-steps-remediation-plan.md
- docker-free-test-failures-remediation-plan.md
- ssh-agent-test-remediation-plan.md
- vde-parser-test-remediation-plan.md
- ssh-vm-to-host-steps-implementation-plan.md
- zsh-rename-plan.md
- docker-required-test-remediation-tracking.md

### Pending (in `plans/`)
- vde-remediation-plan.md
- vde-daily-workflow-improvements-plan.md
- docker-required-test-remediation-plan.md
- daily-workflow-test-remediation-plan.md
- vde-home-path-consistency-plan.md
- vde-codebase-compliance-analysis.md
- mcp-architecture-overview.md
- mcp-config-samples.md
- mcp-implementation-plan.md
- mcp-server-analysis.md
