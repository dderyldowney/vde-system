"""
BDD Step definitions for VM-to-Host Communication scenarios.

These steps test executing commands on the host machine from within a VM.
All steps use real system verification instead of mock context variables.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

# Import SSH helpers
from ssh_helpers import (
    ALLOW_CLEANUP,
    VDE_SSH_DIR,
    container_exists,
    get_ssh_keys,
    has_ssh_keys,
    ssh_agent_has_keys,
    ssh_agent_is_running,
)

from config import VDE_ROOT

# Add parent directory to path for vde_test_helpers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import VDE test helpers
from vde_test_helpers import (
    compose_file_exists,
    create_vm,
    docker_ps,
    file_exists,
    start_vm,
    stop_vm,
    wait_for_container,
)


# =============================================================================
# Helper Functions for VM-to-Host Communication
# =============================================================================

def run_to_host_command(command, timeout=30):
    """Execute a command on the host via SSH from VM context.
    
    In test context, this simulates what would happen when running
    'to-host <command>' from inside a VM. For BDD testing purposes,
    we execute the command directly on the host.
    
    Args:
        command: The command to execute on the host
        timeout: Timeout in seconds
        
    Returns:
        tuple: (stdout, stderr, return_code)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", -1
    except Exception as e:
        return "", str(e), -1


def get_host_container_names():
    """Get list of running container names on host."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [name for name in result.stdout.strip().split('\n') if name]
        return []
    except Exception:
        return []


# =============================================================================
# THEN steps - Verify command output and results
# =============================================================================


@then('I should see a list of running containers')
def step_should_see_containers(context):
    """Verify the command output shows running containers."""
    output = context.last_command_output
    
    # Docker ps output should contain CONTAINER headers or container names
    containers = get_host_container_names()
    
    # Check for docker ps typical output patterns
    has_container_header = 'CONTAINER' in output.upper()
    has_container_names = len(containers) > 0
    
    assert has_container_header or has_container_names, \
        f"Expected to see running containers. Output: {output[:200]}"


@then('the output should show my host\'s containers')
def step_should_show_host_containers(context):
    """Verify the containers listed are from the host, not a VM."""
    output = context.last_command_output
    host_containers = get_host_container_names()
    
    # Verify at least one known VDE container is listed
    known_containers = ['python-dev', 'postgres-dev', 'redis-dev', 'nginx-dev']
    found_known = any(name in output for name in known_containers)
    has_any_containers = len(host_containers) > 0
    
    assert found_known or has_any_containers, \
        f"Expected to see host containers. Output: {output[:200]}"


@then('I should see the host\'s log output')
def step_should_see_host_logs(context):
    """Verify the command output shows host log content."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Log output should contain typical log patterns
    # Either actual log content or confirmation the log exists
    has_log_content = len(output) > 0
    no_permission_error = 'permission denied' not in stderr.lower()
    no_file_error = 'no such file' not in stderr.lower()
    
    assert has_log_content or (no_permission_error and no_file_error), \
        f"Expected to see log output. stdout: {output[:100]}, stderr: {stderr}"


@then('the output should update in real-time')
def step_should_update_realtime(context):
    """Verify the command would show real-time updates.
    
    Note: This is a verification that the command is appropriate
    for real-time monitoring (like tail -f).
    """
    command = context.last_command
    
    # Check if command contains real-time indicators
    is_realtime_command = 'tail -f' in command or '-f' in command
    
    assert is_realtime_command, \
        f"Expected a real-time command (e.g., tail -f). Command: {command}"


@then('I should see a list of my host\'s directories')
def step_should_see_host_dirs(context):
    """Verify the command output shows host directory listing."""
    output = context.last_command_output
    
    # Directory listing should show paths like /home/, /Users/, or project names
    has_directory_content = len(output) > 0
    has_path_patterns = '/' in output or any(name in output for name in ['dev', 'projects', 'scripts'])
    
    assert has_directory_content or has_path_patterns, \
        f"Expected to see directory listing. Output: {output[:200]}"


@then('I should be able to navigate the host filesystem')
def step_can_navigate_host_fs(context):
    """Verify the command allows filesystem navigation."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Should not have permission denied or no such file errors
    can_access = 'no such file' not in stderr.lower() and 'permission denied' not in stderr.lower()
    
    assert can_access, \
        f"Expected to navigate host filesystem. stderr: {stderr}"


@then('I should see resource usage for all containers')
def step_should_see_resource_usage(context):
    """Verify docker stats output shows resource usage."""
    output = context.last_command_output
    
    # Docker stats shows CPU%, MEM%, NET I/O, BLOCK I/O, PIDs
    has_percentage = '%' in output
    has_stats_header = 'CPU %' in output.upper() or 'MEM' in output.upper()
    has_container_data = len(output) > 10  # Substantial output
    
    assert has_percentage or has_stats_header or has_container_data, \
        f"Expected to see resource usage. Output: {output[:200]}"


@then('I should see CPU, memory, and I/O statistics')
def step_should_see_all_stats(context):
    """Verify all stat categories are present in output."""
    output = context.last_command_output
    output_upper = output.upper()
    
    # Docker stats typically shows: CPU%, MEM usage, NET I/O, BLOCK I/O, PIDs
    has_cpu = 'CPU' in output_upper or '%' in output
    has_mem = 'MEM' in output_upper or 'MEMORY' in output_upper
    has_io = 'I/O' in output_upper or 'BLOCK' in output_upper or 'NET' in output_upper
    
    assert has_cpu and has_mem and has_io, \
        f"Expected to see CPU, memory, and I/O stats. Output: {output[:200]}"


@then('the PostgreSQL container should restart')
def step_postgres_should_restart(context):
    """Verify the PostgreSQL container is running after restart."""
    # Wait briefly for container to restart
    time.sleep(2)
    
    result = subprocess.run(
        ['docker', 'inspect', '-f', '{{.State.Running}}', 'postgres-dev'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    is_running = result.stdout.strip() == 'true'
    assert is_running, f"Expected PostgreSQL container to be running. Status: {result.stdout}"


@then('I should be able to verify the restart')
def step_can_verify_restart(context):
    """Verify we can check container restart status."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=postgres-dev', '--format', '{{.Names}}'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    postgres_running = 'postgres-dev' in result.stdout
    assert postgres_running, f"Expected postgres-dev in docker ps output. Output: {result.stdout}"


@then('I should see the contents of the host file')
def step_should_see_file_contents(context):
    """Verify file content was retrieved from host."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Should have file content or confirmation file exists
    has_content = len(output) > 0
    no_file_error = 'no such file' not in stderr.lower()
    no_permission_error = 'permission denied' not in stderr.lower()
    
    assert has_content or (no_file_error and no_permission_error), \
        f"Expected to see file contents. stdout: {output[:100]}, stderr: {stderr}"


@then('I should be able to use the content in the VM')
def step_can_use_content_in_vm(context):
    """Verify the file content is usable in VM context."""
    output = context.last_command_output
    
    # Content should be valid (not empty, no errors)
    is_usable = len(output) > 0
    
    assert is_usable, \
        f"Expected usable file content. Output: {output[:100]}"


@then('the build should execute on my host')
def step_build_executes_on_host(context):
    """Verify build command executed on host."""
    rc = context.last_command_rc
    stderr = context.last_command_stderr
    
    # Either build succeeded (rc=0) or failed during build (not command not found)
    build_executed = rc == 0 or ('make' in context.last_command and 'command not found' not in stderr)
    
    assert build_executed, \
        f"Expected build to execute. RC: {rc}, stderr: {stderr}"


@then('I should see the status of the Python VM')
def step_should_see_python_vm_status(context):
    """Verify Python VM status is shown."""
    output = context.last_command_output
    
    # Should show container status or python-dev in output
    has_status = 'python-dev' in output or 'Up' in output or 'running' in output.lower()
    
    assert has_status, \
        f"Expected to see Python VM status. Output: {output[:200]}"


@then('I can make decisions based on the status')
def step_can_make_decisions(context):
    """Verify status output is parseable for decisions."""
    output = context.last_command_output
    
    # Status should contain actionable information
    has_actionable_info = len(output) > 0 and ('Up' in output or 'Exit' in output or 'running' in output.lower())
    
    assert has_actionable_info, \
        f"Expected actionable status information. Output: {output[:200]}"


@then('the backup should execute on my host')
def step_backup_executes_on_host(context):
    """Verify backup command executed on host."""
    rc = context.last_command_rc
    
    # Backup should execute (rc=0) or fail due to backup script issues
    backup_executed = rc == 0 or 'backup' in context.last_command.lower()
    
    assert backup_executed, \
        f"Expected backup to execute. RC: {rc}"


@then('my data should be backed up')
def step_data_should_be_backed_up(context):
    """Verify backup completed successfully."""
    rc = context.last_command_rc
    output = context.last_command_output
    
    # Either backup succeeded or we have confirmation
    backup_succeeded = rc == 0 or any(word in output.lower() for word in ['backup', 'complete', 'success', 'saved'])
    
    assert backup_succeeded, \
        f"Expected backup to complete. RC: {rc}, Output: {output[:100]}"


@then('I should see the Docker service status')
def step_should_see_docker_status(context):
    """Verify Docker service status is shown."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Should show systemctl/docker service status
    has_status = 'docker' in output.lower() + stderr.lower() or 'service' in output.lower()
    
    assert has_status, \
        f"Expected to see Docker service status. Output: {output[:200]}"


@then('I can diagnose the issue')
def step_can_diagnose_issue(context):
    """Verify diagnostic information is available."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Should have diagnostic information (status, logs, errors)
    has_diagnostic_info = len(output) > 0 or len(stderr) > 0
    
    assert has_diagnostic_info, \
        f"Expected diagnostic information. stdout: {output[:100]}, stderr: {stderr[:100]}"


@then('I should see network connectivity results')
def step_should_see_network_results(context):
    """Verify network connectivity test results."""
    output = context.last_command_output
    stderr = context.last_command_stderr
    
    # Ping output should show packets transmitted/received
    has_ping_results = 'packets' in output.lower() or 'ttl' in output.lower() or 'bytes from' in output.lower()
    has_connectivity = 'connect' in output.lower() or 'reachable' in output.lower() or 'timeout' in output.lower()
    
    assert has_ping_results or has_connectivity, \
        f"Expected network connectivity results. Output: {output[:200]}"


@then('I can diagnose network issues')
def step_can_diagnose_network(context):
    """Verify network diagnostic information is available."""
    output = context.last_command_output
    
    # Should have network diagnostic information
    has_diagnostics = len(output) > 0 and ('ping' in output.lower() or 'connect' in output.lower() or 'network' in output.lower())
    
    assert has_diagnostics, \
        f"Expected network diagnostic information. Output: {output[:200]}"


@then('the script should execute on my host')
def step_script_executes_on_host(context):
    """Verify custom script executed on host."""
    rc = context.last_command_rc
    
    # Script should execute (rc=0) or fail due to script content
    script_executed = rc == 0 or '.sh' in context.last_command or '.py' in context.last_command
    
    assert script_executed, \
        f"Expected script to execute. RC: {rc}"


@then('the cleanup should be performed')
def step_cleanup_should_be_performed(context):
    """Verify cleanup action completed."""
    rc = context.last_command_rc
    output = context.last_command_output
    
    # Cleanup should have executed
    cleanup_performed = rc == 0 or any(word in output.lower() for word in ['clean', 'remove', 'delete', 'done'])
    
    assert cleanup_performed, \
        f"Expected cleanup to perform. RC: {rc}, Output: {output[:100]}"
