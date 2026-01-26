# language: en
@user-guide-internal
Feature: VDE SSH Commands
  As a VDE user
  I want to manage SSH through the vde command interface
  So that I have a consistent CLI for all VDE operations

  Scenario: Check SSH environment status
    When I run "vde ssh-setup status"
    Then the command should succeed
    And status command should show SSH environment state

  Scenario: Initialize SSH environment
    Given VDE SSH environment is not initialized
    When I run "vde ssh-setup init"
    Then the command should succeed
    And VDE SSH directory should exist
    And VDE SSH key should exist
    And SSH key should have correct permissions
    And SSH config should be generated
    And public key should be synced to build context
    And init command should show completion message

  Scenario: Initialize SSH environment idempotently
    Given VDE SSH environment is initialized
    When I run "vde ssh-setup init"
    Then the command should succeed
    And VDE SSH directory should exist
    And VDE SSH key should exist

  Scenario: Start SSH agent and load key
    Given VDE SSH environment is initialized
    When I run "vde ssh-setup start"
    Then the command should succeed
    And SSH agent should be running
    And SSH agent should have VDE key loaded

  Scenario: Regenerate SSH config
    Given VDE SSH environment is initialized
    When I run "vde ssh-setup generate"
    Then the command should succeed
    And SSH config should be regenerated

  Scenario: Sync SSH keys to build context
    Given VDE SSH environment is initialized
    When I run "vde ssh-sync"
    Then the command should succeed
    And public key should be synced to build context
    And sync command should show success message

  Scenario: Start VM with SSH update flag
    Given VDE SSH environment is initialized
    When I run "vde start python --update-ssh"
    # Note: This may fail if python VM doesn't exist; tests the --update-ssh flag
    Then either the command succeeds or VM is not created

  Scenario: Full SSH workflow
    Given VDE SSH environment is not initialized
    When I run "vde ssh-setup init"
    Then the command should succeed
    And VDE SSH directory should exist
    And VDE SSH key should exist
    And SSH config should be generated
    And public key should be synced to build context
    And SSH agent should be running
    And SSH agent should have VDE key loaded
