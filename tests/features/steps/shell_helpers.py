#!/usr/bin/env python3
# VDE ARCHITECTURAL RECORD
# @armor (Engine BDD Steps)
# @armor (BDD Integration Logic)
# @armor (BDD Step Definition)
# @armor (BDD Step Definition)
"""
VDE helper functions for BDD tests.

Provides:
- execute_in_container() - run commands in containers (shell or raw mode)
- Container verification functions
- VM naming utilities

All functions use actual VDE CLI commands via subprocess. NO fake tests.
"""

import os
import subprocess
import json
from typing import Dict, Any, Optional, List

from vm_common import (
    get_container_name as _get_container_name_canonical,
    get_vm_name as _get_vm_name_canonical,
)


class DockerVerificationError(Exception):
    """Raised when VDE verification fails."""

    pass


def _get_vde_root() -> str:
    """Get the VDE root directory."""
    return os.environ.get(
        "VDE_ROOT_DIR",
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ),
    )


def _run_vde_command(
    args: List[str], timeout: int = 30, check: bool = False
) -> subprocess.CompletedProcess:
    """Run a vde command and return the result."""
    vde_root = _get_vde_root()
    vde_script = os.path.join(vde_root, "bin", "vde")
    cmd = ["zsh", vde_script] + args
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=check, cwd=vde_root
    )


def _run_vde_ps(args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run vde ps command."""
    vde_root = _get_vde_root()
    vde_script = os.path.join(vde_root, "bin", "vde")
    cmd = ["zsh", vde_script, "ps"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=vde_root)


def vde_poll(args: List[str], timeout: int = 30, description: str = "condition") -> None:
    """
    Python Bridge: Call bin/vde-poll ZSH utility for deterministic readiness.
    Replaces 'Pink' fixed sleep loops and Python-native polling.
    """
    vde_root = _get_vde_root()
    poll_script = os.path.join(vde_root, "bin", "vde-poll")
    
    # Ensure args are strings
    cmd_args = ["zsh", poll_script] + [str(a) for a in args] + ["--timeout", str(timeout)]
    
    try:
        result = subprocess.run(
            cmd_args, 
            capture_output=True, 
            text=True, 
            timeout=timeout + 5,
            cwd=vde_root
        )
        
        if result.returncode != 0:
            raise AssertionError(
                f"Environment failed to reach ready state for {description} within {timeout}s.\n"
                f"STATUS: {result.returncode}\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        raise AssertionError(f"vde-poll process timed out for {description} after {timeout}s")


def wait_for_container_healthy(container_name: str, timeout: int = 30) -> None:
    """Poll container health status using `vde-poll --health`."""
    vde_poll(
        ["--health", container_name],
        timeout=timeout,
        description=f"container {container_name} to be healthy"
    )


def execute_in_container(
    container_name: str, command: str, timeout: int = 30, use_shell: bool = True
) -> Dict[str, Any]:
    """
    Execute a command inside a VDE container using vde exec.

    Args:
        container_name: Name of the container
        command: Command to execute (string, will be split if use_shell=False)
        timeout: Command timeout in seconds (default: 30)
        use_shell: If True, run via 'sh -c' (shell interpretation).
                   If False, run command directly (no shell).

    Returns:
        Dict with 'stdout', 'stderr', 'returncode'
    """
    try:
        if use_shell:
            cmd_args = ["exec", container_name, "sh", "-c", command]
        else:
            cmd_args = ["exec", container_name] + command.split()
        result = _run_vde_command(cmd_args, timeout=timeout, check=False)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1}


def verify_command_output(
    container_name: str, command: str, expected_output: str, timeout: int = 30
) -> bool:
    """Execute a command and verify its output contains expected string."""
    result = execute_in_container(container_name, command, timeout)
    return result["returncode"] == 0 and expected_output in result["stdout"]


def verify_file_exists_in_container(container_name: str, file_path: str) -> bool:
    """Verify that a file exists inside a VDE container."""
    result = execute_in_container(container_name, f"test -f {file_path}", timeout=10)
    return result["returncode"] == 0


def get_container_env_var(container_name: str, var_name: str) -> Optional[str]:
    """Get the value of an environment variable from a VDE container."""
    result = execute_in_container(container_name, f"printenv {var_name}", timeout=10)
    if result["returncode"] != 0:
        return None
    return result["stdout"].strip()


# =============================================================================
# Container Verification Functions (from docker_helpers)
# =============================================================================


def verify_container_running(container_name: str) -> Dict[str, str]:
    """Verify that a container is running using `vde ps`."""
    try:
        result = _run_vde_ps(["--json", "--filter", f"name={container_name}"])
        if result.returncode != 0:
            raise DockerVerificationError(f"vde ps command failed: {result.stderr}")
        output = result.stdout.strip()
        if not output or output == "[]":
            raise DockerVerificationError(f"Container '{container_name}' is not running")
        containers = json.loads(output)
        if not containers:
            raise DockerVerificationError(f"Container '{container_name}' is not running")
        c = containers[0]
        return {
            "ID": c.get("id", ""),
            "Image": c.get("image", ""),
            "Status": c.get("status", ""),
            "Names": c.get("name", ""),
        }
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde ps command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde ps output: {e}")


def verify_container_state(container_name: str, expected_state: str) -> Dict[str, Any]:
    """Verify container state using `vde inspect`."""
    try:
        result = _run_vde_command(["inspect", container_name, "--state"])
        if result.returncode != 0:
            raise DockerVerificationError(f"vde inspect command failed: {result.stderr}")
        state_info = json.loads(result.stdout.strip())
        actual_state = state_info.get("Status", "").lower()
        if actual_state != expected_state.lower():
            raise DockerVerificationError(
                f"Container '{container_name}' state is '{actual_state}', expected '{expected_state}'"
            )
        return state_info
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde inspect command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde inspect output: {e}")


def get_container_port(container_name: str, internal_port: int) -> int:
    """Get the host port mapped to a container's internal port."""
    try:
        result = _run_vde_command(["port", container_name, str(internal_port)])
        if result.returncode != 0:
            raise DockerVerificationError(f"vde port command failed: {result.stderr}")
        output = result.stdout.strip()
        if not output:
            raise DockerVerificationError(
                f"No port mapping found for '{container_name}' port {internal_port}"
            )
        return int(output.split(":")[-1])
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde port command timed out: {e}")


def verify_container_network(container_name: str, network_name: str) -> Dict[str, Any]:
    """Verify that a container is attached to a specific network."""
    try:
        result = _run_vde_command(["inspect", container_name, "--network"])
        if result.returncode != 0:
            raise DockerVerificationError(f"vde inspect command failed: {result.stderr}")
        networks_data = json.loads(result.stdout.strip())
        networks = networks_data.get("Networks", networks_data)
        if network_name not in networks:
            available = ", ".join(networks.keys()) if networks else "none"
            raise DockerVerificationError(
                f"Container '{container_name}' is not on network '{network_name}'. Available: {available}"
            )
        return networks[network_name]
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde inspect command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde inspect output: {e}")


def verify_container_stopped(container_name: str) -> bool:
    """Verify container is not running (stopped or removed)."""
    try:
        result = _run_vde_ps(["--json", "--filter", f"name={container_name}"])
        output = result.stdout.strip()
        if not output or output == "[]":
            return True
        containers = json.loads(output)
        return len(containers) == 0
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde ps command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde ps output: {e}")


def cleanup_test_container(container_name: str) -> bool:
    """Safely remove a test container using vde remove."""
    try:
        result = _run_vde_command(["remove", container_name], timeout=10, check=False)
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def list_containers(all_containers: bool = False) -> List[str]:
    """List VDE container names using vde ps."""
    try:
        args = ["-q"]
        if all_containers:
            args.append("-a")
        result = _run_vde_ps(args)
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception:
        return []


# =============================================================================
# VM Naming Utilities (consolidated from vm_naming_helpers)
# =============================================================================

SERVICE_VMS = frozenset(
    {
        "postgres",
        "redis",
        "mongodb",
        "mysql",
        "nginx",
        "rabbitmq",
        "couchdb",
    }
)

ALL_SERVICE_VMS = frozenset(
    {
        "postgres",
        "redis",
        "mongodb",
        "mysql",
        "nginx",
        "rabbitmq",
        "couchdb",
    }
)


# Use canonical functions from vm_common
get_container_name = _get_container_name_canonical
get_vm_name = _get_vm_name_canonical


def is_service_vm(vm_name: str) -> bool:
    """Check if VM is a service VM."""
    return vm_name in SERVICE_VMS


def is_language_vm(vm_name: str) -> bool:
    """Check if VM is a language VM."""
    return vm_name not in SERVICE_VMS


def normalize_vm_name(vm_name: str) -> str:
    """Normalize VM name to container name."""
    return _get_container_name_canonical(vm_name)
