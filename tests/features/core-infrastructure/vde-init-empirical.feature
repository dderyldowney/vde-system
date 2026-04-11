@system-spine
Feature: The Sovereign Initialization Ritual (vde init)
  As an Alor of the VDE
  I require a deterministic initialization ritual
  So that the Beskar Hub can be hydrated from a naked state

  Background: The Environment is Naked
    # We simulate a "naked" state by ensuring certain artifacts are missing
    # But we must be careful not to destroy the actual VDE setup if running on a dev machine.
    # For this empirical proof, we verify that running 'vde init' ensures their existence.
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    And the Hub is synchronized to version 1.2.3

  Scenario: Physical Hydration of the Hub
    When I execute "bin/vde init"
    Then the output should contain "Initializing VDE infrastructure"
    And the command should succeed
    And the directory ".cache" should exist
    And the directory "projects" should exist
    And the directory "data" should exist
    And the file "VDE_INSTALL.md" should exist
    And the VDE_SSH_DIR should contain the "vde_student" identity
    And the Docker network "vde-net" should exist
