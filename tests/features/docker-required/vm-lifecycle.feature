# language: en
@user-guide-first-vm
Feature: VM Lifecycle Management
  As a developer
  I want to create, start, stop, and manage development VMs
  So that I can work in isolated development environments

  @requires-docker-host
  Scenario: Create a new language VM
    Given the VM "zig" is defined as a language VM with install command "apt-get install -y zig"
    And no VM configuration exists for "zig"
    When I run "create-virtual-for zig"
    Then a docker-compose.yml file should be created at "configs/docker/zig/docker-compose.yml"
    And the docker-compose.yml should contain SSH port mapping
    And SSH config entry should exist for "zig-dev"
    And projects directory should exist at "projects/zig"
    And logs directory should exist at "logs/zig"

  @requires-docker-host
  Scenario: Create a new service VM with custom port
    Given the VM "rabbitmq" is defined as a service VM with port "5672"
    And no VM configuration exists for "rabbitmq"
    When I run "create-virtual-for rabbitmq"
    Then a docker-compose.yml file should be created at "configs/docker/rabbitmq/docker-compose.yml"
    And the docker-compose.yml should contain service port mapping "5672"
    And data directory should exist at "data/rabbitmq"

  @requires-docker-host
  Scenario: Start a created VM
    Given VM "python" has been created
    And VM "python" is not running
    When I run "start-virtual python"
    Then VM "python" should be running
    And SSH should be accessible on allocated port

  @requires-docker-host
  Scenario: Start multiple VMs
    Given VM "python" has been created
    And VM "rust" has been created
    And neither VM is running
    When I run "start-virtual python rust"
    Then VM "python" should be running
    And VM "rust" should be running
    And each VM should have a unique SSH port

  @requires-docker-host
  Scenario: Start all VMs
    Given VM "python" has been created
    And VM "rust" has been created
    And VM "postgres" has been created
    And none of the VMs are running
    When I run "start-virtual all"
    Then all created VMs should be running

  @requires-docker-host
  Scenario: Stop a running VM
    Given VM "python" is running
    When I run "shutdown-virtual python"
    Then VM "python" should not be running
    But VM configuration should still exist

  @requires-docker-host
  Scenario: Stop all running VMs
    Given VM "python" is running
    And VM "rust" is running
    When I run "shutdown-virtual all"
    Then no VMs should be running

  @requires-docker-host
  Scenario: Restart a VM
    Given VM "python" is running
    When I run "shutdown-virtual python && start-virtual python"
    Then VM "python" should be running
    And the VM should have a fresh container instance

  @requires-docker-host
  Scenario: Rebuild a VM with --rebuild flag
    Given VM "python" is running
    When I run "start-virtual python --rebuild"
    Then VM "python" should be running
    And the container should be rebuilt from the Dockerfile

  @requires-docker-host
  Scenario: Cannot start non-existent VM
    Given VM "nonexistent" is not created
    When I run "start-virtual nonexistent"
    Then the command should fail with error "Unknown VM: nonexistent"

  @requires-docker-host
  Scenario: Cannot create duplicate VM
    Given VM "python" has been created
    When I run "create-virtual-for python"
    Then the command should fail with error "already exists"

  Scenario: List all predefined VM types
    Given VM types are loaded
    When I run "list-vms"
    Then all language VMs should be listed
    And all service VMs should be listed
    And aliases should be shown

  Scenario: List only language VMs
    Given VM types are loaded
    When I run "list-vms --lang"
    Then only language VMs should be listed
    And service VMs should not be listed

  Scenario: List only service VMs
    Given VM types are loaded
    When I run "list-vms --svc"
    Then only service VMs should be listed
    And language VMs should not be listed

  Scenario: Filter VMs by name
    Given VM types are loaded
    When I run "list-vms python"
    Then only VMs matching "python" should be listed

  @requires-docker-host
  Scenario: Remove a VM
    Given VM "python" has been created
    When I run "remove-virtual python"
    Then docker-compose.yml should not exist at "configs/docker/python/docker-compose.yml"
    And SSH config entry for "python-dev" should be removed
    And projects directory should still exist at "projects/python"
    But the VM should be marked as not created

  Scenario: Add a new VM type
    When I run "add-vm-type --type lang --display 'Zig Language' zig 'apt-get install -y zig'"
    Then "zig" should be in known VM types
    And VM type "zig" should have type "lang"
    And VM type "zig" should have display name "Zig Language"

  Scenario: Add VM type with aliases
    When I run "add-vm-type --type lang --display 'JavaScript' js 'apt-get install -y nodejs' 'node,nodejs'"
    Then "js" should be in known VM types
    And "js" should have aliases "node,nodejs"
    And "node" should resolve to "js"
    And "nodejs" should resolve to "js"
