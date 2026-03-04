"""
Integration Test Environment - vde CLI, ssh-setup tests.

This environment is used for @integration tests.
Minimal Docker setup (test network only, no full cleanup).
"""

import os
import subprocess
import sys
from pathlib import Path

tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

from tests.features.steps.config import VDE_ROOT


def run_vde_command(command, timeout=60):
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


def before_all(context):
    """Setup for integration tests."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["DOCKER_BUILDKIT"] = "0"
    os.environ["VDE_TEST_MODE"] = "1"
    os.environ["VDE_NETWORK"] = "vde-testing"

    # Invalidate cache
    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()

    # Only create test network - no full cleanup
    print("[SETUP] Integration tests: creating test network...")
    run_vde_command("init --networks-only --testing", timeout=30)


def before_feature(context, feature):
    """Start SSH agent for SSH-related features."""
    if "ssh" in feature.name.lower() or "ssh" in feature.filename.lower():
        _start_ssh_agent()


def before_scenario(context, scenario):
    """Reset context."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0


def after_all(context):
    """Minimal teardown - just report completion."""
    print("[TEARDOWN] Integration tests complete.")


def _start_ssh_agent():
    """Start SSH agent if not running."""
    try:
        result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, timeout=10)
        if result.returncode in (0, 1):
            return True

        result = subprocess.run(["ssh-agent", "-s"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False
