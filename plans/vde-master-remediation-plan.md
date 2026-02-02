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

| Priority | Category | Plans | Est. Scope |
|----------|----------|-------|------------|
| P1 | Security | vde-remediation-plan.md (Stage 1) | 47 tasks, 7 stages |
| P2 | User Bugs | vde-daily-workflow-improvements-plan.md | 2 high-priority fixes |
| P3 | Test Remediation | docker-required-test-remediation-plan.md | 13 tasks, 300+ violations |
| P4 | BDD Gaps | daily-workflow-test-remediation-plan.md | 1274 undefined steps |
| P5 | Code Quality | vde-home-path-consistency-plan.md | Portability improvements |
| P6 | Documentation | vde-codebase-compliance-analysis.md | Analysis only |
| P7 | MCP Config | mcp-*.md (4 files) | Configuration docs |

---

## Execution Roadmap

### Phase 1: Security Hardening (P1)
**Duration:** 1-2 sessions  
**Trigger:** Must complete before any other phases

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 1.1 | Fix eval injection vulnerability | vde-remediation-plan.md:1.1 | None |
| 1.2 | Fix SSH key permissions | vde-remediation-plan.md:1.2 | None |
| 1.3 | Add input sanitization | vde-remediation-plan.md:1.3 | None |
| 1.4 | Complete Stage 1 | vde-remediation-plan.md | 1.1-1.3 |

### Phase 2: User-Facing Bug Fixes (P2)
**Duration:** 1 session  
**Dependencies:** Phase 1 optional

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 2.1 | Fix `vde status` RUNNING display | vde-daily-workflow-improvements-plan.md | None |
| 2.2 | Add service VM SSH config | vde-daily-workflow-improvements-plan.md | None |

### Phase 3: Test Remediation (P3)
**Duration:** 2-3 sessions  
**Dependencies:** Phase 1 complete (for Docker verification helpers)

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 3.1 | Infrastructure & Framework | docker-required-test-remediation-plan.md | Phase 1 |
| 3.2 | Core VM Operations | docker-required-test-remediation-plan.md | 3.1 |
| 3.3 | SSH & Networking | docker-required-test-remediation-plan.md | 3.1 |

### Phase 4: BDD Step Definitions (P4)
**Duration:** 2-3 sessions  
**Dependencies:** Phase 3 partial

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 4.1 | Docker-free undefined steps | daily-workflow-test-remediation-plan.md | None |
| 4.2 | Docker-required undefined steps | daily-workflow-test-remediation-plan.md | Phase 3 |

### Phase 5: Code Quality (P5)
**Duration:** 1 session  
**Dependencies:** None

| Order | Task | Plan Reference | Dependencies |
|-------|------|----------------|--------------|
| 5.1 | $HOME path consistency | vde-home-path-consistency-plan.md | None |

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

- [ ] Zero security vulnerabilities (Stage 1 complete)
- [ ] `vde status` shows RUNNING for active VMs
- [ ] `vde ssh postgres` connects successfully
- [ ] All fake test patterns eliminated
- [ ] BDD undefined steps reduced to <10%
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
