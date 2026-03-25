# language: en
@config
Feature: SSH Configuration
  As a developer
  I want automatic SSH agent forwarding and key management
  So that I can seamlessly access VMs and external services

  @requires-ssh-agent
  Scenario: Report agent unavailable when SSH_AUTH_SOCK is not set
    Given SSH keys exist in ~/.ssh/vde/
    And SSH_AUTH_SOCK is unset in the test environment
    When I run any VDE command that requires SSH
    Then the command output should indicate no SSH agent is available
    And no running SSH agent processes should be terminated

  @requires-ssh-agent
  Scenario: Generate SSH key if none exists
    Given no SSH keys exist in ~/.ssh/vde/
    When I run any VDE command that requires SSH
    Then an ed25519 SSH key should be generated
    And the public key should be synced to public-ssh-keys directory

  @requires-ssh-agent
  Scenario: Sync public keys to VDE directory
    Given SSH keys exist in ~/.ssh/vde/
    When I run "sync_ssh_keys_to_vde"
    Then public keys should be copied to "public-ssh-keys" directory
    And only .pub files should be copied
    And .keep file should exist in public-ssh-keys directory

  @requires-ssh-agent
  Scenario: Validate public key files only
    Given public-ssh-keys directory contains files
    When private key detection runs
    Then non-.pub files should be rejected
    And files containing "PRIVATE KEY" should be rejected

  @requires-docker-ssh
  Scenario: Create SSH config entry for new VM
    Given VM "python" is created with SSH port "2213"
    When SSH config is generated
    Then SSH config should contain "Host vde-python"
    And SSH config should contain "Port 2213"
    And SSH config should contain "ForwardAgent yes"

  @requires-docker-ssh
  Scenario: SSH config uses correct identity file
    Given primary SSH key is "id_ed25519"
    When SSH config entry is created for VM "python"
    Then SSH config should contain "IdentityFile" pointing to "~/.ssh/vde/id_ed25519"

  @integration
  @requires-docker-ssh
  Scenario: Generate VM-to-VM SSH config entries
    Given VM "python" is allocated port "2213"
    And VM "rust" is allocated port "2216"
    When VM-to-VM SSH config is generated
    Then SSH config should contain entry for "vde-python"
    And SSH config should contain entry for "vde-rust"
    And each entry should use "localhost" as hostname

  @requires-docker-ssh
  Scenario: Prevent duplicate SSH config entries
    Given SSH config already contains "Host vde-python"
    When I create VM "python" again
    Then duplicate SSH config entry should NOT be created
    And command should warn about existing entry

  @integration
  @requires-docker-ssh
  Scenario: Atomic SSH config update prevents corruption
    Given SSH config file exists
    When multiple processes try to update SSH config simultaneously
    Then SSH config should remain valid
    And no partial updates should occur

  @requires-docker-ssh
  Scenario: Backup SSH config before modification
    Given SSH config file exists
    When SSH config is updated
    Then backup file should be created in "backup/ssh/" directory
    And backup filename should contain timestamp

  @requires-docker-ssh
  Scenario: SSH config entries are static and preserved when VM is removed
    Given SSH config contains "Host vde-python"
    When VM "python" is removed
    Then SSH config should still contain "Host vde-python"

  @integration
  @requires-docker-ssh
  Scenario: VM compose file mounts SSH agent socket for agent forwarding
    Given VM "python" is created with SSH port "2213"
    When I inspect the docker-compose.yml for VM "python"
    Then the compose file should mount the SSH agent socket volume
    And the compose file should set SSH_AUTH_SOCK environment variable
    And SSH config entry for "vde-python" should contain "ForwardAgent yes"

  @requires-ssh-agent
  Scenario: Detect all common SSH key types
    Given ~/.ssh/vde/ contains SSH keys
    When detect_ssh_keys runs
    Then "id_ed25519" keys should be detected
    And "id_rsa" keys should be detected
    And "id_ecdsa" keys should be detected
    # Note: DSA keys are deprecated and not supported in modern OpenSSH

  @requires-ssh-agent
  Scenario: Prefer ed25519 keys when multiple exist
    Given both "id_ed25519" and "id_rsa" keys exist
    When primary SSH key is requested
    Then "id_ed25519" should be returned as primary key

  # =============================================================================
  # SSH Config Merge Tests - Critical for preserving user configurations
  # =============================================================================

  @requires-docker-ssh
  Scenario: Merge new VM entry with existing SSH config
    Given ~/.ssh/vde/config exists with existing host entries
    And ~/.ssh/vde/config contains "Host github.com"
    And ~/.ssh/vde/config contains "Host myserver"
    When I create VM "python" with SSH port "2213"
    Then ~/.ssh/vde/config should still contain "Host github.com"
    And ~/.ssh/vde/config should still contain "Host myserver"
    And ~/.ssh/vde/config should contain new "Host vde-python" entry
    And existing entries should be unchanged

  @requires-docker-ssh
  Scenario: Merge preserves user's custom SSH settings
    Given ~/.ssh/vde/config exists with custom settings
    And ~/.ssh/vde/config contains "Host *"
    And ~/.ssh/vde/config contains "    User myuser"
    And ~/.ssh/vde/config contains "    IdentityFile ~/.ssh/vde/mykey"
    When I create VM "rust" with SSH port "2216"
    Then ~/.ssh/vde/config should still contain "Host *"
    And ~/.ssh/vde/config should still contain "    User myuser"
    And ~/.ssh/vde/config should still contain "    IdentityFile ~/.ssh/vde/mykey"
    And new "Host vde-rust" entry should be appended to end

  @requires-docker-ssh
  Scenario: Merge preserves existing VDE entries when adding new VM
    Given ~/.ssh/vde/config contains "Host vde-python"
    And ~/.ssh/vde/config contains "    Port 2213"
    When I create VM "rust" with SSH port "2216"
    Then ~/.ssh/vde/config should still contain "Host vde-python"
    And ~/.ssh/vde/config should still contain "    Port 2213" under vde-python
    And new "Host vde-rust" entry should be added

  @requires-docker-ssh
  Scenario: Merge does not duplicate existing VDE entries
    Given ~/.ssh/vde/config contains "Host vde-python"
    And ~/.ssh/vde/config contains vde-python configuration
    When I attempt to create VM "python" again
    Then ~/.ssh/vde/config should contain only one "Host vde-python" entry
    And error should indicate entry already exists

  @requires-docker-ssh
  Scenario: Atomic merge prevents corruption if interrupted
    Given ~/.ssh/vde/config exists with content
    When merge_ssh_config_entry starts but is interrupted
    Then ~/.ssh/vde/config should either be original or fully updated
    And ~/.ssh/vde/config should NOT be partially written
    And original config should be preserved in backup

  @requires-docker-ssh
  Scenario: Merge uses temporary file then atomic rename
    Given ~/.ssh/vde/config exists
    When new SSH entry is merged
    Then temporary file should be created first
    Then content should be written to temporary file
    Then atomic mv should replace original config
    Then temporary file should be removed

  @requires-docker-ssh
  Scenario: Merge creates SSH config if it doesn't exist
    Given ~/.ssh/vde/config does not exist
    And ~/.ssh/vde directory exists or can be created
    When I create VM "python" with SSH port "2213"
    Then ~/.ssh/vde/config should be created
    And ~/.ssh/vde/config should have permissions "600"
    And ~/.ssh/vde/config should contain "Host vde-python"

  @requires-docker-ssh
  Scenario: Merge creates ~/.ssh/vde directory if needed
    Given ~/.ssh/vde directory does not exist
    When I create VM "python" with SSH port "2213"
    Then ~/.ssh/vde directory should be created
    And ~/.ssh/vde/config should be created
    And directory should have correct permissions

  @requires-docker-ssh
  Scenario: Merge preserves blank lines and formatting
    Given ~/.ssh/vde/config exists with blank lines
    And ~/.ssh/vde/config has comments and custom formatting
    When I create VM "go" with SSH port "2206"
    Then ~/.ssh/vde/config blank lines should be preserved
    And ~/.ssh/vde/config comments should be preserved
    And new entry should be added with proper formatting

  @integration
  @requires-docker-ssh
  Scenario: Merge respects file locking for concurrent updates
    Given ~/.ssh/vde/config exists
    And multiple processes try to add SSH entries simultaneously
    When merge operations complete
    Then all VM entries should be present
    And no entries should be lost
    And config file should be valid

  @requires-docker-ssh
  Scenario: Merge creates backup before any modification
    Given ~/.ssh/vde/config exists
    When I create VM "python" with SSH port "2213"
    Then backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"
    And backup should contain original config content
    And backup timestamp should be before modification

  @requires-docker-ssh
  Scenario: Merge entry has all required SSH config fields
    Given ~/.ssh/vde/config exists
    When I create VM "python" with SSH port "2213"
    Then merged entry should contain "Host vde-python"
    And merged entry should contain "HostName localhost"
    And merged entry should contain "Port 2213"
    And merged entry should contain "User devuser"
    And merged entry should contain "ForwardAgent yes"
    And merged entry should contain "StrictHostKeyChecking no"
    And merged entry should contain "IdentityFile" pointing to detected key

  @requires-docker-ssh
  Scenario: SSH config entries are static and preserved when VM is removed
    Given ~/.ssh/vde/config contains "Host vde-python"
    And ~/.ssh/vde/config contains "Host vde-rust"
    And ~/.ssh/vde/config contains user's "Host github.com" entry
    When I remove VM for SSH cleanup "python"
    Then ~/.ssh/vde/config should still contain "Host vde-python"
    And ~/.ssh/vde/config should still contain "Host vde-rust"
    And ~/.ssh/vde/config should still contain "Host github.com"
    And user's entries should be preserved

  # =============================================================================
  # SSH known_hosts Cleanup Tests - Prevents "host key changed" warnings
  # =============================================================================

  @requires-docker-ssh
  Scenario: Remove known_hosts entry when VM is removed
    Given VM "python" is created with SSH port "2213"
    And ~/.ssh/vde/known_hosts contains entry for "[localhost]:2213"
    When I remove VM for SSH cleanup "python"
    Then ~/.ssh/vde/known_hosts should NOT contain entry for "[localhost]:2213"
    And ~/.ssh/vde/known_hosts should NOT contain entry for "[::1]:2213"

  @requires-docker-ssh
  Scenario: Remove multiple hostname patterns from known_hosts
    Given VM "postgres" is created with SSH port "2404"
    And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
    And ~/.ssh/vde/known_hosts contains "[::1]:2404"
    And ~/.ssh/vde/known_hosts contains "postgres" hostname entry
    When I remove VM for SSH cleanup "postgres"
    Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2404"
    And ~/.ssh/vde/known_hosts should NOT contain "[::1]:2404"
    And ~/.ssh/vde/known_hosts should NOT contain "postgres" entry

  @requires-docker-ssh
  Scenario: Create backup of known_hosts before cleanup
    Given ~/.ssh/vde/known_hosts exists with content
    And VM "redis" is created with SSH port "2406"
    When I remove VM for SSH cleanup "redis"
    Then known_hosts backup file should exist at "~/.ssh/vde/known_hosts.vde-backup"
    And backup should contain original content

  @requires-docker-ssh
  Scenario: Known_hosts cleanup handles missing file gracefully
    Given ~/.ssh/vde/known_hosts does not exist
    And VM "python" is created with SSH port "2213"
    When I remove VM for SSH cleanup "python"
    Then command should succeed without error
    And no known_hosts file should be created

  @requires-docker-ssh
  Scenario: Known_hosts cleanup removes entries by port number
    Given ~/.ssh/vde/known_hosts contains multiple port entries
    And ~/.ssh/vde/known_hosts contains "[localhost]:2213"
    And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
    When VM with port "2213" is removed
    Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2213"
    And ~/.ssh/vde/known_hosts should still contain "[localhost]:2404"

  @requires-docker-ssh
  Scenario: Recreating VM after removal succeeds without host key warning
    Given VM "python" was previously created with SSH port "2213"
    And ~/.ssh/vde/known_hosts had old entry for "[localhost]:2213"
    When I remove VM for SSH cleanup "python"
    And I create VM "python" with SSH port "2213"
    Then SSH connection should succeed without host key warning
    And ~/.ssh/vde/known_hosts should contain new entry for "[localhost]:2213"
