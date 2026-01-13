Feature: Multi-Project Workflow
  As a developer working on multiple projects
  I want to switch between different development environments
  So I can work on different projects without configuration conflicts

  Scenario: Setting up a web development project
    Given I am starting a new web project
    When I request to "create JavaScript and nginx"
    Then the JavaScript VM should be created
    And the nginx VM should be created
    And both should be configured for web development

  Scenario: Switching from web to backend project
    Given I have web containers running (JavaScript, nginx)
    When I request to "stop all and start python and postgres"
    Then the web containers should be stopped
    And the Python VM should start
    And the PostgreSQL VM should start
    And only the backend stack should be running

  Scenario: Setting up a microservices architecture
    Given I am building a microservices application
    When I request to "create Go, Rust, and nginx"
    Then the Go VM should be created for one service
    And the Rust VM should be created for another service
    And the nginx VM should be created as a gateway

  Scenario: Starting all microservices at once
    Given I have created my microservice VMs
    When I request to "start all services"
    Then all service VMs should start
    And they should be able to communicate on the Docker network
    And each should have its own SSH port

  Scenario: Data science project setup
    Given I am doing data analysis
    When I request to "start python and r"
    Then the Python VM should start
    And the R VM should start
    And both should have data science tools available

  Scenario: Full stack web application
    Given I need a complete web stack
    When I request to "create Python, PostgreSQL, Redis, and nginx"
    Then the Python VM should be for the backend API
    And PostgreSQL should be for the database
    And Redis should be for caching
    And nginx should be for the web server
    And all should be on the same network

  Scenario: Mobile development with backend
    Given I am developing a mobile app with backend
    When I request to "start flutter and postgres"
    Then the Flutter VM should start for mobile development
    And PostgreSQL should start for the backend database
    And both should be accessible via SSH

  Scenario: Cleaning up between projects
    Given I have finished working on one project
    When I request to "stop everything"
    Then all containers should stop
    And I can start a fresh environment for another project
    And there should be no leftover processes
