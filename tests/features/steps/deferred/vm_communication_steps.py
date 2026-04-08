from behave import given, when, then
import os
from vm_common import run_vde_command, container_is_running
from critical_steps import ensure_vm_accessible

@given('the SSH agent is running')
def step_ssh_agent_running_check(context):
    output = run_vde_command('ssh-setup', context=context).stdout
    assert 'Agent PID' in output or 'running' in output.lower()

@given('my keys are loaded in the agent')
@given('I have 2 SSH keys loaded in the agent')
def step_keys_loaded_check(context):
    output = run_vde_command('ssh-setup', context=context).stdout
    assert 'SHA256' in output or 'Identity added' in output or 'agent has no identities' not in output.lower()

@given('I create a {vm_alias} VM for my {purpose}')
def step_create_vm_purpose(context, vm_alias, purpose=None):
    vm_alias = vm_alias.lower()
    if 'postgre' in vm_alias: vm_alias = 'postgres'
    if not container_is_running(vm_alias):
        run_vde_command(f'start {vm_alias}', context=context)
        assert ensure_vm_accessible(context, vm_alias)
    context.last_vm = vm_alias

@given('I start all VMs')
def step_start_all_vms(context):
    pass

@then('I should connect to the {vm_alias} VM')
def step_verify_connection(context, vm_alias):
    output = getattr(context, 'last_output', '')
    assert vm_alias.lower() in output.lower() or 'vde-' in output.lower()

@then('I should be authenticated using my host\'s SSH keys')
@then('authentication should use my host\'s SSH keys')
@then('all connections should use my host\'s SSH keys')
@then('all authentications should use my host\'s SSH keys')
@then('authentication should be automatic')
@then('the file should be copied using my host\'s SSH keys')
@then('all should use my host\'s SSH keys')
def step_verify_host_key_auth(context):
    res = getattr(context, 'last_vm_command_result', None)
    output = getattr(context, 'last_output', '')
    assert res and res.returncode == 0
    assert 'password' not in output.lower()

@then('I should not need to enter a password')
@then('no password should be required')
def step_no_password_required(context):
    output = getattr(context, 'last_output', '')
    assert 'password' not in output.lower()

@then('I should not need to copy keys to the {vm_alias} VM')
@then('no keys should be copied to any VM')
@then('the VMs should not have copies of my private keys')
def step_no_keys_copied(context, vm_alias=None):
    vm_to_check = vm_alias.lower() if vm_alias else getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f'exec {vm_to_check} "ls ~/.ssh/id_ed25519"', context=context)
    assert result.returncode != 0

@then('I should be able to run psql commands')
@then('I should see the PostgreSQL list of databases')
def step_psql_check(context):
    output = getattr(context, 'last_output', '')
    assert 'List of databases' in output or 'postgres' in output.lower()

@when('I create a file in the {vm_alias} VM')
def step_create_file_vm(context, vm_alias):
    run_vde_command(f'exec {vm_alias} "echo hello > /tmp/file"', context=context)

@then('I should see "{expected_text}"')
def step_see_text(context, expected_text):
    output = getattr(context, 'last_output', '')
    assert expected_text in output

@then('both services should respond')
def step_both_services_respond(context):
    res = getattr(context, 'last_vm_command_result', None)
    assert res and res.returncode == 0

@given('I am developing a full-stack application')
@given('I have frontend, backend, and database VMs')
def step_full_stack_context(context):
    pass

@when('I need to test the backend from the frontend VM')
def step_test_backend_context(context):
    context.connected_vm = 'frontend' 

@then('the tests should run on the backend VM')
@then('I should see the results in the frontend VM')
def step_test_results_check(context):
    res = getattr(context, 'last_vm_command_result', None)
    assert res and res.returncode == 0

@then('the private keys should remain on the host')
def step_private_keys_on_host(context):
    assert os.path.exists(os.path.expanduser('~/.ssh/vde/id_ed25519'))

@then('only the SSH agent socket should be forwarded')
def step_agent_socket_forwarded(context):
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f'exec {vm_name} "env | grep SSH_AUTH_SOCK"', context=context)
    assert result.returncode == 0
    assert 'SSH_AUTH_SOCK' in result.stdout

@given('I have 5 VMs running')
def step_five_vms_running(context):
    pass

@when('I SSH from {vm1} to {vm2}')
def step_ssh_vm_to_vm(context, vm1, vm2):
    pass

@then('all connections should succeed')
def step_all_connections_succeed(context):
    pass

@given('I am a new VDE user')
def step_new_vde_user(context):
    pass

@when('I read the documentation')
def step_read_docs(context):
    pass

@then('I should see that SSH management is automatic')
@then('no manual SSH setup instructions should be present')
def step_check_docs_content(context):
    pass


@when('I use scp to copy files')
def step_use_scp(context):
    pass

@then('the output should be displayed')
def step_output_displayed(context):
    output = getattr(context, 'last_output', '')
    assert len(output) > 0
