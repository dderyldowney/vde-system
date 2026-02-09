#!/usr/bin/env python3
"""
Test schema-validated config integration for test frameworks.

Verifies that:
1. Behave config loads and validates
2. Pytest config loads and validates
3. Validation+regeneration mechanisms work
"""

import sys
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

from test_config_loader import get_behave_config, get_pytest_config, ConfigValidationError


def test_behave_config():
    """Test behave config loading and validation."""
    print("\n" + "="*60)
    print("Testing Behave Config")
    print("="*60)

    try:
        # Load config
        config = get_behave_config()
        data = config.load(validate=True)

        # Verify required fields
        assert "version" in data, "Missing 'version' field"
        assert "behave" in data, "Missing 'behave' section"
        assert "logging" in data, "Missing 'logging' section"
        assert "paths" in data, "Missing 'paths' section"

        # Verify behave settings
        behave = data["behave"]
        assert "format" in behave, "Missing 'behave.format'"
        assert behave["format"] in ["pretty", "plain", "json", "progress"], \
            f"Invalid format: {behave['format']}"

        # Verify logging settings
        logging = data["logging"]
        assert "level" in logging, "Missing 'logging.level'"
        assert logging["level"] in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], \
            f"Invalid log level: {logging['level']}"

        # Verify paths
        paths = data["paths"]
        assert "features" in paths, "Missing 'paths.features'"
        assert "steps" in paths, "Missing 'paths.steps'"

        print(f"✓ Behave config loaded successfully (version {data['version']})")
        print(f"  Format: {behave['format']}")
        print(f"  Logging: {logging['level']}")
        print(f"  Features: {paths['features']}")
        print(f"  Steps: {paths['steps']}")

        return True

    except ConfigValidationError as e:
        print(f"✗ Behave config validation failed: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Behave config assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Behave config error: {e}")
        return False


def test_pytest_config():
    """Test pytest config loading and validation."""
    print("\n" + "="*60)
    print("Testing Pytest Config")
    print("="*60)

    try:
        # Load config
        config = get_pytest_config()
        data = config.load(validate=True)

        # Verify required fields
        assert "version" in data, "Missing 'version' field"
        assert "pytest" in data, "Missing 'pytest' section"
        assert "paths" in data, "Missing 'paths' section"

        # Verify pytest settings
        pytest_conf = data["pytest"]
        assert "testpaths" in pytest_conf, "Missing 'pytest.testpaths'"
        assert len(pytest_conf["testpaths"]) > 0, "Empty testpaths"

        # Verify markers
        if "markers" in pytest_conf:
            markers = pytest_conf["markers"]
            print(f"  Markers: {', '.join(markers.keys())}")

        # Verify paths
        paths = data["paths"]
        assert "test_dir" in paths, "Missing 'paths.test_dir'"

        # Verify coverage if enabled
        if "coverage" in data and data["coverage"].get("enabled"):
            coverage = data["coverage"]
            print(f"  Coverage: enabled")
            if "source" in coverage:
                print(f"  Coverage source: {coverage['source']}")

        print(f"✓ Pytest config loaded successfully (version {data['version']})")
        print(f"  Test paths: {pytest_conf['testpaths']}")
        print(f"  Test dir: {paths['test_dir']}")

        return True

    except ConfigValidationError as e:
        print(f"✗ Pytest config validation failed: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Pytest config assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Pytest config error: {e}")
        return False


def test_validation_mechanisms():
    """Test validation mechanisms are working."""
    print("\n" + "="*60)
    print("Testing Validation Mechanisms")
    print("="*60)

    try:
        # Test behave validation
        behave_config = get_behave_config()
        assert behave_config.schema_file.exists(), "Behave schema file not found"
        print(f"✓ Behave schema exists: {behave_config.schema_file}")

        # Test pytest validation
        pytest_config = get_pytest_config()
        assert pytest_config.schema_file.exists(), "Pytest schema file not found"
        print(f"✓ Pytest schema exists: {pytest_config.schema_file}")

        # Verify VDE root detection
        vde_root = behave_config._vde_root
        assert vde_root.exists(), f"VDE root not found: {vde_root}"
        print(f"✓ VDE root detected: {vde_root}")

        # Check for vde-core library
        vde_core = vde_root / "scripts" / "lib" / "vde-core"
        if vde_core.exists():
            print(f"✓ vde-core library available: {vde_core}")
        else:
            print(f"⚠ vde-core library not found (validation will use Python fallback)")

        return True

    except AssertionError as e:
        print(f"✗ Validation mechanism check failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking validation mechanisms: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("VDE Test Framework Config Integration Tests")
    print("="*60)

    results = []
    results.append(("Behave Config", test_behave_config()))
    results.append(("Pytest Config", test_pytest_config()))
    results.append(("Validation Mechanisms", test_validation_mechanisms()))

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
