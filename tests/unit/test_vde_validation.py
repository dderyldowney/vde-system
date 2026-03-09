"""
Pytest tests for VDE validation functions.

Tests vde-core validation mechanisms via subprocess.
Uses pytest-config.json for configuration.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add tests directory to path for config loader
TESTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TESTS_DIR))

from test_config_loader import get_pytest_config

# Load test config
pytest_config = get_pytest_config()
config_data = pytest_config.load(validate=True)

# Get VDE root
VDE_ROOT = pytest_config._vde_root


@pytest.fixture
def vde_core_script():
    """Path to vde-core library."""
    return VDE_ROOT / "lib" / "vde-core"


@pytest.fixture
def test_timeout():
    """Get test timeout from config."""
    timeout_config = config_data.get("timeout", {})
    return timeout_config.get("default", 60)


class TestSchemaValidation:
    """Test JSON schema validation functions."""

    def test_validate_vm_types_json(self, vde_core_script, test_timeout):
        """Test vm-types.json validates against schema."""
        script = f"""
source "{vde_core_script}"

vde_validate_json_schema \\
    "{VDE_ROOT}/data/vm-types.json" \\
    "{VDE_ROOT}/data/vm-types.schema.json"

exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, f"Validation failed: {result.stderr}"

    def test_validate_docker_config_json(self, vde_core_script, test_timeout):
        """Test vm-docker-config.json validates against schema."""
        script = f"""
source "{vde_core_script}"

vde_validate_json_schema \\
    "{VDE_ROOT}/data/vm-docker-config.json" \\
    "{VDE_ROOT}/data/vm-docker-config.schema.json"

exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, f"Validation failed: {result.stderr}"

    def test_validate_behave_config_json(self, vde_core_script, test_timeout):
        """Test behave-config.json validates against schema."""
        script = f"""
source "{vde_core_script}"

vde_validate_json_schema \\
    "{VDE_ROOT}/tests/behave-config.json" \\
    "{VDE_ROOT}/tests/behave-config.schema.json"

exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, f"Validation failed: {result.stderr}"

    def test_validate_pytest_config_json(self, vde_core_script, test_timeout):
        """Test pytest-config.json validates against schema."""
        script = f"""
source "{vde_core_script}"

vde_validate_json_schema \\
    "{VDE_ROOT}/tests/pytest-config.json" \\
    "{VDE_ROOT}/tests/pytest-config.schema.json"

exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, f"Validation failed: {result.stderr}"

    def test_invalid_json_fails_validation(self, vde_core_script, test_timeout, tmp_path):
        """Test that invalid JSON fails validation."""
        # Create invalid JSON file
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text('{"invalid": json}')  # Invalid JSON syntax

        # Use vm-types schema for validation
        schema_file = VDE_ROOT / "data" / "vm-types.schema.json"

        script = f"""
source "{vde_core_script}"

vde_validate_json_schema "{invalid_json}" "{schema_file}"
exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode != 0, "Invalid JSON should fail validation"


class TestConfigVersioning:
    """Test config version detection and compatibility."""

    def test_get_config_version(self, vde_core_script, test_timeout):
        """Test vde_get_config_version function."""
        script = f"""
source "{vde_core_script}"

version=$(vde_get_config_version "{VDE_ROOT}/data/vm-types.json")
echo "$version"
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0
        version = result.stdout.strip()
        assert version, "Version should not be empty"
        assert "." in version, "Version should be in X.Y format"

    def test_check_schema_compatibility(self, vde_core_script, test_timeout):
        """Test schema compatibility checking."""
        script = f"""
source "{vde_core_script}"

vde_check_schema_compatibility \\
    "{VDE_ROOT}/data/vm-types.json" \\
    "{VDE_ROOT}/data/vm-types.schema.json"

exit $?
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, "Schema should be compatible"


class TestConfigParsing:
    """Test JSON config parsing and data access."""

    def test_parse_vm_types(self):
        """Test parsing vm-types.json structure."""
        vm_types_file = VDE_ROOT / "data" / "vm-types.json"

        with open(vm_types_file) as f:
            data = json.load(f)

        # Verify structure
        assert "version" in data
        assert "vms" in data
        assert "language" in data["vms"]
        assert "service" in data["vms"]

        # Verify language VMs
        language_vms = data["vms"]["language"]
        assert len(language_vms) > 0
        for vm in language_vms:
            assert "name" in vm
            assert "display" in vm
            assert "install" in vm
            assert "ssh_port" in vm  # Language VMs have ssh_port

        # Verify service VMs
        service_vms = data["vms"]["service"]
        assert len(service_vms) > 0
        for vm in service_vms:
            assert "name" in vm
            assert "display" in vm
            assert "install" in vm
            assert "service_port" in vm
            assert vm["service_port"] is not None  # Service VMs have service_port

    def test_parse_docker_config(self):
        """Test parsing vm-docker-config.json structure."""
        docker_config_file = VDE_ROOT / "data" / "vm-docker-config.json"

        with open(docker_config_file) as f:
            data = json.load(f)

        # Verify structure
        assert "version" in data
        assert "base_settings" in data
        assert "languages" in data
        assert "services" in data

        # Verify base settings
        base = data["base_settings"]
        assert "context" in base
        assert "base_dockerfile" in base

        # Verify language VMs have workspace_mount
        language = data["languages"]
        for vm_name, vm_config in language.items():
            assert "compose_file" in vm_config
            assert "container_name" in vm_config
            assert "workspace_mount" in vm_config

        # Verify service VMs have data_mount
        service = data["services"]
        for vm_name, vm_config in service.items():
            assert "compose_file" in vm_config
            assert "container_name" in vm_config
            assert "data_mount" in vm_config
            assert not vm_config["container_name"].endswith("-dev")


@pytest.mark.slow
class TestConfigIntegration:
    """Integration tests for config loading in VDE libraries."""

    def test_vm_common_loads_validated_config(self, test_timeout):
        """Test that vm-common loads and validates configs."""
        script = f"""
source "{VDE_ROOT}/lib/vm-common"

# Check that arrays are populated (config was loaded)
if [[ ${{#lang_vms[@]}} -eq 0 ]]; then
    echo "lang_vms array is empty" >&2
    exit 1
fi

if [[ ${{#service_vms[@]}} -eq 0 ]]; then
    echo "service_vms array is empty" >&2
    exit 1
fi

echo "Loaded $(( ${{#lang_vms[@]}} + ${{#service_vms[@]}} )) total VMs"
echo "Loaded ${{#lang_vms[@]}} language VMs"
echo "Loaded ${{#service_vms[@]}} service VMs"
exit 0
"""
        result = subprocess.run(
            ["zsh", "-c", script],
            capture_output=True,
            text=True,
            timeout=test_timeout,
            cwd=VDE_ROOT
        )

        assert result.returncode == 0, f"vm-common failed to load config: {result.stderr}"
        assert "total VMs" in result.stdout
