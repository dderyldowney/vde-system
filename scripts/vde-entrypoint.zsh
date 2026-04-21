#!/usr/bin/env zsh
# @armor (Spoke Lifecycle)
#===============================================================================
# VDE-ENTRYPOINT (The Atomic Handshake)
# Dynamically aligns container identity with host resources (Docker/SSH)
#===============================================================================

echo "[VDE-ENTRYPOINT] Starting ignition sequence..."

# 1. Docker Socket Sovereignty
if [[ -S "/var/run/docker.sock" ]]; then
    local _docker_gid=$(stat -c '%g' /var/run/docker.sock)
    echo "[VDE-ENTRYPOINT] Detected docker.sock GID: ${_docker_gid}"
    
    if [[ "${_docker_gid}" != "0" ]]; then
        # Check if GID is already assigned to a group
        local _existing_group=$(getent group "${_docker_gid}" | cut -d: -f1)
        if [[ -n "${_existing_group}" ]]; then
            echo "[VDE-ENTRYPOINT] GID ${_docker_gid} is already assigned to group: ${_existing_group}"
            sudo usermod -aG "${_existing_group}" devuser
        else
            if ! getent group docker > /dev/null; then
                echo "[VDE-ENTRYPOINT] Creating docker group with GID ${_docker_gid}..."
                sudo groupadd -g "${_docker_gid}" docker
            fi
            sudo usermod -aG docker devuser
        fi
    else
        echo "[VDE-ENTRYPOINT] docker.sock is owned by root, adding devuser to root group (fallback)..."
        sudo usermod -aG root devuser
    fi
    # Hard grant permissions to the socket to ensure no-sudo access
    sudo chmod 666 /var/run/docker.sock
else
    echo "[VDE-ENTRYPOINT] Warning: docker.sock not found or not a socket"
fi

# 2. SSH Agent Forwarding (Sovereign Bridge)
local -a _bridge_candidates=(
    "/run/vde-ssh.sock"                # VDE 2026 Standard (Direct Bind)
    "/run/host-services/ssh-auth.sock" # Canonical Darwin / Realignment Path
    "/ssh-agent"                       # Legacy / Alternative
)

local _found_bridge=""
echo "[VDE-ENTRYPOINT] Initializing Sovereign Bridge Handshake..."
for candidate in "${_bridge_candidates[@]}"; do
    echo "[VDE-ENTRYPOINT] Searching for SSH bridge at ${candidate}..."
    if [[ -S "${candidate}" ]]; then
        _found_bridge="${candidate}"
        echo "[VDE-ENTRYPOINT] SUCCESS: Valid socket found at ${_found_bridge}"
        # Grant permissions to the bridge to ensure devuser can access it via socat
        sudo chmod 666 "${_found_bridge}"
        break
    elif [[ -d "${candidate}" ]]; then
        echo "[VDE-ENTRYPOINT] GHOST DETECTED: ${candidate} is a directory (Mount Failure)."
        # Attempt recovery: see if a socket exists INSIDE the ghost directory
        local _inner_sock=$(find "${candidate}" -maxdepth 2 -type s | head -1)
        if [[ -n "${_inner_sock}" ]]; then
            _found_bridge="${_inner_sock}"
            echo "[VDE-ENTRYPOINT] RECOVERY: Found inner socket at ${_found_bridge}"
            break
        fi
    fi
done

if [[ -n "${_found_bridge}" ]]; then
    mkdir -p "/home/devuser/.ssh/vde"
    # Minimum viable chown for bridge functionality
    # Avoid recursive blocks on large directories like .vde-venv
    sudo chown devuser:devuser "/home/devuser"
    sudo chown -R devuser:devuser "/home/devuser/.ssh"
    
    chmod 700 "/home/devuser/.ssh"
    chmod 700 "/home/devuser/.ssh/vde"
    
    local _proxy_sock="/home/devuser/.ssh/vde/agent.sock"
    
    # Only establish proxy if SSH_AUTH_SOCK is NOT already set by a legitimate SSH connection
    if [[ -z "${SSH_AUTH_SOCK}" ]] || [[ "${SSH_AUTH_SOCK}" == "${_proxy_sock}" ]]; then
        export SSH_AUTH_SOCK="${_proxy_sock}"
        
        # Symbolic Handshake (The Bridge Proxy)
        if command -v socat >/dev/null 2>&1; then
            echo "[VDE-ENTRYPOINT] SUCCESS: Proxying ${_found_bridge} to ${_proxy_sock}..."
            # Run proxy in background as devuser
            sudo -u devuser socat UNIX-LISTEN:"${_proxy_sock}",fork,unlink-early UNIX-CONNECT:"${_found_bridge}" &
        else
            echo "[VDE-ENTRYPOINT] WARNING: socat missing. Falling back to direct symlink."
            ln -sf "${_found_bridge}" "${_proxy_sock}"
        fi
        
        # Persistent bridge for non-login shells (Hardened: do not overwrite existing agent)
        grep -q "SSH_AUTH_SOCK" /home/devuser/.zshenv 2>/dev/null || {
            echo 'if [[ -z "${SSH_AUTH_SOCK}" ]]; then export SSH_AUTH_SOCK="'${_proxy_sock}'"; fi' >> /home/devuser/.zshenv
        }
        sudo chown devuser:devuser /home/devuser/.zshenv
        echo "[VDE-ENTRYPOINT] Persistent bridge verified at /home/devuser/.zshenv"
    else
        echo "[VDE-ENTRYPOINT] SUCCESS: SSH agent already established via protocol forwarding."
    fi
else
    echo "[VDE-ENTRYPOINT] WARNING: All SSH bridge candidates failed."
    echo "[VDE-ENTRYPOINT] Blockade: Verification of Section 10.5 will fail."
fi

# 3. Universal Port Configuration (Rule I)
local _types_json="/vde/data/vm-types.json"
local _vde_ssh_port=22 # Default fallback

echo "[VDE-ENTRYPOINT] Checking for authoritative port configuration..."
if [[ -f "${_types_json}" ]]; then
    echo "[VDE-ENTRYPOINT] Found VM types registry: ${_types_json}"
    # We use pure ZSH parsing to avoid direct JQ dependency inside the container (Rule G)
    # Get current container hostname (which matches canonical name)
    local _hostname=$(hostname)
    # Search for the ssh_port in the JSON for this VM name
    # Heuristic: search for the line with the name, then the next few lines for ssh_port
    local _port_found=$(grep -A 10 "\"name\": \"${_hostname}\"" "${_types_json}" | grep "\"ssh_port\":" | head -1 | sed -E 's/.*: ([0-9]+).*/\1/')
    
    echo "[VDE-ENTRYPOINT] Debug: _hostname=${_hostname} _port_found=${_port_found}"
    
    if [[ -z "${_port_found}" ]]; then
        # Try without prefix if hostname doesn't have it (though it should)
        local _base_name="${_hostname#vde-}"
        _port_found=$(grep -A 10 "\"name\": \"${_base_name}\"" "${_types_json}" | grep "\"ssh_port\":" | head -1 | sed -E 's/.*: ([0-9]+).*/\1/')
        echo "[VDE-ENTRYPOINT] Debug: _base_name=${_base_name} _port_found_base=${_port_found}"
    fi
    
    if [[ -n "${_port_found}" ]]; then
        _vde_ssh_port="${_port_found}"
        echo "[VDE-ENTRYPOINT] Authoritative SSH Port: ${_vde_ssh_port}"
    fi

    # 4. Generate Global SSH Client Config (VM-to-VM Bridge)
    echo "[VDE-ENTRYPOINT] Generating VM-to-VM bridge configuration..."
    mkdir -p "/home/devuser/.ssh"
    echo "# VDE Universal VM-to-VM Bridge" > "/home/devuser/.ssh/config"
    
    # Parse all VM names and ports from JSON
    # Simple extraction loop
    local _all_vms=$(grep -E "\"name\":|\"ssh_port\":" "${_types_json}" | sed 's/^[[:space:]]*//')
    local _current_name=""
    
    echo "${_all_vms}" | while read -r _line; do
        if [[ "${_line}" == "\"name\":"* ]]; then
            _current_name=$(echo "${_line}" | sed 's/\"name\": \"\(.*\)\",/\1/')
        elif [[ "${_line}" == "\"ssh_port\":"* && -n "${_current_name}" ]]; then
            local _port=$(echo "${_line}" | sed 's/\"ssh_port\": \([0-9]*\).*/\1/')
            cat >> "/home/devuser/.ssh/config" <<EOF
Host ${_current_name}
    Port ${_port}
    User devuser
    IdentityFile /home/devuser/.ssh/vde/vde_student
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR

EOF
            _current_name=""
        fi
    done
    
    chmod 600 "/home/devuser/.ssh/config"
    sudo chown devuser:devuser "/home/devuser/.ssh/config"
else
    echo "[VDE-ENTRYPOINT] ERROR: VM types registry NOT FOUND at ${_types_json}"
fi

echo "[VDE-ENTRYPOINT] Handshake complete. Starting SSH Gate on port ${_vde_ssh_port}..."

# 5. Spoke Ignition (Sovereign Service Mandate)
# If a spoke has a specific startup script, trigger it now.
# Use /usr/local/bin to avoid being overwritten by /vde mount
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
if [[ -f "${_spoke_ignition}" ]]; then
    echo "[VDE-ENTRYPOINT] Triggering Spoke Ignition: ${_spoke_ignition}..."
    # Execute in background, detached from the SSH gate
    zsh "${_spoke_ignition}" &
fi

# 6. Start SSH Server (The Gate)
# We override the port via command line argument
sudo /usr/sbin/sshd -D -p "${_vde_ssh_port}"
