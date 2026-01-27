"""
Unit tests for shell_helpers module.

These tests use mocks to simulate subprocess responses, allowing us to test
the helper function logic without requiring actual Docker containers.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from tests.features.steps.shell_helpers import (
    execute_in_container,
    verify_command_output,
    verify_file_exists_in_container,
    get_container_env_var
)


class TestExecuteInContainer:
    """Tests for execute_in_container function."""
    
    @patch('tests.features.steps.shell_helpers.subprocess.run')
    def test_successful_command_execution(self, mock_run):
        """Test successful command execution returns correct data structure."""
        # Mock successful command execution
        mock_run.return_value = MagicMock(
            stdout="Python 3.11.0\n",
            stderr="",
            returncode=0
        )
        
        result = execute_in_container("vde-python", "python --version")
        
        assert result['stdout'] == "Python 3.11.0\n"
        assert result['stderr'] == ""
        assert result['returncode'] == 0
        
        # Verify docker exec was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0:3] == ["docker", "exec", "vde-python"]
        assert "python --version" in call_args
    
    @patch('tests.features.steps.shell_helpers.subprocess.run')
    def test_command_with_error_output(self, mock_run):
        """Test command that produces stderr output."""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="command not found: invalid\n",
            returncode=127
        )
        
        result = execute_in_container("vde-python", "invalid")
        
        assert result['stdout'] == ""
        assert "command not found" in result['stderr']
        assert result['returncode'] == 127
    
    @patch('tests.features.steps.shell_helpers.subprocess.run')
    def test_command_timeout(self, mock_run):
        """Test command timeout raises TimeoutExpired."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["docker", "exec", "vde-python", "sh", "-c", "sleep 100"],
            timeout=5
        )
        
        with pytest.raises(subprocess.TimeoutExpired):
            execute_in_container("vde-python", "sleep 100", timeout=5)
    
    @patch('tests.features.steps.shell_helpers.subprocess.run')
    def test_docker_exec_failure(self, mock_run):
        """Test docker exec failure raises RuntimeError."""
        mock_run.side_effect = Exception("Docker daemon not running")
        
        with pytest.raises(RuntimeError) as exc_info:
            execute_in_container("vde-python", "echo test")
        
        assert "Failed to execute command" in str(exc_info.value)
        assert "vde-python" in str(exc_info.value)
    
    @patch('tests.features.steps.shell_helpers.subprocess.run')
    def test_custom_timeout(self, mock_run):
        """Test custom timeout is passed to subprocess.run."""
        mock_run.return_value = MagicMock(
            stdout="output",
            stderr="",
            returncode=0
        )
        
        execute_in_container("vde-python", "echo test", timeout=60)
        
        # Verify timeout parameter was passed
        assert mock_run.call_args[1]['timeout'] == 60


class TestVerifyCommandOutput:
    """Tests for verify_command_output function."""
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_output_contains_expected_string(self, mock_execute):
        """Test returns True when output contains expected string."""
        mock_execute.return_value = {
            'stdout': "Python 3.11.0\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = verify_command_output(
            "vde-python",
            "python --version",
            "Python 3"
        )
        
        assert result is True
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_output_missing_expected_string(self, mock_execute):
        """Test returns False when output doesn't contain expected string."""
        mock_execute.return_value = {
            'stdout': "Python 3.11.0\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = verify_command_output(
            "vde-python",
            "python --version",
            "Python 2"
        )
        
        assert result is False
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_command_failure_returns_false(self, mock_execute):
        """Test returns False when command fails."""
        mock_execute.return_value = {
            'stdout': "",
            'stderr': "command not found\n",
            'returncode': 127
        }
        
        result = verify_command_output(
            "vde-python",
            "invalid_command",
            "expected"
        )
        
        assert result is False
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_exact_match(self, mock_execute):
        """Test exact string matching works."""
        mock_execute.return_value = {
            'stdout': "exact output",
            'stderr': "",
            'returncode': 0
        }
        
        result = verify_command_output(
            "vde-python",
            "echo 'exact output'",
            "exact output"
        )
        
        assert result is True


class TestVerifyFileExistsInContainer:
    """Tests for verify_file_exists_in_container function."""
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_file_exists(self, mock_execute):
        """Test returns True when file exists (test -f returns 0)."""
        mock_execute.return_value = {
            'stdout': "",
            'stderr': "",
            'returncode': 0
        }
        
        result = verify_file_exists_in_container(
            "vde-python",
            "/usr/bin/python3"
        )
        
        assert result is True
        
        # Verify test -f was called
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0]
        assert "test -f /usr/bin/python3" in call_args[1]
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_file_does_not_exist(self, mock_execute):
        """Test returns False when file doesn't exist (test -f returns 1)."""
        mock_execute.return_value = {
            'stdout': "",
            'stderr': "",
            'returncode': 1
        }
        
        result = verify_file_exists_in_container(
            "vde-python",
            "/nonexistent/file"
        )
        
        assert result is False
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_file_path_with_spaces(self, mock_execute):
        """Test handles file paths with spaces."""
        mock_execute.return_value = {
            'stdout': "",
            'stderr': "",
            'returncode': 0
        }
        
        result = verify_file_exists_in_container(
            "vde-python",
            "/path/with spaces/file.txt"
        )
        
        assert result is True
        
        # Verify the path was passed correctly
        call_args = mock_execute.call_args[0]
        assert "/path/with spaces/file.txt" in call_args[1]


class TestGetContainerEnvVar:
    """Tests for get_container_env_var function."""
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_env_var_exists(self, mock_execute):
        """Test returns env var value when it exists."""
        mock_execute.return_value = {
            'stdout': "/usr/local/bin:/usr/bin:/bin\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = get_container_env_var("vde-python", "PATH")
        
        assert result == "/usr/local/bin:/usr/bin:/bin"
        
        # Verify printenv was called
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0]
        assert "printenv PATH" in call_args[1]
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_env_var_does_not_exist(self, mock_execute):
        """Test returns None when env var doesn't exist."""
        mock_execute.return_value = {
            'stdout': "",
            'stderr': "",
            'returncode': 1
        }
        
        result = get_container_env_var("vde-python", "NONEXISTENT_VAR")
        
        assert result is None
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_env_var_empty_string(self, mock_execute):
        """Test handles empty string env var value."""
        mock_execute.return_value = {
            'stdout': "\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = get_container_env_var("vde-python", "EMPTY_VAR")
        
        assert result == ""
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_env_var_multiline_value(self, mock_execute):
        """Test handles multiline env var values."""
        mock_execute.return_value = {
            'stdout': "line1\nline2\nline3\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = get_container_env_var("vde-python", "MULTILINE_VAR")
        
        # Should strip only trailing newline, preserving internal newlines
        assert result == "line1\nline2\nline3"
    
    @patch('tests.features.steps.shell_helpers.execute_in_container')
    def test_env_var_with_special_characters(self, mock_execute):
        """Test handles env var values with special characters."""
        mock_execute.return_value = {
            'stdout': "value=with:special/chars\n",
            'stderr': "",
            'returncode': 0
        }
        
        result = get_container_env_var("vde-python", "SPECIAL_VAR")
        
        assert result == "value=with:special/chars"
