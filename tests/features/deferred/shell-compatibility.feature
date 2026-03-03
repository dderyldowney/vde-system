# language: en
@user-guide-internal
Feature: Shell Compatibility Layer
  As a developer
  I want VDE to work in zsh
  So that VDE has consistent shell behavior

  Scenario: Detect zsh shell
    When running in zsh
    Then _detect_shell should return "zsh"
    And _is_zsh should return true

  Scenario: Use native associative arrays in zsh
    Given running in zsh
    When I initialize an associative array
    Then native zsh typeset should be used
    And array operations should work correctly

  Scenario: Set and get values in associative array (zsh)
    Given running in zsh
    When I set key "foo" to value "bar"
    Then getting key "foo" should return "bar"

  Scenario: Handle special characters in keys (hex encoding)
    Given an associative array
    When I set key "a/b" to value "value1"
    And I set key "a_b" to value "value2"
    Then key "a/b" should return "value1"
    And key "a_b" should return "value2"
    And keys should not collide

  Scenario: Iterate over associative array keys
    Given associative array with keys "foo", "bar", "baz"
    When I get all keys
    Then all keys should be returned
    And original key format should be preserved

  Scenario: Check if key exists in associative array
    Given associative array with key "foo"
    When I check if key "foo" exists
    Then result should be true
    When I check if key "qux" exists
    Then result should be false

  Scenario: Unset key from associative array
    Given associative array with key "foo"
    When I unset key "foo"
    Then key "foo" should no longer exist

  Scenario: Clear all entries in associative array
    Given associative array with multiple entries
    When I clear the array
    Then array should be empty

  Scenario: Get script path portably
    Given running in zsh
    When I call _get_script_path
    Then absolute script path should be returned

  Scenario: Clean up storage on exit
    Given native associative arrays are in use
    When script exits
    Then temporary storage directory should be removed

  # =============================================================================
  # Edge Case Scenarios (zsh only)
  # =============================================================================

  Scenario: Handle empty associative array keys iteration
    Given running in zsh
    And I initialize an associative array named "empty_array"
    When I get all keys from "empty_array"
    Then no keys should be returned
    And array should be considered empty

  Scenario: Handle array values with spaces
    Given running in zsh
    And I initialize an associative array
    When I set key "path_with_spaces" to value "/usr/local/bin with spaces here"
    Then getting key "path_with_spaces" should return "/usr/local/bin with spaces here"

  Scenario: Handle special characters in keys
    Given running in zsh
    And I initialize an associative array
    When I set key "key/with/slashes" to value "slash_value"
    And I set key "key:with:colons" to value "colon_value"
    And I set key "key-with-dashes" to value "dash_value"
    And I set key "key_with_underscores" to value "underscore_value"
    Then key "key/with/slashes" should return "slash_value"
    And key "key:with:colons" should return "colon_value"
    And key "key-with-dashes" should return "dash_value"
    And key "key_with_underscores" should return "underscore_value"

  Scenario: Handle empty string as value
    Given running in zsh
    And I initialize an associative array
    When I set key "empty_value" to an empty value
    Then getting key "empty_value" should return an empty value
    And key "empty_value" should exist

  Scenario: Handle newlines in values
    Given running in zsh
    And I initialize an associative array
    When I set key "multiline" to value "line1\nline2\nline3"
    Then getting key "multiline" should contain newlines

  Scenario: Handle very long key names
    Given running in zsh
    And I initialize an associative array
    When I set key "this_is_a_very_long_key_name_that_exceeds_normal_usage_patterns_for_testing_purposes" to value "long_key_value"
    Then getting key "this_is_a_very_long_key_name_that_exceeds_normal_usage_patterns_for_testing_purposes" should return "long_key_value"

  Scenario: Handle unicode characters in values
    Given running in zsh
    And I initialize an associative array
    When I set key "emoji" to value "Hello World 🌍"
    Then getting key "emoji" should return "Hello World 🌍"

  Scenario: Clear and reuse associative array
    Given running in zsh
    And I initialize an associative array
    And I set key "temp1" to value "value1"
    And I set key "temp2" to value "value2"
    When I clear the array
    And I set key "new1" to value "new_value1"
    Then getting key "new1" should return "new_value1"
    And key "temp1" should no longer exist
    And key "temp2" should no longer exist

  Scenario: Overwrite existing key value
    Given running in zsh
    And I initialize an associative array
    And I set key "config" to value "original"
    When I set key "config" to value "updated"
    Then getting key "config" should return "updated"
    And array should contain exactly 1 key

  Scenario: Get non-existent key should fail gracefully
    Given running in zsh
    And I initialize an associative array
    And I set key "existing" to value "present"
    When I attempt to get key "nonexistent"
    Then operation should return failure status
    And no value should be returned

  Scenario: Unset non-existent key should not error
    Given running in zsh
    And I initialize an associative array
    When I unset key "never_existed"
    Then operation should complete successfully
    And array should remain empty
