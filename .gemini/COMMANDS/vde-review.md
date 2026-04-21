# /vde-review Command (UAP Edition)
<!-- @forge (Agent Logic) -->

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