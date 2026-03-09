"""
Test framework configuration loader with schema validation.

Loads and validates schema-validated JSON configs for Behave and Pytest.
Integrates with VDE validation+regeneration mechanisms.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigValidationError(Exception):
    """Raised when config validation fails."""
    pass


class TestConfigLoader:
    """Loads and validates test framework configurations."""

    def __init__(self, config_file: Path, schema_file: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_file: Path to JSON config file
            schema_file: Optional path to JSON schema (auto-detected if not provided)
        """
        self.config_file = Path(config_file)
        self.schema_file = Path(schema_file) if schema_file else self._detect_schema()
        self._config: Optional[Dict[str, Any]] = None
        self._vde_root = self._find_vde_root()

    def _find_vde_root(self) -> Path:
        """Find VDE root directory."""
        # Try environment variable first
        vde_root = os.environ.get("VDE_ROOT_DIR")
        if vde_root and Path(vde_root).exists():
            return Path(vde_root)

        # Try relative to config file (tests/ is at root)
        tests_dir = self.config_file.parent
        vde_root = tests_dir.parent
        if vde_root.exists():
            return vde_root

        # Fallback to current directory
        return Path.cwd()

    def _detect_schema(self) -> Path:
        """Auto-detect schema file from config filename."""
        # Replace .json with .schema.json
        schema_name = self.config_file.stem + ".schema.json"
        schema_path = self.config_file.parent / schema_name

        if not schema_path.exists():
            raise ConfigValidationError(
                f"Schema file not found: {schema_path}"
            )

        return schema_path

    def _validate_with_vde_core(self) -> bool:
        """
        Validate config using VDE core validation functions.

        Returns:
            True if validation passes, False otherwise
        """
        # Build validation script using vde-core
        validation_script = f"""
source "{self._vde_root}/lib/vde-core" 2>/dev/null || exit 1

vde_validate_json_schema "{self.config_file}" "{self.schema_file}"
exit $?
"""

        try:
            result = subprocess.run(
                ["zsh", "-c", validation_script],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self._vde_root
            )

            if result.returncode == 0:
                return True

            # Validation failed - show error
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            if error_msg:
                print(f"[CONFIG] Validation error: {error_msg}", file=sys.stderr)

            return False

        except subprocess.TimeoutExpired:
            print(f"[CONFIG] Validation timeout for {self.config_file}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[CONFIG] Validation error: {e}", file=sys.stderr)
            return False

    def _validate_with_python(self) -> bool:
        """
        Fallback: validate using Python jsonschema library.

        Returns:
            True if validation passes, False otherwise
        """
        try:
            import jsonschema

            # Load schema
            with open(self.schema_file) as f:
                schema = json.load(f)

            # Load config
            with open(self.config_file) as f:
                config = json.load(f)

            # Validate
            jsonschema.validate(instance=config, schema=schema)
            return True

        except ImportError:
            print("[CONFIG] WARNING: jsonschema not installed, skipping validation",
                  file=sys.stderr)
            return True  # Allow tests to run without validation
        except jsonschema.ValidationError as e:
            print(f"[CONFIG] Schema validation failed: {e.message}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[CONFIG] Validation error: {e}", file=sys.stderr)
            return False

    def load(self, validate: bool = True) -> Dict[str, Any]:
        """
        Load and optionally validate configuration.

        Args:
            validate: Whether to validate against schema (default: True)

        Returns:
            Configuration dictionary

        Raises:
            ConfigValidationError: If validation fails
        """
        if self._config is not None:
            return self._config

        # Check config file exists
        if not self.config_file.exists():
            raise ConfigValidationError(
                f"Config file not found: {self.config_file}"
            )

        # Load JSON
        try:
            with open(self.config_file) as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(
                f"Invalid JSON in {self.config_file}: {e}"
            )

        # Validate if requested
        if validate and self.schema_file.exists():
            # Try VDE core validation first
            vde_validation = self._validate_with_vde_core()

            if not vde_validation:
                # Try Python validation as fallback
                python_validation = self._validate_with_python()

                if not python_validation:
                    raise ConfigValidationError(
                        f"Config validation failed for {self.config_file}"
                    )

        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        if self._config is None:
            self.load()
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key (dict-like access)."""
        if self._config is None:
            self.load()
        return self._config[key]


# Singleton instances
_behave_config: Optional[TestConfigLoader] = None
_pytest_config: Optional[TestConfigLoader] = None


def get_behave_config() -> TestConfigLoader:
    """Get Behave configuration (singleton)."""
    global _behave_config

    if _behave_config is None:
        # Find tests directory
        tests_dir = Path(__file__).parent
        config_file = tests_dir / "behave-config.json"
        schema_file = tests_dir / "behave-config.schema.json"

        _behave_config = TestConfigLoader(config_file, schema_file)

        # Load and validate on first access
        try:
            _behave_config.load(validate=True)
            print(f"[CONFIG] ✓ Loaded behave-config.json (version {_behave_config.get('version')})")
        except ConfigValidationError as e:
            print(f"[CONFIG] ✗ Failed to load behave config: {e}", file=sys.stderr)
            # Allow tests to continue even if validation fails

    return _behave_config


def get_pytest_config() -> TestConfigLoader:
    """Get Pytest configuration (singleton)."""
    global _pytest_config

    if _pytest_config is None:
        # Find tests directory
        tests_dir = Path(__file__).parent
        config_file = tests_dir / "pytest-config.json"
        schema_file = tests_dir / "pytest-config.schema.json"

        _pytest_config = TestConfigLoader(config_file, schema_file)

        # Load and validate on first access
        try:
            _pytest_config.load(validate=True)
            print(f"[CONFIG] ✓ Loaded pytest-config.json (version {_pytest_config.get('version')})")
        except ConfigValidationError as e:
            print(f"[CONFIG] ✗ Failed to load pytest config: {e}", file=sys.stderr)
            # Allow tests to continue even if validation fails

    return _pytest_config
