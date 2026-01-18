# language: en
@user-guide-internal
@requires-docker-host
Feature: AI Assistant for Natural Language Control
  As a developer
  I want to control VDE using natural language
  So that I don't need to remember exact command syntax

  Scenario: Start VMs with conversational command
    Given I have VMs created but not running
    When I say "start the python and rust vms"
    Then both python and rust VMs should start
    And I should not need to remember the exact command

  Scenario: Ask what VMs are available
    Given I'm new to VDE
    When I ask "what vms can I create?"
    Then I should see a list of all available VM types
    And aliases should be shown
    And I should understand my options

  Scenario: Ask what's currently running
    Given I have several VMs configured
    When I ask "what's currently running?"
    Then I should see which VMs are running
    And I should see which VMs are stopped
    And I should see SSH connection info for running VMs

  Scenario: Get help with available commands
    Given I'm not sure what I can do
    When I ask "help" or "what can I do?"
    Then I should see available commands
    And example commands should be shown
    And I should understand how to use VDE

  Scenario: Create VM with natural language
    Given I want a go development environment
    When I say "create a go vm"
    Then go VM should be created
    And I should not need to remember create-virtual-for syntax

  @requires-docker-host
  Scenario: Stop all VMs at once
    Given I have multiple VMs running
    When I say "stop everything" or "shutdown all"
    Then all VMs should be stopped
    And I should not need to list each VM

  Scenario: Rebuild VM with natural language
    Given I've modified a Dockerfile
    When I say "rebuild and start python"
    Then python VM should be rebuilt and started
    And I should not need to remember --rebuild flag

  Scenario: Ask how to connect to a VM
    Given I want to SSH into my VM
    When I ask "how do I connect to python?"
    Then I should see the SSH command
    And I should see the port number
    And I should see VSCode Remote-SSH instructions

  Scenario: List only language VMs
    Given I want to see available programming languages
    When I say "show all language vms"
    Then I should see python, rust, go, js, etc.
    But I should not see postgres, redis, nginx

  Scenario: List only service VMs
    Given I want to see available services
    When I say "what services are available?"
    Then I should see postgres, redis, mongodb, nginx
    But I should not see language VMs

  Scenario: Handle ambiguous input gracefully
    Given I'm not sure of the exact command
    When I say something vague like "do something with containers"
    Then I should get helpful guidance
    And available options should be suggested
    And I should not get a cryptic error

  Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions

  Scenario: Complex multi-step requests
    Given I want to do multiple things
    When I say "create a rust vm and start it with redis"
    Then rust VM should be created
    And rust and redis VMs should be started
    And I should not need separate commands

  Scenario: Status of specific VMs
    Given I have multiple VMs
    When I ask "show status of python and rust"
    Then I should see status for only those VMs
    And other VMs should not clutter the output

  Scenario: Use common aliases naturally
    Given I'm used to saying "js" instead of "javascript"
    When I say "start js vm"
    Then javascript VM should start
    And common aliases should work naturally
