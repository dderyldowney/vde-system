# language: en
@core-infrastructure
@user-guide-internal
Feature: VM State Awareness
  As a developer using VDE
  I want the system to be aware of VM states
  So I don't accidentally duplicate operations or cause conflicts

  @requires-docker-host
  Scenario: Starting an already running VM
    Given I have a Python VM that is already running
    When I request to "start python"
    Then I should be told Python is already running
    And the system should not start a duplicate container
    And the existing container should remain unaffected

  @requires-docker-host
  Scenario: Stopping an already stopped VM
    Given I have a stopped PostgreSQL VM
    When I request to "stop postgres"
    Then I should be told it is already stopped
    And no error should occur
    And the VM should remain stopped

  @requires-docker-host
  Scenario: Creating an existing VM
    Given I already have a Go VM configured
    When I request to "create a Go VM"
    Then I should be told it already exists
    And the system should not overwrite the existing configuration

  @requires-docker-host
  Scenario: Restarting a stopped VM
    Given I have a stopped VM
    When I request to "restart rust"
    Then the system should recognize it's stopped
    And the Rust VM should start again
    And I should be informed that it was started

  @requires-docker-host
  Scenario: Status shows mixed states
    Given I have some running and some stopped VMs
    When I request "status"
    Then I should see which VMs are running
    And I should see which VMs are stopped

  @requires-docker-host
  Scenario: Smart start of already running VMs
    Given I have Python and PostgreSQL running
    When I request to "start python and postgres"
    Then execution would detect the VM is already running
    And no containers should be restarted
    And the operation should complete immediately

  @requires-docker-host
  Scenario: Smart start with mixed states
    Given I have Python running and PostgreSQL stopped
    When I request to "start python and postgres"
    Then I should be told Python is already running
    And the PostgreSQL VM should start
    And I should be informed of the mixed result

  @requires-docker-host
  Scenario: Querying specific VM status
    Given I want to know about a specific VM
    When I ask "is python running?"
    Then I should receive a clear yes/no answer

  @requires-docker-host
  Scenario: Preventing duplicate operations
    Given I have a running VM
    When I try to create it again
    Then execution would detect the VM already exists
    And I would be notified of the existing VM

  @requires-docker-host
  Scenario: Waiting for VM to be ready
    Given I start a VM
    When it takes time to be ready
    Then I should be informed of progress
    And know when it's ready to use

  @requires-docker-host
  Scenario: Notifying about background operations
    Given a VM is being built
    When I check status
    Then I should see it's being built

  @requires-docker-host
  Scenario: Conflicting operation detection
    Given I'm rebuilding a VM
    When I try to start it at the same time
    Then the conflict should be detected
    And I should be notified

  @requires-docker-host
  Scenario: State change notifications
    Given a VM's state changes
    When I'm monitoring the system
    Then I should be notified of the change
    And understand what caused it
    And know the new state

  @requires-docker-host
  Scenario: Batch operation state awareness
    Given I request to start multiple VMs
    When some are already running
    Then only the stopped VMs should start
    And I should see which were started

  @requires-docker-host
  Scenario: Idempotent operations
    Given I repeat the same command
    When the operation is already complete
    Then the result should be the same
    And no errors should occur

  @requires-docker-host
  Scenario: Clear state communication
    Given any VM operation occurs
    When the operation completes
    Then I should see the new state
    And understand what changed
