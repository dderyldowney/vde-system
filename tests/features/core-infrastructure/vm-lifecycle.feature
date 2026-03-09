# language: en
@core-suite
@user-guide-starting-stopping
Feature: VM Lifecycle Management
  As a developer
  I want to create, start, stop, and manage development VMs
  So that I can work in isolated development environments

  @requires-docker-host
  @user-guide-first-vm
  Scenario: Create a new language VM
    Given the VM "testlang" is defined as a language VM with install command "apt-get install -y curl"
    And no VM configuration exists for "testlang"
    When I run "create-virtual-for testlang"
    Then a docker-compose.yml file should be created at "configs/docker/testlang/docker-compose.yml"
    And the docker-compose.yml should contain SSH port mapping
    And projects directory should exist at "projects/testlang"
    And logs directory should exist at "logs/testlang"

  @requires-docker-host
  @user-guide-first-vm
  Scenario: Start a created VM
    Given VM "python" has been created
    And VM "python" is not running
    When I run "start-virtual python"
    Then VM "python" should be running
    And SSH should be accessible on allocated port

  @requires-docker-host
  @user-guide-cluster
  Scenario: Start multiple VMs
    Given VM "python" has been created
    And VM "rust" has been created
    And neither VM is running
    When I run "start-virtual python rust"
    Then VM "python" should be running
    And VM "rust" should be running
    And each VM should have a unique SSH port

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Stop a running VM
    Given VM "python" is running
    When I run "shutdown-virtual python"
    Then VM "python" should not be running
    And VM configuration should still exist

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Stop all running VMs
    Given VM "python" is running
    And VM "rust" is running
    When I run "shutdown-virtual all"
    Then no VMs should be running

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Restart a VM
    Given VM "python" is running
    When I run "shutdown-virtual python && start-virtual python"
    Then VM "python" should be running
    And the VM should have a fresh container instance

  @requires-docker-host
  @user-guide-troubleshooting
  Scenario: Rebuild a VM with --rebuild flag
    Given VM "python" is running
    When I run "start-virtual python --rebuild"
    Then VM "python" should be running
    And the container should be rebuilt from the Dockerfile

  @user-guide-understanding
  Scenario: List all predefined VM types
    Given VM types are loaded
    When I run "list-vms"
    Then all language VMs should be listed
    And all service VMs should be listed
    And aliases should be shown

  @user-guide-understanding
  Scenario: List only language VMs
    Given VM types are loaded
    When I run "list-vms --all --lang"
    Then only language VMs should be listed
    And service VMs should not be listed

  @user-guide-understanding
  Scenario: List only service VMs
    Given VM types are loaded
    When I run "list-vms --all --svc"
    Then only service VMs should be listed
    And language VMs should not be listed

  @user-guide-understanding
  Scenario: Filter VMs by name
    Given VM types are loaded
    When I run "list-vms python"
    Then only VMs matching "python" should be listed

  Scenario: Add a new VM type
    When I run "add-vm-type --type lang --display 'Test Language' testlang 'apt-get install -y curl'"
    Then "testlang" should be in known VM types
    And VM type "testlang" should have type "lang"
    And VM type "testlang" should have display name "Test Language"

  Scenario: Add VM type with aliases
    When I run "add-vm-type --type lang --display 'Test Lang Two' testlang2 'apt-get install -y curl' 'tl2,tlalias'"
    Then "testlang2" should be in known VM types
    And "testlang2" should have aliases "tl2,tlalias"
    And "tl2" should resolve to "testlang2"
    And "tlalias" should resolve to "testlang2"
