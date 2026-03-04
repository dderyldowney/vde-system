"""
Unit Test Environment - Fast, no Docker required.

This environment is used for @unit tests (parser, library functions).
No Docker cleanup or VM setup - pure unit testing.
"""

import os
import sys
from pathlib import Path

# Add tests directory to path
tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

from tests.features.steps.config import VDE_ROOT


def before_all(context):
    """Minimal setup for unit tests."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["VDE_TEST_MODE"] = "1"

    # Invalidate cache for fresh load
    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()


def before_feature(context, feature):
    """No special setup for unit tests."""
    pass


def before_scenario(context, scenario):
    """Reset context for each scenario."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0


def after_all(context):
    """No teardown needed for unit tests."""
    pass
