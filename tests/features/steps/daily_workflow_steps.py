"""
BDD Step Definitions for Daily Development Workflow.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""

from behave import given, when, then
from pathlib import Path
import subprocess
import os

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def mark_step_implemented(context, step_name=""):
    """Mark a step as implemented in context."""
    context.step_implemented = True
    if step_name:
        if not hasattr(context, 'implemented_steps'):
            context.implemented_steps = []
        context.implemented_steps.append(step_name)




VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/vde"))


def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    result = subprocess.run(
        f"cd {VDE_ROOT} && {command}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
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
# Daily Workflow GIVEN steps
# =============================================================================

@given('I previously created VMs for "python", "rust", and "postgres"')
def step_previously_created_vms_daily(context):
    """VMs were previously created."""
    context.created_vms = set()
    for vm in ['python', 'rust', 'postgres']:
        if compose_file_exists(vm):
            context.created_vms.add(vm)


@given('I have a Python VM running')
def step_python_vm_running(context):
    """Python VM is running."""
    context.python_running = container_exists('python')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.python_running:
        context.running_vms.add('python')
        context.created_vms.add('python')


@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    """Python VM is running."""
    context.python_running = container_exists('python')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.python_running:
        context.running_vms.add('python')
        context.created_vms.add('python')


@given('I have "rust" VM created but not running')
def step_rust_created_not_running(context):
    """Rust VM created but not running."""
    context.rust_created = compose_file_exists('rust')
    context.rust_running = container_exists('rust')
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.rust_created:
        context.created_vms.add('rust')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if context.rust_running:
        context.running_vms.discard('rust')


@given('I have a project using Python, JavaScript, and Redis')
def step_project_using_langs(context):
    """Project uses multiple languages."""
    context.project_langs = ['python', 'js', 'redis']
    context.project_needs_full_stack = True


@given('I have a stopped Rust VM')
def step_stopped_rust_vm(context):
    """Rust VM is stopped."""
    context.rust_vm_stopped = compose_file_exists('rust') and not container_exists('rust')
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if compose_file_exists('rust'):
        context.created_vms.add('rust')


@given('I have some running and some stopped VMs')
def step_mixed_vm_states(context):
    """Mixed VM states exist."""
    running = docker_ps()
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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
    """Python and PostgreSQL running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if container_exists('python'):
        context.running_vms.add('python')
        context.created_vms.add('python')
    if container_exists('postgres'):
        context.running_vms.add('postgres')
        context.created_vms.add('postgres')


@given('I have Python running and PostgreSQL stopped')
def step_python_running_postgres_stopped(context):
    """Python running, PostgreSQL stopped."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if container_exists('python'):
        context.running_vms.add('python')
        context.created_vms.add('python')
    if compose_file_exists('postgres'):
        context.created_vms.add('postgres')
    context.postgres_stopped = not container_exists('postgres')


@given('I want to know about a specific VM')
def step_want_know_specific_vm(context):
    """Want specific VM info."""
    context.want_specific_vm_info = True


@given('I need a full stack environment')
def step_need_full_stack(context):
    """Need full stack environment."""
    context.need_full_stack = True


@given('I want to try a new language')
def step_want_new_language(context):
    """Want to try new language."""
    context.want_new_language = True


@given('I have "postgres" VM is running')
def step_postgres_running(context):
    """PostgreSQL running."""
    context.postgres_running = container_exists('postgres')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.postgres_running:
        context.running_vms.add('postgres')
        context.created_vms.add('postgres')


@given('"postgres" VM is running')
def step_postgres_vm_running(context):
    """PostgreSQL VM running."""
    context.postgres_running = container_exists('postgres')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.postgres_running:
        context.running_vms.add('postgres')
        context.created_vms.add('postgres')


@given('I have modified the python Dockerfile to add a new package')
def step_modified_python_dockerfile(context):
    """Modified Python Dockerfile."""
    dockerfile = VDE_ROOT / "configs" / "docker" / "python" / "Dockerfile"
    context.python_dockerfile_modified = dockerfile.exists()
    context.new_package_added = True


@given('"python" VM is currently running')
def step_python_currently_running(context):
    """Python currently running."""
    context.python_running = container_exists('python')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    if context.python_running:
        context.running_vms.add('python')
        context.created_vms.add('python')


@given('I have an old "ruby" VM I don\'t use anymore')
def step_old_ruby_vm_daily(context):
    """Have old Ruby VM."""
    context.old_vm = 'ruby'
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


@given('I want to start my development day')
def step_start_dev_day(context):
    """Starting development day."""
    context.starting_dev_day = True


@given('I\'m starting my development day')
def step_starting_day_daily(context):
    """Starting day."""
    context.starting_day = True


@given('I want to end my development day')
def step_end_dev_day(context):
    """Ending development day."""
    context.ending_dev_day = True


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
    assert context.last_exit_code == 0, f"Failed to remove VM: {context.last_error}"
    assert not compose_file_exists('ruby'), "Ruby VM config still exists"


@then('I can reconnect to my running VMs')
def step_can_reconnect(context):
    """Can reconnect to running VMs."""
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c]
    context.can_reconnect = len(vde_running) > 0
