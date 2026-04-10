#!/usr/bin/env zsh
# VDE Setup Scripts Updater
# Enforces UAP and adds 'git' and 'docker.io' to package lists.
set -e

for script in scripts/setup/*.zsh; do
    echo "Processing ${script}..."
    
    # 1. Enforce UAP before modification
    ./bin/vde-enforce-uap.zsh --quiet || { echo "UAP enforcement failed for ${script}"; exit 1; }
    
    # 2. Safely update the package list
    python3 -c '
import sys, re
script = sys.argv[1]

with open(script, "r") as f:
    content = f.read()

def replacer(m):
    pkgs = m.group(2).split()
    if "git" not in pkgs:
        pkgs.append("git")
    if "docker.io" not in pkgs:
        pkgs.append("docker.io")
    return m.group(1) + " ".join(pkgs) + m.group(3)

# Update the package variable
new_content = re.sub(r"(local\s+vde_\w+_pkgs=\")([^\"]*)(\")", replacer, content)

# Write back if changes were made
if new_content != content:
    with open(script, "w") as f:
        f.write(new_content)
    print(f"Updated {script} with git and docker.io")
else:
    print(f"No changes needed for {script} (packages already present)")
' "${script}"
    echo "----------------------------------------"
done

echo "Batch update complete."
