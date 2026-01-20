# language: en
@user-guide-internal
@requires-docker-host
Feature: Productivity Features for Developers
  As a developer
  I want shortcuts and automation for common tasks
  So that I can focus on coding instead of environment management

  # Real Test: Data Persistence
  Scenario: Persistent data survives container restart
    Given I have data in postgres
    When I stop and restart postgres VM
    Then my data should still be there
    And I don't lose work between sessions

  # Real Test: Fresh Database
  Scenario: Test with clean state quickly
    Given I need to test with fresh database
    When I stop and remove postgres
    And I recreate and start it
    Then I get a fresh database instantly
    And I don't need to manually clean data

  # Real Test: Database Backups
  Scenario: Database backups and restores
    Given I have important data in postgres VM
    When I create a backup of data/postgres/
    Then I can restore from backup later
    And my work is safely backed up

  # Real Test: Service VM Management
  Scenario: Run services in background while I work
    Given I need postgres and redis running
    When I start them as service VMs
    Then they run in background
