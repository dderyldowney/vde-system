# language: en
@vm-lifecycle
Feature: VM Full Lifecycle Critical Path

  Scenario: Full VM lifecycle for Python development environment
    Given no running VM instance exists for "python"
    When I run "vde create python"
    Then a docker-compose.yml file should be created at "configs/docker/python/docker-compose.yml"
    And the docker-compose.yml should contain SSH port mapping
    When I run "vde start python"
    Then SSH config entry should exist for "vde-python"
    Then VM "python" should be running
    And SSH should be accessible on allocated port
    And SSH keys should be generated if none exist
    And public key should be copied to VM's authorized_keys
    When I SSH to "vde-python"
    Then I should connect to the Python VM
    And I should be logged in as devuser
    And I should have a zsh shell
    And workspace should be mounted at ~/workspace
    When I run "vde stop python"
    Then VM "python" should not be running
    But VM configuration should still exist
    When I run "vde start python"
    Then VM "python" should be running
    And SSH connection should still work
    When I run "vde remove python"
    Then container should be gone
    And SSH config entry should be preserved
    And VM configuration should still exist
