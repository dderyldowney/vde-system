"""
Docker verification helper functions for BDD tests.

These helpers execute REAL Docker commands via subprocess to verify container state.
NO fake tests - all verifications use actual Docker CLI commands.
"""

import subprocess
import time
import json
from typing import Optional, Dict, Any


class DockerVerificationError(Exception):
    """Raised when Docker verification fails."""
    pass


def verify_container_running(container_name: str) -> Dict[str, str]:
    """
    Verify that a container is actually running using `docker ps`.
    
    Args:
        container_name: Name or ID of the container to verify
        
    Returns:
        Dict containing container info (ID, Image, Status, Names)
        
    Raises:
        DockerVerificationError: If container is not running or docker command fails
    """
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        if not result.stdout.strip():
            raise DockerVerificationError(
                f"Container '{container_name}' is not running (not found in docker ps output)"
            )
        
        # Parse the JSON output
        container_info = json.loads(result.stdout.strip().split('\n')[0])
        
        return {
            'ID': container_info.get('ID', ''),
            'Image': container_info.get('Image', ''),
            'Status': container_info.get('Status', ''),
            'Names': container_info.get('Names', '')
        }
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"Docker ps command timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise DockerVerificationError(f"Docker ps command failed: {e.stderr}")
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse docker ps output: {e}")


def verify_container_state(container_name: str, expected_state: str) -> Dict[str, Any]:
    """
    Verify container state using `docker inspect`.
    
    Args:
        container_name: Name or ID of the container
        expected_state: Expected state (e.g., 'running', 'exited', 'paused')
        
    Returns:
        Dict containing State section from docker inspect
        
    Raises:
        DockerVerificationError: If state doesn't match or command fails
    """
    try:
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{json .State}}', container_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        state_info = json.loads(result.stdout.strip())
        actual_state = state_info.get('Status', '').lower()
        
        if actual_state != expected_state.lower():
            raise DockerVerificationError(
                f"Container '{container_name}' state is '{actual_state}', expected '{expected_state}'"
            )
        
        return state_info
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"Docker inspect command timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise DockerVerificationError(
            f"Docker inspect command failed for '{container_name}': {e.stderr}"
        )
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse docker inspect output: {e}")


def get_container_port(container_name: str, internal_port: int) -> int:
    """
    Get the host port mapped to a container's internal port using `docker port`.
    
    Args:
        container_name: Name or ID of the container
        internal_port: Internal container port number
        
    Returns:
        Host port number as integer
        
    Raises:
        DockerVerificationError: If port mapping not found or command fails
    """
    try:
        result = subprocess.run(
            ['docker', 'port', container_name, str(internal_port)],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
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
                f"Invalid port format in docker port output: '{output}'"
            )
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"Docker port command timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise DockerVerificationError(
            f"Docker port command failed for '{container_name}': {e.stderr}"
        )


def verify_container_network(container_name: str, network_name: str) -> Dict[str, Any]:
    """
    Verify that a container is attached to a specific network using `docker inspect`.
    
    Args:
        container_name: Name or ID of the container
        network_name: Name of the network to verify
        
    Returns:
        Dict containing network settings for the specified network
        
    Raises:
        DockerVerificationError: If container not on network or command fails
    """
    try:
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{json .NetworkSettings.Networks}}', container_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        networks = json.loads(result.stdout.strip())
        
        if network_name not in networks:
            available_networks = ', '.join(networks.keys()) if networks else 'none'
            raise DockerVerificationError(
                f"Container '{container_name}' is not attached to network '{network_name}'. "
                f"Available networks: {available_networks}"
            )
        
        return networks[network_name]
        
    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"Docker inspect command timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise DockerVerificationError(
            f"Docker inspect command failed for '{container_name}': {e.stderr}"
        )
    except json.JSONDecodeError as e:
        raise DockerVerificationError(f"Failed to parse docker inspect output: {e}")


def wait_for_container_healthy(container_name: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Poll container health status using `docker inspect` until healthy or timeout.
    
    Args:
        container_name: Name or ID of the container
        timeout: Maximum seconds to wait (default: 30)
        
    Returns:
        Dict containing final Health section from docker inspect
        
    Raises:
        DockerVerificationError: If container doesn't become healthy within timeout
    """
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format', '{{json .State.Health}}', container_name],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            
            output = result.stdout.strip()
            
            # Container might not have a healthcheck defined
            if output == '<no value>' or output == 'null':
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
        except subprocess.CalledProcessError as e:
            raise DockerVerificationError(
                f"Docker inspect command failed for '{container_name}': {e.stderr}"
            )
        except json.JSONDecodeError as e:
            raise DockerVerificationError(f"Failed to parse docker inspect output: {e}")
    
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
        DockerVerificationError: If docker command fails
    """
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        # If output is empty, container is not running (stopped or removed)
        return not result.stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise DockerVerificationError(f"Docker ps command timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise DockerVerificationError(f"Docker ps command failed: {e.stderr}")


def cleanup_test_container(container_name: str) -> bool:
    """
    Safely remove a test container.

    Args:
        container_name: Name or ID of the container to remove

    Returns:
        True if container was removed or didn't exist, False on error
    """
    try:
        subprocess.run(
            ['docker', 'rm', '-f', container_name],
            capture_output=True,
            timeout=10
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False
