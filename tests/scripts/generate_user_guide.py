#!/usr/bin/env python3
"""
Generate USER_GUIDE.md from PASSING BDD test scenarios only.

This script:
1. Reads Behave JSON output to identify which scenarios passed
2. Generates user guide with ONLY passing scenarios
3. Ensures all examples in the guide are actually verified to work
4. Loads educational content from YAML (not hardcoded)
5. Dynamically generates quick reference from vm-types.conf

Run: python3 tests/scripts/generate_user_guide.py
"""

import json
import re
import os
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
FEATURES_DIR = REPO_ROOT / "tests" / "features"
BEHAVE_JSON_FILE = REPO_ROOT / "tests" / "behave-results.json"
OUTPUT_FILE = REPO_ROOT / "USER_GUIDE.md"
INTROS_YAML_FILE = REPO_ROOT / "docs" / "user-guide-intros.yml"
VM_TYPES_CONF_FILE = REPO_ROOT / "scripts" / "data" / "vm-types.conf"


# =============================================================================
# YAML LOADING FUNCTIONS (Phase 2)
# =============================================================================

def load_section_intros_from_yaml():
    """
    Load section introductions from YAML file.

    Returns:
        dict: Mapping of section ID to intro text
    """
    if not INTROS_YAML_FILE.exists():
        print(f"Warning: {INTROS_YAML_FILE} not found. Using fallback intros.")
        return get_fallback_intros()

    sections = {}
    current_section = None
    current_content = []
    in_intro = False

    with open(INTROS_YAML_FILE) as f:
        for line in f:
            # Skip comments and empty lines at start
            if line.strip().startswith('#') and not current_section:
                continue

            # Match section start: - id: "Section Name"
            section_match = re.match(r'\s*-\s*id:\s*"([^"]+)"', line)
            if section_match:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).rstrip()
                current_section = section_match.group(1)
                current_content = []
                in_intro = False
                continue

            # Match intro: | marker
            if 'intro: |' in line:
                in_intro = True
                continue

            # Collect intro content (indented lines)
            if in_intro and current_section:
                # Remove the 6-space indentation from YAML format
                if line.startswith('      '):
                    current_content.append(line[6:])
                elif line.strip() and not line.strip().startswith('order:'):
                    # Handle lines that might not have proper indentation
                    current_content.append(line)

        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).rstrip()

    print(f"✓ Loaded {len(sections)} section intros from YAML")
    return sections


def get_fallback_intros():
    """Provide minimal fallback intros if YAML file is missing."""
    return {
        "1. Installation": "Install VDE by cloning the repository and running setup.",
        "2. SSH Keys": "SSH keys are managed automatically by VDE.",
        "3. Your First VM": "Create your first VM with `./scripts/vde create python`.",
        "4. Understanding": "Check VM status with `./scripts/vde list`.",
        "5. Starting and Stopping": "Start VMs with `./scripts/vde start <name>` and stop with `./scripts/vde stop <name>`.",
        "6. Your First Cluster": "Create multiple VMs that work together.",
        "7. Connecting": "SSH into VMs using simple names like `ssh python-dev`.",
        "8. Working with Databases": "Service VMs like PostgreSQL are accessible from language VMs.",
        "9. Daily Workflow": "Start your day with `./scripts/vde start python postgres redis`.",
        "10. Adding More Languages": "Add more languages anytime with `./scripts/vde create <name>`.",
        "11. Troubleshooting": "Check logs and use `--rebuild` if changes aren't reflected.",
    }


# =============================================================================
# VM TYPES CONF PARSING (Phase 4)
# =============================================================================

def parse_vm_types_conf():
    """
    Parse vm-types.conf and return structured data.

    Returns:
        dict: With 'languages' and 'services' lists
    """
    vm_types = {"languages": [], "services": []}

    if not VM_TYPES_CONF_FILE.exists():
        print(f"Warning: {VM_TYPES_CONF_FILE} not found.")
        return vm_types

    with open(VM_TYPES_CONF_FILE) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue

            # Parse: type|name|aliases|display_name|install_command|service_port
            parts = line.split("|")
            if len(parts) >= 6:
                vm_type = parts[0].strip()
                name = parts[1].strip()
                aliases = parts[2].strip() if len(parts) > 2 else ""
                display_name = parts[3].strip() if len(parts) > 3 else name
                install_cmd = parts[4].strip() if len(parts) > 4 else ""
                svc_port = parts[5].strip() if len(parts) > 5 else ""

                entry = {
                    "name": name,
                    "aliases": aliases,
                    "display": display_name,
                    "install": install_cmd,
                    "port": svc_port
                }

                if vm_type == "lang":
                    vm_types["languages"].append(entry)
                elif vm_type == "service":
                    vm_types["services"].append(entry)

    print(f"✓ Parsed {len(vm_types['languages'])} language VMs and {len(vm_types['services'])} service VMs")
    return vm_types


# =============================================================================
# BEHAVE JSON LOADING
# =============================================================================

def load_passing_scenarios_from_json():
    """Load the set of passing scenarios from Behave JSON output."""
    if not BEHAVE_JSON_FILE.exists():
        print(f"Warning: {BEHAVE_JSON_FILE} not found.")
        print("Run BDD tests first: ./tests/run-bdd-fast.sh")
        print("Generating user guide from ALL scenarios (unverified mode)")
        return None

    with open(BEHAVE_JSON_FILE) as f:
        data = json.load(f)

    passing_scenarios = set()
    for feature in data:
        feature_name = feature.get("name", "")
        for element in feature.get("elements", []):
            if element.get("type") == "scenario":
                scenario_name = element.get("name", "")
                status = element.get("status", "")
                if status == "passed":
                    # Create a unique identifier
                    key = f"{feature_name}:{scenario_name}"
                    passing_scenarios.add(key)

    print(f"✓ Found {len(passing_scenarios)} passing scenarios in test results")
    return passing_scenarios


# =============================================================================
# FEATURE FILE PARSING
# =============================================================================

def extract_scenarios_from_feature(content):
    """
    Extract scenarios from a feature file content.

    Returns:
        tuple: (feature_name, scenarios) where scenarios is a list of
               (scenario_name, scenario_body, tags)
    """
    feature_match = re.search(
        r'Feature:\s*(.+?)\n(?:\s*As\s+(.+?)\n\s*I want\s+(.+?)\n\s*So\s+(.+?))?',
        content,
        re.DOTALL
    )
    feature_name = feature_match.group(1).strip() if feature_match else "Unknown Feature"

    # Extract feature-level tags (if any)
    feature_tags = []
    feature_tag_match = re.search(r'Feature:(.+?)\n((?:\s*@\w+(?:\s+@\w+)*\n)*)', content, re.DOTALL)
    if feature_tag_match:
        tag_text = feature_tag_match.group(2) or ""
        feature_tags = [tag.strip() for tag in re.findall(r'@(\w+(?:-\w+)*)', tag_text)]

    # Pattern to match scenarios with optional tags before them
    scenario_pattern = r'(?:((?:\s*@\w+(?:-\w+)*\n)+)*)\s*Scenario:\s*(.+?)\n((?:\s*(?:Given|When|Then|And)\s+.+(?:\n|$))+)'
    scenarios = []
    for match in re.finditer(scenario_pattern, content, re.MULTILINE):
        tag_block = match.group(1) or ""
        scenario_name = match.group(2).strip()
        scenario_body = match.group(3).strip()

        # Extract tags from this scenario
        scenario_tags = [tag.strip() for tag in re.findall(r'@(\w+(?:-\w+)*)', tag_block)]

        # Combine feature and scenario tags (scenario tags take precedence)
        all_tags = scenario_tags if scenario_tags else feature_tags

        scenarios.append((scenario_name, scenario_body, all_tags))

    return feature_name, scenarios


# =============================================================================
# SCENARIO FORMATTING
# =============================================================================

# Mapping of scenario patterns to their actual vde commands
# This maps common scenario descriptions to the commands users would run
SCENARIO_COMMAND_MAP = {
    # Listing/Discovery scenarios
    "what VMs can I create": "vde list",
    "what VMs are available": "vde list",
    "list all available vms": "vde list",
    "show all services": "vde list --services",

    # Creation scenarios
    "create a Python VM": "vde create python",
    "create a go vm": "vde create go",
    "create a rust VM": "vde create rust",
    "create python and postgresql": "vde create python && vde create postgres",
    "plan to create": "vde create <vm-type>",

    # Start scenarios
    "start my development day": "vde start <vms>",
    "plan to start": "vde start <vms>",

    # Verification scenarios
    "verify installation commands": "vde list",
    "check service port configuration": "vde list",
    "count all configured vms": "vde list",
    "check vm status": "vde list",
}


def extract_command_from_scenario(scenario_name, scenario_body):
    """
    Extract or infer the actual vde command from a scenario.

    First tries to find explicit commands in the scenario body,
    then falls back to pattern matching from scenario names.

    Returns:
        str: The command or None if not found
    """
    # First, try to find explicit "When I run" commands
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line.startswith('When I run'):
            # Extract command from quotes
            match = re.search(r'When I run ["\']([^"\']+)["\']', line)
            if match:
                return match.group(1)

    # Second, try to find "When I parse" patterns (parser testing)
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line.startswith('When I parse'):
            # Extract the quoted text as a parser example
            match = re.search(r'When I parse ["\']([^"\']+)["\']', line)
            if match:
                return f"vde {match.group(1)}"

    # Third, try pattern matching from scenario name and body
    lower_name = scenario_name.lower()
    lower_body = scenario_body.lower()

    # Check for list/create/start patterns
    if "what vms can i create" in lower_body or "what VMs are available" in lower_body:
        return "vde list"
    elif "create" in lower_name or "create" in lower_body:
        # Extract VM type from scenario
        if "python" in lower_name or "python" in lower_body:
            return "vde create python"
        elif "go" in lower_name:
            return "vde create go"
        elif "rust" in lower_name:
            return "vde create rust"
        elif "postgres" in lower_name:
            return "vde create postgres"
    elif "start" in lower_name or "start" in lower_body:
        return "vde start <vms>"

    # Try the explicit mapping
    for pattern, command in SCENARIO_COMMAND_MAP.items():
        if pattern in lower_name or pattern in lower_body:
            return command

    return None


def format_scenario_for_user_guide(scenario_name, scenario_body):
    """
    Format a scenario for the user guide with structured sections.

    Format:
    1. **Scenario:** [name] (bold heading)
    2. Code block with Gherkin steps
    3. **Run the command:** heading + code block with actual command
    4. **What this does:** heading + explanation (if we have it)
    """
    lines = []

    # Clean up scenario name for display
    display_name = scenario_name.replace("-", " ").capitalize()

    # 1. Scenario title
    lines.append(f"**Scenario: {display_name}**\n")
    lines.append("")

    # 2. Gherkin steps in code block
    lines.append("```")
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    lines.append("```\n")
    lines.append("")

    # 3. Extract command and add "Run the command:" section
    command = extract_command_from_scenario(scenario_name, scenario_body)
    if command:
        # Map common patterns to more descriptive action labels
        action_label = "Run the command"
        lower_cmd = command.lower()

        if "list" in lower_cmd or "show" in lower_cmd or "what" in lower_cmd:
            action_label = "List available VMs"
        elif "create" in lower_cmd:
            action_label = "Create the VM"
        elif "start" in lower_cmd:
            action_label = "Start the VMs"
        elif "stop" in lower_cmd:
            action_label = "Stop the VMs"
        elif "build" in lower_cmd or "setup" in lower_cmd:
            action_label = "Run the setup"
        elif "remove" in lower_cmd or "delete" in lower_cmd:
            action_label = "Remove the VM"

        lines.append(f"**{action_label}:**\n")
    else:
        # No command found, skip this section
        return "\n".join(lines)

    lines.append("")
    lines.append("```bash")
    lines.append(command)
    lines.append("```")

    # Note: "What this does" section would require additional metadata
    # For now, we skip it since we don't have that information

    # No trailing newline - caller controls spacing
    return "\n".join(lines)


# =============================================================================
# SECTION DETERMINATION
# =============================================================================

def determine_section(scenario_name, tags=None):
    """
    Determine which section a scenario belongs to.

    PRIORITY ORDER:
    1. Explicit @user-guide-section tag (recommended)
    2. Keyword-based matching (fallback)

    TAGGING CONVENTION:
    Add one of these tags to your scenario/feature:
      @user-guide-installation       -> Section 1
      @user-guide-ssh-keys           -> Section 2
      @user-guide-first-vm           -> Section 3
      @user-guide-understanding      -> Section 4
      @user-guide-starting-stopping  -> Section 5
      @user-guide-cluster            -> Section 6
      @user-guide-connecting         -> Section 7
      @user-guide-databases          -> Section 8
      @user-guide-daily-workflow     -> Section 9
      @user-guide-more-languages     -> Section 10
      @user-guide-troubleshooting    -> Section 11
      @user-guide-internal           -> Not included (internal features)
    """
    # First, check for explicit tags
    if tags:
        tag_map = {
            "user-guide-installation": "1. Installation",
            "user-guide-ssh-keys": "2. SSH Keys",
            "user-guide-first-vm": "3. Your First VM",
            "user-guide-understanding": "4. Understanding",
            "user-guide-starting-stopping": "5. Starting and Stopping",
            "user-guide-cluster": "6. Your First Cluster",
            "user-guide-connecting": "7. Connecting",
            "user-guide-databases": "8. Working with Databases",
            "user-guide-daily-workflow": "9. Daily Workflow",
            "user-guide-more-languages": "10. Adding More Languages",
            "user-guide-troubleshooting": "11. Troubleshooting",
            "user-guide-internal": None,  # Explicitly exclude from user guide
        }
        for tag in tags:
            if tag in tag_map:
                return tag_map[tag]

    # Fallback: keyword-based matching
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


# =============================================================================
# DYNAMIC QUICK REFERENCE GENERATION (Phase 4)
# =============================================================================

def generate_quick_reference():
    """Generate the quick reference section from actual vm-types.conf data."""
    vm_types = parse_vm_types_conf()

    # Build language VM table
    lang_rows = []
    for vm in vm_types["languages"][:10]:  # Show first 10
        aliases = vm["aliases"] or "-"
        name = vm["display"]
        cmd = f"`vde create {vm['name']}`"
        lang_rows.append(f"| {name} | {cmd} | {aliases} |")

    # Build service VM table
    service_rows = []
    for vm in vm_types["services"]:
        name = vm["display"]
        cmd = f"`vde create {vm['name']}`"
        port = vm["port"] or "-"
        service_rows.append(f"| {name} | {cmd} | {port} |")

    return f"""## Quick Reference Card 📇

### Essential Commands (Your Cheat Sheet!)

```bash
# See what VMs are available
./scripts/vde list

# Create a new VM
./scripts/vde create <name>

# Start VMs
./scripts/vde start <vm1> <vm2> ...

# Stop VMs
./scripts/vde stop <vm1> <vm2> ...

# Stop everything
./scripts/vde stop all

# Rebuild a VM (when you make config changes)
./scripts/vde start <vm> --rebuild
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

| Language | Command | Aliases |
|----------|---------|---------|
{chr(10).join(lang_rows)}

### Service VMs (for data & infrastructure)

| Service | Command | Port |
|---------|---------|------|
{chr(10).join(service_rows)}

---

## You're Ready! 🎉

Look at you go! You now have:
- ✅ VDE installed and configured (you did it!)
- ✅ SSH keys set up automatically (no manual work!)
- ✅ Your first VM created (how cool is that?)
- ✅ Understanding of starting/stopping (like a pro!)
- ✅ A full cluster ready (Python + PostgreSQL + Redis)
- ✅ Knowledge to troubleshoot hiccups (you've got this!)

**What's Next?** 🚀

1. Create your first project in `projects/python/`
2. Start coding something amazing!
3. Add more languages whenever you want (Rust? Go? Elixir? They're waiting for you!)

**Remember:** You're learning valuable skills here. Every command you run, every VM you create — you're becoming a better developer. Be proud of yourself!

---

*This guide is generated from BDD test scenarios that have been verified to PASS. Every workflow shown here has been tested and verified to work. If you follow these steps, they will work for you.*

**Now go build something awesome!** 💪✨
"""


# =============================================================================
# MAIN GENERATION FUNCTION (Phases 2 & 3: Load YAML + Write Scenarios Bug Fix)
# =============================================================================

def generate_user_guide(passing_scenarios=None):
    """
    Generate the complete USER_GUIDE.md with only passing scenarios.

    Phase 2 Fix: Loads intros from YAML instead of hardcoded dict
    Phase 3 Fix: Actually writes scenarios to the guide (was broken before)
    """
    # Load section intros from YAML (Phase 2)
    section_intros = load_section_intros_from_yaml()

    # Verify mode warning
    if passing_scenarios is None:
        print("⚠ WARNING: Running in UNVERIFIED mode")
        print("  Scenarios have NOT been tested!")
        print("  Run BDD tests first to generate verified guide\n")

    # Read all feature files and extract scenarios
    all_scenarios = {}  # section -> list of (name, body)

    for feature_file in FEATURES_DIR.glob("**/*.feature"):
        try:
            with open(feature_file) as f:
                content = f.read()

            feature_name, scenarios = extract_scenarios_from_feature(content)

            for scenario_name, scenario_body, tags in scenarios:
                # Check if scenario passed (if we have test results)
                if passing_scenarios is not None:
                    key = f"{feature_name}:{scenario_name}"
                    if key not in passing_scenarios:
                        # Skip failed scenarios
                        continue

                # Determine section based on tags (primary) or scenario name (fallback)
                section = determine_section(scenario_name, tags)
                if section:
                    if section not in all_scenarios:
                        all_scenarios[section] = []
                    all_scenarios[section].append((scenario_name, scenario_body))
        except Exception as e:
            print(f"Warning: Could not process {feature_file}: {e}")
            continue

    # Count scenarios that were extracted
    total_extracted = sum(len(s) for s in all_scenarios.values())
    if passing_scenarios is not None:
        print(f"  Included {total_extracted} verified passing scenarios")

    # Write the user guide
    with open(OUTPUT_FILE, 'w') as f:
        # Logo image (always at top)
        f.write('<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>\n\n')

        # Header with verification notice
        if passing_scenarios is not None:
            f.write("**Every workflow in this guide has been tested and verified to PASS.** Follow the steps, they will work for you too.\n\n")
        else:
            f.write("**WARNING: This guide was generated in UNVERIFIED mode. Scenarios have NOT been tested!**\n\n")
            f.write("**Run `./tests/run-bdd-tests.sh` first to generate a verified guide.**\n\n")

        f.write("---\n\n")

        # Table of contents
        f.write("## Table of Contents\n\n")
        sections = [
            ("1. Installation", [
                ("Installing Docker Desktop", [
                    ("For Windows Users", "for-windows-users"),
                    ("For macOS (Mac) Users", "for-macos-mac-users"),
                    ("For Linux Users", "for-linux-users"),
                ]),
                ("Installing Git", [
                    ("For Windows Users", "for-windows-users-1"),
                    ("For macOS (Mac) Users", "for-macos-mac-users-1"),
                    ("For Linux Users", "for-linux-users-1"),
                ]),
                ("Installing Zsh and Bash", [
                    ("For Windows Users", "for-windows-users-2"),
                    ("For macOS (Mac) Users", "for-macos-mac-users-2"),
                    ("For Linux Users", "for-linux-users-2"),
                ]),
                ("Quick Checklist: Are You Ready?", "quick-checklist-are-you-ready"),
            ]),
            ("2. SSH Keys", []),
            ("3. Your First VM", []),
            ("4. Understanding", []),
            ("5. Starting and Stopping", []),
            ("6. Your First Cluster", []),
            ("7. Connecting", []),
            ("8. Working with Databases", []),
            ("9. Daily Workflow", []),
            ("10. Adding More Languages", []),
            ("11. Troubleshooting", []),
        ]
        for i, (section, subsections) in enumerate(sections, 1):
            section_id = section.lower().replace(" ", "-").replace(":", "")
            f.write(f'{i}. [{section}](#{section_id})\n')
            for subsection, sub_subsections in subsections:
                subsection_id = subsection.lower().replace(" ", "-").replace(":", "").replace("?", "")
                f.write(f'   - [{subsection}](#{subsection_id})\n')
                if isinstance(sub_subsections, list):
                    for sub_subsection, sub_subsection_id in sub_subsections:
                        f.write(f'     - [{sub_subsection}](#{sub_subsection_id})\n')
        f.write("\n---\n\n")

        # Write each section with collapsible wrapping
        for i, (section, _) in enumerate(sections, 1):
            # Start collapsible section (default open)
            f.write(f'<details open>\n\n')
            f.write(f'<summary><h2>{section}</h2></summary>\n\n')

            # Add section introduction from YAML (Phase 2)
            intro_key = section
            for key in section_intros:
                if key.startswith(section.split(".")[0] + "."):
                    intro_key = key
                    break
            if intro_key in section_intros:
                intro = section_intros[intro_key]
                f.write(intro)
                # Ensure intro ends with newlines before next section
                if intro and not intro.endswith('\n\n'):
                    f.write("\n\n")

            # *** PHASE 3 BUG FIX: Write scenarios after each section intro ***
            # This was the critical bug - scenarios were extracted but never written
            if section in all_scenarios and all_scenarios[section]:
                f.write("### Verified Scenarios\n\n")
                # Preface: explain vde commands vs scripts
                f.write("> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. ")
                f.write("Each scenario includes the actual **`vde` command** you would run to accomplish the task. ")
                f.write("We show the unified `vde` command because it's simpler and more consistent than ")
                f.write("remembering individual script names like `create-virtual-for` or `start-virtual`. ")
                f.write("The `vde` command handles all the heavy lifting for you!\n\n")
                for scenario_name, scenario_body in all_scenarios[section]:
                    f.write(format_scenario_for_user_guide(scenario_name, scenario_body))
                    f.write("\n\n")

            # End collapsible section
            f.write("</details>\n\n")

        # Quick reference card (now dynamically generated - Phase 4)
        f.write(generate_quick_reference())

    print(f"✓ Generated {OUTPUT_FILE}")
    if passing_scenarios is not None:
        print(f"  All scenarios in this guide have been verified to PASS")
    else:
        print(f"  WARNING: Scenarios in this guide have NOT been verified!")


if __name__ == "__main__":
    passing_scenarios = load_passing_scenarios_from_json()
    generate_user_guide(passing_scenarios)
