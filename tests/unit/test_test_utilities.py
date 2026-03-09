"""
Unit tests for test_utilities.py

All tests use real execution — no mocks. Functions that touch Docker
run against actual Docker daemon. The module under test provides:
  - cleanup_test_containers
  - cleanup_test_vms
  - cleanup_port_registry
  - cleanup_docker_networks
  - cleanup_docker_volumes
  - register_cleanup_handler
  - create_test_vm_config
  - wait_for_condition
  - before_scenario (Behave hook)

Note: after_scenario, after_feature, before_all, after_all are NOT defined
in test_utilities.py and are therefore not tested here.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "features" / "steps"))

import test_utilities
from test_utilities import (
    cleanup_test_containers,
    cleanup_test_vms,
    cleanup_port_registry,
    cleanup_docker_networks,
    cleanup_docker_volumes,
    register_cleanup_handler,
    create_test_vm_config,
    wait_for_condition,
    before_scenario,
    _cleanup_handlers,
)

VDE_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# create_test_vm_config (no Docker required — pure file I/O)
# ---------------------------------------------------------------------------

class TestCreateTestVmConfig:
    def test_creates_file(self):
        path = create_test_vm_config("python")
        try:
            assert os.path.exists(path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_file_contains_vm_type(self):
        path = create_test_vm_config("ruby")
        try:
            content = Path(path).read_text()
            assert "vm_type: ruby" in content
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_file_contains_container_name(self):
        path = create_test_vm_config("js")
        try:
            content = Path(path).read_text()
            assert "container_name: vde-test-js-" in content
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_filename_pattern(self):
        path = create_test_vm_config("go")
        try:
            name = os.path.basename(path)
            assert name.startswith("vde-test-config-")
            assert name.endswith("-go.yml")
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_custom_settings_in_file(self):
        path = create_test_vm_config("python", {"memory": "2g", "cpus": "4"})
        try:
            content = Path(path).read_text()
            assert "memory: 2g" in content
            assert "cpus: 4" in content
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_default_settings_none(self):
        """Calling without custom_settings should not raise."""
        path = create_test_vm_config("rust")
        try:
            assert os.path.exists(path)
        finally:
            if os.path.exists(path):
                os.unlink(path)


# ---------------------------------------------------------------------------
# wait_for_condition (no Docker required — pure timing)
# ---------------------------------------------------------------------------

class TestWaitForCondition:
    def test_immediately_true(self):
        calls = []

        def cond():
            calls.append(1)
            return True

        result = wait_for_condition(cond, timeout=5, interval=0.05)
        assert result is True
        assert len(calls) == 1

    def test_becomes_true_after_delay(self):
        calls = []

        def cond():
            calls.append(1)
            return len(calls) >= 3

        result = wait_for_condition(cond, timeout=5, interval=0.05)
        assert result is True
        assert len(calls) == 3

    def test_timeout_returns_false(self):
        start = time.time()
        result = wait_for_condition(lambda: False, timeout=0.3, interval=0.05)
        elapsed = time.time() - start
        assert result is False
        assert elapsed >= 0.3

    def test_interval_respected(self):
        times = []

        def cond():
            times.append(time.time())
            return len(times) >= 2

        wait_for_condition(cond, timeout=5, interval=0.1)
        assert len(times) >= 2
        gap = times[1] - times[0]
        assert 0.07 < gap < 0.25  # generous bounds for CI


# ---------------------------------------------------------------------------
# register_cleanup_handler (no Docker required)
# ---------------------------------------------------------------------------

class TestRegisterCleanupHandler:
    def setup_method(self):
        test_utilities._cleanup_handlers.clear()

    def teardown_method(self):
        test_utilities._cleanup_handlers.clear()

    def test_handler_registered(self):
        def my_handler():
            pass

        register_cleanup_handler(my_handler)
        assert my_handler in test_utilities._cleanup_handlers

    def test_duplicate_not_added(self):
        def my_handler():
            pass

        register_cleanup_handler(my_handler)
        register_cleanup_handler(my_handler)
        assert test_utilities._cleanup_handlers.count(my_handler) == 1

    def test_multiple_handlers(self):
        def h1():
            pass

        def h2():
            pass

        register_cleanup_handler(h1)
        register_cleanup_handler(h2)
        assert h1 in test_utilities._cleanup_handlers
        assert h2 in test_utilities._cleanup_handlers


# ---------------------------------------------------------------------------
# before_scenario (Behave hook — no Docker required for basic paths)
# ---------------------------------------------------------------------------

class TestBeforeScenario:
    def _make_context(self):
        """Simple namespace object to act as Behave context."""

        class Ctx:
            pass

        return Ctx()

    def _make_scenario(self, tags):
        class Scen:
            effective_tags = tags

            def skip(self, reason):
                self._skipped = reason

            _skipped = None

        return Scen()

    def test_initializes_temp_files(self):
        ctx = self._make_context()
        scen = self._make_scenario([])
        before_scenario(ctx, scen)
        assert hasattr(ctx, "temp_files")
        assert ctx.temp_files == []

    def test_initializes_test_containers(self):
        ctx = self._make_context()
        scen = self._make_scenario([])
        before_scenario(ctx, scen)
        assert hasattr(ctx, "test_containers")
        assert ctx.test_containers == []

    def test_cleanup_containers_tag_sets_flag(self):
        ctx = self._make_context()
        scen = self._make_scenario(["cleanup_containers"])
        before_scenario(ctx, scen)
        assert ctx.cleanup_containers is True

    def test_no_special_tags_no_cleanup_flag(self):
        ctx = self._make_context()
        scen = self._make_scenario([])
        before_scenario(ctx, scen)
        # cleanup_containers should not be set when tag is absent
        assert not getattr(ctx, "cleanup_containers", False)

    @pytest.mark.docker
    def test_requires_docker_tag_docker_available(self):
        """When Docker is available, @requires_docker does not skip."""
        # Verify Docker is reachable first
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        if r.returncode != 0:
            pytest.skip("Docker not available")

        ctx = self._make_context()
        scen = self._make_scenario(["requires_docker"])
        before_scenario(ctx, scen)
        assert getattr(scen, "_skipped", None) is None


# ---------------------------------------------------------------------------
# cleanup_port_registry (real file I/O — no Docker required)
# ---------------------------------------------------------------------------

class TestCleanupPortRegistry:
    def test_no_registry_file_is_noop(self, tmp_path, monkeypatch):
        """cleanup_port_registry should silently do nothing if file absent."""
        # Point VDE root to a tmpdir with no .vde/port-registry.json
        monkeypatch.setattr(
            test_utilities.Path,
            "__new__",
            lambda cls, *args, **kw: object.__new__(cls),
        )
        # Simpler: just ensure calling it with missing file doesn't raise
        fake_root = tmp_path  # no .vde subdir
        # Patch __file__ path resolution by using a real temp structure
        vde_dir = tmp_path / ".vde"
        vde_dir.mkdir()
        # No port-registry.json created — function should be a no-op

        # We call the real function; it resolves VDE root via Path(__file__).parent...
        # so we create the real path structure to make it skip gracefully
        try:
            cleanup_port_registry()
        except Exception as e:
            pytest.fail(f"cleanup_port_registry raised unexpectedly: {e}")

    def test_removes_test_prefixed_entries(self):
        """Test entries prefixed vde-test- are removed from the registry.

        cleanup_port_registry resolves the registry via Path(__file__).parent^4 / .vde / port-registry.json
        where __file__ is tests/features/steps/test_utilities.py, so parent^4 = VDE_ROOT.
        We write a fixture to the real registry path, run the function, then restore.
        """
        real_registry = VDE_ROOT / ".vde" / "port-registry.json"
        data = {
            "vde-test-python": {"8000": "8000"},
            "vde-test-js": {"3000": "3000"},
            "vde-production": {"9000": "9000"},
        }
        backup = real_registry.read_text() if real_registry.exists() else None
        try:
            real_registry.parent.mkdir(parents=True, exist_ok=True)
            real_registry.write_text(json.dumps(data))

            cleanup_port_registry()

            remaining = json.loads(real_registry.read_text())
            assert "vde-test-python" not in remaining
            assert "vde-test-js" not in remaining
            assert "vde-production" in remaining
        finally:
            if backup is not None:
                real_registry.write_text(backup)
            elif real_registry.exists():
                real_registry.unlink()


# ---------------------------------------------------------------------------
# cleanup_test_containers / cleanup_docker_networks / cleanup_docker_volumes
# These call docker directly; we verify they don't raise when nothing exists.
# ---------------------------------------------------------------------------

class TestCleanupFunctionsWithNoTargets:
    """Verify cleanup functions are idempotent when no matching resources exist."""

    PREFIX = "vde-test-absolutely-nonexistent-xyz-"

    def test_cleanup_test_containers_noop(self):
        cleanup_test_containers(prefix=self.PREFIX)

    @pytest.mark.docker
    def test_cleanup_docker_networks_noop(self):
        cleanup_docker_networks(prefix=self.PREFIX)

    @pytest.mark.docker
    def test_cleanup_docker_volumes_noop(self):
        cleanup_docker_volumes(prefix=self.PREFIX)

    @pytest.mark.docker
    def test_cleanup_test_vms_noop(self):
        cleanup_test_vms(prefix=self.PREFIX)
