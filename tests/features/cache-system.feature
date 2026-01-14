# language: en
Feature: Cache System
  As a developer
  I want VM type data to be cached for performance
  So that scripts don't reparse configuration on every invocation

  Scenario: Cache VM types after first load
    Given vm-types.conf has been modified
    When VM types are loaded for the first time
    Then cache file should be created at ".cache/vm-types.cache"
    And cache file should contain all VM type data

  Scenario: Load from cache when config unchanged
    Given VM types cache exists
    And vm-types.conf has not been modified since cache
    When VM types are loaded
    Then data should be loaded from cache
    And vm-types.conf should not be reparsed

  Scenario: Invalidate cache when config is modified
    Given VM types cache exists
    And vm-types.conf has been modified after cache
    When VM types are loaded
    Then cache should be invalidated
    And vm-types.conf should be reparsed
    And cache file should be updated

  Scenario: Force cache bypass with --no-cache flag
    Given VM types cache exists and is valid
    When VM types are loaded with --no-cache
    Then cache should be bypassed
    And vm-types.conf should be reparsed

  Scenario: Cache stores all VM type arrays
    Given VM types are cached
    When cache is read
    Then VM_TYPE array should be populated
    And VM_ALIASES array should be populated
    And VM_DISPLAY array should be populated
    And VM_INSTALL array should be populated
    And VM_SVC_PORT array should be populated

  Scenario: Cache file format is parseable
    Given VM types cache exists
    When cache file is read
    Then each line should match "ARRAY_NAME:key=value" format
    And comments should start with "#"

  Scenario: Port registry cache persists allocations
    Given ports have been allocated for VMs
    When port registry is saved
    Then cache file should exist at ".cache/port-registry"
    And each VM should be mapped to its port

  Scenario: Load port registry from cache
    Given port registry cache exists
    When port registry is loaded
    Then allocated ports should be available without scanning compose files

  Scenario: Verify port registry consistency
    Given port registry cache exists
    And a VM has been removed
    When port registry is verified
    Then removed VM should be removed from registry
    And cache file should be updated

  Scenario: Rebuild port registry from compose files
    Given port registry cache is missing or invalid
    When port registry is verified
    Then registry should be rebuilt by scanning docker-compose files
    And all allocated ports should be discovered

  Scenario: Cache directory is created if missing
    Given .cache directory does not exist
    When cache operation is performed
    Then .cache directory should be created

  Scenario: Cache mtime comparison works correctly
    Given cache file was created before config file
    And cache file is newer than config file
    When cache validity is checked
    Then cache should be considered valid

  Scenario: Invalidate cache programmatically
    Given VM types cache exists
    When invalidate_vm_types_cache is called
    Then cache file should be removed
    And _VM_TYPES_LOADED flag should be reset

  Scenario: Lazy load VM types only when needed
    Given library has been sourced
    And no VM operations have been performed
    When VM types are first accessed
    Then VM types should be loaded at that time
    And not during initial library sourcing
