@requires-docker-host
Feature: Concurrency & Stress Hardening
  @concurrency @stress @critical-path @fresh-vms
  Scenario: Parallel Ignition of multiple VMs
    Given the VDE system is initialized
    And I have a list of VM aliases: "python, postgres, redis"
    When I attempt to create and start these VMs simultaneously
    Then all VMs should be created successfully
    And all VMs should have unique SSH ports
    And there should be no lock file leftovers
    And all VMs should be reachable via SSH

  Scenario: Concurrent registry updates and port allocation
    Given the VDE system is initialized
    When I attempt to add multiple new VM types simultaneously
    Then all new VM types should be added successfully
    And the VDE registry should remain valid and uncorrupted
    And all new VM types should have unique SSH ports
    And I cleanup the stress VM types
