# language: en
@critical-infrastructure @core-infrastructure
Feature: Critical Infrastructure — Spec Invariants
  As the VDE system
  I need to enforce the technical invariants defined in VDE-SPEC.md
  So that every layer of the implementation is correct and predictable

  # ── Naming Convention (spec section 14.4, 3.9) ──

  Scenario: vde_get_container_name adds vde- prefix to raw name
    When I call vde_get_container_name with "python"
    Then the result should be "vde-python"

  Scenario: vde_get_container_name is idempotent on already-prefixed name
    When I call vde_get_container_name with "vde-python"
    Then the result should be "vde-python"

  Scenario: vde_get_ssh_host adds vde- prefix to raw name
    When I call vde_get_ssh_host with "rust"
    Then the result should be "vde-rust"

  Scenario: vde_normalize_name strips vde- prefix
    When I call vde_normalize_name with "vde-python"
    Then the result should be "python"

  Scenario: vde_normalize_name is idempotent on raw name
    When I call vde_normalize_name with "python"
    Then the result should be "python"

  Scenario: All existing compose files use vde- prefixed container names
    Given all VM configs are loaded from vm-types.json
    Then every VM compose file should have container_name starting with "vde-"

  # ── Port Range Constants (spec section 3.1) ──

  Scenario: Language VM port range starts at 2200
    When I read VDE_LANG_PORT_START from vde-constants
    Then the value should be "2200"

  Scenario: Language VM port range ends at 2299
    When I read VDE_LANG_PORT_END from vde-constants
    Then the value should be "2299"

  Scenario: Service VM port range starts at 2400
    When I read VDE_SVC_PORT_START from vde-constants
    Then the value should be "2400"

  Scenario: Service VM port range ends at 2499
    When I read VDE_SVC_PORT_END from vde-constants
    Then the value should be "2499"

  # ── Template Rendering (spec section 5) ──

  Scenario: Language template renders container_name with vde- prefix
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should contain "container_name: vde-testlang"

  Scenario: Language template renders correct SSH port mapping
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should contain "2250:22"

  Scenario: Language template uses vde-net network
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should contain "vde-net"

  Scenario: Language template sets restart: unless-stopped
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should contain "restart: unless-stopped"

  Scenario: Language template no unreplaced placeholders remain
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should NOT contain "{{NAME}}"
    And the rendered output should NOT contain "{{SSH_PORT}}"

  Scenario: SSH entry template renders Host with vde- prefix
    When I render the SSH entry template with VM_NAME="python" SSH_PORT="2213"
    Then the rendered output should contain "Host vde-python"

  Scenario: SSH entry template renders correct port
    When I render the SSH entry template with VM_NAME="python" SSH_PORT="2213"
    Then the rendered output should contain "Port 2213"

  Scenario: SSH entry template uses devuser
    When I render the SSH entry template with VM_NAME="python" SSH_PORT="2213"
    Then the rendered output should contain "User devuser"

  Scenario: SSH entry template references VDE known_hosts path
    When I render the SSH entry template with VM_NAME="python" SSH_PORT="2213"
    Then the rendered output should contain "UserKnownHostsFile ~/.ssh/vde/known_hosts"

  Scenario: SSH entry template includes ForwardAgent yes
    When I render the SSH entry template with VM_NAME="python" SSH_PORT="2213"
    Then the rendered output should contain "ForwardAgent yes"

  # ── SSH Isolation (spec section 14.3) ──

  Scenario: VDE SSH directory is isolated at ~/.ssh/vde/ not ~/.ssh/
    When I check the VDE SSH directory path from vde-constants
    Then the VDE_SSH_DIR should end with ".ssh/vde"

  Scenario: VDE SSH config path is inside ~/.ssh/vde/
    When I check the VDE SSH config path from vde-constants
    Then the VDE_SSH_CONFIG should end with ".ssh/vde/config"

  Scenario: VDE SSH known_hosts path is inside ~/.ssh/vde/
    When I check the VDE SSH known_hosts path from vde-constants
    Then the VDE_SSH_KNOWN_HOSTS should end with ".ssh/vde/known_hosts"

  # ── Filesystem Layout (spec section 9) ──

  Scenario: configs/docker/ directory exists
    Then VDE directory "configs/docker" should exist

  Scenario: scripts/ directory exists
    Then VDE directory "scripts" should exist

  Scenario: scripts/lib/ directory exists
    Then VDE directory "scripts/lib" should exist

  Scenario: scripts/templates/ directory exists
    Then VDE directory "scripts/templates" should exist

  Scenario: scripts/data/ directory exists
    Then VDE directory "scripts/data" should exist

  Scenario: backup/ directory exists
    Then VDE directory "backup" should exist

  Scenario: .cache/ directory exists
    Then VDE directory ".cache" should exist

  Scenario: vm-types.json data file exists
    Then VDE file "scripts/data/vm-types.json" should exist

  Scenario: compose-language.yml template exists
    Then VDE file "scripts/templates/compose-language.yml" should exist

  Scenario: compose-service.yml template exists
    Then VDE file "scripts/templates/compose-service.yml" should exist

  Scenario: ssh-entry.txt template exists
    Then VDE file "scripts/templates/ssh-entry.txt" should exist

  # ── Service VM Template Rendering (spec section 5.2) ──

  Scenario: Service template renders container_name with vde- prefix
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "container_name: vde-testsvc"

  Scenario: Service template renders correct SSH port mapping
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "2450:22"

  Scenario: Service template uses vde-net network
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "vde-net"

  Scenario: Service template sets restart: unless-stopped
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "restart: unless-stopped"

  Scenario: Service template no unreplaced placeholders remain
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should NOT contain "{{NAME}}"
    And the rendered output should NOT contain "{{SSH_PORT}}"

  Scenario: Service template includes vde.type label
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "vde.type=service"

  Scenario: Service template includes vde.name label
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "vde.name=testsvc"

  # ── Permission Policy (spec section 14.1) ──

  Scenario: .cache directory has strict permissions (0700)
    Then VDE directory ".cache" should have permissions 0700

  Scenario: env-files directory has strict permissions (0700)
    Then VDE directory "env-files" should have permissions 0700

  Scenario: backup directory has strict permissions (0700)
    Then VDE directory "backup" should have permissions 0700

  Scenario: VDE SSH config file has strict permissions (0600)
    Then VDE SSH file "config" should have permissions 0600

  Scenario: VDE SSH known_hosts file has strict permissions (0600)
    Then VDE SSH file "known_hosts" should have permissions 0600

  # ── Network Isolation (spec section 14.2) ──

  @requires-docker-host
  Scenario: vde-net Docker network exists
    Then the Docker network "vde-net" should exist

  @requires-docker-host
  Scenario: vde-net network is a bridge network
    Then the Docker network "vde-net" should be a bridge network

  # ── Return Codes (spec section 3.1, 7.2) ──

  Scenario: VDE_ERR_EXISTS is defined as 6
    When I read VDE_ERR_EXISTS from vde-constants
    Then the value should be "6"

  Scenario: VDE_ERR_NOT_FOUND is defined as 3
    When I read VDE_ERR_NOT_FOUND from vde-constants
    Then the value should be "3"

  Scenario: VDE_ERR_INVALID_INPUT is defined as 2
    When I read VDE_ERR_INVALID_INPUT from vde-constants
    Then the value should be "2"
