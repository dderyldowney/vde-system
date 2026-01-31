"""
BDD Step Definitions for Installation and Initial Setup.

These steps handle the GIVEN and WHEN scenarios for installation.
Post-installation verification steps are in post_install_verification_steps.py.
Uninstallation and cleanup steps are in uninstallation_steps.py.
"""
import os
import subprocess
import sys

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, when

from config import VDE_ROOT

# Import shared helper functions from vm_common
from vm_common import (
    check_docker_available,
    check_docker_compose_available,
    check_zsh_available,
    check_ssh_keys_exist,
    check_scripts_executable,
)

# =============================================================================
# Installation GIVEN steps
# =============================================================================

@given('I have a new computer with Docker installed')
def step_new_computer_docker(context):
    """Verify Docker is actually installed - real system check."""
    context.new_computer = True  # This is scenario context, not system state
    context.docker_installed = check_docker_available()  # Real verification

@given('I have cloned the VDE repository to ~/dev')
def step_cloned_vde_repo(context):
    """Verify VDE repository actually exists at the expected location."""
    vde_root_path = Path(VDE_ROOT)
    context.vde_repo_cloned = vde_root_path.exists() and vde_root_path.is_dir()
    context.vde_location = str(VDE_ROOT)

@given('I want to install VDE')
def step_want_install_vde(context):
    context.wants_to_install = True

@given('I\'m setting up VDE for the first time')
def step_first_time_setup(context):
    """Check if this is first-time setup by verifying VDE is not yet configured."""
    context.first_time_setup = True
    # Check if VDE is actually installed by looking for required directories
    required_dirs = ['configs', 'templates', 'data', 'logs']
    all_exist = all((Path(VDE_ROOT) / d).exists() for d in required_dirs)
    context.vde_installed = all_exist

@given('I want VDE commands available everywhere')
def step_want_vde_everywhere(context):
    context.want_vde_in_path = True

@given('VDE is being installed')
def step_vde_being_installed(context):
    context.vde_installing = True

@given('I\'ve just installed VDE')
def step_just_installed_vde(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates', 'data']
    all_exist = all((vde_root_path / d).exists() for d in required_dirs)
    context.vde_installed = all_exist

@given('VDE is freshly installed')
def step_freshly_installed(context):
    """Verify VDE is installed and check for VM configs."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates', 'data']
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)
    # Check if any VMs have been created (configs/docker has VM configs)
    configs_docker_dir = vde_root_path / 'configs' / 'docker'
    context.no_vms_created_yet = not (configs_docker_dir.exists() and list(configs_docker_dir.iterdir()))

@given('VDE has been installed')
def step_has_been_installed(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates']
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)

@given('I have an older version of VDE')
def step_old_version_vde(context):
    """Verify VDE exists - version checking would require actual version logic."""
    # Check if VDE is installed (directories exist)
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates']
    all_exist = all((vde_root_path / d).exists() for d in required_dirs)
    context.vde_installed = all_exist
    # Version tracking would require reading actual version from file or git
    context.vde_version = "detected" if all_exist else "none"

@given('I\'m installing VDE')
def step_installing_vde(context):
    context.installing_vde = True

@given('VDE is being set up')
def step_vde_being_setup(context):
    context.vde_being_setup = True

@given('VDE is installed')
def step_vde_installed(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates']
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)

@given("I've installed VDE")
def step_ive_installed_vde(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ['scripts', 'configs', 'templates']
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)

# =============================================================================
# Installation WHEN steps
# =============================================================================

@when('I run the initial setup script')
def step_run_initial_setup(context):
    """Execute the actual setup script and capture results."""
    setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
    if setup_script.exists() and os.access(setup_script, os.X_OK):
        try:
            result = subprocess.run(
                [str(setup_script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=VDE_ROOT
            )
            context.setup_exit_code = result.returncode
            context.setup_output = result.stdout
            context.setup_error = result.stderr
            context.setup_completed = result.returncode == 0
        except subprocess.TimeoutExpired:
            context.setup_error = "Setup script timed out"
        except Exception as e:
            context.setup_error = str(e)
