"""
Step definitions for service-volume-hardening.feature.
"""

import os
import sys
import subprocess
import time
from behave import given, when, then

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import VDE_ROOT, run_vde_command, container_is_running, get_container_id

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
    # Execute psql command in container as devuser (sudo to postgres)
    # Add retry loop to handle "database system is starting up"
    # Use IF NOT EXISTS to prevent error if already present from previous interrupted run
    cmd = f"exec {vm_name} \"sudo -u postgres psql -d postgres -c 'CREATE TABLE IF NOT EXISTS {table_name} (id serial PRIMARY KEY);'\""
    
    start_time = time.time()
    timeout = 30
    last_err = ""
    while time.time() - start_time < timeout:
        r = run_vde_command(cmd, timeout=10)
        if r.returncode == 0:
            return
        last_err = r.stderr
        # Broaden retry to catch socket errors and connection refused
        low_err = last_err.lower()
        if "starting up" not in low_err and "no such file" not in low_err and "connection refused" not in low_err and "could not connect" not in low_err:
            break
        # Use sub-second sleep for faster response
        time.sleep(0.5)
        
    assert False, f"Failed to create table within {timeout}s: {last_err}"

@then('the table "{table_name}" should still exist in "{vm_name}"')
def step_table_should_exist(context, table_name, vm_name):
    cmd = f"exec {vm_name} \"sudo -u postgres psql -d postgres -c '\\dt {table_name}'\""
    
    start_time = time.time()
    timeout = 30
    last_err = ""
    while time.time() - start_time < timeout:
        r = run_vde_command(cmd, timeout=10)
        if r.returncode == 0:
            assert table_name in r.stdout, f"Table {table_name} not found in {vm_name}"
            return
        last_err = r.stderr
        # Broaden retry to catch socket errors and connection refused
        low_err = last_err.lower()
        if "starting up" not in low_err and "no such file" not in low_err and "connection refused" not in low_err and "could not connect" not in low_err:
            break
        # Use sub-second sleep for faster response
        time.sleep(0.5)
        
    assert False, f"Failed to check table existence within {timeout}s: {last_err}"

@then('host port {port:d} should be open')
def step_port_should_be_open(context, port):
    # Check if port is open on localhost
    try:
        # Simple nc check
        subprocess.run(["nc", "-z", "localhost", str(port)], check=True, timeout=5)
    except subprocess.CalledProcessError:
        assert False, f"Port {port} is not open on localhost"

@then('I should wait for VM "{vm_name}" to be healthy')
def step_wait_for_healthy(context, vm_name):
    start_time = time.time()
    timeout = 60
    while time.time() - start_time < timeout:
        r = run_vde_command(f"inspect {vm_name} --health", timeout=10)
        if r.returncode == 0 and "healthy" in r.stdout.lower():
            return
        time.sleep(0.5)
    assert False, f"VM {vm_name} did not become healthy within {timeout}s"

@then('the database should be ready for connections immediately')
def step_db_ready_immediately(context):
    vm_name = context.vm_name
    cmd = f"exec {vm_name} \"sudo -u postgres psql -d postgres -c 'SELECT 1'\""
    r = run_vde_command(cmd, timeout=10)
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
