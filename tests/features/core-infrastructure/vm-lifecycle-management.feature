# language: en
@core-infrastructure
@user-guide-starting-stopping
Feature: VM Lifecycle Management
  As a developer using VDE
  I want to manage the complete lifecycle of my VMs via conversational commands
  So I can create, configure, start, stop, and destroy VMs as needed

  @requires-docker-host
  Scenario: Creating a new VM
    Given I want to work with a new language
    When I request to "create a Rust VM"
    Then the VM configuration should be generated
    And the Docker image should be built
    And SSH keys should be configured
    And the VM should be ready to use

  @requires-docker-host
  Scenario: Creating multiple VMs at once
    Given I need a full stack environment
    When I request to "create Python, PostgreSQL, and Redis"
    Then all three VMs should be created
    And each should have its own configuration
    And all should be on the same Docker network

  @requires-docker-host
  Scenario: Starting a created VM
    Given I have created a Go VM
    When I request to "start go"
    Then the Go container should start
    And it should be accessible via SSH
    And my workspace should be mounted

  @requires-docker-host
  Scenario: Starting multiple VMs
    Given I have created several VMs
    When I request to "start python, go, and postgres"
    Then all three VMs should start
    And they should be able to communicate
    And each should have its own SSH port

  Scenario: Checking VM status
    Given I have several VMs
    When I request "status"
    Then I should see which VMs are running
    And I should see which VMs are stopped

  @requires-docker-host
  Scenario: Stopping a running VM
    Given I have a running Python VM
    When I request to "stop python"
    Then the container should be stopped if running
    And the VM configuration should remain
    And I can start it again later

  @requires-docker-host
  Scenario: Stopping multiple VMs
    Given I have multiple running VMs
    When I request to "stop python and postgres"
    Then both VMs should stop
    And other VMs should remain running

  @requires-docker-host
  Scenario: Restarting a VM
    Given I have a running VM
    When I request to "restart rust"
    Then the Rust VM should stop
    And the Rust VM should start again
    And my workspace should still be accessible

  @requires-docker-host
  Scenario: Restarting with rebuild
    Given I need to refresh a VM
    When I request to "restart python rebuild=true"
    Then the Python VM should be rebuilt
    And the VM should start with the new image
    And my workspace should be preserved

  @requires-docker-host
  Scenario: Removing a VM instance
    Given I no longer need a VM
    When I run "vde remove ruby"
    Then container should be gone
    And VM "ruby" configuration should be preserved

  @requires-docker-host
  Scenario: Rebuilding after code changes
    Given I have modified the Dockerfile
    When I request to "rebuild go nocache=true"
    Then the Go VM should be rebuilt from scratch
    And no cached layers should be used

  @requires-docker-host
  Scenario: Upgrading a VM
    Given I want to update the base image
    When I rebuild the VM
    Then the latest base image should be used
    And VM configuration should still exist
    And my workspace should still be accessible

  @requires-docker-host
  Scenario: Migrating to a new VDE version
    Given I have updated VDE scripts
    When I rebuild my VMs
    Then they should use the new VDE configuration
    And my data should be preserved
