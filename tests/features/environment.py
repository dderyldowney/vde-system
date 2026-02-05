"""
BDD Hooks for VDE test scenarios.

Hooks are special functions that run at specific points during test execution.
This file is automatically discovered by behave.
"""

import os
import subprocess
import sys

# Import shared configuration
# environment.py is in tests/features/, config.py is in tests/features/steps/
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    result = subprocess.run(
        f"cd {VDE_ROOT} && {command}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def reset_cache_to_valid_state():
    """
    Reset cache files to a valid state by regenerating them.

    This ensures each cache scenario starts with a clean, valid cache
    rather than inheriting corrupted state from previous scenarios.
    """
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Remove any potentially corrupted cache files
    cache_file = cache_dir / "vm-types.cache"
    port_registry = cache_dir / "port-registry"

    # Delete if they contain invalid markers
    for cache_path in [cache_file, port_registry]:
        if cache_path.exists():
            try:
                content = cache_path.read_text()
                if "INVALID" in content or "CORRUPTED" in content:
                    cache_path.unlink()
            except Exception:
                # If we can't read it, delete it
                cache_path.unlink()

    # Regenerate valid cache by running list-vms
    result = run_vde_command("./scripts/list-vms", timeout=30)
    return result.returncode == 0


# =============================================================================
# SCENARIO HOOKS
# =============================================================================

def before_scenario(context, scenario):
    """
    Hook that runs before each scenario.

    This hook resets the cache to a valid state for cache-system scenarios
    to prevent test pollution where scenarios that create invalid cache state
    would cause subsequent scenarios to fail.

    However, we skip this reset for scenarios that specifically test cache
    behavior (expiry, invalid cache, etc.) since those scenarios set up
    specific cache states as part of their test.
    """
    # Only reset cache for cache-system feature scenarios
    if scenario.feature.name == "Cache System":
        # Skip reset for scenarios that set up specific cache states
        scenario_steps = [step.name for step in scenario.steps]

        # Don't reset if the scenario tests invalid cache regeneration
        if "cache file exists with invalid format" in scenario_steps:
            return

        # Reset for all other scenarios to prevent pollution
        reset_cache_to_valid_state()


def after_scenario(context, scenario):
    """
    Hook that runs after each scenario.

    This hook cleans up any temporary files created during testing,
    such as invalid compose files used for error handling tests,
    and removes any test-created containers (labeled with vde.test=true).
    """
    # Clean up invalid compose test directory if it was created
    import shutil
    invalid_compose_dir = VDE_ROOT / "configs" / "docker" / "invalid-test"
    if invalid_compose_dir.exists():
        try:
            shutil.rmtree(invalid_compose_dir)
        except Exception:
            pass  # Best effort cleanup

    # Clean up test-created containers (labeled with vde.test=true)
    # This ensures tests don't leave orphaned containers and don't affect user's VMs
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            test_containers = [c for c in result.stdout.strip().split('\n') if c]
            for container in test_containers:
                # Force remove the test container
                subprocess.run(
                    ["docker", "rm", "-f", container],
                    capture_output=True,
                    timeout=10
                )
    except Exception:
        pass  # Docker may not be available, that's OK


def after_feature(context, feature):
    """
    Hook that runs after each feature.

    For docker-operations feature, stop the python and postgres VMs that were
    started in the Background section to clean up after tests.
    """
    if feature.name == "Docker Operations":
        # Stop python VM
        try:
            subprocess.run(
                ["docker", "rm", "-f", "python-dev"],
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass

        # Stop postgres VM
        try:
            subprocess.run(
                ["docker", "rm", "-f", "postgres"],
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass
