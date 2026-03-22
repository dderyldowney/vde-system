@parser
Feature: Daily Development Workflow
  As a developer
  I want to manage multiple development environments seamlessly via unified commands
  So that I can switch between projects and languages efficiently

  Scenario: Start my daily development VMs
    Given I am following the documented workflow
    When I parse "start python rust postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "rust"
    And VMs should include "postgres"

  Scenario: Create a new language VM for a project
    Given I am following the documented workflow
    When I parse "create go"
    Then intent should be "create_vm"
    And VMs should include "go"

  Scenario: Start VMs for a project
    Given I am following the documented workflow
    When I parse "start rust"
    Then intent should be "start_vm"
    And VMs should include "rust"

  Scenario: Connect to PostgreSQL from Python VM
    Given I am following the documented workflow
    When I parse "connect to postgresql from python"
    Then intent should be "connect"
    And VMs should include "postgresql"

  Scenario: Stop all VMs at end of day
    Given I am following the documented workflow
    When I parse "stop all"
    Then intent should be "stop_vm"
    And VMs should include all known VMs

  Scenario: Run multiple language VMs for a polyglot project
    Given I am following the documented workflow
    When I parse "start python javascript redis"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "javascript"
    And VMs should include "redis"

  Scenario: Rebuild a VM after modifying its Dockerfile
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And VMs should include "python"
    And rebuild flag should be true

  Scenario: Remove VM I no longer need
    Given I am following the documented workflow
    When I parse "remove ruby"
    Then intent should be "remove_vm"
    And VMs should include "ruby"

  Scenario: Add support for a new language
    Given I am following the documented workflow
    When I parse "add-vm-type foobar"
    Then intent should be "add_vm_type"

  Scenario: Check what VMs I can create
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  Scenario: Check what VMs are running
    Given I am following the documented workflow
    When I parse "what's running"
    Then intent should be "status"

  Scenario: Create test environment with database
    Given I am following the documented workflow
    When I parse "create postgres redis python"
    Then intent should be "create_vm"
    And VMs should include "postgres"
    And VMs should include "redis"
    And VMs should include "python"
