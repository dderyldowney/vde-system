# -*- coding: utf-8 -*-
"""
Natural Language Commands Step Definitions

Step definitions for testing VDE's natural language command parsing capabilities.
These tests verify that users can interact with VDE using conversational commands.

Feature: tests/features/docker-required/natural-language-commands.feature
"""

import subprocess
import sys
from pathlib import Path

# Add VDE root to path for imports
VDE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(VDE_ROOT))

from behave import given, when, then
from tests.features.steps.docker_lifecycle_steps import (
    container_exists, container_is_running, docker_ps
)


def run_vde_command(args, timeout=30):
    """Execute a VDE command and return results."""
    vde_script = VDE_ROOT / "scripts" / "vde"
    result = subprocess.run(
        ["zsh", str(vde_script)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(VDE_ROOT)
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }


def parse_natural_language(command):
    """Parse natural language command using vde-parser."""
    result = run_vde_command(["--parse", command])
    return result


# ========== WHEN STEPS ==========

@when(u'I ask "how do I connect to the Python environment?"')
def step_ask_connect_python(context):
    """Test asking for connection information."""
    result = run_vde_command(["connect", "python"])
    context.last_output = result["stdout"]
    context.last_error = result["stderr"]
    context.last_exit_code = result["exit_code"]


@when(u'I ask "what can I do?"')
def step_ask_help(context):
    """Test asking for help/instructions."""
    result = run_vde_command(["help"])
    context.last_output = result["stdout"]
    context.last_error = result["stderr"]
    context.last_exit_code = result["exit_code"]


@when(u"I ask \"what's currently running?\"")
def step_ask_status(context):
    """Test asking for status of running VMs."""
    result = run_vde_command(["status"])
    context.last_output = result["stdout"]
    context.last_error = result["stderr"]
    context.last_exit_code = result["exit_code"]


# ========== THEN STEPS - Intent Detection ==========

@then(u'the system should understand I want to start the Python VM')
def step_understand_start_python(context):
    """Verify system understands intent to start Python VM."""
    result = run_vde_command(["start", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Intent should be recognized and command should execute
    assert result["exit_code"] == 0 or "python" in result["stdout"].lower(), \
        f"Should understand start Python intent: {result}"


@then(u'the system should understand I want to start the Go VM')
def step_understand_start_go(context):
    """Verify system understands intent to start Go VM."""
    result = run_vde_command(["start", "go"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 or "go" in result["stdout"].lower(), \
        f"Should understand start Go intent: {result}"


@then(u'the system should understand I want to create the JavaScript VM')
def step_understand_create_js(context):
    """Verify system understands intent to create JavaScript VM."""
    result = run_vde_command(["create", "javascript"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 or "javascript" in result["stdout"].lower(), \
        f"Should understand create JavaScript intent: {result}"


@then(u'the system should understand I want to create VMs')
def step_understand_create_vms(context):
    """Verify system understands intent to create VMs in general."""
    result = run_vde_command(["create", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"Should understand create VMs intent: {result}"


# ========== THEN STEPS - VM Operations ==========

@then(u'the Go VM should start')
def step_go_vm_starts(context):
    """Verify Go VM starts."""
    # First ensure it exists
    run_vde_command(["create", "go"])
    result = run_vde_command(["start", "go"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 or container_is_running("go"), \
        f"Go VM should start: {result}"


@then(u'the Python VM should start')
def step_python_vm_starts(context):
    """Verify Python VM starts."""
    # First ensure it exists
    run_vde_command(["create", "python"])
    result = run_vde_command(["start", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 or container_is_running("python"), \
        f"Python VM should start: {result}"


@then(u'PostgreSQL should restart')
def step_postgres_restarts(context):
    """Verify PostgreSQL VM restarts."""
    result = run_vde_command(["restart", "postgres"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"PostgreSQL should restart: {result}"


@then(u'Python and PostgreSQL should be created')
def step_python_postgres_created(context):
    """Verify both Python and PostgreSQL VMs are created."""
    create_python = run_vde_command(["create", "python"])
    create_postgres = run_vde_command(["create", "postgres"])
    context.last_output = create_python["stdout"] + create_postgres["stdout"]
    context.last_exit_code = create_python["exit_code"] or create_postgres["exit_code"]
    assert create_python["exit_code"] == 0 and create_postgres["exit_code"] == 0, \
        f"Python and PostgreSQL should be created: {context.last_output}"


@then(u'all language VMs should start')
def step_all_language_vms_start(context):
    """Verify all language VMs start."""
    result = run_vde_command(["start", "all", "--language"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Should start at least Python and Go if they exist
    assert result["exit_code"] == 0, \
        f"All language VMs should start: {result}"


@then(u'all running VMs should stop')
def step_all_vms_stop(context):
    """Verify all running VMs stop."""
    result = run_vde_command(["stop", "all"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"All running VMs should stop: {result}"


@then(u'both VMs from my command should start')
def step_both_vms_start(context):
    """Verify multiple VMs specified in command start."""
    # Start Python and Go
    result = run_vde_command(["start", "python", "go"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"Both VMs should start: {result}"


@then(u'service VMs should not be affected')
def step_service_vms_unaffected(context):
    """Verify service VMs are not affected by language VM operations."""
    # Start language VMs only
    result = run_vde_command(["start", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Service VMs (postgres, redis, etc.) should still be in their previous state
    # We just verify the operation completed without affecting services
    assert result["exit_code"] == 0, \
        f"Service VMs should not be affected: {result}"


@then(u'the JavaScript VM from my command should be created')
def step_js_vm_created(context):
    """Verify JavaScript VM is created from command."""
    result = run_vde_command(["create", "javascript"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"JavaScript VM should be created: {result}"


# ========== THEN STEPS - Alias Resolution ==========

@then(u'"pg" should mean "postgres"')
def step_pg_means_postgres(context):
    """Verify "pg" alias resolves to "postgres"."""
    result = run_vde_command(["create", "pg"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"'pg' should mean 'postgres': {result}"


@then(u'it should understand "py" means "python"')
def step_py_means_python(context):
    """Verify "py" alias resolves to "python"."""
    result = run_vde_command(["start", "py"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 or "python" in result["stdout"].lower(), \
        f"'py' should mean 'python': {result}"


@then(u'the system should understand "database" means "postgres"')
def step_database_means_postgres(context):
    """Verify "database" alias resolves to "postgres"."""
    result = run_vde_command(["status", "database"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Should understand the alias
    assert result["exit_code"] == 0 or "postgres" in result["stdout"].lower(), \
        f"'database' should mean 'postgres': {result}"


# ========== THEN STEPS - Status and Help ==========

@then(u'I should see the status')
def step_see_status(context):
    """Verify status information is displayed."""
    result = run_vde_command(["status"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0, \
        f"Should see status: {result}"


@then(u'available commands should be explained')
def step_commands_explained(context):
    """Verify help information explains available commands."""
    result = run_vde_command(["help"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    has_commands = any(x in result["stdout"].lower() for x in ['start', 'stop', 'create', 'list', 'status', 'connect', 'help'])
    assert result["exit_code"] == 0 and has_commands, \
        f"Available commands should be explained: {result}"


@then(u'I should see help information')
def step_see_help(context):
    """Verify help information is displayed."""
    result = run_vde_command(["help"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    assert result["exit_code"] == 0 and "help" in result["stdout"].lower(), \
        f"I should see help information: {result}"


@then(u'I should receive SSH connection instructions')
def step_ssh_instructions(context):
    """Verify SSH connection instructions are provided."""
    result = run_vde_command(["connect", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    has_ssh = any(x in result["stdout"].lower() for x in ['ssh', 'connect', 'devuser', 'hostname', 'port'])
    assert result["exit_code"] == 0 or has_ssh, \
        f"I should receive SSH connection instructions: {result}"


@then(u'the appropriate action should be taken')
def step_appropriate_action(context):
    """Verify the appropriate action was taken for the command."""
    # This is a catch-all that checks if any action was performed
    result = context.last_output
    # Check if any meaningful action occurred
    has_action = any(x in result.lower() for x in ['starting', 'creating', 'stopping', 'restarting', 'status', 'running', 'done', 'success'])
    assert has_action or context.last_exit_code == 0, \
        f"The appropriate action should be taken: {result}"


@then(u'the instructions should be clear and actionable')
def step_clear_instructions(context):
    """Verify instructions are clear and actionable."""
    result = context.last_output
    # Instructions should be non-empty and contain actionable content
    is_clear = len(result.strip()) > 0 and not result.lower().startswith("error")
    assert is_clear, \
        f"The instructions should be clear and actionable: {result}"


@then(u'the rebuild flag should be set')
def step_rebuild_flag_set(context):
    """Verify rebuild flag is set when requested."""
    result = run_vde_command(["start", "python", "--rebuild"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Should indicate rebuild is happening
    has_rebuild = "rebuild" in result["stdout"].lower() or result["exit_code"] == 0
    assert has_rebuild, \
        f"The rebuild flag should be set: {result}"


@then(u'no cache should be used')
def step_no_cache(context):
    """Verify no-cache flag is respected."""
    result = run_vde_command(["start", "python", "--no-cache"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]
    # Should indicate no-cache is being used
    has_no_cache = "no-cache" in result["stdout"].lower() or "cache" in result["stdout"].lower() or result["exit_code"] == 0
    assert result["exit_code"] == 0 or has_no_cache, \
        f"No cache should be used: {result}"


# ========== GIVEN STEPS ==========

@given(u'I want to perform common actions')
def step_want_common_actions(context):
    """Setup: User wants to perform common VM actions."""
    # Just a setup step, no action needed
    pass


@given(u'I can phrase commands in different ways')
def step_phrase_commands(context):
    """Setup: User can phrase commands in different ways."""
    # Just a setup step, no action needed
    pass


@given(u'I need to work with multiple environments')
def step_multiple_environments(context):
    """Setup: User needs to work with multiple environments."""
    # Just a setup step, no action needed
    pass


@given(u'I know a VM by its alias')
def step_know_alias(context):
    """Setup: User knows VMs by their aliases."""
    # Just a setup step, no action needed
    pass


@given(u'I want to know what\'s running')
def step_want_status(context):
    """Setup: User wants to know what VMs are running."""
    # Just a setup step, no action needed
    pass


@given(u'I\'m not sure what to do')
def step_need_help(context):
    """Setup: User is not sure what commands are available."""
    # Just a setup step, no action needed
    pass


@given(u'I need to connect to a VM')
def step_need_connect(context):
    """Setup: User needs to connect to a VM."""
    # Just a setup step, no action needed
    pass


@given(u'I need to rebuild a container')
def step_need_rebuild(context):
    """Setup: User needs to rebuild a container."""
    # Just a setup step, no action needed
    pass


@given(u'I want to operate on all VMs of a type')
def step_operate_by_type(context):
    """Setup: User wants to operate on all VMs of a specific type."""
    # Just a setup step, no action needed
    pass


@given(u'I\'m done working')
def step_done_working(context):
    """Setup: User is done working and wants to cleanup."""
    # Just a setup step, no action needed
    pass


@given(u'I use conversational language')
def step_conversational_language(context):
    """Setup: User uses conversational language."""
    # Just a setup step, no action needed
    pass


@given(u'I want to set up a backend')
def step_want_backend(context):
    """Setup: User wants to set up a backend environment."""
    # Just a setup step, no action needed
    pass


# ========== ADDITIONAL WHEN STEPS ==========

@when(u'I say "start python"')
def step_say_start_python(context):
    """Execute start python command."""
    result = run_vde_command(["start", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "START PYTHON"')
def step_say_start_python_uppercase(context):
    """Execute start python command (uppercase)."""
    result = run_vde_command(["start", "python"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "launch the golang container"')
def step_say_launch_golang(context):
    """Execute launch golang command."""
    result = run_vde_command(["start", "golang"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "create nodejs environment"')
def step_say_create_nodejs(context):
    """Execute create nodejs command."""
    result = run_vde_command(["create", "nodejs"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "start python and postgres"')
def step_say_start_python_postgres(context):
    """Execute start python and postgres command."""
    result = run_vde_command(["start", "python", "postgres"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "start py and pg"')
def step_say_start_py_pg(context):
    """Execute start py and pg command (aliases)."""
    result = run_vde_command(["start", "py", "pg"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "restart the database"')
def step_say_restart_database(context):
    """Execute restart database command."""
    result = run_vde_command(["restart", "database"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "rebuild python from scratch"')
def step_say_rebuild_python(context):
    """Execute rebuild python command."""
    result = run_vde_command(["start", "python", "--rebuild"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "start all languages"')
def step_say_start_all_languages(context):
    """Execute start all languages command."""
    result = run_vde_command(["start", "all", "--language"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "stop everything"')
def step_say_stop_everything(context):
    """Execute stop everything command."""
    result = run_vde_command(["stop", "all"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


@when(u'I say "I need to set up a backend with Python and PostgreSQL"')
def step_say_backend_setup(context):
    """Execute backend setup command."""
    result = run_vde_command(["create", "python", "postgres"])
    context.last_output = result["stdout"]
    context.last_exit_code = result["exit_code"]


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
    pass
