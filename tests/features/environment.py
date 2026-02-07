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

    # Create config files if container doesn't exist at all
    if container_name not in state['all']:
        result = run_vde_command(f"./scripts/vde create {vm_name} --label vde.test=true")
        if result.returncode != 0:
            print(f"[ERROR] Failed to create {vm_name}: {result.stderr}")
            return False
        _TEST_VMS_CREATED.add(vm_name)
        print(f"[SETUP] Created VM: {vm_name}")

    # Start the VM (this handles both newly created and previously stopped containers)
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
    # Handle multi-project-workflow feature
    if "multi-project-workflow" in scenario.feature.filename:
        _setup_multi_project_scenario(scenario.name)
        return


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

    # Verify VDE root directory
    if not VDE_ROOT.exists():
        raise RuntimeError(f"VDE root directory not found: {VDE_ROOT}")
    print(f"[SETUP] VDE root: {VDE_ROOT}")

    # Verify scripts directory
    scripts_dir = VDE_ROOT / "scripts"
    if not scripts_dir.exists():
        raise RuntimeError(f"Scripts directory not found: {scripts_dir}")
    print(f"[SETUP] Scripts directory: {scripts_dir}")

    # Report initial Docker state
    state = get_current_docker_state()
    print(f"[SETUP] Initial Docker state: {len(state['running'])} running, {len(state['created'])} created")
