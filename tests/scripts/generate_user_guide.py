#!/usr/bin/env python3
"""
Generate USER_GUIDE_SCENARIOS.md from BDD test scenarios.

This script reads all feature files and generates a reference document
showing all available test scenarios. This is for reference only -
the main USER_GUIDE.md is maintained manually.

Run: python3 tests/scripts/generate_user_guide.py
"""

import re
import os
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
FEATURES_DIR = REPO_ROOT / "tests" / "features"
OUTPUT_FILE = REPO_ROOT / "USER_GUIDE_SCENARIOS.md"

# Define the order of sections for user progression
SECTION_ORDER = [
    ("installation-setup", "1. Installation: Getting VDE on Your Computer"),
    ("ssh-agent-automatic-setup", "2. SSH Keys: Setting Up Secure Access"),
    ("vm-lifecycle", "3. Your First VM: The \"Hello World\" Moment"),
    ("ssh-agent-automatic-setup", "4. Understanding What Just Happened"),
    ("vm-lifecycle", "5. Starting and Stopping Your First VM"),
    ("multi-vm-workflow", "6. Your First Cluster: Python + PostgreSQL + Redis"),
    ("ssh-agent-vm-communication", "7. Connecting to Your VMs"),
    ("multi-vm-workflow", "8. Working with Databases"),
    ("daily-workflow", "9. Daily Workflow: Starting Your Day"),
    ("multi-vm-workflow", "10. Adding More Languages"),
    ("debugging", "11. Troubleshooting: When Things Go Wrong"),
]

# Feature keywords to match to sections
SECTION_KEYWORDS = {
    "1. Installation": ["installation", "setup", "fresh install"],
    "2. SSH Keys": ["ssh", "ssh keys", "ssh agent", "ssh config"],
    "3. Your First VM": ["first vm", "single vm", "create vm", "lifecycle"],
    "4. Understanding": ["verify", "check status", "list vms", "available"],
    "5. Starting and Stopping": ["start vm", "stop vm", "shutdown"],
    "6. Your First Cluster": ["multi-vm", "cluster", "python postgres redis"],
    "7. Connecting": ["connect", "ssh into", "ssh access"],
    "8. Working with Databases": ["database", "postgres", "redis", "mongodb"],
    "9. Daily Workflow": ["daily", "workflow", "morning"],
    "10. Adding More Languages": ["multiple languages", "second language", "rust", "go"],
    "11. Troubleshooting": ["troubleshooting", "debug", "error", "won't start", "rebuild"],
}


def extract_scenarios_from_feature(content):
    """Extract scenarios from a feature file content."""
    # Extract feature name and description
    feature_match = re.search(
        r'Feature:\s*(.+?)\n(?:\s*As\s+(.+?)\n\s*I want\s+(.+?)\n\s*So\s+(.+?))?',
        content,
        re.DOTALL
    )
    feature_name = feature_match.group(1).strip() if feature_match else "Unknown Feature"

    # Extract scenarios
    scenario_pattern = r'Scenario:\s*(.+?)\n((?:\s*(?:Given|When|Then|And)\s+.+(?:\n|$))+)'
    scenarios = []
    for match in re.finditer(scenario_pattern, content, re.MULTILINE):
        scenario_name = match.group(1).strip()
        scenario_body = match.group(2).strip()
        scenarios.append((scenario_name, scenario_body))

    return feature_name, scenarios


def categorize_scenario(scenario_name, feature_name):
    """Determine which section a scenario belongs to."""
    text = (scenario_name + " " + feature_name).lower()

    # Check keywords for each section
    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return section
        if keyword in text:
            return section

    return None


def format_scenario_as_guide(scenario_name, scenario_body):
    """Format a scenario as user guide documentation."""
    lines = []
    lines.append(f'**Scenario: {scenario_name}**\n')
    lines.append('```')
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    lines.append('```\n')
    return '\n'.join(lines)


def generate_user_guide():
    """Generate the complete USER_GUIDE.md."""

    # Read all feature files
    all_scenarios = {}  # section -> list of (name, body, feature)

    for feature_file in FEATURES_DIR.glob("**/*.feature"):
        try:
            with open(feature_file) as f:
                content = f.read()

            feature_name, scenarios = extract_scenarios_from_feature(content)

            for scenario_name, scenario_body in scenarios:
                section = categorize_scenario(scenario_name, feature_name)
                if section:
                    if section not in all_scenarios:
                        all_scenarios[section] = []
                    all_scenarios[section].append((scenario_name, scenario_body, feature_name))
        except Exception as e:
            print(f"Warning: Could not process {feature_file}: {e}")
            continue

    # Write the scenarios reference
    with open(OUTPUT_FILE, 'w') as f:
        # Header
        f.write("# VDE Test Scenarios Reference\n\n")
        f.write("> **This is a reference document showing all BDD test scenarios.** ")
        f.write("For the user guide, see USER_GUIDE.md\n\n")
        f.write("---\n\n")

        # Table of contents
        f.write("## Table of Contents\n\n")
        for _, section_title in SECTION_ORDER:
            section_id = section_title.lower().replace(" ", "-").replace(":", "").replace("/", "-")
            f.write(f'{len(SECTION_ORDER)}. [{section_title}](#{section_id})\n')
        f.write("\n---\n\n")

        # Ordered sections
        section_num = 0
        for section_keyword, section_title in SECTION_ORDER:
            section_id = section_title.lower().replace(" ", "-").replace(":", "").replace("/", "-")
            section_num += 1

            # Check if we have scenarios for this section
            scenarios_for_section = []
            for section, scenarios in all_scenarios.items():
                # Match by exact section title or if section is contained in title
                # categorize_scenario returns keys like "9. Daily Workflow"
                # section_title is like "9. Daily Workflow: Starting Your Day"
                if section == section_title or section in section_title:
                    scenarios_for_section.extend(scenarios)

            # Write section header (remove duplicate number from section_title if present)
            clean_title = section_title
            # Remove leading number like "9. " from section_title if present
            title_match = re.match(r'^\d+\.\s+(.+)$', section_title)
            if title_match:
                clean_title = title_match.group(1)
            f.write(f"## {section_num}. {clean_title}\n\n")

            # Write scenarios
            if scenarios_for_section:
                # Remove duplicates based on scenario name
                seen = set()
                for scenario_name, scenario_body, feature_name in scenarios_for_section:
                    key = (scenario_name, section_keyword)
                    if key not in seen:
                        seen.add(key)
                        f.write(format_scenario_as_guide(scenario_name, scenario_body))
                        f.write("\n")
            else:
                f.write("*Scenarios for this section coming soon...*\n\n")

            f.write("---\n\n")

        # Quick reference card
        f.write(generate_quick_reference())

        # Footer
        f.write("\n---\n\n")
        f.write("*This guide is generated from BDD test scenarios. ")
        f.write("Every workflow shown here has been tested and verified to work. ")
        f.write("If you follow these steps, they will work for you.*\n")

    print(f"✓ Generated {OUTPUT_FILE}")
    print(f"  Found {sum(len(s) for s in all_scenarios.values())} total scenarios")
    for section, scenarios in all_scenarios.items():
        print(f"  {section}: {len(scenarios)} scenarios")


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
4. Use the AI assistant for natural language control
"""


if __name__ == "__main__":
    generate_user_guide()
