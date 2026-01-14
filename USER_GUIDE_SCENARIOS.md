# VDE Test Scenarios Reference

> **This is a reference document showing all BDD test scenarios.** For the user guide, see USER_GUIDE.md

---

## Table of Contents

11. [1. Installation: Getting VDE on Your Computer](#1.-installation-getting-vde-on-your-computer)
11. [2. SSH Keys: Setting Up Secure Access](#2.-ssh-keys-setting-up-secure-access)
11. [3. Your First VM: The "Hello World" Moment](#3.-your-first-vm-the-"hello-world"-moment)
11. [4. Understanding What Just Happened](#4.-understanding-what-just-happened)
11. [5. Starting and Stopping Your First VM](#5.-starting-and-stopping-your-first-vm)
11. [6. Your First Cluster: Python + PostgreSQL + Redis](#6.-your-first-cluster-python-+-postgresql-+-redis)
11. [7. Connecting to Your VMs](#7.-connecting-to-your-vms)
11. [8. Working with Databases](#8.-working-with-databases)
11. [9. Daily Workflow: Starting Your Day](#9.-daily-workflow-starting-your-day)
11. [10. Adding More Languages](#10.-adding-more-languages)
11. [11. Troubleshooting: When Things Go Wrong](#11.-troubleshooting-when-things-go-wrong)

---

## 1. Installation: Getting VDE on Your Computer

**Scenario: Data science project setup**

```
Given I am doing data analysis
When I request to "start python and r"
Then the Python VM should start
And the R VM should start
And both should have data science tools available
```

**Scenario: Example 1 - Python API with PostgreSQL Setup**

```
Given I am following the documented Python API workflow
When I plan to create a Python VM
Then the plan should include the create_vm intent
And the plan should include the Python VM
```

**Scenario: Example 3 - Microservices Architecture Setup**

```
Given I am creating a microservices architecture
When I plan to create Python, Go, Rust, PostgreSQL, and Redis
Then the plan should include all five VMs
And each VM should be included in the VM list
```

**Scenario: Daily Workflow - Morning Setup**

```
Given I am starting my development day
When I plan to start Python, PostgreSQL, and Redis
Then the plan should include all three VMs
And the plan should use the start_vm intent
```

**Scenario: New Project Setup - Discover Available VMs**

```
Given I am setting up a new project
When I ask what VMs can I create
Then the plan should include the list_vms intent
And I should see all available VM types
```

**Scenario: New Project Setup - Choose Full Stack**

```
Given I want a Python API with PostgreSQL
When I plan to create Python and PostgreSQL
Then both VMs should be included in the plan
And the plan should use the create_vm intent
```

**Scenario: New Project Setup - Start Development Stack**

```
Given I have created my VMs
When I plan to start Python and PostgreSQL
Then both VMs should start
And they should be able to communicate
```

**Scenario: Fresh installation on new system**

```
Given I have a new computer with Docker installed
And I have cloned the VDE repository to ~/dev
When I run the initial setup script
Then VDE should be properly installed
And required directories should be created
And I should see success message
```

**Scenario: Prerequisites are checked**

```
Given I want to install VDE
When the setup script runs
Then it should verify Docker is installed
And it should verify docker-compose is available
And it should verify zsh is available
And it should report missing dependencies clearly
```

**Scenario: Create required directory structure**

```
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
```

**Scenario: Generate or detect SSH keys**

```
Given I'm setting up VDE for the first time
When SSH keys are checked
Then if keys exist, they should be detected
And if no keys exist, ed25519 keys should be generated
And public keys should be copied to public-ssh-keys/
And .keep file should exist in public-ssh-keys/
```

**Scenario: Initial SSH configuration**

```
Given VDE is being set up
When setup completes
Then backup/ssh/config should exist as a template
And the template should show proper SSH config format
And I should be able to use it as reference
```

**Scenario: Load VM types configuration**

```
Given VDE is installed
When I run list-vms
Then all predefined VM types should be shown
And python, rust, js, csharp, ruby should be listed
And postgres, redis, mongodb, nginx should be listed
And aliases should be shown (py, js, etc.)
```

**Scenario: Set up shell environment**

```
Given I want VDE commands available everywhere
When I add VDE scripts to my PATH
Then I can run vde commands from any directory
And I can run start-virtual, shutdown-virtual, etc.
And tab completion should work
```

**Scenario: Verify Docker permissions**

```
Given VDE is being installed
When setup checks Docker
Then I should be warned if I can't run Docker without sudo
And instructions should be provided for fixing permissions
And setup should continue with a warning
```

**Scenario: Create Docker network**

```
Given VDE is being installed
When the first VM is created
Then vde-network should be created automatically
And all VMs should use this network
And VMs can communicate with each other
```

**Scenario: First time creation experience**

```
Given I've just installed VDE
When I run "create-virtual-for python"
Then I should see helpful progress messages
And configs/docker/python/ should be created
And docker-compose.yml should be generated
And SSH config should be updated
And I should be told what to do next
```

**Scenario: Verify installation with health check**

```
Given I've installed VDE
When I run "vde-health" or check status
Then I should see if VDE is properly configured
And any issues should be clearly listed
And I should get fix suggestions for each issue
```

**Scenario: Upgrade existing installation**

```
Given I have an older version of VDE
When I pull the latest changes
Then my existing VMs should continue working
And new VM types should be available
And my configurations should be preserved
And I should be told about any manual migration needed
```

**Scenario: Uninstall or cleanup**

```
Given I no longer want VDE on my system
When I want to remove it
Then I can stop all VMs
And I can remove VDE directories
And my SSH config should be cleaned up
And my project data should be preserved if I want
```

**Scenario: Installation on different platforms**

```
Given I'm installing VDE
When the setup detects my OS (Linux/Mac)
Then appropriate paths should be used
And platform-specific adjustments should be made
And the installation should succeed
```

**Scenario: Docker image availability**

```
Given I'm setting up VDE for the first time
When I create my first VM
Then required Docker images should be pulled
And base images should be built if needed
And I should see download/build progress
```

**Scenario: Quick start after installation**

```
Given VDE is freshly installed
When I want to start quickly
Then I can run "create-virtual-for python && start-virtual python"
And I should have a working Python environment
And I can start coding immediately
```

**Scenario: Documentation is available**

```
Given VDE is installed
When I need help
Then README.md should provide overview
And Technical-Deep-Dive.md should explain internals
And tests/README.md should explain testing
And help text should be available in commands
```

**Scenario: Validate installation**

```
Given VDE has been installed
When I run validation checks
Then all scripts should be executable
And all templates should be present
And vm-types.conf should be valid
And all directories should have correct permissions
```

**Scenario: First-time user with no SSH keys**

```
Given I have just cloned VDE
And I do not have any SSH keys
And I do not have an SSH agent running
When I create my first VM
Then an SSH key should be generated automatically
And the SSH agent should be started automatically
And the key should be loaded into the agent
And I should be informed of what happened
And I should be able to use SSH immediately
```

**Scenario: First-time user with existing SSH keys**

```
Given I have just cloned VDE
And I have existing SSH keys in ~/.ssh/
And I do not have an SSH agent running
When I create my first VM
Then my existing SSH keys should be detected automatically
And the SSH agent should be started automatically
And my keys should be loaded into the agent
And I should not need to configure anything manually
```

**Scenario: User with multiple SSH key types**

```
Given I have SSH keys of different types
And I have id_ed25519, id_rsa, and id_ecdsa keys
And I create a new VM
When I start the VM
Then all my SSH keys should be detected
And all keys should be loaded into the agent
And the best key should be selected for SSH config
And I should be able to use any of the keys
```

**Scenario: SSH agent setup is silent during normal operations**

```
Given I have created VMs before
And I have SSH configured
When I create a new VM
Then no SSH configuration messages should be displayed
And the setup should happen automatically
And I should only see VM creation messages
```

**Scenario: SSH agent restart if not running**

```
Given I have VMs configured
And my SSH agent is not running
When I start a VM
Then the SSH agent should be started automatically
And my keys should be loaded automatically
And the VM should start normally
```

**Scenario: Viewing SSH status**

```
Given I have VDE configured
When I run "./scripts/ssh-agent-setup"
Then I should see the SSH agent status
And I should see my available SSH keys
And I should see keys loaded in the agent
And I should see running VMs
And I should see usage examples
```

**Scenario: SSH config auto-generation for all VMs**

```
Given I have created multiple VMs
When I use SSH to connect to any VM
Then the SSH config entries should exist
And I should be able to use short hostnames
And I should not need to remember port numbers
```

**Scenario: Rebuilding VMs preserves SSH configuration**

```
Given I have a running VM with SSH configured
When I shutdown and rebuild the VM
Then my SSH configuration should still work
And I should not need to reconfigure SSH
And my keys should still work
```

**Scenario: Automatic key generation preference**

```
Given I do not have any SSH keys
When I create a VM
Then an ed25519 key should be generated
And ed25519 should be the preferred key type
And the key should be generated with a comment
```

**Scenario: Public keys automatically synced to VDE**

```
Given I have SSH keys on my host
When I create a VM
Then my public keys should be copied to public-ssh-keys/
And all my public keys should be in the VM's authorized_keys
And I should not need to manually copy keys
```

**Scenario: SSH setup works with different SSH clients**

```
Given I have configured SSH through VDE
When I use the system ssh command
And when I use OpenSSH clients
And when I use VSCode Remote-SSH
Then all should work with the same configuration
And all should use my SSH keys
```

**Scenario: No manual SSH configuration needed**

```
Given I am a new VDE user
When I read the documentation
Then I should see that SSH is automatic
And I should not see manual setup instructions
And I should be able to start using VMs immediately
```

**Scenario: Development SSL/TLS setup**

```
Given I need to test HTTPS locally
When I configure nginx VM with SSL
Then I can access my app over HTTPS locally
And certificates can be self-signed for development
And browser warnings are expected but acceptable
```

**Scenario: Quick code review setup**

```
Given a colleague wants to review my code
When I share the repository
And they create the same VMs I have
Then they can run my code immediately
And they see the same environment I do
And review process is faster
```

---

## 2. SSH Keys: Setting Up Secure Access

**Scenario: Automatically start SSH agent if not running**

```
Given SSH agent is not running
And SSH keys exist in ~/.ssh/
When I run any VDE command that requires SSH
Then SSH agent should be started
And available SSH keys should be loaded into agent
```

**Scenario: Generate SSH key if none exists**

```
Given no SSH keys exist in ~/.ssh/
When I run any VDE command that requires SSH
Then an ed25519 SSH key should be generated
And the public key should be synced to public-ssh-keys directory
```

**Scenario: Sync public keys to VDE directory**

```
Given SSH keys exist in ~/.ssh/
When I run "sync_ssh_keys_to_vde"
Then public keys should be copied to "public-ssh-keys" directory
And only .pub files should be copied
And .keep file should exist in public-ssh-keys directory
```

**Scenario: Validate public key files only**

```
Given public-ssh-keys directory contains files
When private key detection runs
Then non-.pub files should be rejected
And files containing "PRIVATE KEY" should be rejected
```

**Scenario: Create SSH config entry for new VM**

```
Given VM "python" is created with SSH port "2200"
When SSH config is generated
Then SSH config should contain "Host python-dev"
And SSH config should contain "Port 2200"
And SSH config should contain "ForwardAgent yes"
```

**Scenario: SSH config uses correct identity file**

```
Given primary SSH key is "id_ed25519"
When SSH config entry is created for VM "python"
Then SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"
```

**Scenario: Generate VM-to-VM SSH config entries**

```
Given VM "python" is allocated port "2200"
And VM "rust" is allocated port "2201"
When VM-to-VM SSH config is generated
Then SSH config should contain entry for "python-dev"
And SSH config should contain entry for "rust-dev"
And each entry should use "localhost" as hostname
```

**Scenario: Prevent duplicate SSH config entries**

```
Given SSH config already contains "Host python-dev"
When I create VM "python" again
Then duplicate SSH config entry should NOT be created
And command should warn about existing entry
```

**Scenario: Atomic SSH config update prevents corruption**

```
Given SSH config file exists
When multiple processes try to update SSH config simultaneously
Then SSH config should remain valid
And no partial updates should occur
```

**Scenario: Backup SSH config before modification**

```
Given SSH config file exists
When SSH config is updated
Then backup file should be created in "backup/ssh/" directory
And backup filename should contain timestamp
```

**Scenario: Remove SSH config entry when VM is removed**

```
Given SSH config contains "Host python-dev"
When VM "python" is removed
Then SSH config should NOT contain "Host python-dev"
```

**Scenario: VM-to-VM communication uses agent forwarding**

```
Given SSH agent is running
And keys are loaded into agent
When I SSH from "python-dev" to "rust-dev"
Then the connection should use host's SSH keys
And no keys should be stored on containers
```

**Scenario: Detect all common SSH key types**

```
Given ~/.ssh/ contains SSH keys
When detect_ssh_keys runs
Then "id_ed25519" keys should be detected
And "id_rsa" keys should be detected
And "id_ecdsa" keys should be detected
And "id_dsa" keys should be detected
```

**Scenario: Prefer ed25519 keys when multiple exist**

```
Given both "id_ed25519" and "id_rsa" keys exist
When primary SSH key is requested
Then "id_ed25519" should be returned as primary key
```

**Scenario: Merge new VM entry with existing SSH config**

```
Given ~/.ssh/config exists with existing host entries
And ~/.ssh/config contains "Host github.com"
And ~/.ssh/config contains "Host myserver"
When I create VM "python" with SSH port "2200"
Then ~/.ssh/config should still contain "Host github.com"
And ~/.ssh/config should still contain "Host myserver"
And ~/.ssh/config should contain new "Host python-dev" entry
And existing entries should be unchanged
```

**Scenario: Merge preserves user's custom SSH settings**

```
Given ~/.ssh/config exists with custom settings
And ~/.ssh/config contains "Host *"
And ~/.ssh/config contains "    User myuser"
And ~/.ssh/config contains "    IdentityFile ~/.ssh/mykey"
When I create VM "rust" with SSH port "2201"
Then ~/.ssh/config should still contain "Host *"
And ~/.ssh/config should still contain "    User myuser"
And ~/.ssh/config should still contain "    IdentityFile ~/.ssh/mykey"
And new "Host rust-dev" entry should be appended to end
```

**Scenario: Merge preserves existing VDE entries when adding new VM**

```
Given ~/.ssh/config contains "Host python-dev"
And ~/.ssh/config contains "    Port 2200"
When I create VM "rust" with SSH port "2201"
Then ~/.ssh/config should still contain "Host python-dev"
And ~/.ssh/config should still contain "    Port 2200" under python-dev
And new "Host rust-dev" entry should be added
```

**Scenario: Merge does not duplicate existing VDE entries**

```
Given ~/.ssh/config contains "Host python-dev"
And ~/.ssh/config contains python-dev configuration
When I attempt to create VM "python" again
Then ~/.ssh/config should contain only one "Host python-dev" entry
And error should indicate entry already exists
```

**Scenario: Atomic merge prevents corruption if interrupted**

```
Given ~/.ssh/config exists with content
When merge_ssh_config_entry starts but is interrupted
Then ~/.ssh/config should either be original or fully updated
And ~/.ssh/config should NOT be partially written
And original config should be preserved in backup
```

**Scenario: Merge uses temporary file then atomic rename**

```
Given ~/.ssh/config exists
When new SSH entry is merged
Then temporary file should be created first
Then content should be written to temporary file
Then atomic mv should replace original config
Then temporary file should be removed
```

**Scenario: Merge creates SSH config if it doesn't exist**

```
Given ~/.ssh/config does not exist
And ~/.ssh directory exists or can be created
When I create VM "python" with SSH port "2200"
Then ~/.ssh/config should be created
And ~/.ssh/config should have permissions "600"
And ~/.ssh/config should contain "Host python-dev"
```

**Scenario: Merge creates .ssh directory if needed**

```
Given ~/.ssh directory does not exist
When I create VM "python" with SSH port "2200"
Then ~/.ssh directory should be created
And ~/.ssh/config should be created
And directory should have correct permissions
```

**Scenario: Merge preserves blank lines and formatting**

```
Given ~/.ssh/config exists with blank lines
And ~/.ssh/config has comments and custom formatting
When I create VM "go" with SSH port "2202"
Then ~/.ssh/config blank lines should be preserved
And ~/.ssh/config comments should be preserved
And new entry should be added with proper formatting
```

**Scenario: Merge respects file locking for concurrent updates**

```
Given ~/.ssh/config exists
And multiple processes try to add SSH entries simultaneously
When merge operations complete
Then all VM entries should be present
And no entries should be lost
And config file should be valid
```

**Scenario: Merge creates backup before any modification**

```
Given ~/.ssh/config exists
When I create VM "python" with SSH port "2200"
Then backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"
And backup should contain original config content
And backup timestamp should be before modification
```

**Scenario: Merge entry has all required SSH config fields**

```
Given ~/.ssh/config exists
When I create VM "python" with SSH port "2200"
Then merged entry should contain "Host python-dev"
And merged entry should contain "HostName localhost"
And merged entry should contain "Port 2200"
And merged entry should contain "User devuser"
And merged entry should contain "ForwardAgent yes"
And merged entry should contain "StrictHostKeyChecking no"
And merged entry should contain "IdentityFile" pointing to detected key
```

**Scenario: Merge removes VM entry when VM is removed**

```
Given ~/.ssh/config contains "Host python-dev"
And ~/.ssh/config contains "Host rust-dev"
And ~/.ssh/config contains user's "Host github.com" entry
When I remove VM "python"
Then ~/.ssh/config should NOT contain "Host python-dev"
And ~/.ssh/config should still contain "Host rust-dev"
And ~/.ssh/config should still contain "Host github.com"
And user's entries should be preserved
```

**Scenario: Verify SSH connection is working**

```
Given I cannot SSH into a VM
When I check the SSH config
And I verify the VM is running
And I verify the port is correct
Then I can identify if the issue is SSH, Docker, or the VM itself
```

**Scenario: Port allocation for SSH**

```
Given I create multiple VMs
When each VM starts
Then each should get a unique SSH port
And ports should be auto-allocated from available range
And no two VMs should have the same SSH port
```

**Scenario: Sync team member's SSH config changes**

```
Given the team has updated SSH config templates
And I pull the latest changes
When I create or restart any VM
Then my SSH config should be updated with new entries
And my existing SSH entries should be preserved
And I should not lose my personal SSH configurations
```

**Scenario: Getting SSH connection information**

```
Given I have a Python VM running
When I ask "how do I connect to Python?"
Then I should receive the SSH port
And I should receive the username (devuser)
And I should receive the hostname (localhost)
```

**Scenario: Connecting with SSH client**

```
Given I have the SSH connection details
When I run "ssh python-dev"
Then I should connect to the Python VM
And I should be logged in as devuser
And I should have a zsh shell
```

**Scenario: Using VSCode Remote-SSH**

```
Given I have VSCode installed
When I add the SSH config for python-dev
Then I can connect using Remote-SSH
And my workspace should be mounted
And I can edit files in the projects directory
```

**Scenario: Multiple SSH connections**

```
Given I have multiple VMs running
When I connect to python-dev
And then connect to postgres-dev
Then both connections should work
And each should use a different port
```

**Scenario: SSH key authentication**

```
Given I have set up SSH keys
When I connect to a VM
Then I should not be prompted for a password
And key-based authentication should be used
```

**Scenario: Workspace directory access**

```
Given I am connected via SSH
When I navigate to ~/workspace
Then I should see my project files
And changes should be reflected on the host
```

**Scenario: Sudo access in container**

```
Given I need to perform administrative tasks
When I run sudo commands in the container
Then they should execute without password
And I should have the necessary permissions
```

**Scenario: Shell configuration**

```
Given I connect via SSH
When I start a shell
Then I should be using zsh
And oh-my-zsh should be configured
And my preferred theme should be active
```

**Scenario: Editor configuration**

```
Given I connect via SSH
When I run nvim
Then LazyVim should be available
And my editor configuration should be loaded
```

**Scenario: Transferring files**

```
Given I am connected to a VM
When I use scp to copy files
Then files should transfer to/from the workspace
And permissions should be preserved
```

**Scenario: Port forwarding for services**

```
Given I have a web service running in a VM
When I access localhost on the VM's port
Then I should reach the service
And the service should be accessible from the host
```

**Scenario: SSH session persistence**

```
Given I have a long-running task in a VM
When my SSH connection drops
Then the task should continue running
And I can reconnect to the same session
```

**Scenario: Sharing SSH configurations**

```
Given a new team member joins
When they ask "how do I connect?"
Then they should receive clear connection instructions
And the instructions should include SSH config examples
And the instructions should work on their first try
```

**Scenario: SSH connection failure**

```
Given a container is running but SSH fails
When I try to connect
Then VDE should diagnose the problem
And check if SSH is running
And verify the SSH port is correct
```

**Scenario: Template includes SSH agent forwarding**

```
Given language VM template is rendered
Then rendered output should contain SSH_AUTH_SOCK mapping
And rendered output should contain .ssh volume mount
```

**Scenario: Template exposes SSH port**

```
Given any VM template is rendered
Then rendered output should expose port "22"
And rendered output should map SSH port to host port
```

**Scenario: Cloning a private repository from within a VM**

```
Given I have a Python VM running
And I have a private repository on GitHub
When I SSH into the Python VM
And I run "git clone git@github.com:myuser/private-repo.git"
Then the repository should be cloned
And I should not be prompted for a password
And my host's SSH keys should be used for authentication
```

**Scenario: Pushing code to GitHub from a VM**

```
Given I have a Go VM running
And I have cloned a repository in the Go VM
And I have made changes to the code
When I run "git commit -am 'Add new feature'"
And I run "git push origin main"
Then the changes should be pushed to GitHub
And my host's SSH keys should be used
And no password should be required
```

**Scenario: Pulling from multiple Git hosts**

```
Given I have a Python VM running
And I have repositories on both GitHub and GitLab
And I have SSH keys configured for both hosts
When I SSH into the Python VM
And I run "git pull" in the GitHub repository
And I run "git pull" in the GitLab repository
Then both repositories should update
And each should use the appropriate SSH key from my host
```

**Scenario: Using Git submodules**

```
Given I have a Rust VM running
And I have a repository with Git submodules
And the submodules are from GitHub
When I SSH into the Rust VM
And I run "git submodule update --init"
Then the submodules should be cloned
And authentication should use my host's SSH keys
```

**Scenario: Git operations in microservices architecture**

```
Given I have multiple VMs for different services
And each service has its own repository
And all repositories use SSH authentication
When I SSH to each VM
And I run "git pull" in each service directory
Then all repositories should update
And all should use my host's SSH keys
And no configuration should be needed in any VM
```

**Scenario: Deploying code from VM to external server**

```
Given I have a deployment server
And I have SSH keys configured for the deployment server
And I have a Python VM where I build my application
When I SSH into the Python VM
And I run "scp app.tar.gz deploy-server:/tmp/"
And I run "ssh deploy-server '/tmp/deploy.sh'"
Then the application should be deployed
And my host's SSH keys should be used for both operations
```

**Scenario: Multiple GitHub accounts**

```
Given I have multiple GitHub accounts
And I have different SSH keys for each account
And all keys are loaded in my SSH agent
When I SSH into a VM
And I clone a repository from account1
And I clone a repository from account2
Then both repositories should be cloned
And each should use the correct SSH key
And the agent should automatically select the right key
```

**Scenario: SSH key passed through to child processes**

```
Given I have a Node.js VM running
And I have an npm script that runs Git commands
When I SSH into the Node.js VM
And I run "npm run deploy" which uses Git internally
Then the deployment should succeed
And the Git commands should use my host's SSH keys
```

**Scenario: Git operations in automated workflows**

```
Given I have a CI/CD script in a VM
And the script performs Git operations
When I run the CI/CD script
Then all Git operations should succeed
And my host's SSH keys should be used
And no manual intervention should be required
```

**Scenario: No key copying to VMs required**

```
Given I have a new VM that needs Git access
And I have SSH keys on my host
When I create and start the VM
And I SSH into the VM
And I run "git clone git@github.com:user/repo.git"
Then the clone should succeed
And I should not have copied any keys to the VM
And only the SSH agent socket should be forwarded
```

**Scenario: Automatically setting up SSH environment when creating a VM**

```
Given I do not have an SSH agent running
And I do not have any SSH keys
When I create a Python VM
Then an SSH agent should be started automatically
And an SSH key should be generated automatically
And the key should be loaded into the agent
And no manual configuration should be required
```

**Scenario: Communicating between language VMs**

```
Given I have a Go VM running
And I have a Python VM running
And I have started the SSH agent
When I SSH into the Go VM
And I run "ssh python-dev" from within the Go VM
Then I should connect to the Python VM
And I should be authenticated using my host's SSH keys
And I should not need to enter a password
And I should not need to copy keys to the Go VM
```

**Scenario: Communicating between language and service VMs**

```
Given I have a Python VM running
And I have a PostgreSQL VM running
When I SSH into the Python VM
And I run "ssh postgres-dev" from within the Python VM
Then I should connect to the PostgreSQL VM
And I should be able to run psql commands
And authentication should use my host's SSH keys
```

**Scenario: Copying files between VMs using SCP**

```
Given I have a Python VM running
And I have a Go VM running
When I create a file in the Python VM
And I run "scp go-dev:/tmp/file ." from the Python VM
Then the file should be copied using my host's SSH keys
And no password should be required
```

**Scenario: Running commands on remote VMs**

```
Given I have a Python VM running
And I have a Rust VM running
When I run "ssh rust-dev pwd" from the Python VM
Then the command should execute on the Rust VM
And the output should be displayed
And authentication should use my host's SSH keys
```

**Scenario: Full stack development workflow**

```
Given I create a Python VM for my API
And I create a PostgreSQL VM for my database
And I create a Redis VM for caching
And I start all VMs
When I SSH into the Python VM
And I run "ssh postgres-dev psql -U devuser -l"
Then I should see the PostgreSQL list of databases
When I run "ssh redis-dev redis-cli ping"
Then I should see "PONG"
And all connections should use my host's SSH keys
```

**Scenario: Microservices architecture communication**

```
Given I have a Go VM running as an API gateway
And I have a Python VM running as a payment service
And I have a Rust VM running as an analytics service
When I SSH into the Go VM
And I run "ssh python-dev curl localhost:8000/health"
And I run "ssh rust-dev curl localhost:8080/metrics"
Then both services should respond
And all authentications should use my host's SSH keys
```

**Scenario: VM-to-VM SSH in development workflow**

```
Given I am developing a full-stack application
And I have frontend, backend, and database VMs
When I need to test the backend from the frontend VM
And I run "ssh backend-dev pytest tests/"
Then the tests should run on the backend VM
And I should see the results in the frontend VM
And authentication should be automatic
```

**Scenario: SSH keys never leave the host**

```
Given I have SSH keys on my host
And I have multiple VMs running
When I SSH from one VM to another
Then the private keys should remain on the host
And only the SSH agent socket should be forwarded
And the VMs should not have copies of my private keys
```

**Scenario: Multiple VMs can use the same agent**

```
Given I have 5 VMs running
And I have 2 SSH keys loaded in the agent
When I SSH from VM1 to VM2
And I SSH from VM2 to VM3
And I SSH from VM3 to VM4
And I SSH from VM4 to VM5
Then all connections should succeed
And all should use my host's SSH keys
And no keys should be copied to any VM
```

**Scenario: Quick access to my projects via SSH**

```
Given I have VMs running for my project
When I run "ssh python-dev"
Then I should be connected immediately
And I don't need to remember ports or IP addresses
And SSH agent forwarding is automatic
```

**Scenario: VSCode Remote-SSH development**

```
Given I have VMs running
When I open VSCode and connect to python-dev via Remote-SSH
Then I get full IDE experience inside the VM
And I can use VSCode extensions for Python
And I can debug directly from my editor
```

---

## 3. Your First VM: The "Hello World" Moment

**Scenario: Create a new language VM**

```
Given the VM "zig" is defined as a language VM with install command "apt-get install -y zig"
And no VM configuration exists for "zig"
When I run "create-virtual-for zig"
Then a docker-compose.yml file should be created at "configs/docker/zig/docker-compose.yml"
And the docker-compose.yml should contain SSH port mapping
And SSH config entry should exist for "zig-dev"
And projects directory should exist at "projects/zig"
And logs directory should exist at "logs/zig"
```

**Scenario: Create a new service VM with custom port**

```
Given the VM "rabbitmq" is defined as a service VM with port "5672"
And no VM configuration exists for "rabbitmq"
When I run "create-virtual-for rabbitmq"
Then a docker-compose.yml file should be created at "configs/docker/rabbitmq/docker-compose.yml"
And the docker-compose.yml should contain service port mapping "5672"
And data directory should exist at "data/rabbitmq"
```

**Scenario: Start a created VM**

```
Given VM "python" has been created
And VM "python" is not running
When I run "start-virtual python"
Then VM "python" should be running
And SSH should be accessible on allocated port
```

**Scenario: Start multiple VMs**

```
Given VM "python" has been created
And VM "rust" has been created
And neither VM is running
When I run "start-virtual python rust"
Then VM "python" should be running
And VM "rust" should be running
And each VM should have a unique SSH port
```

**Scenario: Start all VMs**

```
Given VM "python" has been created
And VM "rust" has been created
And VM "postgres" has been created
And none of the VMs are running
When I run "start-virtual all"
Then all created VMs should be running
```

**Scenario: Stop a running VM**

```
Given VM "python" is running
When I run "shutdown-virtual python"
Then VM "python" should not be running
```

**Scenario: Stop all running VMs**

```
Given VM "python" is running
And VM "rust" is running
When I run "shutdown-virtual all"
Then no VMs should be running
```

**Scenario: Restart a VM**

```
Given VM "python" is running
When I run "shutdown-virtual python && start-virtual python"
Then VM "python" should be running
And the VM should have a fresh container instance
```

**Scenario: Rebuild a VM with --rebuild flag**

```
Given VM "python" is running
When I run "start-virtual python --rebuild"
Then VM "python" should be running
And the container should be rebuilt from the Dockerfile
```

**Scenario: Cannot start non-existent VM**

```
Given VM "nonexistent" is not created
When I run "start-virtual nonexistent"
Then the command should fail with error "VM 'nonexistent' is not created yet"
```

**Scenario: Cannot create duplicate VM**

```
Given VM "python" has been created
When I run "create-virtual-for python"
Then the command should fail with error "already exists"
```

**Scenario: List all predefined VM types**

```
Given VM types are loaded
When I run "list-vms"
Then all language VMs should be listed
And all service VMs should be listed
And aliases should be shown
```

**Scenario: List only language VMs**

```
Given VM types are loaded
When I run "list-vms --lang"
Then only language VMs should be listed
And service VMs should not be listed
```

**Scenario: List only service VMs**

```
Given VM types are loaded
When I run "list-vms --svc"
Then only service VMs should be listed
And language VMs should not be listed
```

**Scenario: Filter VMs by name**

```
Given VM types are loaded
When I run "list-vms python"
Then only VMs matching "python" should be listed
```

**Scenario: Remove a VM**

```
Given VM "python" has been created
When I run "remove-virtual python"
Then docker-compose.yml should not exist at "configs/docker/python/docker-compose.yml"
And SSH config entry for "python-dev" should be removed
And projects directory should still exist at "projects/python"
```

**Scenario: Add a new VM type**

```
When I run "add-vm-type --type lang --display 'Zig Language' zig 'apt-get install -y zig'"
Then "zig" should be in known VM types
And VM type "zig" should have type "lang"
And VM type "zig" should have display name "Zig Language"
```

**Scenario: Add VM type with aliases**

```
When I run "add-vm-type --type lang --display 'JavaScript' js 'apt-get install -y nodejs' 'node,nodejs'"
Then "js" should be in known VM types
And "js" should have aliases "node,nodejs"
And "node" should resolve to "js"
And "nodejs" should resolve to "js"
```

**Scenario: Creating a new VM**

```
Given I want to work with a new language
When I request to "create a Rust VM"
Then the VM configuration should be generated
And the Docker image should be built
And SSH keys should be configured
And the VM should be ready to use
```

**Scenario: Creating multiple VMs at once**

```
Given I need a full stack environment
When I request to "create Python, PostgreSQL, and Redis"
Then all three VMs should be created
And each should have its own configuration
And all should be on the same Docker network
```

**Scenario: Starting a created VM**

```
Given I have created a Go VM
When I request to "start go"
Then the Go container should start
And it should be accessible via SSH
And my workspace should be mounted
```

**Scenario: Starting multiple VMs**

```
Given I have created several VMs
When I request to "start python, go, and postgres"
Then all three VMs should start
And they should be able to communicate
And each should have its own SSH port
```

**Scenario: Checking VM status**

```
Given I have several VMs
When I request "status of all VMs"
Then I should see which VMs are running
And I should see which VMs are stopped
And I should see any error states
```

**Scenario: Stopping a running VM**

```
Given I have a running Python VM
When I request to "stop python"
Then the Python container should stop
And the VM configuration should remain
And I can start it again later
```

**Scenario: Stopping multiple VMs**

```
Given I have multiple running VMs
When I request to "stop python and postgres"
Then both VMs should stop
And other VMs should remain running
```

**Scenario: Restarting a VM**

```
Given I have a running VM
When I request to "restart rust"
Then the Rust VM should stop
And the Rust VM should start again
And my workspace should still be accessible
```

**Scenario: Restarting with rebuild**

```
Given I need to refresh a VM
When I request to "restart python with rebuild"
Then the Python VM should be rebuilt
And the VM should start with the new image
And my workspace should be preserved
```

**Scenario: Deleting a VM**

```
Given I no longer need a VM
When I remove its configuration
Then the VM should be removed
And the container should be stopped if running
And the configuration files should be deleted
```

**Scenario: Rebuilding after code changes**

```
Given I have modified the Dockerfile
When I request to "rebuild go with no cache"
Then the Go VM should be rebuilt from scratch
And no cached layers should be used
And the new image should reflect my changes
```

**Scenario: Upgrading a VM**

```
Given I want to update the base image
When I rebuild the VM
Then the latest base image should be used
And my configuration should be preserved
And my workspace should remain intact
```

**Scenario: Migrating to a new VDE version**

```
Given I have updated VDE scripts
When I rebuild my VMs
Then they should use the new VDE configuration
And my data should be preserved
And my SSH access should continue to work
```

**Scenario: Detect create VM intent**

```
When I parse "create a go vm"
Then intent should be "create_vm"
And VMs should include "go"
```

**Scenario: Create VM with natural language**

```
Given I want a go development environment
When I say "create a go vm"
Then go VM should be created
And I should not need to remember create-virtual-for syntax
```

---

## 4. Understanding What Just Happened

**Scenario: Allocate first available port for language VM**

```
Given no language VMs are created
When I create a language VM
Then the VM should be allocated port "2200"
```

**Scenario: Allocate first available port for service VM**

```
Given no service VMs are created
When I create a service VM
Then the VM should be allocated port "2400"
```

**Scenario: Skip allocated ports when finding next available**

```
Given ports "2200", "2201", "2203" are allocated
When I create a new language VM
Then the VM should be allocated port "2202"
```

**Scenario: Verify volumes are mounted correctly**

```
Given my code changes aren't reflected in the VM
When I check the mounts in the container
Then I can see if the volume is properly mounted
And I can verify the host path is correct
```

**Scenario: Verify network connectivity between VMs**

```
Given two VMs can't communicate
When I check the docker network
Then I should see both VMs on "vde-network"
And I can ping one VM from another
```

**Scenario: Verify port registry consistency**

```
Given port registry cache exists
And a VM has been removed
When port registry is verified
Then removed VM should be removed from registry
And cache file should be updated
```

**Scenario: Example 1 - Verify PostgreSQL Accessibility**

```
Given I have started the PostgreSQL VM
When I check if postgres exists
Then the VM should be recognized as a valid VM type
And it should be marked as a service VM
```

**Scenario: Example 3 - Verify All Microservice VMs Exist**

```
Given I have created microservices
When I check for each service VM
Then Python should exist as a language VM
And Go should exist as a language VM
And Rust should exist as a language VM
And PostgreSQL should exist as a service VM
And Redis should exist as a service VM
```

**Scenario: Daily Workflow - Check Status During Development**

```
Given I am actively developing
When I ask what's running
Then the plan should include the status intent
And I should be able to see running VMs
```

**Scenario: Troubleshooting - Step 1 Check Status**

```
Given something isn't working correctly
When I check the status
Then I should receive status information
And I should see which VMs are running
```

**Scenario: Documentation Accuracy - Verify Examples Work**

```
Given the documentation shows specific VM examples
When I verify the documented VMs
Then Python should be a valid VM type
And JavaScript should be a valid VM type
And all microservice VMs should be valid
```

**Scenario: Listing all available VMs**

```
Given I have VDE installed
When I ask "what VMs can I create?"
Then I should see all available language VMs
And I should see all available service VMs
And each VM should have a display name
And each VM should show its type (language or service)
```

**Scenario: Detect list VMs intent**

```
When I parse "list all vms"
Then intent should be "list_vms"
```

**Scenario: Ask what VMs are available**

```
Given I'm new to VDE
When I ask "what vms can I create?"
Then I should see a list of all available VM types
And aliases should be shown
And I should understand my options
```

**Scenario: Get help with available commands**

```
Given I'm not sure what I can do
When I ask "help" or "what can I do?"
Then I should see available commands
And example commands should be shown
And I should understand how to use VDE
```

---

## 5. Starting and Stopping Your First VM

**Scenario: Detect start VM intent**

```
When I parse "start the python vm"
Then intent should be "start_vm"
And VMs should include "python"
```

**Scenario: Detect stop VM intent**

```
When I parse "stop the postgres container"
Then intent should be "stop_vm"
And VMs should include "postgres"
```

**Scenario: Detect restart VM intent**

```
When I parse "restart python"
Then intent should be "restart_vm"
And VMs should include "python"
```

**Scenario: Start VMs with conversational command**

```
Given I have VMs created but not running
When I say "start the python and rust vms"
Then both python and rust VMs should start
And I should not need to remember the exact command
```

---

## 6. Your First Cluster: Python + PostgreSQL + Redis

**Scenario: Coordinating multi-VM operations from host**

```
Given I have a coordination VM running
And I need to check the status of other VMs
When I SSH into the coordination VM
And I run "to-host docker ps --filter 'name=python-dev'"
Then I should see the status of the Python VM
And I can make decisions based on the status
```

---

## 7. Connecting to Your VMs

**Scenario: Connection help requests**

```
Given I need to connect to a VM
When I ask "how do I connect to the Python environment?"
Then I should receive SSH connection instructions
And the instructions should be clear and actionable
```

**Scenario: Test database connectivity from VM**

```
Given my application can't connect to the database
When I SSH into the application VM
And I try to connect to the database VM directly
Then I can see if the issue is network, credentials, or database state
```

**Scenario: Example 1 - Get Connection Info for Python**

```
Given I need to connect to the Python VM
When I ask for connection information
Then the plan should include the connect intent
And the plan should include the Python VM
```

**Scenario: Daily Workflow - Connect to Primary VM**

```
Given I need to work in my primary development environment
When I ask how to connect to Python
Then the plan should provide connection details
And the plan should include the Python VM
```

**Scenario: Troubleshooting - Step 4 Get Connection Info**

```
Given I need to debug inside a container
When I ask to connect to Python
Then the plan should include the connect intent
And I should receive SSH connection information
```

**Scenario: Team Onboarding - Get Connection Help**

```
Given I am new to the team
When I ask how to connect to Python
Then I should receive clear connection instructions
And I should understand how to access the VM
```

**Scenario: Detect connect intent**

```
When I parse "how do I connect to python"
Then intent should be "connect"
And VMs should include "python"
```

**Scenario: Connect to PostgreSQL from Python VM**

```
Given "postgres" VM is running
And "python" VM is running
When I SSH into "python-dev"
And I run "psql -h postgres -U devuser"
Then I should be connected to PostgreSQL
And I can query the database
And the connection uses the container network
```

**Scenario: Ask how to connect to a VM**

```
Given I want to SSH into my VM
When I ask "how do I connect to python?"
Then I should see the SSH command
And I should see the port number
And I should see VSCode Remote-SSH instructions
```

**Scenario: Getting connection information for a VM**

```
Given I have a Python VM running
When I ask "how do I connect to Python?"
Then I should receive SSH connection details
And the details should include the hostname
And the details should include the port number
And the details should include the username
```

---

## 8. Working with Databases

**Scenario: Example 1 - Create PostgreSQL for Python API**

```
Given I have planned to create Python
When I plan to create PostgreSQL
Then the plan should include the create_vm intent
And the plan should include the PostgreSQL VM
```

**Scenario: Example 1 - Start Both Python and PostgreSQL**

```
Given I have created Python and PostgreSQL VMs
When I plan to start both VMs
Then the plan should include the start_vm intent
And the plan should include both Python and PostgreSQL VMs
```

**Scenario: Example 2 - Full-Stack JavaScript with Redis**

```
Given I am following the documented JavaScript workflow
When I plan to create JavaScript and Redis VMs
Then the plan should include both VMs
And the JavaScript VM should use the js canonical name
```

**Scenario: Adding Cache Layer - Create Redis**

```
Given I have an existing Python and PostgreSQL stack
When I plan to add Redis
Then the plan should include the create_vm intent
And the Redis VM should be included
```

**Scenario: Adding Cache Layer - Start Redis**

```
Given I have created the Redis VM
When I plan to start Redis
Then the plan should include the start_vm intent
And Redis should start without affecting other VMs
```

**Scenario: Collaborate with shared PostgreSQL service**

```
Given the team uses PostgreSQL for development
And postgres VM configuration is in the repository
When each team member starts "postgres" VM
Then each developer gets their own isolated PostgreSQL instance
And data persists in each developer's local data/postgres/
And developers don't interfere with each other's databases
```

**Scenario: Create test environment with database**

```
Given I need to test my application with a real database
When I create "postgres" and "redis" service VMs
And I create my language VM (e.g., "python")
And I start all three VMs
Then my application can connect to test database
And test data is isolated from development data
And I can stop test VMs independently
```

**Scenario: Share a single PostgreSQL across projects**

```
Given I have multiple projects using PostgreSQL
When I start one postgres VM
And I start multiple language VMs
Then all language VMs can connect to the same postgres
And I don't need separate databases for each project
```

**Scenario: Develop with database like in production**

```
Given production uses PostgreSQL with specific extensions
When I configure the postgres VM with those extensions
Then my local database matches production
And I catch compatibility issues early
```

**Scenario: Development database with seed data**

```
Given I need realistic data for development
When I create a seed script and run it in postgres VM
Then the data persists across VM restarts
And I always have a fresh starting point
And I can reset data when needed
```

**Scenario: Database migrations across environments**

```
Given I have migration scripts
When I run migrations in development VM
Then I can test migrations safely
And I can verify schema changes work
And production database is not affected
```

**Scenario: Database backups and restores**

```
Given I have important data in postgres VM
When I create a backup of data/postgres/
Then I can restore from backup later
And I can migrate data to another machine
And my work is safely backed up
```

---

## 9. Daily Workflow: Starting Your Day

**Scenario: Setting up a web development project**

```
Given I am starting a new web project
When I request to "create JavaScript and nginx"
Then the JavaScript VM should be created
And the nginx VM should be created
And both should be configured for web development
```

**Scenario: Switching from web to backend project**

```
Given I have web containers running (JavaScript, nginx)
When I request to "stop all and start python and postgres"
Then the web containers should be stopped
And the Python VM should start
And the PostgreSQL VM should start
And only the backend stack should be running
```

**Scenario: Setting up a microservices architecture**

```
Given I am building a microservices application
When I request to "create Go, Rust, and nginx"
Then the Go VM should be created for one service
And the Rust VM should be created for another service
And the nginx VM should be created as a gateway
```

**Scenario: Starting all microservices at once**

```
Given I have created my microservice VMs
When I request to "start all services"
Then all service VMs should start
And they should be able to communicate on the Docker network
And each should have its own SSH port
```

**Scenario: Full stack web application**

```
Given I need a complete web stack
When I request to "create Python, PostgreSQL, Redis, and nginx"
Then the Python VM should be for the backend API
And PostgreSQL should be for the database
And Redis should be for caching
And nginx should be for the web server
And all should be on the same network
```

**Scenario: Mobile development with backend**

```
Given I am developing a mobile app with backend
When I request to "start flutter and postgres"
Then the Flutter VM should start for mobile development
And PostgreSQL should start for the backend database
And both should be accessible via SSH
```

**Scenario: Cleaning up between projects**

```
Given I have finished working on one project
When I request to "stop everything"
Then all containers should stop
And I can start a fresh environment for another project
And there should be no leftover processes
```

**Scenario: Example 2 - Resolve Node.js Alias**

```
Given I want to use the Node.js name
When I resolve the nodejs alias
Then it should resolve to js
And I can use either name in commands
```

**Scenario: Example 3 - Start All Microservice VMs**

```
Given I have created the microservice VMs
When I plan to start them all
Then the plan should include the start_vm intent
And all microservice VMs should be included
```

**Scenario: Daily Workflow - Evening Cleanup**

```
Given I am done with development for the day
When I plan to stop everything
Then the plan should include the stop_vm intent
And the plan should apply to all running VMs
```

**Scenario: Troubleshooting - Step 3 Restart with Rebuild**

```
Given I need to rebuild a VM to fix an issue
When I plan to rebuild Python
Then the plan should include the restart_vm intent
And the plan should set rebuild=true flag
```

**Scenario: Switching Projects - Stop Current Project**

```
Given I am working on one project
When I plan to stop all VMs
Then all running VMs should be stopped
And I should be ready to start a new project
```

**Scenario: Switching Projects - Start New Project**

```
Given I have stopped my current project
When I plan to start Go and MongoDB
Then the new project VMs should start
And only the new project VMs should be running
```

**Scenario: Team Onboarding - Explore Languages**

```
Given I am a new team member
When I ask to list all languages
Then I should see only language VMs
And service VMs should not be included
```

**Scenario: Team Onboarding - Understand System**

```
Given I am learning the VDE system
When I ask for help
Then I should see available commands
And I should understand what I can do
```

**Scenario: Starting Already Running VM**

```
Given I have a Python VM that is already running
When I plan to start Python
Then the plan should be generated
And execution would detect the VM is already running
And I would be notified that it's already running
```

**Scenario: Stopping Already Stopped VM**

```
Given I have a stopped PostgreSQL VM
When I plan to stop PostgreSQL
Then the plan should be generated
And execution would detect the VM is not running
And I would be notified that it's already stopped
```

**Scenario: Creating Existing VM**

```
Given I already have a Go VM configured
When I plan to create Go again
Then the plan should be generated
And execution would detect the VM already exists
And I would be notified of the existing VM
```

**Scenario: Performance - Quick Plan Generation**

```
Given I need to plan my daily workflow
When I generate plans for morning setup, checks, and cleanup
Then all plans should be generated quickly
And the total time should be under 500ms
```

**Scenario: Start my daily development VMs**

```
Given I previously created VMs for "python", "rust", and "postgres"
When I run "start-virtual python rust postgres"
Then all three VMs should be running
And I should be able to SSH to "python-dev" on allocated port
And I should be able to SSH to "rust-dev" on allocated port
And PostgreSQL should be accessible from language VMs
```

**Scenario: Create a new language VM for a project**

```
Given I need to start a "golang" project
```

**Scenario: Switch from Python to Rust project**

```
Given I have "python" VM running
And I have "rust" VM created but not running
When I want to work on a Rust project instead
And I run "start-virtual rust"
Then both "python" and "rust" VMs should be running
And I can SSH to both VMs from my terminal
And each VM has isolated project directories
```

**Scenario: Shut down all VMs at end of day**

```
Given multiple VMs are running
When I run "shutdown-virtual all"
Then all VMs should be stopped
```

**Scenario: Run multiple language VMs for a polyglot project**

```
Given I have a project using Python, JavaScript, and Redis
When I run "start-virtual python js redis"
Then all three VMs should be running
And Python VM can make HTTP requests to JavaScript VM
And Python VM can connect to Redis
And each VM can access shared project directories
```

**Scenario: Rebuild a VM after modifying its Dockerfile**

```
Given I have modified the python Dockerfile to add a new package
And "python" VM is currently running
When I run "start-virtual python --rebuild"
Then the VM should be rebuilt with the new Dockerfile
And the VM should be running after rebuild
And the new package should be available in the VM
```

**Scenario: Remove VM I no longer need**

```
Given I have an old "ruby" VM I don't use anymore
When I run the removal process for "ruby"
Then the docker-compose.yml should be deleted
And SSH config entry should be removed
```

**Scenario: Add support for a new language**

```
Given VDE doesn't support "zig" yet
When I run "add-vm-type --type lang --display 'Zig' zig 'apt-get install -y zig'"
Then "zig" should be available as a VM type
And I can create a zig VM with "create-virtual-for zig"
And zig should appear in "list-vms" output
```

**Scenario: Check what VMs I can create**

```
Given I want to see what development environments are available
When I run "list-vms"
Then all language VMs should be listed with aliases
And all service VMs should be listed with ports
And I can see which VMs are created vs just available
```

**Scenario: Quickly check what's running**

```
Given I have several VMs configured
When I run "list-vms --created"
Then I should see only VMs that have been created
And their status (running/stopped) should be shown
And I can identify which VMs to start or stop
```

**Scenario: VDE handles port conflicts gracefully**

```
Given a system service is using port 2200
When I create a new language VM
Then VDE should allocate the next available port (2201)
And the VM should work correctly on the new port
And SSH config should reflect the correct port
```

**Scenario: Starting my development environment**

```
Given I have VDE installed
When I request to start my Python development environment
Then the Python VM should be started
And SSH access should be available on the configured port
And my workspace directory should be mounted
```

**Scenario: Checking what's currently running**

```
Given I have several VMs running
When I ask "what's running?"
Then I should see a list of all running VMs
And each VM should show its status
And the list should include both language and service VMs
```

**Scenario: Stopping work for the day**

```
Given I have multiple VMs running
When I request to "stop everything"
Then all running VMs should be stopped
And no containers should be left running
And the operation should complete without errors
```

**Scenario: Restarting a VM with rebuild**

```
Given I have a Python VM running
When I request to "restart python with rebuild"
Then the Python VM should be stopped
And the container should be rebuilt from the Dockerfile
And the Python VM should be started again
And my workspace should still be mounted
```

**Scenario: Starting multiple VMs at once**

```
Given I need a full stack environment
When I request to "start python and postgres"
Then both Python and PostgreSQL VMs should start
And they should be on the same Docker network
And they should be able to communicate
```

**Scenario: Creating a new VM for the first time**

```
Given I want to try a new language
When I request to "create a Go VM"
Then the Go VM configuration should be created
And the Docker image should be built
And SSH keys should be configured
And the VM should be ready to start
```

**Scenario: Automated testing workflow**

```
Given I have a comprehensive test suite
When I push code changes
Then CI runs tests in similar VMs
And local test results match CI results
And I catch issues before pushing
```

---

## 10. Adding More Languages

**Scenario: Understanding VM categories**

```
Given I am new to VDE
When I explore available VMs
Then I should understand the difference between language and service VMs
And language VMs should have SSH access
And service VMs should provide infrastructure services
```

---

## 11. Troubleshooting: When Things Go Wrong

**Scenario: Error when all ports in range are allocated**

```
Given all ports from "2200" to "2299" are allocated
When I create a new language VM
Then the command should fail with error "No available ports"
```

**Scenario: Rebuild requests**

```
Given I need to rebuild a container
When I say "rebuild python from scratch"
Then the rebuild flag should be set
And no cache should be used
```

**Scenario: Troubleshooting language**

```
Given something isn't working
When I say "restart the database"
Then PostgreSQL should restart
And the system should understand "database" means "postgres"
```

**Scenario: Diagnose why VM won't start**

```
Given I tried to start a VM but it failed
When I check the VM status
Then I should see a clear error message
And I should know if it's a port conflict, Docker issue, or configuration problem
```

**Scenario: View VM logs for debugging**

```
Given a VM is running but misbehaving
When I run "docker logs <vm-name>"
Then I should see the container logs
And I can identify the source of the problem
```

**Scenario: Access VM shell for debugging**

```
Given a VM is running
When I run "docker exec -it <vm-name> /bin/zsh"
Then I should have shell access inside the container
And I can investigate issues directly
```

**Scenario: Rebuild VM from scratch after corruption**

```
Given a VM seems corrupted or misconfigured
When I stop the VM
And I remove the VM directory
And I recreate the VM
Then I should get a fresh VM
And old configuration issues should be resolved
```

**Scenario: Check if port is already in use**

```
Given I get a "port already allocated" error
When I check what's using the port
Then I should see which process is using it
And I can decide to stop the conflicting process
And VDE can allocate a different port
```

**Scenario: Inspect docker-compose configuration**

```
Given I need to verify VM configuration
When I look at the docker-compose.yml
Then I should see all volume mounts
And I should see all port mappings
And I should see environment variables
And I can verify the configuration is correct
```

**Scenario: Clear Docker cache to fix build issues**

```
Given a VM build keeps failing
When I rebuild with --no-cache
Then Docker should pull fresh images
And build should not use cached layers
```

**Scenario: Reset a VM to initial state**

```
Given I've made changes I want to discard
When I stop the VM
And I remove the container but keep the config
And I start it again
Then I should get a fresh container
And my code volumes should be preserved
```

**Scenario: Check VM resource usage**

```
Given a VM seems slow
When I run "docker stats <vm-name>"
Then I can see CPU and memory usage
And I can identify resource bottlenecks
```

**Scenario: Validate VM configuration before starting**

```
Given I think my docker-compose.yml might have errors
When I run "docker-compose config"
Then I should see any syntax errors
And the configuration should be validated
```

**Scenario: Recover from Docker daemon issues**

```
Given VMs won't start due to Docker problems
When I check Docker is running
And I restart Docker if needed
Then VMs should start normally after Docker is healthy
```

**Scenario: Fix permission issues on shared volumes**

```
Given I get permission denied errors in VM
When I check the UID/GID configuration
Then I should see if devuser (1000:1000) matches my host user
And I can adjust if needed
```

**Scenario: Diagnose why tests fail in VM but pass locally**

```
Given tests work on host but fail in VM
When I compare the environments
Then I can check for missing dependencies
And I can verify environment variables match
And I can check network access from the VM
```

**Scenario: Rebuild port registry from compose files**

```
Given port registry cache is missing or invalid
When port registry is verified
Then registry should be rebuilt by scanning docker-compose files
And all allocated ports should be discovered
```

**Scenario: Rebuild with --build flag**

```
Given VM "python" is running
When I start VM "python" with --rebuild
Then docker-compose up --build should be executed
And image should be rebuilt
```

**Scenario: Rebuild without cache with --no-cache flag**

```
Given VM "python" is running
When I start VM "python" with --rebuild and --no-cache
Then docker-compose up --build --no-cache should be executed
```

**Scenario: Handle port allocation errors**

```
Given all ports in range are in use
When I create a new VM
Then error should indicate "No available ports"
And VM should not be created
```

**Scenario: Handle network errors**

```
Given vde-network does not exist
When I start a VM
Then network should be created automatically
And error should indicate network issue
```

**Scenario: Parse Docker error messages**

```
Given docker-compose operation fails
When stderr is parsed
Then "port is already allocated" should map to port conflict error
And "network.*not found" should map to network error
And "permission denied" should map to permission error
```

**Scenario: Handle disk space errors**

```
Given no disk space is available
When I try to start a VM
Then error should indicate "no space left on device"
And command should fail immediately
```

**Scenario: Collaborative debugging with matching environments**

```
Given a developer cannot reproduce a bug
When another developer shares their exact VM configuration
And the first developer recreates the VM
Then both developers have identical environments
And the bug becomes reproducible
And debugging becomes more effective
```

**Scenario: Detect rebuild VM intent**

```
When I parse "rebuild and start rust"
Then intent should be "restart_vm"
And rebuild flag should be true
```

**Scenario: Detect rebuild without cache intent**

```
When I parse "rebuild python with no cache"
Then intent should be "restart_vm"
And rebuild flag should be true
And nocache flag should be true
```

**Scenario: Debug configuration issues**

```
Given my VM won't start due to configuration
When I check docker-compose config
Then I should see the effective configuration
And errors should be clearly indicated
And I can identify the problematic setting
```

**Scenario: Rebuilding after system updates**

```
Given I have updated my system Docker
When I request to "rebuild python with no cache"
Then the Python container should be rebuilt from scratch
And no cached layers should be used
And the rebuild should use the latest base images
```

**Scenario: Troubleshooting a problematic VM**

```
Given a VM is not working correctly
When I request to "restart postgres with rebuild"
Then the PostgreSQL VM should be completely rebuilt
And my data should be preserved (if using volumes)
And the VM should start with a fresh configuration
```

**Scenario: Recovering from errors**

```
Given a VM has crashed
When I request to "restart the VM"
Then the VM should be stopped if running
And the VM should be started again
And the restart should attempt to recover the state
```

**Scenario: Invalid VM name handling**

```
Given I try to use a VM that doesn't exist
When I request to "start nonexistent-vm"
Then I should receive a clear error message
And the error should explain what went wrong
And suggest valid VM names
```

**Scenario: Port conflict resolution**

```
Given a port is already in use
When I try to start a VM
Then VDE should detect the conflict
And allocate an available port
And continue with the operation
```

**Scenario: Docker daemon not running**

```
Given Docker is not available
When I try to start a VM
Then I should receive a helpful error
And the error should explain Docker is required
And suggest how to fix it
```

**Scenario: Insufficient disk space**

```
Given my disk is nearly full
When I try to create a VM
Then VDE should detect the issue
And warn me before starting
And suggest cleaning up
```

**Scenario: Network creation failure**

```
Given the Docker network can't be created
When I start a VM
Then VDE should report the specific error
And suggest troubleshooting steps
And offer to retry
```

**Scenario: Build failure recovery**

```
Given a VM build fails
When I examine the error
Then I should see what went wrong
And get suggestions for fixing it
And be able to retry after fixing
```

**Scenario: Container startup timeout**

```
Given a container takes too long to start
When VDE detects the timeout
Then it should report the issue
And show the container logs
And offer to check the status
```

**Scenario: Permission denied errors**

```
Given I don't have permission for an operation
When VDE encounters the error
Then it should explain the permission issue
And suggest how to fix it
And offer to retry with proper permissions
```

**Scenario: Configuration file errors**

```
Given a docker-compose.yml is malformed
When I try to use the VM
Then VDE should detect the error
And show the specific problem
And suggest how to fix the configuration
```

**Scenario: Graceful degradation**

```
Given one VM fails to start
When I start multiple VMs
Then other VMs should continue
And I should be notified of the failure
And successful VMs should be listed
```

**Scenario: Automatic retry logic**

```
Given a transient error occurs
When VDE detects it's retryable
Then it should automatically retry
And limit the number of retries
And report if all retries fail
```

**Scenario: Partial state recovery**

```
Given an operation is interrupted
When I try again
Then VDE should detect partial state
And complete the operation
And not duplicate work
```

**Scenario: Clear error messages**

```
Given any error occurs
When the error is displayed
Then it should be in plain language
And explain what went wrong
And suggest next steps
```

**Scenario: Error logging**

```
Given an error occurs
When VDE handles it
Then the error should be logged
And the error should have sufficient detail for debugging
And I can find it in the logs directory
```

**Scenario: Rollback on failure**

```
Given an operation fails partway through
When the failure is detected
Then VDE should clean up partial state
And return to a consistent state
And allow me to retry cleanly
```

**Scenario: AI handles errors gracefully**

```
Given something goes wrong
When I ask the AI to fix it
Then the AI should diagnose the problem
And suggest solutions
And offer to implement the fix
```

**Scenario: Rebuild VM with natural language**

```
Given I've modified a Dockerfile
When I say "rebuild and start python"
Then python VM should be rebuilt and started
And I should not need to remember --rebuild flag
```

**Scenario: Debugging host issues from VM**

```
Given I have a debugging VM running
And my host has an issue I need to diagnose
When I SSH into the debugging VM
And I run "to-host systemctl status docker"
Then I should see the Docker service status
And I can diagnose the issue
```

**Scenario: Debug across multiple services**

```
Given I have a web app (python), database (postgres), and cache (redis)
When I need to debug an issue
Then I can SSH into each service independently
And I can check logs for each service
And I can trace requests across services
```

**Scenario: Log aggregation for debugging**

```
Given multiple VMs generate logs
When I check logs for each VM
Then I can view logs from docker logs command
And I can check logs/<vm>/ directories
And I can trace issues across services
```

**Scenario: File watching and rebuilds**

```
Given I'm compiling code inside VM
When source files change on host
Then the VM sees the changes immediately
And my build tool can rebuild automatically
And I don't need to manually trigger builds
```

---

## Quick Reference Card

### Essential Commands

```bash
# See what VMs are available
./scripts/list-vms

# Create a new VM
./scripts/create-virtual-for <name>

# Start VMs
./scripts/start-virtual <vm1> <vm2> ...

# Stop VMs
./scripts/shutdown-virtual <vm1> <vm2> ...

# Stop everything
./scripts/shutdown-virtual all

# Rebuild a VM
./scripts/start-virtual <vm> --rebuild
```

### SSH Connections

```bash
# Language VMs
ssh python-dev     # Python development
ssh rust-dev       # Rust development
ssh js-dev         # JavaScript/Node.js
ssh csharp-dev     # C# development
ssh ruby-dev       # Ruby development
ssh go-dev         # Go development

# Service VMs
ssh postgres       # PostgreSQL database
ssh redis          # Redis cache
ssh mongodb        # MongoDB
ssh nginx          # Nginx web server
```

### Default Ports

| VM | Port |
|----|------|
| python-dev | 2200 |
| rust-dev | 2201 |
| js-dev | 2202 |
| csharp-dev | 2203 |
| ruby-dev | 2204 |
| postgres | 2400 |
| redis | 2401 |
| mongodb | 2402 |
| nginx | 2403 |

---

## Available VM Types

### Language VMs (for writing code)

| Language | Command | Aliases | Best For |
|----------|---------|---------|---------|
| Python | `create-virtual-for python` | py | Web backends, AI/ML, scripts |
| Rust | `create-virtual-for rust` | rust-dev | Systems, performance |
| JavaScript | `create-virtual-for js` | js, node | Web frontends, Node.js |
| C# | `create-virtual-for csharp` | csharp | .NET development |
| Ruby | `create-virtual-for ruby` | rb | Rails, scripts |
| Go | `create-virtual-for go` | golang | Services, microservices |

### Service VMs (for data & infrastructure)

| Service | Command | Port | Best For |
|---------|---------|------|----------|
| PostgreSQL | `create-virtual-for postgres` | 5432 | Relational databases |
| Redis | `create-virtual-for redis` | 6379 | Caching, queues |
| MongoDB | `create-virtual-for mongodb` | 27017 | NoSQL databases |
| Nginx | `create-virtual-for nginx` | 80/443 | Web server, reverse proxy |

---

## You're Ready!

**You now have:**
- ✅ VDE installed and configured
- ✅ SSH keys set up automatically
- ✅ Your first VM created
- ✅ Understanding of starting/stopping
- ✅ A full cluster (Python + PostgreSQL + Redis)
- ✅ Knowledge of how to troubleshoot

**Next steps:**
1. Create your first project in `projects/python/`
2. Start coding!
3. Add more languages as you need them
4. Use the AI assistant for natural language control

---

*This guide is generated from BDD test scenarios. Every workflow shown here has been tested and verified to work. If you follow these steps, they will work for you.*
