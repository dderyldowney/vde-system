# language: en
@wip
@user-guide-ssh-keys
Feature: SSH Configuration
  As a developer
  I want automatic SSH agent forwarding and key management
  So that I can seamlessly access VMs and external services

  Scenario: Automatically start SSH agent if not running
    Given SSH agent is not running
    And SSH keys exist in ~/.ssh/
    When I run any VDE command that requires SSH
    Then SSH agent should be started
    And available SSH keys should be loaded into agent

  Scenario: Generate SSH key if none exists
    Given no SSH keys exist in ~/.ssh/
    When I run any VDE command that requires SSH
    Then an ed25519 SSH key should be generated
    And the public key should be synced to public-ssh-keys directory

  Scenario: Sync public keys to VDE directory
    Given SSH keys exist in ~/.ssh/
    When I run "sync_ssh_keys_to_vde"
    Then public keys should be copied to "public-ssh-keys" directory
    And only .pub files should be copied
    And .keep file should exist in public-ssh-keys directory

  Scenario: Validate public key files only
    Given public-ssh-keys directory contains files
    When private key detection runs
    Then non-.pub files should be rejected
    And files containing "PRIVATE KEY" should be rejected

  Scenario: Create SSH config entry for new VM
    Given VM "python" is created with SSH port "2200"
    When SSH config is generated
    Then SSH config should contain "Host python-dev"
    And SSH config should contain "Port 2200"
    And SSH config should contain "ForwardAgent yes"

  Scenario: SSH config uses correct identity file
    Given primary SSH key is "id_ed25519"
    When SSH config entry is created for VM "python"
    Then SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"

  Scenario: Generate VM-to-VM SSH config entries
    Given VM "python" is allocated port "2200"
    And VM "rust" is allocated port "2201"
    When VM-to-VM SSH config is generated
    Then SSH config should contain entry for "python-dev"
    And SSH config should contain entry for "rust-dev"
    And each entry should use "localhost" as hostname

  Scenario: Prevent duplicate SSH config entries
    Given SSH config already contains "Host python-dev"
    When I create VM "python" again
    Then duplicate SSH config entry should NOT be created
    And command should warn about existing entry

  Scenario: Atomic SSH config update prevents corruption
    Given SSH config file exists
    When multiple processes try to update SSH config simultaneously
    Then SSH config should remain valid
    And no partial updates should occur

  Scenario: Backup SSH config before modification
    Given SSH config file exists
    When SSH config is updated
    Then backup file should be created in "backup/ssh/" directory
    And backup filename should contain timestamp

  Scenario: Remove SSH config entry when VM is removed
    Given SSH config contains "Host python-dev"
    When VM "python" is removed
    Then SSH config should NOT contain "Host python-dev"

  Scenario: VM-to-VM communication uses agent forwarding
    Given SSH agent is running
    And keys are loaded into agent
    When I SSH from "python-dev" to "rust-dev"
    Then the connection should use host's SSH keys
    And no keys should be stored on containers

  Scenario: Detect all common SSH key types
    Given ~/.ssh/ contains SSH keys
    When detect_ssh_keys runs
    Then "id_ed25519" keys should be detected
    And "id_rsa" keys should be detected
    And "id_ecdsa" keys should be detected
    And "id_dsa" keys should be detected

  Scenario: Prefer ed25519 keys when multiple exist
    Given both "id_ed25519" and "id_rsa" keys exist
    When primary SSH key is requested
    Then "id_ed25519" should be returned as primary key

  # =============================================================================
  # SSH Config Merge Tests - Critical for preserving user configurations
  # =============================================================================

  @requires-docker-ssh
  Scenario: Merge new VM entry with existing SSH config
    Given ~/.ssh/config exists with existing host entries
    And ~/.ssh/config contains "Host github.com"
    And ~/.ssh/config contains "Host myserver"
    When I create VM "python" with SSH port "2200"
    Then ~/.ssh/config should still contain "Host github.com"
    And ~/.ssh/config should still contain "Host myserver"
    And ~/.ssh/config should contain new "Host python-dev" entry
    And existing entries should be unchanged

  @requires-docker-ssh
  Scenario: Merge preserves user's custom SSH settings
    Given ~/.ssh/config exists with custom settings
    And ~/.ssh/config contains "Host *"
    And ~/.ssh/config contains "    User myuser"
    And ~/.ssh/config contains "    IdentityFile ~/.ssh/mykey"
    When I create VM "rust" with SSH port "2201"
    Then ~/.ssh/config should still contain "Host *"
    And ~/.ssh/config should still contain "    User myuser"
    And ~/.ssh/config should still contain "    IdentityFile ~/.ssh/mykey"
    And new "Host rust-dev" entry should be appended to end

  @requires-docker-ssh
  Scenario: Merge preserves existing VDE entries when adding new VM
    Given ~/.ssh/config contains "Host python-dev"
    And ~/.ssh/config contains "    Port 2200"
    When I create VM "rust" with SSH port "2201"
    Then ~/.ssh/config should still contain "Host python-dev"
    And ~/.ssh/config should still contain "    Port 2200" under python-dev
    And new "Host rust-dev" entry should be added

  Scenario: Merge does not duplicate existing VDE entries
    Given ~/.ssh/config contains "Host python-dev"
    And ~/.ssh/config contains python-dev configuration
    When I attempt to create VM "python" again
    Then ~/.ssh/config should contain only one "Host python-dev" entry
    And error should indicate entry already exists

  Scenario: Atomic merge prevents corruption if interrupted
    Given ~/.ssh/config exists with content
    When merge_ssh_config_entry starts but is interrupted
    Then ~/.ssh/config should either be original or fully updated
    And ~/.ssh/config should NOT be partially written
    And original config should be preserved in backup

  Scenario: Merge uses temporary file then atomic rename
    Given ~/.ssh/config exists
    When new SSH entry is merged
    Then temporary file should be created first
    Then content should be written to temporary file
    Then atomic mv should replace original config
    Then temporary file should be removed

  Scenario: Merge creates SSH config if it doesn't exist
    Given ~/.ssh/config does not exist
    And ~/.ssh directory exists or can be created
    When I create VM "python" with SSH port "2200"
    Then ~/.ssh/config should be created
    And ~/.ssh/config should have permissions "600"
    And ~/.ssh/config should contain "Host python-dev"

  Scenario: Merge creates .ssh directory if needed
    Given ~/.ssh directory does not exist
    When I create VM "python" with SSH port "2200"
    Then ~/.ssh directory should be created
    And ~/.ssh/config should be created
    And directory should have correct permissions

  Scenario: Merge preserves blank lines and formatting
    Given ~/.ssh/config exists with blank lines
    And ~/.ssh/config has comments and custom formatting
    When I create VM "go" with SSH port "2202"
    Then ~/.ssh/config blank lines should be preserved
    And ~/.ssh/config comments should be preserved
    And new entry should be added with proper formatting

  Scenario: Merge respects file locking for concurrent updates
    Given ~/.ssh/config exists
    And multiple processes try to add SSH entries simultaneously
    When merge operations complete
    Then all VM entries should be present
    And no entries should be lost
    And config file should be valid

  Scenario: Merge creates backup before any modification
    Given ~/.ssh/config exists
    When I create VM "python" with SSH port "2200"
    Then backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"
    And backup should contain original config content
    And backup timestamp should be before modification

  @requires-docker-ssh
  Scenario: Merge entry has all required SSH config fields
    Given ~/.ssh/config exists
    When I create VM "python" with SSH port "2200"
    Then merged entry should contain "Host python-dev"
    And merged entry should contain "HostName localhost"
    And merged entry should contain "Port 2200"
    And merged entry should contain "User devuser"
    And merged entry should contain "ForwardAgent yes"
    And merged entry should contain "StrictHostKeyChecking no"
    And merged entry should contain "IdentityFile" pointing to detected key

  @requires-docker-ssh
  Scenario: Merge removes VM entry when VM is removed
    Given ~/.ssh/config contains "Host python-dev"
    And ~/.ssh/config contains "Host rust-dev"
    And ~/.ssh/config contains user's "Host github.com" entry
    When I remove VM for SSH cleanup "python"
    Then ~/.ssh/config should NOT contain "Host python-dev"
    And ~/.ssh/config should still contain "Host rust-dev"
    And ~/.ssh/config should still contain "Host github.com"
    And user's entries should be preserved

  # =============================================================================
  # SSH known_hosts Cleanup Tests - Prevents "host key changed" warnings
  # =============================================================================

  @requires-docker-ssh
  Scenario: Remove known_hosts entry when VM is removed
    Given VM "python" is created with SSH port "2200"
    And ~/.ssh/known_hosts contains entry for "[localhost]:2200"
    When I remove VM for SSH cleanup "python"
    Then ~/.ssh/known_hosts should NOT contain entry for "[localhost]:2200"
    And ~/.ssh/known_hosts should NOT contain entry for "[::1]:2200"

  @requires-docker-ssh
  Scenario: Remove multiple hostname patterns from known_hosts
    Given VM "postgres" is created with SSH port "2400"
    And ~/.ssh/known_hosts contains "[localhost]:2400"
    And ~/.ssh/known_hosts contains "[::1]:2400"
    And ~/.ssh/known_hosts contains "postgres" hostname entry
    When I remove VM for SSH cleanup "postgres"
    Then ~/.ssh/known_hosts should NOT contain "[localhost]:2400"
    And ~/.ssh/known_hosts should NOT contain "[::1]:2400"
    And ~/.ssh/known_hosts should NOT contain "postgres" entry

  @requires-docker-ssh
  Scenario: Create backup of known_hosts before cleanup
    Given ~/.ssh/known_hosts exists with content
    And VM "redis" is created with SSH port "2401"
    When I remove VM for SSH cleanup "redis"
    Then known_hosts backup file should exist at "~/.ssh/known_hosts.vde-backup"
    And backup should contain original content

  @requires-docker-ssh
  Scenario: Known_hosts cleanup handles missing file gracefully
    Given ~/.ssh/known_hosts does not exist
    And VM "python" is created with SSH port "2200"
    When I remove VM for SSH cleanup "python"
    Then command should succeed without error
    And no known_hosts file should be created

  @requires-docker-ssh
  Scenario: Known_hosts cleanup removes entries by port number
    Given ~/.ssh/known_hosts contains multiple port entries
    And ~/.ssh/known_hosts contains "[localhost]:2200"
    And ~/.ssh/known_hosts contains "[localhost]:2400"
    When VM with port "2200" is removed
    Then ~/.ssh/known_hosts should NOT contain "[localhost]:2200"
    And ~/.ssh/known_hosts should still contain "[localhost]:2400"

  @requires-docker-ssh
  Scenario: Recreating VM after removal succeeds without host key warning
    Given VM "python" was previously created with SSH port "2200"
    And ~/.ssh/known_hosts had old entry for "[localhost]:2200"
    When I remove VM for SSH cleanup "python"
    And I create VM "python" with SSH port "2200"
    Then SSH connection should succeed without host key warning
    And ~/.ssh/known_hosts should contain new entry for "[localhost]:2200"
