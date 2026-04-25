#!/usr/bin/env zsh
# @armor (Engine Core)
# finalize-ssh-deduplication.zsh - Resolve AmbiguousStep between core and hardening
# Mandate: ZSH ONLY.

set -e

VDE_ROOT_DIR="${0:a:h:h}"
HARDENING_STEPS="${VDE_ROOT_DIR}/tests/features/steps/vde_ssh_hardening_steps.py"
CORE_STEPS="${VDE_ROOT_DIR}/tests/features/steps/ssh_core_steps.py"

print_info() { echo " \033[1;34m[INFO]\033[0m $1"; }

# Get all unique step patterns from core_steps
print_info "Extracting patterns from ssh_core_steps.py..."
patterns=($(grep -oE "@(given|when|then)\(\"([^\"]+)\"\)" "$CORE_STEPS" | sed -E 's/@(given|when|then)\("([^"]+)"\)/\2/'))

for p in "${patterns[@]}"; do
    if grep -qF "$p" "$HARDENING_STEPS"; then
        print_info "Commenting out duplicate pattern: $p"
        # Escape pattern for perl
        escaped_p=$(echo "$p" | sed 's/"/\\"/g')
        perl -i -pe "s,^\@(.*)\"$escaped_p\",\# \@\$1\"$escaped_p\",g" "$HARDENING_STEPS"
    fi
done

print_info "Deduplication complete."
