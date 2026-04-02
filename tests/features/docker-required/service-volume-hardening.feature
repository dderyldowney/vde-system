@integration @docker @service
Feature: Service & Volume Hardening
  As a developer
  I want service VMs to have reliable data persistence and networking
  So that my application state is preserved across restarts

  Background:
    Given postgres service VM is created
    And redis service VM is created

  Scenario: Service VM data persists after restart
    Given VM "postgres" is started
    And I create a test table "persistence_check" in "postgres"
    When I restart VM "postgres"
    Then the table "persistence_check" should still exist in "postgres"

  Scenario: Service VM with multiple ports is reachable
    Given VM "redis" is created with ports "6379,6380"
    When I start VM "redis"
    Then host port 6379 should be open
    And host port 6380 should be open

  Scenario: Deterministic health check prevents early connection
    Given VM "postgres" is stopped
    When I start VM "postgres"
    Then I should wait for VM "postgres" to be healthy
    And the database should be ready for connections immediately

  Scenario: Service VM is resolvable by language VM on vde-net
    Given language VM "python" is started
    And service VM "postgres" is started
    When I ping "vde-postgres" from "vde-python"
    Then the ping should be successful
