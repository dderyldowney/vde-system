"""
BDD Step Definitions for Team Collaboration and Maintenance.

These steps handle team configuration sharing, system maintenance,
VDE updates, batch operations, and scaling for large projects.

All steps use real system verification - no context flags or fake tests.
"""

import subprocess
from pathlib import Path

from behave import then

# Import shared configuration and helpers
from config import VDE_ROOT
from vm_common import run_vde_command, container_exists, docker_ps


# =============================================================================
# Team Collaboration GIVEN steps
# =============================================================================

# Removed duplicate: "I have updated my system Docker"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "my team wants to use a new language"
# This step is defined in ssh_docker_steps.py
# Team new language context is set in ssh_docker_steps.py


# =============================================================================
# Team Collaboration THEN steps - Verification
# =============================================================================

# Removed duplicate: "my data should be preserved (if using volumes)"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "it should use the standard VDE configuration"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "it should be ready for the team to use"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "the instructions should include SSH config examples"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "the instructions should work on their first try"
# This step is defined in ssh_docker_steps.py

# Removed duplicate: "I need to manage multiple VMs"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "only language VMs should stop"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "I need to update VDE itself"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "I can update the VDE scripts"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "I want to check VM resource consumption"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "I should see which VMs are consuming resources"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "I should be able to identify heavy VMs"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "my project has grown"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "the system should handle many VMs"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "old configuration issues should be resolved"
# This step is defined in config_steps.py

# Removed duplicate: "I should see CPU and memory usage"
# This step is defined in vm_status_steps.py

# Removed duplicate: "the configuration should be validated"
# This step is defined in config_steps.py

# Removed duplicate: "I can verify environment variables match"
# This step is defined in config_steps.py

# Removed duplicate: "I should see which containers are healthy"
# This step is defined in vm_status_steps.py

# Removed duplicate: "I should see any that are failing"
# This step is defined in vm_status_steps.py

# Removed duplicate: "I should be able to identify issues"
# This step is defined in vm_status_steps.py

# Removed duplicate: "image should be built successfully"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "image should be rebuilt"
# This step is defined in docker_operations_steps.py

# Removed duplicate: "I have updated VDE scripts"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "they should use the new VDE configuration"
# This step is defined in daily_workflow_steps.py


# =============================================================================
# All team collaboration and maintenance steps are now defined in other files:
# - ssh_docker_steps.py: SSH configuration and team setup
# - daily_workflow_steps.py: Multi-VM management, VDE updates
# - config_steps.py: Configuration management
# - vm_status_steps.py: Container health and status monitoring
# - docker_operations_steps.py: Docker image operations
#
# This file is kept empty for potential future team-specific steps
# =============================================================================
