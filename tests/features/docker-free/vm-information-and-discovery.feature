@user-guide-understanding
Feature: VM Information and Discovery
  As a developer using VDE
  I want to discover what VMs are available and get information about them
  So I can make informed decisions about my development environment

  Scenario: Listing all available VMs
    Given I have VDE installed
    When I ask "what VMs can I create?"
    Then I should see all available language VMs
    And I should see all available service VMs
    And each VM should have a display name
    And each VM should show its type (language or service)

  Scenario: Listing only language VMs
    Given I want to see only programming language environments
    When I ask "show all languages"
    Then I should see only language VMs
    And I should not see service VMs
    And common languages like Python, Go, and Rust should be listed

  Scenario: Listing only service VMs
    Given I want to see only infrastructure services
    When I ask "show all services"
    Then I should see only service VMs
    And I should not see language VMs
    And services like PostgreSQL and Redis should be listed

  Scenario: Getting detailed information about a specific VM
    Given I want to know about the Python VM
    When I request information about "python"
    Then I should see its display name
    And I should see its type (language)
    And I should see any aliases (like py, python3)
    And I should see installation details

  Scenario: Checking if a VM exists
    Given I want to verify a VM type before using it
    When I check if "golang" exists
    Then it should resolve to "go"
    And the VM should be marked as valid

  Scenario: Discovering VMs by alias
    Given I know a VM by an alias but not its canonical name
    When I use the alias "nodejs"
    Then it should resolve to the canonical name "js"
    And I should be able to use either name in commands

  Scenario: Understanding VM categories
    Given I am new to VDE
    When I explore available VMs
    Then I should understand the difference between language and service VMs
    And language VMs should have SSH access
    And service VMs should provide infrastructure services
