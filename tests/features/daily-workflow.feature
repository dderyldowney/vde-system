# language: en
Feature: Daily Development Workflow
  As a developer
  I want to manage multiple development environments seamlessly
  So that I can switch between projects and languages efficiently

  # Background: Developer arrives at workstation
  Background:
    Given VDE is installed on my system
    And Docker is running
    And I have SSH keys configured

  # Morning: Start my development environment
  Scenario: Start my daily development VMs
    Given I previously created VMs for "python", "rust", and "postgres"
    When I run "start-virtual python rust postgres"
    Then all three VMs should be running
    And I should be able to SSH to "python-dev" on allocated port
    And I should be able to SSH to "rust-dev" on allocated port
    And PostgreSQL should be accessible from language VMs

  # Create a new project workspace
  Scenario: Create a new language VM for a project
    Given I need to start a "golang" project
    But I don't have a "go" VM yet
    When I run "create-virtual-for go"
    Then a go development environment should be created
    And docker-compose.yml should be configured for go
    And SSH config entry for "go-dev" should be added
    And projects/go directory should be created
    And I can start the VM with "start-virtual go"

  # Switch between different language projects
  Scenario: Switch from Python to Rust project
    Given I have "python" VM running
    And I have "rust" VM created but not running
    When I want to work on a Rust project instead
    And I run "start-virtual rust"
    Then both "python" and "rust" VMs should be running
    And I can SSH to both VMs from my terminal
    And each VM has isolated project directories

  # Access PostgreSQL database from language VM
  Scenario: Connect to PostgreSQL from Python VM
    Given "postgres" VM is running
    And "python" VM is running
    When I SSH into "python-dev"
    And I run "psql -h postgres -U devuser"
    Then I should be connected to PostgreSQL
    And I can query the database
    And the connection uses the container network

  # Stop VMs when done working
  Scenario: Shut down all VMs at end of day
    Given multiple VMs are running
    When I run "shutdown-virtual all"
    Then all VMs should be stopped
    But VM configurations should remain for next session
    And docker ps should show no VDE containers running

  # Work on multiple projects simultaneously
  Scenario: Run multiple language VMs for a polyglot project
    Given I have a project using Python, JavaScript, and Redis
    When I run "start-virtual python js redis"
    Then all three VMs should be running
    And Python VM can make HTTP requests to JavaScript VM
    And Python VM can connect to Redis
    And each VM can access shared project directories

  # Rebuild VM after Dockerfile changes
  Scenario: Rebuild a VM after modifying its Dockerfile
    Given I have modified the python Dockerfile to add a new package
    And "python" VM is currently running
    When I run "start-virtual python --rebuild"
    Then the VM should be rebuilt with the new Dockerfile
    And the VM should be running after rebuild
    And the new package should be available in the VM

  # Clean up unused VMs
  Scenario: Remove VM I no longer need
    Given I have an old "ruby" VM I don't use anymore
    When I run the removal process for "ruby"
    Then the docker-compose.yml should be deleted
    And SSH config entry should be removed
    But the projects/ruby directory should be preserved
    And I can recreate it later if needed

  # Add a new language to VDE
  Scenario: Add support for a new language
    Given VDE doesn't support "zig" yet
    When I run "add-vm-type --type lang --display 'Zig' zig 'apt-get install -y zig'"
    Then "zig" should be available as a VM type
    And I can create a zig VM with "create-virtual-for zig"
    And zig should appear in "list-vms" output

  # View all available VMs
  Scenario: Check what VMs I can create
    Given I want to see what development environments are available
    When I run "list-vms"
    Then all language VMs should be listed with aliases
    And all service VMs should be listed with ports
    And I can see which VMs are created vs just available

  # Quick status check
  Scenario: Quickly check what's running
    Given I have several VMs configured
    When I run "list-vms --created"
    Then I should see only VMs that have been created
    And their status (running/stopped) should be shown
    And I can identify which VMs to start or stop

  # Automated testing environment
  Scenario: Create test environment with database
    Given I need to test my application with a real database
    When I create "postgres" and "redis" service VMs
    And I create my language VM (e.g., "python")
    And I start all three VMs
    Then my application can connect to test database
    And test data is isolated from development data
    And I can stop test VMs independently

  # Port conflicts are handled automatically
  Scenario: VDE handles port conflicts gracefully
    Given a system service is using port 2200
    When I create a new language VM
    Then VDE should allocate the next available port (2201)
    And the VM should work correctly on the new port
    And SSH config should reflect the correct port
