Feature: System Spine Integrity

  @spine @critical-path
  Scenario: Hub-to-Spoke Deterministic Ignition
    Given the VDE Hub "data/vm-types.conf" is the sole authority
    And the VDE Registry "data/vm-types.json" is synchronized with the Hub
    When I run the one true way to start "python"
    Then a VM-level lock should be created during ignition
    And the container "vde-python" should be started via direct Docker orchestration
    And the container should have been hydrated by "scripts/setup/python-init.zsh"
    And the SSH port should be atomically allocated and recorded in the registry
    And I should be able to SSH into "vde-python" and verify the environment

  Scenario: Full Language and Service Matrix Verification
    Given the VDE system is healthy
    Then every VM defined in the Hub must have a corresponding USP init script
    And every VM must be startable via the VDE orchestrator
    And every VM must adhere to the 8-field registry standard

  Scenario: VM Lifecycle Termination (Stop/Remove)
    Given the VDE Registry is loaded
    And "vde-python" is currently running
    When I run the one true way to stop "python"
    Then the container "vde-python" should be stopped
    And the VM-level lock should be released
    When I run the one true way to remove "python"
    Then the container "vde-python" should be destroyed
    And the SSH configuration should be preserved
