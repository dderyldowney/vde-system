# language: en
@shell-compatibility @core-infrastructure @unit @core-suite
Feature: Shell Compatibility Layer
  As the VDE system
  I want associative array operations defined in VDE-SPEC.md section 3.2 to work in zsh
  So that all library functions that depend on vde-shell-compat behave correctly

  # ── _assoc_set / _assoc_get (spec section 3.2) ──

  Scenario: Set and get a value from an associative array
    Given a new associative array "test_array"
    When I set key "foo" to value "bar" in "test_array"
    Then getting key "foo" from "test_array" should return "bar"

  Scenario: Set and get a value with special characters in the value
    Given a new associative array "test_array"
    When I set key "path" to value "/usr/local/bin" in "test_array"
    Then getting key "path" from "test_array" should return "/usr/local/bin"

  Scenario: Handle keys with slash characters (hex-encoded storage)
    Given a new associative array "test_array"
    When I set key "a/b" to value "val1" in "test_array"
    And I set key "a_b" to value "val2" in "test_array"
    Then getting key "a/b" from "test_array" should return "val1"
    And getting key "a_b" from "test_array" should return "val2"

  # ── _assoc_has_key (spec section 3.2) ──

  Scenario: Check that an existing key is found
    Given a new associative array "test_array"
    And key "foo" is set to "bar" in "test_array"
    When I check if key "foo" exists in "test_array"
    Then the key existence check should return true

  Scenario: Check that a missing key is not found
    Given a new associative array "test_array"
    When I check if key "nonexistent" exists in "test_array"
    Then the key existence check should return false

  # ── _assoc_clear (spec section 3.2) ──

  Scenario: Clear all entries from an associative array
    Given a new associative array "test_array"
    And key "foo" is set to "bar" in "test_array"
    And key "baz" is set to "qux" in "test_array"
    When I clear "test_array"
    Then key "foo" should not exist in "test_array"
    And key "baz" should not exist in "test_array"

  # ── vde_normalize_name (spec section 3.9) used as compat utility ──

  Scenario: Normalize uppercased VM name to lowercase
    When I call vde_normalize_name with "PYTHON"
    Then the result should be "python"
