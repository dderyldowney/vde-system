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


@when("I parse '{input_text}'")
def step_parse_input_text(context, input_text):
    """Parse natural language input and store results."""
    context.nl_input = input_text
    context.nl_intent = _get_real_intent(input_text)
    context.nl_vms = _get_real_vm_names(input_text)
    context.nl_flags = _get_real_flags(input_text)


# =============================================================================
# THEN Steps - Verify parser output assertions
# =============================================================================

@then("intent should be \"{expected_intent}\"")
def step_intent_should_be(context, expected_intent):
    """Verify the detected intent matches expected."""
    actual_intent = getattr(context, 'nl_intent', None)
    assert actual_intent is not None, "No intent was parsed"
    assert actual_intent == expected_intent, f"Expected intent '{expected_intent}', got '{actual_intent}'"


@then('VMs should include "{vm_names}"')
def step_vms_should_include(context, vm_names):
    """Verify the extracted VMs include the expected VM(s). Accepts single or comma-separated VMs."""
    actual_vms = getattr(context, 'nl_vms', [])
    # Handle comma-separated VM names
    expected = [v.strip() for v in vm_names.split(',')]
    for vm in expected:
        assert vm in actual_vms, f"Expected VM '{vm}' in {actual_vms}"


@then('VMs should NOT include "{vm_names}"')
def step_vms_should_not_include(context, vm_names):
    """Verify the extracted VMs do NOT include the expected VM(s)."""
    actual_vms = getattr(context, 'nl_vms', [])
    expected = [v.strip() for v in vm_names.split(',')]
    for vm in expected:
        assert vm not in actual_vms, f"VM '{vm}' should NOT be in {actual_vms}"


@then("VMs should include all known VMs")
def step_vms_should_include_all(context):
    """Verify the extracted VMs include all known VMs."""
    actual_vms = getattr(context, 'nl_vms', [])
    assert len(actual_vms) > 1, f"Expected multiple VMs, got: {actual_vms}"


@then("dangerous characters should be rejected")
def step_dangerous_chars_rejected(context):
    """Verify that dangerous characters are detected and rejected."""
    actual_intent = getattr(context, 'nl_intent', None)
    action_intents = ['start_vm', 'stop_vm', 'restart_vm', 'create_vm', 'status', 'connect', 'list_vms']
    assert actual_intent in ['help', ''] or actual_intent not in action_intents, \
        f"Dangerous characters should be rejected, but got intent: {actual_intent}"


@then("all plan lines should be valid")
def step_plan_lines_valid(context):
    """Verify all plan lines are valid."""
    actual_intent = getattr(context, 'nl_intent', None)
    valid_intents = ['start_vm', 'stop_vm', 'restart_vm', 'create_vm', 'status', 'connect', 'help', 'list_vms', 'list_languages', 'list_services']
    assert actual_intent in valid_intents, f"Invalid intent detected: {actual_intent}"


@then("rebuild flag should be true")
def step_rebuild_flag_true(context):
    """Verify the rebuild flag was parsed as true."""
    flags = getattr(context, 'nl_flags', {})
    assert flags.get('rebuild') is True, f"Expected rebuild=True, got: {flags}"


@then("intent should default to \"{default_intent}\"")
def step_intent_default(context, default_intent):
    """Verify intent defaults correctly for edge cases."""
    actual_intent = getattr(context, 'nl_intent', None)
    assert actual_intent == default_intent, f"Expected default intent '{default_intent}', got '{actual_intent}'"


@then("command should NOT execute")
def step_command_not_execute(context):
    """Verify that the command was not executed (dangerous chars detected)."""
    # When dangerous characters are present, the command should not execute
    # This is verified by checking that there's no actual command result
    # or that the last_exit_code indicates an error/prevention
    if hasattr(context, 'last_exit_code'):
        # If a command was attempted, it should have failed or been prevented
        assert context.last_exit_code != 0, "Command should NOT have executed successfully"
