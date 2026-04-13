# VDE CI Pipeline Update Plan - v1.3.0 Sovereign Baseline

## Objective
Resolve the ZSH installation deadlock ("chicken-and-egg") affecting GitHub Actions on the `ubuntu-latest` (Ubuntu 24.04) runners, while simultaneously enforcing the VDE v1.3.0 Sovereign Baseline mandates (specifically Rule A: UAP Enforcement).

## Key Files & Context
- `.github/workflows/vde-ci.yml`: The primary CI pipeline with the global `shell: zsh {0}` default.
- `.github/workflows/paired-update-check.yml`: The secondary workflow that implicitly requires ZSH but currently lacks an explicit installation step.

## Proposed Solution
The global `shell: zsh {0}` configuration in `vde-ci.yml` overrides the shell for all `run` commands. Since `ubuntu-latest` lacks ZSH by default, the command to install ZSH (`sudo apt-get install -y zsh`) fails because GitHub Actions attempts to execute it in the non-existent ZSH shell. 

We will maintain the strict global ZSH default to ensure tests run natively but explicitly override the shell to `bash` strictly for the setup steps that install dependencies. Furthermore, to adhere to the v1.3.0 Sovereign Mandate, we will integrate `bin/vde-enforce-uap.zsh` as a mandatory validation gate before executing actual test payloads.

## Implementation Steps

### 1. Fix `vde-ci.yml` (ZSH Deadlock)
Update the `Install dependencies` (or `Install linting tools` / `Install zsh`) steps across all 8 jobs in `vde-ci.yml`:
- `lint`
- `unit-tests`
- `integration-tests`
- `comprehensive-tests`
- `coverage`
- `docker-build`
- `bdd-tests`
- `summary`

**Change:**
```yaml
      - name: Install dependencies
        shell: bash  # Explicitly override the global ZSH default to bootstrap the environment
        run: sudo apt-get update && sudo apt-get install -y zsh
```

### 2. Enforce v1.3.0 Sovereign Audit (Rule A)
Insert a mandatory "Sovereign Audit" step into the primary verification jobs (`lint`, `unit-tests`, `integration-tests`, `comprehensive-tests`, `bdd-tests`) immediately after installing ZSH:
```yaml
      - name: Sovereign Audit (Rule A)
        shell: zsh {0}
        run: bin/vde-enforce-uap.zsh
```

### 3. Fix `paired-update-check.yml`
Ensure this workflow explicitly installs ZSH using `bash` before attempting to execute the `paired_update_enforcer` ZSH script:
```yaml
      - name: Install dependencies
        shell: bash
        run: sudo apt-get update && sudo apt-get install -y zsh
```

## Verification & Testing
1. Syntax-check the modified YAML files.
2. Confirm the `shell: bash` override functions correctly and does not break subsequent `shell: zsh {0}` inheritance.
3. Validate that the Action successfully completes a run by pushing to a test branch if possible, or directly monitoring the subsequent pipeline run.