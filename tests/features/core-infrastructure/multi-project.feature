@parser
Feature: Multi-Project Workflow
  As a developer working on multiple projects
  I want to switch between different development environments via unified commands
  So I can work on different projects without configuration conflicts

  Scenario: Setting up a web development project
    Given I am following the documented workflow
    When I parse "create javascript nginx"
    Then intent should be "create_vm"
    And VMs should include "javascript"
    And VMs should include "nginx"

  Scenario: Switching from web to backend project
    Given I am following the documented workflow
    When I parse "start python postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  Scenario: New Project Setup - Start Development Stack
    Given I am following the documented workflow
    When I parse "start python postgres"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "postgres"

  Scenario: Setting up a microservices architecture
    Given I am following the documented workflow
    When I parse "create go rust nginx"
    Then intent should be "create_vm"
    And VMs should include "go"
    And VMs should include "rust"
    And VMs should include "nginx"

  Scenario: Starting all microservices at once
    Given I am following the documented workflow
    When I parse "start all services"
    Then intent should be "start_vm"

  Scenario: Data science project setup
    Given I am following the documented workflow
    When I parse "start python r"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "r"

  Scenario: Full stack web application
    Given I am following the documented workflow
    When I parse "create python postgres redis nginx"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "postgres"
    And VMs should include "redis"
    And VMs should include "nginx"

  Scenario: Mobile development with backend
    Given I am following the documented workflow
    When I parse "start flutter postgres"
    Then intent should be "start_vm"
    And VMs should include "flutter"
    And VMs should include "postgres"

  Scenario: Cleaning up between projects
    Given I am following the documented workflow
    When I parse "stop everything"
    Then intent should be "stop_vm"
