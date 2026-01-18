# language: en
@user-guide-internal
Feature: Team Collaboration and Project Sharing
  As a developer working with a team
  I want to share VDE configurations with my team
  So that everyone has consistent development environments

  @requires-docker-host
  Scenario: New team member sets up VDE for first time
    Given I am a new developer joining the team
    And I have cloned the project repository
    And the project contains VDE configuration in configs/
    When I run the initial setup
    Then VDE should detect my operating system
    And appropriate base images should be built
    And my SSH keys should be automatically configured
    And I should see available VMs with "list-vms"

  @requires-docker-host
  Scenario: Share project VM configuration via git
    Given my project has a "python" VM configuration
    And the docker-compose.yml is committed to the repo
    When a teammate clones the repository
    And they run "create-virtual-for python"
    Then they should get the same Python environment I have
    And all dependencies should be installed
    And project directories should be properly mounted

  @requires-docker-host
  Scenario: Sync team member's SSH config changes
    Given the team has updated SSH config templates
    And I pull the latest changes
    When I create or restart any VM
    Then my SSH config should be updated with new entries
    And my existing SSH entries should be preserved
    And I should not lose my personal SSH configurations

  @requires-docker-host
  Scenario: Collaborate with shared PostgreSQL service
    Given the team uses PostgreSQL for development
    And postgres VM configuration is in the repository
    When each team member starts "postgres" VM
    Then each developer gets their own isolated PostgreSQL instance
    And data persists in each developer's local data/postgres/
    And developers don't interfere with each other's databases

  @requires-docker-host
  Scenario: Development environment matches production
    Given our production uses PostgreSQL 14, Redis 7, and Node 18
    When I configure VDE with matching versions
    Then my local development should match production
    And version-specific bugs can be caught early
    And deployment surprises are minimized

  @requires-docker-host
  Scenario: Onboard new developer with pre-built VMs
    Given the team maintains a set of pre-configured VMs
    And documentation explains how to create each VM
    When a new developer joins
    And they follow the setup instructions
    Then they should have all VMs running in minutes
    And they can start contributing immediately

  @requires-docker-host
  Scenario: Team agrees on standard VM types
    Given the team defines standard VM types in vm-types.conf
    When new projects need specific language support
    And the VM type is already defined
    Then anyone can create the VM using the standard name
    And everyone gets consistent configurations
    And aliases work predictably across the team

  @requires-docker-host
  Scenario: Document project-specific VM requirements
    Given a project requires specific services (postgres, redis, nginx)
    When the project README documents required VMs
    And developers run the documented create commands
    Then all developers have compatible environments
    And "docker-compose up" works for everyone
    And local development matches the documented setup

  @requires-docker-host
  Scenario: Share environment variables via env-files
    Given a project needs environment variables for configuration
    And env-files/project-name.env is committed to git (with defaults)
    When a developer creates and starts the VM
    Then environment variables should be loaded from env-file
    And developers can override variables in local env-file (gitignored)
    And sensitive variables stay out of version control

  @requires-docker-host
  Scenario: Collaborative debugging with matching environments
    Given a developer cannot reproduce a bug
    When another developer shares their exact VM configuration
    And the first developer recreates the VM
    Then both developers have identical environments
    And the bug becomes reproducible
    And debugging becomes more effective

  @requires-docker-host
  Scenario: Team expands VDE with new language support
    Given the team decides to add "dart" support
    When one developer runs "add-vm-type dart 'apt-get install -y dart'"
    And commits the vm-types.conf change
    Then all developers can create dart VMs
    And everyone has access to the same dart environment
    And the team's language support grows consistently
