"""
BDD Step definitions for VDE Natural Language Commands.
Implements common patterns like "I request to '...'" for VM lifecycle operations.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from behave import given, then, when
from vm_common import run_vde_command, docker_ps, wait_for_container, VDE_ROOT

# All known VM types
_ALL_VMS = {
    "js",
    "python",
    "go",
    "rust",
    "nginx",
    "postgres",
    "redis",
    "mongodb",
    "mysql",
    "rabbitmq",
    "couchdb",
    "flutter",
    "r",
    "c",
    "cpp",
    "csharp",
    "java",
    "kotlin",
    "swift",
    "php",
    "ruby",
    "scala",
    "haskell",
    "lua",
    "elixir",
    "zig",
    "asm",
}


def _get_container_name(vm_name):
    """Convert VM name to container name."""
    return f"vde-{vm_name}"


def _container_exists(container_name):
    """Check if container exists (running or stopped) via vde ps -a."""
    result = run_vde_command("ps -a")
    return container_name in result.stdout


def _container_is_running(container_name):
    """Check if container is running via vde ps."""
    running = docker_ps()
    return container_name in running


def _extract_vms_from_command(command):
    """Extract VM names from a natural language command."""
    vms = []
    command_lower = command.lower()

    # Split by various delimiters
    parts = []
    if " and " in command_lower:
        parts = command_lower.split(" and ")
    elif "," in command_lower:
        parts = command_lower.split(",")

    if parts:
        for part in parts:
            part = part.strip()
            # Check each word against known VMs
            words = part.split()
            for word in words:
                word = word.strip().rstrip(".").rstrip(",")
                if word in _ALL_VMS:
                    vms.append(word)
    else:
        # Check each word
        words = command_lower.split()
        for word in words:
            word = word.strip().rstrip(".").rstrip(",")
            if word in _ALL_VMS:
                vms.append(word)

    return vms


def _execute_vde_create_and_start(vm_name, context):
    """Execute vde create and vde start for a VM."""
    # Use vde create first (it's safe if already exists)
    run_vde_command(f"create {vm_name}", context=context)
    # Then start
    result = run_vde_command(f"start {vm_name}", context=context)
    return result


def _capture_intent(request, context):
    """Run generate_plan directly to capture intent for verification steps."""
    vde_parser = VDE_ROOT / "lib" / "vde-parser"
    vde_vm_common = VDE_ROOT / "lib" / "vm-common"
    vde_shell_compat = VDE_ROOT / "lib" / "vde-shell-compat"

    cmd = f"source {vde_shell_compat} && source {vde_vm_common} && source {vde_parser} && generate_plan '{request}'"
    res = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True, cwd=VDE_ROOT)

    context.intents = []
    context.vms = []

    if res.returncode == 0:
        for line in res.stdout.split("\n"):
            if line.startswith("INTENT:"):
                context.intents.append(line.split(":")[1])
            elif line.startswith("VM:"):
                context.vms.append(line.split(":")[1])
    return res


# =============================================================================
# I request to "..." - Natural Language Command Patterns
# =============================================================================


@when('I request to "{command}"')
def step_request_command(context, command):
    """Execute a natural language VDE command."""
    # 1. Capture intent first for verification steps
    _capture_intent(command, context)

    # 2. Execute the command
    command_lower = command.lower()
    all_results = []
    all_stdout = []
    all_stderr = []

    # Handle multi-part commands: "stop all and start X and Y"
    if "stop all" in command_lower and "start" in command_lower:
        # Stop all first
        result = run_vde_command("stop all", context=context)
        all_results.append(result)
        all_stdout.append(result.stdout)
        all_stderr.append(result.stderr)

        # Extract VMs to start and recreate if needed
        vms = _extract_vms_from_command(command)
        for vm in vms:
            result = _execute_vde_create_and_start(vm, context)
            all_results.append(result)
            all_stdout.append(result.stdout)
            all_stderr.append(result.stderr)

        context.vde_command_result = all_results[-1]
        context.vde_command_output = "\n".join(all_stdout) + "\n".join(all_stderr)
        context.vde_command_exit_code = max(r.returncode for r in all_results)
        return

    # Handle "start all services"
    if "start all services" in command_lower:
        service_vms = ["go", "rust", "nginx"]
        for vm in service_vms:
            result = _execute_vde_create_and_start(vm, context)
            all_results.append(result)
            all_stdout.append(result.stdout)
            all_stderr.append(result.stderr)

        context.vde_command_result = all_results[-1]
        context.vde_command_output = "\n".join(all_stdout) + "\n".join(all_stderr)
        context.vde_command_exit_code = max(r.returncode for r in all_results)
        return

    # Handle "stop all" / "stop everything"
    if "stop all" in command_lower or "stop everything" in command_lower:
        result = run_vde_command("stop all", context=context)
        context.vde_command_result = result
        context.vde_command_output = result.stdout + result.stderr
        context.vde_command_exit_code = result.returncode
        return

    # Handle "restart X rebuild=true" pattern
    if "restart" in command_lower and "rebuild=true" in command_lower:
        vms = _extract_vms_from_command(command)
        vm_name = vms[0] if vms else "python"
        result = run_vde_command(f"restart {vm_name} --rebuild", context=context)
        context.vde_command_result = result
        context.vde_command_output = result.stdout + result.stderr
        context.vde_command_exit_code = result.returncode
        return

    # Handle "start X and Y" pattern
    if command_lower.startswith("start ") and (" and " in command_lower or "," in command_lower):
        vms = _extract_vms_from_command(command)
        if vms:
            for vm in vms:
                result = _execute_vde_create_and_start(vm, context)
                all_results.append(result)
                all_stdout.append(result.stdout)
                all_stderr.append(result.stderr)

            context.vde_command_result = all_results[-1]
            context.vde_command_output = "\n".join(all_stdout) + "\n".join(all_stderr)
            context.vde_command_exit_code = max(r.returncode for r in all_results)
            return

    # Handle "create X and Y" pattern
    if command_lower.startswith("create ") and (" and " in command_lower or "," in command_lower):
        vms = _extract_vms_from_command(command)
        if vms:
            for vm in vms:
                result = run_vde_command(f"create {vm}", context=context)
                all_results.append(result)
                all_stdout.append(result.stdout)
                all_stderr.append(result.stderr)

            context.vde_command_result = all_results[-1]
            context.vde_command_output = "\n".join(all_stdout) + "\n".join(all_stderr)
            context.vde_command_exit_code = max(r.returncode for r in all_results)
            return

    # Default: simple command
    result = run_vde_command(command, context=context)
    context.vde_command_result = result
    context.vde_command_output = result.stdout + result.stderr
    context.vde_command_exit_code = result.returncode


# =============================================================================
# I should see ... - Verification Patterns
# =============================================================================


@then("I should see which VMs are stopped")
def step_should_see_stopped(context):
    """Verify stopped VMs are shown in output."""
    output = getattr(context, "vde_command_output", "")
    assert "stopped" in output.lower() or "not running" in output.lower(), (
        f"Expected to see stopped VMs in output: {output}"
    )
