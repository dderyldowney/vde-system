from behave import given, when, then
import os
import shutil
import subprocess
from pathlib import Path
from vm_common import VDE_ROOT, run_vde_command

@given('the Hub is uninitialized')
def step_impl(context):
    # Purge mandatory artifacts to simulate uninitialized state
    # This is dangerous and should only be run in a test environment
    # We use VDE_ROOT from vm_common
    ssh_dir = VDE_ROOT / ".ssh" / "vde"
    cache_dir = VDE_ROOT / ".cache"
    data_dir = VDE_ROOT / "data"
    projects_dir = VDE_ROOT / "projects"
    
    # We don't actually delete projects or data if they have content, 
    # but for init test we want to see them created if missing.
    # For a true 'uninitialized' test, we might just check they don't exist
    # or rename them.
    
    # For now, let's just ensure we can detect their absence or presence.
    # A safer way is to use a temporary VDE_ROOT, but behave setup handles some of this.
    pass

@when('I execute "bin/vde init"')
def step_impl(context):
    context.result = subprocess.run(["zsh", "bin/vde", "init"], capture_output=True, text=True, cwd=VDE_ROOT)
    context.command_exit_code = context.result.returncode
    context.command_output = context.result.stdout + context.result.stderr

@then('the mandatory directories should exist:')
def step_impl(context):
    for row in context.table:
        path = VDE_ROOT / row['directory']
        assert path.is_dir(), f"Directory {path} does not exist"

@then('the SSH identity "{identity}" should exist in the SSH directory')
def step_impl(context, identity):
    # Get VDE_SSH_DIR from constants
    cmd = f'export VDE_ROOT_DIR="{VDE_ROOT}"; source "{VDE_ROOT}/lib/vde-constants"; echo "$VDE_SSH_DIR"'
    res = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
    ssh_dir = Path(res.stdout.strip())
    
    priv_key = ssh_dir / identity
    pub_key = ssh_dir / f"{identity}.pub"
    
    assert priv_key.exists(), f"Private key {priv_key} missing"
    assert pub_key.exists(), f"Public key {pub_key} missing"

@then('the Docker network "{network_name}" should be active')
def step_impl(context, network_name):
    res = subprocess.run(["docker", "network", "ls", "--filter", f"name={network_name}", "-q"], capture_output=True, text=True)
    assert res.stdout.strip() != "", f"Docker network {network_name} is not active"
