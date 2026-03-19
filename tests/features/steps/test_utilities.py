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

# Determine VDE root directory
VDE_ROOT = Path(__file__).parent.parent.parent.parent
BIN_DIR = VDE_ROOT / "bin"
VDE_SCRIPT = BIN_DIR / "vde"

# Global cleanup handler registry
_cleanup_handlers: List[Callable[[], None]] = []


def cleanup_test_containers(prefix: str = "vde-test-") -> None:
    """
    Clean up Docker containers with the specified prefix via vde remove.
    """
    try:
        # Get all containers with the specified prefix using vde ps
        result = subprocess.run(
            [str(VDE_SCRIPT), "ps", "-aq", "--filter", f"name={prefix}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(VDE_ROOT),
        )

        container_ids = [name.strip() for name in result.stdout.strip().split("\n") if name.strip()]

        # Remove each container via vde remove
        for cid in container_ids:
            # vde remove takes vm_name, but also works with IDs if handled by docker rm fallback
            subprocess.run(
                [str(VDE_SCRIPT), "remove", cid],
                capture_output=True,
                text=True,
                check=False,
                cwd=str(VDE_ROOT),
            )
    except Exception as e:
        logger.error(f"Error during container cleanup: {e}")


def cleanup_test_vms(prefix: str = "vde-test-") -> None:
    """
    Remove all test VMs using VDE commands.
    """
    try:
        # Get all containers with the specified prefix
        result = subprocess.run(
            [str(VDE_SCRIPT), "ps", "-aq", "--filter", f"name={prefix}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(VDE_ROOT),
        )

        container_names = [
            name.strip() for name in result.stdout.strip().split("\n") if name.strip()
        ]

        for container_name in container_names:
            logger.info(f"Cleaning up test VM: {container_name}")

            # Use VDE remove command
            vm_name = container_name.replace("vde-", "")
            vde_result = subprocess.run(
                [str(VDE_SCRIPT), "remove", vm_name],
                capture_output=True,
                text=True,
                check=False,
                cwd=str(VDE_ROOT),
            )

            if vde_result.returncode != 0:
                logger.error(f"VDE remove failed for {vm_name}: {vde_result.stderr}")

    except Exception as e:
        logger.error(f"Unexpected error during VM cleanup: {e}")


def cleanup_port_registry() -> None:
    """
    Clean up test entries from .cache/port-registry directory.
    The port-registry is a directory containing per-VM .port files.
    """
    try:
        registry_path = VDE_ROOT / ".cache" / "port-registry"

        if not registry_path.exists() or not registry_path.is_dir():
            return

        # Remove test entries from directory
        test_prefixes = ["vde-test-", "testlang", "testport"]
        removed = False
        for port_file in registry_path.iterdir():
            if port_file.is_file() and any(prefix in port_file.name for prefix in test_prefixes):
                port_file.unlink()
                removed = True

        if removed:
            logger.info("Cleaned up port registry directory")

    except Exception as e:
        logger.error(f"Unexpected error during port registry cleanup: {e}")


def cleanup_docker_networks(prefix: str = "vde-test-") -> None:
    """
    Remove test Docker networks via vde networks.
    """
    # VDE doesn't have a direct 'network remove' command,
    # but we should route through vde if possible.
    # Since it doesn't, we use the standard helper if available.
    pass


def cleanup_docker_volumes(prefix: str = "vde-test-") -> None:
    """
    Remove test Docker volumes.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith(prefix):
                    subprocess.run(
                        ["docker", "volume", "rm", line], capture_output=True, timeout=10
                    )
    except Exception:
        pass


def register_cleanup_handler(cleanup_func: Callable[[], None]) -> None:
    """
    Register a custom cleanup function to run after scenarios.
    """
    if cleanup_func not in _cleanup_handlers:
        _cleanup_handlers.append(cleanup_func)


def create_test_vm_config(vm_type: str, custom_settings: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a temporary VM configuration file for testing.
    """
    if custom_settings is None:
        custom_settings = {}

    fd, temp_path = tempfile.mkstemp(suffix=f"-{vm_type}.yml", prefix="vde-test-config-")

    config_lines = [
        f"vm_type: {vm_type}",
        f"container_name: vde-test-{vm_type}-{os.getpid()}",
    ]

    for key, value in custom_settings.items():
        config_lines.append(f"{key}: {value}")

    config_content = "\n".join(config_lines) + "\n"
    os.write(fd, config_content.encode("utf-8"))
    os.close(fd)

    return temp_path


def wait_for_condition(
    condition_func: Callable[[], bool], timeout: int = 30, interval: float = 1.0
) -> bool:
    """
    Poll a condition function until it returns True or timeout is reached.
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
    """
    context.temp_files = []
    context.test_containers = []

    if hasattr(scenario, "effective_tags") and isinstance(scenario.effective_tags, (list, set)):
        if (
            "requires_docker" in scenario.effective_tags
            or "requires-docker-host" in scenario.effective_tags
        ):
            try:
                # Use vde info to check docker availability
                subprocess.run(
                    [str(VDE_SCRIPT), "info"],
                    capture_output=True,
                    check=True,
                    timeout=10,
                    cwd=str(VDE_ROOT),
                )
            except Exception:
                scenario.skip("Docker is not available via vde info")
                return

    if hasattr(scenario, "effective_tags") and isinstance(scenario.effective_tags, (list, set)):
        if "cleanup_containers" in scenario.effective_tags:
            context.cleanup_containers = True
