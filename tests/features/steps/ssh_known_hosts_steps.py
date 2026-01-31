"""
BDD Step definitions for SSH known_hosts File Management scenarios.

These steps test automatic cleanup of known_hosts entries when VMs are
removed or recreated, preventing "host key changed" warnings.
All steps use real system verification.
"""
import os
import subprocess

# Import shared configuration
import sys
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

# Import SSH helpers
from ssh_helpers import run_vde_command

from config import VDE_ROOT

# =============================================================================
# SSH known_hosts Cleanup Steps - Prevents "host key changed" warnings
# These steps test automatic cleanup of known_hosts entries when VMs are removed
# =============================================================================

@given('~/.ssh/known_hosts contains entry for "{pattern}"')
def step_known_hosts_contains_entry(context, pattern):
    """Setup: Add a known_hosts entry for testing."""
    known_hosts = Path.home() / ".ssh" / "vde" / "known_hosts"
    known_hosts.parent.mkdir(parents=True, exist_ok=True)

    # Create a dummy host key entry for testing
    # Format: hostname ssh-keytype key
    if not known_hosts.exists():
        known_hosts.write_text("")

    content = known_hosts.read_text()
    # Add a test entry if not already present
    if pattern not in content:
        # Create a fake but valid-looking entry
        test_entry = f"{pattern} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA test-key-for-vde-testing\n"
        known_hosts.write_text(content + test_entry)

    context.test_known_hosts_pattern = pattern


@given('~/.ssh/known_hosts contains "{hostname}" hostname entry')
def step_known_hosts_contains_hostname(context, hostname):
    """Setup: Add a hostname entry to known_hosts."""
    known_hosts = Path.home() / ".ssh" / "vde" / "known_hosts"
    known_hosts.parent.mkdir(parents=True, exist_ok=True)

    if not known_hosts.exists():
        known_hosts.write_text("")

    content = known_hosts.read_text()
    if hostname not in content:
        test_entry = f"{hostname} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA test-key-for-vde-testing\n"
        known_hosts.write_text(content + test_entry)


@given('~/.ssh/known_hosts contains multiple port entries')
def step_known_hosts_multiple_entries(context):
    """Setup: Add multiple port entries to known_hosts."""
    known_hosts = Path.home() / ".ssh" / "vde" / "known_hosts"
    known_hosts.parent.mkdir(parents=True, exist_ok=True)

    content = ""
    if known_hosts.exists():
        content = known_hosts.read_text()

    # Add test entries for multiple ports
    entries = [
        "[localhost]:2200 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA test-key-2200\n",
        "[localhost]:2400 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA test-key-2400\n",
    ]

    for entry in entries:
        if entry.split()[0] not in content:
            content += entry

    known_hosts.write_text(content)


@given('~/.ssh/known_hosts exists with content')
def step_known_hosts_exists(context):
    """Setup: Create known_hosts with test content."""
    known_hosts = Path.home() / ".ssh" / "vde" / "known_hosts"
    known_hosts.parent.mkdir(parents=True, exist_ok=True)
    known_hosts.write_text("localhost ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA test-content\n")


@given('~/.ssh/known_hosts does not exist')
def step_known_hosts_not_exists(context):
    """Setup: Ensure known_hosts doesn't exist."""
    known_hosts = Path.home() / ".ssh" / "vde" / "known_hosts"
    # Backup if exists, then remove
    if known_hosts.exists():
        context.known_hosts_backup = known_hosts.read_text()
        known_hosts.unlink()
