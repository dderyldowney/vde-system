"""
Test utilities and fixtures for VDE Behave tests.

Provides shared utility functions and Behave hooks for test setup/teardown.
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# Global cleanup handler registry
_cleanup_handlers: List[Callable[[], None]] = []


def cleanup_test_containers(prefix: str = "vde-test-") -> None:
    """
    Clean up Docker containers with the specified prefix.
    
    Args:
        prefix: Container name prefix to filter by (default: "vde-test-")
    
    Raises:
        subprocess.CalledProcessError: If docker commands fail
    """
    # Get all containers with the specified prefix
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={prefix}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=True
    )
    
    container_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
    
    # Remove each container
    for container_name in container_names:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            text=True,
            check=True
        )


def cleanup_test_vms(prefix: str = "vde-test-") -> None:
    """
    Remove all test VMs using VDE commands and verify Docker cleanup.
    
    This function:
    1. Lists all Docker containers with the specified prefix
    2. Attempts to remove them using VDE remove command
    3. Falls back to direct Docker removal if VDE command fails
    4. Verifies containers are actually removed
    
    Args:
        prefix: Container name prefix to filter by (default: "vde-test-")
    
    Note:
        This function is idempotent and safe to call multiple times.
        Errors are logged but don't raise exceptions.
    """
    try:
        # Get all containers with the specified prefix
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={prefix}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        container_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        
        for container_name in container_names:
            logger.info(f"Cleaning up test VM: {container_name}")
            
            # Use VDE remove command
            vde_result = subprocess.run(
                ["./scripts/vde", "remove", container_name],
                capture_output=True,
                text=True,
                check=False,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            )
            
            if vde_result.returncode != 0:
                logger.error(f"VDE remove failed for {container_name}: {vde_result.stderr}")
                raise Exception(f"Failed to remove VM {container_name}")
            
            # Verify container is removed
            verify_result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if container_name in verify_result.stdout:
                logger.error(f"Failed to remove container: {container_name}")
            else:
                logger.info(f"Successfully removed container: {container_name}")
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during VM cleanup: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during VM cleanup: {e}")


def cleanup_port_registry() -> None:
    """
    Clean up test entries from .vde/port-registry.json.
    
    Removes all port registry entries for containers with test prefixes
    (vde-test-*). If the registry file doesn't exist, this is a no-op.
    
    Note:
        This function is idempotent and safe to call multiple times.
        Errors are logged but don't raise exceptions.
    """
    try:
        # Determine VDE root directory (3 levels up from this file)
        vde_root = Path(__file__).parent.parent.parent.parent
        registry_path = vde_root / ".vde" / "port-registry.json"
        
        if not registry_path.exists():
            logger.debug("Port registry file does not exist, skipping cleanup")
            return
        
        # Read current registry
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Filter out test entries
        original_count = len(registry)
        registry = {
            vm_name: ports
            for vm_name, ports in registry.items()
            if not vm_name.startswith("vde-test-")
        }
        removed_count = original_count - len(registry)
        
        if removed_count > 0:
            # Write back cleaned registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            logger.info(f"Removed {removed_count} test entries from port registry")
        else:
            logger.debug("No test entries found in port registry")
            
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing port registry JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during port registry cleanup: {e}")


def cleanup_docker_networks(prefix: str = "vde-test-") -> None:
    """
    Remove test Docker networks.
    
    Args:
        prefix: Network name prefix to filter by (default: "vde-test-")
    
    Note:
        This function is idempotent and safe to call multiple times.
        Errors are logged but don't raise exceptions.
    """
    try:
        # Get all networks with the specified prefix
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", f"name={prefix}", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        network_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        
        for network_name in network_names:
            logger.info(f"Removing test network: {network_name}")
            subprocess.run(
                ["docker", "network", "rm", network_name],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Verify network is removed
            verify_result = subprocess.run(
                ["docker", "network", "ls", "--filter", f"name={network_name}", "--format", "{{.Name}}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if network_name in verify_result.stdout:
                logger.warning(f"Failed to remove network: {network_name}")
            else:
                logger.info(f"Successfully removed network: {network_name}")
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during network cleanup: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during network cleanup: {e}")


def cleanup_docker_volumes(prefix: str = "vde-test-") -> None:
    """
    Remove test Docker volumes.
    
    Args:
        prefix: Volume name prefix to filter by (default: "vde-test-")
    
    Note:
        This function is idempotent and safe to call multiple times.
        Errors are logged but don't raise exceptions.
    """
    try:
        # Get all volumes with the specified prefix
        result = subprocess.run(
            ["docker", "volume", "ls", "--filter", f"name={prefix}", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        volume_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        
        for volume_name in volume_names:
            logger.info(f"Removing test volume: {volume_name}")
            subprocess.run(
                ["docker", "volume", "rm", volume_name],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Verify volume is removed
            verify_result = subprocess.run(
                ["docker", "volume", "ls", "--filter", f"name={volume_name}", "--format", "{{.Name}}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if volume_name in verify_result.stdout:
                logger.warning(f"Failed to remove volume: {volume_name}")
            else:
                logger.info(f"Successfully removed volume: {volume_name}")
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during volume cleanup: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during volume cleanup: {e}")


def register_cleanup_handler(cleanup_func: Callable[[], None]) -> None:
    """
    Register a custom cleanup function to run after scenarios.
    
    Registered functions will be called during the after_scenario hook.
    Functions should be idempotent and handle their own errors gracefully.
    
    Args:
        cleanup_func: A callable that takes no arguments and returns None
    
    Example:
        def my_cleanup():
            # Custom cleanup logic
            pass
        
        register_cleanup_handler(my_cleanup)
    """
    if cleanup_func not in _cleanup_handlers:
        _cleanup_handlers.append(cleanup_func)
        logger.debug(f"Registered cleanup handler: {cleanup_func.__name__}")


def create_test_vm_config(vm_type: str, custom_settings: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a temporary VM configuration file for testing.
    
    Args:
        vm_type: The VM type (e.g., "python", "js", "ruby")
        custom_settings: Optional dictionary of custom configuration settings
    
    Returns:
        Path to the temporary configuration file
    
    Example:
        config_path = create_test_vm_config("python", {"memory": "2g", "cpus": "2"})
    """
    if custom_settings is None:
        custom_settings = {}
    
    # Create temporary file
    fd, temp_path = tempfile.mkstemp(suffix=f"-{vm_type}.yml", prefix="vde-test-config-")
    
    # Build configuration content
    config_lines = [
        f"vm_type: {vm_type}",
        f"container_name: vde-test-{vm_type}-{os.getpid()}",
    ]
    
    # Add custom settings
    for key, value in custom_settings.items():
        config_lines.append(f"{key}: {value}")
    
    # Write configuration
    config_content = '\n'.join(config_lines) + '\n'
    os.write(fd, config_content.encode('utf-8'))
    os.close(fd)
    
    return temp_path


def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: int = 30,
    interval: float = 1.0
) -> bool:
    """
    Poll a condition function until it returns True or timeout is reached.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds (default: 30)
        interval: Time between checks in seconds (default: 1.0)
    
    Returns:
        True if condition was met, False if timeout was reached
    
    Example:
        def container_running():
            result = subprocess.run(["./scripts/vde", "ps", "--filter", "name=test"], 
                                   capture_output=True, text=True)
            return "test" in result.stdout
        
        success = wait_for_condition(container_running, timeout=60)
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    return False


# Behave hooks

def before_scenario(context, scenario):
    """
    Behave hook executed before each scenario.
    
    Handles tag-based setup:
    - @requires_docker: Verifies Docker is available
    - @cleanup_containers: Marks scenario for container cleanup
    
    Args:
        context: Behave context object
        scenario: Behave scenario object
    """
    # Initialize cleanup tracking
    context.temp_files = []
    context.test_containers = []
    
    # Check for @requires_docker tag
    if "requires_docker" in scenario.effective_tags:
        try:
            subprocess.run(
                ["docker", "info"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            scenario.skip("Docker is not available")
            return
    
    # Mark for cleanup if tagged
    if "cleanup_containers" in scenario.effective_tags:
        context.cleanup_containers = True
