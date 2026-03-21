@core-infrastructure
@user-guide-starting-stopping
@core-suite
Feature: VM Lifecycle Management
  As a developer using VDE
  I want to manage the complete lifecycle of my VMs via conversational commands
  So I can create, configure, start, stop, and destroy VMs as needed

  Scenario: Creating a new VM
    Given I am following the documented workflow
    When I parse "create rust"
    Then intent should be "create_vm"
    And VMs should include "rust"

  Scenario: Creating multiple VMs at once
    Given I am following the documented workflow
    When I parse "create python postgresql redis"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "postgresql"
    And VMs should include "redis"

  Scenario: Starting a created VM
    Given I am following the documented workflow
    When I parse "start go"
    Then intent should be "start_vm"
    And VMs should include "go"

  Scenario: Starting multiple VMs
    Given I am following the documented workflow
    When I parse "start python go postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "go"
    And VMs should include "postgres"

  Scenario: Checking VM status
    Given I am following the documented workflow
    When I parse "what's running"
    Then intent should be "status"

  Scenario: Stopping a running VM
    Given I am following the documented workflow
    When I parse "stop python"
    Then intent should be "stop_vm"
    And VMs should include "python"

  Scenario: Stopping multiple VMs
    Given I am following the documented workflow
    When I parse "stop python and postgres"
    Then intent should be "stop_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  Scenario: Restarting a VM
    Given I am following the documented workflow
    When I parse "restart rust"
    Then intent should be "restart_vm"
    And VMs should include "rust"

  Scenario: Restarting with rebuild
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And VMs should include "python"
    And rebuild flag should be true

  Scenario: Removing a VM instance
    Given I am following the documented workflow
    When I parse "remove ruby"
    Then intent should be "remove_vm"
    And VMs should include "ruby"

  Scenario: Rebuilding after code changes
    Given I am following the documented workflow
    When I parse "rebuild go from scratch"
    Then intent should be "restart_vm"
    And VMs should include "go"
    And nocache flag should be true

  Scenario: Upgrading a VM
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And VMs should include "python"

  Scenario: Migrating to a new VDE version
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And VMs should include "python"
