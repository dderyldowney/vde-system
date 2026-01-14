# VDE User's Guide

> **This guide is generated from working BDD test scenarios.** Every workflow below has been tested and verified to work. If you follow these steps, they will work for you too.

---

## Table of Contents

1. [1. Installation](#1.-installation)
2. [2. SSH Keys](#2.-ssh-keys)
3. [3. Your First VM](#3.-your-first-vm)
4. [4. Understanding](#4.-understanding)
5. [5. Starting and Stopping](#5.-starting-and-stopping)
6. [6. Your First Cluster](#6.-your-first-cluster)
7. [7. Connecting](#7.-connecting)
8. [8. Working with Databases](#8.-working-with-databases)
9. [9. Daily Workflow](#9.-daily-workflow)
10. [10. Adding More Languages](#10.-adding-more-languages)
11. [11. Troubleshooting](#11.-troubleshooting)

---

## 1. Installation

This is the part everyone finds confusing. Let's break it down.

### What You Need Before Starting

**What you need:**
- [ ] Docker Desktop installed and running
- [ ] Git installed (for cloning the repo)
- [ ] About 5GB of free disk space

### Step 1: Clone VDE to Your Computer

**Open your terminal and run:**
```bash
# Clone the repository
git clone <repo-url> ~/dev

# Go into the directory
cd ~/dev
```

### Step 2: Verify Installation

**Verify everything is ready:**
```bash
./scripts/list-vms
```

**Expected output:** You should see a list of available language and service VMs.

**Scenario: Create a new language vm**

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
**Scenario: Allocate first available port for language vm**

```
Given no language VMs are created
When I create a language VM
Then the VM should be allocated port "2200"
```
**Scenario: Natural language variations**

```
Given I can phrase commands in different ways
When I say "launch the golang container"
Then it should be equivalent to "start go"
And the Go VM should start
```
**Scenario: Complex natural language queries**

```
Given I use conversational language
When I say "I need to set up a backend with Python and PostgreSQL"
Then the system should understand I want to create VMs
And Python and PostgreSQL should be created
```
**Scenario: Troubleshooting language**

```
Given something isn't working
When I say "restart the database"
Then PostgreSQL should restart
And the system should understand "database" means "postgres"
```
---

## 2. SSH Keys

This is automatic, but you should understand what's happening.

### Automatic SSH Key Generation

**What happens:**
1. VDE checks if you have SSH keys (~/.ssh/id_ed25519)
2. If not, it creates them for you automatically
3. Public keys are copied to the `public-ssh-keys/` directory
4. VMs are configured to use these keys for access

### Your SSH Config is Updated Automatically

**You don't need to:**
- Manually create SSH keys
- Edit your SSH config file
- Copy keys to VMs
- Set up SSH agent forwarding

**VDE does all of this for you.**

**Scenario: Automatically start ssh agent if not running**

```
Given SSH agent is not running
And SSH keys exist in ~/.ssh/
When I run any VDE command that requires SSH
Then SSH agent should be started
And available SSH keys should be loaded into agent
```
**Scenario: Generate ssh key if none exists**

```
Given no SSH keys exist in ~/.ssh/
When I run any VDE command that requires SSH
Then an ed25519 SSH key should be generated
And the public key should be synced to public-ssh-keys directory
```
**Scenario: Create ssh config entry for new vm**

```
Given VM "python" is created with SSH port "2200"
When SSH config is generated
Then SSH config should contain "Host python-dev"
And SSH config should contain "Port 2200"
And SSH config should contain "ForwardAgent yes"
```
**Scenario: Ssh config uses correct identity file**

```
Given primary SSH key is "id_ed25519"
When SSH config entry is created for VM "python"
Then SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"
```
**Scenario: Generate vm to vm ssh config entries**

```
Given VM "python" is allocated port "2200"
And VM "rust" is allocated port "2201"
When VM-to-VM SSH config is generated
Then SSH config should contain entry for "python-dev"
And SSH config should contain entry for "rust-dev"
And each entry should use "localhost" as hostname
```
---

## 3. Your First VM

Let's create your first development environment. We'll start with Python because it's the most common language for beginners.

### Creating Your Python VM

**Run this command:**
```bash
./scripts/create-virtual-for python
```

**What you'll see:**
- Progress messages as Docker builds the image
- "SSH config entry created" message
- "Your Python VM is ready" message

### Starting Your First VM

**Run this command:**
```bash
./scripts/start-virtual python
```

**What happens:**
- Docker container starts
- SSH port 2200 is allocated
- Your projects/python directory is mounted
- You're ready to code!

**Scenario: Detect create vm intent**

```
When I parse "create a go vm"
Then intent should be "create_vm"
And VMs should include "go"
```
**Scenario: Create vm with natural language**

```
Given I want a go development environment
When I say "create a go vm"
Then go VM should be created
And I should not need to remember create-virtual-for syntax
```
---

## 4. Understanding

Let's verify everything works and understand the pieces.

### Check That Your VM is Running

**Check status:**
```bash
./scripts/list-vms
```

**You should see:**
- python: **running** (on port 2200)

### Understanding Your Directory Structure

**Your directory structure:**
```
~/dev/
├── configs/          # VM configurations
├── projects/         # YOUR CODE GOES HERE
│   └── python/       # Python projects (mounted in VM)
├── data/            # Database data (persists across rebuilds)
├── logs/            # Application logs
└── scripts/         # VDE management commands
```

**Scenario: List all predefined vm types**

```
Given VM types are loaded
When I run "list-vms"
Then all language VMs should be listed
And all service VMs should be listed
And aliases should be shown
```
**Scenario: List only language vms**

```
Given VM types are loaded
When I run "list-vms --lang"
Then only language VMs should be listed
And service VMs should not be listed
```
**Scenario: List only service vms**

```
Given VM types are loaded
When I run "list-vms --svc"
Then only service VMs should be listed
And language VMs should not be listed
```
**Scenario: Verify ssh connection is working**

```
Given I cannot SSH into a VM
When I check the SSH config
And I verify the VM is running
And I verify the port is correct
Then I can identify if the issue is SSH, Docker, or the VM itself
```
**Scenario: Verify volumes are mounted correctly**

```
Given my code changes aren't reflected in the VM
When I check the mounts in the container
Then I can see if the volume is properly mounted
And I can verify the host path is correct
```
---

## 5. Starting and Stopping

Daily workflow: starting when you work, stopping when done.

### Starting Your VM

**Command:**
```bash
./scripts/start-virtual python
```

### Stopping Your VM

**Command:**
```bash
./scripts/shutdown-virtual python
```

**Important:** Stopping doesn't delete your VM - it just stops the container. Your code and configurations are safe.

**Scenario: Start a created vm**

```
Given VM "python" has been created
And VM "python" is not running
When I run "start-virtual python"
Then VM "python" should be running
And SSH should be accessible on allocated port
```
**Scenario: Start multiple vms**

```
Given VM "python" has been created
And VM "rust" has been created
And neither VM is running
When I run "start-virtual python rust"
Then VM "python" should be running
And VM "rust" should be running
And each VM should have a unique SSH port
```
**Scenario: Start all vms**

```
Given VM "python" has been created
And VM "rust" has been created
And VM "postgres" has been created
And none of the VMs are running
When I run "start-virtual all"
Then all created VMs should be running
```
**Scenario: Stop a running vm**

```
Given VM "python" is running
When I run "shutdown-virtual python"
Then VM "python" should not be running
```
**Scenario: Stop all running vms**

```
Given VM "python" is running
And VM "rust" is running
When I run "shutdown-virtual all"
Then no VMs should be running
```
---

## 6. Your First Cluster

Now let's build a real application stack. This is where VDE shines.

### Understanding What We're Building

You'll have:
- **Python VM** - Your application code (port 2200)
- **PostgreSQL VM** - Your database (port 2400)
- **Redis VM** - Your cache (port 2401)

All three can talk to each other automatically.

### Creating Your Service VMs

**Create both services:**
```bash
./scripts/create-virtual-for postgres
./scripts/create-virtual-for redis
```

### Starting Your Full Stack

**Start your full stack:**
```bash
./scripts/start-virtual python postgres redis
```

### Verifying Your Cluster is Running

**Check status:**
```bash
./scripts/list-vms
```

**Expected output:**
```
VM          Type        Status    Port
----------------------------------------
python      language    running   2200
postgres    service     running   2400
redis       service     running   2401
```

**Scenario: Allocate sequential ports for multiple language vms**

```
Given language VM "python" is allocated port "2200"
When I create language VM "rust"
Then "rust" should be allocated port "2201"
```
**Scenario: Multiple vms in one command**

```
Given I need to work with multiple environments
When I say "start python and postgres"
Then both VMs should start
And the command should work the same as "start python, postgres"
```
**Scenario: Prefer ed25519 keys when multiple exist**

```
Given both "id_ed25519" and "id_rsa" keys exist
When primary SSH key is requested
Then "id_ed25519" should be returned as primary key
```
**Scenario: Creating multiple vms at once**

```
Given I need a full stack environment
When I request to "create Python, PostgreSQL, and Redis"
Then all three VMs should be created
And each should have its own configuration
And all should be on the same Docker network
```
**Scenario: Multi stage build optimization**

```
Given I rebuild a language VM
Then the build should use multi-stage Dockerfile
And final images should be smaller
And build cache should be used when possible
```
---

## 7. Connecting

### Connecting to Your Python VM

**Connect:**
```bash
ssh python-dev
```

**You're now inside your VM!** You can:
- Run Python code
- Install packages
- Edit files in projects/python/
- Access postgres and redis

### Exiting a VM

**To exit:** Just type `exit` or press `Ctrl+D`

### Connection Reference

| VM Name | SSH Command | What It's For |
|---------|-------------|---------------|
| python-dev | `ssh python-dev` | Python development |
| rust-dev | `ssh rust-dev` | Rust development |
| js-dev | `ssh js-dev` | JavaScript/Node.js |
| postgres | `ssh postgres` | Direct database access |
| redis | `ssh redis` | Direct Redis access |

**Scenario: Connection help requests**

```
Given I need to connect to a VM
When I ask "how do I connect to the Python environment?"
Then I should receive SSH connection instructions
And the instructions should be clear and actionable
```
**Scenario: Test database connectivity from vm**

```
Given my application can't connect to the database
When I SSH into the application VM
And I try to connect to the database VM directly
Then I can see if the issue is network, credentials, or database state
```
**Scenario: Example 1   get connection info for python**

```
Given I need to connect to the Python VM
When I ask for connection information
Then the plan should include the connect intent
And the plan should include the Python VM
```
**Scenario: Daily workflow   connect to primary vm**

```
Given I need to work in my primary development environment
When I ask how to connect to Python
Then the plan should provide connection details
And the plan should include the Python VM
```
**Scenario: Troubleshooting   step 4 get connection info**

```
Given I need to debug inside a container
When I ask to connect to Python
Then the plan should include the connect intent
And I should receive SSH connection information
```
---

## 8. Working with Databases

### Connecting to PostgreSQL from Your Python VM

**Try it yourself:**
```bash
# 1. Connect to your Python VM
ssh python-dev

# 2. Connect to PostgreSQL from within the VM
psql -h postgres -U devuser

# 3. You're now in PostgreSQL! Try:
# \list                    # List databases
# \c devuser               # Connect to default database
# \dt                      # List tables
# SELECT 1;                # Run a query
# \q                       # Quit
```

### Your Database Data Persists

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your data is safe.

**Scenario: Example 1   create postgresql for python api**

```
Given I have planned to create Python
When I plan to create PostgreSQL
Then the plan should include the create_vm intent
And the plan should include the PostgreSQL VM
```
**Scenario: Example 2   full stack javascript with redis**

```
Given I am following the documented JavaScript workflow
When I plan to create JavaScript and Redis VMs
Then the plan should include both VMs
And the JavaScript VM should use the js canonical name
```
**Scenario: Adding cache layer   create redis**

```
Given I have an existing Python and PostgreSQL stack
When I plan to add Redis
Then the plan should include the create_vm intent
And the Redis VM should be included
```
**Scenario: Collaborate with shared postgresql service**

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
---

## 9. Daily Workflow

### Morning Routine: Start Your Development Environment

**One command to start your day:**
```bash
./scripts/start-virtual python postgres redis
```

### During the Day: Check What's Running

**Check status:**
```bash
./scripts/list-vms
```

### End of Day: Stop Everything

**Stop everything:**
```bash
./scripts/shutdown-virtual all
```

**Scenario: Daily workflow   evening cleanup**

```
Given I am done with development for the day
When I plan to stop everything
Then the plan should include the stop_vm intent
And the plan should apply to all running VMs
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
**Scenario: Vm to vm ssh in development workflow**

```
Given I am developing a full-stack application
And I have frontend, backend, and database VMs
When I need to test the backend from the frontend VM
And I run "ssh backend-dev pytest tests/"
Then the tests should run on the backend VM
And I should see the results in the frontend VM
And authentication should be automatic
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

### Creating a Second Language VM

**Add Rust:**
```bash
./scripts/create-virtual-for rust
./scripts/start-virtual rust
```

### Starting Multiple Language VMs

**Start multiple at once:**
```bash
./scripts/start-virtual python rust js
```

**Scenario: Create a new language vm**

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
**Scenario: Allocate first available port for language vm**

```
Given no language VMs are created
When I create a language VM
Then the VM should be allocated port "2200"
```
**Scenario: Natural language variations**

```
Given I can phrase commands in different ways
When I say "launch the golang container"
Then it should be equivalent to "start go"
And the Go VM should start
```
**Scenario: Complex natural language queries**

```
Given I use conversational language
When I say "I need to set up a backend with Python and PostgreSQL"
Then the system should understand I want to create VMs
And Python and PostgreSQL should be created
```
**Scenario: Troubleshooting language**

```
Given something isn't working
When I say "restart the database"
Then PostgreSQL should restart
And the system should understand "database" means "postgres"
```
---

## 11. Troubleshooting

### Problem: A VM Won't Start

**What to check:**
1. Is Docker running? `docker ps`
2. Is the port already in use? `./scripts/list-vms`
3. Check the logs: `docker logs <vm-name>`

### Problem: Changes Aren't Reflected

**Rebuild with --rebuild:**
```bash
./scripts/start-virtual python --rebuild
```

**For complete rebuild (no cache):**
```bash
./scripts/start-virtual python --rebuild --no-cache
```

**Scenario: Rebuild a vm with   rebuild flag**

```
Given VM "python" is running
When I run "start-virtual python --rebuild"
Then VM "python" should be running
And the container should be rebuilt from the Dockerfile
```
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
**Scenario: View vm logs for debugging**

```
Given a VM is running but misbehaving
When I run "docker logs <vm-name>"
Then I should see the container logs
And I can identify the source of the problem
```
**Scenario: Access vm shell for debugging**

```
Given a VM is running
When I run "docker exec -it <vm-name> /bin/zsh"
Then I should have shell access inside the container
And I can investigate issues directly
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

---

*This guide is generated from BDD test scenarios. Every workflow shown here has been tested and verified to work. If you follow these steps, they will work for you.*
