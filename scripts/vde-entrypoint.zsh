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

echo "[VDE-ENTRYPOINT] Handshake complete. Starting SSH Gate..."
# 3. Start SSH Server (The Gate)
sudo /usr/sbin/sshd -D
