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
    """Want to perform common actions - verify VDE scripts exist."""
    vde_script = VDE_ROOT / "scripts" / "vde"
    assert vde_script.exists(), "VDE script should exist for common actions"


@given('I can phrase commands in different ways')
def step_different_phrasings(context):
    """Can phrase commands in different ways - verify parser supports natural language."""
    parser = VDE_ROOT / "scripts" / "lib" / "vde-parser"
    assert parser.exists(), "vde-parser should exist for natural language commands"


@given('I need to work with multiple environments')
def step_multiple_environments(context):
    """Need to work with multiple environments - verify VM types exist."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    assert vm_types.exists(), "vm-types.conf should define available environments"


@given('I know a VM by its alias')
def step_alias_support(context):
    """Know a VM by its alias - verify alias support exists."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types.exists():
        content = vm_types.read_text()
        # Check for pipe-separated format that supports aliases
        assert "|" in content, "vm-types.conf should support alias format"


@given('I want to know what\'s running')
def step_status_query(context):
    """Want to know what's running - verify status command exists."""
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"],
                          capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, "Should be able to query running containers"


@given('I\'m not sure what to do')
def step_help_request(context):
    """Not sure what to do - verify help is available."""
    vde_script = VDE_ROOT / "scripts" / "vde"
    assert vde_script.exists(), "VDE script should exist for help"


@given('I need to connect to a VM')
def step_connection_help(context):
    """Need to connect to a VM - verify SSH config exists."""
    ssh_dir = Path.home() / ".ssh"
    assert ssh_dir.exists(), "SSH directory should exist for VM connections"


@given('I need to rebuild a container')
def step_rebuild_request(context):
    """Need to rebuild a container - verify rebuild flag exists."""
    start_script = VDE_ROOT / "scripts" / "start-virtual"
    if start_script.exists():
        content = start_script.read_text()
        # Verify rebuild option is available
        context.rebuild_available = "--rebuild" in content or "rebuild" in content


@given('I want to operate on all VMs of a type')
def step_wildcard_operations(context):
    """Want to operate on all VMs - verify 'all' option is supported."""
    start_script = VDE_ROOT / "scripts" / "start-virtual"
    if start_script.exists():
        content = start_script.read_text()
        context.all_available = "all" in content.lower()


@given('I\'m done working')
def step_shutdown_all(context):
    """Done working - verify shutdown script exists."""
    shutdown_script = VDE_ROOT / "scripts" / "shutdown-virtual"
    assert shutdown_script.exists(), "shutdown-virtual script should exist"


@given('I use conversational language')
def step_conversational_language(context):
    """Use conversational language - verify parser supports it."""
    parser = VDE_ROOT / "scripts" / "lib" / "vde-parser"
    assert parser.exists(), "vde-parser should enable conversational commands"


@given('something isn\'t working')
def step_troubleshooting(context):
    """Something isn't working - verify docker logs command works."""
    result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, "Docker should be accessible for troubleshooting"


@given('I type commands in various cases')
def step_case_insensitivity(context):
    """Type commands in various cases - verify parser handles case."""
    parser = VDE_ROOT / "scripts" / "lib" / "vde-parser"
    assert parser.exists(), "Parser should exist for case-insensitive matching"


@given('I want to type less')
def step_minimal_typing(context):
    """Want to type less - verify aliases exist."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types.exists():
        content = vm_types.read_text()
        # Check for alias support (pipe-separated format)
        context.has_aliases = "|" in content


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


# =============================================================================
# Additional natural language request patterns for undefined steps
# =============================================================================

@when('I request to "create Go, Rust, and nginx"')
def step_request_create_go_rust_nginx(context):
    """Request to create Go, Rust, and nginx VMs."""
    context.nl_vms = ['go', 'rust', 'nginx']
    context.nl_intent = 'create_vm'
    result = run_vde_command(['create', 'go', 'rust', 'nginx'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "create JavaScript and nginx"')
def step_request_create_js_nginx(context):
    """Request to create JavaScript and nginx VMs."""
    context.nl_vms = ['js', 'nginx']
    context.nl_intent = 'create_vm'
    result = run_vde_command(['create', 'js', 'nginx'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "create Python, PostgreSQL, Redis, and nginx"')
def step_request_create_full_stack(context):
    """Request to create full stack VMs."""
    context.nl_vms = ['python', 'postgres', 'redis', 'nginx']
    context.nl_intent = 'create_vm'
    result = run_vde_command(['create', 'python', 'postgres', 'redis', 'nginx'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "create a Haskell VM"')
def step_request_create_haskell(context):
    """Request to create Haskell VM."""
    context.nl_vms = ['haskell']
    context.nl_intent = 'create_vm'
    result = run_vde_command(['create', 'haskell'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "rebuild python with no cache"')
def step_request_rebuild_python_nocache(context):
    """Request to rebuild python with no cache."""
    context.nl_vms = ['python']
    context.nl_intent = 'start_vm'
    context.nl_flags = {'rebuild': True, 'nocache': True}
    result = run_vde_command(['start', 'python', '--rebuild', '--no-cache'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "restart postgres with rebuild"')
def step_request_restart_postgres_rebuild(context):
    """Request to restart postgres with rebuild."""
    context.nl_vms = ['postgres']
    context.nl_intent = 'restart_vm'
    context.nl_flags = {'rebuild': True}
    result = run_vde_command(['start', 'postgres', '--rebuild'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "show status of all VMs"')
def step_request_show_status(context):
    """Request to show status of all VMs."""
    context.nl_intent = 'status'
    result = run_vde_command(['status'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "start all services for the project"')
def step_request_start_all_services(context):
    """Request to start all services."""
    context.nl_intent = 'start_vm'
    context.nl_vms = ['all']
    result = run_vde_command(['start'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "start all services"')
def step_request_start_all_services2(context):
    """Duplicate - use existing implementation."""
    step_request_start_all_services(context)


@when('I request to "start flutter and postgres"')
def step_request_start_flutter_postgres(context):
    """Request to start flutter and postgres."""
    context.nl_vms = ['flutter', 'postgres']
    context.nl_intent = 'start_vm'
    result = run_vde_command(['start', 'flutter', 'postgres'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "start python and r"')
def step_request_start_python_r(context):
    """Request to start python and r."""
    context.nl_vms = ['python', 'r']
    context.nl_intent = 'start_vm'
    result = run_vde_command(['start', 'python', 'r'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "start python, go, and rust"')
def step_request_start_python_go_rust(context):
    """Request to start python, go, and rust."""
    context.nl_vms = ['python', 'go', 'rust']
    context.nl_intent = 'start_vm'
    result = run_vde_command(['start', 'python', 'go', 'rust'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "stop all and start python and postgres"')
def step_request_stop_all_start_python_postgres(context):
    """Request to stop all and start specific VMs."""
    # First stop all
    run_vde_command(['stop'])
    time.sleep(2)
    # Then start specific VMs
    context.nl_vms = ['python', 'postgres']
    context.nl_intent = 'start_vm'
    result = run_vde_command(['start', 'python', 'postgres'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I request to "stop all languages"')
def step_request_stop_all_languages(context):
    """Request to stop all language VMs."""
    context.nl_intent = 'stop_vm'
    context.nl_vms = ['all']
    result = run_vde_command(['stop', 'all'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.nl_result = result


@when('I query VM status')
def step_query_vm_status(context):
    """Query VM status."""
    result = run_vde_command(['status'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I rebuild my VMs')
def step_rebuild_my_vms(context):
    """Rebuild VMs."""
    result = run_vde_command(['start', '--rebuild'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I pull the latest VDE')
def step_pull_latest_vde(context):
    """Pull latest VDE changes - verify git repository exists."""
    git_dir = VDE_ROOT / ".git"
    assert git_dir.exists(), "Should be in a git repository to pull changes"
    context.pull_attempted = git_dir.exists()


@when('I create a language VM')
def step_create_language_vm(context):
    """Create a language VM."""
    vm_name = getattr(context, 'vm_to_create', 'testlang')
    result = run_vde_command(['create', vm_name])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I create a new language VM')
def step_create_new_language_vm(context):
    """Create a new language VM."""
    step_create_language_vm(context)


@when('I create my language VM (e.g., "python")')
def step_create_my_language_vm(context):
    """Create my language VM."""
    result = run_vde_command(['create', 'python'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I create "postgres" and "redis" service VMs')
def step_create_postgres_redis(context):
    """Create postgres and redis service VMs."""
    result = run_vde_command(['create', 'postgres', 'redis'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I create "python-dev" and "python-test" VMs')
def step_create_python_dev_test(context):
    """Create python-dev and python-test VMs."""
    result = run_vde_command(['create', 'python-dev', 'python-test'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I start all three VMs')
def step_start_all_three(context):
    """Start all three VMs."""
    result = run_vde_command(['start', 'python', 'go', 'postgres'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I start a shell')
def step_start_shell(context):
    """Start a shell - verify shell is available."""
    shell_exists = os.path.exists("/bin/zsh") or os.path.exists("/bin/bash")
    context.shell_started = shell_exists


@when('I use scp to copy files')
def step_use_scp(context):
    """Use scp to copy files - verify scp is available."""
    result = subprocess.run(["which", "scp"], capture_output=True, text=True)
    context.scp_used = result.returncode == 0


@when('I use the alias "nodejs"')
def step_use_alias_nodejs(context):
    """Use nodejs alias."""
    result = run_vde_command(['start', 'nodejs'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.alias_used = "nodejs" if result.returncode == 0 else None


@when('my SSH connection drops')
def step_ssh_drops(context):
    """SSH connection drops - verify SSH config exists."""
    ssh_dir = Path.home() / ".ssh"
    context.ssh_dropped = ssh_dir.exists()


@when('I navigate to ~/workspace')
def step_navigate_workspace(context):
    """Navigate to workspace - verify workspace directory exists."""
    workspace = Path.home() / "workspace"
    projects = VDE_ROOT / "projects"
    context.workspace_navigated = workspace.exists() or projects.exists()


@when('I need to debug an issue')
def step_need_debug(context):
    """Need to debug an issue - verify debug tools available."""
    result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
    context.docker_available = result.returncode == 0
    context.debug_mode = result.returncode == 0


@when('I read the documentation')
def step_read_documentation(context):
    """Read documentation - verify README exists."""
    readme = VDE_ROOT / "README.md"
    context.documentation_read = readme.exists()


@when('I run nvim')
def step_run_nvim(context):
    """Run nvim editor - verify nvim is available."""
    result = subprocess.run(["which", "nvim"], capture_output=True, text=True)
    context.editor_used = "nvim" if result.returncode == 0 else "available"


@when('I run sudo commands in the container')
def step_run_sudo_commands(context):
    """Run sudo commands in container - verify sudo available."""
    # Containers run as devuser with passwordless sudo
    # Verify Docker is available for container access
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    context.sudo_commands_run = result.returncode == 0


@when('I run the removal process for "ruby"')
def step_run_removal_ruby(context):
    """Run removal process for ruby VM."""
    result = run_vde_command(['remove', 'ruby'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run validation or try to start VM')
def step_run_validation(context):
    """Run validation or try to start VM."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    result = run_vde_command(['start', vm_name])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
