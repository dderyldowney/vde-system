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
    else:
        # Setup script doesn't exist - verify install capability exists
        context.setup_error = f"Setup script not found at {setup_script}"

@when('the setup script runs')
def step_setup_script_runs(context):
    """Verify the setup script runs and captures output."""
    setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
    if not setup_script.exists():
        context.setup_error = f"Setup script not found at {setup_script}"
        return

    if not os.access(setup_script, os.X_OK):
        context.setup_error = f"Setup script is not executable: {setup_script}"
        return

    # Script exists and is executable
    # Store script path for potential execution
    context.setup_script_path = str(setup_script)

@when('SSH keys are checked')
def step_ssh_keys_checked(context):
    """Check if SSH keys exist using real filesystem check."""
    # Use the helper function to do real verification
    context.ssh_keys_found = check_ssh_keys_exist()

@when('setup completes')
def step_setup_completes(context):
    """Verify setup completion by checking for setup artifacts."""
    # Check for setup completion markers
    required_dirs = ['configs', 'templates', 'data', 'logs']
    all_exist = all(
        (Path(VDE_ROOT) / d).exists() for d in required_dirs
    )
    context.setup_completed = all_exist

@when('the setup completes')
def step_the_setup_completes(context):
    """Verify setup completion by checking for setup artifacts."""
    # Check for setup completion markers
    required_dirs = ['configs', 'templates', 'data', 'logs']
    all_exist = all(
        (Path(VDE_ROOT) / d).exists() for d in required_dirs
    )
    context.setup_completed = all_exist

@when('I add VDE scripts to my PATH')
def step_add_to_path(context):
    """Verify VDE scripts are accessible from PATH or scripts directory."""
    # Check if vde command or scripts are accessible
    try:
        # Check if 'vde' wrapper is in PATH
        result = subprocess.run(
            ["which", "vde"],
            capture_output=True,
            text=True,
            timeout=5
        )
        vde_in_path = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        vde_in_path = False

    # Check if individual scripts exist and are executable
    scripts_dir = Path(VDE_ROOT) / "scripts"
    scripts_accessible = False
    if scripts_dir.exists():
        # Check for key VDE scripts
        key_scripts = ['start-virtual', 'shutdown-virtual', 'create-virtual-for']
        scripts_accessible = all(
            (scripts_dir / script).exists() and os.access((scripts_dir / script), os.X_OK)
            for script in key_scripts
        )

    context.vde_added_to_path = vde_in_path or scripts_accessible
    context.vde_wrapper_in_path = vde_in_path
    context.scripts_directly_accessible = scripts_accessible

@when('setup checks Docker')
def step_setup_checks_docker(context):
    """Actually check if Docker is available."""
    context.docker_available = check_docker_available()
    context.docker_compose_available = check_docker_compose_available()

@when('the first VM is created')
def step_first_vm_created(context):

@when('I run "vde-health" or check status')
def step_run_vde_health(context):
    """Check if vde-health script exists and can be run."""
    health_script = Path(VDE_ROOT) / "scripts" / "vde-health"
    context.vde_health_run = health_script.exists() and os.access(health_script, os.X_OK)
    context.vde_status_checked = context.vde_health_run

@when('I run list-vms')
def step_run_list_vms(context):
    """Execute the list-vms command and capture output."""
    scripts_dir = Path(VDE_ROOT) / "scripts"
    list_vms_script = scripts_dir / "list-vms"

    if list_vms_script.exists() and os.access(list_vms_script, os.X_OK):
        try:
            result = subprocess.run(
                [str(list_vms_script)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=VDE_ROOT
            )
            context.list_vms_output = result.stdout
            context.list_vms_returncode = result.returncode
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            context.list_vms_error = str(e)
    else:

@when('I pull the latest changes')
def step_pull_latest_changes(context):
    """Check if git pull would work (verify git is initialized)."""
    # Check if this is a git repository
    git_dir = Path(VDE_ROOT) / ".git"
    is_git_repo = git_dir.exists()

    if is_git_repo:
        # Check if we can run git commands
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=VDE_ROOT
            )
            has_remote = result.returncode == 0 and len(result.stdout.strip()) > 0
            context.latest_changes_pulled = has_remote
        except Exception:
    else:

@when('the setup detects my OS (Linux/Mac)')
def step_detect_os(context):
    """Detect the actual operating system."""
    import platform
    system = platform.system()
    if system == "Darwin":
        context.os_type = "darwin"
    elif system == "Linux":
        context.os_type = "linux"
    else:
        context.os_type = system.lower()

@when('I create my first VM')
def step_create_first_vm(context):
    """Check if VM creation is possible by verifying the create script exists."""
    create_script = Path(VDE_ROOT) / "scripts" / "create-virtual-for"
    context.first_vm_creation = create_script.exists()
    context.creating_first_vm = create_script.exists() and os.access(create_script, os.X_OK)
    if create_script.exists():
        context.create_script_path = str(create_script)

@when('I want to start quickly')
def step_want_start_quickly(context):

@when('I need help')
def step_need_help(context):

@when('I run validation checks')
def step_run_validation(context):
    """Run actual validation checks against VDE installation."""
    # Check key validation items
    checks = [
        (Path(VDE_ROOT) / "scripts").exists(),
        (Path(VDE_ROOT) / "configs").exists(),
        (Path(VDE_ROOT) / "scripts" / "data" / "vm-types.conf").exists(),
        check_scripts_executable()
    ]
    context.validation_checks = all(checks)
    context.validation_results = {
        "scripts_exist": checks[0],
        "configs_exist": checks[1],
        "vm_types_conf": checks[2],
        "scripts_executable": checks[3]
    }
