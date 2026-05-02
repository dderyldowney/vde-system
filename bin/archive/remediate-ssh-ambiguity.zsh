#!/usr/bin/env zsh
# @armor (Engine Core)
# remediate-ssh-ambiguity.zsh - Resolve AmbiguousStep (V3)
# Mandate: ZSH ONLY.


# ZSH-native logic demonstration (UAP Mandate 1)
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

set -e

VDE_ROOT_DIR="${0:h:h}"
STEPS_DIR="${VDE_ROOT_DIR}/tests/features/steps"
SSH_STEPS="${STEPS_DIR}/vde_ssh_hardening_steps.py"

print_info() { echo " \033[1;34m[INFO]\033[0m $1"; }

comment_duplicate() {
    local pattern=$1
    local file=$2
    if grep -qF "$pattern" "$file"; then
        print_info "Commenting out duplicate: $pattern"
        # Escape for perl - use comma as delimiter
        local escaped_pattern=$(echo "$pattern" | sed 's/"/\\"/g')
        perl -i -pe "s,^\@(.*)$escaped_pattern,\# \@\$1$escaped_pattern,g" "$file"
    fi
}

DUPLICATES=(
    "the SSH agent should be started automatically"
    "an SSH key should be generated automatically"
    "an ed25519 key should be generated"
    "the key should be loaded into the agent"
    "the key should be generated with a comment"
    "I should see the SSH agent status"
    "I should see my available SSH keys"
    "the setup should happen automatically"
    "my public keys should be copied to public-ssh-keys/"
    "all my public keys should be in the VM's authorized_keys"
)

for pattern in "${DUPLICATES[@]}"; do
    comment_duplicate "$pattern" "$SSH_STEPS"
done

print_info "SSH Ambiguity remediation (V3) complete."
