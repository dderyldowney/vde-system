"""
Shared configuration for VDE BDD tests.

This module provides a single source of truth for test configuration.
Import from here rather than duplicating path calculations.
"""

import os
import sys
from pathlib import Path

# Add the tests directory to path so we can import from steps
# This is needed because behave's exec_file doesn't set up proper module paths

# Calculate VDE_ROOT once, correctly
# This file is at: tests/features/steps/config.py
# Project root is 4 levels up
_VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

def get_vde_root() -> Path:
    """Get the VDE project root directory."""
    return _VDE_ROOT

# Export for backwards compatibility
VDE_ROOT = get_vde_root()
