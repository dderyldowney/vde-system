# VDE AI Assistant - Complete User Guide

A friendly, comprehensive guide to using the VDE (Virtual Development Environment) AI Assistant to manage your development containers using everyday language.

[← Back to README](../README.md)

---

## Table of Contents

1. [Welcome to VDE AI](#welcome-to-vde-ai)
2. [Getting Started](#getting-started)
3. [Understanding the Basics](#understanding-the-basics)
4. [Setting Up API Keys (Optional)](#setting-up-api-keys-optional)
5. [Using VDE AI - Quick Reference](#using-vde-ai---quick-reference)
6. [Everyday Tasks & Examples](#everyday-tasks--examples)
7. [Interactive Chat Mode](#interactive-chat-mode)
8. [Configuration Files](#configuration-files)
9. [Troubleshooting](#troubleshooting)
10. [Tips & Tricks](#tips--tricks)

---

## Welcome to VDE AI

### What is VDE AI?

The VDE AI Assistant is like having a helpful assistant who understands plain English and can manage your development environment for you. Instead of memorizing complex commands, you just tell it what you want in everyday language.

**Think of it like this:**

| Without VDE AI | With VDE AI |
|----------------|-------------|
| `docker-compose -f configs/docker/python/docker-compose.yml up -d --build` | `start python` |
| `docker ps --format "{{.Names}}"` | `what's running?` |
| `ssh -p 2200 devuser@localhost` | `how do I connect to Python?` |

### What Can You Do?

With VDE AI, you can:

- **Create** new development environments for different programming languages
- **Start** and **stop** your containers
- **Check** what's currently running
- **Get help** connecting to your environments
- **Manage** services like databases and web servers

**All by typing natural commands like:**
- "create a Go environment"
- "start everything"
- "show me what's running"
- "help me connect to Python"

---

## Getting Started

### Prerequisites

Before using VDE AI, make sure:

1. **Docker is installed** and running on your computer
2. **You're in the VDE directory** (typically `~/dev/`)
3. **You have SSH keys set up** (for connecting to your containers)

### Quick Start Test

Let's test if everything is ready:

```bash
# Navigate to your VDE directory
cd ~/dev

# Ask VDE AI what's available
./scripts/vde-ai "what can I create?"
```

You should see a list of available programming languages and services you can create.

### First Time Setup

If this is your first time using VDE, you may need to:

```bash
# 1. Make sure the scripts are executable
chmod +x ~/dev/scripts/vde-ai
chmod +x ~/dev/scripts/vde-chat

# 2. Test the help command
./scripts/vde-ai "help"
```

---

## Understanding the Basics

### The Two Ways to Use VDE AI

VDE AI has two modes:

#### 1. Command-Line Mode (`vde-ai`)

**Best for:** One-off commands, scripting, automation

```bash
# Ask a single question
./scripts/vde-ai "start python"

# Get information
./scripts/vde-ai "what's running?"
```

#### 2. Interactive Chat Mode (`vde-chat`)

**Best for:** Extended sessions, exploring, learning

```bash
# Start a chat session
./scripts/vde-chat

# Now you can have a conversation:
# [VDE] → create a Go environment
# [AI] → Creating Go environment...
#        Done!
# [VDE] → start it
# [AI] → Starting Go environment...
#        Done!
```

### Language VMs vs. Service VMs

VDE creates two types of containers:

**Language VMs** (for programming):
- Python, JavaScript, Rust, Go, Java, C#, Ruby, etc.
- Used for writing and running code
- Each gets its own isolated environment
- SSH ports: 2200-2299

**Service VMs** (for infrastructure):
- PostgreSQL, Redis, MongoDB, Nginx, etc.
- Used as supporting services for your applications
- Shared across your language environments
- SSH ports: 2400-2499

---

## Setting Up API Keys (Optional)

### Do You Need an API Key?

**Short answer:** No!

VDE AI works perfectly well without any API keys. It uses smart pattern matching to understand your commands.

**However**, you can optionally use an AI service (like Claude/Anthropic) for more advanced language understanding.

### Pattern-Based Mode (Default)

**Pros:**
- Works completely offline
- Fast (instant responses)
- No cost
- No setup required
- Privacy-friendly (nothing sent to external services)

**Cons:**
- Needs to match specific patterns
- Less flexible with unusual phrasing

### AI-Enhanced Mode (Optional)

**Pros:**
- More flexible with language
- Better at understanding complex requests
- Can handle more variations in phrasing

**Cons:**
- Requires internet connection
- Has a small cost per API call
- Sends your commands to an external service
- Requires setup

### Setting Up an API Key

If you want to use AI-enhanced mode, follow these steps:

#### Option 1: Environment Variable (Recommended)

1. Get an API key from [Anthropic](https://console.anthropic.com/)

2. Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Add this line to your shell profile
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. Reload your shell:
```bash
source ~/.zshrc
```

#### Option 2: Per-Command

```bash
# Use AI mode for a single command
ANTHROPIC_API_KEY="your-key" ./scripts/vde-ai "your question"
```

#### Option 3: Enable AI by Default

```bash
# Add this to your shell profile
export VDE_USE_AI="true"
```

Now all commands will try to use AI first (falling back to pattern matching if unavailable).

### Testing Your Setup

```bash
# Test if your API key is working
./scripts/vde-ai --ai "create a Python VM"

# If successful, it will use the AI service
# If the key isn't set, it will fall back to pattern matching
```

---

## Using VDE AI - Quick Reference

### Common Commands

Here are the everyday commands you'll use most often:

| What You Want to Say | What It Does |
|----------------------|--------------|
| "what can I create?" | Lists all available VMs |
| "create a Python VM" | Creates a Python environment |
| "start Python" | Starts the Python container |
| "stop Python" | Stops the Python container |
| "restart Python" | Restarts the container |
| "what's running?" | Shows all running containers |
| "how do I connect to Python?" | Shows SSH connection info |
| "help" | Shows help information |

### Command Patterns

VDE AI understands many different ways to say the same thing:

#### Creating VMs

```
✓ "create a Go VM"
✓ "make a Python environment"
✓ "set up Rust"
✓ "create Python and PostgreSQL"
✓ "make a Go container"
```

#### Starting VMs

```
✓ "start Python"
✓ "launch Go"
✓ "boot the Rust container"
✓ "start everything"
✓ "start all languages"
```

#### Stopping VMs

```
✓ "stop Python"
✓ "shutdown Go"
✓ "kill the Rust container"
✓ "stop everything"
✓ "shutdown all services"
```

#### Checking Status

```
✓ "what's running?"
✓ "show status"
✓ "what containers are running?"
✓ "check status of Python"
✓ "is Go running?"
```

#### Getting Connection Info

```
✓ "how do I connect to Python?"
✓ "SSH into Go"
✓ "connect to the Rust container"
✓ "show connection info for PostgreSQL"
```

### Special Flags

You can add special instructions to your commands:

#### Rebuild Flag

Forces a rebuild of the container (useful when Dockerfiles change):

```bash
./scripts/vde-ai "rebuild Python"
./scripts/vde-ai "restart Go with rebuild"
```

#### No-Cache Flag

Forces rebuilding without using Docker's cache (slower, ensures fresh build):

```bash
./scripts/vde-ai "rebuild Python with no cache"
./scripts/vde-ai "start Go without cache"
```

#### Dry Run Flag

Preview what would happen without actually doing it:

```bash
./scripts/vde-ai --dry-run "start Python"
# Output: [DRY RUN] Would start Python...
```

---

## Everyday Tasks & Examples

### Scenario 1: Starting a New Project

**Goal:** Set up a Python development environment

```bash
# Step 1: Create the environment
./scripts/vde-ai "create a Python VM"

# Step 2: Start it
./scripts/vde-ai "start Python"

# Step 3: Get connection info
./scripts/vde-ai "how do I connect to Python?"

# Step 4: Connect using the provided info
ssh python-dev
```

### Scenario 2: Setting Up a Full Stack

**Goal:** Create a web application with Python, PostgreSQL, and Redis

```bash
# Create all three environments
./scripts/vde-ai "create Python, PostgreSQL, and Redis"

# Start everything
./scripts/vde-ai "start Python, PostgreSQL, and Redis"

# Check what's running
./scripts/vde-ai "what's running?"

# Connect to Python to start coding
./scripts/vde-ai "how do I connect to Python?"
```

### Scenario 3: Experimenting with Languages

**Goal:** Try out different programming languages

```bash
# Start chat mode for interactive exploration
./scripts/vde-chat

# Have a conversation:
# [VDE] → what languages can I create?
# [AI] → (shows list of languages)
#
# [VDE] → create a Go VM
# [AI] → Creating Go VM... Done!
#
# [VDE] → start it
# [AI] → Starting Go VM... Done!
#
# [VDE] → connect to Go
# [AI] → To connect to Go:
#        SSH command: ssh go-dev
#        Port: 2201
#
# [VDE] → now create Rust and compare
# [AI] → Creating Rust VM... Done!
```

### Scenario 4: Daily Workflow

**Morning - Start your environments:**

```bash
# Start everything you need for the day
./scripts/vde-ai "start Python, PostgreSQL, and Redis"
```

**During work - Check status:**

```bash
# See what's running
./scripts/vde-ai "what's running?"
```

**Evening - Clean up:**

```bash
# Stop everything to save resources
./scripts/vde-ai "stop everything"
```

### Scenario 5: Troubleshooting

**Something's not working with Python:**

```bash
# Check if it's running
./scripts/vde-ai "is Python running?"

# Restart it with a fresh build
./scripts/vde-ai "rebuild Python with no cache"

# Check connection info
./scripts/vde-ai "how do I connect to Python?"
```

### Scenario 6: Multi-Language Project

**Working on a project that uses multiple languages:**

```bash
# Create all needed environments
./scripts/vde-ai "create Python, JavaScript, and Go"

# Start them all
./scripts/vde-ai "start all languages"

# Check status
./scripts/vde-ai "show status of all VMs"
```

---

## Interactive Chat Mode

### Starting Chat Mode

```bash
./scripts/vde-chat
```

You'll see a welcome screen:

```
╔════════════════════════════════════════════════════════════╗
║          VDE AI Assistant - Interactive Mode                 ║
║                                                            ║
║  Control your Virtual Development Environment              ║
║  using natural language commands                           ║
╚════════════════════════════════════════════════════════════╝

AI Mode:        Pattern-based
Available VMs:  18 language(s), 7 service(s)

Type 'help' for commands or 'exit' to quit
```

### Chat Mode Features

#### Special Commands

While in chat mode, you can use these special commands:

| Command | What It Does |
|---------|--------------|
| `help` | Shows help information |
| `clear` | Clears the screen |
| `history` | Shows your command history in this session |
| `exit` or `quit` | Leaves chat mode |

#### Example Chat Session

```
[VDE] → what can I create?
[AI] → python
        rust
        js
        csharp
        go
        ...

[VDE] → create a Go VM
[AI] → Creating Go VM...
       Done!

[VDE] → start it
[AI] → Starting Go VM...
       Done!

[VDE] → what's running?
[AI] → go-dev
       postgres

[VDE] → history
[AI] → Command History:
       1. what can I create?
       2. create a Go VM
       3. start it
       4. what's running?
       5. history

[VDE] → clear
[AI] → (screen clears, welcome message reappears)

[VDE] → exit
[AI] → Goodbye!
```

### Why Use Chat Mode?

**Advantages:**
- **Conversational:** Natural back-and-forth
- **History:** See what you've done in the session
- **Quick:** Don't need to type `./scripts/vde-ai` each time
- **Learning:** Great for exploring available commands

**When to use:**
- Setting up a new project (multiple related commands)
- Exploring what's available
- When you're unsure of exact commands
- Interactive development sessions

---

## Configuration Files

### What Configuration Files Exist?

VDE uses several configuration files. Here's what you need to know:

#### 1. VM Types Configuration

**Location:** `~/dev/scripts/data/vm-types.conf`

**What it does:** Defines all available VM types, their names, and how to install them.

**Sample entry:**
```
lang|python|python3|Python|apt-get update -y && apt-get install -y python3 python3-pip|
```

**Format:** `type|name|aliases|display_name|install_command|service_port`

**When to modify:** Only if you're adding a new programming language or service.

#### 2. Docker Compose Files

**Location:** `~/dev/configs/docker/<vm-name>/docker-compose.yml`

**What they do:** Define how each container is built and run.

**Example:** `~/dev/configs/docker/python/docker-compose.yml`

**When to modify:** When you need to customize a container's configuration.

#### 3. Environment Files

**Location:** `~/dev/env-files/<vm-name>.env`

**What they do:** Store environment variables for each VM.

**Example:** `~/dev/env-files/python.env`

**When to modify:** When you need to add environment variables for your applications.

#### 4. SSH Configuration

**Location:** `~/.ssh/config`

**What it does:** Stores connection shortcuts for your VMs.

**VDE manages this automatically** when you create VMs, but you can customize manually.

### Viewing Configuration

```bash
# See what VMs are configured
./scripts/vde-ai "what can I create?"

# Check a specific VM's configuration
cat ~/dev/configs/docker/python/docker-compose.yml

# Check environment variables
cat ~/dev/env-files/python.env
```

### Backing Up Configuration

VDE automatically backs up your SSH configuration when making changes:

```bash
# Backups are stored here
ls -la ~/dev/backup/ssh/
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "VM not found" Error

**Symptoms:**
```
[ERROR] Unknown VM: pyton
```

**Cause:** Typo in VM name

**Solution:**
```bash
# Check correct spelling
./scripts/vde-ai "what can I create?"

# Use exact name from the list
./scripts/vde-ai "create python"  # not "pyton"
```

#### Issue 2: "VM already exists" Error

**Symptoms:**
```
[ERROR] VM 'python' already exists
```

**Cause:** Trying to create a VM that's already set up

**Solution:**
```bash
# Just start it instead
./scripts/vde-ai "start python"

# Or check if it's running
./scripts/vde-ai "what's running?"
```

#### Issue 3: "Permission denied" Error

**Symptoms:**
```
Permission denied (publickey)
```

**Cause:** SSH keys not set up correctly

**Solution:**
```bash
# Check if you have SSH keys
ls -la ~/.ssh/id_ed25519

# If not, create one
ssh-keygen -t ed25519

# Make sure your public key is in the right place
cp ~/.ssh/id_ed25519.pub ~/dev/public-ssh-keys/

# Recreate the VM
./scripts/vde-ai "rebuild python with no cache"
```

#### Issue 4: Container won't start

**Symptoms:**
```bash
./scripts/vde-ai "start python"
# Nothing happens or error appears
```

**Possible causes and solutions:**

```bash
# 1. Check if Docker is running
docker ps

# 2. Try with rebuild
./scripts/vde-ai "rebuild python"

# 3. Try with no cache
./scripts/vde-ai "rebuild python with no cache"

# 4. Check Docker logs
docker logs python-dev
```

#### Issue 5: Can't connect to VM

**Symptoms:**
```bash
ssh python-dev
# Connection refused or timeout
```

**Solutions:**

```bash
# 1. Check if VM is running
./scripts/vde-ai "is Python running?"

# 2. Get correct connection info
./scripts/vde-ai "how do I connect to Python?"

# 3. Check SSH config
cat ~/.ssh/config | grep -A 5 python-dev

# 4. Try connecting manually with info from VDE
ssh -p 2200 devuser@localhost
```

### Getting Help

If you're stuck:

```bash
# Get general help
./scripts/vde-ai "help"

# Use chat mode for interactive help
./scripts/vde-chat
[VDE] → help
[VDE] → what can I do?

# Check the logs
tail -f ~/dev/logs/vde-ai.log
```

### Resetting Everything

If something is seriously wrong and you want to start fresh:

```bash
# Stop everything
./scripts/vde-ai "stop everything"

# Remove all containers (careful!)
docker ps -a | grep -E "dev$|[a-z]+$" | awk '{print $1}' | xargs docker rm -f

# You can now recreate VMs from scratch
./scripts/vde-ai "create python"
```

---

## Tips & Tricks

### Efficiency Tips

#### 1. Use Chat Mode for Sessions

Instead of:
```bash
./scripts/vde-ai "create python"
./scripts/vde-ai "start python"
./scripts/vde-ai "start postgres"
./scripts/vde-ai "what's running?"
```

Use chat mode:
```bash
./scripts/vde-chat
# Now just type your commands
```

#### 2. Create Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Quick aliases
alias vde='~/dev/scripts/vde-ai'
alias vdechat='~/dev/scripts/vde-chat'

# Now use shorter commands
vde "start python"
vdechat
```

#### 3. Use Wildcards

Instead of:
```bash
./scripts/vde-ai "start python"
./scripts/vde-ai "start rust"
./scripts/vde-ai "start go"
./scripts/vde-ai "start javascript"
```

Use:
```bash
./scripts/vde-ai "start all languages"
```

### Learning Patterns

VDE AI learns to recognize patterns. Here are common phrases that work:

#### Creating Environments

```
✓ "create a [language] VM"
✓ "make a [language] environment"
✓ "set up [language]"
✓ "I want to code in [language]"
✓ "get [language] ready"
```

#### Managing State

```
✓ "start [vm]"
✓ "launch [vm]"
✓ "boot [vm]"
✓ "stop [vm]"
✓ "shutdown [vm]"
✓ "restart [vm]"
✓ "reboot [vm]"
```

#### Getting Information

```
✓ "what's running?"
✓ "show status"
✓ "list all VMs"
✓ "what can I create?"
✓ "how do I connect to [vm]?"
✓ "show me the connection info for [vm]"
```

### Working with Multiple VMs

#### Batch Operations

```bash
# Create multiple at once
./scripts/vde-ai "create Python, Rust, and Go"

# Start multiple at once
./scripts/vde-ai "start Python and PostgreSQL"

# Stop multiple at once
./scripts/vde-ai "stop Python and Go"
```

#### Working with Categories

```bash
# All language VMs
./scripts/vde-ai "start all languages"
./scripts/vde-ai "show all languages"

# All service VMs
./scripts/vde-ai "start all services"
./scripts/vde-ai "list all services"

# Absolutely everything
./scripts/vde-ai "start everything"
./scripts/vde-ai "stop everything"
```

### Integration with Development Workflow

#### Before Coding

```bash
# Start your dev environment
./scripts/vde-ai "start Python and PostgreSQL"

# Open a new terminal tab/window
# Connect to your environment
./scripts/vde-ai "how do I connect to Python?"
# Use the provided SSH command
ssh python-dev
```

#### During Development

```bash
# In one terminal: connected to VM (coding)
ssh python-dev

# In another terminal: manage VMs
./scripts/vde-ai "what's running?"
./scripts/vde-ai "restart postgres"
```

#### After Development

```bash
# Stop everything to save resources
./scripts/vde-ai "stop everything"
```

### Scripting with VDE AI

You can use VDE AI in your own scripts:

```bash
#!/bin/bash
# my-project-setup.sh

# Create and start needed environments
~/dev/scripts/vde-ai "create Python and PostgreSQL"
~/dev/scripts/vde-ai "start Python and PostgreSQL"

# Wait for services to be ready
sleep 5

# Run your project setup
ssh python-dev "cd /projects/python && ./setup.sh"

echo "Project is ready!"
```

### Environment Variables

Useful environment variables to know about:

| Variable | Purpose | Example |
|----------|---------|---------|
| `VDE_USE_AI` | Enable AI mode by default | `export VDE_USE_AI="true"` |
| `CLAUDE_API_KEY` | Your Claude API key | `export CLAUDE_API_KEY="sk-..."` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | `export ANTHROPIC_API_KEY="sk-..."` |

### Understanding VM Aliases

VDE AI understands multiple names for the same VM:

| Canonical Name | Aliases You Can Use |
|----------------|---------------------|
| `python` | python3, python |
| `js` | node, nodejs, javascript |
| `cpp` | c++, gcc |
| `postgres` | postgresql, pg |
| `rust` | rust |

This means all of these work:
```bash
./scripts/vde-ai "create python"
./scripts/vde-ai "create python3"
./scripts/vde-ai "start node"
./scripts/vde-ai "start js"
./scripts/vde-ai "start postgresql"
```

---

## Quick Command Cheat Sheet

### Single-Line Commands

```bash
# Information
./scripts/vde-ai "help"
./scripts/vde-ai "what can I create?"
./scripts/vde-ai "what's running?"

# Creation
./scripts/vde-ai "create python"
./scripts/vde-ai "create Python, Go, and Rust"

# Starting
./scripts/vde-ai "start python"
./scripts/vde-ai "start all languages"
./scripts/vde-ai "start everything"

# Stopping
./scripts/vde-ai "stop python"
./scripts/vde-ai "stop all services"
./scripts/vde-ai "stop everything"

# Restarting
./scripts/vde-ai "restart python"
./scripts/vde-ai "rebuild python"
./scripts/vde-ai "rebuild python with no cache"

# Connection
./scripts/vde-ai "how do I connect to Python?"
./scripts/vde-ai "SSH into Go"
```

### Interactive Chat

```bash
# Start chat
./scripts/vde-chat

# In chat, type commands naturally:
# create a Go VM
# start it
# what's running?
# connect to Go
# exit
```

### With Options

```bash
# Dry run (preview only)
./scripts/vde-ai --dry-run "start python"

# Use AI mode (if configured)
./scripts/vde-ai --ai "create a Python VM for web development"

# Show help
./scripts/vde-ai --help
./scripts/vde-chat --help
```

---

## Conclusion

The VDE AI Assistant is designed to make managing development environments simple and intuitive. You don't need to memorize complex commands—just tell it what you want in plain English.

### Key Takeaways

1. **Start simple:** Use basic commands like "start python" or "what's running?"
2. **Be natural:** VDE AI understands everyday language
3. **Use chat mode:** For interactive sessions and exploration
4. **Check status:** Use "what's running?" to see current state
5. **Get help:** Type "help" anytime you're unsure

### Next Steps

1. **Try it out:** Start with a simple language like Python
2. **Explore:** Use chat mode to discover available VMs
3. **Customize:** Add your own project-specific setups
4. **Automate:** Create scripts for your common workflows

### Need More Help?

- **Quick help:** `./scripts/vde-ai "help"`
- **Interactive help:** `./scripts/vde-chat` then type `help`
- **Check logs:** `tail -f ~/dev/logs/vde-ai.log`
- **View configuration:** Check `~/dev/scripts/data/vm-types.conf`

---

**Happy coding!** 🚀

With VDE AI, you can focus on writing code instead of managing infrastructure. Just tell it what you need, and it handles the rest.
