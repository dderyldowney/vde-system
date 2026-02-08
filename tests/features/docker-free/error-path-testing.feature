@docker-free
Feature: Error path and negative testing
  As a developer
  I want VDE to handle errors gracefully
  So that I get clear feedback when things go wrong

  Scenario: Invalid VM name with special characters
    Given the VDE system is available
    When I try to create a VM named "invalid;name"
    Then the command should fail with a non-zero exit code
    And the error output should contain useful information

  Scenario: Invalid VM name with path traversal
    Given the VDE system is available
    When I try to create a VM named "../etc/passwd"
    Then the command should fail with a non-zero exit code
    And the error output should contain useful information

  Scenario: Creating a VM with unknown type
    Given the VDE system is available
    When I try to create a VM named "nonexistent-type-xyz123"
    Then the command should fail with a non-zero exit code
    And the error output should contain useful information

  Scenario: Running VDE help command
    Given the VDE system is available
    When I run the VDE help command
    Then the command should complete successfully
    And the output should contain usage information

  @wip
  Scenario: Querying status of non-existent VM
    Given the VDE system is available
    When I query the status of a non-existent VM
    Then the command should indicate the VM was not found

  Scenario: Listing VMs when none are running
    Given the VDE system is available
    When I list all VMs
    Then the command should complete successfully

  Scenario: Empty VM name
    Given the VDE system is available
    When I try to create a VM with an empty name
    Then the command should fail with a non-zero exit code

  Scenario: Parser handles empty input
    Given the VDE natural language parser is available
    When I parse an empty string
    Then the parser should return empty or error result

  Scenario: Parser handles gibberish input
    Given the VDE natural language parser is available
    When I parse gibberish text "asdf jkl qwerty zxcv"
    Then the parser should not crash

  Scenario: Config file validation with missing file
    Given the VDE system is available
    When I check for a config file that does not exist
    Then the system should report the file is missing
