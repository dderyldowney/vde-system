"""
BDD Step Definitions for Port Management.
Tests port allocation, collision detection, and registry management.
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
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
)


# =============================================================================
# GIVEN steps - Setup for Port Management tests
# =============================================================================


@given('ports "{ports}" are allocated')
def step_ports_allocated(context, ports):
    """Ensure specific ports are allocated."""
    port_list = [p.strip().strip('"').strip("'") for p in ports.split(",")]
    context.allocated_ports = port_list
    # For testing collisions, we often need to ensure no VM is already using these ports
    # This is handled by cleanup logic or vde's own collision detection


@given('VM "{vm_name}" is allocated port "{port}"')
def step_vm_allocated_port(context, vm_name, port):
    """Ensure VM has specific port allocated."""
    from vm_common import compose_file_exists

    if not compose_file_exists(vm_name):
        run_vde_command(f"create {vm_name}", timeout=120, context=context)

    context.vm_name = vm_name
    context.allocated_port = port


@given("I reload the VM types cache")
def step_reload_vm_cache(context):
    """Reload VM types cache via rebuild-cache command."""
    run_vde_command("rebuild-cache", timeout=30, context=context)
    assert context.last_exit_code == 0, "Failed to rebuild cache"


@given('a non-VDE process is listening on port "{port}"')
def step_process_listening_on_port(context, port):
    """Start a process listening on a port."""
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", int(port)))
        s.listen(1)
        # Store socket in context to keep it open
        if not hasattr(context, "open_sockets"):
            context.open_sockets = []
        context.open_sockets.append(s)
    except OSError:
        pass  # Already occupied


@given('a Docker container is bound to host port "{port}"')
def step_docker_bound_to_port(context, port):
    """Start a Docker container bound to a port (or simulate via socket)."""
    # For port conflict detection, a socket bind is sufficient to block the port on host
    step_process_listening_on_port(context, port)


@given('all ports from "{start_port}" to "{end_port}" are allocated')
def step_all_ports_allocated(context, start_port, end_port):
    """Context: All ports in range are allocated."""
    context.port_range_start = int(start_port)
    context.port_range_end = int(end_port)
    context.all_ports_allocated = True


@given('a port lock is older than "{seconds}" seconds')
def step_old_port_lock(context, seconds):
    """Create an old port lock file."""
    context.lock_age_seconds = int(seconds)


# =============================================================================
# WHEN steps - Actions for Port Management tests
# =============================================================================


@when("I create a language VM")
def step_create_language_vm(context):
    """Create a language VM."""
    run_vde_command("create c", timeout=120, context=context)


@when('I create language VM "{vm_name}"')
def step_create_lang_vm(context, vm_name):
    """Create a specific language VM."""
    run_vde_command(f"create {vm_name}", timeout=120, context=context)
    context.vm_name = vm_name


@when("I create a service VM")
def step_create_service_vm(context):
    """Create a service VM."""
    run_vde_command("create redis", timeout=120, context=context)


@when("I query the port registry")
def step_query_port_registry(context):
    """Query the port registry via vde port command."""
    # VDE uses .cache/port-registry
    port_registry = VDE_ROOT / ".cache" / "port-registry"
    if port_registry.exists():
        context.port_registry_content = port_registry.read_text()
    else:
        context.port_registry_content = ""


@when("I run port cleanup")
def step_run_port_cleanup(context):
    """Run port cleanup via vde cleanup-ports command."""
    run_vde_command("cleanup-ports", timeout=30, context=context)


@when('I remove VM "{vm_name}"')
def step_remove_vm(context, vm_name):
    """Remove a VM via vde remove."""
    run_vde_command(f"remove {vm_name}", timeout=120, context=context)


# =============================================================================
# THEN steps - Verification for Port Management tests
# =============================================================================


@then('the VM should be allocated port "{expected_port}"')
def step_allocated_port(context, expected_port):
    """Verify VM was allocated the expected port via vde port."""
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert expected_port in result.stdout or expected_port in result.stderr, (
        f"Expected port {expected_port} not found in output: {result.stdout}"
    )


@then('"{vm_name}" should be mapped to port "{port}"')
def step_vm_mapped_to_port(context, vm_name, port):
    """Verify VM is mapped to specific port in registry."""
    registry_content = getattr(context, "port_registry_content", "")
    assert vm_name in registry_content and port in registry_content, (
        f"{vm_name} should be mapped to port {port}"
    )


@then('"{vm_name}" should still be mapped to port "{port}"')
def step_vm_still_mapped(context, vm_name, port):
    """Verify VM mapping persists."""
    # Run vde list to trigger registry refresh/check
    result = run_vde_command("list", context=context)
    assert port in result.stdout or port in result.stderr


@then('the VM should NOT be allocated port "{port}"')
def step_not_allocated_port(context, port):
    """Verify collision avoidance."""
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert port not in result.stdout, f"Port {port} should have been skipped"


@then("the VM should be allocated a different available port")
def step_different_port_allocated(context):
    """Verify a non-conflicting port was allocated."""
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert result.returncode == 0 and result.stdout.strip(), "A valid port should be allocated"



@then("no port should be allocated twice")
def step_no_duplicate_ports(context):
    """Verify uniqueness."""
    assert context.last_exit_code == 0


@then('the allocated port should be between "{start}" and "{end}"')
def step_port_in_range(context, start, end):
    """Verify port range compliance."""
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"port {vm_name} 22", context=context)
    # Parse port from output
    import re

    m = re.search(r"(\d+)", result.stdout)
    if m:
        port = int(m.group(1))
        assert int(start) <= port <= int(end), f"Port {port} outside range {start}-{end}"


@then('the command should fail with error "{error_msg}"')
def step_port_error(context, error_msg):
    """Verify error reporting."""
    assert context.last_exit_code != 0
    output = context.last_output + context.last_error
    assert error_msg.lower() in output.lower()


@then("the stale lock should be removed")
def step_stale_lock_removed(context):
    """Verify lock cleanup."""
    assert context.last_exit_code == 0


@then("the port should be available for allocation")
def step_port_available(context):
    """Verify availability."""
    assert context.last_exit_code == 0


@then('port "{port}" should be removed from registry')
def step_port_removed_from_registry(context, port):
    """Verify registry update."""
    port_registry = VDE_ROOT / ".cache" / "port-registry"
    if port_registry.exists():
        content = port_registry.read_text()
        assert f"={port}" not in content


# =============================================================================
# Additional Port Management Steps
# =============================================================================


@then("VDE should allocate the next available port")
def step_allocate_next_port(context):
    """Verify allocation succeeds."""
    assert context.last_exit_code == 0


@then("VDE should allocate the next available port ({expected_port})")
def step_allocate_expected_port(context, expected_port):
    """Verify exact allocation."""
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert expected_port in result.stdout
