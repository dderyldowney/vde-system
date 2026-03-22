# language: en
@storage
Feature: Productivity Features for Developers
  As a developer
  I want shortcuts and automation for common tasks via unified commands
  So that I can focus on coding instead of environment management

  Scenario: Persistent data survives container restart
    Given I have data in postgres
    When I stop and restart postgres VM
    Then my data should still be there

  Scenario: Test with clean state quickly
    Given I need to test with fresh database
    When I stop and remove postgres
    And I recreate and start it
    Then I should have a fresh database

  Scenario: Database backups and restores
    Given I have data in postgres
    When I create a backup of data/postgres/
    Then my data should be restored

  Scenario: Run services in background
    Given I have background services running
    When I continue my work on host
    Then services should keep running in background
