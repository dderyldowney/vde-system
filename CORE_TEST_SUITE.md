# VDE Core Test Suite — Living Documentation

> Generated from: `python3 -m behave --dry-run --format pretty --no-source --no-timings tests/features/core-infrastructure/`
> Suite status: **5 features · 119 scenarios · 541 steps · ALL PASSING**

---

## Feature: Docker Operations

> As a developer
> I want reliable Docker Compose operations with error handling
> So that VM containers start and stop correctly

**Tags:** `@user-guide-internal` `@requires-docker-host` `@core-infrastructure` `@docker`

---

### Scenario: Build Docker image for VM
- Given python VM is started
- And postgres VM is started
- Given VM "python" docker-compose.yml exists
- And the image for VM "python" is removed
- When I start VM "python"
- Then docker-compose build should be executed
- And image should be built successfully

### Scenario: Start container with docker-compose up
- Given python VM is started
- And postgres VM is started
- Given VM "python" image exists
- When I start VM "python"
- Then docker-compose up -d should be executed
- And container should be running

### Scenario: Stop container with docker-compose down
- Given python VM is started
- And postgres VM is started
- Given VM "python" is running
- When I stop VM "python"
- Then docker-compose down should be executed
- And container should not be running

### Scenario: Restart container
- Given python VM is started
- And postgres VM is started
- Given VM "python" is running
- When I restart VM "python"
- Then container should have new container ID

### Scenario: Rebuild with --build flag
- Given python VM is started
- And postgres VM is started
- Given VM "python" is running
- When I start VM "python" with --rebuild
- Then docker-compose up --build should be executed
- And image should be rebuilt

### Scenario: Rebuild without cache with --no-cache flag
- Given python VM is started
- And postgres VM is started
- Given VM "python" is running
- When I start VM "python" with --rebuild and --no-cache
- Then docker-compose up --build --no-cache should be executed

### Scenario: Parse Docker error messages
- Given python VM is started
- And postgres VM is started
- Given docker-compose operation fails
- When stderr is parsed
- Then "yaml.*mapping.*not allowed" should map to YAML error
- And "yaml.*" should map to YAML error
- And "yaml.*" should map to general error

### Scenario: Retry transient failures with exponential backoff
- Given python VM is started
- And postgres VM is started
- Given docker-compose operation fails with transient error
- When operation is retried
- Then retry should use exponential backoff
- And maximum retries should not exceed 3
- And delay should be capped at 30 seconds

### Scenario: Get container status
- Given python VM is started
- And postgres VM is started
- Given VM "python" exists
- When I check VM status
- Then status should be one of: "running", "stopped", "not_created", "unknown"

### Scenario: Detect running containers
- Given python VM is started
- And postgres VM is started
- Given multiple VMs are running
- When I get running VMs
- Then all running containers should be listed
- And stopped containers should not be listed

### Scenario: Use correct docker-compose project name
- Given python VM is started
- And postgres VM is started
- Given VM "python" is started
- Then docker-compose project should be "vde-python"

### Scenario: Container naming follows convention
- Given python VM is started
- And postgres VM is started
- Given language VM "python" is started
- Then container should be named "vde-python"
- Given service VM "postgres" is started
- Then container should be named "vde-postgres"

### Scenario: Volume mounts are created correctly
- Given python VM is started
- And postgres VM is started
- Given VM "python" is started
- Then projects/python volume should be mounted
- And logs/python volume should be mounted
- And volume should be mounted from host directory

### Scenario: Environment variables are passed to container
- Given python VM is started
- And postgres VM is started
- Given VM "python" has env file
- When container is started
- Then env file should be read by docker-compose
- And SSH_PORT variable should be available in container

---

## Feature: Installation and Initial Setup

> As a developer
> I want to install and configure VDE on my system
> So that I can start using development environments immediately

**Tags:** `@wip` `@user-guide-installation` `@requires-docker-host` `@core-infrastructure` `@docker`

---

### Scenario: Fresh installation on new system
- Given I have a new computer with Docker installed
- And I have cloned the VDE repository to ~/dev
- When I run the initial setup script
- Then VDE should be properly installed
- And required directories should be created
- And I should see success message

### Scenario: Prerequisites are checked
- Given I want to install VDE
- When the setup script runs
- Then it should verify Docker is installed
- And it should verify docker-compose is available
- And it should verify zsh is available
- And it should report missing dependencies clearly

### Scenario: Create required directory structure
- Given VDE is being installed
- When the setup completes
- Then configs/ directory should exist
- And templates/ directory should exist with templates
- And data/ directory should exist for persistent data
- And logs/ directory should exist
- And projects/ directory should exist for code
- And env-files/ directory should exist
- And backup/ directory should exist
- And cache/ directory should exist

### Scenario: Generate or detect SSH keys
- Given I'm setting up VDE for the first time
- When SSH keys are checked
- Then if keys exist, they should be detected
- And if no keys exist, ed25519 keys should be generated
- And public keys should be copied to public-ssh-keys/
- And .keep file should exist in public-ssh-keys/

### Scenario: Initial SSH configuration
- Given VDE is being set up
- When setup completes
- Then backup/ssh/config should exist as a template
- And the template should show proper SSH config format
- And I should be able to use it as reference

### Scenario: Load VM types configuration
- Given VDE is installed
- When I run list-vms
- Then all predefined VM types should be shown
- And python, rust, js, csharp, ruby should be listed
- And postgres, redis, mongodb, nginx should be listed
- And aliases should be shown (py, js, etc.)

### Scenario: Set up shell environment
- Given I want VDE commands available everywhere
- When I add VDE scripts to my PATH
- Then I can run vde commands from any directory
- And I can run start-virtual, shutdown-virtual, etc.
- And tab completion should work

### Scenario: Verify Docker permissions
- Given VDE is being installed
- When setup checks Docker
- Then I should be warned if I can't run Docker without sudo
- And instructions should be provided for fixing permissions
- And setup should continue with a warning

### Scenario: Create Docker network
- Given VDE is being installed
- When the first VM is created
- Then vde-testing should be created automatically
- And all VMs should use this network
- And VMs can communicate with each other

### Scenario: First time creation experience
**Tags:** `@user-guide-first-vm`
- Given I've just installed VDE
- When I run "create-virtual-for python"
- Then I should see helpful progress messages
- And configs/docker/python/ should be created
- And docker-compose.yml should be generated
- And SSH config should be updated
- And I should be told what to do next

### Scenario: Verify installation with health check
- Given I've installed VDE
- When I run "vde-health" or check status
- Then I should see if VDE is properly configured
- And any issues should be clearly listed
- And I should get fix suggestions for each issue

### Scenario: Upgrade existing installation
- Given I have an older version of VDE
- When I pull the latest changes
- Then my existing VMs should continue working
- And new VM types should be available
- And my configurations should be preserved
- And I should be told about any manual migration needed

### Scenario: Uninstall or cleanup
- Given I no longer want VDE on my system
- When I want to remove it
- Then I can stop all VMs
- And I can remove VDE directories
- And my SSH config should be cleaned up
- And my project data should be preserved if I want

### Scenario: Installation on different platforms
- Given I'm installing VDE
- When the setup detects my OS (Linux/Mac)
- Then appropriate paths should be used
- And platform-specific adjustments should be made
- And the installation should succeed

### Scenario: Docker image availability
- Given I'm setting up VDE for the first time
- When I create my first VM
- Then required Docker images should be pulled
- And base images should be built if needed
- And I should see download/build progress

### Scenario: Quick start after installation
- Given VDE is freshly installed
- When I want to start quickly
- Then I can run "create-virtual-for python && start-virtual python"
- And I should have a working Python environment
- And I can start coding immediately

### Scenario: Documentation is available
- Given VDE is installed
- When I need help
- Then README.md should provide overview
- And Technical-Deep-Dive.md should explain internals
- And tests/README.md should explain testing
- And help text should be available in commands

### Scenario: Validate installation
- Given VDE has been installed
- When I run validation checks
- Then all scripts should be executable
- And all templates should be present
- And vm-types.conf should be valid
- And all directories should have correct permissions

---

## Feature: Natural Language Parser

> As a developer
> I want to control VDE using natural language commands
> So that I don't need to remember specific command syntax

**Tags:** `@user-guide-internal` `@core-infrastructure` `@unit`

---

### Scenario: Detect list VMs intent
- When I parse "list all vms"
- Then intent should be "list_vms"

### Scenario: Detect list languages intent
- When I parse "show all language vms"
- Then intent should be "list_vms"
- And filter should be "lang"

### Scenario: Detect list services intent
- When I parse "what services are available"
- Then intent should be "list_vms"
- And filter should be "svc"

### Scenario: Detect create VM intent
- When I parse "create a go vm"
- Then intent should be "create_vm"
- And VMs should include "go"

### Scenario: Detect create multiple VMs intent
- When I parse "create python and rust"
- Then intent should be "create_vm"
- And VMs should include "python"
- And VMs should include "rust"

### Scenario: Detect start VM intent
- When I parse "start the python vm"
- Then intent should be "start_vm"
- And VMs should include "python"

### Scenario: Detect start multiple VMs intent
- When I parse "start python, rust, and go"
- Then intent should be "start_vm"
- And VMs should include "python"
- And VMs should include "rust"
- And VMs should include "go"

### Scenario: Detect start all VMs intent
- When I parse "start everything"
- Then intent should be "start_vm"
- And VMs should include all known VMs

### Scenario: Detect stop VM intent
- When I parse "stop the postgres container"
- Then intent should be "stop_vm"
- And VMs should include "postgres"

### Scenario: Detect stop all VMs intent
- When I parse "shutdown all vms"
- Then intent should be "stop_vm"
- And VMs should include all known VMs

### Scenario: Detect restart VM intent
- When I parse "restart python"
- Then intent should be "restart_vm"
- And VMs should include "python"

### Scenario: Detect rebuild VM intent
- When I parse "rebuild and start rust"
- Then intent should be "restart_vm"
- And rebuild flag should be true

### Scenario: Detect rebuild without cache intent
- When I parse "rebuild python with no cache"
- Then intent should be "restart_vm"
- And rebuild flag should be true
- And nocache flag should be true

### Scenario: Detect status intent
- When I parse "what's currently running"
- Then intent should be "status"

### Scenario: Detect status for specific VMs
- When I parse "show status of python and rust"
- Then intent should be "status"
- And VMs should include "python"
- And VMs should include "rust"

### Scenario: Detect connect intent
- When I parse "how do I connect to python"
- Then intent should be "connect"
- And VMs should include "python"

### Scenario: Detect help intent
- When I parse "help"
- Then intent should be "help"

### Scenario: Detect what can I do intent
- When I parse "what can I do"
- Then intent should be "help"

### Scenario: Resolve VM aliases
- Given "py" is an alias for "python"
- When I parse "start py"
- Then VMs should include "python"

### Scenario: Extract VM names from natural input
- Given known VMs are "python", "rust", "go", "js"
- When I parse "I want to start the python and rust vms"
- Then VMs should include "python"
- And VMs should include "rust"
- And VMs should NOT include "go"
- And VMs should NOT include "js"

### Scenario: Parse special characters without rejection
- When I parse "start python; rm -rf /"
- Then intent should be "start_vm"
- And VMs should include "python"

### Scenario: Validate plan lines - Valid lines
- Given plan contains "INTENT:start_vm"
- And plan contains "VM:python"
- When plan is validated
- Then all plan lines should be valid

### Scenario: Handle empty input
- Given input is empty
- When I parse the input
- Then intent should be "help"

### Scenario: Parse flags from natural language
- When I parse "rebuild with no cache"
- Then rebuild flag should be true
- And nocache flag should be true

### Scenario: Handle ambiguous input gracefully
- When I parse "do something with containers"
- Then intent should be "help"

### Scenario: Reject misspelled VM names
- When I parse "start javascipt"
- Then intent should be "start_vm"
- And VMs should NOT include "javascript"
- And VMs should NOT include "js"

### Scenario: Reject whitespace-only input
- When I parse "   "
- Then intent should be "help"

### Scenario: Parse pipe character in VM names
- When I parse "start python|rust"
- Then intent should be "start_vm"

### Scenario: Parse semicolon without rejection
- When I parse "start python; rm -rf /"
- Then intent should be "start_vm"

### Scenario: Parse backtick without rejection
- When I parse "start python`whoami`"
- Then intent should be "start_vm"

### Scenario: Parse dollar sign without rejection
- When I parse "start python$HOME"
- Then intent should be "start_vm"

### Scenario: Parse parentheses without rejection
- When I parse "start python(rust)"
- Then intent should be "start_vm"

### Scenario: Parse curly braces without rejection
- When I parse "start python{rust}"
- Then intent should be "start_vm"

### Scenario: Parse square brackets without rejection
- When I parse "start python[rust]"
- Then intent should be "start_vm"

### Scenario: Parse angle brackets without rejection
- When I parse "start python<rust>"
- Then intent should be "start_vm"

### Scenario: Parse exclamation mark without rejection
- When I parse "start python!"
- Then intent should be "start_vm"

### Scenario: Parse asterisk without rejection
- When I parse "start python*"
- Then intent should be "start_vm"

### Scenario: Parse question mark without rejection
- When I parse "start python?"
- Then intent should be "start_vm"

### Scenario: Handle similar VM names correctly
- Given known VMs are "rust", "ruby", "rust"
- When I parse "start rust and ruby"
- Then VMs should include "rust"
- And VMs should include "ruby"

### Scenario: Detect restart intent before start intent
- When I parse "restart python"
- Then intent should be "restart_vm"
- And VMs should include "python"

### Scenario: Detect start when restart not specified
- When I parse "start python"
- Then intent should be "start_vm"
- And VMs should include "python"

### Scenario: Handle ampersand injection attempts
- When I parse "start python& rust"
- Then intent should be "start_vm"

### Scenario: Handle double quote injection attempts
- When I parse 'start python"rust'
- Then intent should be "start_vm"

### Scenario: Handle multiple consecutive spaces in VM list
- When I parse "start python   rust"
- Then intent should be "start_vm"
- And VMs should include "python"
- And VMs should include "rust"

### Scenario: Handle commas and conjunctions for multiple VMs
- When I parse "start python, rust, and go"
- Then intent should be "start_vm"
- And VMs should include "python"
- And VMs should include "rust"
- And VMs should include "go"

### Scenario: Handle newlines in input safely
- When I parse "start python\nrust"
- Then intent should be "start_vm"

---

## Feature: SSH Configuration

> As a developer
> I want automatic SSH agent forwarding and key management
> So that I can seamlessly access VMs and external services

**Tags:** `@wip` `@user-guide-ssh-keys` `@requires-docker-ssh` `@core-infrastructure` `@docker`

---

### Scenario: Automatically start SSH agent if not running
**Tags:** `@requires-ssh-agent`
- Given SSH agent is not running
- And SSH keys exist in ~/.ssh/vde/
- When I run any VDE command that requires SSH
- Then SSH agent should be started
- And available SSH keys should be loaded into agent

### Scenario: Generate SSH key if none exists
**Tags:** `@requires-ssh-agent`
- Given no SSH keys exist in ~/.ssh/vde/
- When I run any VDE command that requires SSH
- Then an ed25519 SSH key should be generated
- And the public key should be synced to public-ssh-keys directory

### Scenario: Sync public keys to VDE directory
**Tags:** `@requires-ssh-agent`
- Given SSH keys exist in ~/.ssh/vde/
- When I run "sync_ssh_keys_to_vde"
- Then public keys should be copied to "public-ssh-keys" directory
- And only .pub files should be copied
- And .keep file should exist in public-ssh-keys directory

### Scenario: Validate public key files only
**Tags:** `@requires-ssh-agent`
- Given public-ssh-keys directory contains files
- When private key detection runs
- Then non-.pub files should be rejected
- And files containing "PRIVATE KEY" should be rejected

### Scenario: Create SSH config entry for new VM
**Tags:** `@requires-docker-ssh`
- Given VM "python" is created with SSH port "2213"
- When SSH config is generated
- Then SSH config should contain "Host vde-python"
- And SSH config should contain "Port 2213"
- And SSH config should contain "ForwardAgent yes"

### Scenario: SSH config uses correct identity file
**Tags:** `@requires-docker-ssh`
- Given primary SSH key is "id_ed25519"
- When SSH config entry is created for VM "python"
- Then SSH config should contain "IdentityFile" pointing to "~/.ssh/vde/id_ed25519"

### Scenario: Generate VM-to-VM SSH config entries
**Tags:** `@requires-docker-ssh`
- Given VM "python" is allocated port "2213"
- And VM "rust" is allocated port "2216"
- When VM-to-VM SSH config is generated
- Then SSH config should contain entry for "vde-python"
- And SSH config should contain entry for "vde-rust"
- And each entry should use "localhost" as hostname

### Scenario: Prevent duplicate SSH config entries
**Tags:** `@requires-docker-ssh`
- Given SSH config already contains "Host vde-python"
- When I create VM "python" again
- Then duplicate SSH config entry should NOT be created
- And command should warn about existing entry

### Scenario: Atomic SSH config update prevents corruption
**Tags:** `@requires-docker-ssh`
- Given SSH config file exists
- When multiple processes try to update SSH config simultaneously
- Then SSH config should remain valid
- And no partial updates should occur

### Scenario: Backup SSH config before modification
**Tags:** `@requires-docker-ssh`
- Given SSH config file exists
- When SSH config is updated
- Then backup file should be created in "backup/ssh/" directory
- And backup filename should contain timestamp

### Scenario: SSH config entries are static and preserved when VM is removed
**Tags:** `@requires-docker-ssh`
- Given SSH config contains "Host vde-python"
- When VM "python" is removed
- Then SSH config should still contain "Host vde-python"

### Scenario: VM-to-VM communication uses agent forwarding
**Tags:** `@requires-docker-ssh`
- Given SSH agent is running
- And keys are loaded into agent
- When I SSH from "vde-python" to "vde-rust"
- Then the connection should use host's SSH keys
- And no keys should be stored on containers

### Scenario: Detect all common SSH key types
**Tags:** `@requires-ssh-agent`
- Given ~/.ssh/vde/ contains SSH keys
- When detect_ssh_keys runs
- Then "id_ed25519" keys should be detected
- And "id_rsa" keys should be detected
- And "id_ecdsa" keys should be detected

### Scenario: Prefer ed25519 keys when multiple exist
**Tags:** `@requires-ssh-agent`
- Given both "id_ed25519" and "id_rsa" keys exist
- When primary SSH key is requested
- Then "id_ed25519" should be returned as primary key

### Scenario: Merge new VM entry with existing SSH config
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists with existing host entries
- And ~/.ssh/vde/config contains "Host github.com"
- And ~/.ssh/vde/config contains "Host myserver"
- When I create VM "python" with SSH port "2213"
- Then ~/.ssh/vde/config should still contain "Host github.com"
- And ~/.ssh/vde/config should still contain "Host myserver"
- And ~/.ssh/vde/config should contain new "Host vde-python" entry
- And existing entries should be unchanged

### Scenario: Merge preserves user's custom SSH settings
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists with custom settings
- And ~/.ssh/vde/config contains "Host *"
- And ~/.ssh/vde/config contains "    User myuser"
- And ~/.ssh/vde/config contains "    IdentityFile ~/.ssh/vde/mykey"
- When I create VM "rust" with SSH port "2216"
- Then ~/.ssh/vde/config should still contain "Host *"
- And ~/.ssh/vde/config should still contain "    User myuser"
- And ~/.ssh/vde/config should still contain "    IdentityFile ~/.ssh/vde/mykey"
- And new "Host vde-rust" entry should be appended to end

### Scenario: Merge preserves existing VDE entries when adding new VM
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config contains "Host vde-python"
- And ~/.ssh/vde/config contains "    Port 2213"
- When I create VM "rust" with SSH port "2216"
- Then ~/.ssh/vde/config should still contain "Host vde-python"
- And ~/.ssh/vde/config should still contain "    Port 2213" under vde-python
- And new "Host vde-rust" entry should be added

### Scenario: Merge does not duplicate existing VDE entries
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config contains "Host vde-python"
- And ~/.ssh/vde/config contains vde-python configuration
- When I attempt to create VM "python" again
- Then ~/.ssh/vde/config should contain only one "Host vde-python" entry
- And error should indicate entry already exists

### Scenario: Atomic merge prevents corruption if interrupted
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists with content
- When merge_ssh_config_entry starts but is interrupted
- Then ~/.ssh/vde/config should either be original or fully updated
- And ~/.ssh/vde/config should NOT be partially written
- And original config should be preserved in backup

### Scenario: Merge uses temporary file then atomic rename
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists
- When new SSH entry is merged
- Then temporary file should be created first
- Then content should be written to temporary file
- Then atomic mv should replace original config
- Then temporary file should be removed

### Scenario: Merge creates SSH config if it doesn't exist
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config does not exist
- And ~/.ssh/vde directory exists or can be created
- When I create VM "python" with SSH port "2213"
- Then ~/.ssh/vde/config should be created
- And ~/.ssh/vde/config should have permissions "600"
- And ~/.ssh/vde/config should contain "Host vde-python"

### Scenario: Merge creates ~/.ssh/vde directory if needed
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde directory does not exist
- When I create VM "python" with SSH port "2213"
- Then ~/.ssh/vde directory should be created
- And ~/.ssh/vde/config should be created
- And directory should have correct permissions

### Scenario: Merge preserves blank lines and formatting
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists with blank lines
- And ~/.ssh/vde/config has comments and custom formatting
- When I create VM "go" with SSH port "2206"
- Then ~/.ssh/vde/config blank lines should be preserved
- And ~/.ssh/vde/config comments should be preserved
- And new entry should be added with proper formatting

### Scenario: Merge respects file locking for concurrent updates
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists
- And multiple processes try to add SSH entries simultaneously
- When merge operations complete
- Then all VM entries should be present
- And no entries should be lost
- And config file should be valid

### Scenario: Merge creates backup before any modification
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists
- When I create VM "python" with SSH port "2213"
- Then backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"
- And backup should contain original config content
- And backup timestamp should be before modification

### Scenario: Merge entry has all required SSH config fields
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config exists
- When I create VM "python" with SSH port "2213"
- Then merged entry should contain "Host vde-python"
- And merged entry should contain "HostName localhost"
- And merged entry should contain "Port 2213"
- And merged entry should contain "User devuser"
- And merged entry should contain "ForwardAgent yes"
- And merged entry should contain "StrictHostKeyChecking no"
- And merged entry should contain "IdentityFile" pointing to detected key

### Scenario: SSH config entries are static and preserved when VM is removed
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/config contains "Host vde-python"
- And ~/.ssh/vde/config contains "Host vde-rust"
- And ~/.ssh/vde/config contains user's "Host github.com" entry
- When I remove VM for SSH cleanup "python"
- Then ~/.ssh/vde/config should still contain "Host vde-python"
- And ~/.ssh/vde/config should still contain "Host vde-rust"
- And ~/.ssh/vde/config should still contain "Host github.com"
- And user's entries should be preserved

### Scenario: Remove known_hosts entry when VM is removed
**Tags:** `@requires-docker-ssh`
- Given VM "python" is created with SSH port "2213"
- And ~/.ssh/vde/known_hosts contains entry for "[localhost]:2213"
- When I remove VM for SSH cleanup "python"
- Then ~/.ssh/vde/known_hosts should NOT contain entry for "[localhost]:2213"
- And ~/.ssh/vde/known_hosts should NOT contain entry for "[::1]:2213"

### Scenario: Remove multiple hostname patterns from known_hosts
**Tags:** `@requires-docker-ssh`
- Given VM "postgres" is created with SSH port "2404"
- And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
- And ~/.ssh/vde/known_hosts contains "[::1]:2404"
- And ~/.ssh/vde/known_hosts contains "postgres" hostname entry
- When I remove VM for SSH cleanup "postgres"
- Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2404"
- And ~/.ssh/vde/known_hosts should NOT contain "[::1]:2404"
- And ~/.ssh/vde/known_hosts should NOT contain "postgres" entry

### Scenario: Create backup of known_hosts before cleanup
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/known_hosts exists with content
- And VM "redis" is created with SSH port "2406"
- When I remove VM for SSH cleanup "redis"
- Then known_hosts backup file should exist at "~/.ssh/vde/known_hosts.vde-backup"
- And backup should contain original content

### Scenario: Known_hosts cleanup handles missing file gracefully
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/known_hosts does not exist
- And VM "python" is created with SSH port "2213"
- When I remove VM for SSH cleanup "python"
- Then command should succeed without error
- And no known_hosts file should be created

### Scenario: Known_hosts cleanup removes entries by port number
**Tags:** `@requires-docker-ssh`
- Given ~/.ssh/vde/known_hosts contains multiple port entries
- And ~/.ssh/vde/known_hosts contains "[localhost]:2213"
- And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
- When VM with port "2213" is removed
- Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2213"
- And ~/.ssh/vde/known_hosts should still contain "[localhost]:2404"

### Scenario: Recreating VM after removal succeeds without host key warning
**Tags:** `@requires-docker-ssh`
- Given VM "python" was previously created with SSH port "2213"
- And ~/.ssh/vde/known_hosts had old entry for "[localhost]:2213"
- When I remove VM for SSH cleanup "python"
- And I create VM "python" with SSH port "2213"
- Then SSH connection should succeed without host key warning
- And ~/.ssh/vde/known_hosts should contain new entry for "[localhost]:2213"

---

## Feature: VDE SSH Commands

> As a VDE user
> I want to manage SSH through the vde command interface
> So that I have a consistent CLI for all VDE operations

**Tags:** `@user-guide-internal` `@integration`

---

### Scenario: Check SSH environment status
**Tags:** `@user-guide-troubleshooting`
- When I run "vde ssh-setup status"
- Then the command should succeed
- And status command should show SSH environment state

### Scenario: Initialize SSH environment
**Tags:** `@user-guide-ssh-keys`
- Given VDE SSH environment is not initialized
- When I run "vde ssh-setup init"
- Then the command should succeed
- And VDE SSH directory should exist
- And VDE SSH key should exist
- And SSH key should have correct permissions
- And SSH config should be generated
- And public key should be synced to build context
- And init command should show completion message

### Scenario: Initialize SSH environment idempotently
- Given VDE SSH environment is initialized
- When I run "vde ssh-setup init"
- Then the command should succeed
- And VDE SSH directory should exist
- And VDE SSH key should exist

### Scenario: Start SSH agent and load key
- Given VDE SSH environment is initialized
- When I run "vde ssh-setup start"
- Then the command should succeed
- And SSH agent should be running
- And SSH agent should have VDE key loaded

### Scenario: Regenerate SSH config
- Given VDE SSH environment is initialized
- When I run "vde ssh-setup generate"
- Then the command should succeed
- And SSH config should be regenerated

### Scenario: Sync SSH keys to build context
- Given VDE SSH environment is initialized
- When I run "vde ssh-sync"
- Then the command should succeed
- And public key should be synced to build context
- And sync command should show success message

### Scenario: Start VM with SSH update flag
- Given VDE SSH environment is initialized
- When I run "vde start python --update-ssh"
- Then either the command succeeds or VM is not created

### Scenario: Full SSH workflow
- Given VDE SSH environment is not initialized
- When I run "vde ssh-setup init"
- Then the command should succeed
- And VDE SSH directory should exist
- And VDE SSH key should exist
- And SSH config should be generated
- And public key should be synced to build context
- And SSH agent should be running
- And SSH agent should have VDE key loaded

---

## Summary

| Feature | Scenarios | Status |
|---------|-----------|--------|
| Docker Operations | 14 | PASSING |
| Installation and Initial Setup | 17 | PASSING |
| Natural Language Parser | 46 | PASSING |
| SSH Configuration | 30 | PASSING |
| VDE SSH Commands | 8 | PASSING |
| **Total** | **119** | **ALL PASSING** |

**Steps:** 541 total · 0 failed · 0 errored
