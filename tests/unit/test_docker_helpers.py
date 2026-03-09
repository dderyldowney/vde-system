"""
Unit tests for docker_helpers.py — real implementation, no mocks, no skips.

Container-dependent tests start vde-python in setUpClass and stop it in
tearDownClass so every test runs against a live container.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "features" / "steps"))

from docker_helpers import (
    DockerVerificationError,
    _get_vde_root,
    _run_vde_ps,
    verify_container_running,
    verify_container_stopped,
    list_containers,
    container_exists,
    execute_in_container,
)

VDE_ROOT = Path(__file__).parent.parent.parent
VDE_PYTHON = "vde-python"


def _is_running(name: str) -> bool:
    r = subprocess.run(
        ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=10,
    )
    return name in r.stdout


def _start_container() -> None:
    subprocess.run(
        [str(VDE_ROOT / "bin" / "vde"), "start", "python"],
        cwd=str(VDE_ROOT), capture_output=True, text=True, timeout=60,
        check=True,
    )


def _stop_container() -> None:
    subprocess.run(
        [str(VDE_ROOT / "bin" / "vde"), "stop", "python"],
        cwd=str(VDE_ROOT), capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------------------
# _get_vde_root — no container needed
# ---------------------------------------------------------------------------

class TestGetVdeRoot(unittest.TestCase):
    def test_returns_string(self):
        root = _get_vde_root()
        self.assertIsInstance(root, str)
        self.assertGreater(len(root), 0)

    def test_bin_vde_exists(self):
        root = _get_vde_root()
        vde_bin = os.path.join(root, "bin", "vde")
        self.assertTrue(os.path.isfile(vde_bin), f"bin/vde not found at {vde_bin}")

    def test_env_var_override(self):
        original = os.environ.get("VDE_ROOT_DIR")
        try:
            os.environ["VDE_ROOT_DIR"] = "/tmp"
            self.assertEqual(_get_vde_root(), "/tmp")
        finally:
            if original is None:
                os.environ.pop("VDE_ROOT_DIR", None)
            else:
                os.environ["VDE_ROOT_DIR"] = original


# ---------------------------------------------------------------------------
# _run_vde_ps — no container needed (bin/vde-ps now fixed)
# ---------------------------------------------------------------------------

class TestRunVdePs(unittest.TestCase):
    def test_json_flag_returns_json(self):
        result = _run_vde_ps(["--json"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout.strip() or "[]")
        self.assertIsInstance(data, list)

    def test_quiet_flag_succeeds(self):
        result = _run_vde_ps(["-q"])
        self.assertEqual(result.returncode, 0)

    def test_nonexistent_filter_empty(self):
        result = _run_vde_ps(["--json", "--filter", "name=nonexistent-container-xyz-999"])
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        self.assertIn(output, ("", "[]"))


# ---------------------------------------------------------------------------
# Container-dependent tests — vde-python started/stopped around the class
# ---------------------------------------------------------------------------

class TestWithContainer(unittest.TestCase):
    _started_by_us = False

    @classmethod
    def setUpClass(cls):
        if not _is_running(VDE_PYTHON):
            _start_container()
            cls._started_by_us = True
        # Confirm it is up
        if not _is_running(VDE_PYTHON):
            raise RuntimeError("Failed to start vde-python for tests")

    @classmethod
    def tearDownClass(cls):
        if cls._started_by_us:
            _stop_container()

    # --- verify_container_running ---

    def test_verify_running_returns_dict(self):
        info = verify_container_running(VDE_PYTHON)
        self.assertIsInstance(info, dict)

    def test_verify_running_has_required_keys(self):
        info = verify_container_running(VDE_PYTHON)
        for key in ("ID", "Status", "Names"):
            self.assertIn(key, info)
        self.assertNotEqual(info["ID"], "")

    def test_verify_running_names_field_contains_container(self):
        info = verify_container_running(VDE_PYTHON)
        self.assertIn(VDE_PYTHON, info["Names"])

    def test_verify_running_nonexistent_raises(self):
        with self.assertRaises(DockerVerificationError):
            verify_container_running("nonexistent-container-xyz-999")

    # --- verify_container_stopped ---

    def test_verify_stopped_nonexistent_is_true(self):
        self.assertTrue(verify_container_stopped("nonexistent-container-xyz-999"))

    def test_verify_stopped_running_container_is_false(self):
        self.assertFalse(verify_container_stopped(VDE_PYTHON))

    # --- list_containers ---

    def test_list_containers_returns_list(self):
        result = list_containers()
        self.assertIsInstance(result, list)

    def test_list_containers_all_flag_returns_list(self):
        result = list_containers(all_containers=True)
        self.assertIsInstance(result, list)

    def test_list_containers_includes_python(self):
        containers = list_containers()
        self.assertTrue(
            any(VDE_PYTHON in c for c in containers),
            f"vde-python not found in {containers}",
        )

    # --- container_exists ---

    def test_container_exists_nonexistent_false(self):
        self.assertFalse(container_exists("nonexistent-container-xyz-999"))

    def test_container_exists_running_true(self):
        self.assertTrue(container_exists(VDE_PYTHON))

    # --- execute_in_container ---

    def test_execute_echo_succeeds(self):
        result = execute_in_container(VDE_PYTHON, "echo hello")
        self.assertEqual(result["returncode"], 0)
        self.assertIn("hello", result["stdout"])

    def test_execute_false_nonzero_rc(self):
        result = execute_in_container(VDE_PYTHON, "false")
        self.assertNotEqual(result["returncode"], 0)

    def test_execute_result_has_required_keys(self):
        result = execute_in_container(VDE_PYTHON, "echo test")
        for key in ("stdout", "stderr", "returncode"):
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
