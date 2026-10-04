#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
"""
SSH Helper Functions for VDE Test Steps.

This module provides shared utility functions for SSH verification
used across all SSH-related BDD step definitions.

All SSH operations now use VDE-specific isolated paths at ~/.ssh/vde/
"""

import os
import re
import socket
import subprocess

# Add steps directory to path for config import
import sys
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

# Import shared configuration and constants from vm_common
from vm_common import VDE_ROOT, run_vde_command, docker_ps, container_exists, ALLOW_CLEANUP

# VDE SSH Isolation - All SSH operations use these paths
VDE_SSH_DIR = Path.home() / ".ssh" / "vde"
VDE_SSH_CONFIG = VDE_SSH_DIR / "config"
VDE_SSH_KNOWN_HOSTS = VDE_SSH_DIR / "known_hosts"
VDE_SSH_IDENTITY = VDE_SSH_DIR / "vde_student"

# VDE's own ssh-agent: a dedicated socket inside ~/.ssh/vde, recorded in agent_env,
# preloaded with a fixed set of allowed keys. The user's personal agent is never used.
VDE_SSH_AGENT_ENV = VDE_SSH_DIR / "agent_env"
VDE_SSH_AGENT_SOCK = VDE_SSH_DIR / "agent.sock"
VDE_ALLOWED_KEYS = ("vde_student",)


def _recorded_agent_sock():
    """Socket recorded in VDE's agent_env, or None.

    agent_env uses `SSH_AUTH_SOCK=<path>; export SSH_AUTH_SOCK;` lines (the
    format `ssh-agent -s` prints). Read with a regex, nothing is exported.
    """
    try:
        text = VDE_SSH_AGENT_ENV.read_text()
    except OSError:
        return None
    match = re.search(r"^\s*SSH_AUTH_SOCK=([^;\s]+)", text, re.MULTILINE)
    return match.group(1).strip("\"'") if match else None


def _socket_accepts(path):
    """True if something is listening on the unix socket at `path`.

    Connecting tells a live agent from a dead leftover socket file (refused)
    without guessing about processes; ssh-agent is non-dumpable, so its file
    descriptors cannot be inspected.
    """
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(str(path))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def vde_agent_env():
    """Environment for talking to VDE's own ssh-agent, and to nothing else.

    SSH_AUTH_SOCK is always VDE's dedicated socket and SSH_AGENT_PID is
    removed, so a step using this environment can never reach the user's
    personal agent, whatever the test process inherited.
    """
    env = os.environ.copy()
    env.pop("SSH_AGENT_PID", None)
    env["SSH_AUTH_SOCK"] = str(VDE_SSH_AGENT_SOCK)
    return env


def vde_agent_is_running():
    """True if VDE's own agent is up: agent_env records exactly the dedicated
    socket and the socket accepts connections. Never looks at the inherited agent."""
    return _recorded_agent_sock() == str(VDE_SSH_AGENT_SOCK) and _socket_accepts(
        VDE_SSH_AGENT_SOCK
    )


def _vde_agent_listing():
    """`ssh-add -l` against VDE's agent only; None if the agent is not running."""
    if not vde_agent_is_running():
        return None
    try:
        return subprocess.run(
            ["ssh-add", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
            env=vde_agent_env(),
        )
    except (OSError, subprocess.SubprocessError):
        return None


def ssh_agent_is_running():
    """Check if VDE's own ssh-agent is running (never the user's agent)."""
    return vde_agent_is_running()


def ssh_agent_has_keys():
    """Check if VDE's own ssh-agent has any keys loaded (never the user's agent)."""
    result = _vde_agent_listing()
    return bool(result and result.returncode == 0 and result.stdout.strip())


def vde_agent_key_loaded(key=VDE_SSH_IDENTITY):
    """True if `key` (matched by fingerprint of its .pub) is loaded in VDE's agent."""
    result = _vde_agent_listing()
    if result is None or result.returncode != 0:
        return False
    pub = Path(f"{key}.pub")
    if not pub.exists():
        return False
    try:
        fingerprint = subprocess.run(
            ["ssh-keygen", "-lf", str(pub)], capture_output=True, text=True, timeout=5
        ).stdout.split()[1]
    except (OSError, subprocess.SubprocessError, IndexError):
        return False
    return fingerprint in result.stdout


def vde_agent_add_key():
    """Load the allowed key (vde_student) into VDE's agent, only if it is missing.

    Touches VDE's agent only and never starts one: starting it belongs to the
    VDE tooling (`vde ssh-setup start`, the spine check). Returns True if the
    key is loaded afterwards.
    """
    if not vde_agent_is_running() or not VDE_SSH_IDENTITY.exists():
        return False
    if vde_agent_key_loaded(VDE_SSH_IDENTITY):
        return True
    try:
        subprocess.run(
            ["ssh-add", str(VDE_SSH_IDENTITY)],
            capture_output=True,
            timeout=10,
            env=vde_agent_env(),
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return vde_agent_key_loaded(VDE_SSH_IDENTITY)


def get_ssh_keys():
    """Get the allowed VDE SSH keys in ~/.ssh/vde/ (VDE isolated, fixed set)."""
    keys = []
    if VDE_SSH_DIR.exists():
        for key_type in VDE_ALLOWED_KEYS:
            if (VDE_SSH_DIR / key_type).exists():
                keys.append(str(VDE_SSH_DIR / key_type))
            if (VDE_SSH_DIR / f"{key_type}.pub").exists():
                keys.append(str(VDE_SSH_DIR / f"{key_type}.pub"))
    return keys


def ssh_config_contains(pattern):
    """Check if VDE SSH config contains a pattern."""
    if VDE_SSH_CONFIG.exists():
        try:
            content = VDE_SSH_CONFIG.read_text()
            return pattern in content
        except Exception:
            return False
    return False


def ssh_config_get_host_entry(host):
    """Get host entry from VDE SSH config."""
    if VDE_SSH_CONFIG.exists():
        try:
            content = VDE_SSH_CONFIG.read_text()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip() == f"Host {host}":
                    # Return the host entry
                    entry = [line]
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith((" ", "\t")):
                            break
                        entry.append(lines[j])
                    return "\n".join(entry)
        except Exception as e:
            if os.environ.get("VDE_DEBUG_TESTS") == "1":
                print(f"[DEBUG] SSH agent check failed: {e}")
            return False
    return None


def public_ssh_keys_count():
    """Count .pub files in public-ssh-keys/."""
    public_dir = VDE_ROOT / "public-ssh-keys"
    if public_dir.exists():
        try:
            return len(list(public_dir.glob("*.pub")))
        except Exception:
            return 0
    return 0


def known_hosts_contains(pattern):
    """Check if VDE known_hosts contains a pattern."""
    if VDE_SSH_KNOWN_HOSTS.exists():
        try:
            content = VDE_SSH_KNOWN_HOSTS.read_text()
            return pattern in content
        except Exception:
            return False
    return False


def has_ssh_keys():
    """Check if VDE has any SSH keys."""
    return VDE_SSH_IDENTITY.exists()


def vm_has_private_keys(vm_name):
    """Check if a VM container has private SSH keys.

    This is a security verification - VDE design keeps SSH keys on the host
    and forwards them via SSH agent, not copied into containers.

    Args:
        vm_name: Name of the VM to check

    Returns:
        True if private keys are found in the VM, False otherwise
    """
    # Determine container name (language VMs use vde- prefix)
    container_name = f"vde-{vm_name}"

    # If container doesn't exist with -dev suffix, try plain name
    if not container_exists(container_name):
        container_name = vm_name
        if not container_exists(container_name):
            # Container not running, can't check
            return False

    try:
        # Check for private keys in container's /home/devuser/.ssh location
        # (This is a security check to ensure no private keys were copied into the VM)
        private_key_patterns = [
            "vde_student",
            "vde_student_sk",
            "id_rsa",
            "id_ecdsa",
            "id_dsa",
            "id_ecdsa_sk",
        ]

        for key_name in private_key_patterns:
            # Use the orchestrator for high-fidelity proof (Rule 1 & 15)
            result = run_vde_command(f"exec {vm_name} 'test -f /home/devuser/.ssh/{key_name} && echo FOUND'")

            if result.returncode == 0 and "FOUND" in result.stdout:
                return True  # Private key found

        # Also check /home/devuser/.ssh/ if devuser is the user
        result = run_vde_command(f"exec {vm_name} 'test -d /home/devuser/.ssh && echo EXISTS'")

        if result.returncode == 0 and "EXISTS" in result.stdout:
            for key_name in private_key_patterns:
                result = run_vde_command(f"exec {vm_name} 'test -f /home/devuser/.ssh/{key_name} && echo FOUND'")

                if result.returncode == 0 and "FOUND" in result.stdout:
                    return True

    except Exception:
        # If check fails, assume no keys (fail safe)
        pass

    return False


# =============================================================================
# VDE and Docker Helper Functions
# =============================================================================
