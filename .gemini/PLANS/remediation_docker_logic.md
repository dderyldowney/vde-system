# Remediation Plan: Fraudulent Docker Logic (Audit Alert)

## Issue
An audit of `tests/features/steps/` revealed step definitions using `time.sleep()` to simulate delays instead of deterministically polling Docker events. This violates the "NO SLEEP CALLS" mandate.

## Files Containing Fraudulent Logic (`time.sleep`):
- `tests/features/steps/shell_helpers.py` (L217)
- `tests/features/steps/docker_management_steps.py` (L97)
- `tests/features/steps/ssh_remote_access_steps.py` (L516)
- `tests/features/steps/service_hardening_steps.py` (L74, L96, L117)
- `tests/features/steps/configuration_management_steps.py` (L127, L285)
- `tests/features/steps/vde_maintenance_steps.py` (L64)
- `tests/features/steps/productivity_steps.py` (L210)
- `tests/features/steps/vm_common.py` (L290, L319, L368)

## Files Containing Extraneous `print` Logic:
- `tests/features/steps/configuration_management_steps.py` (L221)
- `tests/features/steps/vm_common.py` (L726, L749, L763, L764, L765)

## Action Plan
1. Refactor all identified files to replace `time.sleep()` with the deterministic polling mechanism (`vde_poll` equivalent in Python or querying `docker events`/`inspect` state).
2. Remove debugging `print()` statements unless strictly part of intended command output simulation.
3. Validate that test execution relies strictly on actual Docker events or deterministic state changes.
