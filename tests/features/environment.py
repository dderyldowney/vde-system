"""
BDD Hooks for VDE test scenarios.

Hooks are special functions that run at specific points during test execution.
This file is automatically discovered by behave.

Lifecycle:
1. before_all: Docker availability check, VDE root verification, initial cache reset
2. before_scenario: Set up environment for each scenario
3. after_scenario: Clean up test-created containers (labeled with vde.test=true)
4. after_feature: Stop VMs started for feature testing
5. after_all: Full cleanup - stop all test VMs, clean test artifacts
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

# Track test VMs created during test run for cleanup
_TEST_VMS_CREATED = set()
_TEST_CONTAINERS_CREATED = set()

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
    if result.returncode == 0:
        # Track this VM for cleanup
        _TEST_VMS_CREATED.add(vm_name)
        print(f"[SETUP] Created test VM: {vm_name}")
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
    if result.returncode == 0:
        # Track this VM as started during testing
        if vm_name not in _TEST_VMS_CREATED:
            _TEST_VMS_CREATED.add(vm_name)
        print(f"[SETUP] Started test VM: {vm_name}")
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

    This hook:
    1. Cleans up any temporary files created during testing
    2. Removes any test-created containers (labeled with vde.test=true)
    3. Tracks containers for cleanup in after_all
    """
    # Clean up invalid compose test directory if it was created
    import shutil
    invalid_compose_dir = VDE_ROOT / "configs" / "docker" / "invalid-test"
    if invalid_compose_dir.exists():
        try:
            shutil.rmtree(invalid_compose_dir)
        except Exception:
            pass  # Best effort cleanup

    # Collect test-created containers for cleanup tracking
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            test_containers = [c for c in result.stdout.strip().split('\n') if c]
            for container in test_containers:
                _TEST_CONTAINERS_CREATED.add(container)
    except Exception:
        pass  # Docker may not be available, that's OK


def after_feature(context, feature):
    """
    Hook that runs after each feature.

    Stops VMs that were started specifically for this feature's tests.
    """
    # Stop VMs started for this feature
    for vm in _TEST_VMS_CREATED:
        run_vde_command(f"./scripts/vde stop {vm}")


def before_all(context):
    """
    Hook that runs once before any tests execute.

    This hook:
    1. Verifies Docker is available and running
    2. Verifies VDE root directory exists
    3. Ensures cache directories are valid
    4. Reports initial Docker state
    """
    import pathlib

    # Verify Docker is available
    try:
        docker_result = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if docker_result.returncode != 0:
            raise RuntimeError("Docker is not available or not installed")
        print(f"[SETUP] Docker available: {docker_result.stdout.strip()}")
    except FileNotFoundError:
        raise RuntimeError("Docker command not found - install Docker to run tests")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Docker check timed out")

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
        raise RuntimeError("Docker info check timed out - daemon may be unresponsive")

    # Verify VDE root directory
    if not VDE_ROOT.exists():
        raise RuntimeError(f"VDE root directory not found: {VDE_ROOT}")
    print(f"[SETUP] VDE root: {VDE_ROOT}")

    # Verify scripts directory
    scripts_dir = VDE_ROOT / "scripts"
    if not scripts_dir.exists():
        raise RuntimeError(f"Scripts directory not found: {scripts_dir}")
    print(f"[SETUP] Scripts directory: {scripts_dir}")

    # Ensure cache directory exists
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"[SETUP] Cache directory: {cache_dir}")

    # Reset cache to valid state at start
    reset_cache_to_valid_state()
    print("[SETUP] Cache reset to valid state")

    # Get initial Docker state
    initial_state = get_current_docker_state()
    print(f"[SETUP] Initial Docker state: {len(initial_state['running'])} running, {len(initial_state['created'])} created")


def after_all(context):
    """
    Hook that runs once after all tests complete.

    This hook performs full cleanup:
    1. Stops all VMs created during testing
    2. Removes all test-labeled containers
    3. Cleans up any test artifacts
    4. Reports final Docker state
    """
    print("\n[CLEANUP] Starting full test cleanup...")

    # Stop all VMs created during testing
    for vm in _TEST_VMS_CREATED:
        try:
            result = run_vde_command(f"./scripts/vde stop {vm}")
            if result.returncode == 0:
                print(f"[CLEANUP] Stopped VM: {vm}")
            else:
                print(f"[CLEANUP] Failed to stop {vm}: {result.stderr}")
        except Exception as e:
            print(f"[CLEANUP] Error stopping {vm}: {e}")

    # Remove all test-labeled containers
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
                        ["docker", "rm", "-f", container],
                        capture_output=True, timeout=10
                    )
                    print(f"[CLEANUP] Removed container: {container}")
                except Exception as e:
                    print(f"[CLEANUP] Error removing {container}: {e}")
    except Exception as e:
        print(f"[CLEANUP] Error querying test containers: {e}")

    # Clean up any test networks
    try:
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", "label=vde.test=true", "--format", "{{.Name}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            test_networks = [n for n in result.stdout.strip().split('\n') if n]
            for network in test_networks:
                try:
                    subprocess.run(
                        ["docker", "network", "rm", network],
                        capture_output=True, timeout=10
                    )
                    print(f"[CLEANUP] Removed network: {network}")
                except Exception as e:
                    print(f"[CLEANUP] Error removing network {network}: {e}")
    except Exception as e:
        print(f"[CLEANUP] Error querying test networks: {e}")

    # Clean up test directories
    test_dirs = ["invalid-test"]
    for test_dir in test_dirs:
        test_path = VDE_ROOT / "configs" / "docker" / test_dir
        if test_path.exists():
            try:
                import shutil
                shutil.rmtree(test_path)
                print(f"[CLEANUP] Removed test directory: {test_path}")
            except Exception as e:
                print(f"[CLEANUP] Error removing {test_path}: {e}")

    # Get final Docker state
    final_state = get_current_docker_state()
    print(f"[CLEANUP] Final Docker state: {len(final_state['running'])} running, {len(final_state['created'])} created")
    print("[CLEANUP] Test cleanup complete")


# Helper function to track test VMs (call this from scenario setup)
def _track_test_vm(vm_name):
    """Track a VM as created during testing for later cleanup."""
    _TEST_VMS_CREATED.add(vm_name)
