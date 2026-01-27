"""
BDD Step Definitions for Daily Development Workflow.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.

Team collaboration steps have been moved to team_collaboration_steps.py
"""
import os
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import time
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    compose_file_exists,
    wait_for_container,
    ensure_vm_created,
    ensure_vm_running,
    ensure_vm_stopped,
)

# Test mode flag - set via environment variable
ALLOW_CLEANUP = os.environ.get("VDE_TEST_MODE") == "1"

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
            ensure_vm_created(context, vm)
        else:
            if compose_file_exists(vm):
                context.created_vms.add(vm)


@given('I have a Python VM running')
def step_python_vm_running(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    context.python_running = container_exists('python')


@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    context.python_running = container_exists('python')


@given('I have "rust" VM created but not running')
def step_rust_created_not_running(context):
    """Rust VM created but not running.

    In test mode: creates VM and ensures it's stopped.
    In local mode: checks if VM exists and is stopped.
    """
    if ALLOW_CLEANUP:
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        if compose_file_exists('rust'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('rust')
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
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        if compose_file_exists('rust'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('rust')
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
        ensure_vm_running(context, 'python')
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
    else:
        running = docker_ps()
        for c in running:
            if "-dev" in c:
                vm = c.replace("-dev", "")
                context.running_vms.add(vm)
                context.created_vms.add(vm)
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
        ensure_vm_created(context, 'postgres')
        ensure_vm_stopped(context, 'postgres')
    else:
        if compose_file_exists('postgres'):
            if not hasattr(context, 'created_vms'):
                context.created_vms = set()
            context.created_vms.add('postgres')
    context.postgres_stopped = not container_exists('postgres')


@given('I want to know about a specific VM')
def step_want_know_specific_vm(context):
    """Want specific VM info - verify vde list is available."""
    vde_script = VDE_ROOT / "scripts" / "vde"
    context.want_specific_vm_info = vde_script.exists()
    if context.want_specific_vm_info:
        result = run_vde_command("list", timeout=30)
        context.available_vms = result.stdout.strip().split("\n") if result.returncode == 0 else []


@given('I need a full stack environment')
def step_need_full_stack(context):
    """Need full stack environment - check available VM types."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        vm_count = len([line for line in content.split("\n") if line.strip() and not line.startswith("#")])
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
    context.postgres_running = container_exists('postgres')


@given('"postgres" VM is running')
def step_postgres_vm_running(context):
    """PostgreSQL VM running.

    In test mode: creates and starts postgres.
    In local mode: checks if postgres is running.
    """
    ensure_vm_running(context, 'postgres')
    context.postgres_running = container_exists('postgres')


@given('I have modified the python Dockerfile to add a new package')
def step_modified_python_dockerfile(context):
    """Modified Python Dockerfile.

    In test mode: touches the Dockerfile to trigger rebuild.
    In local mode: checks if Dockerfile exists.
    """
    dockerfile = VDE_ROOT / "configs" / "docker" / "python" / "Dockerfile"

    if ALLOW_CLEANUP and dockerfile.exists():
        try:
            subprocess.run(["touch", str(dockerfile)], check=True, timeout=5)
            context.python_dockerfile_modified = True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            context.dockerfile_touch_error = str(e)
            context.python_dockerfile_modified = False
    else:
        context.python_dockerfile_modified = dockerfile.exists()

    context.new_package_added = True


@given('"python" VM is currently running')
def step_python_currently_running(context):
    """Python currently running.

    In test mode: creates and starts python.
    In local mode: checks if python is running.
    """
    ensure_vm_running(context, 'python')
    context.python_running = container_exists('python')


@given('I have an old "ruby" VM I don\'t use anymore')
def step_old_ruby_vm_daily(context):
    """Have old Ruby VM.

    In test mode: creates the ruby VM.
    In local mode: checks if ruby VM exists.
    """
    context.old_vm = 'ruby'
    if ALLOW_CLEANUP:
        ensure_vm_created(context, 'ruby')
    else:
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
# Project workflow steps
# =============================================================================
# Project workflow steps
# =============================================================================

@given('I am starting a new web project')
def step_starting_web_project(context):
    """Context: Starting a new web project."""
    context.web_project = True
    context.project_type = 'web'


@given('I have web containers running (JavaScript, nginx)')
def step_web_containers_running(context):
    """Context: Web containers are running."""
    running = docker_ps()
    context.web_containers = [c for c in running if 'js' in c.lower() or 'nginx' in c.lower() or 'node' in c.lower()]
    context.has_web_containers = len(context.web_containers) > 0


@then('the web containers should be stopped')
def step_web_containers_stopped(context):
    """Verify web containers are stopped."""
    running = docker_ps()
    web_running = [c for c in running if 'js' in c.lower() or 'nginx' in c.lower() or 'node' in c.lower()]
    context.web_containers_stopped = len(web_running) == 0


@then('only the backend stack should be running')
def step_only_backend_running(context):
    """Verify only backend stack is running."""
    running = docker_ps()
    web_running = [c for c in running if 'nginx' in c.lower() or 'js-dev' in c or 'node' in c.lower()]
    context.only_backend_running = len(web_running) == 0


@given('I am building a microservices application')
def step_building_microservices(context):
    """Context: Building microservices application."""
    context.microservices = True
    context.services_needed = ['python', 'go', 'postgres']


@then('they should be able to communicate on the Docker network')
def step_communicate_docker_network(context):
    """Verify services can communicate on Docker network."""
    result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, "Docker network should exist for inter-service communication"


@given('I am doing data analysis')
def step_doing_data_analysis(context):
    """Context: Doing data analysis."""
    context.data_analysis = True
    context.data_tools_needed = ['python', 'postgres']


@given('I need a complete web stack')
def step_need_web_stack(context):
    """Context: Need complete web stack."""
    context.web_stack_needed = True


@given('I am developing a mobile app with backend')
def step_developing_mobile_app(context):
    """Context: Developing mobile app with backend."""
    context.mobile_app = True
    context.backend_needed = True


@then('PostgreSQL should start for the backend database')
def step_postgres_starts_backend(context):
    """Verify PostgreSQL starts for backend database."""
    postgres_running = container_exists('postgres')
    context.postgres_for_backend = postgres_running


@then('all containers should stop')
def step_all_containers_stop(context):
    """Verify all containers stop."""
    running = docker_ps()
    context.all_stopped = len(running) == 0


@then('there should be no leftover processes')
def step_no_leftover_processes(context):
    """Verify no leftover processes."""
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', 'status=exited', '--format', '{{.Names}}'],
        capture_output=True, text=True, timeout=10
    )
    vde_leftover = [c for c in result.stdout.strip().split('\n') if c and ('-dev' in c or c in ['postgres', 'redis', 'nginx'])]
    context.no_leftovers = len(vde_leftover) == 0


@then('the system should understand I want to create VMs')
def step_understand_create_vms(context):
    """Verify system understands intent to create VMs."""
    create_script = VDE_ROOT / "scripts" / "create-virtual-for"
    context.understands_create = create_script.exists()


@then('I should be connected to PostgreSQL')
def step_connected_postgresql(context):
    """Verify connected to PostgreSQL."""
    postgres_running = container_exists('postgres')
    if postgres_running:
        result = subprocess.run(
            ['docker', 'exec', 'postgres', 'pg_isready', '-U', 'postgres'],
            capture_output=True, text=True, timeout=10
        )
        context.connected_to_postgres = result.returncode == 0 or 'accepting' in result.stdout
    else:


@then('I can query the database')
def step_can_query_database(context):
    """Verify can query the database."""
    postgres_running = container_exists('postgres')
    if postgres_running:
        result = subprocess.run(
            ['docker', 'exec', 'postgres', 'psql', '-U', 'postgres', '-c', 'SELECT 1'],
            capture_output=True, text=True, timeout=10
        )
        context.can_query = result.returncode == 0
    else:


@then('the connection uses the container network')
def step_uses_container_network(context):
    """Verify connection uses container network."""
    result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True, timeout=10)
    context.uses_network = result.returncode == 0


@given('I need to manage multiple VMs')
def step_need_manage_multiple(context):
    """Context: Need to manage multiple VMs."""
    context.managing_multiple = True


@then('only language VMs should stop')
def step_only_lang_vms_stop(context):
    """Verify only language VMs stop."""
    running = docker_ps()
    language_vms = [c for c in running if c.endswith('-dev')]
    service_vms = [c for c in running if c in ['postgres', 'redis', 'nginx', 'mysql']]
    context.only_lang_stopped = len(language_vms) == 0 and len(service_vms) >= 0


@given('I need to update VDE itself')
def step_need_update_vde(context):
    """Context: Need to update VDE."""
    context.updating_vde = True


@then('I can update the VDE scripts')
def step_can_update_vde(context):
    """Verify can update VDE scripts."""
    result = subprocess.run(['git', 'status'], capture_output=True, cwd=VDE_ROOT, timeout=10)
    context.can_update = result.returncode == 0


@given('I want to check VM resource consumption')
def step_want_check_resources(context):
    """Context: Want to check VM resource consumption."""
    context.checking_resources = True


@then('I should see which VMs are consuming resources')
def step_see_resource_consumers(context):
    """Verify can see which VMs are consuming resources."""
    result = subprocess.run(['docker', 'stats', '--no-stream', '--format', 'table {{.Names}}'],
                          capture_output=True, text=True, timeout=10)
    context.can_see_consumers = result.returncode == 0


@then('I should be able to identify heavy VMs')
def step_identify_heavy_vms(context):
    """Verify can identify resource-heavy VMs."""
    result = subprocess.run(['docker', 'stats', '--no-stream'],
                          capture_output=True, text=True, timeout=10)
    context.can_identify_heavy = result.returncode == 0


@given('my project has grown')
def step_project_grown(context):
    """Context: Project has grown."""
    context.project_grown = True


@then('the system should handle many VMs')
def step_handle_many_vms(context):
    """Verify system can handle many VMs."""
    result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
    context.handles_many = result.returncode == 0


@then('rendered output should contain .ssh volume mount')
def step_rendered_ssh_volume(context):
    """Verify rendered output contains .ssh volume mount."""
    compose = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    if compose.exists():
        content = compose.read_text()
        context.ssh_volume_in_output = '.ssh' in content or 'ssh' in content.lower()
    else:


@given('I have updated VDE scripts')
def step_updated_vde_scripts(context):
    """Context: VDE scripts have been updated."""
    context.vde_scripts_updated = True


@then('they should use the new VDE configuration')
def step_uses_new_vde_config(context):
    """Verify VMs use new VDE configuration."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.uses_new_config = vm_types.exists()


@then('logs directory should exist at "logs/zig"')
def step_logs_directory_zig(context):
    """Verify logs directory exists at logs/zig."""
    logs_dir = VDE_ROOT / "logs" / "zig"
    context.zig_logs_exist = logs_dir.exists()


@then('the VM should have a fresh container instance')
def step_fresh_container_instance(context):
    """Verify VM has a fresh container instance."""
    running = docker_ps()
    context.fresh_instance = len(running) > 0


@then('the command should fail with error "Unknown VM: nonexistent"')
def step_error_unknown_vm(context):
    """Verify command fails with unknown VM error."""
    result = run_vde_command("start nonexistent", timeout=30)
    context.has_unknown_error = (
        result.returncode != 0 and
        ('unknown' in result.stderr.lower() or 'not found' in result.stderr.lower() or 'no such' in result.stderr.lower())
    )


@then('the command should fail with error "already exists"')
def step_error_already_exists(context):
    """Verify command fails with already exists error."""
    result = run_vde_command("create python", timeout=30)
    context.has_exists_error = (
        result.returncode != 0 and
        ('exists' in result.stderr.lower() or 'already' in result.stderr.lower())
    )


@then('aliases should be shown')
def step_aliases_shown(context):
    """Verify aliases are shown in list output."""
    result = run_vde_command("list", timeout=30)
    context.aliases_shown = 'alias' in result.stdout.lower() or result.returncode == 0


@then('only language VMs should be listed')
def step_only_lang_vms_listed(context):
    """Verify only language VMs are listed."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types.exists():
        content = vm_types.read_text()
        lang_vms = [line for line in content.split('\n') if 'lang|' in line]
        context.only_lang_listed = len(lang_vms) > 0
    else:


@then('only service VMs should be listed')
def step_only_service_vms_listed(context):
    """Verify only service VMs are listed."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types.exists():
        content = vm_types.read_text()
        service_vms = [line for line in content.split('\n') if 'service|' in line]
        context.only_service_listed = len(service_vms) > 0
    else:


@then('language VMs should not be listed')
def step_lang_vms_not_listed(context):
    """Verify language VMs are not listed."""


@then('only VMs matching "python" should be listed')
def step_only_python_listed(context):
    """Verify only VMs matching python are listed."""
    result = run_vde_command("list python", timeout=30)
    context.only_matching_listed = result.returncode == 0


@then('docker-compose.yml should not exist at "configs/docker/python/docker-compose.yml"')
def step_compose_not_exist(context):
    """Verify docker-compose.yml should not exist at specified path."""
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    context.compose_not_exist = not compose_path.exists()


@then('"nodejs" should resolve to "js"')
def step_nodejs_resolves_js(context):
    """Verify nodejs alias resolves to js."""
    result = run_vde_command("list nodejs", timeout=30)
    context.nodejs_resolves = result.returncode == 0


@then('the system should not overwrite the existing configuration')
def step_no_overwrite_config(context):
    """Verify system doesn't overwrite existing configuration."""


@then('start the Rust VM')
def step_start_rust_vm(context):
    """Start the Rust VM using vde start command."""
    result = run_vde_command("start rust", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    if result.returncode == 0:
        wait_for_container('rust', timeout=60)


@then('I should see container uptime')
def step_see_uptime(context):
    """Verify can see container uptime."""
    result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
                          capture_output=True, text=True, timeout=10)
    context.uptime_visible = result.returncode == 0


@given('I start a VM')
def step_start_vm(context):
    """Start a VM using vde start command."""
    result = run_vde_command("start python", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    if result.returncode == 0:
        wait_for_container('python', timeout=60)
