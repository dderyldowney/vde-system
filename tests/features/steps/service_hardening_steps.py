"""
Step definitions for service-volume-hardening.feature.
"""

import os
import sys
import subprocess

from behave import given, when, then

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import VDE_ROOT, run_vde_command, container_is_running, get_container_id
from shell_helpers import vde_poll

@given("{vm_name} service VM is created")
def step_service_vm_created(context, vm_name):
    # Ensure VM is created
    run_vde_command(f"create {vm_name}", timeout=60)
    context.vm_name = vm_name

@given('VM "{vm_name}" is created with ports "{ports}"')
def step_vm_created_with_ports(context, vm_name, ports):
    # Use add-vm-type to ensure ports are in config
    ssh_port_res = run_vde_command(f"port {vm_name}", timeout=10)
    ssh_port = ssh_port_res.stdout.strip() if ssh_port_res.returncode == 0 else "2406"
    
    # Remove and re-add with new service ports
    run_vde_command(f"uninstall {vm_name}", timeout=30)
    
    # Define a starting command that starts the service and sshd
    start_cmd = "/usr/sbin/sshd -D"
    if vm_name == "redis":
        start_cmd = "sh -c 'service redis-server start && /usr/sbin/sshd -D'"
    elif vm_name == "postgres":
        start_cmd = "sh -c 'service postgresql start && /usr/sbin/sshd -D'"
        
    cmd = f"add --type service --ssh-port {ssh_port} --svc-port {ports} {vm_name} \"{start_cmd}\""
    run_vde_command(cmd, timeout=30)
    # Re-create the compose file
    run_vde_command(f"create {vm_name} --force", timeout=60)
    # Force rebuild to ensure new ports are picked up
    run_vde_command(f"start {vm_name} --rebuild", timeout=300)
    context.vm_name = vm_name
    context.requested_ports = ports.split(',')

@given('VM "{vm_name}" is stopped')
def step_vm_stopped(context, vm_name):
    run_vde_command(f"stop {vm_name}", timeout=60)
    context.vm_name = vm_name

@given('I create a test table "{table_name}" in "{vm_name}"')
def step_create_test_table(context, table_name, vm_name):
    """Prerequisite: Create a test table in the VM."""
    step_create_table(context, table_name, vm_name)

@when('I create a table "{table_name}" in "{vm_name}"')
def step_create_table(context, table_name, vm_name):
    cmd = f"sudo -u postgres psql -d postgres -c 'CREATE TABLE IF NOT EXISTS {table_name} (id serial PRIMARY KEY);'"
    vde_poll(
        ["--exec", cmd, vm_name],
        timeout=30,
        description=f"table '{table_name}' creation in {vm_name}"
    )

@then('the table "{table_name}" should still exist in "{vm_name}"')
def step_table_should_exist(context, table_name, vm_name):
    cmd = f"sudo -u postgres psql -d postgres -c '\\dt {table_name}'"
    vde_poll(
        ["--exec", cmd, vm_name],
        timeout=30,
        description=f"table '{table_name}' existence in {vm_name}"
    )

@then('host port {port:d} should be open')
def step_port_should_be_open(context, port):
    # Map to vde-poll --port
    vde_poll(
        ["--port", str(port), "vde-base"],
        timeout=10,
        description=f"host port {port}"
    )

@then('I should wait for VM "{vm_name}" to be healthy')
def step_wait_for_healthy(context, vm_name):
    # Map to vde-poll --health
    vde_poll(
        ["--health", vm_name],
        timeout=60,
        description=f"VM '{vm_name}' health"
    )

@then('the database should be ready for connections immediately')
def step_db_ready_immediately(context):
    vm_name = context.vm_name
    cmd = f"sudo -u postgres psql -d postgres -c 'SELECT 1'"
    # Note: Immediately means we don't use vde_poll here, but run once
    r = run_vde_command(f"exec {vm_name} \"{cmd}\"", timeout=10)
    assert r.returncode == 0, f"Database not ready: {r.stderr}"

@when('I ping "{target}" from "{source}"')
def step_ping_container(context, target, source):
    # Force rebuild source to ensure it has ping (iputils-ping)
    vm_name = source.replace('vde-', '')
    run_vde_command(f"start {vm_name} --rebuild", timeout=300)
    
    # vde exec source sudo ping -c 1 target
    cmd = f"exec {source} \"sudo ping -c 1 {target}\""
    context.ping_result = run_vde_command(cmd, timeout=30)

@then("the ping should be successful")
def step_ping_successful(context):
    assert context.ping_result.returncode == 0, f"Ping failed: {context.ping_result.stderr}"
