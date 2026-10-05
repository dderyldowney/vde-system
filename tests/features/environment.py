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


def _cleanup_feature_containers(tags):
    """Purge containers associated with specific feature tags."""
    if "dns" in tags:
        for container in ["vde-python", "vde-postgres"]:
            subprocess.run(["docker", "rm", "-f", container], capture_output=True, check=False)
    if "jupyterlab" in tags:
        subprocess.run(["docker", "rm", "-f", "vde-jupyterlab"], capture_output=True, check=False)
    # Rule K caps the Hub at 3 concurrent Spokes. These features ignite Spokes
    # to verify real device state, so leaving them running makes the NEXT suite
    # fail with "Combat Load exceeded" -- including the Proof of Life, which
    # must start vde-python. Purge rather than stop, so the entrypoint re-runs
    # and the device nodes and port map are rebuilt on the next ignition.
    if "usb-serial" in tags:
        for container in ["vde-python", "vde-go"]:
            subprocess.run(["docker", "rm", "-f", container], capture_output=True, check=False)
    if "embed-spoke" in tags:
        subprocess.run(["docker", "rm", "-f", "vde-embed"], capture_output=True, check=False)


def before_feature(context, feature):
    """Trigger cleanup for pristine features."""
    if "pristine" in feature.tags:
        sweep_script = os.path.join(VDE_ROOT, "bin/vde-tactical-sweep.zsh")
        if os.path.exists(sweep_script):
            subprocess.run([sweep_script], check=False)
    
    _cleanup_feature_containers(feature.tags)


def after_feature(context, feature):
    """Cleanup after pristine features."""
    if "pristine" in feature.tags:
        sweep_script = os.path.join(VDE_ROOT, "bin/vde-tactical-sweep.zsh")
        if os.path.exists(sweep_script):
            subprocess.run([sweep_script], check=False)
    
    _cleanup_feature_containers(feature.tags)


def _hub_has_serial_board():
    """True when a real USB serial board is attached to the Hub right now."""
    import glob

    return bool(glob.glob("/dev/ttyUSB*") or glob.glob("/dev/ttyACM*"))


def before_scenario(context, scenario):
    """Reset state for each scenario."""
    context.output = ""
    context.exit_code = 0
    context.last_command = ""

    # USB passthrough hardware gate (Signet #526).
    # Scenarios tagged @hardware exercise a physically attached development
    # board. When none is present they are SKIPPED LOUDLY -- never passed --
    # per the 100% Real Tests Mandate. Simulating device state is forbidden.
    if "hardware" in scenario.tags and not _hub_has_serial_board():
        reason = (
            "SKIPPED (no hardware): '%s' requires a USB serial board attached "
            "to the Hub (/dev/ttyUSB* or /dev/ttyACM*). None is present, so "
            "this scenario is skipped rather than passed." % scenario.name
        )
        print("\n[VDE-HARDWARE-GATE] " + reason)
        scenario.skip(reason)
        return

    # Scenarios tagged @hardware-interactive need a board physically plugged or
    # unplugged DURING the run, so they cannot execute unattended. They run only
    # when VDE_HW_INTERACTIVE=1 declares the Clan Leader is present to act.
    if "hardware-interactive" in scenario.tags and os.environ.get(
        "VDE_HW_INTERACTIVE"
    ) != "1":
        reason = (
            "SKIPPED (needs a human): '%s' requires a board to be physically "
            "plugged or unplugged mid-scenario. Set VDE_HW_INTERACTIVE=1 and "
            "run it while present to act on the prompts." % scenario.name
        )
        print("\n[VDE-HARDWARE-GATE] " + reason)
        scenario.skip(reason)
        return

    # The mirror gate: scenarios tagged @no-board prove behaviour with an EMPTY
    # Hub and cannot be judged while a board is plugged in.
    if "no-board" in scenario.tags and _hub_has_serial_board():
        reason = (
            "SKIPPED (board attached): '%s' proves behaviour with NO serial "
            "board on the Hub, but one is currently attached. Unplug it to run "
            "this scenario." % scenario.name
        )
        print("\n[VDE-HARDWARE-GATE] " + reason)
        scenario.skip(reason)


def after_scenario(context, scenario):
    """Scenario cleanup."""
    # Automated restore for gospel audit tests
    if hasattr(context, 'backup_path') and os.path.exists(context.backup_path):
        # Infer the target path from the backup path
        target_path = context.backup_path.replace('.bak', '')
        shutil.move(context.backup_path, target_path)
    
    # Cleanup ghost scripts from bin/
    for ghost_name in ["vde-ghost-script.zsh", "vde-ghost-unseen.zsh"]:
        ghost = os.path.join(".", "bin", ghost_name)
        if os.path.exists(ghost):
            os.remove(ghost)


