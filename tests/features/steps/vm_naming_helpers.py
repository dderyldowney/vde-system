"""
VM Naming Convention Helpers for BDD Tests.

These functions handle the conversion between VM names (used in tests)
and container names (used by Docker).

VM Naming Rules:
- Language VMs: "python" → "python-dev", "rust" → "rust-dev", "go" → "go-dev"
- Service VMs: "postgres" → "postgres", "redis" → "redis" (no suffix)
"""

# Service VMs that don't get the "-dev" suffix
SERVICE_VMS = frozenset({
    'postgres',
    'redis',
    'mongodb',
    'mysql',
    'nginx',
    'rabbitmq',
    'couchdb',
})

# All known service VMs (for validation)
ALL_SERVICE_VMS = frozenset({
    'postgres',
    'redis',
    'mongodb',
    'mysql',
    'nginx',
    'rabbitmq',
    'couchdb',
})


def _get_container_name(vm_name: str) -> str:
    """
    Convert VM name to container name.

    Args:
        vm_name: VM name as used in test steps (e.g., "python", "postgres")

    Returns:
        Container name as used by Docker (e.g., "python-dev", "postgres")

    Examples:
        >>> _get_container_name("python")
        'python-dev'
        >>> _get_container_name("postgres")
        'postgres'
        >>> _get_container_name("rust")
        'rust-dev'
    """
    if vm_name in SERVICE_VMS:
        return vm_name
    return f"{vm_name}-dev"


def _get_vm_name(container_name: str) -> str:
    """
    Convert container name back to VM name.

    Args:
        container_name: Container name as used by Docker (e.g., "python-dev", "postgres")

    Returns:
        VM name as used in test steps (e.g., "python", "postgres")

    Examples:
        >>> _get_vm_name("python-dev")
        'python'
        >>> _get_vm_name("postgres")
        'postgres'
    """
    if container_name in SERVICE_VMS:
        return container_name
    # Remove "-dev" suffix to get VM name
    if container_name.endswith('-dev'):
        return container_name[:-4]
    return container_name


def is_service_vm(vm_name: str) -> bool:
    """
    Check if VM is a service VM.

    Args:
        vm_name: VM name to check

    Returns:
        True if VM is a service VM (no "-dev" suffix needed)
    """
    return vm_name in SERVICE_VMS


def is_language_vm(vm_name: str) -> bool:
    """
    Check if VM is a language VM.

    Args:
        vm_name: VM name to check

    Returns:
        True if VM is a language VM (needs "-dev" suffix)
    """
    return vm_name not in SERVICE_VMS


def normalize_vm_name(vm_name: str) -> str:
    """
    Normalize VM name to container name.

    This is an alias for _get_container_name() for clarity.

    Args:
        vm_name: VM name as used in test steps

    Returns:
        Container name as used by Docker
    """
    return _get_container_name(vm_name)
