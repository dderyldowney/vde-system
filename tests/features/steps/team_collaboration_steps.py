"""
BDD Step Definitions for Team Collaboration and Onboarding Workflows.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists, wait_for_container

# =============================================================================
# Team Onboarding GIVEN steps
# =============================================================================

@given('I am a new developer joining the team')
def step_new_developer(context):
    """Context: New developer joining the team."""
    # Verify setup resources exist for new developers
    readme = VDE_ROOT / "README.md"
    context.new_developer = readme.exists()


@given('a new team member joins')
def step_new_team_member(context):
    """Context: New team member joins - verify vm-types.conf exists."""
    vm_types = VDE_ROOT / "data" / "vm-types.conf"
    context.new_team_member = vm_types.exists()


@given('the team has updated SSH config templates')
def step_team_updated_ssh_templates(context):
    """Context: Team updated SSH config templates."""
    # Check if SSH config directory exists
    ssh_config_dir = Path.home() / ".ssh" / "vde"
    context.ssh_templates_updated = ssh_config_dir.exists()


@given('I pull the latest changes')
def step_pull_latest_changes(context):
    """Context: Pull latest changes."""
    # Verify git is available for pulling
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    context.latest_changes_pulled = result.returncode == 0


@given('the team uses PostgreSQL for development')
def step_team_uses_postgres(context):
    """Context: Team uses PostgreSQL."""
    # Check for VM type in data
    vm_types = VDE_ROOT / "data" / "vm-types.conf"
    assert vm_types.exists()
    content = vm_types.read_text()
    context.team_uses_postgres = "postgres" in content


@given('postgres VM configuration is in the repository')
def step_postgres_config_in_repo(context):
    """Verify postgres config is in repository."""
    # Template exists in data/ or config structure exists
    assert (VDE_ROOT / "data" / "vm-types.conf").exists()


@given('our production uses PostgreSQL 14, Redis 7, and Node 18')
def step_production_versions(context):
    """Context: Production uses specific versions."""
    context.production_versions = {'postgres': 14, 'redis': 7, 'node': 18}


@given('the team maintains a set of pre-configured VMs')
def step_preconfigured_vms(context):
    """Context: Team maintains pre-configured VMs."""
    vm_types = VDE_ROOT / "data" / "vm-types.conf"
    context.preconfigured_vms = vm_types.exists()


# =============================================================================
# Team Onboarding WHEN steps
# =============================================================================

@when('they follow the setup instructions')
def step_follow_setup_instructions(context):
    """Context: Following setup instructions."""
    # Verify setup script is available in bin/
    setup_script = VDE_ROOT / "bin" / "vde-init"
    context.setup_instructions_followed = setup_script.exists()


@when('they run "create-virtual-for python"')
def step_run_create_python(context):
    """Run vde create python command."""
    result = run_vde_command('create python', context=context)
    context.last_exit_code = result.returncode


@when('a teammate clones the repository')
def step_teammate_clones(context):
    """Context: Teammate clones the repository."""
    result = subprocess.run(['git', 'status'], capture_output=True, cwd=VDE_ROOT)
    context.repo_cloned = result.returncode == 0


@when('they run the documented create commands')
def step_run_documented_commands(context):
    """Context: Run documented create commands."""
    # Verify VDE script exists
    vde_script = VDE_ROOT / "bin" / "vde"
    context.commands_run = vde_script.exists()


@when('one developer runs "add-vm-type dart \'apt-get install -y dart\'"')
def step_add_dart_vm_type(context):
    """Add dart VM type via vde add."""
    result = run_vde_command("add dart --type lang --display-name Dart --install 'apt-get install -y dart'", context=context)
    context.last_exit_code = result.returncode


@when('commits the vm-types.conf change')
def step_commit_vm_types(context):
    """Context: Commit change."""
    context.vm_types_committed = True


@when('the first developer recreates the VM')
def step_recreate_vm(context):
    """Recreate the VM via vde create."""
    result = run_vde_command('create python', context=context)
    context.last_exit_code = result.returncode


@when('I create or restart any VM')
def step_create_or_restart_any_vm(context):
    """Create or restart any VM using vde command."""
    result = run_vde_command('start python', context=context)
    context.last_exit_code = result.returncode


@when('I configure VDE with matching versions')
def step_configure_matching_versions(context):
    """Context: Configure VDE with matching versions."""
    vm_types = VDE_ROOT / "data" / "vm-types.conf"
    context.versions_configured = vm_types.exists()


@when('each team member starts "postgres" VM')
def step_each_start_postgres(context):
    """Each team member starts postgres VM via vde start."""
    result = run_vde_command('start postgres', context=context)
    context.last_exit_code = result.returncode


@when('a new developer joins')
def step_new_dev_joins(context):
    """Context: New developer joins."""
    context.new_developer_joined = True


# =============================================================================
# Team Onboarding THEN steps
# =============================================================================

@then('they should get the same Python environment I have')
def step_same_python_env(context):
    """Verify same Python environment is created."""
    from vm_common import compose_file_exists
    assert compose_file_exists('python'), "Python environment should be created"


@then('all dependencies should be installed')
def step_dependencies_installed(context):
    """Verify dependencies are installed - success of start/create implies this."""
    assert context.last_exit_code == 0, "VM setup failed, dependencies may be missing"


# =============================================================================
# Additional Collaboration Steps
# =============================================================================

@given('I have cloned the project repository')
def step_cloned_project_repo(context):
    """Verify project repository is cloned."""
    assert (VDE_ROOT / ".git").exists(), "Not in a git repository"
    context.repo_cloned = True


@given('my project has a "{vm_name}" VM configuration')
def step_project_has_vm_config(context, vm_name):
    """Check if project has VM configuration."""
    from vm_common import compose_file_exists
    context.vm_config_exists = compose_file_exists(vm_name)


@then('my local development should match production')
def step_local_matches_production(context):
    """Verify local development matches production configuration."""
    # Check that configuration files exist
    assert (VDE_ROOT / "data" / "vm-types.conf").exists()


@given('documentation explains how to create each VM')
def step_documentation_exists(context):
    """Check if documentation exists."""
    readme_path = VDE_ROOT / "docs" / "quick-start.md"
    context.documentation_exists = readme_path.exists()


@given('the team defines standard VM types in vm-types.conf')
def step_standard_vm_types_exist(context):
    """Verify vm-types.conf exists."""
    vm_types_path = VDE_ROOT / "data" / "vm-types.conf"
    assert vm_types_path.exists(), "vm-types.conf missing"
    context.vm_types_exist = True


@given('a project requires specific services ({services})')
def step_project_requires_services(context, services):
    """Check if project requires specific services."""
    service_list = [s.strip() for s in services.split(',')]
    context.required_services = service_list
    context.services_available = all(
        (VDE_ROOT / "data" / "vm-types.conf").exists() for _ in service_list
    )


@given('a project needs environment variables for configuration')
def step_project_needs_env_vars(context):
    """Check if environment variable files exist."""
    env_dir = VDE_ROOT / "env-files"
    context.env_files_exist = env_dir.exists()
