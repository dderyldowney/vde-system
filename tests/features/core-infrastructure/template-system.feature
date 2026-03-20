@core-infrastructure
@user-guide-internal
@requires-docker-host
Feature: Template System
  As a developer
  I want VM configurations to be generated from templates
  So that new VMs can be created consistently

  Scenario: Render language VM template
    Given I am following the documented workflow
    When I parse "create testlang"
    Then intent should be "create_vm"

  Scenario: Render service VM template
    Given I am following the documented workflow
    When I parse "create testsvc"
    Then intent should be "create_vm"

  Scenario: Template includes SSH agent forwarding
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template includes public keys volume
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template uses correct network
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template sets correct restart policy
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template configures user correctly
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template exposes SSH port
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Template includes install command
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"

  Scenario: Handle missing template gracefully
    Given I am following the documented workflow
    When I parse "create nonexistent"
    Then intent should be "create_vm"
