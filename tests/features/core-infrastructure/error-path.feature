# language: en
@error-path
Feature: Error Path and Input Validation
  As the VDE system
  I want to reject invalid input and unknown VMs with correct error codes
  So that the error handling defined in VDE-SPEC.md sections 7 and 3.9 is enforced

  # ── VM name validation (spec section 3.9 vde_validate_name) ──

  Scenario: Reject VM name with semicolon injection
    When I run VDE command "create invalid;name"
    Then the exit code should not be 0
    And the command output should mention "invalid"

  Scenario: Reject VM name with path traversal
    When I run VDE command "create ../etc/passwd"
    Then the exit code should not be 0

  Scenario: Reject empty VM name
    When I run VDE command "create"
    Then the exit code should not be 0
    And the command output should mention "name"

  # ── Unknown VM type (spec section 7.2 VDE_ERR_NOT_FOUND) ──

  Scenario: Unknown VM type returns non-zero exit code
    When I run VDE command "create nonexistent-type-xyz123"
    Then the exit code should not be 0

  Scenario: Unknown VM type output mentions the unknown name
    When I run VDE command "create nonexistent-type-xyz123"
    Then the output should contain "nonexistent-type-xyz123"

  # ── Help and list commands always succeed (spec section 4.1) ──

  Scenario: vde help completes successfully
    When I run VDE command "help"
    Then the exit code should be 0

  Scenario: vde list completes successfully even with no running VMs
    When I run VDE command "list --all"
    Then the exit code should be 0
