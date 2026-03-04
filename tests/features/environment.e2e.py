"""
End-to-End Test Environment - Full Docker/VM workflows.

This environment is used for @docker and @e2e tests.
Full Docker cleanup and VM management.
"""

import os
import subprocess
import sys
from pathlib import Path

tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

from tests.features.steps.config import VDE_ROOT


def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "0"
    vde_script = os.path.join(VDE_ROOT, "scripts", "vde")
    full_cmd = f"cd {VDE_ROOT} && {vde_script} {command}"
    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def run_vde_ps(args=None, timeout=30):
    """Run vde-ps and return the result."""
    vde_ps = os.path.join(VDE_ROOT, "scripts", "vde-ps")
    cmd = ["zsh", vde_ps]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=VDE_ROOT)
    return result


def before_all(context):
    """Full setup for e2e tests."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["DOCKER_BUILDKIT"] = "0"
    os.environ["VDE_TEST_MODE"] = "1"
    os.environ["VDE_NETWORK"] = "vde-testing"

    # Invalidate cache
    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()

    # Full cleanup of existing containers
    print("[SETUP] E2E tests: cleaning up existing VDE containers...")
    result = run_vde_ps(["-a", "-q"])
    if result.returncode == 0:
        containers = [c.strip() for c in result.stdout.split("\n") if c.strip()]
        for container in containers:
            vm_name = container.replace("vde-", "") if container.startswith("vde-") else container
            run_vde_command(f"remove {vm_name}", timeout=30)
            print(f"[SETUP] Removed container: {container}")

    # Create test network
    run_vde_command("init --networks-only --testing", timeout=30)


def before_feature(context, feature):
    """Start SSH agent for SSH features."""
    if "ssh" in feature.name.lower() or "ssh" in feature.filename.lower():
        _start_ssh_agent()


def before_scenario(context, scenario):
    """Reset context."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0


def after_all(context):
    """Full teardown."""
    if os.environ.get("KEEP_VMS") == "true":
        print("[TEARDOWN] KEEP_VMS is true. Skipping cleanup.")
        return

    print("[TEARDOWN] E2E tests: cleaning up VDE resources...")
    result = run_vde_ps(["-a", "-q"])
    if result.returncode == 0:
        containers = [c.strip() for c in result.stdout.split("\n") if c.strip()]
        for container in containers:
            vm_name = container.replace("vde-", "") if container.startswith("vde-") else container
            run_vde_command(f"remove {vm_name}", timeout=30)


def _start_ssh_agent():
    """Start SSH agent."""
    try:
        result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, timeout=10)
        if result.returncode in (0, 1):
            return

        result = subprocess.run(["ssh-agent", "-s"], capture_output=True, text=True, timeout=10)
    except Exception:
        pass
