"""
BDD Step definitions for common scenarios (cache, templates, docker, etc.).
"""

import os
import shlex
import subprocess
import sys
import time

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


# =============================================================================
# GIVEN steps - Cache System
# =============================================================================

@given('vm-types.conf has been modified')
def step_vm_conf_modified(context):
    """VM types config was modified."""
    context.vm_conf_modified = True


@given('VM types cache exists')
def step_cache_exists(context):
    """Cache file exists - create actual cache file for testing."""
    # VDE uses .cache directory (not .vde/cache)
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "vm-types.cache"

    # If cache doesn't exist, run VDE command to create it
    if not cache_path.exists():
        result = run_vde_command("list", timeout=30)
        context.cache_exists = (result.returncode == 0) and cache_path.exists()
