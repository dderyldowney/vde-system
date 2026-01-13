Feature: Daily Development Workflow
  As a developer using VDE
  I want to manage my development containers efficiently
  So I can focus on coding without managing infrastructure

  Scenario: Starting my development environment
    Given I have VDE installed
    When I request to start my Python development environment
    Then the Python VM should be started
    And SSH access should be available on the configured port
    And my workspace directory should be mounted

  Scenario: Checking what's currently running
    Given I have several VMs running
    When I ask "what's running?"
    Then I should see a list of all running VMs
    And each VM should show its status
    And the list should include both language and service VMs

  Scenario: Getting connection information for a VM
    Given I have a Python VM running
    When I ask "how do I connect to Python?"
    Then I should receive SSH connection details
    And the details should include the hostname
    And the details should include the port number
    And the details should include the username

  Scenario: Stopping work for the day
    Given I have multiple VMs running
    When I request to "stop everything"
    Then all running VMs should be stopped
    And no containers should be left running
    And the operation should complete without errors

  Scenario: Restarting a VM with rebuild
    Given I have a Python VM running
    When I request to "restart python with rebuild"
    Then the Python VM should be stopped
    And the container should be rebuilt from the Dockerfile
    And the Python VM should be started again
    And my workspace should still be mounted

  Scenario: Starting multiple VMs at once
    Given I need a full stack environment
    When I request to "start python and postgres"
    Then both Python and PostgreSQL VMs should start
    And they should be on the same Docker network
    And they should be able to communicate

  Scenario: Creating a new VM for the first time
    Given I want to try a new language
    When I request to "create a Go VM"
    Then the Go VM configuration should be created
    And the Docker image should be built
    And SSH keys should be configured
    And the VM should be ready to start
