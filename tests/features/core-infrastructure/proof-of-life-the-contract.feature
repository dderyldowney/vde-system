@system-spine
Feature: The Proof of Life - The Contract
  As an Alor of the VDE
  I require empirical proof of the Spoke lifecycle
  So that the fundamental building block of the platform is certified

  Background: The Tetrad is Active
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    And the Hub is synchronized to version 1.2.1

  Scenario: The Sovereign Lifecycle - From Forge to Quench
    # 1. The Forge (Create)
    Given I have a valid VM definition for "python" in the Beskar Registry
    When I execute "bin/vde create python"
    Then the Docker image "vde-python" should exist on the Hub
    And the return code should be 0

    # 2. The Ignition (Start)
    When I execute "bin/vde start python"
    Then a container named "vde-python" should be running
    And the SSH bridge to "python" should be established
    And the return code should be 0

    # 3. The Reinforcement (Rebuild)
    When I execute "bin/vde rebuild python"
    Then the command should succeed
    And the Docker image "vde-python" should exist on the Hub
    And the container "vde-python" should be running
    And the return code should be 0

    # 4. The Handshake (Enter & Shell Execution)
    # Note: We use 'vde enter' to prove orchestration, NOT raw SSH.
    When I execute "bin/vde enter python --command 'echo \"The Contract is Signed\"'"
    Then the output should contain "The Contract is Signed"
    And the command should be executed as the "vde_student" identity
    And the return code should be 0

    # 4. The Quench (Stop)
    When I execute "bin/vde stop python"
    Then the container "vde-python" should not be running
    And the return code should be 0

    # 5. The Dissolution (Remove)
    When I execute "bin/vde rm python"
    Then the container "vde-python" should not exist
    And the return code should be 0

  Scenario: The Forge Hardening - Hardened Rebuild
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    And I have a valid VM definition for "python" in the Beskar Registry
    When I execute "bin/vde rebuild --no-cache python"
    Then the command should succeed
    And the Docker image "vde-python" should exist on the Hub
    And the return code should be 0
