---
# @forge (Governance Sentinel)
name: vde-review
description: "Runs a full logic and security audit of changed files for the Reviewer side of the Dual Approval gate, covering correctness, UAP DRY and fake-test scans, and SSH, Docker and portability posture."
---
# /vde-review Command (UAP Edition)
<!-- @forge (Governance Sentinel) -->

Full Logic and Security Audit. Enforces the Reviewer side of the Dual Approval gate.

## Usage
/vde-review [files]

## Execution Flow
1.  **Identify Scope**: Diff changes against HEAD.
2.  **Logic Audit**: Reviewer Agent performs deep dive into correctness and performance.
3.  **UAP Audit**: 
    - DRY Audit (Greedy function matching).
    - Fake Test Scan (`assert True`, `pass`, placeholder flags).
4.  **Security Audit**: Verify SSH posture, Docker isolation, and portability.

## Exit Gate (MANDATORY)
Requires **Reviewer: APPROVED** AND **User Approval** to exit Phase 4.