#!/usr/bin/env zsh
# @armor (Spoke Entrypoint)
# VDE Sovereign Entrypoint
# Version: 2.5.1 (Hardened SSH Bridge)
#===============================================================================

# Ensure path includes local bin
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

echo "[VDE-ENTRYPOINT] Initializing Spoke Identity..."

# 1. Identity & Permissions
# We ensure devuser owns their home and the VDE identity
if [[ "$(whoami)" == "root" ]]; then
    # Fix ownership of devuser home (targeting directories only for speed)
    find "/home/devuser/.ssh" -type d -exec chown devuser:devuser {} +
    chmod 700 "/home/devuser/.ssh"
    chmod 700 "/home/devuser/.ssh/vde"
fi

# 2. Sovereign SSH Bridge (The Transversal Handshake)
# We prioritize the Sovereign Bridge socket mapping
local _found_bridge=""
local _proxy_sock="/run/vde-ssh.sock"
local _bridge_candidates=(
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

# 3. SPOKE IGNITION HOOKS
# Trigger automated hydration background services as root
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
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
