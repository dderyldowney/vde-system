# Implementation Plan: Phase 21 - Cluster Persistence

## Objective
Implement a multi-VM "cluster" management system that allows users to group VMs, save the grouping, and perform lifecycle operations (start/stop) on the entire group as a single unit.

## Proposed Solution
(see original design in temporary path)

## Implementation Steps

### Phase 1: Infrastructure
1. [COMPLETE] Create `bin/vde-cluster` stub.
2. [COMPLETE] Update `bin/vde` command registry.
3. [COMPLETE] Update `AGENTS.md` and `MEMORY.md` to reflect Phase 21 start.

### Phase 2: Core Logic
1. [COMPLETE] Implement `vde_cluster_save` and `vde_cluster_load` in `lib/vde-docker-state` or a new `lib/vde-cluster-utils`.
2. [COMPLETE] Implement actions in `bin/vde-cluster`.

### Phase 3: NLP & BDD
1. [COMPLETE] Add cluster intent to `lib/vde-parser`.
2. [COMPLETE] Create `tests/features/docker-required/cluster-persistence.feature`.
3. [COMPLETE] Implement step definitions in `tests/features/steps/cluster_steps.py`.

## Verification & Testing
- **Unit Tests:** [COMPLETE] Verify JSON serialization/deserialization.
- **BDD Tests:** 
  - [COMPLETE] Scenario: Saving a cluster named "web-app" with python and redis.
  - [COMPLETE] Scenario: Starting the "web-app" cluster.
  - [COMPLETE] Scenario: Listing saved clusters.
- **Manual Verification:** [COMPLETE] Confirm `.docker-state/clusters/` contains correct data.

---
**STATUS: 100% COMPLETE & AUDITED**
