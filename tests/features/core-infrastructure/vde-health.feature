# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@core-infrastructure @health
Feature: Health Check Command
  As an Alor of the VDE
  I require `vde health` to produce a report on every supported host OS
  So that infrastructure problems are visible instead of aborting silently

  @health @linux-portability
  Scenario: Health check produces a report instead of aborting
    When I execute "bin/vde health"
    Then the output should contain "VDE Health Report"
    And the output should contain "Overall Status:"

  # A measurement that fails must be reported as a failed check, never as a
  # plausible healthy value. Each scenario breaks exactly one host tool.
  # The "invoked with" stubs match the literal argument ("-aq", "--filter"):
  # if bin/vde-health changes how it calls `docker ps`, update the argument here.

  @health @failed-measurement
  Scenario: Healthy measurements are not reported as undeterminable
    When I execute "bin/vde health"
    Then the output should contain "VDE Health Report"
    And the command output should not contain "could not be determined"

  @health @failed-measurement
  Scenario: Container listing failure is reported, not read as zero containers
    Given the "docker" command fails when invoked with "-aq"
    When I execute "bin/vde health"
    Then the output should contain "[MAJOR] containers"
    And the output should contain "could not be determined"
    And the command output should not contain "No containers found"

  @health @failed-measurement
  Scenario: Unhealthy-container query failure is reported, not read as zero unhealthy
    Given the "docker" command fails when invoked with "--filter"
    When I execute "bin/vde health"
    Then the output should contain "[MAJOR] containers"
    And the output should contain "could not be determined"

  @health @failed-measurement
  Scenario: Disk usage failure is reported, not read as an empty percentage
    Given the "df" command fails
    When I execute "bin/vde health"
    Then the output should contain "[MAJOR] disk"
    And the output should contain "could not be determined"
    And the command output should not contain "Disk usage is %"

  # Linux memory path (free(1)); the macOS path uses vm_stat instead.
  @health @failed-measurement
  Scenario: Memory usage failure is reported, not read as healthy
    Given the "free" command fails
    When I execute "bin/vde health"
    Then the output should contain "[MAJOR] memory"
    And the output should contain "could not be determined"
