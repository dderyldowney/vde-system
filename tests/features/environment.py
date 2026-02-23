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

# Add tests directory to path for config loader
tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

try:
    from test_config_loader import get_behave_config
except ImportError:
    # Fallback if not found
    def get_behave_config():
        return None

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
    vde_script = os.path.join(VDE_ROOT, "scripts", "vde")
    full_cmd = f"cd {VDE_ROOT} && {vde_script} {command}"
    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def run_vde_ps(args=None, timeout=30):
    """Run vde-ps and return the result."""
    vde_ps = os.path.join(VDE_ROOT, "scripts", "vde-ps")
    cmd = ["zsh", vde_ps]
    if args:
        cmd.extend(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=VDE_ROOT
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
    
    # Invalidate cache to ensure fresh load of new naming scheme
    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()
        print(f"[SETUP] Invalidated VM types cache at {cache_file}")

    # Load and validate configuration
    config = get_behave_config()
    if config:
        try:
            context.config_data = config.load(validate=True)
        except Exception as e:
            print(f"[CONFIG] Warning: Failed to load/validate config: {e}")
            context.config_data = {}
    
    # Ensure VDE_ROOT is set
    os.environ['VDE_ROOT_DIR'] = str(VDE_ROOT)
    os.environ['DOCKER_BUILDKIT'] = '0'
    
    # Set VDE_TEST_MODE to 1 to enable test-specific behavior in scripts
    os.environ['VDE_TEST_MODE'] = '1'
    
    # Use test network
    os.environ['VDE_NETWORK'] = 'vde-testing'

    # Cleanup any leftovers from previous aborted runs using vde commands
    print("[SETUP] Cleaning up any existing VDE test containers...")
    # Use vde ps to list all containers, then remove them
    result = run_vde_ps(["-a", "-q"])
    if result.returncode == 0:
        containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
        for container in containers:
            # Container names from vde-ps are like "vde-python", but vde commands
            # expect VM names like "python". Strip the vde- prefix.
            vm_name = container.replace('vde-', '') if container.startswith('vde-') else container
            run_vde_command(f"remove {vm_name}", timeout=30)
            print(f"[SETUP] Removed container: {container}")
    
    # Create test network using vde init
    run_vde_command("init", timeout=30)


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
    
    # Stop and remove all test containers created during this run using vde commands
    try:
        result = run_vde_ps(["-a", "-q"])
        if result.returncode == 0:
            containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
            for container in containers:
                # Container names from vde-ps are like "vde-python", but vde commands
                # expect VM names like "python". Strip the vde- prefix.
                vm_name = container.replace('vde-', '') if container.startswith('vde-') else container
                print(f"[TEARDOWN] Stopping VM: {vm_name}")
                run_vde_command(f"stop {vm_name}", timeout=30)
                print(f"[TEARDOWN] Removing VM: {vm_name}")
                run_vde_command(f"remove {vm_name}", timeout=30)
    except Exception as e:
        print(f"[TEARDOWN] Error during container cleanup: {e}")

    # Remove test network - use docker directly for this as vde doesn't have network remove
    subprocess.run(["docker", "network", "rm", "vde-testing"], capture_output=True)
    
    # Stop SSH agent if started
    _stop_ssh_agent()
    
    print("[TEARDOWN] Test suite teardown complete.")
