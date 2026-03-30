# language: en
@vm-lifecycle
Feature: Critical Path — VM Lifecycle
  As a developer
  I want to create, start, stop, and use VMs via the vde CLI
  So that the primary user workflows defined in VDE-SPEC.md section 4 function correctly

  # ── VM Config Structure (spec sections 4.1, 5.1, 5.2) ──

  Scenario: Language VM docker-compose.yml has correct container name
    Given VM "python" config exists at "configs/docker/languages/python/docker-compose.yml"
    Then the compose file should contain "container_name: vde-python"

  Scenario: Service VM docker-compose.yml has correct container name
    Given VM "postgres" config exists at "configs/docker/services/postgres/docker-compose.yml"
    Then the compose file should contain "container_name: vde-postgres"

  Scenario: VM docker-compose.yml uses vde-net network
    Given VM "python" config exists at "configs/docker/languages/python/docker-compose.yml"
    Then the compose file should contain "vde-net"

  Scenario: VM docker-compose.yml has restart: unless-stopped
    Given VM "python" config exists at "configs/docker/languages/python/docker-compose.yml"
    Then the compose file should contain "restart: unless-stopped"

  Scenario: Service VM docker-compose.yml exposes service port
    Given VM "redis" config exists at "configs/docker/services/redis/docker-compose.yml"
    Then the compose file should contain "6379:6379"

  # ── Port Range Enforcement (spec section 10) ──

  Scenario: All language VMs have SSH ports in range 2200-2399
    Given all language VM configs are loaded from vm-types.json
    Then every language VM compose file should have SSH port between 2200 and 2399

  Scenario: All service VMs have SSH ports in range 2400-2499
    Given all service VM configs are loaded from vm-types.json
    Then every service VM compose file should have SSH port between 2400 and 2499

  Scenario: No two VMs share the same SSH port
    Given all VM configs are loaded from vm-types.json
    Then all configured VMs should have unique SSH ports in their compose files

  # ── CLI Commands (spec section 4.1) ──

  Scenario: vde list-vms shows all spec-defined language VMs
    When I run the list-vms script with "--all"
    Then the output should contain "python"
    And the output should contain "rust"
    And the output should contain "go"

  Scenario: vde list-vms shows all spec-defined service VMs
    When I run the list-vms script with "--all"
    Then the output should contain "postgres"
    And the output should contain "redis"

  Scenario: vde create returns VDE_ERR_EXISTS=6 for existing VM
    When I run vde-cli "create python"
    Then the exit code should be 6

  Scenario: vde create returns VDE_ERR_EXISTS=6 for existing service VM
    When I run vde-cli "create redis"
    Then the exit code should be 6

  # ── Docker-required scenarios (spec section 4.1) ──

  @requires-docker-host
  Scenario: vde start runs a VM container with correct name
    When I run vde-cli "start python"
    Then container "vde-python" should be running

  @requires-docker-host
  Scenario: vde stop stops a running VM container
    Given container "vde-python" is running
    When I run vde-cli "stop python"
    Then container "vde-python" should not be running
    And "configs/docker/languages/python/docker-compose.yml" should still exist
