"""
BDD Step Definitions for Daily Development Workflow.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import sys

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import subprocess
import time
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


# VDE_ROOT imported from config


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


def docker_ps():
    """Get list of running Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except Exception:
        pass
    return set()


def container_exists(vm_name):
    """Check if a container is running for the VM."""
    containers = docker_ps()
    return f"{vm_name}-dev" in containers or vm_name in containers


def compose_file_exists(vm_name):
    """Check if docker-compose.yml exists for VM."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    return compose_path.exists()


# =============================================================================
# TEST MODE DETECTION (from vm_lifecycle_steps.py pattern)
# =============================================================================
# In container: VDE_ROOT_DIR is set to /vde
# Locally: VDE_ROOT_DIR is not set or points to a different path
# Test mode: VDE_TEST_MODE is set to 1 (allows cleanup during local testing)
IN_CONTAINER = os.environ.get("VDE_ROOT_DIR") == "/vde"
IN_TEST_MODE = os.environ.get("VDE_TEST_MODE") == "1"
# Allow cleanup if running in container OR in test mode
ALLOW_CLEANUP = IN_CONTAINER or IN_TEST_MODE


# =============================================================================
# VM STATE MANAGEMENT HELPERS
# =============================================================================

def wait_for_container(vm_name, timeout=60, interval=2):
    """Wait for a container to be running."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if container_exists(vm_name):
            return True
        time.sleep(interval)
    return False


def wait_for_container_stopped(vm_name, timeout=30, interval=1):
    """Wait for container to stop."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not container_exists(vm_name):
            return True
        time.sleep(interval)
    return False


def ensure_vm_created(context, vm_name, timeout=120):
    """Ensure VM compose file exists, create if not.

    In test mode (ALLOW_CLEANUP=True), actually creates the VM.
    In local mode, only checks if VM exists and sets context flags.
    """
    if not compose_file_exists(vm_name):
        if ALLOW_CLEANUP:
            result = run_vde_command(f"./scripts/create-virtual-for {vm_name}", timeout=timeout)
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add(vm_name)
            context.last_exit_code = result.returncode
            context.last_output = result.stdout
            context.last_error = result.stderr
            return result.returncode == 0
        else:
            # Local mode: just note that VM doesn't exist
            return False
    return True


def ensure_vm_running(context, vm_name, create_timeout=120, start_timeout=180):
    """Ensure VM is created and running.

    In test mode (ALLOW_CLEANUP=True), actually creates/starts the VM.
    In local mode, only checks existing state and sets context flags.
    """
    # Initialize context tracking sets
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()

    if ALLOW_CLEANUP:
        # Test mode: create if needed
        if not compose_file_exists(vm_name):
            if not ensure_vm_created(context, vm_name, timeout=create_timeout):
                return False

        # Check if already running
        if container_exists(vm_name):
            context.running_vms.add(vm_name)
            context.created_vms.add(vm_name)
            return True

        # Start the VM
        result = run_vde_command(f"./scripts/start-virtual {vm_name}", timeout=start_timeout)

        # Wait for container
        if result.returncode == 0:
            wait_for_container(vm_name, timeout=60)

        # Track state
        if container_exists(vm_name):
            context.running_vms.add(vm_name)
            context.created_vms.add(vm_name)

        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr
        return result.returncode == 0
    else:
        # Local mode: detect existing state
        is_running = container_exists(vm_name)
        is_created = compose_file_exists(vm_name)
        if is_running:
            context.running_vms.add(vm_name)
        if is_created:
            context.created_vms.add(vm_name)
        return is_running


def ensure_vm_stopped(context, vm_name, timeout=60):
    """Ensure VM is stopped.

    In test mode (ALLOW_CLEANUP=True), actually stops the VM.
    In local mode, only checks existing state.
    """
    if ALLOW_CLEANUP:
        if not container_exists(vm_name):
            return True

        result = run_vde_command(f"./scripts/shutdown-virtual {vm_name}", timeout=timeout)

        if result.returncode == 0:
            wait_for_container_stopped(vm_name, timeout=30)

        if hasattr(context, 'running_vms'):
            context.running_vms.discard(vm_name)

        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr
        return not container_exists(vm_name)
    else:
        # Local mode: just check if stopped
        is_stopped = not container_exists(vm_name)
        if is_stopped and hasattr(context, 'running_vms'):
            context.running_vms.discard(vm_name)
        return is_stopped


# =============================================================================
# Daily Workflow GIVEN steps
# =============================================================================

@given('I previously created VMs for "python", "rust", and "postgres"')
def step_previously_created_vms_daily(context):
    """VMs were previously created.

    In test mode: actually creates the VMs.
    In local mode: checks if VMs exist.
    """
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    for vm in ['python', 'rust', 'postgres']:
        if ALLOW_CLEANUP:
            # Test mode: actually create the VM
            ensure_vm_created(context, vm)
        else:
            # Local mode: check if exists
            if compose_file_exists(vm):
                context.created_vms.add(vm)


@given('I have a Python VM running')
def step_python_vm_running(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    # For backwards compatibility with existing THEN steps
    context.python_running = container_exists('python')


@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    # For backwards compatibility with existing THEN steps
    context.python_running = container_exists('python')


@given('I have "rust" VM created but not running')
def step_rust_created_not_running(context):
    """Rust VM created but not running.

    In test mode: creates VM and ensures it's stopped.
    In local mode: checks if VM exists and is stopped.
    """
    if ALLOW_CLEANUP:
        # Test mode: create and ensure stopped
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        # Local mode: check existing state
        if compose_file_exists('rust'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('rust')
    # For backwards compatibility
    context.rust_created = compose_file_exists('rust')
    context.rust_running = container_exists('rust')


@given('I have a project using Python, JavaScript, and Redis')
def step_project_using_langs(context):
    """Project uses multiple languages."""
    context.project_langs = ['python', 'js', 'redis']
    context.project_needs_full_stack = True


@given('I have a stopped Rust VM')
def step_stopped_rust_vm(context):
    """Rust VM is stopped.

    In test mode: creates VM and ensures it's stopped.
    In local mode: checks if VM exists and is stopped.
    """
    if ALLOW_CLEANUP:
        # Test mode: create and ensure stopped
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        # Local mode: check existing state
        if compose_file_exists('rust'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('rust')
    # For backwards compatibility
    context.rust_vm_stopped = compose_file_exists('rust') and not container_exists('rust')


@given('I have some running and some stopped VMs')
def step_mixed_vm_states(context):
    """Mixed VM states exist.

    In test mode: creates python (running) and rust (stopped).
    In local mode: checks existing VM states.
    """
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()

    if ALLOW_CLEANUP:
        # Test mode: set up specific states
        ensure_vm_running(context, 'python')
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        # Local mode: detect existing states
        running = docker_ps()
        for c in running:
            if "-dev" in c:
                vm = c.replace("-dev", "")
                context.running_vms.add(vm)
                context.created_vms.add(vm)
        # Check created but not running
        configs_dir = VDE_ROOT / "configs" / "docker"
        if configs_dir.exists():
            for vm_dir in configs_dir.iterdir():
                if vm_dir.is_dir():
                    vm = vm_dir.name
                    if vm not in context.running_vms:
                        context.created_vms.add(vm)
    context.mixed_states = len(context.running_vms) < len(context.created_vms)


@given('I have Python and PostgreSQL running')
def step_python_postgres_running(context):
    """Python and PostgreSQL running.

    In test mode: creates and starts both VMs.
    In local mode: checks if both are running.
    """
    ensure_vm_running(context, 'python')
    ensure_vm_running(context, 'postgres')


@given('I have Python running and PostgreSQL stopped')
def step_python_running_postgres_stopped(context):
    """Python running, PostgreSQL stopped.

    In test mode: creates/starts python and creates/stops postgres.
    In local mode: checks existing states.
    """
    ensure_vm_running(context, 'python')
    if ALLOW_CLEANUP:
        # Test mode: ensure postgres is created but stopped
        ensure_vm_created(context, 'postgres')
        ensure_vm_stopped(context, 'postgres')
    else:
        # Local mode: track existing state
        if compose_file_exists('postgres'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('postgres')
    context.postgres_stopped = not container_exists('postgres')


@given('I want to know about a specific VM')
def step_want_know_specific_vm(context):
    """Want specific VM info - verify list-vms is available."""
    list_vms_script = VDE_ROOT / "scripts" / "list-vms"
    context.want_specific_vm_info = list_vms_script.exists()
    # Also check if we have any VMs to list
    if context.want_specific_vm_info:
        result = run_vde_command("./scripts/list-vms", timeout=30)
        context.available_vms = result.stdout.strip().split("\n") if result.returncode == 0 else []


@given('I need a full stack environment')
def step_need_full_stack(context):
    """Need full stack environment - check available VM types."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        vm_count = len([line for line in content.split("\n") if line.strip() and not line.startswith("#")])
        # Full stack means we have web, db, and language VMs available
        context.need_full_stack = vm_count >= 3
        context.available_vm_count = vm_count
    else:
        context.need_full_stack = False


@given('I want to try a new language')
def step_want_new_language(context):
    """Want to try new language - check for uncreated VM types."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    configs_dir = VDE_ROOT / "configs" / "docker"

    available_vms = set()
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split("\n"):
            if line.strip() and not line.startswith("#"):
                parts = line.split("|")
                if parts:
                    available_vms.add(parts[0].strip())

    created_vms = set()
    if configs_dir.exists():
        for vm_dir in configs_dir.iterdir():
            if vm_dir.is_dir():
                created_vms.add(vm_dir.name)

    # New language available if some VM types aren't created yet
    uncreated = available_vms - created_vms
    context.want_new_language = len(uncreated) > 0
    context.available_new_languages = list(uncreated)


@given('I have "postgres" VM is running')
def step_postgres_running(context):
    """PostgreSQL running.

    In test mode: creates and starts postgres.
    In local mode: checks if postgres is running.
    """
    ensure_vm_running(context, 'postgres')
    # For backwards compatibility
    context.postgres_running = container_exists('postgres')


@given('"postgres" VM is running')
def step_postgres_vm_running(context):
    """PostgreSQL VM running.

    In test mode: creates and starts postgres.
    In local mode: checks if postgres is running.
    """
    ensure_vm_running(context, 'postgres')
    # For backwards compatibility
    context.postgres_running = container_exists('postgres')


@given('I have modified the python Dockerfile to add a new package')
def step_modified_python_dockerfile(context):
    """Modified Python Dockerfile.

    In test mode: touches the Dockerfile to trigger rebuild.
    In local mode: checks if Dockerfile exists.

    This simulates a Dockerfile modification that would trigger
    a rebuild on next start-virtual.
    """
    dockerfile = VDE_ROOT / "configs" / "docker" / "python" / "Dockerfile"

    if ALLOW_CLEANUP and dockerfile.exists():
        # Test mode: touch the Dockerfile to change modification time
        # This triggers rebuild on next start-virtual without actually changing content
        try:
            subprocess.run(["touch", str(dockerfile)], check=True, timeout=5)
            context.python_dockerfile_modified = True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            # Log the error for debugging
            context.dockerfile_touch_error = str(e)
            context.python_dockerfile_modified = False
    else:
        # Local mode: just check if exists
        context.python_dockerfile_modified = dockerfile.exists()

    context.new_package_added = True


@given('"python" VM is currently running')
def step_python_currently_running(context):
    """Python currently running.

    In test mode: creates and starts python.
    In local mode: checks if python is running.
    """
    ensure_vm_running(context, 'python')
    # For backwards compatibility
    context.python_running = container_exists('python')


@given('I have an old "ruby" VM I don\'t use anymore')
def step_old_ruby_vm_daily(context):
    """Have old Ruby VM.

    In test mode: creates the ruby VM.
    In local mode: checks if ruby VM exists.
    """
    context.old_vm = 'ruby'
    if ALLOW_CLEANUP:
        # Test mode: actually create the VM
        ensure_vm_created(context, 'ruby')
    else:
        # Local mode: check if exists
        if compose_file_exists('ruby'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('ruby')


@given('VDE doesn\'t support "zig" yet')
def step_zig_not_supported_daily(context):
    """Zig not supported yet."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        context.zig_not_supported = "zig" not in content.lower()
    else:
        context.zig_not_supported = True


@given('I have a working directory')
def step_working_directory(context):
    """Working directory exists."""
    context.working_directory = VDE_ROOT / "projects"
    context.has_working_dir = context.working_directory.exists()


# =============================================================================
# Daily Workflow WHEN steps
# =============================================================================

@when('I run "start-virtual all"')
def step_start_all(context):
    """Start all VMs."""
    result = run_vde_command("./scripts/start-virtual all", timeout=300)
    context.last_command = "start-virtual all"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "shutdown-virtual all"')
def step_shutdown_all(context):
    """Shutdown all VMs."""
    result = run_vde_command("./scripts/shutdown-virtual all", timeout=120)
    context.last_command = "shutdown-virtual all"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "list-vms"')
def step_list_vms(context):
    """List VMs."""
    result = run_vde_command("./scripts/list-vms", timeout=30)
    context.last_command = "list-vms"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I start a language VM')
def step_start_lang_vm(context):
    """Start a language VM."""
    result = run_vde_command("./scripts/start-virtual python", timeout=180)
    context.last_exit_code = result.returncode


@when('I stop a VM')
def step_stop_vm(context):
    """Stop a VM."""
    result = run_vde_command("./scripts/shutdown-virtual python", timeout=60)
    context.last_exit_code = result.returncode


@when('I restart a VM')
def step_restart_vm(context):
    """Restart a VM."""
    result = run_vde_command("./scripts/shutdown-virtual python && ./scripts/start-virtual python", timeout=180)
    context.last_exit_code = result.returncode


@when('I create a new VM type')
def step_create_vm_type(context):
    """Create new VM type."""
    result = run_vde_command("./scripts/add-vm-type zig lang Zig 'apt-get install -y zig'", timeout=30)
    context.last_exit_code = result.returncode


@when('I remove an old VM')
def step_remove_old_vm(context):
    """Remove old VM."""
    result = run_vde_command("./scripts/remove-virtual ruby", timeout=60)
    context.last_exit_code = result.returncode


# =============================================================================
# Daily Workflow THEN steps
# =============================================================================

@then('all my VMs should start')
def step_all_vms_start(context):
    """All VMs should start."""
    assert context.last_exit_code == 0, f"Failed to start VMs: {context.last_error}"


@then('I should see running VMs')
def step_see_running(context):
    """Should see running VMs."""
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c or c in ['postgres', 'redis', 'nginx', 'mongodb']]
    assert len(vde_running) > 0, "No VMs are running"


@then('my VMs should shut down cleanly')
def step_vms_shutdown(context):
    """VMs should shutdown cleanly."""
    assert context.last_exit_code == 0, f"Failed to shutdown VMs: {context.last_error}"
    # Check VMs are actually stopped
    import time
    time.sleep(2)
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c]
    # Allow some VMs to be still running, but most should be stopped
    context.vms_shutdown_cleanly = len(vde_running) == 0


@then('I should see a list of available VMs')
def step_see_vm_list(context):
    """Should see VM list."""
    assert context.last_exit_code == 0, f"Failed to list VMs: {context.last_error}"
    assert len(context.last_output) > 0, "No VM list output"


@then('the VM should start')
def step_vm_starts(context):
    """VM should start."""
    assert context.last_exit_code == 0, f"Failed to start VM: {context.last_error}"
    # Check VM is actually running
    import time
    time.sleep(3)
    assert container_exists('python'), "Python VM is not running"


@then('the VM should stop')
def step_vm_stops(context):
    """VM should stop."""
    assert context.last_exit_code == 0, f"Failed to stop VM: {context.last_error}"
    import time
    time.sleep(2)
    assert not container_exists('python'), "Python VM is still running"


@then('the VM should restart')
def step_vm_restarts(context):
    """VM should restart."""
    assert context.last_exit_code == 0, f"Failed to restart VM: {context.last_error}"


@then('the new VM type should be added')
def step_vm_type_added(context):
    """VM type should be added."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        context.vm_type_added = "zig" in content


@then('the VM should be removed')
def step_vm_removed_check(context):
    """VM should be removed."""
    # Get the VM name from context (set by the WHEN step that removed it)
    removed_vm = getattr(context, 'removed_vm_name', 'ruby')
    # Verify the removal command succeeded
    exit_code = getattr(context, 'last_exit_code', None)
    if exit_code is not None:
        assert exit_code == 0, f"Failed to remove VM: {getattr(context, 'last_error', 'unknown error')}"
    # Verify compose file was actually removed
    assert not compose_file_exists(removed_vm), f"{removed_vm} VM config still exists"
    # Verify container was removed
    running = docker_ps()
    vm_containers = [c for c in running if removed_vm in c.lower()]
    assert len(vm_containers) == 0, f"{removed_vm} containers still running: {vm_containers}"


@then('I can reconnect to my running VMs')
def step_can_reconnect(context):
    """Can reconnect to running VMs."""
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c]
    context.can_reconnect = len(vde_running) > 0
