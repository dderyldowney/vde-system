# language: en
@vm-lifecycle @requires-docker-host @integration
Feature: VM Lifecycle Management
  As a developer
  I want to create, start, stop, and manage development VMs via the vde command
  So that I can work in isolated development environments

  VDE uses a data-driven approach where VM types are defined in data/vm-types.conf.
  On first use, VDE auto-generates docker-compose.yml from templates.
  The workflow is: start -> builds image if needed -> creates container -> starts it.

  @user-guide-first-vm
  Scenario: Start an existing language VM
    Given VM "python" is not running
    When I run VDE command "start python"
    Then VM "python" should be running

  @user-guide-first-vm
  Scenario: Start a language VM (first use - builds image)
    Given VM "python" is not created
    When I run VDE command "start python"
    Then VM "python" should be running
    And Docker image should be built

  @user-guide-cluster
  Scenario: Start multiple VMs
    Given VM "python" is not running
    And VM "rust" is not running
    When I run VDE command "start python rust"
    Then VM "python" should be running
    And VM "rust" should be running

  @user-guide-daily-workflow
  Scenario: Start all VMs
    Given VM "python" is not running
    And VM "postgres" is not running
    When I run VDE command "start all"
    Then VM "python" should be running
    And VM "postgres" should be running

  @user-guide-starting-stopping
  Scenario: Stop a running VM
    Given VM "python" is running
    When I run VDE command "stop python"
    Then VM "python" should not be running

  @user-guide-starting-stopping
  Scenario: Stop all running VMs
    Given VM "python" is running
    And VM "rust" is running
    When I run VDE command "stop all"
    Then no VMs should be running

  @user-guide-starting-stopping
  Scenario: Restart a VM
    Given VM "python" is running
    When I run VDE command "restart python"
    Then VM "python" should be running
    And the VM should have a fresh container instance

  Scenario: Rebuild VM with --rebuild flag
    Given VM "python" is running
    When I run VDE command "start python --rebuild"
    Then VM "python" should be running
    And Docker image should be rebuilt

  Scenario: Rebuild without cache using --no-cache
    Given VM "python" is running
    When I run VDE command "start python --no-cache"
    Then VM "python" should be running

  Scenario: Cannot start unknown VM
    Given VM "nonexistent" is not known
    When I run VDE command "start nonexistent"
    Then the command should fail with error "Unknown VM"

  Scenario: Remove a VM container (config preserved)
    Given VM "python" is running
    When I run VDE command "remove python"
    Then VM "python" should not be running
    But VM configuration should still exist

  @parser
  Scenario: List all predefined VM types
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  @parser
  Scenario: List only language VMs
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"
    And filter should be "lang"

  @parser
  Scenario: List only service VMs
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"
    And filter should be "svc"

  @parser
  Scenario: Add a new VM type
    Given I am following the documented workflow
    When I parse "vde add mylang"
    Then intent should be "add_vm_type"
