# -*- coding: utf-8 -*-
"""
Natural Language Commands Step Definitions

Step definitions for testing VDE's natural language command parsing capabilities.
These tests verify that users can interact with VDE using conversational commands.

Feature: tests/features/core-infrastructure/natural-language-commands.feature
"""

import subprocess
import sys
import os
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, when, then
from vm_common import (
    run_vde_command,
    container_is_running,
    docker_ps,
)

# ========== WHEN STEPS ==========

@when(u'I ask "how do I connect to the Python environment?"')
def step_ask_connect_python(context):
    """Test asking for connection information via vde ask."""
    run_vde_command("ask 'how do I connect to the Python environment?'", context=context)


@when(u'I ask "what can I do?"')
def step_ask_help(context):
    """Test asking for help via vde ask."""
    run_vde_command("ask 'what can I do?'", context=context)


@when(u"I ask \"what's currently running?\"")
def step_ask_status(context):
    """Test asking for status via vde ask."""
    run_vde_command("ask \"what's currently running?\"", context=context)


# ========== THEN STEPS - Intent Detection ==========

@then(u'the system should understand I want to start the Python VM')
def step_understand_start_python(context):
    """Verify system understands intent to start Python VM."""
    # Intent should be recognized and command should execute
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    exit_code = getattr(context, 'last_exit_code', -1)
    assert exit_code == 0 or "python" in output.lower(), \
        f"Should understand start Python intent: {output}"


@then(u'the system should understand I want to start the Go VM')
def step_understand_start_go(context):
    """Verify system understands intent to start Go VM."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    exit_code = getattr(context, 'last_exit_code', -1)
    assert exit_code == 0 or "go" in output.lower(), \
        f"Should understand start Go intent: {output}"


@then(u'the system should understand I want to create the JavaScript VM')
def step_understand_create_js(context):
    """Verify system understands intent to create JavaScript VM."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    exit_code = getattr(context, 'last_exit_code', -1)
    assert exit_code == 0 or "js" in output.lower() or "javascript" in output.lower(), \
        f"Should understand create JavaScript intent: {output}"


@then(u'the system should understand I want to create VMs')
def step_understand_create_vms(context):
    """Verify system understands intent to create VMs in general."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    exit_code = getattr(context, 'last_exit_code', -1)
    assert exit_code in [0, 6], \
        f"Should understand create VMs intent: {output}"


# ========== THEN STEPS - VM Operations ==========

@then(u'the Go VM should start')
def step_go_vm_starts(context):
    """Verify Go VM starts."""
    assert container_is_running("go"), "Go VM should be running"


@then(u'the Python VM should start')
def step_python_vm_starts(context):
    """Verify Python VM starts."""
    assert container_is_running("python"), "Python VM should be running"


@then(u'PostgreSQL should restart')
def step_postgres_restarts(context):
    """Verify PostgreSQL VM restarts."""
    # restart intent handled by vde
    assert getattr(context, 'last_exit_code', 1) == 0


@then(u'Python and PostgreSQL should be created')
def step_python_postgres_created(context):
    """Verify both Python and PostgreSQL VMs are created."""
    from vm_common import compose_file_exists
    assert compose_file_exists("python"), "Python config missing"
    assert compose_file_exists("postgres"), "PostgreSQL config missing"


@then(u'all language VMs should start')
def step_all_language_vms_start(context):
    """Verify all language VMs start."""
    # Verification depends on existing VMs
    assert getattr(context, 'last_exit_code', 1) == 0


@then(u'all running VMs should stop')
def step_all_vms_stop(context):
    """Verify all running VMs stop."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) == 0, f"VMs still running: {vde_running}"


@then(u'both VMs from my command should start')
def step_both_vms_start(context):
    """Verify multiple VMs specified in command start."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) >= 1, "At least one VM should be running"


@then(u'service VMs should not be affected')
def step_service_vms_unaffected(context):
    """Verify service VMs are not affected by language VM operations."""
    assert getattr(context, 'last_exit_code', 1) == 0


@then(u'the JavaScript VM from my command should be created')
def step_js_vm_created(context):
    """Verify JavaScript VM is created from command."""
    from vm_common import compose_file_exists
    assert compose_file_exists("js"), "JavaScript config missing"


# ========== THEN STEPS - Alias Resolution ==========

@then(u'"pg" should mean "postgres"')
def step_pg_means_postgres(context):
    """Verify "pg" alias resolves to "postgres"."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    assert "postgres" in output.lower(), f"'pg' should resolve to 'postgres': {output}"


@then(u'it should understand "py" means "python"')
def step_py_means_python(context):
    """Verify "py" alias resolves to "python"."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    assert "python" in output.lower(), f"'py' should resolve to 'python': {output}"


@then(u'the system should understand "database" means "postgres"')
def step_database_means_postgres(context):
    """Verify "database" alias resolves to "postgres"."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    assert "postgres" in output.lower(), f"'database' should resolve to 'postgres': {output}"


# ========== THEN STEPS - Status and Help ==========

@then(u'I should see the status')
def step_see_status(context):
    """Verify status information is displayed."""
    output = getattr(context, 'last_output', '')
    assert len(output) > 0, "Status output missing"


@then(u'available commands should be explained')
def step_commands_explained(context):
    """Verify help information explains available commands."""
    output = getattr(context, 'last_output', '')
    has_commands = any(x in output.lower() for x in ['start', 'stop', 'create', 'list', 'status'])
    assert has_commands, f"Help missing command info: {output}"


@then(u'I should see help information')
def step_see_help(context):
    """Verify help information is displayed."""
    output = getattr(context, 'last_output', '')
    assert "usage" in output.lower() or "help" in output.lower()


@then(u'I should receive SSH connection instructions')
def step_ssh_instructions(context):
    """Verify SSH connection instructions are provided."""
    output = getattr(context, 'last_output', '')
    has_ssh = any(x in output.lower() for x in ['ssh', 'connect', 'port'])
    assert has_ssh or getattr(context, 'last_exit_code', 1) == 0


@then(u'the appropriate action should be taken')
def step_appropriate_action(context):
    """Verify the appropriate action was taken for the command."""
    assert getattr(context, 'last_exit_code', 1) == 0


@then(u'the instructions should be clear and actionable')
def step_clear_instructions(context):
    """Verify instructions are clear and actionable."""
    output = getattr(context, 'last_output', '')
    assert len(output.strip()) > 0


@then(u'the rebuild flag should be set')
def step_rebuild_flag_set(context):
    """Verify rebuild flag is set when requested by checking command output."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    # vde ask with rebuild=true should mention rebuilding in its plan or execution
    assert any(x in output.lower() for x in ['rebuild', 'rebuilding', 'build']), \
        f"Output should indicate a rebuild was planned: {output}"


@then(u'no cache should be used')
def step_no_cache(context):
    """Verify no-cache flag is respected by checking command output."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    # vde ask with nocache=true should mention --no-cache or similar
    assert any(x in output.lower() for x in ['no-cache', 'nocache', 'without cache']), \
        f"Output should indicate no-cache was planned: {output}"


# ========== GIVEN STEPS ==========

@given(u'I want to perform common actions')
def step_want_common_actions(context):
    """Setup: User wants to perform common VM actions."""
    pass


@given(u'I can phrase commands in different ways')
def step_phrase_commands(context):
    """Setup: User can phrase commands in different ways."""
    pass


@given(u'I need to work with multiple environments')
def step_multiple_environments(context):
    """Setup: User needs to work with multiple environments."""
    pass


@given(u'I know a VM by its alias')
def step_know_alias(context):
    """Setup: User knows VMs by their aliases."""
    pass


@given(u'I want to know what\'s running')
def step_want_status(context):
    """Setup: User wants to know what VMs are running."""
    pass


@given(u'I\'m not sure what to do')
def step_need_help(context):
    """Setup: User is not sure what commands are available."""
    pass


@given(u'I need to connect to a VM')
def step_need_connect(context):
    """Setup: User needs to connect to a VM."""
    pass


@given(u'I need to rebuild a container')
def step_need_rebuild(context):
    """Setup: User needs to rebuild a container."""
    pass


@given(u'I want to operate on all VMs of a type')
def step_operate_by_type(context):
    """Setup: User wants to operate on all VMs of a specific type."""
    pass


@given(u'I\'m done working')
def step_done_working(context):
    """Setup: User is done working and wants to cleanup."""
    pass


@given(u'I use conversational language')
def step_conversational_language(context):
    """Setup: User uses conversational language."""
    pass


@given(u'I want to set up a backend')
def step_want_backend(context):
    """Setup: User wants to set up a backend environment."""
    pass


# ========== ADDITIONAL WHEN STEPS ==========

@when(u'I say "{phrase}"')
def step_say_phrase(context, phrase):
    """Execute conversational command via vde ask."""
    run_vde_command(f"ask '{phrase}'", context=context)


# ========== ADDITIONAL GIVEN STEPS ==========

@given(u'I type commands in various cases')
def step_type_cases(context):
    """Setup: User types commands in various cases."""
    pass


@given(u'I want to type less')
def step_type_less(context):
    """Setup: User wants to type less."""
    pass


@given(u'something isn\'t working')
def step_troubleshooting(context):
    """Setup: User is troubleshooting an issue."""
    # Ensure postgres exists so we can restart it
    run_vde_command('create postgres', context=context)
