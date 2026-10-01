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
