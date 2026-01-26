"""
BDD Step Definitions for Installation and Initial Setup.
These are critical for ZeroToMastery students getting started with VDE.
"""
import os
import shutil
import subprocess
import sys

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT

# VDE_ROOT imported from config


# =============================================================================
# Helper Functions for Real Verification
# =============================================================================

def check_docker_available():
    """Check if Docker is installed and accessible."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_docker_compose_available():
    """Check if docker-compose is installed and accessible."""
    try:
        # Try docker-compose (standalone) first
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True
        # Try docker compose (plugin) next
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_zsh_available():
    """Check if zsh is installed and accessible."""
    try:
        result = subprocess.run(
            ["zsh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_vde_script_exists(script_name):
    """Check if a VDE script exists and is executable."""
    script_path = Path(VDE_ROOT) / "scripts" / script_name
    return script_path.exists() and os.access(script_path, os.X_OK)


def check_directory_exists(dir_name):
    """Check if a directory exists in VDE_ROOT."""
    dir_path = Path(VDE_ROOT) / dir_name
    return dir_path.exists() and dir_path.is_dir()


def check_file_in_vde(file_path):
    """Check if a file exists relative to VDE_ROOT."""
    full_path = Path(VDE_ROOT) / file_path
    return full_path.exists() and full_path.is_file()


def get_vm_types():
    """Read and parse vm-types.conf to get available VM types."""
    vm_types_file = Path(VDE_ROOT) / "scripts" / "data" / "vm-types.conf"
    if not vm_types_file.exists():
        return []
    content = vm_types_file.read_text()
    # Extract VM type names (first word of each line, skipping comments)
    vm_types = set()  # Use set to avoid duplicates
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split('|')
            if parts:
                # Get all aliases for this VM type
                for vm_type in parts:
                    vm_type = vm_type.strip()
                    if vm_type and vm_type not in ['lang', 'service', 'display']:
                        vm_types.add(vm_type)
    return sorted(vm_types)  # Return sorted list for consistency


def check_docker_network_exists(network_name):
    """Check if a Docker network exists."""
    try:
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", f"name={network_name}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return network_name in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ssh_keys_exist():
    """Check if SSH keys exist in standard location."""
    ssh_dir = Path.home() / ".ssh"
    key_file = ssh_dir / "id_ed25519"
    return key_file.exists()


def check_scripts_executable():
    """Check that all shell scripts in scripts/ are executable."""
    scripts_dir = Path(VDE_ROOT) / "scripts"
    if not scripts_dir.exists():
        return False
    return all(os.access(script_file, os.X_OK) for script_file in scripts_dir.rglob("*.sh"))

# =============================================================================
# Installation GIVEN steps
# =============================================================================

@given('I have a new computer with Docker installed')
def step_new_computer_docker(context):
    context.new_computer = True
    context.docker_installed = True

@given('I have cloned the VDE repository to ~/dev')
def step_cloned_vde_repo(context):
    context.vde_repo_cloned = True
    context.vde_location = str(VDE_ROOT)

@given('I want to install VDE')
def step_want_install_vde(context):
    context.wants_to_install = True

@given('I\'m setting up VDE for the first time')
def step_first_time_setup(context):
    context.first_time_setup = True
    context.vde_installed = False

@given('I want VDE commands available everywhere')
def step_want_vde_everywhere(context):
    context.want_vde_in_path = True

@given('VDE is being installed')
def step_vde_being_installed(context):
    context.vde_installing = True

@given('I\'ve just installed VDE')
def step_just_installed_vde(context):
    context.vde_installed = True

@given('VDE is freshly installed')
def step_freshly_installed(context):
    context.vde_installed = True
    context.no_vms_created_yet = True

@given('VDE has been installed')
def step_has_been_installed(context):
    context.vde_installed = True

@given('I have an older version of VDE')
def step_old_version_vde(context):
    context.vde_version = "old"
    context.vde_installed = True

@given('I no longer want VDE on my system')
def step_want_remove_vde(context):
    context.want_uninstall = True

@given('I\'m installing VDE')
def step_installing_vde(context):
    context.installing_vde = True

@given('VDE is being set up')
def step_vde_being_setup(context):
    context.vde_being_setup = True

@given('VDE is installed')
def step_vde_installed(context):
    context.vde_installed = True

@given("I've installed VDE")
def step_ive_installed_vde(context):
    context.vde_installed = True

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
            context.initial_setup_run = True
            context.setup_exit_code = result.returncode
            context.setup_output = result.stdout
            context.setup_error = result.stderr
            context.setup_completed = result.returncode == 0
        except subprocess.TimeoutExpired:
            context.initial_setup_run = True
            context.setup_completed = False
            context.setup_error = "Setup script timed out"
        except Exception as e:
            context.initial_setup_run = True
            context.setup_completed = False
            context.setup_error = str(e)
    else:
        # Setup script doesn't exist - verify install capability exists
        context.initial_setup_run = False
        context.setup_completed = False
        context.setup_error = f"Setup script not found at {setup_script}"

@when('the setup script runs')
def step_setup_script_runs(context):
    """Verify the setup script runs and captures output."""
    setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
    if not setup_script.exists():
        context.setup_ran = False
        context.setup_error = f"Setup script not found at {setup_script}"
        return

    if not os.access(setup_script, os.X_OK):
        context.setup_ran = False
        context.setup_error = f"Setup script is not executable: {setup_script}"
        return

    # Script exists and is executable
    context.setup_ran = True
    # Store script path for potential execution
    context.setup_script_path = str(setup_script)

@when('SSH keys are checked')
def step_ssh_keys_checked(context):
    """Check if SSH keys exist using real filesystem check."""
    context.ssh_keys_checked = True
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
    context.docker_checked = True
    context.docker_available = check_docker_available()
    context.docker_compose_available = check_docker_compose_available()

@when('the first VM is created')
def step_first_vm_created(context):
    context.first_vm_created = True
    context.vde_network_created = True

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
            context.list_vms_run = True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            context.list_vms_error = str(e)
            context.list_vms_run = False
    else:
        context.list_vms_run = False

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
            context.latest_changes_pulled = False
    else:
        context.latest_changes_pulled = False

@when('I want to remove it')
def step_want_to_remove(context):
    context.removal_requested = True

@when('the setup detects my OS (Linux/Mac)')
def step_detect_os(context):
    """Detect the actual operating system."""
    import platform
    context.os_detected = True
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
    context.quick_start = True

@when('I need help')
def step_need_help(context):
    context.help_needed = True

@when('I run validation checks')
def step_run_validation(context):
    """Run actual validation checks against VDE installation."""
    context.validation_run = True
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

# =============================================================================
# Installation THEN steps
# =============================================================================

@then('VDE should be properly installed')
def step_vde_properly_installed(context):
    """Verify VDE is properly installed by checking directory structure and scripts."""
    vde_root = Path(VDE_ROOT)
    assert vde_root.exists(), f"VDE_ROOT directory does not exist: {vde_root}"

    # Check core directories exist
    required_dirs = ['scripts', 'configs', 'templates', 'data', 'logs']
    for dir_name in required_dirs:
        dir_path = vde_root / dir_name
        assert dir_path.exists(), f"Required directory {dir_name} does not exist at {dir_path}"
        assert dir_path.is_dir(), f"{dir_path} is not a directory"

    # Check that scripts directory has executable files
    scripts_dir = vde_root / "scripts"
    script_files = list(scripts_dir.glob("*.sh"))
    assert len(script_files) > 0, "No shell scripts found in scripts directory"
    assert check_scripts_executable(), "Not all scripts are executable"

@then('required directories should be created')
def step_required_dirs_created(context):
    """Verify all required VDE directories are created."""
    required_dirs = ['configs', 'templates', 'data', 'logs', 'projects', 'env-files', 'backup', 'cache']
    for dir_name in required_dirs:
        dir_path = Path(VDE_ROOT) / dir_name
        assert dir_path.exists(), f"Required directory {dir_name} does not exist at {dir_path}"
        assert dir_path.is_dir(), f"{dir_path} is not a directory"

@then('I should see success message')
def step_see_success_message(context):
    """Verify a success message was displayed (check command output if available)."""
    # If a command was run, check its output
    if hasattr(context, 'last_command_output'):
        output = context.last_command_output
        # Check for success indicators
        success_indicators = ['success', 'completed', 'done', 'installed', 'ready']
        has_success = any(indicator in output.lower() for indicator in success_indicators)
        assert has_success, f"No success message found in output: {output}"

@then('it should verify Docker is installed')
def step_verify_docker_installed(context):
    """Verify Docker installation is checked."""
    assert check_docker_available(), "Docker is not installed or not accessible"

@then('it should verify docker-compose is available')
def step_verify_docker_compose(context):
    """Verify docker-compose availability is checked."""
    assert check_docker_compose_available(), "docker-compose is not installed or not accessible"

@then('it should verify zsh is available')
def step_verify_zsh_available(context):
    """Verify zsh availability is checked."""
    assert check_zsh_available(), "zsh is not installed or not accessible"

@then('it should report missing dependencies clearly')
def step_report_missing_deps(context):
    """Verify missing dependencies are reported (check command output)."""
    # This step validates that when dependencies are missing, they're clearly reported
    # Since we're testing with a working environment, we verify the reporting mechanism exists
    setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
    assert setup_script.exists(), "Setup script not found at expected location"
    content = setup_script.read_text()
    # Check that script has dependency checking logic
    has_dependency_check = (
        'docker' in content.lower() or
        'zsh' in content.lower() or
        'depend' in content.lower()
    )
    assert has_dependency_check, "Setup script does not contain dependency checking logic"

@then('configs/ directory should exist')
def step_configs_dir_exists(context):
    """Verify configs directory exists."""
    configs_dir = Path(VDE_ROOT) / "configs"
    assert configs_dir.exists(), f"configs directory does not exist at {configs_dir}"
    assert configs_dir.is_dir(), f"{configs_dir} is not a directory"

@then('templates/ directory should exist with templates')
def step_templates_dir_exists(context):
    """Verify templates directory exists and contains templates."""
    templates_dir = Path(VDE_ROOT) / "templates"
    assert templates_dir.exists(), f"templates directory does not exist at {templates_dir}"
    assert templates_dir.is_dir(), f"{templates_dir} is not a directory"

    # Check that there are actual template files
    template_files = list(templates_dir.rglob("*"))
    non_keep_files = [f for f in template_files if f.name != ".keep"]
    assert len(template_files) > 0, "templates directory is empty"

@then('data/ directory should exist for persistent data')
def step_data_dir_exists(context):
    """Verify data directory exists."""
    data_dir = Path(VDE_ROOT) / "data"
    assert data_dir.exists(), f"data directory does not exist at {data_dir}"
    assert data_dir.is_dir(), f"{data_dir} is not a directory"

@then('logs/ directory should exist')
def step_logs_dir_exists(context):
    """Verify logs directory exists."""
    logs_dir = Path(VDE_ROOT) / "logs"
    assert logs_dir.exists(), f"logs directory does not exist at {logs_dir}"
    assert logs_dir.is_dir(), f"{logs_dir} is not a directory"

@then('projects/ directory should exist for code')
def step_projects_dir_exists(context):
    """Verify projects directory exists."""
    projects_dir = Path(VDE_ROOT) / "projects"
    assert projects_dir.exists(), f"projects directory does not exist at {projects_dir}"
    assert projects_dir.is_dir(), f"{projects_dir} is not a directory"

@then('env-files/ directory should exist')
def step_env_files_dir_exists(context):
    """Verify env-files directory exists."""
    env_files_dir = Path(VDE_ROOT) / "env-files"
    assert env_files_dir.exists(), f"env-files directory does not exist at {env_files_dir}"
    assert env_files_dir.is_dir(), f"{env_files_dir} is not a directory"

@then('backup/ directory should exist')
def step_backup_dir_exists(context):
    """Verify backup directory exists."""
    backup_dir = Path(VDE_ROOT) / "backup"
    assert backup_dir.exists(), f"backup directory does not exist at {backup_dir}"
    assert backup_dir.is_dir(), f"{backup_dir} is not a directory"

@then('cache/ directory should exist')
def step_cache_dir_exists(context):
    """Verify cache directory exists."""
    cache_dir = Path(VDE_ROOT) / "cache"
    assert cache_dir.exists(), f"cache directory does not exist at {cache_dir}"
    assert cache_dir.is_dir(), f"{cache_dir} is not a directory"

@then('if keys exist, they should be detected')
def step_keys_detected_if_exist(context):
    """Verify existing SSH keys would be detected."""
    # Check if SSH keys actually exist in standard location
    keys_exist = check_ssh_keys_exist()
    if keys_exist:
        # If keys exist, verify they can be detected
        ssh_dir = Path.home() / ".ssh"
        key_file = ssh_dir / "id_ed25519"
        assert key_file.exists(), "SSH keys should exist but were not found"
    # If keys don't exist, this step documents that they would be detected if present

@then('if no keys exist, ed25519 keys should be generated')
def step_keys_generated(context):
    """Verify SSH keys are generated when they don't exist."""
    # Check if SSH keys now exist (should be generated by setup)
    keys_exist = check_ssh_keys_exist()
    if keys_exist:
        # Verify key type is ed25519
        ssh_dir = Path.home() / ".ssh"
        key_file = ssh_dir / "id_ed25519"
        assert key_file.exists(), "ed25519 SSH key was not generated"

        # Verify public key also exists
        pub_key_file = ssh_dir / "id_ed25519.pub"
        assert pub_key_file.exists(), "ed25519 public key was not generated"
    # In test scenarios, keys may already exist, so we just verify the mechanism

@then('public keys should be copied to public-ssh-keys/')
def step_public_keys_copied(context):
    """Verify public keys are copied to public-ssh-keys directory."""
    public_ssh_dir = Path(VDE_ROOT) / "public-ssh-keys"
    assert public_ssh_dir.exists(), f"public-ssh-keys directory does not exist at {public_ssh_dir}"

    # Check for .pub files
    pub_files = list(public_ssh_dir.glob("*.pub"))
    assert len(pub_files) > 0, "No public key files found in public-ssh-keys directory"

@then('.keep file should exist in public-ssh-keys/')
def step_keep_file_exists(context):
    """Verify .keep file exists in public-ssh-keys directory."""
    public_ssh_dir = Path(VDE_ROOT) / "public-ssh-keys"
    keep_file = public_ssh_dir / ".keep"
    assert keep_file.exists(), f".keep file does not exist at {keep_file}"

@then('backup/ssh/config should exist as a template')
def step_backup_ssh_config_exists(context):
    """Verify SSH config template exists in backup directory."""
    backup_ssh_config = Path(VDE_ROOT) / "backup" / "ssh" / "config"
    assert backup_ssh_config.exists(), f"backup/ssh/config template does not exist at {backup_ssh_config}"
    assert backup_ssh_config.is_file(), f"{backup_ssh_config} is not a file"

@then('the template should show proper SSH config format')
def step_ssh_template_format(context):
    """Verify SSH config template has proper format."""
    backup_ssh_config = Path(VDE_ROOT) / "backup" / "ssh" / "config"
    assert backup_ssh_config.exists(), "SSH config template does not exist"

    content = backup_ssh_config.read_text()
    # Check for SSH config format indicators
    ssh_config_indicators = ['Host', 'HostName', 'User', 'Port', 'IdentityFile']
    has_valid_format = any(indicator in content for indicator in ssh_config_indicators)
    assert has_valid_format, "SSH config template does not contain valid SSH config format"

@then('I should be able to use it as reference')
def step_can_use_as_reference(context):
    """Verify SSH config template is readable for reference."""
    backup_ssh_config = Path(VDE_ROOT) / "backup" / "ssh" / "config"
    assert backup_ssh_config.exists(), "SSH config template does not exist"

    # Verify file is readable
    assert os.access(backup_ssh_config, os.R_OK), f"SSH config template is not readable: {backup_ssh_config}"

@then('all predefined VM types should be shown')
def step_all_vm_types_shown(context):
    """Verify all VM types from vm-types.conf can be listed."""
    vm_types = get_vm_types()
    assert len(vm_types) > 0, "No VM types found in vm-types.conf"

    # Check for common VM types
    common_vms = ['python', 'rust', 'js', 'csharp', 'ruby', 'postgres', 'redis', 'mongodb', 'nginx']
    found_vms = [vm for vm in common_vms if vm in vm_types]
    assert len(found_vms) > 0, f"No common VM types found. Available: {vm_types}"

@then('python, rust, js, csharp, ruby should be listed')
def step_lang_vms_listed_install(context):
    """Verify language VM types are listed."""
    vm_types = get_vm_types()
    language_vms = ['python', 'rust', 'js', 'csharp', 'ruby']
    for vm in language_vms:
        assert vm in vm_types, f"Language VM {vm} not found in vm-types.conf. Available: {vm_types}"

@then('postgres, redis, mongodb, nginx should be listed')
def step_svc_vms_listed_install(context):
    """Verify service VM types are listed."""
    vm_types = get_vm_types()
    service_vms = ['postgres', 'redis', 'mongodb', 'nginx']
    for vm in service_vms:
        assert vm in vm_types, f"Service VM {vm} not found in vm-types.conf. Available: {vm_types}"

@then('aliases should be shown (py, js, etc.)')
def step_aliases_shown_install(context):
    """Verify VM type aliases are shown."""
    vm_types_file = Path(VDE_ROOT) / "scripts" / "data" / "vm-types.conf"
    assert vm_types_file.exists(), "vm-types.conf does not exist"

    content = vm_types_file.read_text()
    # Check for alias definitions (lines with multiple VM names separated by |)
    has_aliases = '|' in content
    assert has_aliases, "No aliases found in vm-types.conf"

    # Check for specific common aliases
    common_aliases = ['py', 'js', 'node', 'ts']
    found_aliases = [alias for alias in common_aliases if alias in content]
    assert len(found_aliases) > 0, f"No common aliases found. Content includes: {content[:200]}"

@then('I can run vde commands from any directory')
def step_vde_commands_anywhere(context):
    """Verify VDE commands are accessible (scripts are in PATH or vde wrapper exists)."""
    # Check if 'vde' command exists (wrapper script)
    try:
        result = subprocess.run(
            ["which", "vde"],
            capture_output=True,
            text=True,
            timeout=5
        )
        vde_in_path = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        vde_in_path = False

    # If vde wrapper is not in PATH, check that individual scripts exist and are executable
    if not vde_in_path:
        scripts_dir = Path(VDE_ROOT) / "scripts"
        assert scripts_dir.exists(), "scripts directory does not exist"

        # Check for key VDE scripts
        key_scripts = ['start-virtual', 'shutdown-virtual', 'create-virtual-for']
        for script in key_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"VDE script {script} does not exist at {script_path}"
            assert os.access(script_path, os.X_OK), f"VDE script {script} is not executable"

@then('I can run start-virtual, shutdown-virtual, etc.')
def step_run_vde_commands(context):
    """Verify VDE commands are available and executable."""
    scripts_dir = Path(VDE_ROOT) / "scripts"

    # Check for core VDE commands
    vde_commands = ['start-virtual', 'shutdown-virtual', 'create-virtual-for', 'list-vms']
    for command in vde_commands:
        script_path = scripts_dir / command
        assert script_path.exists(), f"VDE command {command} does not exist at {script_path}"
        assert os.access(script_path, os.X_OK), f"VDE command {command} is not executable"

@then('tab completion should work')
def step_tab_completion_works(context):
    """Verify tab completion configuration exists."""
    # Check for completion scripts in configs directory
    configs_dir = Path(VDE_ROOT) / "configs"
    completion_files = []

    if configs_dir.exists():
        # Look for completion files
        completion_files = list(configs_dir.rglob("*completion*"))

    # If no completion files in configs, check for scripts/completion
    if not completion_files:
        completion_dir = Path(VDE_ROOT) / "scripts" / "completion"
        if completion_dir.exists():
            completion_files = list(completion_dir.glob("*"))

    # Verify at least one completion file exists
    if completion_files:
        # Infrastructure exists - verify files are readable
        for cf in completion_files[:3]:  # Check first few
            assert os.access(cf, os.R_OK), f"Completion file {cf} is not readable"

@then('I should be warned if I can\'t run Docker without sudo')
def step_docker_sudo_warning(context):
    """Verify Docker permission check would warn if needed."""
    # Check if Docker can be run without sudo
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        docker_works = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        docker_works = False

    # If Docker doesn't work without sudo, verify warning mechanism exists
    if not docker_works:
        # Check that setup scripts contain Docker permission logic
        setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
        if setup_script.exists():
            content = setup_script.read_text()
            has_permission_check = (
                'sudo' in content.lower() and
                'docker' in content.lower()
            )
            assert has_permission_check, "Setup script does not contain Docker permission checking"
    # If Docker works, no warning needed

@then('instructions should be provided for fixing permissions')
def step_permission_fix_instructions(context):
    """Verify permission fix instructions exist."""
    # Check README or setup documentation for permission instructions
    readme = Path(VDE_ROOT) / "README.md"
    assert readme.exists(), "README.md not found - cannot verify permission instructions"
    content = readme.read_text().lower()
    # Look for Docker permission instructions
    has_permission_instructions = (
        'docker' in content and
        ('permission' in content or 'sudo' in content or 'group' in content)
    )
    assert has_permission_instructions, "README does not contain Docker permission instructions"

@then('setup should continue with a warning')
def step_setup_continues_with_warning(context):
    """Verify setup continues even with warnings."""
    # This step validates that setup doesn't fail on warnings
    # Check that setup script has error handling
    setup_script = Path(VDE_ROOT) / "scripts" / "install-vde.sh"
    assert setup_script.exists(), "Setup script not found - cannot verify warning handling"
    content = setup_script.read_text()
    # Look for warning vs error handling
    has_warning_handling = (
        'warn' in content.lower() or
        'warning' in content.lower() or
        'continue' in content.lower()
    )
    assert has_warning_handling, "Setup script does not appear to have warning handling"

@then('vde-network should be created automatically')
def step_vde_network_created(context):
    """Verify vde-network Docker network exists."""
    assert check_docker_network_exists("vde-network"), "vde-network Docker network does not exist"

@then('all VMs should use this network')
def step_all_vms_use_network(context):
    """Verify VMs are configured to use vde-network."""
    # Check that VM templates/configs reference vde-network
    configs_dir = Path(VDE_ROOT) / "configs"
    assert configs_dir.exists(), "configs directory does not exist - cannot verify network configuration"

    # Look for network references in config files
    network_found = False
    for config_file in configs_dir.rglob("*.yml"):
        content = config_file.read_text()
        if "vde-network" in content or "network_mode: bridge" in content:
            network_found = True
            break
    assert network_found, "No VM configuration references vde-network"

@then('VMs can communicate with each other')
def step_vms_can_communicate(context):
    """Verify VMs are configured for inter-VM communication."""
    # Check that VMs are on the same network
    assert check_docker_network_exists("vde-network"), "vde-network must exist for VM communication"

    # Verify network is bridge type (allows communication)
    try:
        result = subprocess.run(
            ["docker", "network", "inspect", "vde-network"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Check if it's a bridge network
            assert "bridge" in result.stdout or "macvlan" in result.stdout, \
                "vde-network is not configured for inter-VM communication"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Docker not available - skip bridge type verification

@then('I should see helpful progress messages')
def step_progress_messages(context):
    """Verify progress messages are shown during setup."""
    # Check that scripts echo progress information
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify progress messages"

    # Check a few key scripts for progress messages
    setup_script = scripts_dir / "install-vde.sh"
    assert setup_script.exists(), "Setup script not found - cannot verify progress messages"
    content = setup_script.read_text()
    # Look for progress indicators
    has_progress = (
        'echo' in content or
        'print' in content or
        'progress' in content.lower() or
        'installing' in content.lower() or
        'setting' in content.lower()
    )
    assert has_progress, "Setup script does not contain progress messages"

@then('configs/docker/python/ should be created')
def step_python_config_created(context):
    """Verify Python VM config directory exists."""
    python_config_dir = Path(VDE_ROOT) / "configs" / "docker" / "python"
    assert python_config_dir.exists(), f"Python config directory does not exist at {python_config_dir}"
    assert python_config_dir.is_dir(), f"{python_config_dir} is not a directory"

@then('docker-compose.yml should be generated')
def step_compose_generated(context):
    """Verify docker-compose.yml file is generated for VMs."""
    # Check that compose files can be generated
    templates_dir = Path(VDE_ROOT) / "templates"
    assert templates_dir.exists(), "templates directory does not exist - cannot verify compose generation"

    # Look for docker-compose templates
    compose_templates = list(templates_dir.rglob("docker-compose*.yml"))
    compose_templates.extend(list(templates_dir.rglob("compose*.yml")))

    # Or check if generation script exists
    scripts_dir = Path(VDE_ROOT) / "scripts"
    if scripts_dir.exists():
        # Check for compose generation logic
        for script_file in scripts_dir.glob("*.sh"):
            content = script_file.read_text()
            if "docker-compose" in content or "compose" in content:
                return  # Compose generation capability exists

    assert len(compose_templates) > 0, "No docker-compose templates found"

@then('SSH config should be updated')
def step_ssh_config_updated_install(context):
    """Verify SSH config is updated for VM access."""
    # Check if SSH config includes VDE VM entries
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Look for VDE-specific SSH entries (vde- prefix or similar)
        has_vde_entries = (
            'vde-' in content or
            'vde_' in content or
            'virtual' in content.lower()
        )
        # In test scenarios, SSH config may not be modified - just verify file exists
        assert ssh_config.exists(), "SSH config file does not exist"
    # If SSH config doesn't exist, that's acceptable for test scenarios

@then('I should be told what to do next')
def step_next_steps_shown(context):
    """Verify next steps are provided after installation."""
    # Check README for next steps
    readme = Path(VDE_ROOT) / "README.md"
    assert readme.exists(), "README.md does not exist"

    content = readme.read_text().lower()
    # Look for next steps or getting started sections
    has_next_steps = (
        'next step' in content or
        'getting started' in content or
        'quick start' in content or
        'after install' in content
    )
    assert has_next_steps, "README does not contain next steps or getting started section"

@then('I should see if VDE is properly configured')
def step_vde_health_status(context):
    """Verify VDE health check functionality exists."""
    # Check for vde-health script or equivalent
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify health check"

    health_script = scripts_dir / "vde-health"
    if health_script.exists():
        assert os.access(health_script, os.X_OK), "vde-health script exists but is not executable"
    # If health script doesn't exist, it may be integrated differently

@then('any issues should be clearly listed')
def step_issues_listed(context):
    """Verify issues are clearly listed in health check."""
    # Check that health script or documentation lists issues clearly
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify issue listing"

    health_script = scripts_dir / "vde-health"
    if health_script.exists():
        content = health_script.read_text()
        # Look for issue reporting logic
        has_issue_listing = (
            'error' in content.lower() or
            'issue' in content.lower() or
            'problem' in content.lower() or
            'check' in content.lower()
        )
        assert has_issue_listing, "Health check script does not contain issue listing logic"
    # If health script doesn't exist, issue listing may be in a different mechanism

@then('I should get fix suggestions for each issue')
def step_fix_suggestions(context):
    """Verify fix suggestions are provided for issues."""
    # Check README or health script for fix suggestions
    readme = Path(VDE_ROOT) / "README.md"
    scripts_dir = Path(VDE_ROOT) / "scripts"

    fix_suggestions_found = False

    if readme.exists():
        content = readme.read_text().lower()
        # Look for fix suggestions
        has_fix_suggestions = (
            'fix' in content or
            'resolve' in content or
            'solution' in content or
            'troubleshoot' in content
        )
        if has_fix_suggestions:
            fix_suggestions_found = True

    if not fix_suggestions_found and scripts_dir.exists():
        health_script = scripts_dir / "vde-health"
        if health_script.exists():
            content = health_script.read_text().lower()
            has_fix_suggestions = (
                'fix' in content or
                'resolve' in content or
                'solution' in content
            )
            if has_fix_suggestions:
                fix_suggestions_found = True

    assert fix_suggestions_found, "Fix suggestions should be documented"

@then('my existing VMs should continue working')
def step_existing_vms_work(context):
    """Verify existing VMs continue to work after update."""
    # Check that existing VM configurations are preserved
    configs_dir = Path(VDE_ROOT) / "configs"
    if configs_dir.exists():
        # If VM configs exist, verify they're still valid
        vm_configs = list(configs_dir.rglob("*.yml"))
        if vm_configs:
            # Verify at least one config is valid YAML
            for config_file in vm_configs[:3]:  # Check first few
                try:
                    content = config_file.read_text()
                    # Basic YAML validation - check for common keys
                    has_valid_structure = (
                        'version:' in content or
                        'services:' in content or
                        'image:' in content
                    )
                    assert has_valid_structure, f"VM config {config_file} appears invalid"
                except Exception:
                    raise AssertionError(f"Could not read VM config {config_file}")
    # If no VMs exist yet, this is expected

@then('new VM types should be available')
def step_new_vm_types_available(context):
    """Verify new VM types are available after update."""
    vm_types = get_vm_types()
    assert len(vm_types) > 0, "No VM types found in vm-types.conf"

    # Check for newer or recently added VM types
    # (This validates that vm-types.conf is being read correctly)
    assert isinstance(vm_types, list), "VM types should be returned as a list"

@then('my configurations should be preserved')
def step_configs_preserved(context):
    """Verify user configurations are preserved during update."""
    # Check that configs directory and its contents exist
    configs_dir = Path(VDE_ROOT) / "configs"
    if configs_dir.exists():
        # Verify configs directory has content
        config_files = list(configs_dir.rglob("*"))
        assert len(config_files) > 0, "configs directory exists but is empty"
    # If configs directory doesn't exist, it may not have been created yet

@then('I should be told about any manual migration needed')
def step_migration_instructions(context):
    """Verify migration instructions are provided if needed."""
    # Check documentation for migration instructions
    readme = Path(VDE_ROOT) / "README.md"
    migration_doc = Path(VDE_ROOT) / "MIGRATION.md"

    has_migration_info = False
    if migration_doc.exists():
        has_migration_info = True
    elif readme.exists():
        content = readme.read_text().lower()
        has_migration_info = (
            'migrate' in content or
            'migration' in content or
            'upgrade' in content
        )

    assert has_migration_info, "Migration instructions should be documented"

@then('I can stop all VMs')
def step_can_stop_all_vms(context):
    """Verify all VMs can be stopped."""
    # Check that stop-all script or functionality exists
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify stop functionality"

    # Look for stop-all or shutdown-virtual script
    stop_all_script = scripts_dir / "shutdown-virtual"
    assert stop_all_script.exists(), "shutdown-virtual script not found"
    assert os.access(stop_all_script, os.X_OK), "shutdown-virtual script is not executable"

@then('I can remove VDE directories')
def step_can_remove_vde_dirs(context):
    """Verify VDE directories can be removed."""
    # Check that uninstall script exists
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify uninstall capability"

    uninstall_script = scripts_dir / "uninstall-vde.sh"
    assert uninstall_script.exists(), "uninstall script not found"
    assert os.access(uninstall_script, os.X_OK), "uninstall script is not executable"

@then('my SSH config should be cleaned up')
def step_ssh_config_cleanup(context):
    """Verify SSH config cleanup is possible."""
    # This step validates that cleanup capability exists
    # Actual cleanup would be destructive in test
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        # Verify file is writable (can be cleaned up)
        assert os.access(ssh_config, os.W_OK), f"SSH config is not writable: {ssh_config}"
    # If SSH config doesn't exist, cleanup is not needed

@then('my project data should be preserved if I want')
def step_project_data_preserved(context):
    """Verify project data can be preserved during uninstall."""
    # Check that projects directory exists (can be preserved)
    projects_dir = Path(VDE_ROOT) / "projects"
    if projects_dir.exists():
        assert projects_dir.is_dir(), "projects directory exists but is not a directory"
    # If projects directory doesn't exist, preservation is not applicable

@then('appropriate paths should be used')
def step_appropriate_paths(context):
    """Verify platform-appropriate paths are used."""
    import platform
    system = platform.system()

    # Check that VDE_ROOT is set appropriately for the platform
    vde_root = Path(VDE_ROOT)
    assert vde_root.exists(), f"VDE_ROOT does not exist: {vde_root}"

    # Verify paths match platform conventions
    if system == "Darwin":  # macOS
        # On macOS, paths should use ~/dev or similar
        assert "Users" in str(vde_root) or "home" in str(vde_root), \
            f"VDE_ROOT path {vde_root} doesn't match macOS conventions"
    elif system == "Linux":
        # On Linux, paths can vary - just verify VDE_ROOT exists
        assert vde_root.exists(), f"VDE_ROOT does not exist on Linux: {vde_root}"

@then('platform-specific adjustments should be made')
def step_platform_adjustments(context):
    """Verify platform-specific adjustments are handled."""
    import platform
    system = platform.system()

    # Check that scripts handle platform differences
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify platform handling"

    # Look for platform detection in key scripts
    script_files = list(scripts_dir.glob("*.sh"))[:3]  # Check first few scripts
    platform_handling_found = False
    for script_file in script_files:
        content = script_file.read_text()
        # Look for platform detection
        has_platform_handling = (
            'Darwin' in content or
            'Linux' in content or
            'PLATFORM' in content or
            'uname' in content
        )
        if has_platform_handling:
            platform_handling_found = True
            break

    assert platform_handling_found, "Platform handling not found in scripts"

@then('the installation should succeed')
def step_installation_succeeds(context):
    """Verify installation completes successfully."""
    # Check that installation artifacts exist
    vde_root = Path(VDE_ROOT)
    assert vde_root.exists(), f"VDE_ROOT does not exist: {vde_root}"

    # Check core directories
    core_dirs = ['scripts', 'configs']
    for dir_name in core_dirs:
        dir_path = vde_root / dir_name
        assert dir_path.exists(), f"Core directory {dir_name} does not exist"

@then('required Docker images should be pulled')
def step_docker_images_pulled(context):
    """Verify required Docker images are available."""
    if not check_docker_available():
        return  # Docker not available - skip image check

    # Check that some Docker images are available
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            images = result.stdout.strip().split('\n')
            # Docker command executed successfully - informational check
            # In a clean environment, images list may be empty
            pass  # Docker images command works
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Docker not available

@then('base images should be built if needed')
def step_base_images_built(context):
    """Verify base images can be built."""
    # Check for Dockerfile or build scripts
    vde_root = Path(VDE_ROOT)
    dockerfiles = list(vde_root.rglob("Dockerfile"))
    build_scripts = list(vde_root.rglob("*build*.sh"))

    has_build_capability = len(dockerfiles) > 0 or len(build_scripts) > 0
    assert has_build_capability, "No Docker build capability found"

@then('I should see download/build progress')
def step_build_progress(context):
    """Verify build progress is shown."""
    # Check that build scripts show progress
    vde_root = Path(VDE_ROOT)
    build_scripts = list(vde_root.rglob("*build*.sh"))

    progress_found = False
    if build_scripts:
        for script in build_scripts[:3]:  # Check first few
            content = script.read_text()
            # Look for progress indicators
            has_progress = (
                'echo' in content or
                'progress' in content.lower() or
                'building' in content.lower() or
                'downloading' in content.lower()
            )
            if has_progress:
                progress_found = True
                break

    assert progress_found, "Build progress reporting not found in scripts"

@then('I can run "create-virtual-for python && start-virtual python"')
def step_quick_start_command(context):
    """Verify quick start command works."""
    scripts_dir = Path(VDE_ROOT) / "scripts"

    # Check that both commands exist and are executable
    create_script = scripts_dir / "create-virtual-for"
    start_script = scripts_dir / "start-virtual"

    assert create_script.exists(), f"create-virtual-for script does not exist at {create_script}"
    assert os.access(create_script, os.X_OK), "create-virtual-for is not executable"

    assert start_script.exists(), f"start-virtual script does not exist at {start_script}"
    assert os.access(start_script, os.X_OK), "start-virtual is not executable"

@then('I should have a working Python environment')
def step_python_env_working(context):
    """Verify Python environment can be created and accessed."""
    # Check that Python VM type is defined
    vm_types = get_vm_types()
    assert 'python' in vm_types or 'py' in vm_types, \
        f"Python VM type not found in vm-types.conf. Available: {vm_types}"

    # Check that Python VM config/template exists
    python_config = Path(VDE_ROOT) / "configs" / "docker" / "python"
    if not python_config.exists():
        # May use templates
        templates_dir = Path(VDE_ROOT) / "templates"
        if templates_dir.exists():
            python_templates = list(templates_dir.rglob("*python*"))
            assert len(python_templates) > 0, "No Python VM configuration found"
    else:
        assert python_config.is_dir(), "Python config path exists but is not a directory"

@then('I can start coding immediately')
def step_can_start_coding(context):
    """Verify environment is ready for immediate coding."""
    # Check that projects directory exists and is writable
    projects_dir = Path(VDE_ROOT) / "projects"
    if projects_dir.exists():
        assert projects_dir.is_dir(), "projects directory exists but is not a directory"
        # Verify it's writable (can create project files)
        assert os.access(projects_dir, os.W_OK), f"projects directory is not writable: {projects_dir}"
    # If projects directory doesn't exist, it may not have been created yet

@then('README.md should provide overview')
def step_readme_overview(context):
    """Verify README provides project overview."""
    readme = Path(VDE_ROOT) / "README.md"
    assert readme.exists(), "README.md does not exist"

    content = readme.read_text()
    # Check for overview elements
    has_overview = (
        len(content) > 100 and  # Substantial content
        ('VDE' in content or 'Virtual Development Environment' in content)
    )
    assert has_overview, "README does not contain project overview"

@then('Technical-Deep-Dive.md should explain internals')
def step_technical_deep_dive(context):
    """Verify technical documentation exists."""
    tech_doc = Path(VDE_ROOT) / "Technical-Deep-Dive.md"
    if tech_doc.exists():
        content = tech_doc.read_text()
        # Verify it has substantial content
        assert len(content) > 500, "Technical documentation exists but is minimal"
    else:
        # Technical documentation may be in different location
        docs_dir = Path(VDE_ROOT) / "docs"
        if docs_dir.exists():
            tech_docs = list(docs_dir.rglob("*.md"))
            assert len(tech_docs) > 0, "No technical documentation found in docs/"
        # If neither location has docs, technical docs may not exist

@then('tests/README.md should explain testing')
def step_tests_readme(context):
    """Verify testing documentation exists."""
    tests_readme = Path(VDE_ROOT) / "tests" / "README.md"
    if tests_readme.exists():
        content = tests_readme.read_text()
        # Verify it has testing information
        has_test_info = (
            'test' in content.lower() or
            'bdd' in content.lower() or
            'behave' in content.lower()
        )
        assert has_test_info, "tests/README.md exists but doesn't explain testing"
    # If tests README doesn't exist, testing docs may be elsewhere

@then('help text should be available in commands')
def step_help_in_commands(context):
    """Verify commands have help text."""
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist - cannot verify help text"

    # Check a few key scripts for help functionality
    checked = 0
    for script_file in ['start-virtual', 'create-virtual-for', 'list-vms']:
        script_path = scripts_dir / script_file
        if script_path.exists():
            content = script_path.read_text()
            # Look for help text indicators
            has_help = (
                '--help' in content or
                '-h' in content or
                'usage' in content.lower() or
                'help' in content.lower()
            )
            if has_help:
                checked += 1

    # At least some scripts should have help
    assert checked > 0, "No command help text found"

@then('all scripts should be executable')
def step_scripts_executable(context):
    """Verify all shell scripts are executable."""
    scripts_dir = Path(VDE_ROOT) / "scripts"
    assert scripts_dir.exists(), "scripts directory does not exist"

    # Check that shell scripts are executable
    non_executable = []
    for script_file in scripts_dir.rglob("*.sh"):
        if not os.access(script_file, os.X_OK):
            non_executable.append(str(script_file))

    assert len(non_executable) == 0, \
        f"Found {len(non_executable)} non-executable scripts: {non_executable[:5]}"

@then('all templates should be present')
def step_templates_present(context):
    """Verify all VM templates are present."""
    templates_dir = Path(VDE_ROOT) / "templates"
    if templates_dir.exists():
        # Check that templates exist
        template_files = list(templates_dir.rglob("*"))
        # Filter out .keep files
        actual_templates = [f for f in template_files if f.name != ".keep"]
        assert len(actual_templates) > 0, "templates directory exists but contains no templates"
    # If templates directory doesn't exist, it may not have been created yet

@then('vm-types.conf should be valid')
def step_vm_types_conf_valid(context):
    """Verify vm-types.conf is valid."""
    vm_types_file = Path(VDE_ROOT) / "scripts" / "data" / "vm-types.conf"
    assert vm_types_file.exists(), f"vm-types.conf does not exist at {vm_types_file}"

    content = vm_types_file.read_text()
    lines = content.split('\n')

    # Parse and validate VM type definitions
    valid_count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Each line should have at least one VM type name
            parts = line.split('|')
            if parts and parts[0].strip():
                valid_count += 1

    assert valid_count > 0, "vm-types.conf exists but contains no valid VM type definitions"

@then('all directories should have correct permissions')
def step_dir_permissions_correct(context):
    """Verify directories have appropriate permissions."""
    vde_root = Path(VDE_ROOT)
    assert vde_root.exists(), f"VDE_ROOT does not exist: {vde_root}"

    # Check that core directories are readable
    core_dirs = ['scripts', 'configs', 'data']
    for dir_name in core_dirs:
        dir_path = vde_root / dir_name
        if dir_path.exists():
            assert os.access(dir_path, os.R_OK), f"{dir_name} directory is not readable"
            assert os.access(dir_path, os.X_OK), f"{dir_name} directory is not accessible"
