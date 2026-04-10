# Plan: Empirical Proof for the Tetrad of the Forge (The Law of Protection)

**Goal:** Formally codify and execute empirical BDD tests in `tests/features/core-infrastructure/system-spine.feature` to prove the four base technologies (Docker, Git, Zsh, SSH) are fully functional on the Hub, as mandated by Section 16: "The Law of Protection — The Unyielding Tetrad".

## Analysis
The updated `.gemini/instructions.md` explicitly provides the Gherkin scenarios required to prove the `@system-spine` tetrad is functional on the VDE Hub. These tests are the "Immutable Gatekeeper" and must pass with 0 return codes.

## Proposed Changes
Append the following specific scenarios to `tests/features/core-infrastructure/system-spine.feature` (and implement any missing step definitions in Python):

```gherkin
  @law-of-protection @zsh
  Scenario: Pillar I - The Voice of the Tribe (Zsh)
    Given the Hub is active
    When I execute "zsh --version"
    Then the output should contain "zsh 5."
    And the return code should be 0

  @law-of-protection @git
  Scenario: Pillar II - The Chronicler's Record (Git)
    Given a temporary workspace in "plans/scripts/git-test"
    When I execute "git init" in the workspace
    Then the directory ".git" should exist
    And the return code should be 0

  @law-of-protection @docker
  Scenario: Pillar III - The World-Forge (Docker)
    Given the Docker daemon is responsive
    When I run a diagnostic probe with "docker run --rm alpine echo 'Forge Active'"
    Then the output should contain "Forge Active"
    And the return code should be 0

  @law-of-protection @ssh
  Scenario: Pillar IV - The Transversal Bridge (SSH)
    Given the "vde_student" identity exists at "~/.ssh/vde/"
    When the SSH agent is active on the Hub
    And I execute "ssh-add -l"
    Then the output should contain "vde_student"
    And the return code should be 0
```

### Execution Strategy
1. **Append Scenarios:** Add the scenarios above to the end of `tests/features/core-infrastructure/system-spine.feature`.
2. **Implement Steps:** Add the necessary step definitions to `tests/features/steps/system_spine_steps.py` (e.g., `Given the Hub is active`, `When I execute "{cmd}" in the workspace`, `Then the return code should be {code}`).
3. **Run Suite:** Execute `bin/vde-enforce-uap.zsh` followed by `behave tests/features/core-infrastructure/system-spine.feature` to prove the Tetrad is unyielding.

## Verification
- The test suite must report 100% GREEN for the new scenarios, empirically proving the Hub's base technologies are functional and protected.