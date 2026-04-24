#!/usr/bin/env python3
# @forge (Governance Sentinel)
"""
BDD Hooks for VDE test scenarios - SIMPLIFIED + PARSER OPTIMIZATION

This environment runs minimal setup and lets tests define their own requirements.
Includes persistent zsh process for parser tests.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Load root .env file (python.terminal.useEnvFile equivalent for Behave)
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.is_file():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                os.environ.setdefault(_key.strip(), _val.strip())

# Add tests directory to path
tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

# Feature and step directories
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

# Now import after path adjustment
from config import VDE_ROOT, VDE_SSH_DIR  # noqa: E402

# Track state
_SSH_AGENT_PID = None

# Parser library paths
VDE_PARSER = os.path.join(VDE_ROOT, "lib/vde-parser")
VDE_VM_COMMON = os.path.join(VDE_ROOT, "lib/vm-common")
VDE_SHELL_COMPAT = os.path.join(VDE_ROOT, "lib/vde-shell-compat")


def test_vde_command(command, timeout=60):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "0"
    # Ensure VDE_SSH_DIR is passed to subprocess
    if VDE_SSH_DIR:
        env["VDE_SSH_DIR"] = VDE_SSH_DIR

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=VDE_ROOT,
            env=env,
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout}s: {command}")
        return None


def before_all(context):
    """Global setup for BDD tests."""
    context.vde_root = VDE_ROOT
    context.temp_dir = tempfile.mkdtemp(prefix="vde_test_")

    # Ensure vde-net exists if docker is available
    try:
        res = subprocess.run(
            ["docker", "network", "inspect", "vde-net"],
            capture_output=True,
            check=False,
        )
        if res.returncode != 0:
            subprocess.run(["docker", "network", "create", "vde-net"], check=False)
    except Exception:
        pass


def after_all(context):
    """Global cleanup."""
    if hasattr(context, "temp_dir") and os.path.exists(context.temp_dir):
        shutil.rmtree(context.temp_dir)


def before_feature(context, feature):
    """Trigger cleanup for pristine features."""
    if "pristine" in feature.tags:
        sweep_script = os.path.join(VDE_ROOT, "bin/vde-tactical-sweep.zsh")
        if os.path.exists(sweep_script):
            subprocess.run([sweep_script], check=False)


def after_feature(context, feature):
    """Cleanup after pristine features."""
    if "pristine" in feature.tags:
        sweep_script = os.path.join(VDE_ROOT, "bin/vde-tactical-sweep.zsh")
        if os.path.exists(sweep_script):
            subprocess.run([sweep_script], check=False)


def before_scenario(context, scenario):
    """Reset state for each scenario."""
    context.output = ""
    context.exit_code = 0
    context.last_command = ""


def after_scenario(context, scenario):
    """Scenario cleanup."""
    pass
