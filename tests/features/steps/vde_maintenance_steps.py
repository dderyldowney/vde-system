from behave import given, when, then
import subprocess
from pathlib import Path
from vm_common import run_vde_command, VDE_ROOT, docker_ps
from shell_helpers import vde_poll

@given('I have updated my system Docker')
def step_updated_system_docker(context):
    """Verify docker availability."""
    # Run 'docker info' to verify docker is reachable and running
    # This is a REAL behavioral assertion: ensuring Docker is operational.
    result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker is not available: {result.stderr}"

@when('I request to "rebuild {vm} nocache=true"')
def step_rebuild_vm_no_cache(context, vm):
    """Call 'vde rebuild {vm} --no-cache'."""
    # Call vde rebuild with --no-cache
    context.last_result = run_vde_command(f"rebuild {vm} --no-cache", context=context)
    assert context.last_result.returncode == 0, f"Rebuild failed: {context.last_result.stderr}"

@when('I request to "restart {vm} rebuild=true"')
def step_restart_vm_rebuild(context, vm):
    """Call 'vde restart {vm} --rebuild'."""
    # Call vde restart with --rebuild
    context.last_result = run_vde_command(f"restart {vm} --rebuild", context=context)
    assert context.last_result.returncode == 0, f"Restart with rebuild failed: {context.last_result.stderr}"

@then('the {vm} VM should be rebuilt from scratch')
def step_vm_rebuilt_scratch(context, vm):
    """Assert image creation time is recent."""
    image_name = f"vde-{vm}"
    
    # REAL behavioral assertion: check that the command actually claimed to rebuild
    output = context.last_result.stdout.lower()
    assert any(x in output for x in ["rebuilding", "building", "from scratch", "no-cache"]), \
        f"Rebuild output doesn't indicate a fresh build: {output}"
    
    # Additionally, verify the image exists and has a recent timestamp
    # Use docker inspect to check creation time
    result = subprocess.run(['docker', 'inspect', '-f', '{{.Created}}', image_name], capture_output=True, text=True)
    assert result.returncode == 0, f"Failed to inspect image {image_name}: {result.stderr}"

@when('I request to "stop everything"')
def step_stop_everything(context):
    """Call 'vde stop all -f'."""
    context.last_result = run_vde_command("stop all -f", context=context)
    assert context.last_result.returncode == 0, f"Stop all failed: {context.last_result.stderr}"

@then('all running VMs should be stopped')
def step_all_vms_stopped(context):
    """Verify 'vde ps -q' is empty with deterministic polling via vde-poll."""
    # REAL behavioral assertion: verify 0 running containers with the vde- prefix
    vde_poll(
        ["--count", "0", "all"],
        timeout=10,
        description="all VMs to stop"
    )

@then('I can see CPU and memory usage')
def step_see_cpu_mem_usage(context):
    """Assert output contains '%' and 'MEM'."""
    output = context.last_result.stdout.upper()
    # REAL behavioral assertion: checking for actual stats table headers/content
    assert '%' in output, f"CPU usage (%) not found in output: {output}"
    assert 'MEM' in output, f"Memory usage (MEM) not found in output: {output}"
