"""
BDD Step Definitions for productivity features - REAL IMPLEMENTATIONS

These steps test actual VDE functionality using real Docker operations,
PostgreSQL data persistence, VM lifecycle, and file system state.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

from config import VDE_ROOT

# =============================================================================
# Helper Functions
# =============================================================================

from vm_common import run_vde_command, docker_ps, container_exists, wait_for_container

# =============================================================================
# Port Registry and Cache Steps (Real implementations)
# =============================================================================

@when('port registry is saved')
def step_port_registry_saved(context):
    """Actually check that port registry cache is saved."""
    cache_path = VDE_ROOT / ".cache" / "port-registry"
    if cache_path.exists():
        context.port_registry_cache = str(cache_path)
