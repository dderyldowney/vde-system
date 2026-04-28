#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth: ${(%):-%x}
# VDE Sovereign Entrypoint
# Version: 2.5.1 (Hardened SSH Bridge)
#===============================================================================

# Ensure path includes local bin
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

echo "[VDE-ENTRYPOINT] Initializing Spoke Identity..."

# 1. Identity & Permissions (Hardened)
# We ensure the SSH directory exists and has the correct permissions.
# We use sudo to ensure we can fix ownership if old build artifacts exist.
sudo mkdir -p /home/devuser/.ssh/vde
sudo chmod 755 /home/devuser  # sshd requires home NOT to be group-writable
sudo chmod 700 /home/devuser/.ssh
sudo chmod 700 /home/devuser/.ssh/vde

# 1.1. Dynamic SSH Identity Injection (Option B)
# We write the public key from the environment variable to the isolated vault
if [[ -n "${VDE_AUTHORIZED_KEY}" ]]; then
    echo "[VDE-ENTRYPOINT] Injecting Dynamic SSH Identity..."
    echo "${VDE_AUTHORIZED_KEY}" | sudo tee /home/devuser/.ssh/vde/authorized_keys >/dev/null
    sudo chmod 644 /home/devuser/.ssh/vde/authorized_keys
fi

# Force reclaim ownership for devuser
sudo chown -R devuser:devuser /home/devuser/.ssh
sudo chown devuser:devuser /home/devuser/.zshenv 2>/dev/null || true

# 2. Sovereign SSH Bridge (The Transversal Handshake)
# We prioritize the Sovereign Bridge socket mapping
typeset _found_bridge=""
typeset _proxy_sock="/run/vde-ssh.sock"
typeset _bridge_candidates=(
    "/run/vde-ssh.sock"
    "/run/host-services/ssh-auth.sock"
    "/home/devuser/.ssh/vde/agent.sock"
)

for candidate in "${_bridge_candidates[@]}"; do
    if [[ -S "${candidate}" ]]; then
        _found_bridge="${candidate}"
        # Ensure world-readability for the bridge proxy
        chmod 666 "${_found_bridge}" 2>/dev/null || true
        break
    fi
done

if [[ -n "${_found_bridge}" ]]; then
    echo "[VDE-ENTRYPOINT] Sovereign Bridge Established: ${_found_bridge}"
    export SSH_AUTH_SOCK="${_found_bridge}"
    # Persist for subshells
    echo "export SSH_AUTH_SOCK=${_found_bridge}" > /home/devuser/.zshenv
    chown devuser:devuser /home/devuser/.zshenv
else
    echo "[VDE-ENTRYPOINT] WARNING: No SSH bridge found. Forwarding disabled."
fi

# 3. SSH IDENTITY MANDATE (Rule 14 Readiness)
# We ensure the Spoke has host keys for the Transversal Bridge
if [[ ! -f /etc/ssh/ssh_host_rsa_key ]]; then
    echo "[VDE-ENTRYPOINT] Generating SSH host keys..."
    sudo ssh-keygen -A
fi

# 3.1. Dynamic Port Handshake
# If SSH_PORT is provided, we update the daemon configuration
if [[ -n "${SSH_PORT}" ]]; then
    echo "[VDE-ENTRYPOINT] Configuring SSH to listen on port ${SSH_PORT}..."
    sudo sed -i "s/^#\?Port .*/Port ${SSH_PORT}/" /etc/ssh/sshd_config
fi

# 4. SPOKE IGNITION HOOKS
# Trigger automated hydration background services as root
typeset _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
if [[ -f "${_spoke_ignition}" ]]; then
    echo "[VDE-ENTRYPOINT] Triggering Spoke Ignition..."
    zsh "${_spoke_ignition}" &
fi

# 4. EXECUTION HANDOVER
# We hand over to the Spoke's primary voice
if [[ $# -gt 0 ]]; then
    exec "$@"
else
    # Default to an interactive zsh shell if no command provided
    exec /bin/zsh
fi
EOF
