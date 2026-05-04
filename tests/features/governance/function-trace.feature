# Function Trace Diagnostic Command
# @forge (Forge Diagnostic Tooling)
Feature: VDE Function Trace Diagnostic Command
  As a VDE support technician
  I need to trace the full function call chain for any vde command
  So I can diagnose user issues without executing side effects

  @forge
  Scenario: Trace produces function entries for a known command
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "Function:"
    And the output should contain "File: $VDE_ROOT_DIR"
    And the return code should be 0

  @forge
  Scenario: Trace shows library boundary transitions
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "lib/vm-common"
    And the output should contain "bin/vde"

  @forge
  Scenario: Trace captures argument values passed to traced functions
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "Params: vde-python"

  @forge
  Scenario: Trace stops at executor boundary without starting the container
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "[EXECUTOR]"
    And the container "vde-python" should not be running

  @forge
  Scenario: Trace identifies the executor coordinator function before the boundary
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "vde_run()"

  @forge
  Scenario: Trace includes the dispatch entry point
    Given the Hub is active
    When I execute "bin/vde function-trace start python"
    Then the output should contain "dispatch: vde start"
