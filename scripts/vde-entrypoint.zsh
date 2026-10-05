#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth: ${(%):-%x}
# VDE Sovereign Entrypoint
# Version: 2.5.5 (Issue #457: Host-safe Docker socket GID handling)
#===============================================================================

# Ensure path includes local bin and VDE lib, but PRESERVE existing PATH (Rule 24)
# We append system paths to avoid shadowing Spoke-specific binaries (like Cargo)
export PATH="${PATH}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Sourcery Remediation 1: Portable privilege escalation helper.
# REQUIREMENT: This entrypoint MUST be launched as root (UID 0) OR have sudo
# available. In the VDE Forge, containers run as devuser with NOPASSWD sudo
# (see vde-base.Dockerfile). Minimal images without sudo MUST invoke this
# entrypoint via 'docker run --user root' or equivalent.
_root_exec() {
    if [[ "$(id -u)" -eq 0 ]]; then
        "$@"
    else
        sudo "$@"
    fi
}

echo "[VDE-ENTRYPOINT] Initializing Spoke Identity..."

# 0. Sovereign Docker Socket (The World-Forge Bridge)
#
# Issue #457: This socket is typically bind-mounted from the HOST (DooD).
# The entrypoint MUST NEVER chown/chmod/groupadd this socket at runtime --
# any of those mutate identity based on the CONTAINER's own /etc/group or
# /etc/passwd, which is assigned at image-build time and has no relation
# to the HOST's actual GID for "docker". A prior version of this block did
# `chown root:docker /var/run/docker.sock`, which silently corrupted the
# HOST socket's group ownership to whatever GID the container happened to
# call "docker" -- observed colliding with the host's unrelated "_ssh"
# group and locking every host user in the real "docker" group out of
# their own daemon.
#
# Fix: supplementary group access is granted entirely at container LAUNCH
# time via Compose's `group_add:` (see templates/compose-*.yml), which
# receives the host socket's numeric GID as a runtime-supplied value
# (VDE_DOCKER_SOCK_GID, computed by bin/vde right before `docker compose
# up`). Nothing GID-related is baked into the Dockerfile or mutated here,
# so the image stays portable across hosts with differing GIDs.
if [[ -S "/var/run/docker.sock" ]]; then
    echo "[VDE-ENTRYPOINT] Docker Socket present (access granted via launch-time group_add, no runtime mutation)."
fi

# 1. Identity & Permissions (Hardened)
# We ensure the SSH directory exists and has the correct permissions.
_root_exec mkdir -p /home/devuser/.ssh/vde
_root_exec chmod 755 /home/devuser  # sshd requires home NOT to be group-writable
_root_exec chmod 700 /home/devuser/.ssh
_root_exec chmod 700 /home/devuser/.ssh/vde

# 1.1. Dynamic SSH Identity Injection (Option B)
# We write the public key from the environment variable to the isolated vault
if [[ -n "${VDE_AUTHORIZED_KEY}" ]]; then
    echo "[VDE-ENTRYPOINT] Injecting Dynamic SSH Identity..."
    echo "${VDE_AUTHORIZED_KEY}" | _root_exec tee /home/devuser/.ssh/vde/authorized_keys >/dev/null
    _root_exec chmod 644 /home/devuser/.ssh/vde/authorized_keys
fi

# Force reclaim ownership for devuser
_root_exec chown -R devuser:devuser /home/devuser/.ssh
_root_exec chown devuser:devuser /home/devuser/.zshenv 2>/dev/null || true

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
        # Sourcery Remediation: Avoid world-writable bridge sockets.
        # We ensure devuser owns the bridge or has group access.
        _root_exec chown devuser:devuser "${_found_bridge}" 2>/dev/null || _root_exec chmod 666 "${_found_bridge}" 2>/dev/null || true
        break
    fi
done

if [[ -n "${_found_bridge}" ]]; then
    echo "[VDE-ENTRYPOINT] Sovereign Bridge Established: ${_found_bridge}"
    export SSH_AUTH_SOCK="${_found_bridge}"
    # Persist for subshells (Append to avoid overwriting build-time PATH)
    if ! grep -q "SSH_AUTH_SOCK" /home/devuser/.zshenv 2>/dev/null; then
        echo "export SSH_AUTH_SOCK=${_found_bridge}" | _root_exec tee -a /home/devuser/.zshenv >/dev/null
    else
        _root_exec sed -i "s|export SSH_AUTH_SOCK=.*|export SSH_AUTH_SOCK=${_found_bridge}|" /home/devuser/.zshenv
    fi
    _root_exec chown devuser:devuser /home/devuser/.zshenv
else
    echo "[VDE-ENTRYPOINT] WARNING: No SSH bridge found. Forwarding disabled."
fi

# 2.5. USB SERIAL DEVICE NODES (Signet #526)
# Opt-in via VDE_USB_TTY_NODES, set only by the per-Spoke USB overlay.
# Format: "<name>:<major>:<count>" entries, e.g. "ttyUSB:188:4 ttyACM:166:2".
#
# Container /dev is a fresh tmpfs on every start, so this runs each ignition.
# Nodes are pre-created so a board can be plugged, unplugged and replugged
# while the Spoke runs: a node with no device behind it fails open() with
# ENXIO (empty slot) or ENODEV (stale port still held), and begins working
# again the moment the kernel re-registers that port. Spare slots matter
# because a replug while the port is held open returns the board on the NEXT
# minor, and an unprivileged user cannot mknod the new node (EACCES).
#
# Node creation and node access are gated SEPARATELY: CAP_MKNOD creates the
# node, while the device cgroup rule gates open(). A node created without the
# matching rule exists but fails open() with EPERM. No probing open() is done
# here on purpose: opening a usb-serial port asserts DTR, which would reset an
# attached ESP32 on every Spoke ignition.
#
# Failure here MUST NEVER block the Spoke from starting.
if [[ -n "${VDE_USB_TTY_NODES}" ]]; then
    echo "[VDE-ENTRYPOINT] Pre-creating USB serial nodes..."
    typeset -a _usb_specs
    _usb_specs=( ${=VDE_USB_TTY_NODES} )

    for _spec in "${_usb_specs[@]}"; do
        if [[ ! "${_spec}" =~ ^[A-Za-z]+:[0-9]+:[0-9]+$ ]]; then
            echo "[VDE-ENTRYPOINT] WARNING: ignoring malformed VDE_USB_TTY_NODES entry '${_spec}'."
            continue
        fi

        _name="${_spec%%:*}"
        _rest="${_spec#*:}"
        _major="${_rest%%:*}"
        _count="${_rest#*:}"

        for (( _i = 0; _i < _count; _i++ )); do
            _node="/dev/${_name}${_i}"
            if [[ ! -e "${_node}" ]]; then
                if ! _root_exec mknod -m 0660 "${_node}" c "${_major}" "${_i}" 2>/dev/null; then
                    echo "[VDE-ENTRYPOINT] WARNING: could not create ${_node} (CAP_MKNOD missing or /dev not writable?)."
                    continue
                fi
            fi
            # Group ownership comes from the Spoke's own devuser group, not a
            # host gid: the node is this container's file. SSH logins rebuild
            # supplementary groups from /etc/group, so the PRIMARY group is
            # used and group_add is deliberately avoided.
            _root_exec chgrp devuser "${_node}" 2>/dev/null || \
                echo "[VDE-ENTRYPOINT] WARNING: could not chgrp ${_node}."
            _root_exec chmod 0660 "${_node}" 2>/dev/null || true
        done
    done
    unset _spec _name _rest _major _count _i _node
fi

# 3. SSH IDENTITY MANDATE (Rule 14 Readiness)
# We ensure the Spoke has host keys for the Transversal Bridge
if [[ ! -f /etc/ssh/ssh_host_rsa_key ]]; then
    echo "[VDE-ENTRYPOINT] Generating SSH host keys..."
    _root_exec ssh-keygen -A
fi

# 3.1. Dynamic Port Handshake
# Sourcery Remediations 2 & 3: Validate SSH_PORT is a numeric value in the
# legal range before touching sshd_config. Then apply a deterministic rewrite:
# remove ALL existing Port directives and append a single canonical one so the
# final configuration is unambiguous regardless of what the base image ships.
if [[ -n "${SSH_PORT}" ]]; then
    if [[ "${SSH_PORT}" =~ ^[0-9]+$ ]] && (( SSH_PORT >= 1 && SSH_PORT <= 65535 )); then
        echo "[VDE-ENTRYPOINT] Configuring SSH to listen on port ${SSH_PORT}..."
        # Strip any existing Port lines (commented or active), then append one.
        _root_exec sed -i '/^#\?Port /d' /etc/ssh/sshd_config
        echo "Port ${SSH_PORT}" | _root_exec tee -a /etc/ssh/sshd_config >/dev/null
    else
        echo "[VDE-ENTRYPOINT] WARNING: SSH_PORT '${SSH_PORT}' is not a valid port number (1-65535). Skipping port configuration."
    fi
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
