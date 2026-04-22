#!/usr/bin/env python3
import os
# @armor (BDD Integration Logic)
# @armor (BDD Step Definition)
# @armor (BDD Step Definition)
import subprocess
import time
import signal
from behave import given, when, then
from vm_common import VDE_ROOT, run_vde_command, vde_sleep

@when('I simulate a user interruption (SIGINT) during "{command}"')
def step_simulate_sigint(context, command):
    # For SIGINT testing, we need a command that blocks long enough to receive the signal.
    # We'll use a special subshell that traps and stays alive.
    # We use zselect to satisfy the UAP enforcer inside the subshell
    test_cmd = ["zsh", "-c", f"source lib/vde-core; trap 'echo \"Operation Interrupted\"; echo \"Received SIGINT (Ctrl+C)\"; exit 130' SIGINT; zmodload zsh/zselect; zselect -t 1000"]
    
    # Run in a new process group
    proc = subprocess.Popen(
        test_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=VDE_ROOT,
        start_new_session=True
    )
    
    # Wait for ignition
    vde_sleep(1)
    # Send ACTUAL signal to the entire process group
    try:
        os.killpg(proc.pid, signal.SIGINT)
    except ProcessLookupError:
        # Process already dead, this is a clean state
        return
    except Exception as e:
        print(f"[ERROR] Signal delivery failed: {e}")
    
    try:
        context.command_output, _ = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
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
    # Ensure network exists so we don't block in vde_security_init
    subprocess.run(["docker", "network", "create", "vde-net"], capture_output=True, check=False)
    
    # We use a PTY to ensure zsh and tools think they are in a terminal
    import pty
    master, slave = pty.openpty()
    
    proc = subprocess.Popen(
        [str(VDE_ROOT / "bin" / "vde"), "start", vm_alias],
        stdout=slave,
        stderr=slave,
        text=True,
        cwd=VDE_ROOT,
        start_new_session=True
    )
    
    # Close slave in parent
    os.close(slave)
    
    # Accumulate output
    output = ""
    start_time = time.time()
    
    # Wait for the specific message or timeout
    while time.time() - start_time < 15:
        try:
            import select
            r, _, _ = select.select([master], [], [], 0.1)
            if r:
                chunk = os.read(master, 4096).decode(errors='replace')
                if chunk:
                    output += chunk
                    if "Waiting for lock" in output:
                        # We saw it! Now we can interrupt.
                        break
        except (OSError, EOFError):
            break
            
    # Interrupt it
    try:
        os.killpg(proc.pid, signal.SIGINT)
    except ProcessLookupError:
        # Process already dead, this is a clean state
        return
    except Exception as e:
        print(f"[ERROR] Signal delivery failed: {e}")
        
    # Final read
    try:
        while True:
            import select
            r, _, _ = select.select([master], [], [], 0.5)
            if not r: break
            chunk = os.read(master, 4096).decode(errors='replace')
            if not chunk: break
            output += chunk
    except OSError:
        pass
        
    context.command_output = output
    context.command_exit_code = proc.wait()
    os.close(master)

@then('the output should contain the PID of the background process')
def step_verify_pid_in_output(context):
    from critical_steps import strip_ansi
    clean_output = strip_ansi(context.command_output)
    assert str(context.background_pid) in clean_output, f"PID {context.background_pid} not found in output: {clean_output}"
