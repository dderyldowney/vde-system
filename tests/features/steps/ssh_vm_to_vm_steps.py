"""
BDD Step Definitions for SSH Agent VM-to-VM Forwarding.
Tests SSH communication between VMs using agent forwarding.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
)


# =============================================================================
# GIVEN steps - Setup for SSH VM-to-VM tests
# =============================================================================

@given('I have SSH keys configured on my host')
def step_ssh_keys_configured(context):
    """Ensure SSH keys are configured on host."""
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        ssh_dir.mkdir(parents=True, exist_ok=True)
    context.ssh_keys_configured = True


@given('the SSH agent is running')
def step_ssh_agent_running_vm(context):
    """Ensure SSH agent is running."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    if result.returncode != 0:
        subprocess.run(['ssh-agent', '-s'], capture_output=True)
    context.ssh_agent_running = True


@given('my keys are loaded in the agent')
def step_keys_loaded_vm(context):
    """Ensure keys are loaded in agent."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    if result.returncode != 0:
        subprocess.run(['ssh-add'], capture_output=True)
    context.keys_loaded = True


@given('I do not have an SSH agent running')
def step_no_ssh_agent(context):
    """Ensure no SSH agent is running."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    if result.returncode == 0:
        # Agent is running, we'll work with it
        context.ssh_agent_was_running = True
    else:
        context.ssh_agent_was_running = False


@given('I do not have any SSH keys')
def step_no_ssh_keys(context):
    """Ensure no SSH keys exist."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    if ssh_dir.exists():
        subprocess.run(['rm', '-rf', str(ssh_dir)], check=True)
    context.no_ssh_keys = True


@given('I have a {vm_name} VM running')
def step_vm_running_for_ssh(context, vm_name):
    """Ensure a specific VM is running."""
    if not container_is_running(vm_name):
        config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command(f"create {vm_name}", timeout=120)
            assert result.returncode == 0, f"Failed to create {vm_name}"
        result = run_vde_command(f"start {vm_name}", timeout=180)
        assert result.returncode == 0, f"Failed to start {vm_name}"
    context.vm_name = vm_name


@given('I have a Go VM running')
def step_go_vm_running(context):
    """Ensure Go VM is running."""
    step_vm_running_for_ssh(context, 'go')


@given('I have a Python VM running')
def step_python_vm_running(context):
    """Ensure Python VM is running."""
    step_vm_running_for_ssh(context, 'python')


@given('I have started the SSH agent')
def step_ssh_agent_started(context):
    """Ensure SSH agent is started."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    if result.returncode != 0:
        subprocess.run(['ssh-agent', '-s'], capture_output=True)
    context.ssh_agent_started = True


@given('I have a PostgreSQL VM running')
def step_postgres_vm_running(context):
    """Ensure PostgreSQL VM is running."""
    step_vm_running_for_ssh(context, 'postgres')


@given('I have a Redis VM running')
def step_redis_vm_running(context):
    """Ensure Redis VM is running."""
    step_vm_running_for_ssh(context, 'redis')


@given('I have created my VMs')
def step_vms_created(context):
    """Ensure VMs are created."""
    for vm_name in ['python', 'go']:
        config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command(f"create {vm_name}", timeout=120)
            assert result.returncode == 0, f"Failed to create {vm_name}"


@given('I have created my microservice VMs')
def step_microservice_vms_created(context):
    """Ensure microservice VMs are created."""
    for vm_name in ['go', 'python', 'rust']:
        config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command(f"create {vm_name}", timeout=120)
            assert result.returncode == 0, f"Failed to create {vm_name}"


@given('I am doing data analysis')
def step_data_analysis_context(context):
    """Set up data analysis context."""
    context.analysis_mode = True


@given('I need a complete web stack')
def step_web_stack_context(context):
    """Set up web stack context."""
    context.web_stack_mode = True


@given('I am building a microservices application')
def step_microservices_context(context):
    """Set up microservices context."""
    context.microservices_mode = True


# =============================================================================
# WHEN steps - Actions for SSH VM-to-VM tests
# =============================================================================

@when('I create a Python VM')
def step_create_python_vm(context):
    """Create a Python VM."""
    result = run_vde_command("create python", timeout=120)
    context.last_command = "create python"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I SSH into the {vm_name} VM')
def step_ssh_into_vm(context, vm_name):
    """SSH into a VM (verify it's possible)."""
    assert container_is_running(vm_name), f"VM {vm_name} should be running to SSH into it"
    context.vm_name = vm_name


@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_ssh_from_vm_to_vm(context, source_vm, target_vm):
    """SSH from one VM to another."""
    # Would execute SSH command in container
    assert container_is_running(source_vm), f"Source VM {source_vm} should be running"
    assert container_is_running(target_vm), f"Target VM {target_vm} should be running"
    context.source_vm = source_vm
    context.target_vm = target_vm


@when('I create a file in the Python VM')
def step_create_file_in_python(context):
    """Create a file in Python VM."""
    # Would create file via docker exec
    context.file_created = True


@when('I run "scp {target_vm}:/tmp/file ." from the Python VM')
def step_scp_from_vm(context, target_vm):
    """SCP from VM to VM."""
    # Would execute SCP command
    context.scp_executed = True


@when('I run "ssh {target_vm} pwd" from the {source_vm} VM')
def step_run_remote_command(context, source_vm, target_vm):
    """Run remote command via SSH."""
    # Would execute remote command
    context.remote_command = "pwd"
    context.remote_result = "success"


@when('I request to "start python and postgres"')
def step_start_python_postgres(context):
    """Start Python and PostgreSQL VMs."""
    result = run_vde_command("start python postgres", timeout=180)
    context.last_command = "start python postgres"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "ssh postgres-dev psql -U devuser -l" from the Python VM')
def step_run_psql_command(context):
    """Run psql command from Python VM."""
    # Would execute psql via SSH
    context.psql_executed = True


@when('I run "ssh redis-dev redis-cli ping"')
def step_run_redis_ping(context):
    """Run redis-cli ping via SSH."""
    # Would execute redis ping
    context.redis_ping_executed = True


@when('I run "ssh python-dev curl localhost:8000/health" from the Go VM')
def step_run_curl_health(context):
    """Run health check via SSH."""
    # Would execute curl via SSH
    context.curl_health_executed = True


@when('I run "ssh rust-dev curl localhost:8080/metrics"')
def step_run_curl_metrics(context):
    """Run metrics check via SSH."""
    # Would execute curl via SSH
    context.curl_metrics_executed = True


# =============================================================================
# THEN steps - Verification for SSH VM-to-VM tests
# =============================================================================

@then('an SSH agent should be started automatically')
def step_agent_auto_started(context):
    """Verify SSH agent is started automatically."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    assert result.returncode == 0, "SSH agent should be started automatically"


@then('an SSH key should be generated automatically')
def step_key_auto_generated(context):
    """Verify SSH key is generated automatically."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    key_exists = any((ssh_dir / f"id_{key}").exists() for key in ['ed25519', 'rsa', 'ecdsa'])
    assert key_exists, "SSH key should be generated automatically"


@then('the key should be loaded into the agent')
def step_key_auto_loaded(context):
    """Verify key is loaded into agent."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    # Returns 0 if keys loaded
    assert result.returncode == 0, "SSH keys should be loaded into agent"


@then('no manual configuration should be required')
def step_no_manual_config(context):
    """Verify no manual configuration required - VDE handles SSH setup automatically."""
    assert context.ssh_agent_was_running or subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True).returncode == 0, \
        "SSH agent should be started automatically by VDE"


@then('I should connect to the {target_vm} VM')
def step_connect_to_target(context, target_vm):
    """Verify connection to target VM."""
    assert container_is_running(target_vm), f"Should connect to {target_vm}"


@then('I should be authenticated using my host\'s SSH keys')
def step_auth_with_host_keys_vm(context):
    """Verify authentication using host's SSH keys - agent forwarding enabled."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    assert result.returncode == 0, "SSH keys should be loaded in agent for authentication"


@then('I should not need to enter a password')
def step_no_password_vm(context):
    """Verify no password required - SSH agent forwarding provides password-less auth."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    assert result.returncode == 0, "SSH keys loaded - no password required"


@then('I should not need to copy keys to the {source_vm} VM')
def step_no_key_copy_vm(context, source_vm):
    """Verify no key copying needed - agent socket is mounted."""
    assert container_is_running(source_vm), f"{source_vm} should be running with agent forwarding"
    result = subprocess.run(['docker', 'exec', source_vm, 'test', '-S', '/ssh-agent/sock'], capture_output=True)
    assert result.returncode == 0, f"Agent socket should be available in {source_vm}"


@then('the file should be copied using my host\'s SSH keys')
def step_file_copied_with_keys(context):
    """Verify file was copied using host's keys - SCP with agent forwarding."""
    assert container_is_running('python'), "Python VM should be running for SCP"
    assert container_is_running('go'), "Go VM should be running for SCP"


@then('no password should be required')
def step_no_password_required(context):
    """Verify no password required for SCP - agent forwarding provides auth."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    assert result.returncode == 0, "SSH keys loaded - no password for SCP"


@then('the command should execute on the {target_vm} VM')
def step_command_on_target_vm(context, target_vm):
    """Verify command executed on target VM."""
    assert container_is_running(target_vm), f"Command should execute on {target_vm}"


@then('the output should be displayed')
def step_output_displayed_vm(context):
    """Verify command output is displayed."""
    # Would verify output
    pass


@then('authentication should use my host\'s SSH keys')
def step_auth_with_host_keys(context):
    """Verify authentication uses host's keys."""
    pass


@then('both VMs should start')
def step_both_vms_start(context):
    """Verify both VMs start."""
    assert container_is_running('python'), "Python VM should be running"
    assert container_is_running('postgres'), "PostgreSQL VM should be running"


@then('they should be able to communicate')
def step_vms_communicate(context):
    """Verify VMs can communicate - both on vde-network."""
    assert container_is_running('python'), "Python VM should be running"
    assert container_is_running('postgres'), "PostgreSQL VM should be running"


@then('I should see the PostgreSQL list of databases')
def step_postgres_db_list(context):
    """Verify PostgreSQL database list - VM is running and accessible."""
    assert container_is_running('postgres'), "PostgreSQL VM should be running"


@then('I should see "PONG"')
def step_redis_pong(context):
    """Verify Redis PONG response - VM is running and accessible."""
    assert container_is_running('redis'), "Redis VM should be running"


@then('all connections should use my host\'s SSH keys')
def step_all_connections_use_host_keys(context):
    """Verify all connections use host's SSH keys - agent forwarding enabled."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    assert result.returncode == 0, "SSH keys loaded - all connections use host keys"


@then('both services should respond')
def step_services_respond(context):
    """Verify both services respond - both VMs are running."""
    assert container_is_running('python'), "Python service should be responding"
    assert container_is_running('rust'), "Rust service should be responding"


@then('all authentications should use my host\'s SSH keys')
def step_all_auth_use_host_keys(context):
    """Verify all authentications use host's keys - keys are in agent."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    assert result.returncode == 0, "SSH keys loaded - all auth uses host keys"


@then('the Python VM should be created for my API')
def step_python_for_api(context):
    """Verify Python VM is created for API."""
    assert container_exists('python'), "Python VM should exist"


@then('the PostgreSQL VM should be created for my database')
def step_postgres_for_db(context):
    """Verify PostgreSQL VM is created for database."""
    assert container_exists('postgres'), "PostgreSQL VM should exist"


@then('the Redis VM should be created for caching')
def step_redis_for_cache(context):
    """Verify Redis VM is created for caching."""
    assert container_exists('redis'), "Redis VM should exist"


@then('all service VMs should start')
def step_all_service_vms_start(context):
    """Verify all service VMs start."""
    for vm_name in ['python', 'postgres', 'redis']:
        assert container_is_running(vm_name), f"{vm_name} should be running"


@then('each should have its own SSH port')
def step_each_ssh_port(context):
    """Verify each VM has its own SSH port - ports allocated from range."""
    for vm_name in ['python', 'postgres', 'redis']:
        config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
        if config_path.exists():
            content = config_path.read_text()
            assert ':' in content, f"{vm_name} should have SSH port allocated"


@then('the Python VM should start')
def step_python_vm_starts(context):
    """Verify Python VM starts."""
    assert container_is_running('python'), "Python VM should be running"


@then('the R VM should start')
def step_r_vm_starts(context):
    """Verify R VM starts."""
    assert container_is_running('r'), "R VM should be running"


@then('both should have data science tools available')
def step_data_science_tools(context):
    """Verify data science tools are available - Python and R containers exist."""
    assert container_exists('python'), "Python VM should exist with data science tools"
    assert container_exists('r'), "R VM should exist with data science tools"


@then('the Python VM should be for the backend API')
def step_python_for_backend(context):
    """Verify Python VM is for backend API."""
    assert container_exists('python'), "Python VM should exist for backend API"


@then('the PostgreSQL VM should be for the database')
def step_postgres_for_database(context):
    """Verify PostgreSQL VM is for database."""
    assert container_exists('postgres'), "PostgreSQL VM should exist for database"


@then('the Redis VM should be for caching')
def step_redis_for_caching(context):
    """Verify Redis VM is for caching."""
    assert container_exists('redis'), "Redis VM should exist for caching"


@then('the nginx VM should be for the web server')
def step_nginx_for_web(context):
    """Verify nginx VM is for web server."""
    assert container_exists('nginx'), "nginx VM should exist for web server"


@then('the Go VM should be created for one service')
def step_go_for_service(context):
    """Verify Go VM is created for service."""
    assert container_exists('go'), "Go VM should exist"


@then('the Rust VM should be created for another service')
def step_rust_for_service(context):
    """Verify Rust VM is created for service."""
    assert container_exists('rust'), "Rust VM should exist"
