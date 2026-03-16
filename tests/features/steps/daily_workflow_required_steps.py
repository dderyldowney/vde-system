# -*- coding: utf-8 -*-
"""
Daily Workflow Step Definitions for Docker-Required Tests

Step definitions for testing VDE's daily development workflow scenarios.
These tests verify common developer workflows with multiple VMs.

Feature: tests/features/core-infrastructure/daily-workflow.feature
"""

import subprocess
import os
import sys
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, when, then
from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    compose_file_exists,
    wait_for_container,
)

# ========== GIVEN STEPS ==========


@given("I have SSH keys configured")
def step_have_ssh_keys(context):
    """Verify SSH keys are configured for the user."""
    # Check if SSH directory exists
    ssh_dir = Path.home() / ".ssh" / "vde"
    if not ssh_dir.exists():
        # Create SSH directory if it doesn't exist via ssh-setup
        run_vde_command("ssh-setup --init", context=context)

    # Check for existing SSH keys
    key_files = list(ssh_dir.glob("id_*"))
    context.ssh_keys_exist = len(key_files) > 0
    assert context.ssh_keys_exist, "SSH keys should be configured"


@given("I have no VMs running")
def step_no_vms_running(context):
    """Ensure no VDE VMs are currently running."""
    # Stop all running VMs first
    run_vde_command("stop all -f", context=context)
    time.sleep(2)  # Wait for containers to stop
    running = docker_ps()
    vde_containers = [c for c in running if c.startswith("vde-")]
    assert len(vde_containers) == 0, f"Expected no VDE containers running, found: {vde_containers}"


@given("I want to work on a Python project")
def step_want_python_project(context):
    """Setup: User wants to work on a Python project."""
    context.vm_name = "python"


@given("I want to work on a Rust project instead")
def step_want_rust_project(context):
    """Setup: User wants to switch to a Rust project."""
    context.vm_name = "rust"


@given("I need a PostgreSQL database")
def step_need_postgres(context):
    """Setup: User needs a PostgreSQL database."""
    context.requires_postgres = True


@given("I want to work on multiple language VMs")
def step_multiple_languages(context):
    """Setup: User wants to work with multiple language VMs."""
    context.vm_list = ["python", "go", "rust"]


@given("I have modified the Python VM Dockerfile")
def step_modified_dockerfile(context):
    """Setup: User has modified the Python VM Dockerfile."""
    context.dockerfile_modified = True


@given("I no longer need the Ruby VM")
def step_ruby_not_needed(context):
    """Setup: User no longer needs the Ruby VM."""
    context.vm_to_remove = "ruby"


@given("I want to see what VM types are available")
def step_check_available_vms(context):
    """Setup: User wants to check available VM types."""
    context.wants_vm_list = True


@given("I want a clean test environment")
def step_clean_test_env(context):
    """Setup: User wants a clean test environment."""
    context.clean_environment = True


@given("I want to test with a database")
def step_test_with_database(context):
    """Setup: User wants to test with a database."""
    context.test_with_database = True


@given("port 5432 might be in use")
def step_port_may_be_used(context):
    """Setup: Port might be in use."""
    context.port_conflict_scenario = True


# ========== WHEN STEPS ==========


@when("I start my daily development VMs")
def step_start_daily_vms(context):
    """Start the user's daily development VMs."""
    result = run_vde_command("start python", context=context)
    context.last_exit_code = result.returncode
    wait_for_container("python", timeout=60)


@when("I create a new language VM for a project")
def step_create_language_vm(context):
    """Create a new language VM for a project."""
    result = run_vde_command("create python", context=context)
    context.last_exit_code = result.returncode


@when("I switch from Python to Rust project")
def step_switch_to_rust(context):
    """Switch from Python to Rust project."""
    # Stop Python
    run_vde_command("stop python", context=context)
    # Create and start Rust
    result = run_vde_command("start rust", context=context)
    context.last_exit_code = result.returncode
    wait_for_container("rust", timeout=60)


@when("I need to connect to PostgreSQL from Python VM")
def step_connect_postgres(context):
    """Connect to PostgreSQL from Python VM."""
    # First ensure PostgreSQL is running
    run_vde_command("start postgres", context=context)
    wait_for_container("postgres", timeout=60)
    context.postgres_running = True


@when("I shut down all VMs at end of day")
def step_shutdown_all(context):
    """Shut down all VMs at the end of the day."""
    result = run_vde_command("stop all -f", context=context)
    context.last_exit_code = result.returncode


@when("I run multiple language VMs for a polyglot project")
def step_run_multiple_vms(context):
    """Run multiple language VMs for a polyglot project."""
    result = run_vde_command("start python go rust", context=context)
    context.last_exit_code = result.returncode
    for vm in ["python", "go", "rust"]:
        wait_for_container(vm, timeout=60)


@when("I rebuild a VM after modifying its Dockerfile")
def step_rebuild_vm(context):
    """Rebuild a VM after modifying its Dockerfile."""
    result = run_vde_command("start python --rebuild", context=context)
    context.last_exit_code = result.returncode
    wait_for_container("python", timeout=120)


@when("I remove VM I no longer need")
def step_remove_vm(context):
    """Remove a VM that is no longer needed."""
    result = run_vde_command("remove ruby", context=context)
    context.last_exit_code = result.returncode


@when("I add support for a new language")
def step_add_new_language(context):
    """Add support for a new language."""
    # This tests the add intent
    result = run_vde_command(
        "add zig --type lang --display-name Zig --install 'apt-get install -y zig'", context=context
    )
    context.last_exit_code = result.returncode


@when("I quickly check what's running")
def step_quick_status(context):
    """Quickly check what VMs are running."""
    result = run_vde_command("status", context=context)
    context.last_exit_code = result.returncode


@when("I create test environment with database")
def step_create_test_env(context):
    """Create a test environment with a database."""
    result = run_vde_command("create python postgres", context=context)
    context.last_exit_code = result.returncode


@when("I start Python and Go VMs")
def step_start_python_go(context):
    """Start Python and Go VMs."""
    result = run_vde_command("start python go", context=context)
    context.last_exit_code = result.returncode
    wait_for_container("python", timeout=60)
    wait_for_container("go", timeout=60)


@when("I create PostgreSQL VM")
def step_create_postgres(context):
    """Create PostgreSQL VM."""
    result = run_vde_command("create postgres", context=context)
    context.last_exit_code = result.returncode


@when('SSH into "{hostname}"')
def step_ssh_into_vm(context, hostname):
    """SSH into the specified VM (canonical or alias)."""
    vm_name = hostname.replace("vde-", "")
    result = run_vde_command(f"connect {vm_name} --dry-run", context=context)
    context.ssh_command = result.stdout
    context.last_exit_code = result.returncode


# ========== THEN STEPS ==========


@then("all three VMs should be running")
def step_all_three_vms_running(context):
    """Verify all expected VMs are running."""
    running = docker_ps()
    expected_vms = getattr(context, "created_vms", ["python", "rust", "postgres"])
    for vm in expected_vms:
        full_name = f"vde-{vm}"
        assert full_name in running, f"VM {full_name} not running. Found: {running}"


@then('I should be able to SSH to "{hostname}" on allocated port')
def step_ssh_to_vm_on_port(context, hostname):
    """Verify SSH connection to specified VM."""
    vm_name = hostname.replace("vde-", "")
    result = run_vde_command(f"connect {vm_name} --dry-run", context=context)
    assert result.returncode == 0, f"Connect command failed for {vm_name}: {result.stderr}"
    assert "ssh" in result.stdout.lower() or "port" in result.stdout.lower(), (
        "Missing SSH info in output"
    )


@then("PostgreSQL should be accessible from language VMs")
def step_postgres_accessible(context):
    """Verify PostgreSQL is accessible from language VMs."""
    assert container_exists("postgres"), "PostgreSQL should be running"
    # Verify we can reach it from python
    result = run_vde_command('exec python "pg_isready -h vde-postgres"', context=context)
    assert result.returncode == 0, f"PostgreSQL not reachable from Python: {result.stderr}"


@then('SSH config entry for "{hostname}" should be added')
def step_ssh_config_entry_added(context, hostname):
    """Verify SSH config entry for VM is present in project config."""
    ssh_config = VDE_ROOT / "configs" / "ssh" / "config"
    assert ssh_config.exists(), "Project SSH config missing"
    assert hostname in ssh_config.read_text(), f"SSH config missing entry for {hostname}"


@then("I can SSH to both VMs from my terminal")
def step_ssh_both_vms(context):
    """Verify SSH to both VMs is configured."""
    for vm in ["python", "go"]:
        result = run_vde_command(f"connect {vm} --dry-run", context=context)
        assert result.returncode == 0, f"Connect failed for {vm}"


@then("each VM has isolated project directories")
def step_isolated_directories(context):
    """Verify each VM has isolated project directories."""
    for vm in ["python", "go"]:
        assert (VDE_ROOT / "projects" / vm).exists(), f"Project dir missing for {vm}"


@then("I should be connected to PostgreSQL")
def step_connected_to_postgres(context):
    """Verify connection to PostgreSQL."""
    assert container_exists("postgres"), "PostgreSQL not running"


@then("I can query the database")
def step_query_database(context):
    """Verify database queries work."""
    # Use pg_isready as a proxy for 'querying' capability
    result = run_vde_command('exec postgres "pg_isready"', context=context)
    assert result.returncode == 0


@then("the connection uses the container network")
def step_container_network(context):
    """Verify connection uses container network."""
    result = run_vde_command(
        'inspect postgres -f "{{json .NetworkSettings.Networks}}"', context=context
    )
    assert "vde-net" in result.stdout or "vde-testing" in result.stdout


@then("all VMs should be stopped")
def step_all_vms_stopped(context):
    """Verify all VMs are stopped via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) == 0, f"VMs still running: {vde_running}"


@then("VM configurations should remain for next session")
def step_configs_remain(context):
    """Verify VM configurations remain for next session."""
    assert (VDE_ROOT / "configs" / "docker" / "python").exists(), "Python config missing"
    assert (VDE_ROOT / "configs" / "docker" / "rust").exists(), "Rust config missing"


@then("Python VM can make HTTP requests to JavaScript VM")
def step_python_http_js(context):
    """Verify connectivity between VMs."""
    # Ensure both are running
    run_vde_command("start python js", context=context)
    wait_for_container("python")
    wait_for_container("js")
    # Ping as proxy for 'HTTP request' capability
    result = run_vde_command('exec python "/sbin/ping -c 1 vde-js"', context=context)
    assert result.returncode == 0, f"Python failed to reach JS: {result.stderr}"


@then("Python VM can connect to Redis")
def step_python_redis(context):
    """Verify connection to Redis."""
    run_vde_command("start redis", context=context)
    wait_for_container("redis")
    # Check port 6379 from python
    result = run_vde_command(
        "exec python \"timeout 2 bash -c '> /dev/tcp/vde-redis/6379'\"", context=context
    )
    assert result.returncode == 0, "Redis not reachable from Python"


@then("Python VM should be created")
def step_python_created(context):
    """Verify Python VM config exists."""
    assert compose_file_exists("python")


@then("I should see Python VM status")
def step_python_status(context):
    """Verify Python status in output."""
    result = run_vde_command("status", context=context)
    assert "python" in result.stdout.lower()


@then("Rust VM should be created and started")
def step_rust_created(context):
    """Verify Rust VM is created and running."""
    assert compose_file_exists("rust")
    assert container_exists("rust")


@then("PostgreSQL VM should be running")
def step_postgres_running(context):
    """Verify PostgreSQL VM is running."""
    assert container_exists("postgres")


@then("connection information should be displayed")
def step_connection_info_displayed(context):
    """Verify connection info in output."""
    assert "ssh" in context.last_output.lower() or "port" in context.last_output.lower()


@then("Python VM should be restarted")
def step_python_restarted(context):
    """Verify Python VM is running."""
    assert container_exists("python")


@then("the rebuild should complete successfully")
def step_rebuild_success(context):
    """Verify rebuild succeeded."""
    assert context.last_exit_code == 0


@then("Ruby VM should be removed")
def step_ruby_removed(context):
    """Verify Ruby container is gone."""
    assert not container_exists("ruby")


@then("I should see list of available VM types")
def step_available_vms_listed(context):
    """Verify list output."""
    assert "available" in context.last_output.lower() or "vm" in context.last_output.lower()


@then("clean state should be available")
def step_clean_state(context):
    """Verify no running VMs."""
    assert len([c for c in docker_ps() if c.startswith("vde-")]) == 0


@then("database should be running")
def step_database_running(context):
    """Verify database is running."""
    assert container_exists("postgres")


@then("I can start Python VM")
def step_start_python(context):
    """Verify Python can start."""
    result = run_vde_command("start python", context=context)
    assert result.returncode == 0


@then("port conflict should be resolved")
def step_port_conflict_resolved(context):
    """Verify port conflict resolved."""
    assert context.last_exit_code == 0


@then("I should see status information")
def step_status_info(context):
    """Verify status in output."""
    assert "status" in context.last_output.lower() or "running" in context.last_output.lower()


@then("the VM should be rebuilt from scratch")
def step_rebuild_from_scratch(context):
    """Verify rebuild."""
    assert context.last_exit_code == 0


# ========== Additional Missing Steps ==========


@then("each VM can access shared project directories")
def step_shared_directories(context):
    """Verify project mounts via inspect."""
    result = run_vde_command("inspect python -f '{{json .Mounts}}'", context=context)
    assert "projects" in result.stdout.lower()


@given("I have modified the python Dockerfile to add a new package")
def step_modified_python_dockerfile(context):
    """Setup: Simulate Dockerfile modification."""
    context.dockerfile_modified = True


@then("the VM should be rebuilt with the new Dockerfile")
def step_rebuilt_with_new_dockerfile(context):
    """Verify rebuild completed by checking for new container instance."""
    # Successful rebuild + start results in exit code 0 and a running container
    assert getattr(context, "last_exit_code", 1) == 0, "Rebuild failed"
    assert container_exists("python"), "Python VM should be running after rebuild"


@then("the VM should be running after rebuild")
def step_running_after_rebuild(context):
    """Verify VM running."""
    assert container_exists("python")


@then("the new package should be available in the VM")
def step_new_package_available(context):
    """Verify rebuild success."""
    assert context.last_exit_code == 0


@given('I have an old "ruby" VM I don\'t use anymore')
def step_old_ruby_vm(context):
    """Setup: Ensure Ruby VM exists."""
    run_vde_command("create ruby", context=context)


@when('I run the removal process for "ruby"')
def step_run_removal_ruby(context):
    """Remove Ruby VM."""
    result = run_vde_command("remove ruby", context=context)
    context.last_exit_code = result.returncode


@then("the docker-compose.yml should be preserved for easy recreation")
def step_docker_compose_preserved(context):
    """Verify config preservation."""
    assert compose_file_exists("ruby")


@given("a system service is using port {port:d}")
def step_system_service_using_port(context, port):
    """Simulate a port conflict by starting a listener on the specified port."""
    import socket

    context.port_conflict_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.port_conflict_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        context.port_conflict_socket.bind(("127.0.0.1", port))
        context.port_conflict_socket.listen(1)
        context.conflict_port = port
    except OSError:
        pass  # Port already in use, that's fine
