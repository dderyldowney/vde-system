"""
Step definitions for Team Collaboration and Sharing features.
Focuses on how developers share and sync VDE configurations.
"""

import os
import re
from pathlib import Path
from behave import given, when, then

# Import shared configuration and helpers
from vm_common import (
    VDE_ROOT,
    run_vde_command,
    get_compose_file,
    container_is_running,
    wait_for_container
)

# =============================================================================
# GIVEN steps
# =============================================================================

@given('I am a new developer joining the team')
def step_new_developer_joining(context):
    """Initialize clean context for a new developer."""
    # Ensure VDE_ROOT is set and exists
    assert VDE_ROOT.exists(), f"VDE_ROOT {VDE_ROOT} does not exist"
    
    # Simulate a clean environment by checking if we have the binary
    vde_bin = VDE_ROOT / "bin" / "vde"
    assert vde_bin.exists(), f"VDE binary not found at {vde_bin}"
    
    context.new_developer = True

@given('I have cloned the project repository')
def step_cloned_project_repo(context):
    """Verify project repository directory structure."""
    # Verify core VDE directories that should be in a cloned repo
    expected_dirs = ["bin", "configs", "lib", "templates", "data"]
    for d in expected_dirs:
        dir_path = VDE_ROOT / d
        assert dir_path.is_dir(), f"Required directory {d} missing from cloned repository"
    
    # Verify we are in a git repo (optional but good for 'cloned' context)
    git_dir = VDE_ROOT / ".git"
    assert git_dir.exists(), "Project does not appear to be a git repository"

@given('my project has a "{vm_name}" VM configuration')
def step_project_has_vm_config(context, vm_name):
    """Verify VM configuration exists for the given name."""
    # Check both new (category-specific) and old (flat) paths
    category_map = {"python": "languages", "postgres": "services", "go": "languages"}
    category = category_map.get(vm_name, "languages")
    
    config_path = VDE_ROOT / "configs" / "docker" / category / vm_name
    if not config_path.exists():
        # Fallback to legacy flat structure
        config_path = VDE_ROOT / "configs" / "docker" / vm_name
        
    assert config_path.exists(), f"VM configuration for '{vm_name}' not found at {config_path}"
    context.target_vm = vm_name

@given('the team uses PostgreSQL for development')
def step_team_uses_postgres(context):
    """Verify configs/docker/services/postgres exists."""
    step_project_has_vm_config(context, "postgres")

@given('the team defines standard VM types in vm-types.conf')
def step_team_defines_standard_vms(context):
    """Verify 'data/vm-types.conf' existence and content."""
    vm_types_conf = VDE_ROOT / "data" / "vm-types.conf"
    assert vm_types_conf.exists(), f"Standard VM types file {vm_types_conf} missing"
    
    # Verify it has some content
    content = vm_types_conf.read_text()
    assert len(content.strip()) > 0, "vm-types.conf is empty"
    assert "python" in content, "Standard VM type 'python' not found in vm-types.conf"

# =============================================================================
# WHEN steps
# =============================================================================

@when('a new developer follows the setup instructions')
def step_developer_follows_setup(context):
    """Run 'vde init' and 'vde create python'."""
    # 1. Run vde init
    result_init = run_vde_command("init", context=context)
    assert result_init.returncode == 0, f"vde init failed: {result_init.stderr}"
    
    # 2. Run vde create python (standard onboarding example)
    result_create = run_vde_command("create python", context=context)
    assert result_create.returncode == 0, f"vde create python failed: {result_create.stderr}"

@when('each team member starts "{vm_name}" VM')
def step_team_member_starts_vm(context, vm_name):
    """Run 'vde start <vm_name>'."""
    result = run_vde_command(f"start {vm_name}", context=context)
    assert result.returncode == 0, f"vde start {vm_name} failed: {result.stderr}"
    
    # Wait for container to be ready
    container_name = f"vde-{vm_name}"
    ready = wait_for_container(container_name, timeout=60)
    assert ready, f"Container {container_name} failed to become ready after start"

@when('a teammate clones the repository')
def step_teammate_clones_repo(context):
    """Simulate teammate cloning (we use the current VDE_ROOT as the shared state)."""
    # Verify we can run VDE commands - this simulates the environment being ready after clone
    result = run_vde_command("info", context=context)
    assert result.returncode == 0, "VDE commands not working after 'clone'"

# @when('they run "vde create {vm_name}"')
# def step_teammate_runs_create(context, vm_name):
#     """Duplicate of documented_workflow_steps.py."""
#     result = run_vde_command(f"create {vm_name}", context=context)
#     assert result.returncode == 0, f"vde create {vm_name} failed: {result.stderr}"

# =============================================================================
# THEN steps
# =============================================================================

# @then('VDE should detect my operating system')
# def step_vde_detects_os(context):
#     """Duplicate of documented_workflow_steps.py."""
#     result = run_vde_command("info", context=context)
#     assert result.returncode == 0, f"vde info failed: {result.stderr}"
#     
#     output = result.stdout.lower()
#     # Check for OS-related keywords
#     os_keywords = ["os:", "operating system", "darwin", "linux", "kernel"]
#     found = any(k in output for k in os_keywords)
#     assert found, f"Operating system info not detected in 'vde info' output:\n{result.stdout}"

@then('they should get the same Python environment I have')
def step_same_python_environment(context):
    """Compare 'vde exec python python --version' output."""
    # Ensure VM is started
    if not container_is_running("vde-python"):
        run_vde_command("start python", context=context)
        wait_for_container("vde-python", timeout=60)
    
    # Check python version
    result = run_vde_command("exec python python --version", context=context)
    assert result.returncode == 0, f"Failed to check python version: {result.stderr}"
    
    # We expect Python 3.x
    version_out = (result.stdout + result.stderr).strip()
    assert "Python 3." in version_out, f"Unexpected Python version environment: {version_out}"

# @then('each developer gets their own isolated PostgreSQL instance')
def step_isolated_postgres_instance(context):
    """Verify VDE_ROOT pathing in docker-compose.yml ensures isolation."""
    compose_file = get_compose_file("postgres")
    assert compose_file.exists(), f"Postgres compose file missing: {compose_file}"
    
    content = compose_file.read_text()
    
    # 1. Isolation via container name
    assert "container_name: vde-postgres" in content, "Missing standard container name for isolation"
    
    # 2. Isolation via local data volumes (relative to VDE_ROOT)
    # Looking for something like ./data/postgres:/var/lib/postgresql/data
    assert "data/postgres" in content, "Postgres data should be mapped to local VDE 'data/postgres' for isolation"
    
    # 3. Network isolation
    assert "networks:" in content and "vde-net" in content, "Postgres should be on isolated vde-net"

# @then('anyone can create the VM using the standard name')
def step_anyone_can_create_standard_vm(context):
    """Run 'vde create python' and assert success."""
    # Clean up first to ensure a fresh creation
    run_vde_command("remove python", context=context)
    
    result = run_vde_command("create python", context=context)
    assert result.returncode == 0, f"Failed to create VM using standard name 'python': {result.stderr}"
    
    # Verify the result of creation
    compose_file = get_compose_file("python")
    assert compose_file.exists(), f"Creation failed: {compose_file} not found"

# @then('my SSH keys should be automatically configured')
def step_ssh_keys_automatically_configured(context):
    """Verify ~/.ssh/vde/ config and keys exist."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    assert ssh_dir.is_dir(), f"SSH directory {ssh_dir} was not created"
    assert (ssh_dir / "id_ed25519").exists(), "VDE private key missing"
    assert (ssh_dir / "config").exists(), "VDE SSH config missing"

# @then('I should see available VMs with "vde list"')
def step_see_available_vms(context):
    """Run vde list and check for VMs."""
    result = run_vde_command("list", context=context)
    assert result.returncode == 0, f"vde list failed: {result.stderr}"
    assert "python" in result.stdout.lower(), "Standard VM 'python' should be listed"

# @then('all dependencies should be installed')
def step_all_dependencies_installed(context):
    """Verify dependencies (like pip packages) are present in the environment."""
    # For python, check if pip works
    result = run_vde_command("exec python pip --version", context=context)
    assert result.returncode == 0, f"Dependencies verification failed: {result.stderr}"

@then('data persists in each developer\'s local data/postgres/')
def step_data_persists_locally(context):
    """Verify local data directory exists."""
    data_dir = VDE_ROOT / "data" / "postgres"
    assert data_dir.is_dir(), f"Local data directory {data_dir} missing"

# @then('everyone gets consistent configurations')
def step_consistent_configurations(context):
    """Verify that creation results in standard structure."""
    step_anyone_can_create_standard_vm(context)
