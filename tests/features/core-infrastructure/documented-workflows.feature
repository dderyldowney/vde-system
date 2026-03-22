@parser
Feature: Daily Development Workflow
  As documented in the VDE development workflows
  I want to follow the same patterns that are documented
  So that the tests match the documentation exactly

  @user-guide-cluster
  Scenario: Example 1 - Python API with PostgreSQL Setup
    Given I am following the documented Python API workflow
    When I parse "create python"
    Then intent should be "create_vm"
    And VMs should include "python"

  @user-guide-cluster
  Scenario: Example 1 - Create PostgreSQL for Python API
    Given I am following the documented Python API workflow
    When I parse "create postgresql"
    Then intent should be "create_vm"
    And VMs should include "postgresql"

  @user-guide-cluster
  Scenario: Example 1 - Start Both Python and PostgreSQL
    Given I am following the documented Python API workflow
    When I parse "start python and postgresql"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgresql"

  @user-guide-connecting
  Scenario: Example 1 - Get Connection Info for Python
    Given I need to connect to the Python VM
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  @user-guide-databases
  Scenario: Example 1 - Verify PostgreSQL Accessibility
    Given I am following the documented workflow
    When I parse "check postgresql"
    Then intent should be "status"
    And VMs should include "postgresql"

  @user-guide-cluster
  Scenario: Example 2 - Full-Stack JavaScript with Redis
    Given I am following the documented JavaScript workflow
    When I parse "create javascript and redis"
    Then intent should be "create_vm"
    And VMs should include "javascript"
    And VMs should include "redis"

  @user-guide-understanding
  Scenario: Example 2 - Resolve Node.js Alias
    Given I want to use the Node.js name
    When I parse "use nodejs"
    Then intent should be "create_vm"
    And VMs should include "nodejs"

  @user-guide-cluster
  Scenario: Example 3 - Microservices Architecture Setup
    Given I am following the documented microservices workflow
    When I parse "create python, go, rust, postgresql and redis"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "go"
    And VMs should include "rust"
    And VMs should include "postgresql"
    And VMs should include "redis"

  @user-guide-cluster
  Scenario: Example 3 - Start All Microservice VMs
    Given I am following the documented microservices workflow
    When I parse "start all VMs"
    Then intent should be "start_vm"
    And VMs should include all known VMs

  @user-guide-cluster
  Scenario: Example 3 - Verify All Microservice VMs Exist
    Given I am following the documented microservices workflow
    When I parse "list service VMs"
    Then intent should be "list_vms"

  @user-guide-daily-workflow
  Scenario: Daily Workflow - Morning Setup
    Given I am starting my development day
    When I parse "start python, postgresql and redis"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgresql"
    And VMs should include "redis"

  @user-guide-daily-workflow
  Scenario: Daily Workflow - Check Status During Development
    Given I am following the documented workflow
    When I parse "what's running"
    Then intent should be "status"

  @user-guide-daily-workflow
  Scenario: Daily Workflow - Connect to Primary VM
    Given I am following the documented workflow
    When I parse "how do I connect to python"
    Then intent should be "connect"

  @user-guide-daily-workflow
  Scenario: Daily Workflow - Evening Cleanup
    Given I am following the documented workflow
    When I parse "stop everything"
    Then intent should be "stop_vm"

  @user-guide-troubleshooting
  Scenario: Troubleshooting - Step 1 Check Status
    Given I am following the documented workflow
    When I parse "what's running"
    Then intent should be "status"

  @user-guide-troubleshooting
  Scenario: Troubleshooting - Step 3 Restart with Rebuild
    Given I need to rebuild a VM to fix an issue
    When I parse "rebuild python"
    Then intent should be "restart_vm"
    And rebuild flag should be true

  @user-guide-troubleshooting
  Scenario: Troubleshooting - Step 4 Get Connection Info
    Given I need to debug inside a container
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  @user-guide-first-vm
  Scenario: New Project Setup - Discover Available VMs
    Given I am setting up a new project
    When I parse "what VMs can I create"
    Then intent should be "list_vms"

  @user-guide-first-vm
  Scenario: New Project Setup - Choose Full Stack
    Given I want a Python API with PostgreSQL
    When I parse "create python and postgresql"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "postgresql"

  @user-guide-more-languages
  @requires-docker-host
  Scenario: Adding Cache Layer - Create Redis
    Given I have an existing Python and PostgreSQL stack
    When I parse "create redis"
    Then intent should be "create_vm"
    And VMs should include "redis"

  @user-guide-more-languages
  @requires-docker-host
  Scenario: Adding Cache Layer - Start Redis
    Given I have an existing Python and PostgreSQL stack
    When I parse "start redis"
    Then intent should be "start_vm"
    And VMs should include "redis"

  @user-guide-daily-workflow
  Scenario: Switching Projects - Stop Current Project
    Given I am following the documented workflow
    When I parse "stop all VMs"
    Then intent should be "stop_vm"

  @user-guide-daily-workflow
  Scenario: Switching Projects - Start New Project
    Given I am following the documented workflow
    When I parse "start go and mongodb"
    Then intent should be "start_vm"

  @user-guide-understanding
  Scenario: Team Onboarding - Explore Languages
    Given I am following the documented workflow
    When I parse "help"
    Then intent should be "help"

  @user-guide-understanding
  Scenario: Team Onboarding - Get Connection Help
    Given I am following the documented workflow
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  @user-guide-understanding
  Scenario: Team Onboarding - Understand System
    Given I am following the documented workflow
    When I parse "help"
    Then intent should be "help"

  @user-guide-troubleshooting
  Scenario: Starting Already Running VM
    Given I have a Python VM that is already running
    When I parse "start python"
    Then intent should be "start_vm"
    And VMs should include "python"

  @user-guide-troubleshooting
  Scenario: Stopping Already Stopped VM
    Given I have a stopped PostgreSQL VM
    When I parse "stop postgresql"
    Then intent should be "stop_vm"
    And VMs should include "postgresql"

  @user-guide-troubleshooting
  Scenario: Creating Existing VM
    Given I already have a Go VM configured
    When I parse "create go"
    Then intent should be "create_vm"
    And VMs should include "go"

  @user-guide-understanding
  Scenario: Documentation Accuracy - Verify Examples Work
    Given the documentation shows specific VM examples
    When I parse "list all VMs"
    Then intent should be "list_vms"
