Feature: VDE Signal Handling
  As a developer
  I want VDE to handle POSIX signals gracefully
  So that I get clear feedback when an operation is interrupted or terminated

  @requires-docker-host
  Scenario: Interrupting a rebuild operation
    Given I have a valid VM type "python"
    When I interrupt the "rebuild python" command with SIGINT
    Then I should receive a clear error message
    And the error should explain what went wrong
    And it should mention "Operation Interrupted"

  @requires-docker-host
  Scenario: Process terminated by system (SIGTERM)
    Given I have a valid VM type "python"
    When I interrupt the "start python" command with SIGTERM
    Then I should receive a clear error message
    And the error should explain what went wrong
    And it should mention "Termination Requested"
