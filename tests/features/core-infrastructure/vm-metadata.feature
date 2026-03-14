@core-infrastructure
@user-guide-internal
Feature: VM Metadata Verification
  As a developer using VDE
  I want to verify that VM metadata is correctly configured
  So I can trust the VM type definitions and ensure proper system behavior

  Scenario: Language VM display names are user-friendly
    Given I have VDE installed
    When I query the display name for language VMs
    Then each language VM should have a display name
    And the display name should be descriptive
    And common languages like Python, Go, and Rust should have recognizable names

  Scenario: Service VM display names are user-friendly
    Given I have VDE installed
    When I query the display name for service VMs
    Then each service VM should have a display name
    And services like PostgreSQL and Redis should have recognizable names

  Scenario: Language VM ports are in correct range
    Given I have VDE installed
    When I check the SSH port allocation for language VMs
    Then all language VM ports should be between 2200 and 2399

  Scenario: Service VM ports are in correct range
    Given I have VDE installed
    When I check the SSH port allocation for service VMs
    Then all service VM ports should be between 2400 and 2499

  Scenario: VM types are correctly categorized as language
    Given I have VDE installed
    When I query VM types
    Then programming language VMs should be categorized as "lang"
    And Python, Go, Rust, and JavaScript should be language VMs

  Scenario: VM types are correctly categorized as service
    Given I have VDE installed
    When I query VM types
    Then infrastructure service VMs should be categorized as "service"
    And PostgreSQL, Redis, MongoDB, and Nginx should be service VMs

  Scenario: Common programming language aliases resolve correctly
    Given I have VDE installed
    When I query alias mappings for programming languages
    Then the metadata alias "python3" should map to "python"
    And the metadata alias "nodejs" should map to "js"
    And the metadata alias "golang" should map to "go"
    And the metadata alias "c++" should map to "cpp"
    And the metadata alias "rlang" should map to "r"

  Scenario: Common service aliases resolve correctly
    Given I have VDE installed
    When I query alias mappings for services
    Then the metadata alias "postgresql" should map to "postgres"
    And the metadata alias "mongo" should map to "mongodb"

  Scenario: Language VM container names follow naming convention
    Given I have VDE installed
    When I check container naming for language VMs
    Then language VM containers should use the "vde-{name}" pattern

  Scenario: Service VM container names follow naming convention
    Given I have VDE installed
    When I check container naming for service VMs
    Then service VM containers should use the "vde-{name}" pattern

  Scenario: All VMs have valid installation commands
    Given I have VDE installed
    When I verify installation commands for all VMs
    Then each VM should have a non-empty install command

  Scenario: Service VMs have service port configured
    Given I have VDE installed
    When I check service port configuration
    Then all service VMs should have a service_port defined
    And the service_port should be a valid port number

  Scenario: Language VMs do not have service ports configured
    Given I have VDE installed
    When I check service port configuration for language VMs
    Then language VMs should not have service_port values

  Scenario: Total VM count matches expected inventory
    Given I have VDE installed
    When I count all configured VMs
    Then the total should match the expected inventory
    And there should be at least 19 language VMs
    And there should be at least 7 service VMs
