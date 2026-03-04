"""
BDD Hooks for VDE test scenarios - SIMPLIFIED

This environment runs minimal setup and lets tests define their own requirements.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add tests directory to path
tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

try:
    from test_config_loader import get_behave_config
except ImportError:

    def get_behave_config():
        return None


# Import shared configuration
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from config import VDE_ROOT

# Track state
_SSH_AGENT_PID = None


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


def run_vde_ps(args=None, timeout=30):
    """Run vde-ps and return the result."""
    vde_ps = os.path.join(VDE_ROOT, "scripts", "vde-ps")
    cmd = ["zsh", vde_ps]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=VDE_ROOT)
    return result


def before_all(context):
    """Minimal setup."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["DOCKER_BUILDKIT"] = "0"
    os.environ["VDE_TEST_MODE"] = "1"

    # Invalidate cache
    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()


def before_feature(context, feature):
    """Tier-aware setup based on feature tags."""
    tags = feature.tags

    # Check for unit tests - no Docker needed
    if "@unit" in tags:
        print("[SETUP] Unit test mode")
        return

    # Check for integration tests - minimal Docker
    if "@integration" in tags:
        print("[SETUP] Integration test mode")
        os.environ["VDE_NETWORK"] = "vde-testing"
        run_vde_command("init --networks-only --testing", timeout=30)
        return

    # Check for docker tests - full setup
    if "@docker" in tags:
        print("[SETUP] Docker test mode")
        os.environ["VDE_NETWORK"] = "vde-testing"
        # Clean up existing containers
        result = run_vde_ps(["-a", "-q"])
        if result.returncode == 0:
            containers = [c.strip() for c in result.stdout.split("\n") if c.strip()]
            for container in containers:
                vm_name = (
                    container.replace("vde-", "") if container.startswith("vde-") else container
                )
                run_vde_command(f"remove {vm_name}", timeout=30)
        run_vde_command("init --networks-only --testing", timeout=30)
        return

    # Default: integration mode for core-infrastructure
    if "core-infrastructure" in feature.filename:
        print("[SETUP] Core infrastructure - minimal setup")
        os.environ["VDE_NETWORK"] = "vde-testing"
        # Don't run full init by default - too slow


def before_scenario(context, scenario):
    """Reset context."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0


def after_all(context):
    """No teardown."""
    pass
