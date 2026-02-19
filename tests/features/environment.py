"""
BDD Hooks for VDE test scenarios.

Lifecycle:
1. before_all: Verify Docker and VDE setup
2. before_feature: Start SSH agent if needed
3. before_scenario: Set up environment for each scenario
4. after_all: Final cleanup of all VDE test resources
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT

# Track test VMs created during test run for cleanup
_TEST_VMS_CREATED = set()

# Track SSH agent PID started by tests
_SSH_AGENT_PID = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    # Disable BuildKit as requested by user for this environment
    env['DOCKER_BUILDKIT'] = '0'
    full_cmd = f"cd {VDE_ROOT} && {command}"
    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def _start_ssh_agent():
    """Start a local SSH agent and return the PID and socket."""
    global _SSH_AGENT_PID
    
    # Check if SSH agent is already running
    result = subprocess.run(
        ["ssh-add", "-l"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode in (0, 1):  # 0 = has keys, 1 = no keys but agent running
        return True
    
    # Start a new SSH agent
    result = subprocess.run(
        ["ssh-agent", "-s"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode != 0:
        return False
    
    # Parse the output to get PID and socket
    for line in result.stdout.split('\n'):
        if line.startswith('SSH_AUTH_SOCK='):
            socket = line.split('=')[1].split(';')[0]
            os.environ['SSH_AUTH_SOCK'] = socket
        elif line.startswith('SSH_AGENT_PID='):
            pid = line.split('=')[1].split(';')[0]
            _SSH_AGENT_PID = int(pid)
            os.environ['SSH_AGENT_PID'] = pid
    
    return True


def _stop_ssh_agent():
    """Stop the SSH agent if it was started by tests."""
    global _SSH_AGENT_PID
    
    if _SSH_AGENT_PID is not None:
        try:
            os.kill(_SSH_AGENT_PID, 0)
            subprocess.run(["kill", str(_SSH_AGENT_PID)], capture_output=True, timeout=10)
            _SSH_AGENT_PID = None
        except Exception:
            _SSH_AGENT_PID = None


def _get_container_name(vm_name):
    """Get the container name for a VM."""
    return f"vde-{vm_name}"


# =============================================================================
# LIFECYCLE HOOKS
# =============================================================================

def before_all(context):
    """Initial setup before any tests run."""
    # Ensure VDE_ROOT is set
    os.environ['VDE_ROOT_DIR'] = str(VDE_ROOT)
    os.environ['DOCKER_BUILDKIT'] = '0'
    
    # Set VDE_TEST_MODE to 1 to enable test-specific behavior in scripts
    os.environ['VDE_TEST_MODE'] = '1'
    
    # Use test network
    os.environ['VDE_NETWORK'] = 'vde-testing'

    # Cleanup any leftovers from previous aborted runs
    print("[SETUP] Cleaning up any existing VDE test containers...")
    subprocess.run(
        "docker ps -a --filter label=vde.test=true -q | xargs -r docker rm -f",
        shell=True, capture_output=True
    )
    
    # Create test network
    subprocess.run(["docker", "network", "create", "vde-testing"], capture_output=True)


def before_feature(context, feature):
    """Hook that runs before each feature."""
    # Start SSH agent for SSH-related features
    if "ssh" in feature.name.lower() or "ssh" in feature.filename.lower():
        _start_ssh_agent()


def before_scenario(context, scenario):
    """Hook that runs before each scenario."""
    # Reset context for each scenario
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0


def after_all(context):
    """Final teardown after ALL tests have completed."""
    
    # Support conditional cleanup via environment variable
    if os.environ.get('KEEP_VMS') == 'true':
        print("[TEARDOWN] KEEP_VMS is true. Skipping resource cleanup.")
        return

    print("[TEARDOWN] Final cleanup of VDE test resources...")
    
    # Stop and remove all test containers created during this run
    # We use the vde.test label to identify them
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
            for container in containers:
                subprocess.run(["docker", "stop", container], capture_output=True, timeout=10)
                subprocess.run(["docker", "rm", "-f", container], capture_output=True, timeout=10)
                print(f"[TEARDOWN] Removed container: {container}")
    except Exception as e:
        print(f"[TEARDOWN] Error during container cleanup: {e}")

    # Remove test network
    subprocess.run(["docker", "network", "rm", "vde-testing"], capture_output=True)
    
    # Stop SSH agent if started
    _stop_ssh_agent()
    
    print("[TEARDOWN] Test suite teardown complete.")
