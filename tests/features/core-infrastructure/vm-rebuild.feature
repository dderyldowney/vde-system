# language: en
@rebuild @requires-docker-host
Feature: VM Image Rebuild Tests

  These scenarios test VM image rebuild functionality with --rebuild and --no-cache flags.
  They are inherently slow (5-15 minutes on older hardware) due to Docker image rebuilds.
  Run separately with: python3 -m behave core-infrastructure/vm-rebuild.feature

  Scenario: Rebuild with --rebuild flag
    Given VM "python" has been created
    And VM "python" is running
    When I start VM "python" with --rebuild
    Then docker-compose up --build should be executed
    And image should be rebuilt
    And VM "python" should be running

  Scenario: Rebuild without cache with --no-cache flag
    Given VM "python" is running
    When I start VM "python" with --rebuild and --no-cache
    Then docker-compose up --build --no-cache should be executed
    And VM "python" should be running

  Scenario: Rebuild a VM with --rebuild flag
    Given VM "python" is running
    When I run "vde start python --rebuild"
    Then VM "python" should be running
    And the container should be rebuilt from the Dockerfile
