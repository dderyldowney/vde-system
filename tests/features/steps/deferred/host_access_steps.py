"""
BDD Step Definitions for Host Access and Connectivity.

These steps handle VM-to-host access, host file system navigation,
host service management, and host diagnostics.

All steps use real system verification - no context flags or fake tests.
"""

import subprocess
from pathlib import Path

from behave import given, then

# Import shared configuration and helpers
from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists


# =============================================================================
# Host Access GIVEN steps
# =============================================================================

# Removed duplicate: "I have VMs running with Docker socket access"
# This step is defined in docker_operations_steps.py


# Removed duplicate: "I need to check what's running on my host"
# This step is defined in docker_operations_steps.py


# Removed duplicate: "my host has application logs"
# This step is defined in docker_operations_steps.py


# Removed duplicate: "I need to check resource usage"
# This step is defined in docker_operations_steps.py


# Removed duplicate: "I need to restart a service on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I need to read a configuration file on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I need to trigger a build on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I need to check the status of other VMs"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I need to trigger a backup on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "my host has an issue I need to diagnose"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I need to check host network connectivity"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see a list of running containers"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see the host's log output"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see a list of my host's directories"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should be able to navigate the host filesystem"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see resource usage for all containers"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see CPU, memory, and I/O statistics"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should be able to verify the restart"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see the contents of the host file"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should be able to use the content in the VM"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "the build should execute on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see the status of the Python VM"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "the backup should execute on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "my data should be backed up"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see the Docker service status"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I can diagnose the issue"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I should see network connectivity results"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I can diagnose network issues"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "the script should execute on my host"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "the cleanup should be performed"
# This step is defined in docker_operations_steps.py


# =============================================================================
# All host access steps are now defined in docker_operations_steps.py
# This file is kept empty for potential future host-specific steps
# =============================================================================