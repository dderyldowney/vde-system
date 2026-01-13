Feature: Daily Development Workflow
  As documented in the VDE development workflows
  I want to follow the same patterns that are documented
  So that the tests match the documentation exactly

  Scenario: Example 1 - Python API with PostgreSQL Setup
    Given I am following the documented Python API workflow
    When I plan to create a Python VM
    Then the plan should include the create_vm intent
    And the plan should include the Python VM

  Scenario: Example 1 - Create PostgreSQL for Python API
    Given I have planned to create Python
    When I plan to create PostgreSQL
    Then the plan should include the create_vm intent
    And the plan should include the PostgreSQL VM

  Scenario: Example 1 - Start Both Python and PostgreSQL
    Given I have created Python and PostgreSQL VMs
    When I plan to start both VMs
    Then the plan should include the start_vm intent
    And the plan should include both Python and PostgreSQL VMs

  Scenario: Example 1 - Get Connection Info for Python
    Given I need to connect to the Python VM
    When I ask for connection information
    Then the plan should include the connect intent
    And the plan should include the Python VM

  Scenario: Example 1 - Verify PostgreSQL Accessibility
    Given I have started the PostgreSQL VM
    When I check if postgres exists
    Then the VM should be recognized as a valid VM type
    And it should be marked as a service VM

  Scenario: Example 2 - Full-Stack JavaScript with Redis
    Given I am following the documented JavaScript workflow
    When I plan to create JavaScript and Redis VMs
    Then the plan should include both VMs
    And the JavaScript VM should use the js canonical name

  Scenario: Example 2 - Resolve Node.js Alias
    Given I want to use the Node.js name
    When I resolve the nodejs alias
    Then it should resolve to js
    And I can use either name in commands

  Scenario: Example 3 - Microservices Architecture Setup
    Given I am creating a microservices architecture
    When I plan to create Python, Go, Rust, PostgreSQL, and Redis
    Then the plan should include all five VMs
    And each VM should be included in the VM list

  Scenario: Example 3 - Start All Microservice VMs
    Given I have created the microservice VMs
    When I plan to start them all
    Then the plan should include the start_vm intent
    And all microservice VMs should be included

  Scenario: Example 3 - Verify All Microservice VMs Exist
    Given I have created microservices
    When I check for each service VM
    Then Python should exist as a language VM
    And Go should exist as a language VM
    And Rust should exist as a language VM
    And PostgreSQL should exist as a service VM
    And Redis should exist as a service VM

  Scenario: Daily Workflow - Morning Setup
    Given I am starting my development day
    When I plan to start Python, PostgreSQL, and Redis
    Then the plan should include all three VMs
    And the plan should use the start_vm intent

  Scenario: Daily Workflow - Check Status During Development
    Given I am actively developing
    When I ask what's running
    Then the plan should include the status intent
    And I should be able to see running VMs

  Scenario: Daily Workflow - Connect to Primary VM
    Given I need to work in my primary development environment
    When I ask how to connect to Python
    Then the plan should provide connection details
    And the plan should include the Python VM

  Scenario: Daily Workflow - Evening Cleanup
    Given I am done with development for the day
    When I plan to stop everything
    Then the plan should include the stop_vm intent
    And the plan should apply to all running VMs

  Scenario: Troubleshooting - Step 1 Check Status
    Given something isn't working correctly
    When I check the status
    Then I should receive status information
    And I should see which VMs are running

  Scenario: Troubleshooting - Step 3 Restart with Rebuild
    Given I need to rebuild a VM to fix an issue
    When I plan to rebuild Python
    Then the plan should include the restart_vm intent
    And the plan should set rebuild=true flag

  Scenario: Troubleshooting - Step 4 Get Connection Info
    Given I need to debug inside a container
    When I ask to connect to Python
    Then the plan should include the connect intent
    And I should receive SSH connection information

  Scenario: New Project Setup - Discover Available VMs
    Given I am setting up a new project
    When I ask what VMs can I create
    Then the plan should include the list_vms intent
    And I should see all available VM types

  Scenario: New Project Setup - Choose Full Stack
    Given I want a Python API with PostgreSQL
    When I plan to create Python and PostgreSQL
    Then both VMs should be included in the plan
    And the plan should use the create_vm intent

  Scenario: New Project Setup - Start Development Stack
    Given I have created my VMs
    When I plan to start Python and PostgreSQL
    Then both VMs should start
    And they should be able to communicate

  Scenario: Adding Cache Layer - Create Redis
    Given I have an existing Python and PostgreSQL stack
    When I plan to add Redis
    Then the plan should include the create_vm intent
    And the Redis VM should be included

  Scenario: Adding Cache Layer - Start Redis
    Given I have created the Redis VM
    When I plan to start Redis
    Then the plan should include the start_vm intent
    And Redis should start without affecting other VMs

  Scenario: Switching Projects - Stop Current Project
    Given I am working on one project
    When I plan to stop all VMs
    Then all running VMs should be stopped
    And I should be ready to start a new project

  Scenario: Switching Projects - Start New Project
    Given I have stopped my current project
    When I plan to start Go and MongoDB
    Then the new project VMs should start
    And only the new project VMs should be running

  Scenario: Team Onboarding - Explore Languages
    Given I am a new team member
    When I ask to list all languages
    Then I should see only language VMs
    And service VMs should not be included

  Scenario: Team Onboarding - Get Connection Help
    Given I am new to the team
    When I ask how to connect to Python
    Then I should receive clear connection instructions
    And I should understand how to access the VM

  Scenario: Team Onboarding - Understand System
    Given I am learning the VDE system
    When I ask for help
    Then I should see available commands
    And I should understand what I can do

  Scenario: Starting Already Running VM
    Given I have a Python VM that is already running
    When I plan to start Python
    Then the plan should be generated
    And execution would detect the VM is already running
    And I would be notified that it's already running

  Scenario: Stopping Already Stopped VM
    Given I have a stopped PostgreSQL VM
    When I plan to stop PostgreSQL
    Then the plan should be generated
    And execution would detect the VM is not running
    And I would be notified that it's already stopped

  Scenario: Creating Existing VM
    Given I already have a Go VM configured
    When I plan to create Go again
    Then the plan should be generated
    And execution would detect the VM already exists
    And I would be notified of the existing VM

  Scenario: Documentation Accuracy - Verify Examples Work
    Given the documentation shows specific VM examples
    When I verify the documented VMs
    Then Python should be a valid VM type
    And JavaScript should be a valid VM type
    And all microservice VMs should be valid

  Scenario: Performance - Quick Plan Generation
    Given I need to plan my daily workflow
    When I generate plans for morning setup, checks, and cleanup
    Then all plans should be generated quickly
    And the total time should be under 500ms
