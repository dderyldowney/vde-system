@ssh-access @integration
Feature: VDE SSH Commands
  As a VDE user
  I want to manage SSH through the vde command interface
  So that I have a consistent CLI for all VDE Operations

  @requires-docker-host
  Scenario: Check SSH environment status
    Given I have SSH configured
    When I run VDE command "ssh-setup status"
    Then the VDE command should execute successfully

  @requires-docker-host
  Scenario: Initialize SSH environment
    Given I do not have any SSH keys
    When I run VDE command "ssh-setup init"
    Then the VDE command should execute successfully

  @requires-docker-host
  Scenario: Start VM with SSH update flag
    Given I have SSH configured
    When I run VDE command "start python"
    Then the VDE command should execute successfully

  @requires-docker-host
  Scenario: Full SSH workflow
    Given I do not have any SSH keys
    When I run VDE command "ssh-setup init"
    Then the VDE command should execute successfully
