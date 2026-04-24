# VDE ARCHITECTURAL RECORD
# @forge (DNS Discovery Verification)
@advanced-orchestration @dns
Feature: Spoke-to-Spoke DNS Discovery
  As an Alor of the VDE
  I require Spokes to discover each other by canonical name
  So that multi-VM tech stacks can communicate without hardcoded IPs

  Background: Core Services are Active
    Given the VDE system is healthy
    And the Hub is synchronized to version 1.4.1
    And "python" is running
    And "postgres" is running
Scenario: ICMP Heartbeat Discovery (Prefixed Name)
  When I execute "ping -c 3 vde-postgres" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "64 bytes from"

Scenario: ICMP Heartbeat Discovery (Short Alias)
  When I execute "ping -c 3 postgres" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "64 bytes from"

Scenario: Canonical Name Resolution (Dual Verification)
  When I execute "nslookup vde-postgres" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "vde-postgres"
  When I execute "nslookup postgres" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "postgres"

Scenario: Service Bridge Connectivity (Short Alias TCP)
  When I execute "nc -zv postgres 5432" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "succeeded"

Scenario: Sovereign Bridge Resolution (Hub-to-Spoke)
  When I execute "ping -c 3 vde-host" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "64 bytes from"
  When I execute "ping -c 3 host" inside "python" as "devuser"
  Then the exit code should be 0
  And the output should contain "64 bytes from"

