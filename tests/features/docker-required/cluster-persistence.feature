@integration
@cluster-persistence
Feature: Multi-VM Cluster Persistence
  As a developer using VDE
  I want to group multiple VMs into a named cluster
  So I can start and stop them as a single unit

  @requires-docker-host
  Scenario: Saving and listing a cluster
    Given I have "python" and "postgres" VMs created
    When I run VDE command "cluster save web-app python postgres"
    Then the cluster "web-app" should be saved
    And VDE command "cluster list" should contain "web-app"

  @requires-docker-host
  Scenario: Starting a saved cluster
    Given I have a saved cluster "web-app" with "python" and "postgres"
    And "python" and "postgres" VMs are stopped
    When I run VDE command "cluster start web-app"
    Then "python" and "postgres" VMs should be running

  @requires-docker-host
  Scenario: Stopping a cluster
    Given I have a saved cluster "web-app" with "python" and "postgres"
    And "python" and "postgres" VMs are running
    When I run VDE command "cluster stop web-app"
    Then "python" and "postgres" VMs should be stopped

  @requires-docker-host
  Scenario: Removing a cluster
    Given I have a saved cluster "web-app" with "python" and "postgres"
    When I run VDE command "cluster remove web-app"
    Then the cluster "web-app" should NOT exist
    But the "python" and "postgres" VMs should still exist

  @parser
  Scenario: Natural language cluster saving
    When I parse "save this stack as my-project with go and redis"
    Then intent should be "cluster_op"
    And CLUSTER_ACTION should be "save"
    And CLUSTER_NAME should be "my-project"
    And VMs should include "go"
    And VMs should include "redis"

  @parser
  Scenario: Natural language cluster starting
    When I parse "start the my-project cluster"
    Then intent should be "cluster_op"
    And CLUSTER_ACTION should be "start"
    And CLUSTER_NAME should be "my-project"
