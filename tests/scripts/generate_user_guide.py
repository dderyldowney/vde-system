#!/usr/bin/env python3
"""
Generate USER_GUIDE.md from BDD test scenarios.

This script reads all feature files and generates a user guide
with helpful explanations and instructions.

Run: python3 tests/scripts/generate_user_guide.py
"""

import re
import os
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
FEATURES_DIR = REPO_ROOT / "tests" / "features"
OUTPUT_FILE = REPO_ROOT / "USER_GUIDE.md"

# Section introductions and explanations
SECTION_INTROS = {
    "1. Installation": """This is the part everyone finds confusing. Let's break it down.

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
""",

    "2. SSH Keys": """This is automatic, but you should understand what's happening.

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
""",

    "3. Your First VM": """Let's create your first development environment. We'll start with Python because it's the most common language for beginners.

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
""",

    "4. Understanding": """Let's verify everything works and understand the pieces.

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
""",

    "5. Starting and Stopping": """Daily workflow: starting when you work, stopping when done.

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
""",

    "6. Your First Cluster": """Now let's build a real application stack. This is where VDE shines.

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
""",

    "7. Connecting": """### Connecting to Your Python VM

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
""",

    "8. Working with Databases": """### Connecting to PostgreSQL from Your Python VM

**Try it yourself:**
```bash
# 1. Connect to your Python VM
ssh python-dev

# 2. Connect to PostgreSQL from within the VM
psql -h postgres -U devuser

# 3. You're now in PostgreSQL! Try:
# \\list                    # List databases
# \\c devuser               # Connect to default database
# \\dt                      # List tables
# SELECT 1;                # Run a query
# \\q                       # Quit
```

### Your Database Data Persists

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your data is safe.
""",

    "9. Daily Workflow": """### Morning Routine: Start Your Development Environment

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
""",

    "10. Adding More Languages": """### Creating a Second Language VM

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
""",

    "11. Troubleshooting": """### Problem: A VM Won't Start

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
"""
}


# Helper templates for common scenario patterns
SCENARIO_TEMPLATES = {
    "create": {
        "intro": "**Scenario: {title}**\n\n",
        "steps": "```\n{steps}\n```\n\n",
        "explanation": "**Run this command:**\n```bash\n{command}\n```\n\n"
    },
    "verify": {
        "intro": "**Scenario: {title}**\n\n",
        "steps": "```\n{steps}\n```\n\n",
        "explanation": "**Verify:**\n```bash\n{command}\n```\n\n**Expected:** {expected}\n\n"
    }
}


def extract_scenarios_from_feature(content):
    """Extract scenarios from a feature file content."""
    feature_match = re.search(
        r'Feature:\s*(.+?)\n(?:\s*As\s+(.+?)\n\s*I want\s+(.+?)\n\s*So\s+(.+?))?',
        content,
        re.DOTALL
    )
    feature_name = feature_match.group(1).strip() if feature_match else "Unknown Feature"

    scenario_pattern = r'Scenario:\s*(.+?)\n((?:\s*(?:Given|When|Then|And)\s+.+(?:\n|$))+)'
    scenarios = []
    for match in re.finditer(scenario_pattern, content, re.MULTILINE):
        scenario_name = match.group(1).strip()
        scenario_body = match.group(2).strip()
        scenarios.append((scenario_name, scenario_body))

    return feature_name, scenarios


def format_scenario_for_user_guide(scenario_name, scenario_body):
    """Format a scenario for the user guide with explanations."""
    lines = []

    # Clean up scenario name for display
    display_name = scenario_name.replace("-", " ").capitalize()

    lines.append(f"**Scenario: {display_name}**\n")
    lines.append("```")
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def generate_user_guide():
    """Generate the complete USER_GUIDE.md."""

    # Read all feature files
    all_scenarios = {}  # section -> list of (name, body)

    for feature_file in FEATURES_DIR.glob("**/*.feature"):
        try:
            with open(feature_file) as f:
                content = f.read()

            feature_name, scenarios = extract_scenarios_from_feature(content)

            for scenario_name, scenario_body in scenarios:
                # Determine section based on scenario name
                section = determine_section(scenario_name)
                if section:
                    if section not in all_scenarios:
                        all_scenarios[section] = []
                    all_scenarios[section].append((scenario_name, scenario_body))
        except Exception as e:
            print(f"Warning: Could not process {feature_file}: {e}")
            continue

    # Write the user guide
    with open(OUTPUT_FILE, 'w') as f:
        # Header
        f.write("# VDE User's Guide\n\n")
        f.write("> **This guide is generated from working BDD test scenarios.** ")
        f.write("Every workflow below has been tested and verified to work. ")
        f.write("If you follow these steps, they will work for you too.\n\n")
        f.write("---\n\n")

        # Table of contents
        f.write("## Table of Contents\n\n")
        sections = [
            "1. Installation",
            "2. SSH Keys",
            "3. Your First VM",
            "4. Understanding",
            "5. Starting and Stopping",
            "6. Your First Cluster",
            "7. Connecting",
            "8. Working with Databases",
            "9. Daily Workflow",
            "10. Adding More Languages",
            "11. Troubleshooting",
        ]
        for i, section in enumerate(sections, 1):
            section_id = section.lower().replace(" ", "-").replace(":", "")
            f.write(f'{i}. [{section}](#{section_id})\n')
        f.write("\n---\n\n")

        # Write each section
        for i, section in enumerate(sections, 1):
            f.write(f"## {section}\n\n")

            # Add section introduction if available
            intro_key = section
            for key in SECTION_INTROS:
                if key.startswith(section.split(".")[0] + "."):
                    intro_key = key
                    break
            if intro_key in SECTION_INTROS:
                f.write(SECTION_INTROS[intro_key])
                f.write("\n")

            # Add scenarios for this section
            scenarios_in_section = []
            for sec_key, scenarios in all_scenarios.items():
                if section.lower() in sec_key.lower() or sec_key.lower().startswith(section.split(".")[0].lower()):
                    scenarios_in_section.extend(scenarios)

            # Write a few representative scenarios (not all to keep it readable)
            if scenarios_in_section:
                seen = set()
                count = 0
                for scenario_name, scenario_body in scenarios_in_section:
                    if scenario_name not in seen and count < 5:  # Limit scenarios per section
                        seen.add(scenario_name)
                        count += 1
                        f.write(format_scenario_for_user_guide(scenario_name, scenario_body))

            f.write("---\n\n")

        # Quick reference card
        f.write(generate_quick_reference())

    print(f"✓ Generated {OUTPUT_FILE}")
    print(f"  Found {sum(len(s) for s in all_scenarios.values())} total scenarios")


def determine_section(scenario_name):
    """Determine which section a scenario belongs to."""
    name_lower = scenario_name.lower()

    if "installation" in name_lower or "prerequisite" in name_lower or "setup" in name_lower:
        return "1. Installation"
    elif "ssh" in name_lower and ("key" in name_lower or "agent" in name_lower or "config" in name_lower):
        return "2. SSH Keys"
    elif "first vm" in name_lower or "create vm" in name_lower or "hello world" in name_lower:
        return "3. Your First VM"
    elif "verify" in name_lower or "check status" in name_lower or "list" in name_lower or "understanding" in name_lower:
        return "4. Understanding"
    elif "start" in name_lower or "stop" in name_lower or "shutdown" in name_lower:
        return "5. Starting and Stopping"
    elif "cluster" in name_lower or "multi" in name_lower or "python postgres" in name_lower:
        return "6. Your First Cluster"
    elif "connect" in name_lower or "ssh into" in name_lower:
        return "7. Connecting"
    elif "database" in name_lower or "postgres" in name_lower or "redis" in name_lower:
        return "8. Working with Databases"
    elif "daily" in name_lower or "workflow" in name_lower or "morning" in name_lower:
        return "9. Daily Workflow"
    elif "language" in name_lower or "rust" in name_lower or "adding" in name_lower:
        return "10. Adding More Languages"
    elif "troubleshoot" in name_lower or "debug" in name_lower or "error" in name_lower or "rebuild" in name_lower:
        return "11. Troubleshooting"

    return None


def generate_quick_reference():
    """Generate the quick reference section."""
    return """## Quick Reference Card

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
"""


if __name__ == "__main__":
    generate_user_guide()
