# language: en
@user-guide-connecting
Feature: SSH and Remote Access
  As a developer using VDE
  I want to access my VMs via SSH
  So I can use my preferred tools and editors

  Scenario: Getting SSH connection information
    Given I have a Python VM running
    When I ask "how do I connect to Python?"
    Then I should receive the SSH port
    And I should receive the username (devuser)
    And I should receive the hostname (localhost)

  @requires-docker-host
  Scenario: Connecting with SSH client
    Given I have the SSH connection details
    When I run "ssh python-dev"
    Then I should connect to the Python VM
    And I should be logged in as devuser
    And I should have a zsh shell

  @requires-docker-host
  Scenario: Using VSCode Remote-SSH
    Given I have VSCode installed
    When I add the SSH config for python-dev
    Then I can connect using Remote-SSH
    And my workspace should be mounted
    And I can edit files in the projects directory

  @requires-docker-host
  Scenario: Multiple SSH connections
    Given I have multiple VMs running
    When I connect to python-dev
    And then connect to postgres-dev
    Then both connections should work
    And each should use a different port

  @requires-docker-host
  Scenario: SSH key authentication
    Given I have set up SSH keys
    When I connect to a VM
    Then I should not be prompted for a password
    And key-based authentication should be used

  @requires-docker-host
  Scenario: Workspace directory access
    Given I am connected via SSH
    When I navigate to ~/workspace
    Then I should see my project files
    And changes should be reflected on the host

  @requires-docker-host
  Scenario: Sudo access in container
    Given I need to perform administrative tasks
    When I run sudo commands in the container
    Then they should execute without password
    And I should have the necessary permissions

  @requires-docker-host
  Scenario: Shell configuration
    Given I connect via SSH
    When I start a shell
    Then I should be using zsh
    And oh-my-zsh should be configured
    And my preferred theme should be active

  @requires-docker-host
  Scenario: Editor configuration
    Given I connect via SSH
    When I run nvim
    Then LazyVim should be available
    And my editor configuration should be loaded

  @requires-docker-host
  Scenario: Transferring files
    Given I am connected to a VM
    When I use scp to copy files
    Then files should transfer to/from the workspace
    And permissions should be preserved

  @requires-docker-host
  Scenario: Port forwarding for services
    Given I have a web service running in a VM
    When I access localhost on the VM's port
    Then I should reach the service
    And the service should be accessible from the host

  @requires-docker-host
  Scenario: SSH session persistence
    Given I have a long-running task in a VM
    When my SSH connection drops
    Then the task should continue running
    And I can reconnect to the same session
