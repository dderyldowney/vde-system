"""
BDD Hooks for VDE test scenarios.

Hooks are special functions that run at specific points during test execution.
This file is automatically discovered by behave.
"""

import os
import subprocess
import sys

# Import shared configuration
# environment.py is in tests/features/, config.py is in tests/features/steps/
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT

# =============================================================================
# HELPER FUNCTIONS
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


def reset_cache_to_valid_state():
    """
    Reset cache files to a valid state by regenerating them.

    This ensures each cache scenario starts with a clean, valid cache
    rather than inheriting corrupted state from previous scenarios.
    """
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Remove any potentially corrupted cache files
    cache_file = cache_dir / "vm-types.cache"
    port_registry = cache_dir / "port-registry"

    # Delete if they contain invalid markers
    for cache_path in [cache_file, port_registry]:
        if cache_path.exists():
            try:
                content = cache_path.read_text()
                if "INVALID" in content or "CORRUPTED" in content:
                    cache_path.unlink()
            except Exception:
                # If we can't read it, delete it
                cache_path.unlink()

    # Regenerate valid cache by running list-vms
    result = run_vde_command("./scripts/list-vms", timeout=30)
    return result.returncode == 0


# =============================================================================
# DOCKER STATE EVALUATION
# =============================================================================

def get_current_docker_state():
    """
    Evaluate the current Docker state for VDE containers.

    Returns a dict with:
    - running: set of container names that are running
    - created: set of container names that exist but are stopped
    - all: set of all VDE container names
    """
    running = set()
    created = set()

    # Use ./scripts/vde ps to get running containers
    result = run_vde_command("./scripts/vde ps")
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('='):
                # Parse VDE ps output format
                parts = line.split()
                if parts:
                    container_name = parts[0]
                    running.add(container_name)

    # Use ./scripts/vde list to get all created VMs
    result = run_vde_command("./scripts/vde list")
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('='):
                parts = line.split()
                if parts:
                    container_name = parts[0]
                    if container_name not in running:
                        created.add(container_name)

    return {
        'running': running,
        'created': created,
        'all': running | created
    }


def ensure_vm_exists(vm_name):
    """
    Ensure a VM/container exists (created or running).
    Creates it if necessary using ./scripts/vde create.
    """
    state = get_current_docker_state()
    container_name = _get_container_name(vm_name)

    if container_name in state['all']:
        return True  # Already exists

    # Check if env file exists
    env_file = VDE_ROOT / "env-files" / f"{vm_name}.env"
    if not env_file.exists():
        # Env file missing - can't create VM without it
        import warnings
        warnings.warn(f"Env file missing: {env_file} - cannot create {vm_name} VM")
        return False

    # Use VDE create command
    result = run_vde_command(f"./scripts/vde create {vm_name}")
    return result.returncode == 0


def ensure_vm_running(vm_name):
    """
    Ensure a VM/container is running.
    Creates it first if necessary, then starts it using ./scripts/vde start.
    """
    state = get_current_docker_state()
    container_name = _get_container_name(vm_name)

    if container_name in state['running']:
        return True  # Already running

    # Ensure it exists first
    ensure_vm_exists(vm_name)

    # Use VDE start command
    result = run_vde_command(f"./scripts/vde start {vm_name}")
    return result.returncode == 0


def ensure_vm_stopped(vm_name):
    """
    Ensure a VM/container is stopped.
    Uses ./scripts/vde stop.
    """
    state = get_current_docker_state()
    container_name = _get_container_name(vm_name)

    if container_name not in state['running']:
        return True  # Already stopped

    # Use VDE stop command
    result = run_vde_command(f"./scripts/vde stop {vm_name}")
    return result.returncode == 0


def _get_container_name(vm_name):
    """
    Get the container name for a VM.

    Language VMs get '-dev' suffix, service VMs keep their name.
    """
    _SERVICE_VMS = {
        'redis', 'postgres', 'mongodb', 'mysql', 'nginx',
        'rabbitmq', 'couchdb', 'couchdb'
    }
    if vm_name in _SERVICE_VMS:
        return vm_name
    return f"{vm_name}-dev"


# =============================================================================
# SCENARIO SETUP
# =============================================================================

# VMs that are commonly needed for tests
_COMMON_TEST_VMS = {
    'python', 'rust', 'go', 'js', 'redis', 'postgres'
}

# Define VM requirements for each scenario
_SCENARIO_REQUIREMENTS = {
    "Start my daily development VMs": {
        'create': ['python', 'rust', 'postgres'],
        'start': ['python', 'rust', 'postgres'],
    },
    "Create a new language VM for a project": {
        'create': [],  # go should NOT exist - tests creation
        'start': [],
    },
    "Switch from Python to Rust project": {
        'create': ['python', 'rust'],
        'start': ['python'],  # Python running
        'stop': ['rust'],      # Rust stopped
    },
    "Connect to PostgreSQL from Python VM": {
        'create': ['postgres', 'python'],
        'start': ['postgres', 'python'],
    },
    "Shut down all VMs at end of day": {
        'create': ['python', 'rust'],
        'start': ['python', 'rust'],  # VMs should be running to test shutdown
    },
    "Run multiple language VMs for a polyglot project": {
        'create': ['python', 'js', 'redis'],
        'start': ['python', 'js', 'redis'],
    },
    "Rebuild a VM after modifying its Dockerfile": {
        'create': ['python'],
        'start': ['python'],
    },
    "Remove VM I no longer need": {
        'create': ['ruby'],  # Ruby should exist but not running
        'start': [],
    },
    "Add support for a new language": {
        'create': [],  # zig should NOT exist - tests adding new language
        'start': [],
    },
    "Check what VMs I can create": {
        'create': [],
        'start': [],
    },
    "Quickly check what's running": {
        'create': ['python', 'rust'],
        'start': [],  # Just list, no specific state needed
    },
    "Create test environment with database": {
        'create': ['postgres', 'redis', 'python'],
        'start': ['postgres', 'redis', 'python'],
    },
    "VDE handles port conflicts gracefully": {
        'create': ['python'],  # Create but don't start (tests port allocation)
        'start': [],
    },
}


def _setup_scenario_environment(scenario_name):
    """
    Set up the Docker environment for a specific scenario.

    This function:
    1. Gets current Docker state
    2. Determines what's needed for the scenario
    3. Creates any missing VMs
    4. Adjusts VM states (start/stop) as needed
    """
    # Find matching scenario requirements
    requirements = None
    for pattern, reqs in _SCENARIO_REQUIREMENTS.items():
        if pattern in scenario_name:
            requirements = reqs
            break

    if requirements is None:
        # No specific requirements, ensure common VMs exist
        for vm in _COMMON_TEST_VMS:
            ensure_vm_exists(vm)
        return

    # Create required VMs
    for vm in requirements.get('create', []):
        ensure_vm_exists(vm)

    # Stop VMs that should not be running
    for vm in requirements.get('stop', []):
        ensure_vm_stopped(vm)

    # Start VMs that should be running
    for vm in requirements.get('start', []):
        ensure_vm_running(vm)


# =============================================================================
# SCENARIO HOOKS
# =============================================================================

def before_scenario(context, scenario):
    """
    Hook that runs before each scenario.

    This hook:
    1. Evaluates the current Docker state
    2. Sets up the environment for daily-workflow scenarios
    3. Resets cache for cache-system scenarios
    """
    # Set up daily-workflow environment
    if scenario.feature.name == "Daily Development Workflow":
        _setup_scenario_environment(scenario.name)

    # Only reset cache for cache-system feature scenarios
    if scenario.feature.name == "Cache System":
        # Skip reset for scenarios that set up specific cache states
        scenario_steps = [step.name for step in scenario.steps]

        # Don't reset if the scenario tests invalid cache regeneration
        if "cache file exists with invalid format" in scenario_steps:
            return

        # Reset for all other scenarios to prevent pollution
        reset_cache_to_valid_state()


def after_scenario(context, scenario):
    """
    Hook that runs after each scenario.

    This hook cleans up any temporary files created during testing,
    such as invalid compose files used for error handling tests,
    and removes any test-created containers (labeled with vde.test=true).
    """
    # Clean up invalid compose test directory if it was created
    import shutil
    invalid_compose_dir = VDE_ROOT / "configs" / "docker" / "invalid-test"
    if invalid_compose_dir.exists():
        try:
            shutil.rmtree(invalid_compose_dir)
        except Exception:
            pass  # Best effort cleanup

    # Clean up test-created containers (labeled with vde.test=true)
    # This ensures tests don't leave orphaned containers and don't affect user's VMs
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            test_containers = [c for c in result.stdout.strip().split('\n') if c]
            for container in test_containers:
                # Force remove the test container
                subprocess.run(
                    ["docker", "rm", "-f", container],
                    capture_output=True, timeout=10
                )
    except Exception:
        pass  # Docker may not be available, that's OK


def after_feature(context, feature):
    """
    Hook that runs after each feature.

    For docker-operations feature, stop the python and postgres VMs that were
    started in the Background section to clean up after tests.
    """
    if feature.name == "Docker Operations":
        # Stop python VM using VDE
        run_vde_command("./scripts/vde stop python")
        # Stop postgres VM using VDE
        run_vde_command("./scripts/vde stop postgres")
