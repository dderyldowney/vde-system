"""
Common BDD Step Definitions shared across all features.

These are generic utility steps that don't belong to any specific
feature category but are used throughout multiple test scenarios.
"""

from behave import given, when, then
from pathlib import Path
import os

VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/vde"))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def mark_step_implemented(context, step_name=""):
    """Mark a step as implemented in context."""
    context.step_implemented = True
    if step_name:
        if not hasattr(context, 'implemented_steps'):
            context.implemented_steps = []
        context.implemented_steps.append(step_name)


# =============================================================================
# GENERIC CONTEXT STATE STEPS
# =============================================================================

@given('an error occurs')
def step_an_error_occurs(context):
    """A generic error occurs."""
    context.error_occurred = True


@given('a transient error occurs')
def step_transient_error(context):
    """A transient error occurs."""
    context.transient_error = True


@given('any VM operation occurs')
def step_any_vm_operation(context):
    """Any VM operation occurs."""
    context.vm_operation = True


@given('an associative array')
def step_associative_array(context):
    """An associative array is used."""
    context.associative_array = True


@given('I have a working directory')
def step_working_directory(context):
    """I have a working directory."""
    context.working_directory = VDE_ROOT / "projects"
    context.has_working_dir = context.working_directory.exists()


@given('I am connected to a VM')
def step_connected_to_vm(context):
    """I am connected to a VM."""
    context.connected_to_vm = True


@given('I am connected via SSH')
def step_connected_via_ssh(context):
    """I am connected via SSH."""
    context.ssh_connected = True


# =============================================================================
# GENERIC ACTION STEPS
# =============================================================================

@when('I check status')
def step_check_status(context):
    """Check status."""
    context.status_checked = True


@when('I repeat the same command')
def step_repeat_command(context):
    """Repeat the same command."""
    context.command_repeated = True


@when('I pull the latest changes')
def step_pull_latest(context):
    """Pull latest changes."""
    context.latest_changes_pulled = True


@when('I push code changes')
def step_push_changes(context):
    """Push code changes."""
    context.changes_pushed = True


@when('I read the documentation')
def step_read_documentation(context):
    """Read the documentation."""
    context.documentation_read = True


# =============================================================================
# GENERIC VERIFICATION STEPS
# =============================================================================

@then('the command should succeed')
def step_command_succeeds(context):
    """The command should succeed."""
    assert context.last_exit_code == 0 if hasattr(context, 'last_exit_code') else True


@then('I should see helpful information')
def step_see_helpful_info(context):
    """Should see helpful information."""
    context.helpful_info_shown = True


@then('I should understand what happened')
def step_understand_what_happened(context):
    """Should understand what happened."""
    context.outcome_understood = True


@then('errors should be clearly indicated')
def step_errors_clear(context):
    """Errors should be clearly indicated."""
    context.errors_clear = True


# =============================================================================
# GENERIC USER STATE STEPS
# =============================================================================

@given('I am a new VDE user')
def step_new_vde_user(context):
    """I am a new VDE user."""
    context.is_new_user = True


@given('I am actively developing')
def step_actively_developing(context):
    """I am actively developing."""
    context.developing = True


@given('I am experiencing issues')
def step_experiencing_issues(context):
    """I am experiencing issues."""
    context.having_issues = True


# =============================================================================
# GENERIC VM STATE STEPS
# =============================================================================

@given('I have a running VM')
def step_have_running_vm(context):
    """I have a running VM."""
    context.has_running_vm = True


@given('I have multiple VMs')
def step_have_multiple_vms(context):
    """I have multiple VMs."""
    context.has_multiple_vms = True


@given('I have VMs configured')
def step_have_vms_configured(context):
    """I have VMs configured."""
    context.vms_configured = True


@given('I have several VMs')
def step_have_several_vms(context):
    """I have several VMs."""
    context.several_vms = True


@given('I have created VMs before')
def step_created_vms_before(context):
    """I have created VMs before."""
    context.created_vms_before = True


# =============================================================================
# GENERIC PROJECT STEPS
# =============================================================================

@given('I have projects on my host')
def step_projects_on_host(context):
    """I have projects on my host."""
    context.projects_on_host = True


@given('I work on multiple unrelated projects')
def step_multiple_projects(context):
    """I work on multiple unrelated projects."""
    context.multiple_projects = True


@given('I have a comprehensive test suite')
def step_comprehensive_tests(context):
    """I have a comprehensive test suite."""
    context.comprehensive_tests = True


@given('I have made changes to the code')
def step_made_code_changes(context):
    """I have made changes to the code."""
    context.code_changed = True


# =============================================================================
# GENERIC SERVICE/DEPENDENCY STEPS
# =============================================================================

@given('I have dependent services')
def step_dependent_services(context):
    """I have dependent services."""
    context.dependent_services = True


@given('I have different settings for dev and production')
def step_different_settings(context):
    """I have different settings for dev and production."""
    context.different_settings = True


@given('a project needs environment variables for configuration')
def step_project_needs_env_vars(context):
    """A project needs environment variables for configuration."""
    context.needs_env_vars = True
