# language: en
@user-guide-troubleshooting
@requires-docker-host
Feature: Error Handling and Recovery
  As a developer using VDE
  I want the system to handle errors gracefully
  So I can recover quickly from problems

  Scenario: Invalid VM name handling
    Given I try to use a VM that doesn't exist
    When I request to "start nonexistent-vm"
    Then I should receive a clear error message
    And the error should explain what went wrong
    And suggest valid VM names

  Scenario: Port conflict resolution
    Given a port is already in use
    When I try to start a VM
    Then VDE should detect the conflict
    And allocate an available port
    And continue with the operation

  Scenario: Docker daemon not running
    Given Docker is not available
    When I try to start a VM
    Then I should receive a helpful error
    And the error should explain Docker is required
    And suggest how to fix it

  Scenario: Insufficient disk space
    Given my disk is nearly full
    When I try to create a VM
    Then VDE should detect the issue
    And warn me before starting
    And suggest cleaning up

  Scenario: Network creation failure
    Given the Docker network can't be created
    When I start a VM
    Then VDE should report the specific error
    And suggest troubleshooting steps
    And offer to retry

  Scenario: Build failure recovery
    Given a VM build fails
    When I examine the error
    Then I should see what went wrong
    And get suggestions for fixing it
    And be able to retry after fixing

  Scenario: Container startup timeout
    Given a container takes too long to start
    When VDE detects the timeout
    Then it should report the issue
    And show the container logs
    And offer to check the status

  Scenario: SSH connection failure
    Given a container is running but SSH fails
    When I try to connect
    Then VDE should diagnose the problem
    And check if SSH is running
    And verify the SSH port is correct

  Scenario: Permission denied errors
    Given I don't have permission for an operation
    When VDE encounters the error
    Then it should explain the permission issue
    And suggest how to fix it
    And offer to retry with proper permissions

  Scenario: Configuration file errors
    Given a docker-compose.yml is malformed
    When I try to use the VM
    Then VDE should detect the error
    And show the specific problem
    And suggest how to fix the configuration

  Scenario: Graceful degradation
    Given one VM fails to start
    When I start multiple VMs
    Then other VMs should continue
    And I should be notified of the failure
    And successful VMs should be listed

  Scenario: Automatic retry logic
    Given a transient error occurs
    When VDE detects it's retryable
    Then it should automatically retry
    And limit the number of retries
    And report if all retries fail

  Scenario: Partial state recovery
    Given an operation is interrupted
    When I try again
    Then VDE should detect partial state
    And complete the operation
    And not duplicate work

  Scenario: Clear error messages
    Given any error occurs
    When the error is displayed
    Then it should be in plain language
    And explain what went wrong
    And suggest next steps

  Scenario: Error logging
    Given an error occurs
    When VDE handles it
    Then the error should be logged
    And the error should have sufficient detail for debugging
    And I can find it in the logs directory

  Scenario: Rollback on failure
    Given an operation fails partway through
    When the failure is detected
    Then VDE should clean up partial state
    And return to a consistent state
    And allow me to retry cleanly
