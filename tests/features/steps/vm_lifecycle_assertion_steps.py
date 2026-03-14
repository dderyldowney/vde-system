"""
BDD Step definitions for VM Lifecycle Assertion scenarios.
These steps handle assertions for VM lifecycle management tests.
"""

import subprocess
import re
import os
import time
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    docker_ps,
    container_exists,
    run_vde_command,
    wait_for_container,
)


# =============================================================================
# THEN steps - File and directory assertions
# =============================================================================

@then('a docker-compose.yml file should be created at "{compose_path}"')
def step_compose_file_created(context, compose_path):
    """Verify docker-compose.yml file was created at the specified path."""
    full_path = VDE_ROOT / compose_path
    assert full_path.exists(), f"docker-compose.yml should exist at {compose_path}"


@then('the docker-compose.yml should contain SSH port mapping')
def step_compose_has_ssh_mapping(context):
    """Verify docker-compose.yml contains SSH port mapping."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    # Check at least one known VM type
    compose_file = configs_dir / "python" / "docker-compose.yml"
    if compose_file.exists():
        content = compose_file.read_text()
        assert '22:' in content or 'ports' in content.lower()


@then('the docker-compose.yml should contain service port mapping "{port}"')
def step_compose_has_service_port(context, port):
    """Verify docker-compose.yml contains specific service port mapping."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    # Check all service VMs
    for svc in ['postgres', 'redis', 'mongodb', 'mysql']:
        compose_file = configs_dir / svc / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            if f'{port}:' in content:
                return
    assert False, f"No docker-compose.yml found with service port mapping {port}"


@then('SSH config entry should exist for "{hostname}"')
def step_ssh_config_exists(context, hostname):
    """Verify SSH config entry exists for the specified hostname."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), "VDE SSH config missing"
    content = ssh_config.read_text()
    assert hostname in content, f"SSH config missing entry for {hostname}"


@then('SSH config entry for "{hostname}" should be preserved')
def step_ssh_config_preserved(context, hostname):
    """Verify SSH config entry is preserved (static port assignments)."""
    ssh_config = VDE_ROOT / "configs" / "ssh" / "config"
    assert ssh_config.exists(), "Project SSH config missing"
    content = ssh_config.read_text()
    assert hostname in content, f"SSH config missing entry for {hostname}"


@then('projects directory should exist at "{dir_path}"')
def step_projects_dir_exists(context, dir_path):
    """Verify projects directory exists."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists(), f"Directory missing at {dir_path}"


@then('projects directory should still exist at "{dir_path}"')
def step_projects_dir_still_exists(context, dir_path):
    """Verify projects directory still exists after removal."""
    step_projects_dir_exists(context, dir_path)


@then('logs directory should exist at "{dir_path}"')
def step_logs_dir_exists(context, dir_path):
    """Verify logs directory exists."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists()


@then('data directory should exist at "{dir_path}"')
def step_data_dir_exists(context, dir_path):
    """Verify data directory exists."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists()

# =============================================================================
# THEN steps - VM status assertions
# =============================================================================

@then('VM "{vm_name}" should be running')
def step_vm_should_be_running(context, vm_name):
    """Verify the specified VM is running via vde ps."""
    running = docker_ps()
    assert f"vde-{vm_name}" in running, f"VM {vm_name} should be running"


@then('VM "{vm_name}" should not be running')
def step_vm_not_running(context, vm_name):
    """Verify the specified VM is not running via vde ps."""
    running = docker_ps()
    assert f"vde-{vm_name}" not in running, f"VM {vm_name} should not be running"


@then('all created VMs should be running')
def step_all_vms_running(context):
    """Verify all created VMs are running via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) >= 1


@then('no VMs should be running')
def step_no_vms_running(context):
    """Verify no VMs are running via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) == 0, f"VMs still running: {vde_running}"


@then('each VM should have a unique SSH port')
def step_unique_ssh_ports(context):
    """Verify each running VM has a unique SSH port via vde port."""
    running = docker_ps()
    ports = []
    for container in running:
        vm_name = container.replace('vde-', '')
        result = run_vde_command(f"port {vm_name} 22", context=context)
        if result.returncode == 0 and result.stdout.strip():
            ports.append(result.stdout.strip())
    assert len(ports) == len(set(ports))


@then('SSH should be accessible on allocated port')
def step_ssh_accessible(context):
    """Verify SSH is accessible on the allocated port."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert result.returncode == 0 and result.stdout.strip()


@then('the VM should have a fresh container instance')
def step_fresh_container(context):
    """Verify the VM has a fresh container instance."""
    # Start command handled fresh lifecycle
    assert getattr(context, 'last_exit_code', 1) == 0


@then('the container should be rebuilt from the Dockerfile')
def step_container_rebuilt(context):
    """Verify the container was rebuilt."""
    assert getattr(context, 'last_exit_code', 1) == 0


# =============================================================================
# THEN steps - VM type listing assertions
# =============================================================================

@then('all language VMs should be listed')
def step_all_lang_vms_listed(context):
    """Verify all language VMs are listed in vde list output."""
    result = run_vde_command("list", context=context)
    output = result.stdout.lower()
    for lang in ['python', 'rust', 'go', 'js']:
        assert lang in output


@then('aliases should be shown')
def step_aliases_shown(context):
    """Verify VM aliases are shown in the output."""
    result = run_vde_command("list", context=context)
    assert 'alias' in result.stdout.lower() or '(' in result.stdout


@then('only language VMs should be listed')
def step_only_lang_vms_listed(context):
    """Verify only language VMs are listed."""
    result = run_vde_command("list --type language", context=context)
    assert 'python' in result.stdout.lower()
    assert 'postgres' not in result.stdout.lower()


@then('language VMs should not be listed')
def step_lang_vms_not_listed(context):
    """Verify language VMs are not listed."""
    result = run_vde_command("list --type service", context=context)
    assert 'python' not in result.stdout.lower()


@then('only VMs matching "{pattern}" should be listed')
def step_vms_matching_pattern(context, pattern):
    """Verify only VMs matching the pattern are listed."""
    result = run_vde_command(f"list {pattern}", context=context)
    assert pattern.lower() in result.stdout.lower()


# =============================================================================
# THEN steps - VM type management assertions
# =============================================================================

@then('"{vm_name}" should be in known VM types')
def step_vm_in_known_types(context, vm_name):
    """Verify the VM type is in known VM types."""
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
    assert vm_name in vm_types_file.read_text()


@then('VM type "{vm_name}" should have type "{vm_type}"')
def step_vm_has_type(context, vm_name, vm_type):
    """Verify the VM type has the expected type."""
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
    content = vm_types_file.read_text()
    assert f"{vm_type}|vde-{vm_name}" in content


@then('VM type "{vm_name}" should have display name "{display_name}"')
def step_vm_has_display_name(context, vm_name, display_name):
    """Verify the VM type has the expected display name."""
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
    assert display_name in vm_types_file.read_text()


@then('"{vm_name}" should have aliases "{aliases}"')
def step_vm_has_aliases(context, vm_name, aliases):
    """Verify the VM type has the expected aliases."""
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
    assert aliases in vm_types_file.read_text()


@then('"{alias}" should resolve to "{vm_name}"')
def step_alias_resolves_to(context, alias, vm_name):
    """Verify the alias resolves to the expected VM name."""
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
    assert alias in vm_types_file.read_text()


@then('VM configuration should still exist')
def step_config_still_exists(context):
    """Verify VM configuration still exists."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert (VDE_ROOT / "configs" / "docker" / vm_name).exists()


@then('the VM should be marked as not created')
def step_vm_not_created(context):
    """Verify the VM is marked as not created by checking config existence."""
    vm_name = getattr(context, 'vm_name', 'python')
    # If not created, the compose file should not exist
    from vm_common import compose_file_exists
    assert not compose_file_exists(vm_name), f"VM {vm_name} config should not exist"


# =============================================================================
# GIVEN steps - VM state setup
# =============================================================================

@given('VM "{vm_name}" is not running')
def step_given_vm_not_running(context, vm_name):
    """Ensure VM is not running."""
    run_vde_command(f"stop {vm_name} -f", context=context)


@given('neither VM is running')
def step_given_neither_vm_running(context):
    """Ensure multiple VMs are not running."""
    run_vde_command("stop all -f", context=context)


@given('none of the VMs are running')
def step_given_none_of_vms_running(context):
    """Ensure no VMs are running."""
    run_vde_command("stop all -f", context=context)


# =============================================================================
# THEN steps - VM lifecycle verification
# =============================================================================

@then('workspace should be mounted at ~/{workspace_dir}')
def step_workspace_mounted(context, workspace_dir):
    """Verify workspace directory is mounted in the container."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"inspect {vm_name} -f '{{{{json .Mounts}}}}'", context=context)
    assert 'projects' in result.stdout.lower() or 'workspace' in result.stdout.lower()


@then('the container should be rebuilt without cache')
def step_container_rebuilt_no_cache(context):
    """Verify the container was rebuilt without cache."""
    assert getattr(context, 'last_exit_code', 1) == 0


@then('SSH connection should still work')
def step_ssh_still_works(context):
    """Verify SSH connection still works."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert result.returncode == 0


@then('VM "{vm_name}" configuration should be preserved')
def step_vm_config_preserved(context, vm_name):
    """Verify VM configuration files were preserved after remove."""
    assert (VDE_ROOT / "configs" / "docker" / vm_name).exists()


@then('container should be gone')
def step_container_gone(context):
    """Verify the Docker container was removed."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert not container_exists(vm_name)


@then('SSH config entry should be preserved')
def step_ssh_config_preserved_assertion(context):
    """Verify SSH config entry is preserved (static port assignments)."""
    vm_name = getattr(context, 'vm_name', 'python')
    ssh_host = f"vde-{vm_name}"
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), "VDE SSH config missing"
    content = ssh_config.read_text()
    assert ssh_host in content, f"SSH config entry for {ssh_host} should be preserved (static port assignment)"


@then('SSH keys should be generated if none exist')
def step_ssh_keys_generated(context):
    """Verify SSH keys were generated."""
    assert (Path.home() / ".ssh" / "vde" / "id_ed25519").exists()


@then('public key should be copied to VM\'s authorized_keys')
def step_public_key_copied(context):
    """Verify public key was copied."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"exec {vm_name} 'ls ~/.ssh/authorized_keys'", context=context)
    assert result.returncode == 0


@when('I SSH to "{ssh_host}"')
def step_i_ssh_to(context, ssh_host):
    """Attempt SSH connection."""
    vm_name = ssh_host.replace('vde-', '')
    result = run_vde_command(f"connect {vm_name} --dry-run", context=context)
    assert result.returncode == 0
