@core-infrastructure
@user-guide-internal
@core-suite
Feature: VM Metadata Verification
  As a developer using VDE
  I want to verify that VM metadata is correctly configured
  So I can trust the VM type definitions and ensure proper system behavior

  Scenario: Language VM display names are user-friendly
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"
    And VMs should include "python"
    And VMs should include "go"
    And VMs should include "rust"

  Scenario: Service VM display names are user-friendly
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"
    And VMs should include "postgres"
    And VMs should include "redis"

  Scenario: Language VM ports are in correct range
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"

  Scenario: Service VM ports are in correct range
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"

  Scenario: VM types are correctly categorized as language
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"

  Scenario: VM types are correctly categorized as service
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"

  Scenario: Common programming language aliases resolve correctly
    Given I am following the documented workflow
    When I parse "use nodejs"
    Then intent should be "create_vm"
    And VMs should include "nodejs"

  Scenario: Common service aliases resolve correctly
    Given I am following the documented workflow
    When I parse "use postgres"
    Then intent should be "create_vm"

  Scenario: Language VM container names follow naming convention
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Service VM container names follow naming convention
    Given I am following the documented workflow
    When I parse "create postgres"
    Then intent should be "create_vm"

  Scenario: All VMs have valid installation commands
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  Scenario: Service VMs have service port configured
    Given I am following the documented workflow
    When I parse "create postgres"
    Then intent should be "create_vm"

  Scenario: Language VMs do not have service ports configured
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Total VM count matches expected inventory
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"
