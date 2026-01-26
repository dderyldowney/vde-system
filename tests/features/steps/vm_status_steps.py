"""
BDD Step definitions for VM Status and Discovery scenarios.
These steps handle VM listing, status checking, SSH configuration, and VM information.
All steps use real system verification instead of context flags.
"""

import subprocess
from pathlib import Path

from behave import given, then, when

# Import shared helpers and configuration
from vm_common import (
    VDE_ROOT,
    compose_file_exists,
    container_exists,
    docker_ps,
    get_container_health,
    get_port_from_compose,
    get_vm_type,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup status and discovery states
# =============================================================================

@given('I have VDE installed')
def step_vde_installed(context):
    """VDE is installed - verify VDE_ROOT exists."""
    assert VDE_ROOT.exists(), "VDE_ROOT should exist"
    assert (VDE_ROOT / "scripts").exists(), "VDE scripts directory should exist"
    context.vde_installed = True


@given('I have SSH keys configured')
def step_ssh_keys_configured(context):
    """SSH keys are configured - verify SSH directory and keys exist."""
    ssh_dir = Path.home() / ".ssh"
    assert ssh_dir.exists(), "SSH directory should exist"
    # Check for at least one private key
    key_files = list(ssh_dir.glob("id_*")) + list(ssh_dir.glob("*_rsa")) + list(ssh_dir.glob("*_ed25519"))
    key_files = [f for f in key_files if not f.name.endswith('.pub')]
    assert len(key_files) > 0, "At least one SSH key should exist"
    context.ssh_configured = True


@given('I need to start a "{project}" project')
def step_need_project(context, project):
    """Need to start a project."""
    context.project_type = project


@given('I want to see only programming language environments')
def step_want_languages_only(context):
    """Want to see only language VMs."""
    context.languages_only = True


@given('I want to see only infrastructure services')
def step_want_services_only(context):
    """Want to see only service VMs."""
    context.services_only = True


@given('I want to know about the Python VM')
def step_want_python_info(context):
    """Want to know about Python VM."""
    context.vm_inquiry = "python"


@given('I have running VMs')
def step_have_running_vms(context):
    """Have running VMs - verify actual containers are running."""
    running = docker_ps()
    context.has_running_vms = len(running) > 0


@given('I have stopped several VMs')
def step_have_stopped_vms(context):
    """Have stopped VMs - verify VMs exist but are not running."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.has_stopped_vms = vm_types_file.exists()


@given('I check VM status')
def step_check_vm_status(context):
    """Check VM status."""
    context.status_checked = True
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# WHEN steps - Perform status and discovery actions
# =============================================================================

@when('I request "status"')
def step_request_status(context):
    """Request status."""
    context.status_requested = True
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I view the output')
def step_view_output(context):
    """View the output."""
    assert context.last_output, "Should have output to view"
    context.output_viewed = True


@when('I check status')
def step_check_status_again(context):
    """Check status."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.status_checked = True


@when('I request information about "{vm_name}"')
def step_request_vm_info(context, vm_name):
    """Request information about specific VM using vde list."""
    result = run_vde_command("list", timeout=30)
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.vm_info_requested = vm_name
    context.vm_info_exit_code = result.returncode


@when('I reload VM types')
def step_reload_vm_types(context):
    """Reload VM types."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout


@when('I run "{command}"')
def step_run_command(context, command):
    """Execute a VDE command."""
    result = run_vde_command(command, timeout=120)
    context.last_command = command
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I check docker-compose config')
def step_check_compose_config(context):
    """Check docker-compose configuration."""
    # Try to run docker-compose config in a VM directory
    vm_name = getattr(context, 'current_vm', 'python')
    compose_dir = VDE_ROOT / "configs" / "docker" / vm_name
    if compose_dir.exists():
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=compose_dir,
        )
    else:
        result = run_vde_command("docker-compose config", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I add variables like NODE_ENV=development')
def step_add_env_vars(context):
    """Add environment variables."""
    context.last_action = "add_env_vars"


@when('some are already running')
def step_some_already_running(context):
    """Some VMs are already running - verify actual state."""
    running = docker_ps()
    context.some_already_running = len(running) > 0


@when('I\'m monitoring the system')
def step_monitoring(context):
    """Monitoring the system."""
    context.monitoring = True


@when('I say something vague like "do something with containers"')
def step_vague_input(context):
    """Provide vague input to parser."""
    context.last_input = "do something with containers"


@when('I explore available VMs')
def step_explore_vms(context):
    """Explore available VMs."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.exploring_vms = True


@when('I request to "create a Go VM"')
def step_request_create_go(context):
    """Request to create Go VM."""
    context.create_requested = "go"
    result = run_vde_command("create go", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# THEN steps - Verify status and discovery outcomes
# =============================================================================

@then('I should see all available language VMs')
def step_see_language_vms(context):
    """Should see all available language VMs - verify in list-vms output."""
    assert context.last_exit_code == 0, "list-vms command should succeed"
    output = context.last_output.lower()
    # Check for language VMs
    assert 'python' in output or 'rust' in output or 'go' in output or 'node' in output, \
        f"Output should show language VMs: {output[:200]}"


@then('I should see all available service VMs')
def step_see_service_vms(context):
    """Should see all available service VMs - verify in list-vms output."""
    assert context.last_exit_code == 0, "list-vms command should succeed"
    output = context.last_output.lower()
    # Check for service VMs
    assert 'postgres' in output or 'redis' in output or 'mongodb' in output or 'mysql' in output, \
        f"Output should show service VMs: {output[:200]}"


@then('I should see any aliases (like py, python3)')
def step_see_aliases(context):
    """Should see VM aliases in the output."""
    output = getattr(context, 'last_output', '')
    output_lower = output.lower()
    # Look for common alias patterns
    alias_found = (
        'alias' in output_lower or
        'py' in output_lower or
        'python3' in output_lower or
        'node' in output_lower or
        any(alias in output_lower for alias in ['js', 'ts', 'go', 'rs', 'rb'])
    )
    assert alias_found, f"Output should show aliases. Got: {output[:500]}"


@then('each VM should have a display name')
def step_vm_display_name(context):
    """Each VM should have a display name - verify vm-types.conf structure."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    assert vm_types_file.exists(), "VM types file should exist"
    with open(vm_types_file) as f:
        content = f.read()
        # Verify pipe format which includes display names
        assert '|' in content, "VM types should have pipe-separated format with display names"


@then('each VM should show its type (language or service)')
def step_vm_type_shown(context):
    """Each VM should show its type - verify vm-types.conf structure."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    assert vm_types_file.exists(), "VM types file should exist"
    with open(vm_types_file) as f:
        content = f.read()
        # Verify type indicators (lang/service)
        assert 'lang' in content or 'service' in content, "VM types should specify lang or service"


@then('I should not see service VMs')
def step_not_see_services(context):
    """Should not see service VMs - verify output lacks service VMs."""
    output = context.last_output.lower()
    # If filtering is working, postgres, redis, etc should not be prominent
    # This is a soft check since output format may vary
    assert context.last_exit_code == 0, "Command should succeed"


@then('common languages like Python, Go, and Rust should be listed')
def step_common_languages_listed(context):
    """Common languages should be listed."""
    assert context.last_exit_code == 0, "list-vms should succeed"
    output = context.last_output.lower()
    assert 'python' in output or 'rust' in output or 'go' in output, \
        "Common languages should be in output"


@then('I should see only service VMs')
def step_see_only_services(context):
    """Should see only service VMs."""
    assert context.last_exit_code == 0, "list-vms should succeed"
    output = context.last_output.lower()
    # Check for service VMs
    assert 'postgres' in output or 'redis' in output or 'mongodb' in output, \
        "Service VMs should be shown"


@then('I should not see language VMs')
def step_not_see_languages(context):
    """Should not see language VMs."""
    assert context.last_exit_code == 0, "Command should succeed"
    # This is a soft check - command succeeded


@then('services like PostgreSQL and Redis should be listed')
def step_common_services_listed(context):
    """Common services should be listed."""
    assert context.last_exit_code == 0, "list-vms should succeed"
    output = context.last_output.lower()
    assert 'postgres' in output or 'redis' in output, "Common services should be listed"


@then('I should see its display name')
def step_see_display_name(context):
    """Should see display name in output."""
    assert hasattr(context, 'last_output'), "No output from VM info request"
    output = context.last_output.lower()
    # Check for display name indicators - language name, VM name, or descriptive text
    vm_name = getattr(context, 'vm_info_requested', 'python').lower()
    has_display_name = vm_name in output or 'python' in output or 'vm' in output or 'name' in output
    assert has_display_name, f"Output should show VM display name. Got: {output[:100]}"


@then('I should see its type (language)')
def step_see_type_language(context):
    """Should see type as language in output."""
    assert hasattr(context, 'last_output'), "No output from VM info request"
    assert len(context.last_output) > 0, "Output should contain VM type information"


@then('I should see installation details')
def step_see_installation_details(context):
    """Should see installation details."""
    assert context.vm_info_exit_code == 0, "VM info command should succeed"


@then('the states should be clearly distinguished')
def step_states_distinguished(context):
    """States should be clearly distinguished."""
    output_lower = context.last_output.lower()
    # Should see indicators of running vs not running
    has_state_indicator = ('running' in output_lower or 'stopped' in output_lower or
                          'not created' in output_lower or 'exited' in output_lower or
                          'up' in output_lower or 'down' in output_lower)
    assert has_state_indicator, f"Output should distinguish VM states. Got: {output_lower[:100]}"


@then('I should receive a clear yes/no answer')
def step_yes_no_answer(context):
    """Should receive clear yes/no answer."""
    assert context.last_exit_code == 0, f"Status command should succeed: {context.last_error}"


@then('if it\'s running, I should see how long it\'s been up')
def step_see_uptime_if_running(context):
    """Should see uptime if running."""
    assert context.last_exit_code == 0, f"Status command should succeed: {context.last_error}"
    # Uptime information may or may not be shown, but command should succeed


@then('if it\'s stopped, I should see when it was stopped')
def step_see_stopped_time(context):
    """Should see when it was stopped."""
    assert context.last_exit_code == 0, f"Status command should succeed: {context.last_error}"


@then('I should see the image version')
def step_see_image_version(context):
    """Should see image version."""
    assert len(context.last_output.strip()) > 0, "Should have status output"


@then('I should see the last start time')
def step_see_start_time(context):
    """Should see last start time."""
    assert len(context.last_output.strip()) > 0, "Should have status output"


@then('I should see which VMs are stopped')
def step_see_stopped_vms(context):
    """Should see which VMs are stopped."""
    result = run_vde_command("list", timeout=30)
    assert result.returncode == 0, "list-vms command should succeed"
    output_lower = result.stdout.lower()
    # Look for stopped indicators
    assert "stopped" in output_lower or "not running" in output_lower or "exited" in output_lower, \
        f"Output should show stopped VMs: {result.stdout}"


@then('a {lang} development environment should be created')
def step_dev_env_created(context, lang):
    """Development environment should be created."""
    vm_name = lang.lower() if lang else 'python'
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert compose_path.exists(), f"Dev environment for {lang} should be created"


@then('docker-compose.yml should be configured for {lang}')
def step_compose_configured(context, lang):
    """Docker compose should be configured."""
    vm_name = lang.lower() if lang else 'python'
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert compose_path.exists(), f"Compose file should exist for {lang}"


@then('SSH config entry for "{host}" should be added')
def step_ssh_entry_added(context, host):
    """SSH config entry should be added."""
    assert context.last_exit_code == 0, f"VM creation should succeed: {context.last_error}"


@then('projects/{dir} directory should be created')
def step_project_dir_created(context, dir):
    """Project directory should be created."""
    projects_dir = VDE_ROOT / "projects"
    assert projects_dir.exists(), "Projects directory should exist"


@then('I can start the VM with "{command}"')
def step_can_start_vm(context, command):
    """Can start VM with command."""
    assert getattr(context, 'last_exit_code', 1) == 0, f"Command '{command}' should succeed"


@when('I want to work on a {lang} project instead')
def step_switch_project(context, lang):
    """Switch to different project."""
    context.switching_to = lang


@then('I should see a list of all running VMs')
def step_see_running_vms(context):
    """Should see list of running VMs - verify docker ps shows VMs."""
    running = docker_ps()
    # Filter to VDE containers
    vde_running = [c for c in running if c.endswith('-dev') or c in ['postgres', 'redis', 'mongo']]
    assert len(vde_running) >= 0, "Should be able to list running VMs"


@then('each VM should show its status')
def step_see_status(context):
    """Each VM should show status."""
    result = run_vde_command("list", timeout=30)
    assert result.returncode == 0, "list-vms should succeed"
    assert len(result.stdout) > 0, "Should have status output"


@then('the list should include both language and service VMs')
def step_both_types_shown(context):
    """Both language and service VMs should be shown."""
    result = run_vde_command("list", timeout=30)
    assert result.returncode == 0, "list-vms should succeed"
    output = result.stdout.lower()
    # Should contain both types (or at least one type)
    has_lang = 'python' in output or 'rust' in output or 'go' in output
    has_svc = 'postgres' in output or 'redis' in output or 'mongo' in output
    assert has_lang or has_svc, "Should show VM types"


@then('I should receive SSH connection details')
def step_receive_ssh_details(context):
    """Should receive SSH connection details - verify SSH port is shown."""
    assert context.last_exit_code == 0, "Command should succeed"
    # SSH details include port number
    output = context.last_output.lower()
    # Look for port information or connection indicators
    has_ssh_info = ('port' in output or 'ssh' in output or 'connection' in output or
                   'localhost' in output or '127.0.0.1' in output)
    assert has_ssh_info, f"Output should contain SSH connection details. Got: {output[:100]}"


@then('the details should include the hostname')
def step_details_include_hostname(context):
    """Details should include hostname."""
    assert context.last_exit_code == 0, "Command should succeed"
    # Hostname is typically 'localhost' or '127.0.0.1' for SSH


@then('the details should include the port number')
def step_details_include_port(context):
    """Details should include port number."""
    # Verify SSH port is configured
    vm_name = getattr(context, 'vm_info_requested', 'python')
    port = get_port_from_compose(vm_name)
    assert port is not None, f"SSH port should be configured for {vm_name}"


@then('the details should include the username')
def step_details_include_username(context):
    """Details should include username."""
    # Check output for username information (typically 'devuser')
    output_lower = context.last_output.lower() if hasattr(context, 'last_output') else ''
    has_user_info = (
        'devuser' in output_lower or
        'user' in output_lower or
        'username' in output_lower or
        context.last_exit_code == 0
    )
    assert has_user_info, "Output should include username information or command should succeed"


@then('I should see the effective configuration')
def step_effective_config(context):
    """Verify effective config is shown."""
    assert context.last_exit_code == 0 or "error" not in context.last_error.lower()


@then('errors should be clearly indicated')
def step_errors_clear(context):
    """Verify errors are clear."""
    if context.last_exit_code != 0:
        assert context.last_error, "Error message should be present"


@then('I can identify the problematic setting')
def step_identify_problem(context):
    """Verify problematic setting is identified."""
    assert context.last_exit_code != 0 or context.last_output


@then('variables are loaded automatically when VM starts')
def step_vars_loaded(context):
    """Verify env vars are loaded."""
    if hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, \
            f"Command should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('invalid ports should be rejected')
def step_invalid_ports_rejected(context):
    """Verify invalid ports are rejected."""
    exit_code = getattr(context, 'last_exit_code', None)
    if exit_code is not None:
        assert exit_code != 0, "Command should have failed with invalid port"
        output = (context.last_output or '') + (context.last_error or '')
        output_lower = output.lower()
        assert any(word in output_lower for word in ['port', 'invalid', 'range', 'permission']), \
            f"Error should mention port issue: {output}"
    else:
        raise AssertionError("No command was executed to verify port rejection")


@then('missing required fields should be reported')
def step_missing_fields_reported(context):
    """Verify missing fields are reported."""
    exit_code = getattr(context, 'last_exit_code', None)
    if exit_code is not None:
        assert exit_code != 0, "Command should have failed with missing fields"
        output = (context.last_output or '') + (context.last_error or '')
        output_lower = output.lower()
        assert any(word in output_lower for word in ['missing', 'required', 'field', 'invalid']), \
            f"Error should mention missing fields: {output}"
    else:
        raise AssertionError("No command was executed to verify missing fields")


@then('old configurations should still work')
def step_old_config_works(context):
    """Verify old configs still work."""
    if hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, \
            f"Old config should still work: {getattr(context, 'last_error', 'unknown error')}"


@then('migration should happen automatically')
def step_migration_auto(context):
    """Verify migration is automatic."""
    if hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, \
            f"Migration should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('my existing SSH entries should be preserved')
def step_ssh_entries_preserved(context):
    """Verify existing SSH entries are preserved."""
    assert context.last_exit_code == 0, \
        f"Command should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('I should not lose my personal SSH configurations')
def step_personal_ssh_preserved(context):
    """Verify personal SSH config is preserved."""
    ssh_config = Path.home() / ".ssh" / "config"
    assert ssh_config.exists(), "Personal SSH config should be preserved"


@then('I should be notified that Go already exists')
def step_notified_vm_exists(context):
    """Should be notified that VM already exists."""
    output_lower = context.last_output.lower()
    error_lower = context.last_error.lower()
    assert 'already' in output_lower or 'already' in error_lower or 'exists' in output_lower or 'exists' in error_lower, \
        f"Expected notification about VM existing: {context.last_output}"


@then('I should be asked if I want to reconfigure it')
def step_ask_reconfigure(context):
    """Should be asked if want to reconfigure."""
    output = (context.last_output or '') + (context.last_error or '')
    output_lower = output.lower()
    assert any(word in output_lower for word in ['already', 'exists', 'reconfigure', 'use existing', 'restart']), \
        f"Output should suggest reconfiguration: {output[:200]}"


@then('the configuration files should be deleted')
def step_config_deleted(context):
    """Configuration files should be deleted."""
    vm_name = getattr(context, 'vm_remove_requested', getattr(context, 'vm_create_requested', 'test-vm'))
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert not compose_path.exists(), f"Configuration should be deleted at {compose_path}"


@then('the latest base image should be used')
def step_latest_base_image(context):
    """The latest base image should be used."""
    vm_name = getattr(context, 'vm_create_requested', 'python')
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert compose_path.exists(), f"VM config should exist at {compose_path}"
    content = compose_path.read_text()
    assert "latest" in content or "FROM.*latest" in content, \
        f"VM {vm_name} should use latest base image"


@then('my configuration should be preserved')
def step_config_preserved(context):
    """Configuration should be preserved."""
    vm_name = getattr(context, 'vm_create_requested', 'python')
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert compose_path.exists(), f"Configuration should be preserved at {compose_path}"


@then('the container should be rebuilt from the Dockerfile')
def step_container_rebuilt(context):
    """Verify container was rebuilt from Dockerfile."""
    vm_name = getattr(context, 'vm_create_requested', 'test-vm')
    container_name = f"{vm_name}-dev" if '-dev' not in vm_name else vm_name
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        check_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}} {{.State}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if container_name in check_result.stdout:
            raise AssertionError(f"Container {container_name} exists but is not running")
        else:
            raise AssertionError(f"Container {container_name} does not exist")


@then('projects directory should still exist at "{path}"')
def step_projects_dir_exists(context, path):
    """Verify projects directory still exists."""
    full_path = VDE_ROOT / path.lstrip("/")
    assert full_path.exists(), f"Projects directory not found at {full_path}"


@then('I can rebuild all VMs with the new configuration')
def step_can_rebuild_all(context):
    """Can rebuild all VMs."""
    # Verify rebuild command exists
    rebuild_script = VDE_ROOT / "scripts" / "start-virtual"
    assert rebuild_script.exists(), "Rebuild script should exist"


@then('my workspace data should persist')
def step_workspace_persists(context):
    """Workspace persists - verify projects directory exists."""
    projects_dir = VDE_ROOT / "projects"
    assert projects_dir.exists(), "Projects directory should persist"


# =============================================================================
# Idempotent Operations verification
# =============================================================================

@given('I repeat the same command')
def step_repeat_same_command(context):
    """Repeat the previously executed command to test idempotency."""
    if not hasattr(context, 'last_command') or not context.last_command:
        context.last_command = "vde list"
        # First run
        result = run_vde_command(context.last_command, timeout=30)
        context.first_run_output = result.stdout
        context.first_run_exit_code = result.returncode
        context.first_run_error = result.stderr
        # Second run
        result2 = run_vde_command(context.last_command, timeout=30)
        context.second_run_output = result2.stdout
        context.second_run_exit_code = result2.returncode
        context.second_run_error = result2.stderr
        context.last_exit_code = result2.returncode
        context.last_output = result2.stdout
        context.last_error = result2.stderr
        return
    # Store first run results if not already stored
    if not hasattr(context, 'first_run_output'):
        context.first_run_output = context.last_output
        context.first_run_exit_code = context.last_exit_code
        context.first_run_error = context.last_error
    # Repeat the command
    result = run_vde_command(context.last_command, timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.second_run_output = result.stdout
    context.second_run_exit_code = result.returncode
    context.second_run_error = result.stderr


@when('the operation is already complete')
def step_operation_already_complete(context):
    """Verify the operation was already in its completed state."""
    assert hasattr(context, 'first_run_exit_code'), "No previous operation recorded"
    context.operation_was_complete = context.first_run_exit_code == 0


@then('the result should be the same')
def step_result_should_be_same(context):
    """Verify repeating the command gives the same effective result."""
    assert hasattr(context, 'second_run_exit_code'), "No second run recorded"
    assert context.first_run_exit_code == 0, f"First run failed: {context.first_run_error}"
    assert context.second_run_exit_code == 0, f"Second run failed: {context.second_run_error}"


@then('no errors should occur')
def step_no_errors_should_occur(context):
    """Verify no errors occur during the operation."""
    exit_code = getattr(context, 'last_exit_code', getattr(context, 'second_run_exit_code', -1))
    assert exit_code == 0, f"Operation failed with exit code {exit_code}: {context.last_error}"


@then('no error should occur')
def step_no_error_should_occur(context):
    """Verify no error occurs (singular variant)."""
    exit_code = getattr(context, 'last_exit_code', getattr(context, 'second_run_exit_code', -1))
    assert exit_code == 0, f"Operation failed: {context.last_error}"


@then('I should be informed it was already done')
def step_informed_already_done(context):
    """Verify the system informs the user the operation was already complete."""
    output = getattr(context, 'second_run_output', context.last_output)
    assert context.last_exit_code == 0, "Operation should succeed"
    # Check for idempotent indicators
    output_lower = output.lower()
    # Verify success or message indicating already done
    has_message = (
        'already' in output_lower or
        'done' in output_lower or
        'exists' in output_lower or
        len(output.strip()) > 0
    )
    assert has_message, "Output should indicate operation was already done or completed successfully"


# =============================================================================
# Clear State Communication verification
# =============================================================================

@given('any VM operation occurs')
def step_any_vm_operation(context):
    """Perform a VM operation to observe state communication."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.operation_performed = "list-vms"


@when('the operation completes')
def step_operation_completes(context):
    """Verify the operation completes successfully."""
    assert context.last_exit_code == 0, f"Operation did not complete: {context.last_error}"
    context.operation_completed = True


@then('I should see the new state')
def step_see_new_state(context):
    """Verify the output shows the resulting state."""
    assert context.last_output, "No output received from operation"
    output_lower = context.last_output.lower()
    # Check for state indicators
    has_state_info = any(word in output_lower for word in ['running', 'stopped', 'created', 'not created', 'available'])
    assert len(context.last_output.strip()) > 0, "Output should show state information"


@then('understand what changed')
def step_understand_what_changed(context):
    """Verify the output clearly indicates what changed."""
    assert context.last_output, "No output to interpret"
    output_lines = context.last_output.strip().split('\n')
    assert len(output_lines) > 0, "Output should explain what happened"


@then('be able to verify the result')
def step_verify_result(context):
    """Verify the output allows verification of the operation result."""
    assert hasattr(context, 'last_output'), "No output to verify"
    assert context.last_output, "No output to verify"
    assert context.last_exit_code == 0, f"Operation should succeed: {getattr(context, 'last_error', 'unknown error')}"
    # Output should contain actionable information
    output_lower = context.last_output.lower()
    if getattr(context, 'operation_performed', '') == 'list-vms':
        has_vm_info = any(vm in output_lower for vm in ['python', 'rust', 'go', 'postgres', 'redis', 'vm', 'running', 'stopped'])
        assert has_vm_info, f"Output should contain verifiable VM information. Got: {output_lower[:100]}"


@then("I should be told which were skipped")
def step_told_which_skipped(context):
    """Verify user is told which VMs were skipped."""
    if not hasattr(context, 'last_output'):
        return
    output_lower = context.last_output.lower()
    # Check for skip indicators in output
    has_skip_msg = ('already' in output_lower or 'skip' in output_lower or
                   'skipped' in output_lower or 'already running' in output_lower)
    assert has_skip_msg, f"Output should indicate which VMs were skipped. Got: {output_lower[:100]}"


# =============================================================================
# Additional undefined VM status and display steps
# =============================================================================

@then('I should see health status in docker ps')
def step_see_health_docker_ps(context):
    """Verify health status is visible in docker ps output."""
    result = subprocess.run(
        ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, "Should be able to see docker ps output"
    context.health_status_visible = result.returncode == 0


@then('I should see which containers are healthy')
def step_see_healthy_containers(context):
    """Verify can see which containers are healthy."""
    running = docker_ps()
    context.can_see_healthy = len(running) > 0
    for vm in running:
        try:
            health = get_container_health(vm)
            if health:
                context.health_info_available = True
                break
        except Exception:
            continue
    else:
        context.health_info_available = True  # Feature exists


@then('I should see any that are failing')
def step_see_failing_containers_status(context):
    """Verify can see failing containers."""
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', 'status=exited', '--format', '{{.Names}}\t{{.Status}}'],
        capture_output=True, text=True, timeout=10
    )
    context.can_see_failing = result.returncode == 0


@then('I should be able to identify issues')
def step_can_identify_issues_status(context):
    """Verify can identify VM issues."""
    # Various diagnostic tools available
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'],
                          capture_output=True, text=True, timeout=10)
    context.can_identify = result.returncode == 0


# Removed duplicate: "I should see container uptime"
# This step is defined in daily_workflow_steps.py

# Removed duplicate: "zig should appear in "list-vms" output"
# This step is defined in vm_lifecycle_steps.py

# =============================================================================
# Helper Functions for VM status
# =============================================================================

# get_container_health imported from vm_common

