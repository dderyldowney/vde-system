#!/usr/bin/env python3
# VDE ARCHITECTURAL RECORD
# @forge (Error Handling Steps)
from behave import given, when, then
import subprocess
import os
from pathlib import Path
from vm_common import VDE_ROOT, run_vde_command

@given('a background process holds a lock on "{vm_alias}"')
def step_background_lock(context, vm_alias):
    lock_dir = VDE_ROOT / ".locks" / "vms" / f"{vm_alias}.lock"
    lock_dir.mkdir(parents=True, exist_ok=True)
    pid = 99999
    (lock_dir / "pid").write_text(f"{pid}")
    (lock_dir / f"ticket-0000000001-{pid}").touch()
    context.background_pid = pid

@when('I simulate a user interruption (SIGINT) during "{command_str}"')
def step_physical_sigint(context, command_str):
    # Strip 'bin/vde ' from the start if present
    cmd = command_str.replace("bin/vde ", "")
    rig_path = VDE_ROOT / "plans" / "scripts" / "signal-strike.zsh"
    
    # Execute the physical injection rig
    res = subprocess.run(
        [str(rig_path), "SIGINT", cmd],
        capture_output=True,
        text=True,
        cwd=VDE_ROOT
    )
    
    context.command_output = res.stdout + res.stderr
    context.command_exit_code = res.returncode

@when('I simulate a forceful termination (SIGKILL) during "{command_str}"')
def step_physical_sigkill(context, command_str):
    cmd = command_str.replace("bin/vde ", "")
    rig_path = VDE_ROOT / "plans" / "scripts" / "signal-strike.zsh"
    
    res = subprocess.run(
        [str(rig_path), "SIGKILL", cmd],
        capture_output=True,
        text=True,
        cwd=VDE_ROOT
    )
    
    context.command_output = res.stdout + res.stderr
    context.command_exit_code = res.returncode

@then('the output should contain the PID of the background process')
def step_verify_pid_in_output(context):
    from critical_steps import strip_ansi
    clean_output = strip_ansi(context.command_output)
    assert str(context.background_pid) in clean_output, f"PID {context.background_pid} not found in output: {clean_output}"

@when('I attempt to start "{vm_alias}" in the foreground')
def step_attempt_start(context, vm_alias):
    # Use the rig for consistency even here if we want to capture output and interrupt
    context.target_vm = vm_alias
    step_physical_sigint(context, f"start {vm_alias}")
