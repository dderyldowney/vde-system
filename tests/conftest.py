"""
Pytest configuration using schema-validated JSON config.

Loads pytest-config.json and applies settings dynamically.
"""

import sys
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from test_config_loader import get_pytest_config


def pytest_configure(config):
    """
    Configure pytest using schema-validated JSON config.

    Called before test collection begins.
    """
    # Load schema-validated config
    try:
        pytest_config = get_pytest_config()
        config_data = pytest_config.load(validate=True)

        # Register custom markers from config
        markers = config_data.get("pytest", {}).get("markers", {})
        for marker_name, marker_desc in markers.items():
            config.addinivalue_line("markers", f"{marker_name}: {marker_desc}")

        # Store config in pytest's config object for access in tests
        config._vde_pytest_config = config_data

    except Exception as e:
        print(f"[PYTEST] Warning: Failed to load pytest-config.json: {e}")
        # Continue anyway - pytest will use default settings


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection based on config.

    Called after collection has been performed.
    """
    # Get VDE pytest config if available
    config_data = getattr(config, '_vde_pytest_config', None)
    if not config_data:
        return

    # Apply any collection modifications from config
    # (Currently none needed, but hook is available for future use)
    pass


def pytest_addoption(parser):
    """
    Add custom command-line options from config.
    """
    # Add VDE-specific options
    parser.addoption(
        "--vde-verbose",
        action="store_true",
        default=False,
        help="Enable VDE verbose output"
    )
    parser.addoption(
        "--vde-validate-config",
        action="store_true",
        default=True,
        help="Validate pytest-config.json before running tests"
    )
