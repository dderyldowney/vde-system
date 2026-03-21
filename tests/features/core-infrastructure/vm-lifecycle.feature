# language: en
@core-infrastructure
@user-guide-starting-stopping
Feature: VM Lifecycle Management
  As a developer
  I want to create, start, stop, and manage development VMs via the vde command
  So that I can work in isolated development environments

  @requires-docker-host
  @user-guide-first-vm
  Scenario: Create a new language VM
    Given the VM "elixir" is defined as a language VM with install command "apt-get update -y && apt-get install -y elixir erlang"
    And no VM configuration exists for "elixir"
    When I run "vde create elixir"
    Then a docker-compose.yml file should be created at "configs/docker/elixir/docker-compose.yml"
    And the docker-compose.yml should contain SSH port mapping
    And SSH config entry should exist for "vde-elixir"
    And projects directory should exist at "projects/elixir"
    And logs directory should exist at "logs/elixir"

  @requires-docker-host
  @user-guide-cluster
  Scenario: Create a new service VM with custom port
    Given the VM "rabbitmq" is defined as a service VM with port "5672"
    And no VM configuration exists for "rabbitmq"
    When I run "vde create rabbitmq"
    Then a docker-compose.yml file should be created at "configs/docker/rabbitmq/docker-compose.yml"
    And the docker-compose.yml should contain service port mapping "5672"
    And data directory should exist at "data/rabbitmq"

  @requires-docker-host
  @user-guide-first-vm
  Scenario: Start a created VM
    Given VM "python" has been created
    And VM "python" is not running
    When I run "vde start python"
    Then VM "python" should be running
    And SSH should be accessible on allocated port

  @requires-docker-host
  @user-guide-cluster
  Scenario: Start multiple VMs
    Given VM "python" has been created
    And VM "rust" has been created
    And neither VM is running
    When I run "vde start python rust"
    Then VM "python" should be running
    And VM "rust" should be running
    And each VM should have a unique SSH port

  @requires-docker-host
  @user-guide-daily-workflow
  Scenario: Start all VMs
    Given VM "python" has been created
    And VM "rust" has been created
    And VM "postgres" has been created
    And none of the VMs are running
    When I run "vde start all"
    Then all created VMs should be running

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Stop a running VM
    Given VM "python" is running
    When I run "vde stop python"
    Then VM "python" should not be running
    But VM configuration should still exist

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Stop all running VMs
    Given VM "python" is running
    And VM "rust" is running
    When I run "vde stop all"
    Then no VMs should be running

  @requires-docker-host
  @user-guide-starting-stopping
  Scenario: Restart a VM
    Given VM "python" is running
    When I run "vde restart python"
    Then VM "python" should be running
    And the VM should have a fresh container instance

  @requires-docker-host
  Scenario: Cannot start non-existent VM
    Given VM "nonexistent" is not created
    When I run "vde start nonexistent"
    Then the command should fail with error "Unknown VM: nonexistent"

  @requires-docker-host
  Scenario: Cannot create duplicate VM
    Given VM "python" has been created
    When I run "vde create python"
    Then the command should fail with error "already exists"

  @user-guide-understanding
  Scenario: List all predefined VM types
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  @user-guide-understanding
  Scenario: List only language VMs
    Given I am following the documented workflow
    When I parse "list language VMs"
    Then intent should be "list_vms"
    And filter should be "lang"

  @user-guide-understanding
  Scenario: List only service VMs
    Given I am following the documented workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"
    And filter should be "svc"

  @user-guide-understanding
  Scenario: Filter VMs by name
    Given I am following the documented workflow
    When I parse "list all VMs"
    Then intent should be "list_vms"

  @requires-docker-host
  Scenario: Remove a VM
    Given VM "python" has been created
    When I run "vde remove python"
    Then SSH config entry should be preserved
    And projects directory should still exist at "projects/python"
    But container should be gone

  Scenario: Add a new VM type
    When I run "vde add mylang --type lang --display 'My Language' --install 'apt-get install -y curl'"
    Then "mylang" should be in known VM types
    And VM type "mylang" should have type "lang"
    And VM type "mylang" should have display name "My Language"

  Scenario: Add VM type with aliases
    When I run "vde add js --type lang --display 'JavaScript' --install 'apt-get install -y nodejs' --aliases 'node,nodejs'"
    Then "js" should be in known VM types
    And "js" should have aliases "node,nodejs"
    And "node" should resolve to "js"
    And "nodejs" should resolve to "js"
