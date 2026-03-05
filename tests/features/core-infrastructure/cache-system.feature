# language: en
@cache-system @core-infrastructure @unit
Feature: Cache System
  As the VDE system
  I want VM type data cached at .cache/vm-types.cache as defined in VDE-SPEC.md section 2.4
  So that scripts load VM types from cache without reparsing the source config each time

  # ── Cache file existence and location (spec section 2.4) ──

  Scenario: vm-types.cache exists after VM types are loaded
    When VM types are loaded via the vde script
    Then ".cache/vm-types.cache" should exist

  Scenario: vm-types.cache is inside the .cache directory (spec section 2.4)
    When VM types are loaded via the vde script
    Then ".cache/vm-types.cache" should be a file inside the VDE root

  # ── Cache file content (spec section 2.4) ──

  Scenario: Cache contains VM_TYPE array entries
    Given ".cache/vm-types.cache" exists
    When I read the cache file
    Then the cache should contain "VM_TYPE"

  Scenario: Cache contains VM_ALIASES array entries
    Given ".cache/vm-types.cache" exists
    When I read the cache file
    Then the cache should contain "VM_ALIASES"

  Scenario: Cache contains VM_DISPLAY array entries
    Given ".cache/vm-types.cache" exists
    When I read the cache file
    Then the cache should contain "VM_DISPLAY"

  Scenario: Cache stores known language VM entries
    Given ".cache/vm-types.cache" exists
    When I read the cache file
    Then the cache should contain "vde-python"
    And the cache should contain "vde-rust"

  Scenario: Cache stores known service VM entries
    Given ".cache/vm-types.cache" exists
    When I read the cache file
    Then the cache should contain "vde-postgres"
    And the cache should contain "vde-redis"

  # ── Port registry (spec section 2.3) ──

  Scenario: Port registry directory exists inside .cache
    Then ".cache/port-registry" should exist as a directory

  # ── Cache directory (spec section 9) ──

  Scenario: .cache directory exists
    Then VDE directory ".cache" should exist
