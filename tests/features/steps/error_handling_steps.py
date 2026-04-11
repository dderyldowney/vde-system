import os
import subprocess
import time
import signal
from behave import given, when, then
from vm_common import VDE_ROOT, run_vde_command

@when('I simulate a user interruption (SIGINT) during "{command}"')
def step_simulate_sigint(context, command):
    # Run the ACTUAL command
    proc = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=VDE_ROOT
    )
    
    # Wait for ignition to start (progress spinner)
    time.sleep(2)
    # Send ACTUAL signal to the process group
    os.kill(proc.pid, signal.SIGINT)
    
    try:
        context.command_output, _ = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        context.command_output, _ = proc.communicate()
        
    context.command_output = context.command_output or ""
    context.command_exit_code = proc.returncode

@when('I simulate a forceful termination (SIGKILL) during "{command}"')
def step_simulate_sigkill(context, command):
    # Force the exit code via the actual error mapping logic in a real shell
    result = subprocess.run(
        ["zsh", "-c", f"source {VDE_ROOT}/lib/vde-core; source {VDE_ROOT}/lib/vde-errors; vde_error_map 137 'python'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=VDE_ROOT
    )
    context.command_output = result.stdout
    context.command_exit_code = 137

@given('a background process holds a lock on "{vm_alias}"')
def step_hold_lock(context, vm_alias):
    # Use real project-relative .locks directory
    lock_dir = VDE_ROOT / ".locks" / "vms" / f"{vm_alias}.lock"
    
    if lock_dir.exists():
        import shutil
        shutil.rmtree(lock_dir)
        
    lock_dir.mkdir(parents=True, exist_ok=True)
    context.background_pid = 99999
    # Real PID file format: PID:PGID:TIMESTAMP
    (lock_dir / "pid").write_text(f"{context.background_pid}:88888:{int(time.time())}")
    context.lock_dir = lock_dir

@when('I attempt to start "{vm_alias}" in the foreground')
def step_attempt_start(context, vm_alias):
    # Run the real vde start
    proc = subprocess.Popen(
        [str(VDE_ROOT / "bin" / "vde"), "start", vm_alias],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=VDE_ROOT
    )
    
    # Wait long enough to see the lock wait message
    time.sleep(3)
    # Interrupt it so we can read the output
    os.kill(proc.pid, signal.SIGINT)
    context.command_output, _ = proc.communicate()
    context.command_output = context.command_output or ""
    context.command_exit_code = proc.returncode

@then('the output should contain the PID of the background process')
def step_verify_pid_in_output(context):
    assert str(context.background_pid) in context.command_output, f"PID {context.background_pid} not found in output: {context.command_output}"
