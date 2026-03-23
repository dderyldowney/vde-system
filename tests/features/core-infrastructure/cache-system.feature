# language: en
@spec
Feature: Cache System
  As a developer
  I want VM type data to be cached for performance
  So that scripts don't reparse configuration on every invocation

  Scenario: vm-types.cache exists after VM types are loaded
    Given VM types are loaded
    Then cache file should be created at ".cache/vm-types.cache"
    And cache file should contain all VM type data

  Scenario: Cache stores all VM type arrays
    Given VM types are cached
    When cache is read
    Then VM_TYPE array should be populated
    And VM_ALIASES array should be populated

  Scenario: Cache directory is created if missing
    Given .cache directory does not exist
    When cache operation is performed
    Then .cache directory should be created
