"""
Shell command execution helpers for VDE container testing.

This module provides utilities for executing shell commands within VDE containers
and verifying their outputs. All functions perform REAL command execution using
subprocess.run() with actual VDE commands via the vde CLI.
"""

import os
import subprocess
from typing import Dict, Any, Optional, List


def _get_vde_root() -> str:
    """Get the VDE root directory."""
    return os.environ.get("VDE_ROOT_DIR", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


def _run_vde_command(args: List[str], timeout: int = 30, check: bool = False) -> subprocess.CompletedProcess:
    """Run a vde command and return the result.
    
    Args:
        args: Arguments to pass to vde command
        timeout: Command timeout in seconds
        check: Whether to raise on non-zero exit
        
    Returns:
        CompletedProcess result
    """
    vde_root = _get_vde_root()
    vde_script = os.path.join(vde_root, "bin", "vde")
    
    cmd = [vde_script] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
        cwd=vde_root
    )


def execute_in_container(
    container_name: str,
    command: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute a shell command inside a VDE container using vde exec.
    
    Args:
        container_name: Name of the container (with or without vde- prefix)
        command: Shell command to execute
        timeout: Command timeout in seconds (default: 30)
    
    Returns:
        Dict containing:
            - stdout: Command standard output (str)
            - stderr: Command standard error (str)
            - returncode: Command exit code (int)
    
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        RuntimeError: If vde exec command fails to start
    
    Example:
        result = execute_in_container("python", "python --version")
        if result['returncode'] == 0:
            print(f"Python version: {result['stdout']}")
    """
    try:
        result = _run_vde_command(
            ["exec", container_name, "sh", "-c", command],
            timeout=timeout,
            check=False
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(
            cmd=["vde", "exec", container_name, "sh", "-c", command],
            timeout=timeout,
            output=e.output,
            stderr=e.stderr
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to execute command in container '{container_name}': {e}"
        )


def verify_command_output(
    container_name: str,
    command: str,
    expected_output: str,
    timeout: int = 30
) -> bool:
    """
    Execute a command in a container and verify its output contains expected string.
    
    Args:
        container_name: Name of the container (with or without vde- prefix)
        command: Shell command to execute
        expected_output: String that should be present in stdout
        timeout: Command timeout in seconds (default: 30)
    
    Returns:
        True if expected_output is found in stdout, False otherwise
    
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        RuntimeError: If vde exec command fails to start
    
    Example:
        if verify_command_output("python", "python --version", "Python 3"):
            print("Python 3 is installed")
    """
    result = execute_in_container(container_name, command, timeout)
    
    if result['returncode'] != 0:
        return False
    
    return expected_output in result['stdout']


def verify_file_exists_in_container(
    container_name: str,
    file_path: str
) -> bool:
    """
    Verify that a file exists inside a VDE container.
    
    Args:
        container_name: Name of the container (with or without vde- prefix)
        file_path: Absolute path to the file inside the container
    
    Returns:
        True if file exists, False otherwise
    
    Raises:
        RuntimeError: If vde exec command fails to start
    
    Example:
        if verify_file_exists_in_container("python", "/usr/bin/python3"):
            print("Python3 binary exists")
    """
    # Use test -f to check if file exists (returns 0 if exists, 1 if not)
    result = execute_in_container(
        container_name,
        f"test -f {file_path}",
        timeout=10
    )
    
    return result['returncode'] == 0


def get_container_env_var(
    container_name: str,
    var_name: str
) -> Optional[str]:
    """
    Get the value of an environment variable from a VDE container.
    
    Args:
        container_name: Name of the container (with or without vde- prefix)
        var_name: Name of the environment variable
    
    Returns:
        Value of the environment variable, or None if not set
    
    Raises:
        RuntimeError: If vde exec command fails to start
    
    Example:
        path = get_container_env_var("python", "PATH")
        if path:
            print(f"Container PATH: {path}")
    """
    result = execute_in_container(
        container_name,
        f"printenv {var_name}",
        timeout=10
    )
    
    if result['returncode'] != 0:
        return None
    
    # Strip trailing newline from printenv output
    return result['stdout'].strip()
