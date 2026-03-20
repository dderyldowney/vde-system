@core-infrastructure
@user-guide-daily-workflow
@core-suite
Feature: Daily Development Workflow
  As a developer using VDE
  I want to manage my development containers efficiently via unified commands
  So I can focus on coding without managing infrastructure

  Scenario: Starting my development environment
    Given I am following the documented workflow
    When I parse "start python"
    Then intent should be "start_vm"
    And VMs should include "python"

  Scenario: Checking what's currently running
    Given I am following the documented workflow
    When I parse "what's running"
    Then intent should be "status"

  Scenario: Getting connection information for a VM
    Given I am following the documented workflow
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  Scenario: Stopping work for the day
    Given I am following the documented workflow
    When I parse "stop everything"
    Then intent should be "stop_vm"

  Scenario: Restarting a VM with rebuild
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And VMs should include "python"
    And rebuild flag should be true

  Scenario: Starting multiple VMs at once
    Given I am following the documented workflow
    When I parse "start python and postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  Scenario: Creating a new VM for the first time
    Given I am following the documented workflow
    When I parse "create go"
    Then intent should be "create_vm"
    And VMs should include "go"
