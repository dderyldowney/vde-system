# language: en
@user-guide-internal
Feature: Shell Compatibility Layer
  As a developer
  I want VDE to work across different shells (zsh, bash 4+, bash 3.x)
  So that VDE is portable across different systems

  Scenario: Detect zsh shell
    When running in zsh
    Then _detect_shell should return "zsh"
    And _is_zsh should return true
    And _is_bash should return false

  Scenario: Detect bash shell
    When running in bash
    Then _detect_shell should return "bash"
    And _is_bash should return true
    And _is_zsh should return false

  Scenario: Detect bash version for compatibility
    Given running in bash "4.0"
    Then _bash_version_major should return "4"
    And _shell_supports_native_assoc should return true

  Scenario: Detect bash 3.x for fallback mode
    Given running in bash "3.2"
    Then _bash_version_major should return "3"
    And _shell_supports_native_assoc should return false

  Scenario: Use native associative arrays in zsh
    Given running in zsh
    When I initialize an associative array
    Then native zsh typeset should be used
    And array operations should work correctly

  Scenario: Use native associative arrays in bash 4+
    Given running in bash "4.0"
    When I initialize an associative array
    Then native bash declare should be used
    And array operations should work correctly

  Scenario: Use file-based fallback in bash 3.x
    Given running in bash "3.2"
    When I initialize an associative array
    Then file-based storage should be used
    And operations should work via file I/O

  Scenario: Set and get values in associative array (zsh)
    Given running in zsh
    When I set key "foo" to value "bar"
    Then getting key "foo" should return "bar"

  Scenario: Set and get values in associative array (bash 4+)
    Given running in bash "4.0"
    When I set key "foo" to value "bar"
    Then getting key "foo" should return "bar"

  Scenario: Set and get values in associative array (bash 3.x)
    Given running in bash "3.2"
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
    Given running in bash
    When I call _get_script_path
    Then absolute script path should be returned

  Scenario: Clean up file-based storage on exit
    Given file-based associative arrays are in use
    When script exits
    Then temporary storage directory should be removed
