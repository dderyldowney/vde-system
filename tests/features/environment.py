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
