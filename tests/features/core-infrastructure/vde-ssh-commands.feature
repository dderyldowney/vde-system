@ssh-access @integration
Feature: VDE SSH Commands
  As a VDE user
  I want to manage SSH through the vde command interface
  So that I have a consistent CLI for all VDE Operations

  @requires-docker-host
  Scenario: Check SSH environment status
    Given VDE SSH environment is initialized
    When I run "vde ssh-setup status"
    Then the command should succeed

  @requires-docker-host
  Scenario: Initialize SSH environment
    Given VDE SSH environment is not initialized
    When I run "vde ssh-setup init"
    Then the command should succeed

  @requires-docker-host
  Scenario: Start VM with SSH update flag
    Given VDE SSH environment is initialized
    When I run "vde start python"
    Then the command should succeed

  @requires-docker-host
  Scenario: Full SSH workflow
    Given VDE SSH environment is not initialized
    When I run "vde ssh-setup init"
    Then the command should succeed
