"""
SSH Helper Functions for VDE Test Steps.

This module provides shared utility functions for SSH verification
used across all SSH-related BDD step definitions.

All SSH operations now use VDE-specific isolated paths at ~/.ssh/vde/
"""
import subprocess
from pathlib import Path
import os


# Add steps directory to path for config import
import sys
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT


# VDE SSH Isolation - All SSH operations use these paths
VDE_SSH_DIR = Path.home() / ".ssh" / "vde"
VDE_SSH_CONFIG = VDE_SSH_DIR / "config"
VDE_SSH_KNOWN_HOSTS = VDE_SSH_DIR / "known_hosts"
VDE_SSH_IDENTITY = VDE_SSH_DIR / "id_ed25519"


# =============================================================================
# SSH Helper Functions for Real Verification
# =============================================================================

def ssh_agent_is_running():
    """Check if SSH agent is running."""
    try:
        result = subprocess.run(
            ["ssh-add", "-l"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 or "no identities" in result.stderr.lower()
    except Exception:
        return False


def ssh_agent_has_keys():
    """Check if SSH agent has any keys loaded."""
    try:
        result = subprocess.run(
            ["ssh-add", "-l"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 and result.stdout.strip()
    except Exception:
        return False


def get_ssh_keys():
    """Get list of SSH keys in ~/.ssh/vde/ (VDE isolated)."""
    keys = []
    if VDE_SSH_DIR.exists():
        for key_type in ["id_ed25519", "id_rsa", "id_ecdsa", "id_dsa"]:
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
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == f"Host {host}":
                    # Return the host entry
                    entry = [line]
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith((' ', '\t')):
                            break
                        entry.append(lines[j])
                    return '\n'.join(entry)
        except Exception:
            pass
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


# Test mode detection - ALLOW_CLEANUP indicates we can modify state
# When VDE_TEST_CLEANUP is not 'false', we allow cleanup operations
ALLOW_CLEANUP = os.environ.get('VDE_TEST_CLEANUP', 'true') != 'false'


# =============================================================================
# VDE and Docker Helper Functions
# =============================================================================

def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    result = subprocess.run(
        f"cd {VDE_ROOT} && {command}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def container_exists(vm_name):
    """Check if a container is running for the VM."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            containers = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            return f"{vm_name}-dev" in containers or vm_name in containers
    except Exception:
        pass
    return False


def vm_has_private_keys(vm_name):
    """Check if a VM container has private SSH keys in ~/.ssh/."""
    try:
        # Use docker exec to check for private keys in the VM
        result = subprocess.run(
            ["docker", "exec", f"{vm_name}-dev", "sh", "-c",
             "ls ~/.ssh/*.key ~/.ssh/id_* 2>/dev/null | grep -v '\\.pub$' || true"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # If output is not empty, private keys exist
        return bool(result.stdout.strip())
    except Exception:
        # If container doesn't exist or command fails, assume no keys
        return False
