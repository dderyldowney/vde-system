# language: en
Feature: Port Management
  As a developer
  I want VDE to automatically allocate and manage SSH ports
  So that VMs don't have port conflicts and can be accessed via SSH

  Scenario: Allocate first available port for language VM
    Given no language VMs are created
    When I create a language VM
    Then the VM should be allocated port "2200"

  Scenario: Allocate sequential ports for multiple language VMs
    Given language VM "python" is allocated port "2200"
    When I create language VM "rust"
    Then "rust" should be allocated port "2201"

  Scenario: Allocate first available port for service VM
    Given no service VMs are created
    When I create a service VM
    Then the VM should be allocated port "2400"

  Scenario: Skip allocated ports when finding next available
    Given ports "2200", "2201", "2203" are allocated
    When I create a new language VM
    Then the VM should be allocated port "2202"

  Scenario: Port registry tracks all allocated ports
    Given VM "python" is allocated port "2200"
    And VM "rust" is allocated port "2201"
    When I query the port registry
    Then "python" should be mapped to port "2200"
    And "rust" should be mapped to port "2201"

  Scenario: Port registry persists across script invocations
    Given VM "python" is allocated port "2200"
    When I reload the VM types cache
    Then "python" should still be mapped to port "2200"

  Scenario: Detect host port collision during allocation
    Given a non-VDE process is listening on port "2200"
    When I create a new language VM
    Then the VM should NOT be allocated port "2200"
    And the VM should be allocated a different available port

  Scenario: Detect Docker port collision during allocation
    Given a Docker container is bound to host port "2201"
    When I create a new language VM
    Then the VM should NOT be allocated port "2201"

  Scenario: Atomic port reservation prevents race conditions
    Given two processes try to allocate ports simultaneously
    When both processes request the next available port
    Then each process should receive a unique port
    And no port should be allocated twice

  Scenario: Port ranges are respected
    Given language ports range from "2200" to "2299"
    And service ports range from "2400" to "2499"
    When I create a language VM
    Then the allocated port should be between "2200" and "2299"
    When I create a service VM
    Then the allocated port should be between "2400" and "2499"

  Scenario: Error when all ports in range are allocated
    Given all ports from "2200" to "2299" are allocated
    When I create a new language VM
    Then the command should fail with error "No available ports"

  Scenario: Clean up stale port locks
    Given a port lock is older than "300" seconds
    When I run port cleanup
    Then the stale lock should be removed
    And the port should be available for allocation

  Scenario: Port registry updates when VM is removed
    Given VM "python" is allocated port "2200"
    When I remove VM "python"
    Then port "2200" should be removed from registry
    And port "2200" should be available for new VMs
