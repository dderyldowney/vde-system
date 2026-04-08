#!/usr/bin/env zsh
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
        if ! getent group docker > /dev/null; then
            echo "[VDE-ENTRYPOINT] Creating docker group with GID ${_docker_gid}..."
            sudo groupadd -g "${_docker_gid}" docker
        fi
        echo "[VDE-ENTRYPOINT] Adding devuser to docker group..."
        sudo usermod -aG docker devuser
    else
        echo "[VDE-ENTRYPOINT] docker.sock is owned by root, adding devuser to root group (fallback)..."
        sudo usermod -aG root devuser
    fi
    # Hard grant permissions to the socket to ensure no-sudo access
    sudo chmod 666 /var/run/docker.sock
else
    echo "[VDE-ENTRYPOINT] Warning: docker.sock not found or not a socket"
fi

# 2. SSH Agent Forwarding (macOS Bridge)
if [[ -S "/run/host-services/ssh-auth.sock" ]]; then
    echo "[VDE-ENTRYPOINT] macOS SSH bridge detected, symlinking..."
    mkdir -p "/home/devuser/.ssh/vde"
    # Recursive chown to handle root-owned parent dirs from mounts
    sudo chown -R devuser:devuser "/home/devuser/.ssh"
    chmod 700 "/home/devuser/.ssh"
    chmod 700 "/home/devuser/.ssh/vde"
    export SSH_AUTH_SOCK="/home/devuser/.ssh/vde/agent.sock"
    ln -sf /run/host-services/ssh-auth.sock "${SSH_AUTH_SOCK}"
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
# 5. Start SSH Server (The Gate)
# We override the port via command line argument
sudo /usr/sbin/sshd -D -p "${_vde_ssh_port}"
