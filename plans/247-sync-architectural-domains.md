# Plan: Synchronize Hub Labels and Searches with Architectural Domains

This plan outlines the steps to synchronize GitHub labels and documentation searches with the VDE architectural domains: `@armor`, `@forge`, and `@shared-law`.

## Mission
Ensure that the Hub (GitHub) and documentation provide immediate access to strikes categorized by their architectural domain.

## Objectives
1.  **GitHub Label Creation**: Create missing labels `armor`, `forge`, and `shared-law`.
2.  **Documentation Integration**: Add "One-Click Domain Searches" to `docs/GITHUB_LIFECYCLE.md`.
3.  **Architectural Tagging**: Ensure all changes are tagged according to Mandate 24.

## Strike Details
- **Issue**: #247
- **Branch**: `feat/247-sync-architectural-domains`
- **Architectural Tag**: `@forge`

## Execution Steps

### Phase 1: Label Creation (@forge)
- [ ] Create label `armor` (Color: `#006b75`, Description: "The Armor (Project 1): Runtime Engine Product")
- [ ] Create label `forge` (Color: `#5319e7`, Description: "The Forge (Project 2): AI-Governance System")
- [ ] Create label `shared-law` (Color: `#d93f0b`, Description: "Shared-Law: Foundational bridges between Armor and Forge")

### Phase 2: Documentation Update (@forge)
- [ ] Update `docs/GITHUB_LIFECYCLE.md` to include Section 7: One-Click Domain Searches.
- [ ] Add links:
    - armor: `https://github.com/dderyldowney/vde-system/issues?q=is%3Aopen+label%3Aarmor`
    - forge: `https://github.com/dderyldowney/vde-system/issues?q=is%3Aopen+label%3Aforge`
    - shared-law: `https://github.com/dderyldowney/vde-system/issues?q=is%3Aopen+label%3Ashared-law`

### Phase 3: Verification (@forge)
- [ ] Verify labels exist on GitHub using `gh label list`.
- [ ] Verify search links in `docs/GITHUB_LIFECYCLE.md`.
- [ ] Perform Sovereign Startup Ritual to ensure no regressions.

## Tagging Report
| Path | Domain | Functional Effect |
| :--- | :--- | :--- |
| plans/247-sync-architectural-domains.md | @forge | Strike implementation plan. |
| docs/GITHUB_LIFECYCLE.md | @forge | Added architectural domain searches. |
