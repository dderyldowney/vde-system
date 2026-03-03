# language: en
@user-guide-internal
Feature: Natural Language Commands
  As a developer using VDE
  I want to control my environment using natural language
  So I don't have to remember specific command syntax

  @requires-docker-host
  Scenario: Simple intent commands
    Given I want to perform common actions
    When I say "start python"
    Then the system should understand I want to start the Python VM
    And the appropriate action should be taken

  @requires-docker-host
  Scenario: Natural language variations
    Given I can phrase commands in different ways
    When I say "launch the golang container"
    Then the system should understand I want to start the Go VM
    And the Go VM should start

  @requires-docker-host
  Scenario: Multiple VMs in one command
    Given I need to work with multiple environments
    When I say "start python and postgres"
    Then both VMs from my command should start

  @requires-docker-host
  Scenario: Using aliases instead of canonical names
    Given I know a VM by its alias
    When I say "create nodejs environment"
    Then the system should understand I want to create the JavaScript VM
    And the JavaScript VM from my command should be created

  Scenario: Descriptive status queries
    Given I want to know what's running
    When I ask "what's currently running?"
    Then I should see the status

  Scenario: Asking for help naturally
    Given I'm not sure what to do
    When I ask "what can I do?"
    Then I should see help information
    And available commands should be explained

  Scenario: Connection help requests
    Given I need to connect to a VM
    When I ask "how do I connect to the Python environment?"
    Then I should receive SSH connection instructions
    And the instructions should be clear and actionable

  @requires-docker-host
  Scenario: Rebuild requests
    Given I need to rebuild a container
    When I say "rebuild python from scratch"
    Then the rebuild flag should be set
    And no cache should be used

  @requires-docker-host
  Scenario: Wildcard operations
    Given I want to operate on all VMs of a type
    When I say "start all languages"
    Then all language VMs should start
    And service VMs should not be affected

  @requires-docker-host
  Scenario: Stopping everything
    Given I'm done working
    When I say "stop everything"
    Then all running VMs should stop

  @requires-docker-host
  Scenario: Complex natural language queries
    Given I use conversational language
    When I say "I need to set up a backend with Python and PostgreSQL"
    Then the system should understand I want to create VMs
    And Python and PostgreSQL should be created

  @requires-docker-host
  Scenario: Troubleshooting language
    Given something isn't working
    When I say "restart the database"
    Then PostgreSQL should restart
    And the system should understand "database" means "postgres"

  @requires-docker-host
  Scenario: Case insensitive commands
    Given I type commands in various cases
    When I say "START PYTHON"
    Then the system should understand I want to start the Python VM
    And the Python VM should start

  @requires-docker-host
  Scenario: Minimal typing commands
    Given I want to type less
    When I say "start py and pg"
    Then it should understand "py" means "python"
    And "pg" should mean "postgres"
