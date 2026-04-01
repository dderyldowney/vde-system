@docker-required @ssh @hardening
Feature: SSH VM Hardening
  As a VDE user
  I want my SSH arguments to be parsed correctly
  So that I can pass options to both SSH and the target command without conflict

  Background:
    Given all language VM configs are loaded from vm-types.json

  Scenario: Standard command passing
    When I run VDE command "ssh python ls -l --show-command"
    Then the output should contain "ls -l"
    And the exit code should be 0

  Scenario: SSH options before VM name
    When I run VDE command "ssh -v python ls --show-command"
    Then the output should contain "ssh"
    And the output should contain "-v"
    And the output should contain "vde-python"
    And the output should contain "ls"
    And the exit code should be 0

  Scenario: Command options after VM name
    When I run VDE command "ssh python ls -v --show-command"
    Then the output should contain "vde-python"
    And the output should contain "ls -v"
    And the exit code should be 0

  Scenario: Conflict option after VM name is passed to command
    When I run VDE command "ssh python ls --help --show-command"
    Then the output should NOT contain "Usage:"
    And the output should contain "ls --help"
    And the exit code should be 0

  Scenario: Using -- separator for strict isolation
    When I run VDE command "ssh python --show-command -- ls -v --something"
    Then the output should contain "ls -v --something"
    And the exit code should be 0

  Scenario: Option starting with - after -- should NOT go to SSH_OPTS
    When I run VDE command "ssh python --show-command -- -v"
    Then the output should contain "vde-python -v"
    And the exit code should be 0
