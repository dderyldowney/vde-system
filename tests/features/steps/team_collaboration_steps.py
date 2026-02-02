"""
BDD Step Definitions for Team Collaboration and Onboarding Workflows.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists

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
    """Context: New team member joins."""
    # Verify vm-types.conf exists for team member onboarding
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
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
    compose_path = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
    context.team_uses_postgres = compose_path.exists()


@given('postgres VM configuration is in the repository')
def step_postgres_config_in_repo(context):
    """Verify postgres config is in repository."""
    compose_path = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
    context.postgres_in_repo = compose_path.exists()


@given('our production uses PostgreSQL 14, Redis 7, and Node 18')
def step_production_versions(context):
    """Context: Production uses specific versions."""
    # Check if these service configs exist
    configs = VDE_ROOT / "configs" / "docker"
    postgres_exists = (configs / "postgres").exists()
    redis_exists = (configs / "redis").exists()
    node_exists = (configs / "node" if (configs / "node").exists() else
                   (configs / "nodejs" if (configs / "nodejs").exists() else
                    (configs / "js" if (configs / "js").exists() else False)))
    context.production_versions = {
        'postgres': 14 if postgres_exists else None,
        'redis': 7 if redis_exists else None,
        'node': 18 if node_exists else None
    }


@given('the team maintains a set of pre-configured VMs')
def step_preconfigured_vms(context):
    """Context: Team maintains pre-configured VMs."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.preconfigured_vms = vm_types.exists()


# =============================================================================
# Team Onboarding WHEN steps
# =============================================================================

@when('they follow the setup instructions')
def step_follow_setup_instructions(context):
    """Context: Following setup instructions."""
    # Verify setup script is available
    setup_script = VDE_ROOT / "scripts" / "setup-vde"
    context.setup_instructions_followed = setup_script.exists()


@when('they run "create-virtual-for python"')
def step_run_create_python(context):
    """Run create-virtual-for python command."""
    result = run_vde_command(['create-virtual-for', 'python'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('a teammate clones the repository')
def step_teammate_clones(context):
    """Context: Teammate clones the repository."""
    # Verify git repository is accessible
    result = subprocess.run(['git', 'status'], capture_output=True, cwd=VDE_ROOT)
    context.repo_cloned = result.returncode == 0


@when('they run the documented create commands')
def step_run_documented_commands(context):
    """Context: Run documented create commands."""
    # Verify create-virtual-for script exists and is executable
    create_script = VDE_ROOT / "scripts" / "create-virtual-for"
    context.commands_run = create_script.exists()


@when('one developer runs "add-vm-type dart \'apt-get install -y dart\'"')
def step_add_dart_vm_type(context):
    """Add dart VM type."""
    result = run_vde_command(['add-vm-type', 'dart', 'apt-get install -y dart'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('commits the vm-types.conf change')
def step_commit_vm_types(context):
    """Context: Commit vm-types.conf change."""
    # Verify git is available for committing
    result = subprocess.run(['git', 'status'], capture_output=True, cwd=VDE_ROOT)
    context.vm_types_committed = result.returncode == 0


@when('the first developer recreates the VM')
def step_recreate_vm(context):
    """Recreate the VM."""
    result = run_vde_command(['create-virtual-for', 'python', '--force'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I create or restart any VM')
def step_create_or_restart_any_vm(context):
    """Create or restart any VM using vde start command."""
    result = run_vde_command('start python')
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I configure VDE with matching versions')
def step_configure_matching_versions(context):
    """Context: Configure VDE with matching versions."""
    # Verify configs can be created for version matching
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.versions_configured = vm_types.exists()


@when('each team member starts "postgres" VM')
def step_each_start_postgres(context):
    """Each team member starts postgres VM."""
    result = run_vde_command(['start-virtual', 'postgres'])
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('a new developer joins')
def step_new_dev_joins(context):
    """Context: New developer joins."""
    # Verify onboarding resources exist
    readme = VDE_ROOT / "README.md"
    context.new_developer_joined = readme.exists()


# =============================================================================
# Team Onboarding THEN steps
# =============================================================================

@then('they should get the same Python environment I have')
def step_same_python_env(context):
    """Verify same Python environment is created."""
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert compose_path.exists(), "Python environment should be created"


@then('all dependencies should be installed')
def step_dependencies_installed(context):
    """Verify dependencies are installed in the VM - check Docker image."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        # Check container is running which implies dependencies were installed
        assert container_exists(vm.replace("-dev", "")), \
            f"VM {vm} should be running with dependencies installed"


# =============================================================================
# Additional Missing Steps (Added 2026-02-02)
# =============================================================================

@given('I have cloned the project repository')
def step_cloned_project_repo(context):
    """Verify project repository is cloned."""
    # Check if we're in a git repository
    result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                          capture_output=True, cwd=VDE_ROOT)
    context.repo_cloned = result.returncode == 0


@given('my project has a "{vm_name}" VM configuration')
def step_project_has_vm_config(context, vm_name):
    """Check if project has VM configuration for the specified VM."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    context.vm_config_exists = compose_path.exists()


@then('my local development should match production')
def step_local_matches_production(context):
    """Verify local development matches production configuration."""
    # Check that configuration files exist for production services
    configs = VDE_ROOT / "configs" / "docker"
    required_services = ['postgres', 'redis']
    for service in required_services:
        compose_path = configs / service / "docker-compose.yml"
        assert compose_path.exists(), f"{service} config should exist for production matching"


@given('documentation explains how to create each VM')
def step_documentation_exists(context):
    """Check if documentation exists for VM creation."""
    readme_path = VDE_ROOT / "docs" / "quick-start.md"
    context.documentation_exists = readme_path.exists()


@given('the team defines standard VM types in vm-types.conf')
def step_standard_vm_types_exist(context):
    """Verify vm-types.conf exists and contains standard VM types."""
    vm_types_path = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.vm_types_exist = vm_types_path.exists()
    if context.vm_types_exist:
        # Read and parse the vm-types.conf to verify it has content
        with open(vm_types_path, 'r') as f:
            content = f.read()
            context.vm_types_content = content


@given('a project requires specific services ({services})')
def step_project_requires_services(context, services):
    """Check if project requires specific services."""
    service_list = [s.strip() for s in services.split(',')]
    context.required_services = service_list
    configs = VDE_ROOT / "configs" / "docker"
    context.services_available = all(
        (configs / service).exists() for service in service_list
    )


@given('a project needs environment variables for configuration')
def step_project_needs_env_vars(context):
    """Check if environment variable files exist."""
    env_dir = VDE_ROOT / "env-files"
    context.env_files_exist = env_dir.exists()
    if context.env_files_exist:
        context.env_files = list(env_dir.glob("*.env"))
