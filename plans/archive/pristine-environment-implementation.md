# Pristine Testing Environment Implementation Plan
<!-- @shared-law (Forge Component) -->

## Objective
Ensure the testing environment is absolutely clean and pristine before and after the execution of the `proof-of-life-the-contract.feature` test suite, without disrupting the sequential dependencies between scenarios.

## Key Files & Context
- `tests/features/core-infrastructure/proof-of-life-the-contract.feature`: The BDD feature file that requires a pristine environment.
- `tests/features/environment.py`: Behave environment hooks where feature-level setup and teardown logic resides.
- `bin/vde-tactical-sweep.zsh` (New File): A new standalone ZSH script responsible for executing the comprehensive cleanup.

## Implementation Steps

1. **Create the Tactical Sweep Script (`bin/vde-tactical-sweep.zsh`)**:
   - Write a new ZSH script adhering to the Universal Agent Protocol (UAP).
   - The script will forcefully remove all containers matching the `vde-*` naming convention.
   - The script will forcefully remove all lock files in `.locks/vms/` and port registries in `.cache/port-registry/`.
   - Ensure the script is executable (`chmod +x`).

2. **Update the Behave Environment (`tests/features/environment.py`)**:
   - Implement the `before_feature` and `after_feature` hooks.
   - Add logic within these hooks to check for the presence of a `@pristine` tag on the executing feature.
   - If the tag is present, execute the `bin/vde-tactical-sweep.zsh` script.

3. **Tag the Feature File (`tests/features/core-infrastructure/proof-of-life-the-contract.feature`)**:
   - Add the `@pristine` tag to the feature file, alongside the existing `@system-spine` tag.

## Verification & Testing
- Execute `bin/vde-enforce-uap.zsh behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`.
- Observe the test output to confirm that the `before_feature` tactical sweep executes successfully prior to Scenario 1.
- Confirm that the `after_feature` tactical sweep executes successfully after Scenario 6.
- Ensure the total execution time and results demonstrate a 100% Green status.