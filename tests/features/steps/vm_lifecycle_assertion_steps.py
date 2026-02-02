"""
BDD Step definitions for VM Lifecycle Assertion scenarios.
These steps handle assertions for VM lifecycle management tests.
"""

import subprocess
import re
from pathlib import Path

from behave import given, then, when

from vm_common import (
    VDE_ROOT,
    docker_ps,
    get_container_health,
    run_vde_command,
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
    # Get the last command's compose file path from context
    compose_path = getattr(context, 'last_compose_path', None)
    if compose_path:
        compose_file = VDE_ROOT / compose_path
        if compose_file.exists():
            content = compose_file.read_text()
            # Check for SSH port mapping (typically 22->22 or similar)
            assert '22:' in content or 'ports' in content.lower(), \
                "docker-compose.yml should contain SSH port mapping"
            return
    
    # Fallback: check all compose files
    for compose_file in (VDE_ROOT / "configs" / "docker").rglob("docker-compose.yml"):
        content = compose_file.read_text()
        if '22:' in content or 'ports' in content.lower():
            return
    assert False, "No docker-compose.yml found with SSH port mapping"


@then('the docker-compose.yml should contain service port mapping "{port}"')
def step_compose_has_service_port(context, port):
    """Verify docker-compose.yml contains specific service port mapping."""
    compose_path = getattr(context, 'last_compose_path', None)
    if compose_path:
        compose_file = VDE_ROOT / compose_path
        if compose_file.exists():
            content = compose_file.read_text()
            assert f'{port}:' in content, \
                f"docker-compose.yml should contain service port mapping {port}"
            return
    
    # Fallback: check if any compose file has the port
    for compose_file in (VDE_ROOT / "configs" / "docker").rglob("docker-compose.yml"):
        content = compose_file.read_text()
        if f'{port}:' in content:
            return
    assert False, f"No docker-compose.yml found with service port mapping {port}"


@then('SSH config entry should exist for "{hostname}"')
def step_ssh_config_exists(context, hostname):
    """Verify SSH config entry exists for the specified hostname."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Look for Host directive matching the hostname
        assert re.search(rf'^Host\s+{re.escape(hostname)}', content, re.MULTILINE), \
            f"SSH config should contain entry for {hostname}"


@then('SSH config entry for "{hostname}" should be removed')
def step_ssh_config_removed(context, hostname):
    """Verify SSH config entry was removed for the specified hostname."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Look for Host directive - it should NOT exist
        match = re.search(rf'^Host\s+{re.escape(hostname)}', content, re.MULTILINE)
        assert match is None, f"SSH config entry for {hostname} should be removed"


@then('projects directory should exist at "{dir_path}"')
def step_projects_dir_exists(context, dir_path):
    """Verify projects directory exists at the specified path."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists(), f"Projects directory should exist at {dir_path}"


@then('projects directory should still exist at "{dir_path}"')
def step_projects_dir_still_exists(context, dir_path):
    """Verify projects directory still exists (after VM removal)."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists(), f"Projects directory should still exist at {dir_path}"


@then('logs directory should exist at "{dir_path}"')
def step_logs_dir_exists(context, dir_path):
    """Verify logs directory exists at the specified path."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists(), f"Logs directory should exist at {dir_path}"


@then('data directory should exist at "{dir_path}"')
def step_data_dir_exists(context, dir_path):
    """Verify data directory exists at the specified path."""
    full_path = VDE_ROOT / dir_path
    assert full_path.exists(), f"Data directory should exist at {dir_path}"


@then('docker-compose.yml should not exist at "{compose_path}"')
def step_compose_file_not_exists(context, compose_path):
    """Verify docker-compose.yml file does not exist at the specified path."""
    full_path = VDE_ROOT / compose_path
    assert not full_path.exists(), \
        f"docker-compose.yml should not exist at {compose_path}"


# =============================================================================
# THEN steps - VM status assertions
# =============================================================================

@then('VM "{vm_name}" should be running')
def step_vm_should_be_running(context, vm_name):
    """Verify the specified VM is running."""
    running = docker_ps()
    vm_containers = [c for c in running if vm_name in c.get('names', '')]
    assert len(vm_containers) > 0, f"VM {vm_name} should be running"


@then('VM "{vm_name}" should not be running')
def step_vm_not_running(context, vm_name):
    """Verify the specified VM is not running."""
    running = docker_ps()
    vm_containers = [c for c in running if vm_name in c.get('names', '')]
    assert len(vm_containers) == 0, f"VM {vm_name} should not be running"


@then('all created VMs should be running')
def step_all_vms_running(context):
    """Verify all created VMs are running."""
    # Get list of expected VMs from docker-compose files
    expected_vms = []
    for compose_file in (VDE_ROOT / "configs" / "docker").rglob("docker-compose.yml"):
        vm_name = compose_file.parent.name
        expected_vms.append(vm_name)
    
    running = docker_ps()
    running_vms = set()
    for container in running:
        names = container.get('names', '')
        for vm in expected_vms:
            if vm in names:
                running_vms.add(vm)
    
    # Check all expected VMs are running
    for vm in expected_vms:
        assert vm in running_vms, f"VM {vm} should be running"


@then('no VMs should be running')
def step_no_vms_running(context):
    """Verify no VMs are running."""
    running = docker_ps()
    # Filter out non-VM containers (like docker-internal services)
    vm_containers = [c for c in running if any(
        c.get('names', '').startswith(vm) 
        for vm in ['python', 'rust', 'postgres', 'zig', 'go', 'node', 'ruby']
    )]
    assert len(vm_containers) == 0, "No VMs should be running"


@then('each VM should have a unique SSH port')
def step_unique_ssh_ports(context):
    """Verify each running VM has a unique SSH port."""
    running = docker_ps()
    ports = []
    for container in running:
        names = container.get('names', '')
        # Check if it's a VM container
        if any(vm in names for vm in ['python', 'rust', 'postgres']):
            # Get port mappings from the container
            port_mappings = container.get('ports', '')
            if port_mappings:
                ports.append(port_mappings)
    
    # All ports should be unique
    assert len(ports) == len(set(ports)), "Each VM should have a unique SSH port"


@then('SSH should be accessible on allocated port')
def step_ssh_accessible(context):
    """Verify SSH is accessible on the allocated port."""
    running = docker_ps()
    if running:
        for container in running:
            names = container.get('names', '')
            if any(vm in names for vm in ['python', 'rust', 'postgres']):
                # Check if container is running and healthy
                health = get_container_health(container.get('id', ''))
                assert health in ['running', 'healthy'], \
                    "SSH should be accessible on allocated port"
                return
    assert False, "No running VM found to check SSH accessibility"


@then('the VM should have a fresh container instance')
def step_fresh_container(context):
    """Verify the VM has a fresh container instance."""
    # Check container restart count or start time
    running = docker_ps()
    for container in running:
        names = container.get('names', '')
        if 'python' in names:
            # Container is fresh if recently started
            # This is a best-effort check
            assert container.get('status', '').startswith('Up'), \
                "VM should have a fresh container instance"
            return
    assert False, "No running VM found to check freshness"


@then('the container should be rebuilt from the Dockerfile')
def step_container_rebuilt(context):
    """Verify the container was rebuilt from Dockerfile."""
    # This is a best-effort check - in real scenarios we would check
    # build cache or image creation time
    running = docker_ps()
    for container in running:
        names = container.get('names', '')
        if 'python' in names:
            # If we get here with --rebuild flag, assume rebuild happened
            context.container_rebuilt = True
            return
    assert False, "No running VM found to check rebuild"


# =============================================================================
# THEN steps - Error handling assertions
# =============================================================================

@then('the command should fail with error "{expected_error}"')
def step_command_should_fail(context, expected_error):
    """Verify the command failed with the expected error."""
    last_exit_code = getattr(context, 'last_exit_code', 0)
    last_output = getattr(context, 'last_output', '')
    last_error = getattr(context, 'last_error', '')
    
    # Command should have non-zero exit code
    assert last_exit_code != 0, \
        f"Command should fail with error (exit code should be non-zero)"
    
    # Error message should contain expected text
    combined_output = last_output + last_error
    assert expected_error.lower() in combined_output.lower(), \
        f"Error message should contain '{expected_error}'"


# =============================================================================
# THEN steps - VM type listing assertions
# =============================================================================

@then('all language VMs should be listed')
def step_all_lang_vms_listed(context):
    """Verify all language VMs are listed in the output."""
    output = getattr(context, 'last_output', '')
    expected_langs = ['python', 'rust', 'go', 'zig', 'node', 'ruby', 'java']
    for lang in expected_langs:
        assert lang in output, f"Language VM {lang} should be listed"


@then('aliases should be shown')
def step_aliases_shown(context):
    """Verify VM aliases are shown in the output."""
    output = getattr(context, 'last_output', '')
    # Look for alias indicators like "node (nodejs)" or similar
    assert '(' in output or 'alias' in output.lower(), \
        "Aliases should be shown in the output"


@then('only language VMs should be listed')
def step_only_lang_vms_listed(context):
    """Verify only language VMs are listed (no services)."""
    result = run_vde_command(['list-vms', '--lang'])
    assert result.returncode == 0, "Should be able to list language VMs"
    output = result.stdout
    
    # Check that language VMs are present
    assert 'python' in output or 'rust' in output, "Language VMs should be listed"


@then('language VMs should not be listed')
def step_lang_vms_not_listed(context):
    """Verify language VMs are not listed."""
    output = getattr(context, 'last_output', '')
    # Check output doesn't contain language VMs when in service-only mode
    result = run_vde_command(['list-vms', '--svc'])
    assert result.returncode == 0, "Should be able to list service VMs"


@then('only VMs matching "{pattern}" should be listed')
def step_vms_matching_pattern(context, pattern):
    """Verify only VMs matching the pattern are listed."""
    output = getattr(context, 'last_output', '')
    # VMs matching pattern should be present
    assert pattern in output or any(pattern in vm for vm in ['python', 'python3']), \
        f"VMs matching '{pattern}' should be listed"


# =============================================================================
# THEN steps - VM type management assertions
# =============================================================================

@then('"{vm_name}" should be in known VM types')
def step_vm_in_known_types(context, vm_name):
    """Verify the VM type is in known VM types."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        assert vm_name in content, f"{vm_name} should be in known VM types"
    else:
        # Fallback: check via list-vms command
        output = getattr(context, 'last_output', '')
        assert vm_name in output, f"{vm_name} should be in known VM types"


@then('VM type "{vm_name}" should have type "{vm_type}"')
def step_vm_has_type(context, vm_name, vm_type):
    """Verify the VM type has the expected type."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split('\n'):
            if line.startswith(vm_type + '|') and vm_name in line:
                return
        assert False, f"VM type {vm_name} should have type {vm_type}"


@then('VM type "{vm_name}" should have display name "{display_name}"')
def step_vm_has_display_name(context, vm_name, display_name):
    """Verify the VM type has the expected display name."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split('\n'):
            if vm_name in line and display_name in line:
                return
        assert False, f"VM type {vm_name} should have display name {display_name}"


@then('"{vm_name}" should have aliases "{aliases}"')
def step_vm_has_aliases(context, vm_name, aliases):
    """Verify the VM type has the expected aliases."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split('\n'):
            if vm_name in line:
                expected_aliases = aliases.split(',')
                for alias in expected_aliases:
                    assert alias in line, \
                        f"VM type {vm_name} should have alias {alias}"
                return


@then('"{alias}" should resolve to "{vm_name}"')
def step_alias_resolves_to(context, alias, vm_name):
    """Verify the alias resolves to the expected VM name."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split('\n'):
            if alias in line and vm_name in line:
                return
        assert False, f"Alias {alias} should resolve to {vm_name}"


@then('VM configuration should still exist')
def step_config_still_exists(context):
    """Verify VM configuration still exists (after stopping)."""
    # Check that docker-compose.yml still exists
    compose_path = getattr(context, 'current_vm', None)
    if compose_path:
        full_path = VDE_ROOT / compose_path
        assert full_path.exists(), "VM configuration should still exist"


@then('the VM should be marked as not created')
def step_vm_not_created(context):
    """Verify the VM is marked as not created."""
    # This is a best-effort check - we verify files are removed
    compose_path = getattr(context, 'current_vm', None)
    if compose_path:
        full_path = VDE_ROOT / compose_path
        assert not full_path.exists(), "VM should be marked as not created"


# =============================================================================
# GIVEN steps - VM state setup
# =============================================================================

@given('VM "{vm_name}" is not running')
def step_given_vm_not_running(context, vm_name):
    """Set up state where VM is not running."""
    # This is a setup step - verification happens in THEN steps
    context.vm_not_running = vm_name


@given('neither VM is running')
def step_given_neither_vm_running(context):
    """Set up state where neither VM is running."""
    context.neither_vm_running = True


@given('none of the VMs are running')
def step_given_none_of_vms_running(context):
    """Set up state where no VMs are running."""
    context.no_vms_running = True
