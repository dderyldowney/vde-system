# language: en
@user-guide-ssh-keys
@requires-docker-host
Feature: Automatic SSH Setup and Key Management
  As a developer getting started with VDE
  I want SSH to be configured automatically
  So I don't need to manually set up SSH keys or agents

  Scenario: First-time user with no SSH keys
    Given I have just cloned VDE
    And I do not have any SSH keys
    And I do not have an SSH agent running
    When I create my first VM
    Then an SSH key should be generated automatically
    And the SSH agent should be started automatically
    And the key should be loaded into the agent
    And I should be informed of what happened
    And I should be able to use SSH immediately

  Scenario: First-time user with existing SSH keys
    Given I have just cloned VDE
    And I have existing SSH keys in ~/.ssh/
    And I do not have an SSH agent running
    When I create my first VM
    Then my existing SSH keys should be detected automatically
    And the SSH agent should be started automatically
    And my keys should be loaded into the agent
    And I should not need to configure anything manually

  Scenario: User with multiple SSH key types
    Given I have SSH keys of different types
    And I have id_ed25519, id_rsa, and id_ecdsa keys
    And I create a new VM
    When I start the VM
    Then all my SSH keys should be detected
    And all keys should be loaded into the agent
    And the best key should be selected for SSH config
    And I should be able to use any of the keys

  Scenario: SSH agent setup is silent during normal operations
    Given I have created VMs before
    And I have SSH configured
    When I create a new VM
    Then no SSH configuration messages should be displayed
    And the setup should happen automatically
    And I should only see VM creation messages

  Scenario: SSH agent restart if not running
    Given I have VMs configured
    And my SSH agent is not running
    When I start a VM
    Then the SSH agent should be started automatically
    And my keys should be loaded automatically
    And the VM should start normally

  Scenario: Viewing SSH status
    Given I have VDE configured
    When I run "./scripts/ssh-agent-setup"
    Then I should see the SSH agent status
    And I should see my available SSH keys
    And I should see keys loaded in the agent
    And the list-vms command should show available VMs
    And I should see usage examples

  Scenario: SSH config auto-generation for all VMs
    Given I have created multiple VMs
    When I use SSH to connect to any VM
    Then the SSH config entries should exist
    And I should be able to use short hostnames
    And I should not need to remember port numbers

  Scenario: Rebuilding VMs preserves SSH configuration
    Given I have a running VM with SSH configured
    When I shutdown and rebuild the VM
    Then my SSH configuration should still work
    And I should not need to reconfigure SSH
    And my keys should still work

  Scenario: Automatic key generation preference
    Given I do not have any SSH keys
    When I create a VM
    Then an ed25519 key should be generated
    And ed25519 should be the preferred key type
    And the key should be generated with a comment

  Scenario: Public keys automatically synced to VDE
    Given I have SSH keys on my host
    When I create a VM
    Then my public keys should be copied to public-ssh-keys/
    And all my public keys should be in the VM's authorized_keys
    And I should not need to manually copy keys

  Scenario: SSH setup works with different SSH clients
    Given I have configured SSH through VDE
    When I use the system ssh command
    And when I use OpenSSH clients
    And when I use VSCode Remote-SSH
    Then all should work with the same configuration
    And all should use my SSH keys

  Scenario: No manual SSH configuration needed
    Given I am a new VDE user
    When I read the documentation
    Then I should see that SSH is automatic
    And I should not see manual setup instructions
    And I should be able to start using VMs immediately
