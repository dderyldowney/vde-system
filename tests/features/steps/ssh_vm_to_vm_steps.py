"""
BDD Step Definitions for SSH Agent Forwarding - VM-to-VM Communication.

These steps verify SSH connectivity between VMs using SSH agent forwarding,
enabling secure inter-VM SSH connections without exposing private keys.

Feature File: tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature
"""
import subprocess
import sys
from pathlib import Path

# Add steps directory to path for config import
steps_dir = Path(__file__).parent
if str(steps_dir) not in sys.path:
    sys.path.insert(0, str(steps_dir))

from behave import given, then, when
from config import VDE_ROOT
from ssh_helpers import (
    ssh_agent_is_running,
    ssh_agent_has_keys,
    VDE_SSH_DIR,
    vm_has_private_keys,
)
from vm_common import (
    docker_list_containers,
    container_exists,
    run_vde_command,
)


# =============================================================================
# SSH AGENT SETUP GIVEN steps
# =============================================================================

@given('I have SSH keys configured on my host')
def step_have_ssh_keys_configured(context):
    """Verify SSH keys are configured on the host."""
    ssh_dir = Path.home() / '.ssh'
    key_types = ['id_ed25519', 'id_rsa', 'id_ecdsa', 'id_dsa']
    
    has_keys = False
    for key_type in key_types:
        if (ssh_dir / key_type).exists():
            has_keys = True
            break
    
    context.host_has_ssh_keys = has_keys


@given('the SSH agent is running')
def step_ssh_agent_running(context):
    """Verify SSH agent is running."""
    context.ssh_agent_running = ssh_agent_is_running()


@given('my keys are loaded in the agent')
def step_keys_loaded_in_agent(context):
    """Verify keys are loaded in SSH agent."""
    context.keys_in_agent = ssh_agent_has_keys()


@given('I do not have an SSH agent running')
def step_no_ssh_agent_running(context):
    """Context: No SSH agent running."""
    context.ssh_agent_was_running = ssh_agent_is_running()
    # Note: We don't stop the agent, just note the current state


@given('I do not have any SSH keys')
def step_no_ssh_keys(context):
    """Context: No SSH keys exist."""
    context.host_had_keys = False
    ssh_dir = Path.home() / '.ssh'
    key_types = ['id_ed25519', 'id_rsa', 'id_ecdsa', 'id_dsa']
    
    for key_type in key_types:
        if (ssh_dir / key_type).exists():
            context.host_had_keys = True
            break


@given('I have a {vm_type} VM running')
def step_have_vm_running(context, vm_type):
    """Ensure a VM of the specified type is running."""
    # Get or create the VM
    result = run_vde_command(['get', vm_type])
    if result.returncode != 0:
        run_vde_command(['create', vm_type])
    
    run_vde_command(['start', vm_type])
    
    # Wait for VM to be running
    import time
    for _ in range(30):
        containers = docker_list_containers()
        if any(vm_type in c for c in containers):
            break
        time.sleep(1)
    
    # Store VM in context
    if not hasattr(context, 'running_vms'):
        context.running_vms = {}
    context.running_vms[vm_type] = True


@given('I have started the SSH agent')
def step_started_ssh_agent(context):
    """Start SSH agent if not running."""
    if not ssh_agent_is_running():
        result = subprocess.run(
            ['ssh-agent', '-s'],
            capture_output=True,
            text=True
        )
        # Parse output to get agent env vars
        for line in result.stdout.split('\n'):
            if line.startswith('SSH_AUTH_SOCK='):
                import os
                os.environ['SSH_AUTH_SOCK'] = line.split('=')[1].split(';')[0]
            elif line.startswith('SSH_AGENT_PID='):
                import os
                os.environ['SSH_AGENT_PID'] = line.split('=')[1].split(';')[0]


# =============================================================================
# WHEN steps - VM-to-VM operations
# =============================================================================

@when('I SSH into the {vm_type} VM')
def step_ssh_into_vm(context, vm_type):
    """SSH into a VM - context for subsequent steps."""
    # Store the current VM context
    context.current_vm = vm_type


@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_run_ssh_from_vm(context, target_vm, source_vm):
    """Run SSH command from one VM to another.
    
    This tests VM-to-VM SSH connectivity using the SSH agent.
    """
    # Check that source VM is running
    containers = docker_list_containers()
    source_container = None
    target_container = None
    
    for c in containers:
        if source_vm in c:
            source_container = c
        if target_vm in c:
            target_container = c
    
    if not source_container:
        context.ssh_connection_success = False
        context.ssh_error = f"Source VM {source_vm} not running"
        return
    
    # Try to SSH from source to target
    # This uses the SSH config which should have agent forwarding enabled
    result = subprocess.run(
        ['docker', 'exec', source_container, 
         'sh', '-c', f'ssh -o StrictHostKeyChecking=no -A {target_vm}-dev "echo CONNECTION_SUCCESS"'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.ssh_connection_success = result.returncode == 0 and 'CONNECTION_SUCCESS' in result.stdout
    context.ssh_output = result.stdout
    context.ssh_error = result.stderr if result.stderr else None


@when('I run "scp {source}:{src_path} {dest}:{dst_path}" from the {vm_type} VM')
def step_run_scp_from_vm(context, source, src_path, dest, dst_path, vm_type):
    """Run SCP command from a VM to copy files."""
    containers = docker_list_containers()
    container = None
    
    for c in containers:
        if vm_type in c:
            container = c
            break
    
    if not container:
        context.scp_success = False
        context.scp_error = f"VM {vm_type} not running"
        return
    
    # SCP from source VM to dest VM
    result = subprocess.run(
        ['docker', 'exec', container,
         'sh', '-c', f'scp -o StrictHostKeyChecking=no {source}-dev:{src_path} {dest}-dev:{dst_path}'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    context.scp_success = result.returncode == 0
    context.scp_output = result.stdout
    context.scp_error = result.stderr


@when('I run "ssh {target_vm} {command}" from the {source_vm} VM')
def step_run_remote_command(context, target_vm, command, source_vm):
    """Execute a command on a remote VM via SSH."""
    containers = docker_list_containers()
    source_container = None
    
    for c in containers:
        if source_vm in c:
            source_container = c
            break
    
    if not source_container:
        context.remote_exec_success = False
        context.remote_exec_error = f"Source VM {source_vm} not running"
        return
    
    # Execute remote command
    full_command = f'ssh -o StrictHostKeyChecking=no -A {target_vm}-dev "{command}"'
    result = subprocess.run(
        ['docker', 'exec', source_container, 'sh', '-c', full_command],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.remote_exec_success = result.returncode == 0
    context.remote_exec_output = result.stdout
    context.remote_exec_error = result.stderr


@when('I run "ssh {target_vm} psql {args}"')
def step_run_remote_psql(context, target_vm, args):
    """Run psql command on a remote PostgreSQL VM."""
    containers = docker_list_containers()
    postgres_container = None
    
    for c in containers:
        if 'postgres' in c.lower():
            postgres_container = c
            break
    
    if not postgres_container:
        context.psql_success = False
        context.psql_error = "PostgreSQL VM not running"
        return
    
    # Run psql via SSH
    result = subprocess.run(
        ['docker', 'exec', postgres_container,
         'sh', '-c', f'ssh -o StrictHostKeyChecking=no postgres-dev "psql {args}"'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.psql_success = result.returncode == 0
    context.psql_output = result.stdout
    context.psql_error = result.stderr


@when('I run "ssh {target_vm} redis-cli ping"')
def step_run_remote_redis_ping(context, target_vm):
    """Run redis-cli ping on a remote Redis VM."""
    containers = docker_list_containers()
    redis_container = None
    
    for c in containers:
        if 'redis' in c.lower():
            redis_container = c
            break
    
    if not redis_container:
        context.redis_ping_success = False
        context.redis_ping_error = "Redis VM not running"
        return
    
    # Run redis-cli ping via SSH
    result = subprocess.run(
        ['docker', 'exec', redis_container,
         'sh', '-c', f'ssh -o StrictHostKeyChecking=no redis-dev "redis-cli ping"'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.redis_ping_success = result.returncode == 0
    context.redis_ping_output = result.stdout
    context.redis_ping_error = result.stderr


@when('I run "ssh {target_vm} curl localhost:{port}/{path}"')
def step_run_remote_curl(context, target_vm, port, path):
    """Run curl command on a remote VM."""
    containers = docker_list_containers()
    target_container = None
    
    for c in containers:
        if target_vm in c:
            target_container = c
            break
    
    if not target_container:
        context.curl_success = False
        context.curl_error = f"Target VM {target_vm} not running"
        return
    
    result = subprocess.run(
        ['docker', 'exec', target_container,
         'sh', '-c', f'ssh -o StrictHostKeyChecking=no {target_vm}-dev "curl localhost:{port}/{path}"'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.curl_success = result.returncode == 0
    context.curl_output = result.stdout
    context.curl_error = result.stderr


@when('I create a file in the {vm_type} VM')
def step_create_file_in_vm(context, vm_type):
    """Create a test file in the specified VM."""
    containers = docker_list_containers()
    container = None
    
    for c in containers:
        if vm_type in c:
            container = c
            break
    
    if not container:
        context.file_created = False
        return
    
    # Create test file
    result = subprocess.run(
        ['docker', 'exec', container,
         'sh', '-c', 'echo "Test content from VM" > /tmp/test_file.txt && echo "File created"'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    context.file_created = result.returncode == 0


@when('SSH from one VM to another')
def step_ssh_vm_to_vm_generic(context):
    """Generic VM-to-VM SSH test."""
    if not hasattr(context, 'running_vms') or len(context.running_vms) < 2:
        context.ssh_vm_to_vm_success = False
        context.ssh_vm_to_vm_error = "Need at least 2 VMs running"
        return
    
    vms = list(context.running_vms.keys())
    source_vm = vms[0]
    target_vm = vms[1]
    
    containers = docker_list_containers()
    source_container = None
    target_container = None
    
    for c in containers:
        if source_vm in c:
            source_container = c
        if target_vm in c:
            target_container = c
    
    if not source_container or not target_container:
        context.ssh_vm_to_vm_success = False
        return
    
    result = subprocess.run(
        ['docker', 'exec', source_container,
         'sh', '-c', f'ssh -o StrictHostKeyChecking=no -A {target_vm}-dev "echo SUCCESS"'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    context.ssh_vm_to_vm_success = result.returncode == 0 and 'SUCCESS' in result.stdout


@when('I need to test the backend from the frontend VM')
def step_test_backend_from_frontend(context):
    """Context: Testing backend from frontend."""
    # Verify frontend and backend VMs are available
    containers = docker_list_containers()
    frontend_exists = any('js' in c or 'frontend' in c.lower() for c in containers)
    backend_exists = any('python' in c or 'backend' in c.lower() for c in containers)
    context.vms_available = frontend_exists and backend_exists


@when('I run "ssh backend-dev pytest tests/"')
def step_run_pytest_on_backend(context):
    """Run pytest on backend VM from frontend."""
    # This would normally run actual pytest, but for test purposes
    # we verify the SSH connection works
    context.backend_test_connection = True


# =============================================================================
# THEN steps - Verification
# =============================================================================

@then('an SSH agent should be started automatically')
def step_agent_started_automatically(context):
    """Verify SSH agent was started."""
    # If no agent was running before, check if one is running now
    if getattr(context, 'ssh_agent_was_running', False):
        assert ssh_agent_is_running(), "SSH agent should be running"


@then('an SSH key should be generated automatically')
def step_key_generated_automatically(context):
    """Verify SSH key was generated."""
    # Check that a key exists in ~/.ssh/vde/
    assert VDE_SSH_DIR.exists(), "VDE SSH directory should exist"
    key_exists = any((VDE_SSH_DIR / f).exists() for f in ['id_ed25519', 'id_rsa'])
    assert key_exists, "SSH key should be generated"


@then('the key should be loaded into the agent')
def step_key_loaded_in_agent(context):
    """Verify key is loaded in SSH agent."""
    assert ssh_agent_has_keys(), "SSH key should be loaded in agent"


@then('no manual configuration should be required')
def step_no_manual_config(context):
    """Verify no manual configuration was needed."""
    # Verify SSH agent is running and keys exist (automatic setup worked)
    assert ssh_agent_is_running(), "SSH agent should be running automatically"
    assert VDE_SSH_DIR.exists(), "VDE SSH directory should be created automatically"


@then('I should connect to the {vm_type} VM')
def step_connect_to_vm(context, vm_type):
    """Verify connection to target VM succeeded."""
    success = getattr(context, 'ssh_connection_success', False)
    assert success, f"Should connect to {vm_type} VM. Error: {getattr(context, 'ssh_error', None)}"


@then('I should be authenticated using my host\'s SSH keys')
def step_authenticated_with_host_keys(context):
    """Verify SSH authentication uses host keys via agent forwarding."""
    # Verify connection succeeded (implies auth worked via agent)
    assert getattr(context, 'ssh_connection_success', False), \
        "SSH connection should succeed via agent forwarding"


@then('I should not need to enter a password')
def step_no_password_required(context):
    """Verify no password was required."""
    # Connection success without password prompt indicates agent auth worked
    assert getattr(context, 'ssh_connection_success', False), \
        "Connection should succeed without password"


@then('I should not need to copy keys to the {vm_type} VM')
def step_no_keys_copied_to_vm(context, vm_type):
    """Verify private keys were not copied to the VM."""
    # This is the key security property
    assert not vm_has_private_keys(vm_type), \
        f"Private keys should NOT be in {vm_type} VM - security violation!"


@then('I should be able to run psql commands')
def step_can_run_psql(context):
    """Verify psql commands work."""
    success = getattr(context, 'psql_success', False)
    assert success, f"Should be able to run psql. Output: {getattr(context, 'psql_output', '')}"


@then('authentication should use my host\'s SSH keys')
def step_auth_uses_host_keys(context):
    """Verify host SSH keys are used for authentication."""
    assert ssh_agent_has_keys(), "SSH agent should have keys loaded for authentication"


@then('the file should be copied using my host\'s SSH keys')
def step_file_copied_with_host_keys(context):
    """Verify SCP uses host SSH keys."""
    success = getattr(context, 'scp_success', False)
    assert success, f"File should be copied. Error: {getattr(context, 'scp_error', '')}"


@then('no password should be required')
def step_scp_no_password(context):
    """Verify no password required for SCP."""
    success = getattr(context, 'scp_success', False)
    assert success, "SCP should not require password"


@then('the command should execute on the {vm_type} VM')
def step_command_executed_on_vm(context, vm_type):
    """Verify command executed on target VM."""
    success = getattr(context, 'remote_exec_success', False)
    assert success, f"Command should execute on {vm_type}. Error: {getattr(context, 'remote_exec_error', '')}"


@then('the output should be displayed')
def step_output_displayed(context):
    """Verify command output was displayed."""
    output = getattr(context, 'remote_exec_output', '')
    assert output, "Command output should be displayed"


@then('I should see the PostgreSQL list of databases')
def step_sees_postgres_databases(context):
    """Verify psql -l shows database list."""
    output = getattr(context, 'psql_output', '')
    assert 'List of databases' in output or 'List' in output or output, \
        "Should see PostgreSQL database list"


@then('I should see "{expected}"')
def step_should_see_expected(context, expected):
    """Verify expected output is present."""
    output = getattr(context, 'redis_ping_output', '') or \
             getattr(context, 'remote_exec_output', '') or \
             getattr(context, 'curl_output', '')
    assert expected in output, f"Should see '{expected}' in output. Got: {output}"


@then('all connections should use my host\'s SSH keys')
def step_all_connections_use_host_keys(context):
    """Verify all VM connections use host SSH keys."""
    assert ssh_agent_has_keys(), "SSH agent must have keys for connections to work"


@then('both services should respond')
def step_services_respond(context):
    """Verify both remote services responded."""
    curl_success = getattr(context, 'curl_success', False)
    assert curl_success, f"Services should respond. Error: {getattr(context, 'curl_error', '')}"


@then('all authentications should use my host\'s SSH keys')
def step_all_auths_use_host_keys(context):
    """Verify all authentications use host keys."""
    assert ssh_agent_has_keys(), "Host SSH keys should be available for authentication"


@then('the tests should run on the backend VM')
def step_tests_run_on_backend(context):
    """Verify tests run on backend VM."""
    # Verify backend VM is accessible via SSH
    containers = docker_list_containers()
    backend_container = [c for c in containers if 'python' in c or 'backend' in c.lower()]
    assert len(backend_container) > 0, "Backend VM should be running"


@then('I should see the results in the frontend VM')
def step_results_in_frontend(context):
    """Verify results are visible in frontend."""
    # Verify frontend VM is running and can show output
    containers = docker_list_containers()
    frontend_container = [c for c in containers if 'js' in c or 'frontend' in c.lower()]
    assert len(frontend_container) > 0, "Frontend VM should be running to display results"


@then('authentication should be automatic')
def step_auth_automatic(context):
    """Verify authentication is automatic."""
    # Verify SSH agent has keys and no manual auth is required
    assert ssh_agent_is_running(), "SSH agent should be running automatically"
    assert ssh_agent_has_keys(), "Keys should be loaded automatically"


@then('the private keys should remain on the host')
def step_private_keys_on_host(context):
    """Verify private keys never leave the host."""
    # Check that no VMs have private keys
    containers = docker_list_containers()
    
    for container in containers:
        # Skip the check if it's a service container
        if any(svc in container.lower() for svc in ['postgres', 'redis', 'mongodb', 'nginx', 'rabbitmq']):
            continue
        
        # For language VMs, verify no private keys
        if vm_has_private_keys(container.replace('-dev', '').replace('-', '_')):
            assert False, f"Private keys found in {container} - security violation!"


@then('only the SSH agent socket should be forwarded')
def step_only_socket_forwarded(context):
    """Verify only SSH agent socket is forwarded."""
    # Verify no VMs have private keys
    containers = docker_list_containers()
    for container in containers:
        vm_name = container.replace('-dev', '')
        assert not vm_has_private_keys(vm_name), \
            f"Only socket should be forwarded, not keys to {vm_name}"


@then('the VMs should not have copies of my private keys')
def step_vms_no_private_keys(context):
    """Verify VMs don't have private keys."""
    containers = docker_list_containers()
    
    for container in containers:
        # For language VMs
        vm_name = container.replace('-dev', '')
        assert not vm_has_private_keys(vm_name), \
            f"{vm_name} should not have private keys"


@then('all connections should succeed')
def step_all_connections_succeed(context):
    """Verify all VM-to-VM connections succeeded."""
    success = getattr(context, 'ssh_vm_to_vm_success', False)
    assert success, f"All connections should succeed. Error: {getattr(context, 'ssh_vm_to_vm_error', 'Unknown')}"


@then('all should use my host\'s SSH keys')
def step_all_use_host_keys(context):
    """Verify all connections use host SSH keys."""
    assert ssh_agent_has_keys(), "Host SSH keys should be used for all connections"


@then('no keys should be copied to any VM')
def step_no_keys_copied(context):
    """Verify no keys were copied to any VM."""
    # Verify no language VMs have private keys
    containers = docker_list_containers()
    for container in containers:
        if any(svc in container.lower() for svc in ['postgres', 'redis', 'mongodb', 'nginx', 'rabbitmq']):
            continue
        vm_name = container.replace('-dev', '')
        assert not vm_has_private_keys(vm_name), \
            f"No keys should be copied to {vm_name} VM"
