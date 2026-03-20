@core-infrastructure
@user-guide-internal
Feature: VM State Awareness
  As a developer using VDE
  I want the system to be aware of VM states
  So I don't accidentally duplicate operations or cause conflicts

  @requires-docker-host
  Scenario: Starting an already running VM
    Given I am following the documented workflow
    When I parse "start python"
    Then intent should be "start_vm"
    And VMs should include "python"

  @requires-docker-host
  Scenario: Stopping an already stopped VM
    Given I am following the documented workflow
    When I parse "stop postgres"
    Then intent should be "stop_vm"
    And VMs should include "postgres"

  @requires-docker-host
  Scenario: Creating an existing VM
    Given I am following the documented workflow
    When I parse "create go"
    Then intent should be "create_vm"
    And VMs should include "go"

  @requires-docker-host
  Scenario: Restarting a stopped VM
    Given I am following the documented workflow
    When I parse "restart rust"
    Then intent should be "restart_vm"

  @requires-docker-host
  Scenario: Status shows mixed states
    Given I am following the documented workflow
    When I parse "status"
    Then intent should be "status"

  @requires-docker-host
  Scenario: Smart start of already running VMs
    Given I am following the documented workflow
    When I parse "start python and postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  @requires-docker-host
  Scenario: Smart start with mixed states
    Given I am following the documented workflow
    When I parse "start python and postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  @requires-docker-host
  Scenario: Querying specific VM status
    Given I am following the documented workflow
    When I parse "is python running"
    Then intent should be "status"
    And VMs should include "python"

  @requires-docker-host
  Scenario: Preventing duplicate operations
    Given I am following the documented workflow
    When I parse "create python"
    Then intent should be "create_vm"
    And VMs should include "python"

  @requires-docker-host
  Scenario: Waiting for VM to be ready
    Given I am following the documented workflow
    When I parse "start python"
    Then intent should be "start_vm"

  @requires-docker-host
  Scenario: Notifying about background operations
    Given I am following the documented workflow
    When I parse "status"
    Then intent should be "status"

  @requires-docker-host
  Scenario: Conflicting operation detection
    Given I am following the documented workflow
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And rebuild flag should be true

  @requires-docker-host
  Scenario: State change notifications
    Given I am following the documented workflow
    When I parse "status"
    Then intent should be "status"

  @requires-docker-host
  Scenario: Batch operation state awareness
    Given I am following the documented workflow
    When I parse "start python and postgres"
    Then intent should be "start_vm"

  @requires-docker-host
  Scenario: Idempotent operations
    Given I am following the documented workflow
    When I parse "start python"
    Then intent should be "start_vm"

  @requires-docker-host
  Scenario: Clear state communication
    Given I am following the documented workflow
    When I parse "status"
    Then intent should be "status"
