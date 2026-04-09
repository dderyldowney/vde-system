# Phase 24 System-Wide Spoke Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor all setup scripts in `scripts/setup/` to follow the VDE USP Hydration Ritual template, including persistence anchors for services.

**Architecture:** Use a ZSH refactor script to automate the transformation across all 31 setup scripts, ensuring consistency and adherence to the 2.0.6 USP mandate.

**Tech Stack:** ZSH, sed/awk, bin/vde-enforce-uap.zsh.

---

### Task 1: Research and Mapping

- [ ] **Step 1: Map all setup scripts and identify service properties.**
  List all files in `scripts/setup/` and identify which ones are services based on the provided mapping.

- [ ] **Step 2: Define service mappings in a ZSH associative array.**
  Create a mapping of script names to service names.

### Task 2: Refactor Script Development

- [ ] **Step 1: Write the refactor script `plans/scripts/refactor_setup.zsh`.**
  This script will iterate through the setup scripts, extract packages, and apply the template.

```zsh
#!/usr/bin/env zsh
# plans/scripts/refactor_setup.zsh
# Refactor all setup scripts to the v2.0.6 USP template

typeset -A service_map
service_map=(
    "redis" "redis-server"
    "mysql" "mysql"
    "nginx" "nginx"
    "rabbitmq" "rabbitmq-server"
    "couchdb" "couchdb"
    "mongodb" "mongodb"
    "postgres" "postgresql"
)

for file in scripts/setup/*-init.zsh; do
    name=$(basename "$file" "-init.zsh")
    is_service="false"
    service_name=""
    if [[ -n "${service_map[$name]}" ]]; then
        is_service="true"
        service_name="${service_map[$name]}"
    fi

    echo "Processing $file (name: $name, is_service: $is_service, service_name: $service_name)"

    # Extract existing packages
    # First, look for local vde_${name}_pkgs="..." or vde_pkgs="..."
    pkgs=$(grep -oP 'local vde_(python|c|js|...)?pkgs="\K[^"]+' "$file" || grep -oP 'local vde_pkgs="\K[^"]+' "$file")
    
    # If not found, look for apt-get install -y ...
    if [[ -z "$pkgs" ]]; then
        pkgs=$(grep "apt-get install -y" "$file" | sed 's/.*apt-get install -y //;s/\${=vde_.*_pkgs}//;s/sudo //g' | tr '\n' ' ' | xargs)
    fi

    # Fallback to empty if still not found
    pkgs=${pkgs:-""}

    # Extract custom build logic (lines between apt-get install and clean/rm)
    # This is tricky, we'll try to find any lines that aren't part of the standard boilerplate
    custom_logic=$(grep -vE "^(#!|#|apt-get|rm -rf|local|set -e|export|if|fi|mkdir|touch|grep|echo|chown|$) " "$file" | grep -v "local vde_" | grep -v "rm -rf /var/lib/apt/lists")

    # Construct new file content
    cat <<EOF > "$file"
#!/usr/bin/env zsh
# VDE USP Hydration Ritual: $name
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_${name}_pkgs="$pkgs"

# 2. THE FORGE WORK
apt-get update
apt-get install -y \${=vde_${name}_pkgs}
$custom_logic

# 3. PERSISTENCE ANCHOR (ONLY FOR SERVICES)
local _zshenv="/home/devuser/.zshenv"
if [[ "$is_service" == "true" ]]; then
    mkdir -p /home/devuser
    touch "\${_zshenv}"
    grep -q "service $service_name start" "\${_zshenv}" || echo "sudo service $service_name start >/dev/null 2>&1" >> "\${_zshenv}"
    chown devuser:devuser "\${_zshenv}"
fi

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF
done
```

### Task 3: Execution and Verification

- [ ] **Step 1: Run the refactor script.**
  `zsh plans/scripts/refactor_setup.zsh`

- [ ] **Step 2: Run UAP enforcer.**
  `bin/vde-enforce-uap.zsh`

- [ ] **Step 3: Verify a service script (e.g., `redis-init.zsh`).**
  `cat scripts/setup/redis-init.zsh`

- [ ] **Step 4: Verify a non-service script (e.g., `python-init.zsh`).**
  `cat scripts/setup/python-init.zsh`

- [ ] **Step 5: Commit changes.**
  `git add scripts/setup/*.zsh && git commit -m "refactor: apply Phase 24 Spoke Hardening to setup scripts"`
