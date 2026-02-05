# language: en
@wip
@user-guide-internal
@wip
Feature: Team Collaboration and Maintenance
  # SKIPPED: Team collaboration tests need VDE implementation updates - deferring to Phase 3
  As a developer in a team environment
  I want to maintain and share development environments
  So my team can work consistently across different machines

  @requires-docker-host
  Scenario: Rebuilding after system updates
    Given I have updated my system Docker
    When I request to "rebuild python with no cache"
    Then the Python container should be rebuilt from scratch
    And no cached layers should be used
    And the rebuild should use the latest base images

  @requires-docker-host
  Scenario: Troubleshooting a problematic VM
    Given a VM is not working correctly
    When I request to "restart postgres with rebuild"
    Then the PostgreSQL VM should be completely rebuilt
    And my data should be preserved (if using volumes)
    And the VM should start with a fresh configuration

  Scenario: Checking system status
    Given I am experiencing issues
    When I request to "show status of all VMs"
    Then I should see which VMs are running
    And I should see which VMs are stopped
    And I should see any error conditions

  @requires-docker-host
  Scenario: Adding a new language to the team
    Given my team wants to use a new language
    When I request to "create a Haskell VM"
    Then the Haskell VM should be created
    And it should use the standard VDE configuration
    And it should be ready for the team to use

  Scenario: Sharing SSH configurations
    Given a new team member joins
    When they ask "how do I connect?"
    Then they should receive clear connection instructions
    And the instructions should include SSH config examples
    And the instructions should work on their first try

  @requires-docker-host
  Scenario: Batch operations for efficiency
    Given I need to manage multiple VMs
    When I request to "start python, go, and rust"
    Then all three VMs should start in parallel
    And the operation should complete faster than sequential starts
    And all VMs should be running when complete

  @requires-docker-host
  Scenario: Stopping only development VMs
    Given I have both development and service VMs running
    When I request to "stop all languages"
    Then only language VMs should stop
    And service VMs should continue running
    And databases and caches should remain available

  @requires-docker-host
  Scenario: Performing system maintenance
    Given I need to update VDE itself
    When I stop all VMs
    Then I can update the VDE scripts
    And I can rebuild all VMs with the new configuration
    And my workspace data should persist

  @requires-docker-host
  Scenario: Recovering from errors
    Given a VM has crashed
    When I request to "restart the VM"
    Then the VM should be stopped if running
    And the VM should be started again
    And the restart should attempt to recover the state

  Scenario: Monitoring resource usage
    Given I want to check VM resource consumption
    When I query VM status
    Then I should see which VMs are consuming resources
    And I should be able to identify heavy VMs
    And I can make decisions about which VMs to stop

  @requires-docker-host
  Scenario: Scaling for a large project
    Given my project has grown
    When I request to "start all services for the project"
    Then all required VMs should start
    And the system should handle many VMs
    And each VM should have adequate resources
