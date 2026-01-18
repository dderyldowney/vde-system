# language: en
@user-guide-troubleshooting
Feature: Debugging and Troubleshooting
  As a developer
  I want tools to diagnose and fix VM issues
  So that I can quickly resolve problems and continue working

  Scenario: Diagnose why VM won't start
    Given I tried to start a VM but it failed
    When I check the VM status
    Then I should see a clear error message
    And I should know if it's a port conflict, Docker issue, or configuration problem

  @requires-docker-host
  Scenario: View VM logs for debugging
    Given a VM is running but misbehaving
    When I run "docker logs <vm-name>"
    Then I should see the container logs
    And I can identify the source of the problem

  @requires-docker-host
  Scenario: Access VM shell for debugging
    Given a VM is running
    When I run "docker exec -it <vm-name> /bin/zsh"
    Then I should have shell access inside the container
    And I can investigate issues directly

  @requires-docker-host
  Scenario: Rebuild VM from scratch after corruption
    Given a VM seems corrupted or misconfigured
    When I stop the VM
    And I remove the VM directory
    And I recreate the VM
    Then I should get a fresh VM
    And old configuration issues should be resolved

  @requires-docker-host
  Scenario: Check if port is already in use
    Given I get a "port already allocated" error
    When I check what's using the port
    Then I should see which process is using it
    And I can decide to stop the conflicting process
    And VDE can allocate a different port

  @requires-docker-host
  Scenario: Verify SSH connection is working
    Given I cannot SSH into a VM
    When I check the SSH config
    And I verify the VM is running
    And I verify the port is correct
    Then I can identify if the issue is SSH, Docker, or the VM itself

  @requires-docker-host
  Scenario: Test database connectivity from VM
    Given my application can't connect to the database
    When I SSH into the application VM
    And I try to connect to the database VM directly
    Then I can see if the issue is network, credentials, or database state

  @requires-docker-host
  Scenario: Inspect docker-compose configuration
    Given I need to verify VM configuration
    When I look at the docker-compose.yml
    Then I should see all volume mounts
    And I should see all port mappings
    And I should see environment variables
    And I can verify the configuration is correct

  @requires-docker-host
  Scenario: Verify volumes are mounted correctly
    Given my code changes aren't reflected in the VM
    When I check the mounts in the container
    Then I can see if the volume is properly mounted
    And I can verify the host path is correct

  @requires-docker-host
  Scenario: Clear Docker cache to fix build issues
    Given a VM build keeps failing
    When I rebuild with --no-cache
    Then Docker should pull fresh images
    And build should not use cached layers

  @requires-docker-host
  Scenario: Reset a VM to initial state
    Given I've made changes I want to discard
    When I stop the VM
    And I remove the container but keep the config
    And I start it again
    Then I should get a fresh container
    And my code volumes should be preserved

  @requires-docker-host
  Scenario: Verify network connectivity between VMs
    Given two VMs can't communicate
    When I check the docker network
    Then I should see both VMs on "vde-network"
    And I can ping one VM from another

  @requires-docker-host
  Scenario: Check VM resource usage
    Given a VM seems slow
    When I run "docker stats <vm-name>"
    Then I can see CPU and memory usage
    And I can identify resource bottlenecks

  @requires-docker-host
  Scenario: Validate VM configuration before starting
    Given I think my docker-compose.yml might have errors
    When I run "docker-compose config"
    Then I should see any syntax errors
    And the configuration should be validated

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
    And I can adjust if needed

  @requires-docker-host
  Scenario: Diagnose why tests fail in VM but pass locally
    Given tests work on host but fail in VM
    When I compare the environments
    Then I can check for missing dependencies
    And I can verify environment variables match
    And I can check network access from the VM
