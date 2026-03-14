# language: en
@core-infrastructure
@user-guide-internal
Feature: Team Collaboration and Maintenance
  As a developer in a team environment
  I want to maintain and share development environments via unified commands
  So my team can work consistently across different machines

  @requires-docker-host
  Scenario: Rebuilding after system updates
    Given I have updated my system Docker
    When I request to "rebuild python nocache=true"
    Then the Python VM should be rebuilt from scratch
    And no cached layers should be used
    And the rebuild should use the latest base images

  @requires-docker-host
  Scenario: Troubleshooting a problematic VM
    Given a VM is not working correctly
    When I request to "restart postgres rebuild=true"
    Then the PostgreSQL VM should be completely rebuilt
    And my data should be preserved
    And the VM should start with a fresh configuration

  Scenario: Checking system status
    Given I am experiencing issues
    When I request to "status"
    Then I should see which VMs are running
    And I should see which VMs are stopped

  @requires-docker-host
  Scenario: Adding a new language to the team
    Given my team wants to use a new language
    When I request to "create a Haskell VM"
    Then the VM configuration should be generated
    And the VM should be ready to use

  Scenario: Sharing SSH configurations
    Given a new team member joins
    When they ask "how do I connect to python?"
    Then they should receive clear connection instructions
    And the instructions should be clear and actionable

  @requires-docker-host
  Scenario: Batch operations for efficiency
    Given I need to manage multiple VMs
    When I request to "start python, go, and rust"
    Then all three VMs should start
    And the operation should complete faster than sequential starts

  @requires-docker-host
  Scenario: Stopping only development VMs
    Given I have multiple running VMs
    When I request to "stop all languages"
    Then only language VMs should stop
    And service VMs should continue running
    And databases and caches should remain available

  @requires-docker-host
  Scenario: Performing system maintenance
    Given I need to update VDE itself
    When I request to "stop everything"
    Then all running VMs should be stopped
    And I can rebuild all VMs with the new configuration
    And my data should be preserved

  @requires-docker-host
  Scenario: Recovering from errors
    Given a VM has crashed
    When I request to "restart python"
    Then the container should be stopped if running
    And the VM should start again

  Scenario: Monitoring resource usage
    Given I want to check VM resource consumption
    When I check resource usage
    Then I can see CPU and memory usage
    And I can identify resource bottlenecks

  @requires-docker-host
  Scenario: Scaling for a large project
    Given my project has grown
    When I request to "start all services"
    Then all service VMs should start
    And each container should have reasonable limits
