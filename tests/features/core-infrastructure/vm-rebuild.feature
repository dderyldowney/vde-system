# language: en
@vm-rebuild @integration
Feature: VM Image Rebuild Tests

  These scenarios test VM image rebuild functionality with --rebuild and --no-cache flags.
  Testing top 5 language VMs (python, js, rust, go, ruby) + top 3 services (postgres, redis, nginx).
  Run separately with: python3 -m behave tests/features/core-infrastructure/vm-rebuild.feature

  Background:
    Given VM types are loaded from configuration

  @vm-rebuild
  Scenario: Rebuild Python VM with --rebuild flag
    Given VM "python" has been created
    And VM "python" is running
    When I start VM "python" with --rebuild
    Then docker-compose up --build should be executed
    And image should be rebuilt
    And VM "python" should be running

  @vm-rebuild
  Scenario: Rebuild JavaScript VM without cache
    Given VM "js" is running
    When I start VM "js" with --rebuild and --no-cache
    Then docker-compose up --build --no-cache should be executed
    And VM "js" should be running

  @vm-rebuild
  Scenario: Rebuild Rust VM with --rebuild flag
    Given VM "rust" is running
    When I run "vde start rust --rebuild"
    Then VM "rust" should be running
    And the container should be rebuilt from the Dockerfile

  @vm-rebuild
  Scenario: Rebuild Go VM with --rebuild flag
    Given VM "go" has been created
    And VM "go" is running
    When I start VM "go" with --rebuild
    Then docker-compose up --build should be executed
    And VM "go" should be running

  @vm-rebuild
  Scenario: Rebuild Ruby VM without cache
    Given VM "ruby" is running
    When I start VM "ruby" with --rebuild and --no-cache
    Then docker-compose up --build --no-cache should be executed
    And VM "ruby" should be running

  @vm-rebuild
  Scenario: Rebuild PostgreSQL service with --rebuild flag
    Given VM "postgres" has been created
    And VM "postgres" is running
    When I start VM "postgres" with --rebuild
    Then docker-compose up --build should be executed
    And VM "postgres" should be running

  @vm-rebuild
  Scenario: Rebuild Redis service without cache
    Given VM "redis" is running
    When I start VM "redis" with --rebuild and --no-cache
    Then docker-compose up --build --no-cache should be executed
    And VM "redis" should be running

  @vm-rebuild
  Scenario: Rebuild Nginx service with --rebuild flag
    Given VM "nginx" has been created
    And VM "nginx" is running
    When I start VM "nginx" with --rebuild
    Then docker-compose up --build should be executed
    And VM "nginx" should be running