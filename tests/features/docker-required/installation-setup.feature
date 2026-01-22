# language: en
@user-guide-installation
@requires-docker-host
Feature: Installation and Initial Setup
  As a developer
  I want to install and configure VDE on my system
  So that I can start using development environments immediately

  Scenario: Fresh installation on new system
    Given I have a new computer with Docker installed
    And I have cloned the VDE repository to ~/dev
    When I run the initial setup script
    Then VDE should be properly installed
    And required directories should be created
    And I should see success message

  Scenario: Prerequisites are checked
    Given I want to install VDE
    When the setup script runs
    Then it should verify Docker is installed
    And it should verify docker-compose is available
    And it should verify zsh is available
    And it should report missing dependencies clearly

  Scenario: Create required directory structure
    Given VDE is being installed
    When the setup completes
    Then configs/ directory should exist
    And templates/ directory should exist with templates
    And data/ directory should exist for persistent data
    And logs/ directory should exist
    And projects/ directory should exist for code
    And env-files/ directory should exist
    And backup/ directory should exist
    And cache/ directory should exist

  Scenario: Generate or detect SSH keys
    Given I'm setting up VDE for the first time
    When SSH keys are checked
    Then if keys exist, they should be detected
    And if no keys exist, ed25519 keys should be generated
    And public keys should be copied to public-ssh-keys/
    And .keep file should exist in public-ssh-keys/

  Scenario: Initial SSH configuration
    Given VDE is being set up
    When setup completes
    Then backup/ssh/config should exist as a template
    And the template should show proper SSH config format
    And I should be able to use it as reference

  Scenario: Load VM types configuration
    Given VDE is installed
    When I run list-vms
    Then all predefined VM types should be shown
    And python, rust, js, csharp, ruby should be listed
    And postgres, redis, mongodb, nginx should be listed
    And aliases should be shown (py, js, etc.)

  Scenario: Set up shell environment
    Given I want VDE commands available everywhere
    When I add VDE scripts to my PATH
    Then I can run vde commands from any directory
    And I can run start-virtual, shutdown-virtual, etc.
    And tab completion should work

  Scenario: Verify Docker permissions
    Given VDE is being installed
    When setup checks Docker
    Then I should be warned if I can't run Docker without sudo
    And instructions should be provided for fixing permissions
    And setup should continue with a warning

  Scenario: Create Docker network
    Given VDE is being installed
    When the first VM is created
    Then vde-network should be created automatically
    And all VMs should use this network
    And VMs can communicate with each other

  @user-guide-first-vm
  Scenario: First time creation experience
    Given I've just installed VDE
    When I run "create-virtual-for python"
    Then I should see helpful progress messages
    And configs/docker/python/ should be created
    And docker-compose.yml should be generated
    And SSH config should be updated
    And I should be told what to do next

  Scenario: Verify installation with health check
    Given I've installed VDE
    When I run "vde-health" or check status
    Then I should see if VDE is properly configured
    And any issues should be clearly listed
    And I should get fix suggestions for each issue

  Scenario: Upgrade existing installation
    Given I have an older version of VDE
    When I pull the latest changes
    Then my existing VMs should continue working
    And new VM types should be available
    And my configurations should be preserved
    And I should be told about any manual migration needed

  Scenario: Uninstall or cleanup
    Given I no longer want VDE on my system
    When I want to remove it
    Then I can stop all VMs
    And I can remove VDE directories
    And my SSH config should be cleaned up
    And my project data should be preserved if I want

  Scenario: Installation on different platforms
    Given I'm installing VDE
    When the setup detects my OS (Linux/Mac)
    Then appropriate paths should be used
    And platform-specific adjustments should be made
    And the installation should succeed

  Scenario: Docker image availability
    Given I'm setting up VDE for the first time
    When I create my first VM
    Then required Docker images should be pulled
    And base images should be built if needed
    And I should see download/build progress

  Scenario: Quick start after installation
    Given VDE is freshly installed
    When I want to start quickly
    Then I can run "create-virtual-for python && start-virtual python"
    And I should have a working Python environment
    And I can start coding immediately

  Scenario: Documentation is available
    Given VDE is installed
    When I need help
    Then README.md should provide overview
    And Technical-Deep-Dive.md should explain internals
    And tests/README.md should explain testing
    And help text should be available in commands

  Scenario: Validate installation
    Given VDE has been installed
    When I run validation checks
    Then all scripts should be executable
    And all templates should be present
    And vm-types.conf should be valid
    And all directories should have correct permissions
