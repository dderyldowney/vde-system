@core-suite
@user-guide-understanding
Feature: VM Information and Discovery
  As a developer using VDE
  I want to discover what VMs are available and get information about them
  So I can make informed decisions about my development environment

  Scenario: Listing all available VMs
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  Scenario: Listing only language VMs
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"
    And filter should be "lang"

  Scenario: Listing only service VMs
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"
    And filter should be "svc"

  Scenario: Getting detailed information about a specific VM
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Checking if a VM exists
    Given I am following the documented workflow
    When I parse "create golang"
    Then intent should be "create_vm"

  Scenario: Discovering VMs by alias
    Given I am following the documented workflow
    When I parse "use nodejs"
    Then intent should be "create_vm"

  Scenario: Understanding VM categories
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"
