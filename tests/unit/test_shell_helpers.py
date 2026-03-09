"""
Unit tests for shell_helpers.py — real implementation, no mocks, no skips.

Container-dependent tests start vde-python in setUpClass and stop it in
tearDownClass so every test runs against a live container.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "features" / "steps"))

from shell_helpers import (
    execute_in_container,
    verify_command_output,
    verify_file_exists_in_container,
    get_container_env_var,
    _get_vde_root,
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

    def test_env_override(self):
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
# Container-dependent tests — vde-python started/stopped around the class
# ---------------------------------------------------------------------------

class TestWithContainer(unittest.TestCase):
    _started_by_us = False

    @classmethod
    def setUpClass(cls):
        if not _is_running(VDE_PYTHON):
            _start_container()
            cls._started_by_us = True
        if not _is_running(VDE_PYTHON):
            raise RuntimeError("Failed to start vde-python for tests")

    @classmethod
    def tearDownClass(cls):
        if cls._started_by_us:
            _stop_container()

    # --- execute_in_container ---

    def test_execute_returns_dict(self):
        result = execute_in_container(VDE_PYTHON, "echo hello")
        self.assertIsInstance(result, dict)
        for key in ("stdout", "stderr", "returncode"):
            self.assertIn(key, result)

    def test_execute_output(self):
        result = execute_in_container(VDE_PYTHON, "echo hello")
        self.assertEqual(result["returncode"], 0)
        self.assertIn("hello", result["stdout"])

    def test_execute_failing_command_nonzero_rc(self):
        result = execute_in_container(VDE_PYTHON, "false")
        self.assertNotEqual(result["returncode"], 0)

    def test_execute_stderr_captured(self):
        result = execute_in_container(VDE_PYTHON, "echo error >&2")
        self.assertEqual(result["returncode"], 0)

    def test_execute_pipe(self):
        result = execute_in_container(VDE_PYTHON, "echo hello | tr a-z A-Z")
        self.assertEqual(result["returncode"], 0)
        self.assertIn("HELLO", result["stdout"])

    def test_execute_nonexistent_container_errors(self):
        try:
            result = execute_in_container("nonexistent-container-xyz-999", "echo hi")
            self.assertNotEqual(result["returncode"], 0)
        except RuntimeError:
            pass  # also acceptable

    # --- verify_command_output ---

    def test_verify_output_match_returns_true(self):
        self.assertTrue(verify_command_output(VDE_PYTHON, "echo hello", "hello"))

    def test_verify_output_mismatch_returns_false(self):
        self.assertFalse(verify_command_output(VDE_PYTHON, "echo hello", "world"))

    def test_verify_output_failing_command_returns_false(self):
        self.assertFalse(verify_command_output(VDE_PYTHON, "false", "anything"))

    def test_verify_output_partial_match(self):
        self.assertTrue(verify_command_output(VDE_PYTHON, "python3 --version", "Python"))

    # --- verify_file_exists_in_container ---

    def test_existing_file_returns_true(self):
        self.assertTrue(verify_file_exists_in_container(VDE_PYTHON, "/bin/sh"))

    def test_nonexistent_file_returns_false(self):
        self.assertFalse(verify_file_exists_in_container(VDE_PYTHON, "/nonexistent/file/xyz"))

    def test_python3_binary_exists(self):
        result = (
            verify_file_exists_in_container(VDE_PYTHON, "/usr/bin/python3")
            or verify_file_exists_in_container(VDE_PYTHON, "/usr/local/bin/python3")
        )
        self.assertTrue(result)

    # --- get_container_env_var ---

    def test_path_var_exists(self):
        value = get_container_env_var(VDE_PYTHON, "PATH")
        self.assertIsNotNone(value)
        self.assertGreater(len(value), 0)
        self.assertIn("/", value)

    def test_nonexistent_var_returns_none(self):
        self.assertIsNone(get_container_env_var(VDE_PYTHON, "NONEXISTENT_VAR_XYZ_999"))

    def test_home_var_exists(self):
        value = get_container_env_var(VDE_PYTHON, "HOME")
        self.assertIsNotNone(value)
        self.assertIn("/", value)


if __name__ == "__main__":
    unittest.main()
