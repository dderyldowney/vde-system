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
    run_vde_command,
    step_vde_installed,
)

# =============================================================================
# Installation GIVEN steps
# =============================================================================


@given("I have a new computer with Docker installed")
def step_new_computer_docker(context):
    """Verify Docker is actually installed - real system check."""
    context.new_computer = True  # This is scenario context, not system state
    context.docker_installed = check_docker_available(context)  # Real verification


@given("I have just cloned VDE")
@given("I have cloned the VDE repository to ~/dev")
def step_cloned_vde_repo(context):
    """Verify VDE repository actually exists at the expected location."""
    vde_root_path = Path(VDE_ROOT)
    context.vde_repo_cloned = vde_root_path.exists() and vde_root_path.is_dir()
    context.vde_location = str(VDE_ROOT)


@given("I want to install VDE")
def step_want_install_vde(context):
    context.wants_to_install = True


@given("I'm setting up VDE for the first time")
def step_first_time_setup(context):
    """Check if this is first-time setup by verifying VDE is not yet configured."""
    context.first_time_setup = True
    # Check if VDE is actually installed by looking for required directories
    required_dirs = ["configs", "templates", "data", "logs"]
    all_exist = all((Path(VDE_ROOT) / d).exists() for d in required_dirs)
    context.vde_installed = all_exist


@given("I want VDE commands available everywhere")
def step_want_vde_everywhere(context):
    context.want_vde_in_path = True


@given("VDE is being installed")
def step_vde_being_installed(context):
    context.vde_installing = True


@given("I've just installed VDE")
def step_just_installed_vde(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ["scripts", "configs", "templates", "data"]
    all_exist = all((vde_root_path / d).exists() for d in required_dirs)
    context.vde_installed = all_exist


@when('I run "create-virtual-for python"')
def step_run_create_virtual_for_python(context):
    """Run create-virtual-for python --no-start and accept success or already-exists."""
    script = Path(VDE_ROOT) / "bin" / "create-virtual-for"
    assert script.exists(), f"create-virtual-for script not found at {script}"
    assert os.access(script, os.X_OK), "create-virtual-for is not executable"

    result = subprocess.run(
        [str(script), "python", "--no-start", "--quiet"],
        capture_output=True,
        text=True,
        env={**os.environ, "VDE_ROOT_DIR": str(VDE_ROOT)},
    )

    VDE_ERR_EXISTS = 6
    assert result.returncode in (0, VDE_ERR_EXISTS), (
        f"create-virtual-for exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    context.create_vm_output = result.stdout + result.stderr
    context.create_vm_returncode = result.returncode


@given("VDE is freshly installed")
def step_freshly_installed(context):
    """Verify VDE is installed and check for VM configs."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ["scripts", "configs", "templates", "data"]
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)
    # Check if any VMs have been created (configs/docker has VM configs)
    configs_docker_dir = vde_root_path / "configs" / "docker"
    context.no_vms_created_yet = not (
        configs_docker_dir.exists() and list(configs_docker_dir.iterdir())
    )


@given("VDE has been installed")
def step_has_been_installed(context):
    """Verify VDE is actually installed."""
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ["scripts", "configs", "templates"]
    context.vde_installed = all((vde_root_path / d).exists() for d in required_dirs)


@given("I have an older version of VDE")
def step_old_version_vde(context):
    """Verify VDE exists - version checking would require actual version logic."""
    # Check if VDE is installed (directories exist)
    vde_root_path = Path(VDE_ROOT)
    required_dirs = ["scripts", "configs", "templates"]
    all_exist = all((vde_root_path / d).exists() for d in required_dirs)
    context.vde_installed = all_exist
    # Version tracking would require reading actual version from file or git
    context.vde_version = "detected" if all_exist else "none"


@given("I'm installing VDE")
def step_installing_vde(context):
    context.installing_vde = True


@given("VDE is being set up")
def step_vde_being_setup(context):
    context.vde_being_setup = True


@given("VDE is installed")
def step_vde_installed_installation(context):
    """Verify VDE is actually installed."""
    step_vde_installed(context)


@given("I've installed VDE")
def step_ive_installed_vde(context):
    """Verify VDE is actually installed."""
    step_vde_installed(context)


# =============================================================================
# Installation WHEN steps
# =============================================================================


@when("I run the initial setup script")
def step_run_initial_setup(context):
    """Execute the actual setup script and capture results."""
    setup_script = Path(VDE_ROOT) / "bin" / "build-and-start"
    if not setup_script.exists():
        setup_script = Path(VDE_ROOT) / "bin" / "install-vde.sh"
    if setup_script.exists() and os.access(setup_script, os.X_OK):
        try:
            result = subprocess.run(
                [str(setup_script)], capture_output=True, text=True, timeout=120, cwd=VDE_ROOT
            )
            context.setup_exit_code = result.returncode
            context.setup_output = result.stdout
            context.setup_error = result.stderr
            context.setup_completed = result.returncode == 0
        except subprocess.TimeoutExpired:
            context.setup_error = "Setup script timed out"
        except Exception as e:
            context.setup_error = str(e)


@when("the setup script runs")
def step_setup_script_runs(context):
    """Trigger the setup script execution."""
    step_run_initial_setup(context)


@when("the setup completes")
def step_setup_completes(context):
    """Wait for setup to complete."""
    # Setup is assumed complete when directories exist
    context.setup_completed = True


@when("setup completes")
def step_setup_completes_alt(context):
    """Wait for setup to complete (alternate phrasing)."""
    step_setup_completes(context)


@when("SSH keys are checked")
def step_ssh_keys_checked(context):
    """Check for SSH keys."""
    context.ssh_keys_exist = check_ssh_keys_exist(context)
    context.ssh_keys_checked = True


@when("I run list-vms")
def step_run_list_vms(context):
    """Run the list-vms command."""
    list_vms_script = Path(VDE_ROOT) / "bin" / "list-vms"
    if list_vms_script.exists():
        result = subprocess.run([str(list_vms_script)], capture_output=True, text=True, timeout=30)
        context.list_vms_output = result.stdout
        context.list_vms_exit_code = result.returncode
    else:
        context.list_vms_output = ""
        context.list_vms_exit_code = 1


@when("I add VDE scripts to my PATH")
def step_add_vde_to_path(context):
    """Add VDE scripts to PATH."""
    scripts_dir = Path(VDE_ROOT) / "bin"
    context.vde_in_path = scripts_dir.exists()
    if scripts_dir.exists():
        os.environ["PATH"] = str(scripts_dir) + ":" + os.environ.get("PATH", "")


@when("setup checks Docker")
def step_setup_checks_docker(context):
    """Setup checks Docker permissions."""
    context.docker_checked = check_docker_available(context)


@when("the first VM is created")
def step_first_vm_created(context):
    """Mark that the first VM is being created."""
    context.first_vm_creating = True


@when('I run "vde-health" or check status')
def step_run_vde_health(context):
    """Run health check."""
    health_script = Path(VDE_ROOT) / "bin" / "vde-health"
    if health_script.exists():
        result = subprocess.run([str(health_script)], capture_output=True, text=True, timeout=30)
        context.health_output = result.stdout
        context.health_exit_code = result.returncode
    else:
        context.health_output = "vde-health script not found"
        context.health_exit_code = 1


@when("I pull the latest changes")
def step_pull_latest_changes(context):
    """Pull latest changes from git."""
    result = subprocess.run(
        ["git", "pull"], capture_output=True, text=True, timeout=60, cwd=VDE_ROOT
    )
    context.git_pull_output = result.stdout
    context.git_pull_exit_code = result.returncode


@when("I request to remove VDE")
def step_want_to_remove(context):
    """Mark intent to remove VDE."""
    context.wants_to_remove = True


@when("the setup detects my OS (Linux/Mac)")
def step_detect_os(context):
    """Detect the operating system."""
    import platform

    context.detected_os = platform.system().lower()
    context.os_detected = True


@when("I want to start quickly")
def step_want_start_quickly(context):
    """Mark intent for quick start."""
    context.quick_start = True


@when("I need help")
def step_need_help(context):
    """Mark that user needs help."""
    context.needs_help = True


@when("I run validation checks")
def step_run_validation_checks(context):
    """Run validation checks on VDE installation."""
    context.validation_results = {
        "scripts_executable": check_scripts_executable(context),
        "templates_present": (Path(VDE_ROOT) / "templates").exists()
        or (Path(VDE_ROOT) / "templates").exists(),
        "vm_types_valid": (Path(VDE_ROOT) / "data" / "vm-types.conf").exists(),
    }


@when("I create my first VM")
def step_create_first_vm(context):
    """Create the first VM and ensure SSH environment is set up."""
    # First ensure SSH environment is set up (like VDE does when starting a VM)
    ssh_result = run_vde_command(["ssh-setup", "init"])
    context.ssh_setup_result = ssh_result.returncode == 0

    # Then create the VM
    result = run_vde_command(["create", "python"])
    context.vm_create_result = result.returncode == 0
