"""
BDD Hooks for VDE test scenarios.

Lifecycle:
1. before_all: Verify Docker and VDE setup
2. before_scenario: Set up environment for each scenario
3. after_scenario: Clean up temporary files
4. after_feature: Remove test containers
"""

import os
import subprocess
import sys
import time

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
        print("[SETUP] SSH agent already running")
        return True
    
    # Start a new SSH agent
    result = subprocess.run(
        ["ssh-agent", "-s"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode != 0:
        print(f"[SETUP] Failed to start SSH agent: {result.stderr}")
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
    
    print(f"[SETUP] Started SSH agent (PID: {_SSH_AGENT_PID}, Socket: {os.environ.get('SSH_AUTH_SOCK', 'unknown')})")
    return True


def _stop_ssh_agent():
    """Stop the SSH agent if it was started by tests."""
    global _SSH_AGENT_PID
    
    if _SSH_AGENT_PID is not None:
        try:
            os.kill(_SSH_AGENT_PID, 0)  # Check if process exists
            subprocess.run(
                ["kill", str(_SSH_AGENT_PID)],
                capture_output=True,
                timeout=10
            )
            print(f"[TEARDOWN] Stopped SSH agent (PID: {_SSH_AGENT_PID})")
            _SSH_AGENT_PID = None
        except (OSError, subprocess.TimeoutExpired):
            print(f"[TEARDOWN] SSH agent (PID: {_SSH_AGENT_PID}) already stopped")
            _SSH_AGENT_PID = None
    else:
        # Check if there's an SSH agent from the environment
        agent_pid = os.environ.get('SSH_AGENT_PID')
        if agent_pid:
            try:
                pid_int = int(agent_pid)
                os.kill(pid_int, 0)
                # Process exists - kill it
                subprocess.run(
                    ["kill", agent_pid],
                    capture_output=True,
                    timeout=10
                )
                print(f"[TEARDOWN] Stopped SSH agent from environment (PID: {agent_pid})")
            except (ValueError, OSError):
                pass  # Process doesn't exist


def get_current_docker_state():
    """Evaluate the current Docker state for VDE containers."""
    running = set()
    created = set()

    # Use docker ps to get running containers
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    running.add(line.strip())
    except Exception:
        pass

    # Use docker ps -a to get all containers
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip() and line.strip() not in running:
                    created.add(line.strip())
    except Exception:
        pass

    return {
        'running': running,
        'created': created,
        'all': running | created
    }


def _get_container_name(vm_name):
    """Get the container name for a VM."""
    _SERVICE_VMS = {
        'redis', 'postgres', 'mongodb', 'mysql', 'nginx',
        'rabbitmq', 'couchdb'
    }
    if vm_name in _SERVICE_VMS:
        return vm_name
    return f"{vm_name}-dev"


def ensure_vm_exists(vm_name):
    """Ensure a VM/container exists and is running."""
    container_name = _get_container_name(vm_name)
    state = get_current_docker_state()

    if container_name in state['running']:
        return True  # Already running

    # If container exists but is stopped, just start it
    if container_name in state['created']:
        result = subprocess.run(
            ["docker", "start", container_name],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"[ERROR] Failed to start {container_name}: {result.stderr}")
            return False
        time.sleep(2)
        print(f"[SETUP] Started existing VM: {vm_name}")
        return True

    # Create config files if container doesn't exist at all
    result = run_vde_command(f"./scripts/vde create {vm_name} --label vde.test=true")
    if result.returncode != 0:
        print(f"[ERROR] Failed to create {vm_name}: {result.stderr}")
        return False
    _TEST_VMS_CREATED.add(vm_name)
    print(f"[SETUP] Created VM: {vm_name}")

    # Start the newly created VM
    result = run_vde_command(f"./scripts/vde start {vm_name}")
    if result.returncode != 0:
        print(f"[ERROR] Failed to start {vm_name}: {result.stderr}")
        return False

    # Allow Docker to register the container as running
    time.sleep(2)

    print(f"[SETUP] Started VM: {vm_name}")
    return True


def ensure_vm_running(vm_name):
    """Ensure a VM/container is running."""
    container_name = _get_container_name(vm_name)
    state = get_current_docker_state()

    if container_name in state['running']:
        return True

    return ensure_vm_exists(vm_name)


# =============================================================================
# FEATURE-SPECIFIC VM REQUIREMENTS
# =============================================================================

# VMs needed for each docker-required feature
# These VMs will be started before scenarios in these features run
_FEATURE_VM_REQUIREMENTS = {
    # VM lifecycle tests - need python, rust, postgres for various scenarios
    "vm-lifecycle": ['python', 'rust', 'postgres'],
    
    # Docker operations tests - need running containers to test operations
    "docker-operations": ['python', 'postgres'],
    
    # SSH agent forwarding VM-to-VM tests - need language + service VMs
    "ssh-agent-forwarding-vm-to-vm": ['python', 'go', 'postgres', 'redis'],
    
    # SSH agent automatic setup tests
    "ssh-agent-automatic-setup": ['python'],
    
    # SSH external git operations
    "ssh-agent-external-git-operations": ['python', 'go'],
    
    # SSH and remote access tests
    "ssh-and-remote-access": ['python', 'go'],
    
    # VM-to-host communication tests
    "ssh-agent-vm-to-host-communication": ['python', 'go'],
    
    # Error handling tests - need various VMs
    "error-handling-and-recovery": ['python', 'postgres', 'redis'],
    
    # Daily development workflow tests
    "daily-development-workflow": ['python', 'postgres'],
}


def _setup_feature_vms(feature_name, scenario_name):
    """Set up VMs for a given feature and scenario."""
    # Check if this feature has VM requirements
    feature_key = None
    for key in _FEATURE_VM_REQUIREMENTS:
        if key in feature_name.lower():
            feature_key = key
            break
    
    if not feature_key:
        return
    
    required_vms = _FEATURE_VM_REQUIREMENTS.get(feature_key, [])
    if not required_vms:
        return
    
    print(f"[SETUP] Setting up VMs for feature: {feature_name}")
    print(f"[SETUP] VMs: {required_vms}")
    
    # Ensure all required VMs exist and are running
    for vm in required_vms:
        ensure_vm_running(vm)


# =============================================================================
# MULTI-PROJECT WORKFLOW SCENARIO REQUIREMENTS
# =============================================================================

# Define VM requirements for multi-project-workflow feature.
# Scenarios with "I have" GIVEN steps need VMs pre-created before the scenario runs.
_MULTI_PROJECT_REQUIREMENTS = {
    "Setting up a web development project": ['js', 'nginx'],
    "Setting up a microservices architecture": ['go', 'rust', 'nginx'],
    "Data science project setup": ['python', 'r'],
    "Full stack web application": ['python', 'postgres', 'redis', 'nginx'],
    "Mobile development with backend": ['flutter', 'postgres'],
}

# Workflow scenarios that need pre-creation (they have "I have" GIVEN steps)
# These scenarios expect VMs/containers to exist before they run
_WORKFLOW_SCENARIOS = {
    "Switching from web to backend project": ['js', 'nginx', 'python', 'postgres'],
    "New Project Setup - Start Development Stack": ['python', 'postgres'],
    "Starting all microservices at once": ['go', 'rust', 'nginx'],
    "Cleaning up between projects": [],  # No pre-creation needed, just cleanup
}

# Scenarios that have "I have" GIVEN steps - these need VMs created before scenario
_WORKFLOW_GIVEN_SCENARIOS = {
    "Switching from web to backend project",
    "New Project Setup - Start Development Stack",
    "Starting all microservices at once",
}


def _setup_multi_project_scenario(scenario_name):
    """Set up VMs for multi-project-workflow scenarios."""
    # Check if this is a workflow scenario that needs pre-creation
    if scenario_name in _WORKFLOW_SCENARIOS:
        required_vms = _WORKFLOW_SCENARIOS.get(scenario_name, [])
        if required_vms:
            print(f"[SETUP] Pre-creating for workflow scenario: {scenario_name}")
            print(f"[SETUP] VMs: {required_vms}")
            # Create and start required VMs
            for vm in required_vms:
                ensure_vm_exists(vm)
            return
        else:
            # Scenario like "Cleaning up between projects" - no pre-creation needed
            print(f"[SETUP] Skipping (cleanup scenario): {scenario_name}")
            return

    required_vms = _MULTI_PROJECT_REQUIREMENTS.get(scenario_name, [])
    if not required_vms:
        return

    print(f"[SETUP] Setting up: {scenario_name}")
    print(f"[SETUP] VMs: {required_vms}")

    # Stop any running VDE containers first to ensure clean state
    state = get_current_docker_state()
    for container in state['running']:
        try:
            subprocess.run(
                ["docker", "stop", container],
                capture_output=True, timeout=10
            )
            print(f"[SETUP] Stopped: {container}")
        except Exception:
            pass

    # Ensure all required VMs are running
    for vm in required_vms:
        ensure_vm_running(vm)


# =============================================================================
# SCENARIO HOOKS
# =============================================================================

def before_scenario(context, scenario):
    """Hook that runs before each scenario."""
    # Skip @wip scenarios (work in progress)
    if 'wip' in scenario.tags:
        print(f"[SKIP] Skipping @wip scenario: {scenario.name}")
        scenario.skip("Marked as @wip")
        return
    
    # Handle multi-project-workflow feature
    if "multi-project-workflow" in scenario.feature.filename:
        _setup_multi_project_scenario(scenario.name)
        return
    
    # Handle other docker-required features - auto-start VMs
    if "docker-required" in scenario.feature.filename:
        _setup_feature_vms(scenario.feature.name, scenario.name)
        return


def before_feature(context, feature):
    """Hook that runs before each feature."""
    # Start SSH agent for SSH-related features
    if "vde-ssh" in feature.filename or "ssh-agent" in feature.filename:
        _start_ssh_agent()


def after_feature(context, feature):
    """Hook that runs after each feature."""
    # Stop SSH agent for SSH-related features
    if "vde-ssh" in feature.filename or "ssh-agent" in feature.filename:
        _stop_ssh_agent()
    
    # Remove test-created containers


def after_scenario(context, scenario):
    """Hook that runs after each scenario."""
    pass


def after_feature(context, feature):
    """Hook that runs after each feature."""
    # Remove test-created containers
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            test_containers = [c for c in result.stdout.strip().split('\n') if c]
            for container in test_containers:
                try:
                    subprocess.run(
                        ["docker", "stop", container],
                        capture_output=True, timeout=10
                    )
                    subprocess.run(
                        ["docker", "rm", "-v", container],
                        capture_output=True, timeout=10
                    )
                    print(f"[CLEANUP] Removed: {container}")
                except Exception as e:
                    print(f"[CLEANUP] Error removing {container}: {e}")
    except Exception:
        pass


def before_all(context):
    """Hook that runs once before any tests execute."""
    # Verify Docker is available
    try:
        docker_result = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if docker_result.returncode != 0:
            raise RuntimeError("Docker is not available")
        print(f"[SETUP] Docker available: {docker_result.stdout.strip()}")
    except FileNotFoundError:
        raise RuntimeError("Docker command not found")

    # Verify Docker daemon is running
    try:
        docker_ps = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=30
        )
        if docker_ps.returncode != 0:
            raise RuntimeError("Docker daemon is not running")
        print("[SETUP] Docker daemon is running")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Docker check timed out")

    # CLEANUP: Remove any existing containers before starting tests
    print("[SETUP] Cleaning up any existing containers...")
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        containers = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
        if containers:
            print(f"[SETUP] Found {len(containers)} existing containers to remove")
            for container in containers:
                subprocess.run(["docker", "stop", container], capture_output=True, timeout=30)
                subprocess.run(["docker", "rm", "-f", container], capture_output=True, timeout=30)
                print(f"[SETUP] Removed existing container: {container}")
        else:
            print("[SETUP] No existing containers to clean up")

    # Verify VDE root directory
    if not VDE_ROOT.exists():
        raise RuntimeError(f"VDE root directory not found: {VDE_ROOT}")
    print(f"[SETUP] VDE root: {VDE_ROOT}")

    # Verify scripts directory
    scripts_dir = VDE_ROOT / "scripts"
    if not scripts_dir.exists():
        raise RuntimeError(f"Scripts directory not found: {scripts_dir}")
    print(f"[SETUP] Scripts directory: {scripts_dir}")

    # Restore critical config files if missing
    _restore_config_files()

    # Report initial Docker state
    state = get_current_docker_state()
    print(f"[SETUP] Initial Docker state: {len(state['running'])} running, {len(state['created'])} created")


def _restore_config_files():
    """Generate all config files using the generate-all-configs script."""
    import shutil

    generate_script = VDE_ROOT / "scripts" / "generate-all-configs"

    if not generate_script.exists():
        print("[SETUP] ERROR: generate-all-configs script not found")
        return

    print("[SETUP] Running generate-all-configs to create env-files and configs...")

    result = subprocess.run(
        ["zsh", str(generate_script)],
        cwd=VDE_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode == 0:
        print("[SETUP] ✓ Generated all config files")
    else:
        print(f"[SETUP] ✗ Failed to generate configs: {result.stderr}")
        if result.stdout:
            print(f"[SETUP] STDOUT: {result.stdout}")


# =============================================================================
# TEARDOWN HOOKS
# =============================================================================

def after_all(context):
    """Final cleanup: remove all VDE test containers."""
    print("[TEARDOWN] Cleaning up all VDE test containers...")

    # Get all VDE containers (both running and stopped)
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            containers = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
            if containers:
                print(f"[TEARDOWN] Found {len(containers)} containers to remove")
                # Stop and remove all containers
                for container in containers:
                    # Stop if running
                    subprocess.run(
                        ["docker", "stop", container],
                        capture_output=True,
                        timeout=30,
                    )
                    # Remove the container
                    subprocess.run(
                        ["docker", "rm", "-f", container],
                        capture_output=True,
                        timeout=30,
                    )
                    print(f"[TEARDOWN] Removed container: {container}")
            else:
                print("[TEARDOWN] No containers to clean up")
        else:
            print(f"[TEARDOWN] Error listing containers: {result.stderr}")
    except Exception as e:
        print(f"[TEARDOWN] Error during cleanup: {e}")

    # Verify no containers remain
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        remaining = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
        if remaining:
            print(f"[TEARDOWN] WARNING: {len(remaining)} containers still remain")
        else:
            print("[TEARDOWN] ✓ All containers removed successfully")
    except Exception:
        pass

    print("[TEARDOWN] Test suite cleanup complete")
