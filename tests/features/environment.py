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


# Files a VM-type registration mutates. Scenarios tagged @vault-mutating are
# wrapped in a backup/restore of these, so a failure mid-registration cannot
# leave the Beskar Vault or the SSH configs altered.
_VAULT_FILES = (
    "data/vm-types.conf",
    "data/vm-types.json",
    "configs/ssh/config",
    "configs/ssh/config.spoke",
)

# add-vm-type copies configs/ssh/config to the LIVE ssh config, which lives
# outside the repository. Restoring only the in-repo files would leave the
# user's real ~/.ssh/vde/config carrying a Host block for a throwaway Spoke,
# pointing at a port that no longer exists.
def _live_ssh_config():
    if not VDE_SSH_DIR:
        return None
    return os.path.join(VDE_SSH_DIR, "config")


def _vault_backup():
    """
    Snapshot the Vault and the live SSH config.

    Keys are repo-relative paths, except the live SSH config which is keyed by
    its absolute path since it sits outside the repository.
    """
    snapshot = {}
    targets = [os.path.join(VDE_ROOT, rel) for rel in _VAULT_FILES]
    live = _live_ssh_config()
    if live:
        targets.append(live)

    for full in targets:
        try:
            with open(full, "rb") as handle:
                snapshot[full] = handle.read()
        except FileNotFoundError:
            snapshot[full] = None
    return snapshot


def _vault_restore(snapshot, throwaway_names=()):
    """Put the Vault back exactly as it was and purge generated artifacts."""
    # Snapshot keys are already absolute.
    for full, content in snapshot.items():
        if content is None:
            if os.path.exists(full):
                os.remove(full)
        else:
            with open(full, "wb") as handle:
                handle.write(content)

    port_registry = os.path.join(VDE_ROOT, ".cache/port-registry")

    for name in throwaway_names:
        # Reclaim the allocated port. lib/vm-common:1057 records it as
        # <name>.port and mkdirs port-<port>.lock; leaving those behind makes
        # find_available_ssh_port skip a port nothing holds, which steadily
        # exhausts the 2200-2299 language range across repeated runs.
        port_file = os.path.join(port_registry, f"{name}.port")
        allocated = None
        try:
            with open(port_file, encoding="utf-8") as handle:
                allocated = handle.read().strip()
        except (FileNotFoundError, OSError):
            pass
        if os.path.exists(port_file):
            os.remove(port_file)
        if allocated:
            lock_dir = os.path.join(port_registry, f"port-{allocated}.lock")
            if os.path.isdir(lock_dir):
                shutil.rmtree(lock_dir, ignore_errors=True)

        for rel in (
            f"env-files/{name}.env",
            f"scripts/setup/{name}-init.zsh",
            "data/vm-types.conf.bak",
        ):
            full = os.path.join(VDE_ROOT, rel)
            if os.path.exists(full):
                os.remove(full)

        # Service types land under configs/docker/services, not languages.
        for category in ("languages", "services"):
            config_dir = os.path.join(VDE_ROOT, "configs/docker", category, name)
            if os.path.isdir(config_dir):
                shutil.rmtree(config_dir, ignore_errors=True)

    # The loader caches the Vault; a stale cache would outlive the restore.
    cache = os.path.join(VDE_ROOT, ".cache/vm-types.cache")
    if os.path.exists(cache):
        os.remove(cache)


def _hub_has_serial_board():
    """True when a real USB serial board is attached to the Hub right now."""
    import glob

    return bool(glob.glob("/dev/ttyUSB*") or glob.glob("/dev/ttyACM*"))


def _scenario_tags(scenario):
    """
    Every tag that applies to a scenario, including tags inherited from the
    Feature.

    scenario.tags holds ONLY the scenario's own tags, so a gate keyed on it
    silently does nothing when the tag is declared at Feature level. That
    failure mode is invisible: the gate does not error, it just never fires.
    """
    try:
        return scenario.effective_tags
    except AttributeError:  # behave < 1.2.7
        tags = set(scenario.tags)
        feature = getattr(scenario, "feature", None)
        if feature is not None:
            tags.update(feature.tags)
        return tags


def before_scenario(context, scenario):
    """Reset state for each scenario."""
    context.output = ""
    context.exit_code = 0
    context.last_command = ""

    # Snapshot the Vault before any scenario that registers a VM type.
    if "vault-mutating" in _scenario_tags(scenario):
        context.vault_snapshot = _vault_backup()
        context.vault_throwaway = set()

    # USB passthrough hardware gate (Signet #526).
    # Scenarios tagged @hardware exercise a physically attached development
    # board. When none is present they are SKIPPED LOUDLY -- never passed --
    # per the 100% Real Tests Mandate. Simulating device state is forbidden.
    if "hardware" in _scenario_tags(scenario) and not _hub_has_serial_board():
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
    if "hardware-interactive" in _scenario_tags(scenario) and os.environ.get(
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
    if "no-board" in _scenario_tags(scenario) and _hub_has_serial_board():
        reason = (
            "SKIPPED (board attached): '%s' proves behaviour with NO serial "
            "board on the Hub, but one is currently attached. Unplug it to run "
            "this scenario." % scenario.name
        )
        print("\n[VDE-HARDWARE-GATE] " + reason)
        scenario.skip(reason)


def after_scenario(context, scenario):
    """Scenario cleanup."""
    # Restore the Vault unconditionally, so a failed registration cannot leave
    # the registry, the SSH configs or the generated artifacts altered.
    if hasattr(context, "vault_snapshot"):
        _vault_restore(
            context.vault_snapshot, getattr(context, "vault_throwaway", ())
        )
        del context.vault_snapshot

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


