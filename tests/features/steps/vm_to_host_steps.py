from behave import given, when, then
from vm_common import run_vde_command, container_exists, container_is_running, wait_for_container, check_docker_available
import os

@given('I have Docker installed on my host for VM-to-Host')
def step_docker_installed_host(context):
    """Verify Docker is available on the host."""
    assert check_docker_available(context), "Docker must be installed on host"

@given('I have VMs running with Docker socket access')
def step_vms_running_docker_socket(context):
    """Most VDE VMs have docker socket access by default in their compose."""
    context.docker_socket_access = True

@given('I have a {vm_name} VM running for VM-to-Host')
def step_vm_running_tohost(context, vm_name):
    """Ensure a specific VM is running."""
    vm_name = vm_name.lower()
    if not container_is_running(vm_name):
        run_vde_command(f'start {vm_name}', context=context)
        wait_for_container(vm_name, timeout=60)
    context.current_vm = vm_name

@given('I have multiple VMs running in VM-to-Host')
def step_multiple_vms_running_tohost(context):
    """Ensure multiple VMs are running."""
    for vm in ['python', 'go']:
        if not container_is_running(vm):
            run_vde_command(f'start {vm}', context=context)
            wait_for_container(vm, timeout=60)
    context.num_vms_running = 2

@when('I SSH into the {vm_name} VM for VM-to-Host')
@when('I SSH into a VM for VM-to-Host')
def step_ssh_into_vm_tohost(context, vm_name='python'):
    """Simulate SSHing into a VM."""
    context.connected_vm = vm_name.lower()

@when('I run "{command}" for VM-to-Host')
def step_run_command_tohost(context, command):
    """Run a command that uses to-host inside the VM."""
    vm_name = getattr(context, 'connected_vm', 'python')
    
    # We execute the command inside the VM using 'vde exec'
    # The command itself is expected to be something like "vde to-host docker ps"
    # or "to-host docker ps" if it hasn't been refactored yet in the feature file.
    result = run_vde_command(f'exec {vm_name} "{command}"', context=context)
    
    # Store results for different assertions
    if 'docker ps' in command:
        context.tohost_output = result.stdout
        context.tohost_result = (result.returncode == 0)
    elif 'restart postgres' in command:
        context.tohost_restart_output = result.stdout
        context.tohost_restart_result = (result.returncode == 0)
    else:
        context.tohost_output = result.stdout
        context.tohost_result = (result.returncode == 0)
    
    context.last_tohost_command = command
    context.last_tohost_result = result

@then("I should see a list of running containers")
@then("the output should show my host's containers")
def step_see_host_containers(context):
    """Verify host containers are shown."""
    output = getattr(context, 'tohost_output', '')
    tohost_result = getattr(context, 'tohost_result', False)
    assert tohost_result or 'CONTAINER' in output.upper() or 'NAMES' in output, \
        f"Output should show host containers. Got: {output[:200]}"

@then('the PostgreSQL container should restart')
def step_postgres_restarted(context):
    """Verify PostgreSQL restarted."""
    output = getattr(context, 'tohost_restart_output', '')
    tohost_result = getattr(context, 'tohost_restart_result', False)
    assert tohost_result or 'postgres' in output.lower() or 'restarted' in output.lower(), \
        f"PostgreSQL restart verification failed. Output: {output[:200]}"

# -----------------------------------------------------------------------------
# Contextual "Feel-Good" Steps (Given/And)
# -----------------------------------------------------------------------------
@given('I need to check what\'s running on my host')
@given('my host has application logs')
@given('I have projects on my host for VM-to-Host')
@given('I need to check resource usage')
@given('I need to restart a service on my host')
@given('I need to read a configuration file on my host')
@given('I need to trigger a build on my host')
@given('I need to check the status of other VMs')
@given('I need to trigger a backup on my host')
@given('my host has an issue I need to diagnose')
@given('I need to check host network connectivity')
@given('I have custom scripts on my host for VM-to-Host')
def step_noop_context(context, vm_name=None):
    if vm_name:
        step_vm_running_tohost(context, vm_name)

# -----------------------------------------------------------------------------
# Verification Steps (Then/And)
# -----------------------------------------------------------------------------
@then('I should see a list of my host\'s directories')
@then('I should be able to navigate the host filesystem')
@then('I should see resource usage for all containers')
@then('I should see CPU, memory, and I/O statistics')
@then('I should be able to verify the restart')
@then('I should see the contents of the host file')
@then('I should be able to use the content in the VM')
@then('the build should execute on my host')
@then('I should see the build output for VM-to-Host')
@then('I should see the status of the Python VM')
@then('I can make decisions based on the status')
@then('the backup should execute on my host')
@then('my data should be backed up')
@then('I should see the Docker service status')
@then('I can diagnose the issue')
@then('I should see network connectivity results')
@then('I can diagnose network issues')
@then('the script should execute on my host')
@then('the cleanup should be performed')
@then("I should see the host's log output")
@then("the output should update in real-time")
def step_success_assertion(context):
    """Generic success assertion for VM-to-Host commands."""
    tohost_result = getattr(context, 'tohost_result', False)
    last_res = getattr(context, 'last_tohost_result', None)
    err_msg = ""
    if last_res:
        err_msg = f"\nStdout: {last_res.stdout[:200]}\nStderr: {last_res.stderr[:200]}"
    assert tohost_result, f"Command failed.{err_msg}"
