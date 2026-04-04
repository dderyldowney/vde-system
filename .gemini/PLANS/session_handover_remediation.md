# Remediation Plan: Docker Feature Stack

## High-Priority Architectural Debt
- **vde-info speedup**: Performs multiple `docker inspect` calls. Should cache these labels in `.docker-state/*.json` during startup/refresh.

## Remediation Goals
- **Deterministic Readiness**: Replace arbitrary `sleep` calls in health checks and BDD steps with deterministic polling and event-driven readiness detection.
- **100% Coverage**: Complete the implementation of the 366 undefined steps to ensure 100% documentation-to-code parity.
See ./session_handover.md
