"""
VDE verification helper functions for BDD tests.

These helpers execute VDE commands via subprocess to verify container state.
All Docker operations are abstracted through the vde command interface.
NO fake tests - all verifications use actual VDE CLI commands.
"""

import os
import subprocess
import time
import json
from typing import Optional, Dict, Any, List


class DockerVerificationError(Exception):
    """Raised when VDE verification fails."""
    pass


def _get_vde_root() -> str:
    """Get the VDE root directory."""
    return os.environ.get("VDE_ROOT_DIR", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


def _run_vde_command(args: List[str], timeout: int = 10, check: bool = True) -> subprocess.CompletedProcess:
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


def _run_vde_ps(args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run vde-ps command directly.
    
    Args:
        args: Arguments to pass to vde-ps
        timeout: Command timeout in seconds
        
    Returns:
        CompletedProcess result
    """
    vde_root = _get_vde_root()
    vde_ps = os.path.join(vde_root, "bin", "vde-ps")
    
    cmd = ["zsh", vde_ps] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=vde_root
    )


def verify_container_running(container_name: str) -> Dict[str, str]:
    """
    Verify that a container is actually running using `vde ps`.
    
    Args:
        container_name: Name or ID of the container to verify
        
    Returns:
        Dict containing container info (ID, Image, Status, Names)
        
    Raises:
        DockerVerificationError: If container is not running or vde command fails
    """
    try:
        # Use vde ps with JSON output and filter
        result = _run_vde_ps(["--json", "--filter", f"name={container_name}"])
        
        if result.returncode != 0:
            raise DockerVerificationError(f"vde ps command failed: {result.stderr}")
        
        # Parse JSON output
        output = result.stdout.strip()
        if not output or output == "[]":
            raise DockerVerificationError(
                f"Container '{container_name}' is not running (not found in vde ps output)"
            )
        
        containers = json.loads(output)
        if not containers:
            raise DockerVerificationError(
                f"Container '{container_name}' is not running (not found in vde ps output)"
            )
        
        # Return first matching container
        container_info = containers[0]
        return {
            'ID': container_info.get('id', ''),
            'Image': container_info.get('image', ''),
            'Status': container_info.get('status', ''),
            'Names': container_info.get('name', '')
        }
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde ps command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde ps output: {e}")


def verify_container_state(container_name: str, expected_state: str) -> Dict[str, Any]:
    """
    Verify container state using `vde inspect`.
    
    Args:
        container_name: Name or ID of the container
        expected_state: Expected state (e.g., 'running', 'exited', 'paused')
        
    Returns:
        Dict containing State section from vde inspect
        
    Raises:
        DockerVerificationError: If state doesn't match or command fails
    """
    try:
        result = _run_vde_command(["inspect", container_name, "--state"])
        
        if result.returncode != 0:
            raise DockerVerificationError(
                f"vde inspect command failed for '{container_name}': {result.stderr}"
            )
        
        state_info = json.loads(result.stdout.strip())
        actual_state = state_info.get('Status', '').lower()
        
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
    """
    Get the host port mapped to a container's internal port using `vde port`.
    
    Args:
        container_name: Name or ID of the container
        internal_port: Internal container port number
        
    Returns:
        Host port number as integer
        
    Raises:
        DockerVerificationError: If port mapping not found or command fails
    """
    try:
        result = _run_vde_command(["port", container_name, str(internal_port)])
        
        if result.returncode != 0:
            raise DockerVerificationError(
                f"vde port command failed for '{container_name}': {result.stderr}"
            )
        
        output = result.stdout.strip()
        if not output:
            raise DockerVerificationError(
                f"No port mapping found for container '{container_name}' port {internal_port}"
            )
        
        # Output format: "0.0.0.0:8080" or "[::]:8080"
        # Extract the port number after the last colon
        host_port = output.split(':')[-1]
        
        try:
            return int(host_port)
        except ValueError:
            raise DockerVerificationError(
                f"Invalid port format in vde port output: '{output}'"
            )
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde port command timed out: {e}")


def verify_container_network(container_name: str, network_name: str) -> Dict[str, Any]:
    """
    Verify that a container is attached to a specific network using `vde inspect`.
    
    Args:
        container_name: Name or ID of the container
        network_name: Name of the network to verify
        
    Returns:
        Dict containing network settings for the specified network
        
    Raises:
        DockerVerificationError: If container not on network or command fails
    """
    try:
        result = _run_vde_command(["inspect", container_name, "--network"])
        
        if result.returncode != 0:
            raise DockerVerificationError(
                f"vde inspect command failed for '{container_name}': {result.stderr}"
            )
        
        networks_data = json.loads(result.stdout.strip())
        networks = networks_data.get('Networks', networks_data)
        
        if network_name not in networks:
            available_networks = ', '.join(networks.keys()) if networks else 'none'
            raise DockerVerificationError(
                f"Container '{container_name}' is not attached to network '{network_name}'. "
                f"Available networks: {available_networks}"
            )
        
        return networks[network_name]
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"vde inspect command timed out: {e}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse vde inspect output: {e}")


def wait_for_container_healthy(container_name: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Poll container health status using `vde inspect` until healthy or timeout.
    
    Args:
        container_name: Name or ID of the container
        timeout: Maximum seconds to wait (default: 30)
        
    Returns:
        Dict containing final Health section from vde inspect
        
    Raises:
        DockerVerificationError: If container doesn't become healthy within timeout
    """
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        try:
            result = _run_vde_command(["inspect", container_name, "--health"], timeout=5)
            
            if result.returncode != 0:
                raise DockerVerificationError(
                    f"vde inspect command failed for '{container_name}': {result.stderr}"
                )
            
            output = result.stdout.strip()
            
            # Container might not have a healthcheck defined
            if output == '<no value>' or output == 'null' or not output:
                raise DockerVerificationError(
                    f"Container '{container_name}' does not have a healthcheck defined"
                )
            
            health_info = json.loads(output)
            last_status = health_info.get('Status', 'unknown')
            
            if last_status == 'healthy':
                return health_info
            
            # Wait before next poll
            time.sleep(1)
            
        except subprocess.TimeoutExpired:
            # Continue polling even if one check times out
            continue
        except json.JSONDecodeError as e:
            raise DockerVerificationError(f"Failed to parse vde inspect output: {e}")
    
    # Timeout reached
    elapsed = time.time() - start_time
    raise DockerVerificationError(
        f"Container '{container_name}' did not become healthy within {timeout}s "
        f"(last status: {last_status}, elapsed: {elapsed:.1f}s)"
    )


def verify_container_stopped(container_name: str) -> bool:
    """
    Verify container is not running (stopped or removed).

    Args:
        container_name: Name or ID of the container to check

    Returns:
        True if container is not running, False if it is running

    Raises:
        DockerVerificationError: If vde command fails
    """
    try:
        result = _run_vde_ps(["--json", "--filter", f"name={container_name}"])

        # If output is empty or [], container is not running (stopped or removed)
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
    """
    Safely remove a test container using vde remove.

    Args:
        container_name: Name or ID of the container to remove

    Returns:
        True if container was removed or didn't exist, False on error
    """
    try:
        result = _run_vde_command(["remove", container_name], timeout=10, check=False)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False


def list_containers(all_containers: bool = False) -> List[str]:
    """
    List VDE container names using vde ps.

    Args:
        all_containers: If True, include stopped containers

    Returns:
        List of container names
    """
    try:
        args = ["-q"]
        if all_containers:
            args.append("-a")
        
        result = _run_vde_ps(args)
        
        if result.returncode != 0:
            return []
        
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    except Exception:
        return []


def container_exists(container_name: str) -> bool:
    """
    Check if a container exists (running or stopped) using vde ps.

    Args:
        container_name: Name of the container to check

    Returns:
        True if container exists, False otherwise
    """
    try:
        result = _run_vde_ps(["-a", "-q", "--filter", f"name={container_name}"])
        return container_name in result.stdout or f"vde-{container_name}" in result.stdout
    except Exception:
        return False


def execute_in_container(container_name: str, command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a command in a container using vde exec.

    Args:
        container_name: Name of the container
        command: Command to execute
        timeout: Command timeout in seconds

    Returns:
        Dict with 'stdout', 'stderr', 'returncode'
    """
    try:
        # Split command into args for vde exec
        result = _run_vde_command(
            ["exec", container_name] + command.split(),
            timeout=timeout,
            check=False
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }
