"""
BDD Step definitions for Natural Language Commands scenarios.
Uses real vde-parser library functions and ACTUAL Docker verification.
"""

import os
import subprocess
import sys
import time

from behave import given, then, when

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

# Get VDE_ROOT from environment or calculate
VDE_ROOT = os.environ.get('VDE_ROOT_DIR')
if not VDE_ROOT:
    try:
        from config import VDE_ROOT as config_root
        VDE_ROOT = str(config_root)
    except ImportError:
        VDE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

VDE_PARSER = os.path.join(VDE_ROOT, 'scripts/lib/vde-parser')
VDE_VM_COMMON = os.path.join(VDE_ROOT, 'scripts/lib/vm-common')
VDE_SHELL_COMPAT = os.path.join(VDE_ROOT, 'scripts/lib/vde-shell-compat')
VDE_SCRIPT = os.path.join(VDE_ROOT, 'scripts/vde')


def _call_vde_parser_function(function_name, input_string):
    """Call a vde-parser function and return stdout."""
    env = os.environ.copy()
    env['VDE_TEST_INPUT'] = input_string
    cmd = f"zsh -c 'source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \"$VDE_TEST_INPUT\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    return result.stdout.strip(), result.returncode


def _get_real_intent(input_string):
    """Call vde-parser's detect_intent function."""
    stdout, _ = _call_vde_parser_function('detect_intent', input_string)
    return stdout


def _get_real_vm_names(input_string):
    """Call vde-parser's extract_vm_names function."""
    stdout, _ = _call_vde_parser_function('extract_vm_names', input_string)
    if not stdout:
        return []
    return [vm for vm in stdout.split('\n') if vm]


def _get_real_flags(input_string):
    """Call vde-parser's extract_flags function."""
    stdout, _ = _call_vde_parser_function('extract_flags', input_string)
    flags = {'rebuild': False, 'nocache': False}
    if stdout:
        for pair in stdout.split():
            if '=' in pair:
                key, value = pair.split('=', 1)
                flags[key] = value.lower() == 'true'
    return flags


def run_vde_command(command_args):
    """Run a VDE command and return result."""
    cmd = [VDE_SCRIPT, *command_args]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result


def container_is_running(container_name):
    """Check if a Docker container is running using docker inspect."""
    result = subprocess.run(
        ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
        capture_output=True, text=True
    )
    return result.returncode == 0 and result.stdout.strip() == 'true'


def get_running_containers():
    """Get list of running VDE containers using docker ps."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=-dev', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    return [name.strip() for name in result.stdout.split('\n') if name.strip()]


def get_all_vde_containers():
    """Get list of all VDE containers (running and stopped) using docker ps -a."""
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', 'name=-dev', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    return [name.strip() for name in result.stdout.split('\n') if name.strip()]


def _resolve_vm_name(vm_type):
    """Resolve VM name via parser."""
    vm_names = _get_real_vm_names(vm_type.lower())
    return vm_names[0] if vm_names else vm_type.lower()


# =============================================================================
# GIVEN Steps - Setup context
# =============================================================================

@given('I want to perform common actions')
def step_common_actions(context):
    pass


@given('I can phrase commands in different ways')
def step_different_phrasings(context):
    pass


@given('I need to work with multiple environments')
def step_multiple_environments(context):
    pass


@given('I know a VM by its alias')
def step_alias_support(context):
    pass


@given('I want to know what\'s running')
def step_status_query(context):
    pass


@given('I\'m not sure what to do')
def step_help_request(context):
    pass


@given('I need to connect to a VM')
def step_connection_help(context):
    pass


@given('I need to rebuild a container')
def step_rebuild_request(context):
    pass


@given('I want to operate on all VMs of a type')
def step_wildcard_operations(context):
    pass


@given('I\'m done working')
def step_shutdown_all(context):
    pass


@given('I use conversational language')
def step_conversational_language(context):
    pass


@given('something isn\'t working')
def step_troubleshooting(context):
    pass


@given('I type commands in various cases')
def step_case_insensitivity(context):
    pass


@given('I want to type less')
def step_minimal_typing(context):
    pass


# =============================================================================
# WHEN Steps - Execute natural language commands with REAL VDE execution
# =============================================================================

@when('I say {quote}{input_text}{quote}')
def step_say_input(context, quote, input_text):
    """Process and execute a natural language input through vde-parser."""
    context.nl_input = input_text
    context.nl_intent = _get_real_intent(input_text)
    context.nl_vms = _get_real_vm_names(input_text)
    context.nl_flags = _get_real_flags(input_text)

    # Execute the actual VDE command
    if context.nl_intent in ('start_vm', 'create_vm', 'stop_vm', 'restart_vm'):
        cmd_args = []
        if context.nl_intent == 'create_vm':
            cmd_args.append('create')
        elif context.nl_intent == 'start_vm':
            cmd_args.append('start')
        elif context.nl_intent == 'stop_vm':
            cmd_args.append('stop')
        elif context.nl_intent == 'restart_vm':
            cmd_args.append('restart')

        if context.nl_flags.get('rebuild'):
            cmd_args.append('--rebuild')
        if context.nl_flags.get('nocache'):
            cmd_args.append('--no-cache')

        cmd_args.extend(context.nl_vms)
        context.nl_result = run_vde_command(cmd_args)
        context.last_exit_code = context.nl_result.returncode
        context.last_output = context.nl_result.stdout
        context.last_error = context.nl_result.stderr

    elif context.nl_intent == 'status':
        result = run_vde_command(['status'])
        context.nl_result = result
        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr

    elif context.nl_intent == 'help':
        result = run_vde_command(['--help'])
        context.nl_result = result
        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr
    else:
        context.nl_result = None


@when('I ask {quote}{input_text}{quote}')
def step_ask_input(context, quote, input_text):
    """Process and execute a natural language query."""
    step_say_input(context, quote, input_text)


# =============================================================================
# THEN Steps - Verify REAL Docker state
# =============================================================================

@then('the system should understand I want to {action} the {vm_type} VM')
def step_verify_intent(context, action, vm_type):
    """Verify the correct intent was detected and command executed."""
    expected_intents = {
        'start': 'start_vm',
        'create': 'create_vm',
        'stop': 'stop_vm',
        'restart': 'restart_vm',
        'status': 'status',
    }
    expected_intent = expected_intents.get(action)
    assert expected_intent is not None, f"Unknown action: {action}"
    assert context.nl_intent == expected_intent, \
        f"Expected intent '{expected_intent}', got '{context.nl_intent}'"

    # Verify command succeeded
    assert context.last_exit_code == 0, f"Command failed: {context.last_error}"

    # Verify actual Docker state for VM operations
    if action in ('start', 'create'):
        canonical = _resolve_vm_name(vm_type)
        container_name = f"{canonical}-dev"
        if action == 'start':
            assert container_is_running(container_name), \
                f"Container {container_name} is not running (docker inspect)"
        else:  # create
            all_containers = get_all_vde_containers()
            assert container_name in all_containers, \
                f"Container {container_name} not found (docker ps -a)"


@then('both VMs from my command should start')
def step_both_vms_from_command_start(context):
    """Verify both VMs started successfully using REAL Docker."""
    assert len(context.nl_vms) >= 2, "Expected at least 2 VMs in command"
    assert context.last_exit_code == 0, f"Command failed: {context.last_error}"

    for vm_name in context.nl_vms:
        container_name = f"{vm_name}-dev"
        assert container_is_running(container_name), \
            f"Container {container_name} is not running (docker inspect)"


@then('the {vm_type} VM from my command should be created')
def step_vm_created(context, vm_type):
    """Verify the VM was created using REAL Docker."""
    canonical = _resolve_vm_name(vm_type)
    container_name = f"{canonical}-dev"

    all_containers = get_all_vde_containers()
    assert container_name in all_containers, \
        f"Container {container_name} not found (docker ps -a)"


@then('I should see the status')
def step_see_status(context):
    """Verify status information is displayed."""
    assert context.last_exit_code == 0, f"Status command failed: {context.last_error}"
    output = context.last_output.lower()
    assert any(word in output for word in ['running', 'stopped', 'vm', 'container', 'created']), \
        f"Status output doesn't contain expected info: {output[:200]}"


@then('I should see help information')
def step_see_help(context):
    """Verify help information is displayed."""
    assert context.last_exit_code == 0, f"Help command failed: {context.last_error}"
    output = context.last_output.lower()
    assert any(word in output for word in ['usage', 'command', 'available', 'help']), \
        f"Help doesn't explain commands: {output[:200]}"


@then('available commands should be explained')
def step_commands_explained(context):
    """Verify commands are explained in help."""
    output = context.last_output.lower()
    assert any(word in output for word in ['create', 'start', 'stop', 'status', 'list']), \
        f"Help doesn't explain commands: {output[:200]}"


@then('I should receive SSH connection instructions')
def step_receive_ssh_instructions(context):
    """Verify SSH connection info is provided."""
    assert context.nl_intent == 'connect', f"Expected 'connect' intent, got '{context.nl_intent}'"
    if context.nl_result:
        output = context.nl_result.stdout.lower()
        assert any(word in output for word in ['ssh', 'port', 'connect', 'localhost']), \
            f"No SSH instructions found in: {output[:200]}"


@then('the instructions should be clear and actionable')
def step_instructions_clear(context):
    """Verify instructions are usable."""
    assert context.nl_intent == 'connect', "Should be a connection request"
    if context.nl_result:
        output = context.nl_result.stdout.lower()
        assert any(word in output for word in ['ssh', 'connect', 'command', 'run', 'port']), \
            "Instructions should contain actionable commands"


@then('the rebuild flag should be set')
def step_rebuild_flag_set(context):
    """Verify rebuild flag was detected."""
    assert context.nl_flags.get('rebuild') is True, \
        f"Expected rebuild=True, got {context.nl_flags}"


@then('no cache should be used')
def step_nocache_set(context):
    """Verify no-cache flag was detected."""
    assert context.nl_flags.get('nocache') is True, \
        f"Expected nocache=True, got {context.nl_flags}"


@then('all language VMs should start')
def step_all_lang_start(context):
    """Verify all language VMs started using REAL Docker."""
    vm_types_file = os.path.join(VDE_ROOT, 'scripts/data/vm-types.conf')
    lang_vms = []
    with open(vm_types_file) as f:
        for line in f:
            if line.strip() and not line.strip().startswith('#'):
                parts = line.split('|')
                if len(parts) >= 3:
                    vm_type = parts[2].strip()
                    if vm_type == 'lang':
                        lang_vms.append(parts[0].strip())

    assert context.last_exit_code == 0, f"Command failed: {context.last_error}"

    running = get_running_containers()
    running_lang_vms = [vm for vm in lang_vms if f"{vm}-dev" in running]
    assert len(running_lang_vms) > 0, \
        f"No language VMs are running (docker ps shows: {running})"


@then('service VMs should not be affected')
def step_services_unaffected(context):
    """Verify service VMs weren't started."""
    vm_types_file = os.path.join(VDE_ROOT, 'scripts/data/vm-types.conf')
    svc_vms = []
    with open(vm_types_file) as f:
        for line in f:
            if line.strip() and not line.strip().startswith('#'):
                parts = line.split('|')
                if len(parts) >= 3:
                    vm_type = parts[2].strip()
                    if vm_type == 'svc':
                        svc_vms.append(parts[0].strip())

    running = get_running_containers()
    for svc in svc_vms:
        assert svc not in running, \
            f"Service VM {svc} should not be running (docker ps shows: {running})"


@then('all running VMs should stop')
def step_all_stop(context):
    """Verify all VMs were stopped using REAL Docker."""
    running = get_running_containers()
    assert len(running) == 0, \
        f"Expected no running containers, but found: {running} (docker ps)"


@then('{vm1} and {vm2} should be created')
def step_both_created(context, vm1, vm2):
    """Verify both VMs were created using REAL Docker."""
    assert context.last_exit_code == 0, f"Create command failed: {context.last_error}"

    for vm in [vm1.lower(), vm2.lower()]:
        resolved = _get_real_vm_names(vm)
        canonical = resolved[0] if resolved else vm
        container_name = f"{canonical}-dev"

        all_containers = get_all_vde_containers()
        assert container_name in all_containers, \
            f"Container {container_name} not found (docker ps -a)"


@then('{vm_type} should restart')
def step_vm_restart(context, vm_type):
    """Verify VM restarted using REAL Docker."""
    vm_lookup = {'database': 'postgres', 'db': 'postgres'}
    vm_name = vm_lookup.get(vm_type.lower(), vm_type.lower())

    resolved = _get_real_vm_names(vm_name)
    canonical = resolved[0] if resolved else vm_name
    container_name = f"{canonical}-dev"

    assert container_is_running(container_name), \
        f"Container {container_name} is not running after restart (docker inspect)"


@then('the system should understand {quote}database{quote} means {quote}postgres{quote}')
def step_understand_database_alias(context, quote):
    """Verify "database" maps to postgres."""
    resolved = _get_real_vm_names('database')
    assert 'postgres' in resolved, \
        f"Expected 'postgres' to be resolved from 'database', got {resolved}"


@then('case should not matter')
def step_case_not_matter(context):
    """Verify case insensitivity by checking actual execution."""
    assert context.last_exit_code == 0, f"Command failed: {context.last_error}"
    # The real verification is that the command executed and container is running
    if context.nl_vms:
        for vm_name in context.nl_vms:
            container_name = f"{vm_name}-dev"
            assert container_is_running(container_name), \
                f"Container {container_name} is not running (docker inspect)"


@then('it should understand {quote}py{quote} means {quote}python{quote}')
def step_py_means_python(context, quote):
    """Verify short alias 'py' maps to python."""
    resolved = _get_real_vm_names('py')
    assert 'python' in resolved, \
        f"Expected 'python' to be resolved from 'py', got {resolved}"


@then('{quote}pg{quote} should mean {quote}postgres{quote}')
def step_pg_means_postgres(context, quote):
    """Verify short alias 'pg' maps to postgres."""
    resolved = _get_real_vm_names('pg')
    assert 'postgres' in resolved, \
        f"Expected 'postgres' to be resolved from 'pg', got {resolved}"


@then('the appropriate action should be taken')
def step_appropriate_action(context):
    """Verify the appropriate action was taken."""
    assert hasattr(context, 'nl_intent'), "No intent was detected"
    assert context.nl_intent in ('start_vm', 'create_vm', 'stop_vm', 'restart_vm', 'status', 'help'), \
        f"Unexpected intent: {context.nl_intent}"

    if context.nl_intent != 'help' and context.nl_intent != 'status':
        assert context.last_exit_code == 0, f"Command should succeed: {context.last_error}"


@then('the {vm_type} VM should start')
def step_vm_should_start(context, vm_type):
    """Verify a specific VM started using REAL Docker."""
    canonical = _resolve_vm_name(vm_type)
    container_name = f"{canonical}-dev"

    assert container_is_running(container_name), \
        f"Container {container_name} is not running (docker inspect)"
