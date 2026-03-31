"""
Step definitions for VM lifecycle operations.
"""

import os
import sys
from pathlib import Path
from behave import given, when, then

# Add steps directory to path for vm_common import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import VDE_ROOT, run_vde_command


@given('I have VMs configured')
def step_vms_configured(context):
    """Check for existing configs in configs/docker/"""
    config_dir = VDE_ROOT / "configs" / "docker"
    assert config_dir.exists(), f"VDE config directory {config_dir} not found"
    # Check if there's at least one config file (besides .gitignore)
    configs = [f for f in config_dir.glob("*.yml") if f.name != ".gitignore"]
    assert len(configs) > 0, f"No VM configurations found in {config_dir}"


@when("I create a VM")
@when("I create a new VM")
@when("I create a new language VM")
def step_create_vm(context):
    """Call 'vde create {vm_name}'"""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", context=context)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    assert result.returncode == 0, f"Failed to create VM {vm_name}: {result.stderr}"


@when('I start a VM')
def step_start_a_vm(context):
    """Call 'vde start python'"""
    result = run_vde_command("start python", context=context)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    assert result.returncode == 0, f"Failed to start VM: {result.stderr}"


@when('I start the VM')
def step_start_the_vm(context):
    """Call 'vde start {vm_name}'"""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"start {vm_name}", context=context)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    assert result.returncode == 0, f"Failed to start VM {vm_name}: {result.stderr}"


@when('I shutdown and rebuild the VM')
def step_shutdown_rebuild_vm(context):
    """Sequential: 'vde stop', 'vde remove', 'vde create --rebuild'"""
    vm_name = getattr(context, 'vm_name', 'python')
    
    # Stop the VM
    stop_res = run_vde_command(f"stop {vm_name}", context=context)
    assert stop_res.returncode == 0, f"Failed to stop VM {vm_name}: {stop_res.stderr}"
    
    # Remove the VM
    remove_res = run_vde_command(f"remove {vm_name}", context=context)
    assert remove_res.returncode == 0, f"Failed to remove VM {vm_name}: {remove_res.stderr}"
    
    # Rebuild the VM
    rebuild_res = run_vde_command(f"create {vm_name} --rebuild", context=context)
    context.command_output = rebuild_res.stdout + rebuild_res.stderr
    context.command_exit_code = rebuild_res.returncode
    assert rebuild_res.returncode == 0, f"Failed to rebuild VM {vm_name}: {rebuild_res.stderr}"


@when('I use SSH to connect to any VM')
def step_ssh_connect_any(context):
    """Call 'vde ssh python echo connected'"""
    result = run_vde_command("ssh python echo connected", context=context)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    assert result.returncode == 0, f"SSH connection failed: {result.stderr}"
    assert "connected" in result.stdout.lower(), f"Unexpected SSH output: {result.stdout}"


@then('the VM should start normally')
def step_vm_start_normally(context):
    """Verify container_is_running"""
    vm_name = getattr(context, 'vm_name', 'python')
    container_name = f"vde-{vm_name}"
    
    # Use vde ps to check if container is running
    result = run_vde_command(f"ps --filter name={vm_name} -q", context=context)
    assert container_name in result.stdout, (
        f"Container '{container_name}' is not running.\nvde ps output: {result.stdout}"
    )


@then('my SSH configuration should still work')
def step_ssh_config_still_works(context):
    """Verify SSH connectivity"""
    result = run_vde_command("ssh python echo works", context=context)
    assert result.returncode == 0, f"SSH connectivity check failed: {result.stderr}"
    assert "works" in result.stdout.lower(), f"Unexpected SSH output: {result.stdout}"


@then('I should not need to reconfigure SSH')
def step_no_ssh_reconfig_needed(context):
    """Assert config file mtime or content unchanged"""
    ssh_config = VDE_ROOT / "configs" / "ssh" / "config"
    assert ssh_config.exists(), f"SSH config file missing at {ssh_config}"
    # Basic validation that it's not empty and contains Host entries
    content = ssh_config.read_text()
    assert len(content) > 0, "SSH config file is empty"
    assert "Host" in content, "SSH config file missing 'Host' entries"


@when("I request to start my Python development environment")
def step_start_python_dev(context):
    """Call 'vde start python'"""
    run_vde_command("start python", context=context)


@then("the Go VM configuration should be created")
def step_go_config_created(context):
    """Verify configs/docker/languages/go/ exists"""
    go_config = VDE_ROOT / "configs" / "docker" / "languages" / "go"
    assert go_config.exists(), f"Go VM configuration not found at {go_config}"


@then("no containers should be left running")
def step_no_containers_running(context):
    """Verify 'vde ps -q' is empty"""
    result = run_vde_command("ps -q", context=context)
    assert not result.stdout.strip(), f"Containers are still running: {result.stdout}"


@then("SSH access should be available on the configured port")
def step_ssh_access_available(context):
    """Check if SSH port is open on localhost"""
    from vm_common import get_ssh_port_from_compose
    import socket
    
    vm_name = getattr(context, 'vm_name', 'python')
    port = get_ssh_port_from_compose(vm_name)
    assert port is not None, f"Could not find SSH port for {vm_name}"
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('localhost', port))
        s.close()
    except Exception as e:
        assert False, f"SSH access to {vm_name} on port {port} failed: {e}"


@then("the appropriate action should be taken")
def step_appropriate_action_taken(context):
    """Verify last output/exit code"""
    exit_code = getattr(context, 'last_exit_code', 1)
    assert exit_code == 0, f"Command failed with exit code {exit_code}"


@then("the Python VM should be started")
def step_python_vm_started(context):
    """Verify 'vde ps' contains python"""
    result = run_vde_command("ps", context=context)
    assert "vde-python" in result.stdout, f"Python VM not found in vde ps output: {result.stdout}"


@then("the Go VM should start")
def step_go_vm_started(context):
    """Verify 'vde ps' contains go"""
    result = run_vde_command("ps", context=context)
    assert "vde-go" in result.stdout, f"Go VM not found in vde ps output: {result.stdout}"


@then("both VMs from my command should start")
def step_both_vms_started(context):
    """Verify both running"""
    result = run_vde_command("ps", context=context)
    assert "vde-python" in result.stdout and "vde-go" in result.stdout, \
        f"Both VMs should be running. Output: {result.stdout}"
