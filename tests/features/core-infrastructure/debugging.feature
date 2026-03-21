# language: en
@core-infrastructure
@user-guide-troubleshooting
@core-suite
Feature: Debugging and Troubleshooting
  As a developer
  I want tools to diagnose and fix VM issues via unified commands
  So that I can quickly resolve problems and continue working

  Scenario: Diagnose why VM won't start
    Given I am following the documented workflow
    When I parse "status"
    Then intent should be "status"

  @requires-docker-host
  Scenario: View VM logs for debugging
    Given a VM is running but misbehaving
    When I run "vde logs python"
    Then I should see the container logs

  @requires-docker-host
  Scenario: Access VM shell for debugging
    Given a VM is running
    When I run "vde exec python /bin/zsh"
    Then I should be logged in as devuser

  @requires-docker-host
  Scenario: Rebuild VM from scratch after corruption
    Given a VM is not working correctly
    When I request to "restart python rebuild=true"
    Then the Python VM should be rebuilt

  @requires-docker-host
  Scenario: Check if port is already in use
    Given a port is already in use
    When I try to start a VM
    Then VDE should detect the conflict

  @requires-docker-host
  Scenario: Verify SSH connection is working
    Given I cannot SSH into a VM
    When I check the SSH config
    And I verify the SSH port is correct
    Then I can identify issues

  @requires-docker-host
  Scenario: Test database connectivity from VM
    Given my application can't connect to the database
    When I SSH into the Python VM
    And I try to connect to the database VM directly
    Then I can see if the issue is network

  @requires-docker-host
  Scenario: Inspect docker-compose configuration
    Given I need to verify VM configuration
    When I check the Docker Compose configuration detail
    Then I should see all port mappings

  @requires-docker-host
  Scenario: Verify volumes are mounted correctly
    Given my code changes aren't reflected in the VM
    When I check the VDE status
    Then my workspace directory should be mounted

  @requires-docker-host
  Scenario: Clear Docker cache to fix build issues
    Given a VM build keeps failing
    When I request to "rebuild go nocache=true"
    Then the Go VM should be rebuilt from scratch

  @requires-docker-host
  Scenario: Reset a VM to initial state
    Given I've made changes I want to discard
    When I stop and remove postgres
    And I start them again
    Then I should have a fresh database

  @requires-docker-host
  Scenario: Verify network connectivity between VMs
    Given two VMs can't communicate
    When I check the ./bin/vde networks
    Then I should see both VMs on "vde-testing"
    And I can ping one VM from another

  @requires-docker-host
  Scenario: Check VM resource usage
    Given a VM seems slow
    When I check resource usage
    Then I can see CPU and memory usage

  @requires-docker-host
  Scenario: Validate VM configuration before starting
    Given I think my docker-compose.yml might have errors
    When I check the Docker Compose configuration detail
    Then the configuration should be validated

  @requires-docker-host
  Scenario: Recover from Docker daemon issues
    Given VMs won't start due to Docker problems
    When I check Docker is running
    And I restart Docker if needed
    Then VMs should start normally after Docker is healthy

  @requires-docker-host
  Scenario: Fix permission issues on shared volumes
    Given I get permission denied errors in VM
    When I check the UID/GID configuration
    Then I should see if devuser (1000:1000) matches my host user

  @requires-docker-host
  Scenario: Diagnose why tests fail in VM but pass locally
    Given tests work on host but fail in VM
    When I compare the environments
    Then I can check for missing dependencies
