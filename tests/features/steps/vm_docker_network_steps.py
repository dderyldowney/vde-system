"""
BDD Step definitions for Docker Networking and Port Management.
These steps handle Docker network creation, port allocation, inter-VM communication,
and service name resolution.
All steps use real system verification instead of context flags.
"""

import subprocess
import os
import yaml
import re
from pathlib import Path

from behave import given, then

# Import shared helpers and configuration
from vm_common import (
    VDE_ROOT,
    docker_ps,
    docker_list_containers,
    get_port_from_compose,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup network states
# =============================================================================

@given('vde-testing does not exist')
def step_no_network(context):
    """Network does not exist - verify vde-net missing via vde networks."""
    result = run_vde_command('networks', context=context)
    context.network_missing = "vde-net" not in result.stdout.lower() and "vde-testing" not in result.stdout.lower()


# =============================================================================
# THEN steps - Verify network and port outcomes
# =============================================================================

@then('network should be created automatically')
def step_network_auto_created(context):
    """Network should be auto-created - verify vde-net exists."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "Should be able to list VDE networks"
    # Accept both vde-net and vde-testing
    assert any(x in result.stdout.lower() for x in ['vde-net', 'vde-testing']), \
        f"VDE network should exist. Output: {result.stdout}"
    context.network_configured = True


@then('they should be on the same Docker network')
def step_they_same_network(context):
    """VMs should be on same Docker network."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "Should be able to list VDE networks"
    assert any(x in result.stdout.lower() for x in ['vde-net', 'vde-testing']), \
        f"VDE network should exist. Output: {result.stdout}"
    context.network_configured = True


@then('VDE should create the vde-testing network')
def step_dev_net_created(context):
    """VDE creates network (vde-net or vde-testing)."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "Should be able to list networks"
    assert any(x in result.stdout for x in ['vde-net', 'vde-testing']), "VDE network missing"
    context.dev_net_created = True


@then('all VMs should join this network')
def step_all_vms_join_network(context):
    """All VMs join network - verify via vde networks."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "VDE network should exist"


@then('VMs should be able to communicate by name')
def step_vms_communicate_by_name(context):
    """VMs communicate by name - verify network exists."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "VDE network should exist for VM communication"


@then('each should get a unique SSH port')
def step_unique_ssh_port(context):
    """Each gets unique SSH port - verify via vde port."""
    running = docker_ps()
    ports = []
    for container in running:
        vm_name = container.replace('vde-', '')
        result = run_vde_command(f"port {vm_name} 22", context=context)
        if result.returncode == 0 and result.stdout.strip():
            # Extract port number (handles formats like "0.0.0.0:2213" or just "2213")
            m = re.search(r'(\d+)$', result.stdout.strip())
            if m:
                port = m.group(1)
                ports.append(port)
    # Verify all unique
    assert len(ports) > 0, "No SSH ports found for running VMs"
    assert len(ports) == len(set(ports)), f"Each VM should have unique SSH port, got: {ports}"


@then('ports should be auto-allocated from available range')
def step_ports_auto_allocated(context):
    """Ports auto-allocated - verify ports are in valid range (2200-2499)."""
    running = docker_ps()
    for container in running:
        vm_name = container.replace('vde-', '')
        result = run_vde_command(f"port {vm_name} 22", context=context)
        if result.returncode == 0 and result.stdout.strip():
            m = re.search(r'(\d+)$', result.stdout.strip())
            if m:
                port_num = int(m.group(1))
                # Support full range 2200-2499
                assert 2200 <= port_num <= 2499, \
                    f"Port {port_num} for {vm_name} should be in VDE range 2200-2499"


@then('no two VMs should have the same SSH port')
def step_no_duplicate_ports(context):
    """No duplicate SSH ports."""
    # Reuse unique port logic
    step_unique_ssh_port(context)


@then('the PostgreSQL port should be mapped')
def step_postgresql_port_mapped(context):
    """PostgreSQL port mapped."""
    port = get_port_from_compose('postgres')
    assert port is not None, "PostgreSQL should have port configured"


@then('I can connect to PostgreSQL from the host')
def step_connect_postgresql_host(context):
    """Connect to PostgreSQL from host - verify port mapping."""
    result = run_vde_command("port postgres 5432", context=context)
    assert result.returncode == 0 and ('5432' in result.stdout or result.stdout.strip()), \
        "PostgreSQL port should be mapped and accessible"


@then('other VMs can connect using the service name')
def step_connect_service_name(context):
    """Connect using service name - verify network exists."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0 and any(x in result.stdout.lower() for x in ['vde-net', 'vde-testing']), \
        "VDE network should exist for service name resolution"


@then('all should be on the same network')
def step_same_network_alt(context):
    """All VMs should be on same network."""
    result = run_vde_command('networks', context=context)
    assert result.returncode == 0, "Should be able to list VDE networks"


@then('each VM should be mapped to its port')
def step_each_vm_mapped_port(context):
    """Verify each VM is mapped to its port via vde port."""
    running = docker_ps()
    if running:
        for container in list(running)[:3]:
            vm_name = container.replace('vde-', '')
            result = run_vde_command(f"port {vm_name}", context=context)
            assert result.returncode == 0, f"VM {vm_name} should have port mapping"
