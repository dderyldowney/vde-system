#!/usr/bin/env zsh
# plans/scripts/refactor_setup_simple.zsh
# Refactor simple setup scripts to follow the mandatory pattern

VDE_ROOT_DIR="${0:a:h:h:h}"
cd "$VDE_ROOT_DIR"

targets=(
    asm c cpp csharp displaytest flutter go haskell java lua php python ruby scala swift
)
# Add globbed targets
targets+=( $(ls scripts/setup/testcfg*-init.zsh scripts/setup/testport*-init.zsh 2>/dev/null | sed 's|scripts/setup/||;s|-init.zsh||') )

for target in "${targets[@]}"; do
    file="scripts/setup/${target}-init.zsh"
    [[ ! -f "$file" ]] && continue

    echo "Refactoring $file..."

    # Extract current packages
    pkgs=$(grep -oP 'local vde_.*_pkgs="\K[^"]+' "$file" || grep -oP 'local vde_pkgs="\K[^"]+' "$file")
    if [[ -z "$pkgs" ]]; then
        pkgs=$(grep "apt-get install -y" "$file" | sed 's/.*apt-get install -y //;s/\${=vde_.*_pkgs}//;s/sudo //g' | tr '\n' ' ' | xargs)
    fi

    # Extract any echo or other simple custom logic in THE FORGE WORK
    custom_logic=$(grep -vE "^(#!|#|apt-get|rm -rf|local|set -e|export|if|fi|mkdir|touch|grep|echo|chown|$) " "$file" | grep -v "local vde_" | grep -v "rm -rf /var/lib/apt/lists" | grep -v "Standardized Headers")
    # Also include echo "test" or similar if they are not common boilerplate
    extra_echo=$(grep "^echo " "$file" | grep -v "Registry" | grep -v "Fixing" | grep -v "Hammering")
    custom_logic="${custom_logic}
${extra_echo}"

    # Reconstruct the file
    cat <<EOF > "$file"
#!/usr/bin/env zsh
# VDE USP Hydration Script: $target
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_${target//-/_}_pkgs="$pkgs"

# 2. THE FORGE WORK
apt-get update
apt-get install -y \${=vde_${target//-/_}_pkgs}
$custom_logic

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF
done
