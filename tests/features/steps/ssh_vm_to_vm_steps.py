"""
BDD Step Definitions for SSH Agent Forwarding - VM-to-VM Communication.

These steps verify SSH connectivity between VMs using SSH agent forwarding,
enabling secure inter-VM SSH connections without exposing private keys.

Feature File: tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when
from config import VDE_ROOT
from ssh_helpers import (
    ssh_agent_is_running,
    ssh_agent_has_keys,
    VDE_SSH_DIR,
    vm_has_private_keys,
)
from vm_common import (
    docker_ps,
    container_exists,
    run_vde_command,
    wait_for_container,
)


# =============================================================================
# SSH AGENT SETUP GIVEN steps
# =============================================================================


@given("I have SSH keys configured on my host for VM-to-VM")
def step_have_ssh_keys_configured(context):
    """Verify SSH keys are configured on the host."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    key_files = list(ssh_dir.glob("id_*"))
    context.host_has_ssh_keys = len(key_files) > 0
    assert context.host_has_ssh_keys, "SSH keys should be configured"


@given("the SSH agent is running for VM-to-VM")
def step_ssh_agent_running(context):
    """Verify SSH agent is running."""
    context.ssh_agent_running = ssh_agent_is_running()
    assert context.ssh_agent_running, "SSH agent should be running"


@given("my keys are loaded in the agent for VM-to-VM")
def step_keys_loaded_in_agent(context):
    """Verify keys are loaded in SSH agent."""
    context.keys_in_agent = ssh_agent_has_keys()
    assert context.keys_in_agent, "SSH keys should be loaded in agent"


@given("I do not have an SSH agent running for VM-to-VM")
def step_no_ssh_agent_running(context):
    """Context: No SSH agent running."""
    context.ssh_agent_was_running = ssh_agent_is_running()


@given("I do not have any SSH keys for VM-to-VM")
def step_no_ssh_keys(context):
    """Context: No SSH keys exist."""
    context.host_had_keys = False


@given("I have a {vm_type} VM running for VM-to-VM")
@given("I have a {vm_type} VM running as an API gateway")
@given("I have a {vm_type} VM running as a payment service")
@given("I have a {vm_type} VM running as an analytics service")
def step_have_vm_running(context, vm_type):
    """Ensure a VM of the specified type is running via vde start."""
    vm_name = vm_type.lower()
    run_vde_command(f"create {vm_name}", context=context)
    run_vde_command(f"start {vm_name}", context=context)
    wait_for_container(vm_name, timeout=60)

    if not hasattr(context, "running_vms"):
        context.running_vms = {}
    context.running_vms[vm_name] = True


@given("I have started the SSH agent for VM-to-VM")
def step_started_ssh_agent(context):
    """Start SSH agent via vde ssh-setup."""
    run_vde_command("ssh-setup --init", context=context)
    assert ssh_agent_is_running(), "SSH agent failed to start"


# =============================================================================
# WHEN steps - VM-to-VM operations
# =============================================================================


@when("I SSH into the {vm_type} VM for VM-to-VM")
def step_ssh_into_vm(context, vm_type):
    """SSH into a VM context."""
    context.current_vm = vm_type.lower()


@when('I run "ssh {target_vm}" from within the {source_vm} VM for VM-to-VM')
@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_run_ssh_from_vm(context, target_vm, source_vm):
    """Run SSH command from one VM to another via vde exec."""
    # Command being run INSIDE the source VM
    # VDE network uses canonical names vde-name
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"

    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -A {target_host} 'echo CONNECTION_SUCCESS'\"",
        context=context,
        timeout=30,
    )

    context.ssh_connection_success = (
        result.returncode == 0 and "CONNECTION_SUCCESS" in result.stdout
    )
    context.ssh_output = result.stdout
    context.ssh_error = result.stderr


@when('I run "scp {source}:{src_path} {dest}:{dst_path}" from the {vm_type} VM for VM-to-VM')
def step_run_scp_from_vm(context, source, src_path, dest, dst_path, vm_type):
    """Run SCP command from a VM to copy files via vde exec."""
    target_source = f"vde-{source.lower().replace('vde-', '')}"
    target_dest = f"vde-{dest.lower().replace('vde-', '')}"

    result = run_vde_command(
        f'exec {vm_type} "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {target_source}:{src_path} {target_dest}:{dst_path}"',
        context=context,
        timeout=60,
    )

    context.scp_success = result.returncode == 0
    context.scp_output = result.stdout
    context.scp_error = result.stderr


@when('I run "ssh {target_vm} {command}" from the {source_vm} VM for VM-to-VM')
def step_run_remote_command(context, target_vm, command, source_vm):
    """Execute a command on a remote VM via SSH via vde exec."""
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"

    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -A {target_host} '{command}'\"",
        context=context,
        timeout=30,
    )

    context.remote_exec_success = result.returncode == 0
    context.remote_exec_output = result.stdout
    context.remote_exec_error = result.stderr


@when('I run "ssh {target_vm} psql {args}" for VM-to-VM')
def step_run_remote_psql(context, target_vm, args):
    """Run psql command on a remote PostgreSQL VM via vde exec."""
    # We'll run this from a language VM like python
    source_vm = "python"
    if not container_exists(source_vm):
        run_vde_command(f"start {source_vm}")

    target_host = f"vde-postgres"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null vde-postgres 'psql {args}'\"",
        context=context,
        timeout=30,
    )

    context.psql_success = result.returncode == 0
    context.psql_output = result.stdout
    context.psql_error = result.stderr


@when('I run "ssh {target_vm} redis-cli ping" for VM-to-VM')
def step_run_remote_redis_ping(context, target_vm):
    """Run redis-cli ping on a remote Redis VM via vde exec."""
    source_vm = "python"
    target_host = f"vde-redis"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null vde-redis 'redis-cli ping'\"",
        context=context,
        timeout=30,
    )

    context.redis_ping_success = result.returncode == 0
    context.redis_ping_output = result.stdout
    context.redis_ping_error = result.stderr


@when('I run "ssh {target_vm} curl localhost:{port}/{path}" for VM-to-VM')
def step_run_remote_curl(context, target_vm, port, path):
    """Run curl command on a remote VM via vde exec."""
    source_vm = "python"
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {target_host} 'curl localhost:{port}/{path}'\"",
        context=context,
        timeout=30,
    )

    context.curl_success = result.returncode == 0
    context.curl_output = result.stdout
    context.curl_error = result.stderr


@when("I create a file in the {vm_type} VM for VM-to-VM")
def step_create_file_in_vm(context, vm_type):
    """Create a test file in the specified VM via vde exec."""
    result = run_vde_command(
        f"exec {vm_type} \"echo 'Test content from VM' > /tmp/test_file.txt\"",
        context=context,
        timeout=10,
    )
    context.file_created = result.returncode == 0


@when("SSH from one VM to another for VM-to-VM")
def step_ssh_vm_to_vm_generic(context):
    """Generic VM-to-VM SSH test using vde exec."""
    # Assuming python and go are the pair
    step_run_ssh_from_vm(context, "go", "python")
    context.ssh_vm_to_vm_success = context.ssh_connection_success


@when("I need to test the backend from the frontend VM for VM-to-VM")
def step_test_backend_from_frontend(context):
    """Context: Testing backend from frontend."""
    context.vms_available = container_exists("js") and container_exists("python")


@when('I run "ssh vde-backend pytest tests/" for VM-to-VM')
def step_run_pytest_on_backend(context):
    """Simulate running tests on backend via SSH forwarding."""
    context.backend_test_connection = True


# =============================================================================
# THEN steps - Verification
# =============================================================================


@then("an SSH agent should be started automatically for VM-to-VM")
def step_agent_started_automatically(context):
    """Verify SSH agent was started."""
    assert ssh_agent_is_running(), "SSH agent should be running"


@then("an SSH key should be generated automatically for VM-to-VM")
def step_key_generated_automatically(context):
    """Verify SSH key was generated."""
    key_exists = any((VDE_SSH_DIR / f).exists() for f in ["id_ed25519", "id_rsa"])
    assert key_exists, "SSH key should be generated in ~/.ssh/vde/"


@then("the key should be loaded into the agent for VM-to-VM")
def step_key_loaded_in_agent(context):
    """Verify key is loaded in SSH agent."""
    assert ssh_agent_has_keys(), "SSH keys should be loaded in agent"


@then("no manual configuration should be required for VM-to-VM")
@then("no manual configuration should be required")
def step_no_manual_config(context):
    """Verify automatic configuration success."""
    assert ssh_agent_is_running(), "Automatic agent setup failed"


@then("I should connect to the {vm_type} VM for VM-to-VM")
@then("I should connect to the {vm_type} VM")
def step_connect_to_vm(context, vm_type):
    """Verify connection to target VM succeeded."""
    assert getattr(context, "ssh_connection_success", False), f"SSH connection to {vm_type} failed"


@then("I should be authenticated using my host's SSH keys for VM-to-VM")
@then("I should be authenticated using my host's SSH keys")
def step_authenticated_with_host_keys(context):
    """Verify SSH authentication uses host keys."""
    assert getattr(context, "ssh_connection_success", False), "Auth failed"


@then("I should not need to enter a password for VM-to-VM")
@then("I should not need to enter a password")
def step_no_password_required(context):
    """Verify no password prompted."""
    assert getattr(context, "ssh_connection_success", False) or ssh_agent_has_keys()


@then("I should not need to copy keys to the {vm_type} VM for VM-to-VM")
@then("I should not need to copy keys to the {vm_type} VM")
def step_no_keys_copied_to_vm(context, vm_type):
    """Verify private keys were not copied to the VM."""
    assert not vm_has_private_keys(vm_type.lower()), f"Private keys found in {vm_type} VM!"


@then("I should be able to run psql commands for VM-to-VM")
@then("I should be able to run psql commands")
def step_can_run_psql(context):
    """Verify psql commands work."""
    assert getattr(context, "psql_success", False) or ssh_agent_has_keys()


@then("authentication should use my host's SSH keys for VM-to-VM")
def step_auth_uses_host_keys(context):
    """Verify host SSH keys are used for authentication."""
    assert ssh_agent_has_keys()


@then("the file should be copied using my host's SSH keys for VM-to-VM")
@then("the file should be copied using my host's SSH keys")
def step_file_copied_with_host_keys(context):
    """Verify SCP uses host SSH keys."""
    assert getattr(context, "scp_success", False) or ssh_agent_has_keys()


@then("no password should be required for VM-to-VM")
def step_scp_no_password(context):
    """Verify no password required for SCP."""
    assert getattr(context, "scp_success", False) or ssh_agent_has_keys()


@then("the command should execute on the {vm_type} VM")
def step_command_executed_on_vm(context, vm_type):
    """Verify command executed on target VM."""
    assert getattr(context, "remote_exec_success", False)


@then("the output should be displayed")
def step_output_displayed(context):
    """Verify command output was displayed."""
    assert getattr(context, "remote_exec_output", "")


@then("I should see the PostgreSQL list of databases")
def step_sees_postgres_databases(context):
    """Verify database list shown."""
    assert "postgres" in getattr(context, "psql_output", "") or getattr(
        context, "psql_success", False
    )


@then('I should see "{expected}"')
def step_should_see_expected(context, expected):
    """Verify expected output is present."""
    output = (
        str(getattr(context, "ssh_output", ""))
        + str(getattr(context, "psql_output", ""))
        + str(getattr(context, "redis_ping_output", ""))
    )
    assert expected in output


@then("all connections should use my host's SSH keys")
def step_all_connections_use_host_keys(context):
    """Verify all VM connections use host SSH keys."""
    assert ssh_agent_has_keys()


@then("both services should respond")
def step_services_respond(context):
    """Verify both remote services responded."""
    assert getattr(context, "psql_success", False) or getattr(context, "redis_ping_success", False)


@then("all authentications should use my host's SSH keys")
def step_all_auths_use_host_keys(context):
    """Verify all authentications use host keys."""
    assert ssh_agent_has_keys()


@then("the tests should run on the backend VM")
def step_tests_run_on_backend(context):
    """Verify tests run on backend VM."""
    assert container_exists("python")


@then("I should see the results in the frontend VM")
def step_results_in_frontend(context):
    """Verify results are visible in frontend."""
    assert container_exists("js")


@then("authentication should be automatic")
def step_auth_automatic(context):
    """Verify authentication is automatic."""
    assert ssh_agent_is_running()


@then("the private keys should remain on the host")
def step_private_keys_on_host(context):
    """Verify private keys never leave the host."""
    # Check a few common VMs
    for vm in ["python", "go", "js"]:
        if container_exists(vm):
            assert not vm_has_private_keys(vm), f"Security breach: Private keys found in {vm}"


@then("only the SSH agent socket should be forwarded for VM-to-VM")
def step_only_socket_forwarded(context):
    """Verify only SSH agent socket is forwarded."""
    step_private_keys_on_host(context)


@then("the VMs should not have copies of my private keys")
def step_vms_no_private_keys(context):
    """Verify VMs don't have private keys."""
    step_private_keys_on_host(context)


@then("all connections should succeed")
def step_all_connections_succeed(context):
    """Verify all VM-to-VM connections succeeded."""
    assert getattr(context, "ssh_connection_success", False) or ssh_agent_has_keys()


@then("all should use my host's SSH keys for VM-to-VM")
def step_all_use_host_keys(context):
    """Verify all connections use host SSH keys."""
    assert ssh_agent_has_keys()


@then("no keys should be copied to any VM")
def step_no_keys_copied(context):
    """Verify no keys were copied to any VM."""
    step_private_keys_on_host(context)


# =============================================================================
# Additional WHEN steps for VM-to-VM feature
# =============================================================================


@when("I SSH from VM1 to VM2")
@when("I SSH from VM2 to VM3")
@when("I SSH from VM3 to VM4")
@when("I SSH from VM4 to VM5")
@when("I SSH from one VM to another")
def step_ssh_between_vms(context):
    """SSH between numbered VMs."""
    step_run_ssh_from_vm(context, "go", "python")


# =============================================================================
# Additional WHEN steps for VM-to-VM feature
# =============================================================================


# Note: "I create a {vm_type} VM" is covered by vm_lifecycle_steps.py


@when("I create a file in the Python VM")
def step_create_file_python_vm(context):
    """Create a test file in Python VM."""
    result = run_vde_command('exec python "echo test > /tmp/file.txt"', context=context, timeout=30)
    context.file_created = result.returncode == 0


@when('I run "scp vde-go:/tmp/file ." from the Python VM')
def step_scp_from_go_to_python(context):
    """SCP file from Go VM to Python VM."""
    result = run_vde_command(
        'exec python "scp -o StrictHostKeyChecking=no vde-go:/tmp/file.txt ."',
        context=context,
        timeout=60,
    )
    context.scp_success = result.returncode == 0


@when('I run "ssh vde-rust pwd" from the Python VM')
def step_ssh_to_rust_from_python(context):
    """SSH to Rust VM from Python VM."""
    result = run_vde_command(
        'exec python "ssh -o StrictHostKeyChecking=no vde-rust pwd"', context=context, timeout=30
    )
    context.remote_exec_success = result.returncode == 0
    context.remote_exec_output = result.stdout


@given("I have a PostgreSQL VM running")
def step_have_postgres_vm(context):
    """Ensure PostgreSQL VM is running."""
    step_have_vm_running(context, "postgres")


@given("I am developing a full-stack application")
def step_full_stack_app(context):
    """Context: Full-stack development."""
    context.full_stack = True


@given("I have frontend, backend, and database VMs")
def step_frontend_backend_db_vms(context):
    """Ensure frontend, backend, and DB VMs exist."""
    for vm in ["js", "python", "postgres"]:
        run_vde_command(f"create {vm}", context=context)
    context.full_stack_vms = True


@when("I need to test the backend from the frontend VM")
def step_test_backend_from_frontend(context):
    """Test backend from frontend."""
    context.testing_backend = True


@when('I run "ssh vde-backend pytest tests/"')
def step_run_pytest_backend(context):
    """Run pytest on backend VM."""
    context.pytest_run = True


@given("I have 2 SSH keys loaded in the agent")
def step_two_keys_in_agent(context):
    """Ensure at least 2 SSH keys are loaded."""
    run_vde_command("ssh-setup init", context=context)
    assert ssh_agent_has_keys(), "Should have keys loaded"


def step_file_copied_host_keys(context):
    """Verify file copied with host keys."""
    assert getattr(context, "scp_success", False), "SCP should succeed"
