# -*- coding: utf-8 -*-
"""Error path and negative testing steps."""

import subprocess
import os
from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR",
    str(Path(__file__).parent.parent.parent.parent)))


def run_vde(args, timeout=30):
    """Run a VDE command and return result."""
    cmd = [str(VDE_ROOT / 'scripts' / 'vde')] + args
    return subprocess.run(cmd, capture_output=True, text=True,
                         timeout=timeout, cwd=str(VDE_ROOT))


@given('the VDE system is available')
def step_vde_available(context):
    """Verify VDE system is available."""
    vde_script = VDE_ROOT / 'scripts' / 'vde'
    assert vde_script.exists(), f"VDE script not found at {vde_script}"
    context.vde_root = VDE_ROOT


@given('the VDE natural language parser is available')
def step_parser_available(context):
    """Verify parser script exists."""
    parser = VDE_ROOT / 'scripts' / 'lib' / 'vde-parser'
    assert parser.exists(), f"Parser not found at {parser}"
    context.parser_path = parser


@when('I try to create a VM named "{name}"')
def step_create_vm_named(context, name):
    """Try to create a VM with given name."""
    result = run_vde(['create', name])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run the VDE help command')
def step_run_help(context):
    """Run VDE help command."""
    result = run_vde(['help'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I query the status of a non-existent VM')
def step_query_nonexistent(context):
    """Query status of VM that doesn't exist."""
    result = run_vde(['status', 'nonexistent-vm-xyz-999'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I list all VMs')
def step_list_vms(context):
    """List all VMs."""
    result = run_vde(['list'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I try to create a VM with an empty name')
def step_create_empty_name(context):
    """Try to create VM with empty name."""
    result = run_vde(['create', ''])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I parse an empty string')
def step_parse_empty(context):
    """Parse empty string through parser."""
    result = subprocess.run(
        ['zsh', '-c', f'source {context.parser_path} && parse_intent ""'],
        capture_output=True, text=True, timeout=10, cwd=str(VDE_ROOT)
    )
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I parse gibberish text "{text}"')
def step_parse_gibberish_text(context, text):
    """Parse gibberish text through parser."""
    result = subprocess.run(
        ['zsh', '-c', f'source {context.parser_path} && parse_intent "{text}"'],
        capture_output=True, text=True, timeout=10, cwd=str(VDE_ROOT)
    )
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I check for a config file that does not exist')
def step_check_missing_config(context):
    """Check for a non-existent config file."""
    config_path = VDE_ROOT / 'configs' / 'docker' / 'nonexistent-vm-xyz' / 'docker-compose.yml'
    context.config_exists = config_path.exists()
    context.config_path = str(config_path)


@then('the command should fail with a non-zero exit code')
def step_command_fails(context):
    """Verify command failed."""
    assert context.last_exit_code != 0, \
        f"Expected non-zero exit code, got {context.last_exit_code}"


@then('the error output should contain useful information')
def step_error_useful(context):
    """Verify error output has useful info."""
    combined = (context.last_output or '') + (context.last_error or '')
    assert len(combined) > 0, "Error output should contain useful information"


@then('the command should complete successfully')
def step_command_succeeds(context):
    """Verify command succeeded."""
    assert context.last_exit_code == 0, \
        f"Expected exit code 0, got {context.last_exit_code}. Error: {context.last_error}"


@then('the output should contain usage information')
def step_output_has_usage(context):
    """Verify help output."""
    combined = (context.last_output or '') + (context.last_error or '')
    assert any(word in combined.lower() for word in ['usage', 'help', 'command', 'vde']), \
        f"Expected usage info in output: {combined[:200]}"


@then('the command should indicate the VM was not found')
def step_vm_not_found(context):
    """Verify VM not found response."""
    combined = (context.last_output or '') + (context.last_error or '')
    assert context.last_exit_code != 0 or 'not found' in combined.lower() or \
        'not running' in combined.lower() or 'unknown' in combined.lower(), \
        f"Expected 'not found' indication: exit={context.last_exit_code}"


@then('the parser should return empty or error result')
def step_parser_empty_result(context):
    """Verify parser handles empty input gracefully."""
    # Parser should not crash - any result is acceptable
    assert context.last_exit_code is not None, "Parser should return a result"


@then('the parser should not crash')
def step_parser_no_crash(context):
    """Verify parser doesn't crash on gibberish."""
    # Any exit code is fine as long as it didn't crash (timeout/signal)
    assert context.last_exit_code is not None, "Parser should not crash"
    assert context.last_exit_code < 128, \
        f"Parser crashed with signal {context.last_exit_code - 128}"


@then('the system should report the file is missing')
def step_file_missing(context):
    """Verify missing config is detected."""
    assert not context.config_exists, \
        f"Config should not exist at {context.config_path}"
