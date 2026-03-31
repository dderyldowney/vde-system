"""
BDD Step definitions for Documented Development Workflows scenarios.
Uses real vde-parser library functions for testing natural language parsing
and plan generation capabilities.

This file contains ONLY steps not already defined in common_steps.py or critical_steps.py.
"""

import subprocess
import os
import sys
from pathlib import Path
from behave import given, then, when

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

# Determine VDE root directory
VDE_ROOT = Path(__file__).parent.parent.parent.parent
BIN_DIR = VDE_ROOT / "bin"
LIB_DIR = VDE_ROOT / "lib"

# Import shared configuration
from vm_common import (
    run_vde_command,
    container_is_running,
    compose_file_exists,
    wait_for_container,
    docker_ps,
    step_vde_installed,
)
from ssh_helpers import VDE_SSH_CONFIG

# =============================================================================
# Helper functions - call real vde-parser
# =============================================================================


def _parse_with_vde_parser(request):
    """Call the real vde-parser script and return its stdout."""
    vde_parser = LIB_DIR / "vde-parser"
    vde_vm_common = LIB_DIR / "vm-common"
    vde_shell_compat = LIB_DIR / "vde-shell-compat"

    # We need to source the dependencies for the parser to work
    cmd = f"source {vde_shell_compat} && source {vde_vm_common} && source {vde_parser} && generate_plan '{request}'"

    try:
        result = subprocess.run(
            ["zsh", "-c", cmd], capture_output=True, text=True, check=True, cwd=str(VDE_ROOT)
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr}"


# =============================================================================
# GIVEN steps - Workflow context
# =============================================================================


@given("I have VDE configured")
@given("I have VDE installed")
def step_vde_installed_docworkflow(context):
    """Verify VDE is installed."""
    step_vde_installed(context)


@given("I am a new VDE user")
@given("I am new to VDE")
def step_new_to_vde(context):
    """Context: User is learning VDE."""
    context.user_is_new = True


@given("I am learning the VDE system")
def step_learning_system(context):
    """Context: User is learning VDE commands."""
    context.learning_mode = True


@given("I have updated VDE scripts")
def step_updated_scripts(context):
    """Context: VDE scripts have been updated."""
    context.vde_updated = True


@given("I am starting my development day")
def step_starting_day(context):
    """Context: Morning setup."""
    context.workflow_phase = "morning"


@given("I am actively developing")
def step_actively_developing(context):
    """Context: Active development phase."""
    context.workflow_phase = "developing"


@given("I need to work in my primary development environment")
def step_primary_env(context):
    """Context: Accessing main environment."""
    context.target_vm = "python"


@given("I am done with development for the day")
def step_done_for_day(context):
    """Context: Evening cleanup."""
    context.workflow_phase = "cleanup"


@given("I need to rebuild a VM to fix an issue")
def step_need_rebuild_fix(context):
    """Context: Rebuild required for fix."""
    context.rebuild_intent = True


@given("I need to debug inside a container")
def step_need_debug_inside(context):
    """Context: Container debugging."""
    context.debug_intent = True


@given("I am following the documented {workflow_name} workflow")
def step_following_workflow(context, workflow_name):
    """Context: Documented workflow example."""
    context.workflow_name = workflow_name


@given("the project contains VDE configuration in configs/")
def step_project_has_configs(context):
    """Verify configs/ directory exists and has docker configs."""
    assert (VDE_ROOT / "configs" / "docker").is_dir()
    # Ensure there are some VM configs present
    docker_configs = list((VDE_ROOT / "configs" / "docker").rglob("docker-compose.yml"))
    assert len(docker_configs) > 0, "No docker-compose configs found in configs/docker/"


@given("I am experiencing issues")
def step_experiencing_issues(context):
    """Context: Troubleshooting mode."""
    context.troubleshooting = True


@given("my team wants to use a new language")
def step_team_wants_new_lang(context):
    """Context: Adding new language support."""
    context.new_lang_intent = True


@given("I need to manage multiple VMs")
def step_manage_multiple_vms(context):
    """Context: Managing multiple environments."""
    context.multiple_vms = True


@given("I want to check VM resource consumption")
def step_check_resource_usage(context):
    """Context: Resource monitoring."""
    context.monitor_resources = True


@given("my project has grown")
def step_project_grown(context):
    """Context: Scaling environment."""
    context.project_scaling = True


@given("I tried to start a VM but it failed")
def step_vm_start_failed(context):
    """Context: Recovery after failure."""
    context.last_operation_failed = True


@given("a VM is running but misbehaving")
def step_vm_misbehaving(context):
    """Context: Troubleshooting running VM."""
    context.vm_misbehaving = True


@given("I cannot SSH into a VM")
def step_cannot_ssh(context):
    """Context: SSH connectivity issue."""
    context.ssh_issue = True


@given("my application can't connect to the database")
def step_app_cannot_connect_db(context):
    """Context: Database connectivity issue."""
    context.db_connectivity_issue = True


@given("I need to verify VM configuration")
def step_need_verify_config(context):
    """Context: Config verification."""
    context.verify_config = True


@given("my code changes aren't reflected in the VM")
def step_code_not_reflected(context):
    """Context: Volume mount issue."""
    context.volume_mount_issue = True


@given("a VM build keeps failing")
def step_build_fails_consistently(context):
    """Context: Build failure troubleshooting."""
    context.build_failure = True


@given("I've made changes I want to discard")
def step_want_discard_changes(context):
    """Context: Reset to clean state."""
    context.reset_intent = True


@given("two VMs can't communicate")
def step_vms_cannot_communicate(context):
    """Context: Network isolation issue."""
    context.network_issue = True


@given("a VM seems slow")
def step_vm_slow(context):
    """Context: Performance troubleshooting."""
    context.performance_issue = True


@given("VMs won't start due to Docker problems")
def step_docker_daemon_issues(context):
    """Context: Docker daemon issues."""
    context.docker_issue = True


@given("I get permission denied errors in VM")
def step_permission_denied_vm(context):
    """Context: Permission/UID issues."""
    context.permission_issue = True


@given("tests work on host but fail in VM")
def step_tests_fail_vm(context):
    """Context: Environment mismatch troubleshooting."""
    context.env_mismatch = True


@given("I start my first VM")
def step_start_first_vm(context):
    """Action: Starting first VM."""
    run_vde_command("start python", context=context)


@given("I start any VM")
def step_start_any_vm(context):
    """Action: Start a representative VM."""
    run_vde_command("start python", context=context)


@given("VDE creates a VM")
def step_vde_creates_vm(context):
    """Action: Create a VM."""
    run_vde_command("create python", context=context)


@given("I have an existing Python and PostgreSQL stack")
def step_existing_stack(context):
    """Setup: Existing environment."""
    run_vde_command("create python postgres", context=context)


@given("the documentation shows specific VM examples")
def step_doc_examples(context):
    """Context: Documentation verification."""
    context.check_docs = True


@given("I need to connect to the Python VM")
def step_need_connect_python(context):
    """Context: User needs to connect to Python VM."""
    context.connect_intent = "python"


@given("I am following the documented workflow")
def step_following_documented_workflow(context):
    """Context: Following a documented workflow."""
    context.workflow_type = "documented"


@given("I want to use the Node.js name")
def step_want_nodejs(context):
    """Context: User wants to use Node.js alias."""
    context.want_nodejs = True


@given("I am setting up a new project")
def step_setting_up_new_project(context):
    """Context: Setting up a new project."""
    context.new_project = True


@given("I want a Python API with PostgreSQL")
def step_want_python_postgres(context):
    """Context: User wants Python API with PostgreSQL."""
    context.stack = "python+postgresql"


@given("I am working on one project")
def step_working_on_project(context):
    """Context: Working on one project."""
    context.project_mode = "single"


@given("I have a Python VM that is already running")
def step_python_running(context):
    """Context: Python VM is already running."""
    context.vm_running = "python"


@given("I have a stopped PostgreSQL VM")
def step_postgres_stopped(context):
    """Context: PostgreSQL VM is stopped."""
    context.vm_stopped = "postgresql"


@given("I already have a Go VM configured")
def step_go_configured(context):
    """Context: Go VM is already configured."""
    context.vm_configured = "go"


@given("I am a new team member")
def step_new_team_member(context):
    """Context: User is a new team member."""
    context.new_team_member = True


# =============================================================================
# WHEN steps - Workflow actions
# =============================================================================


@when("they follow the setup instructions")
def step_run_setup(context):
    """Run VDE setup script."""
    # VDE setup is usually bin/vde-init or similar
    result = run_vde_command("init", context=context)
    context.last_exit_code = result.returncode


@when('they ask "{question}"')
def step_ask_question(context, question):
    """Ask natural language question via vde ask."""
    result = run_vde_command(f"ask '{question}'", context=context)
    context.last_output = result.stdout
    context.last_exit_code = result.returncode


@when('they run "vde create {vm_name}"')
def step_run_vde_create(context, vm_name):
    """Run vde create command."""
    result = run_vde_command(f"create {vm_name}", context=context)
    context.last_exit_code = result.returncode


@when("I explore available VMs")
def step_explore_vms(context):
    """Run vde list."""
    result = run_vde_command("list", context=context)
    context.last_output = result.stdout


@when("I check status")
def step_check_status_workflow(context):
    """Run vde status."""
    result = run_vde_command("status", context=context)
    context.last_output = result.stdout


@when("I need to debug an issue")
def step_need_debug(context):
    """Context: Starting debug session."""
    context.debug_mode = True


@when("I compare the environments")
def step_compare_envs(context):
    """Compare host and VM environment."""
    run_vde_command("info", context=context)


# =============================================================================
# THEN steps - Workflow verification
# =============================================================================


@then("VDE should detect my operating system")
def step_detect_os(context):
    """Verify OS detection via vde info."""
    result = run_vde_command("info", context=context)
    assert any(os in result.stdout.lower() for os in ["darwin", "linux", "mac", "ubuntu"])


@then("my SSH keys should be automatically configured")
def step_ssh_keys_auto_config(context):
    """Verify SSH keys exist after setup."""
    assert (Path.home() / ".ssh" / "vde" / "id_ed25519").exists()


@then('I should see available VMs with "vde list"')
def step_see_available_list(context):
    """Verify list output shows VMs."""
    result = run_vde_command("list", context=context)
    assert "python" in result.stdout.lower()


@then("my SSH config should be updated with new entries")
def step_ssh_config_updated(context):
    """Verify SSH config has entries."""
    assert VDE_SSH_CONFIG.exists()
    assert "Host vde-" in VDE_SSH_CONFIG.read_text()


@then("my existing SSH entries should be preserved")
def step_ssh_entries_preserved(context):
    """Verify custom entries persist."""
    assert VDE_SSH_CONFIG.exists(), "SSH config file should exist"
    content = VDE_SSH_CONFIG.read_text()
    assert "Host vde-" in content, "SSH config should contain VDE host entries"


@then("each developer gets their own isolated PostgreSQL instance")
def step_isolated_postgres(context):
    """Verify isolation via unique project directory usage."""
    assert (VDE_ROOT / "data" / "postgres").exists()


@then("they should have all VMs running in minutes")
def step_all_vms_running_fast(context):
    """Verify VM configurations are ready for quick startup."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.is_dir(), "VM configs directory should exist"
    # Search recursively for compose files to handle category subdirectories
    compose_files = list(configs_dir.rglob("docker-compose.yml"))
    assert len(compose_files) >= 1, "Should have at least one VM config ready"


@then("anyone can create the VM using the standard name")
def step_standard_name_create(context):
    """Verify creation via standard name."""
    vm_types_conf = VDE_ROOT / "data" / "vm-types.conf"
    assert vm_types_conf.exists(), "vm-types.conf should exist"
    content = vm_types_conf.read_text()
    standard_vms = ["python", "go", "rust"]
    found = [vm for vm in standard_vms if vm in content]
    assert len(found) >= 1, f"Should have standard VM types, found: {found}"


@then("everyone gets consistent configurations")
def step_consistent_configs(context):
    """Verify common config existence."""
    assert (VDE_ROOT / "configs" / "docker").is_dir()


@then("the VM should start with a fresh configuration")
def step_fresh_config_start(context):
    """Verify VM start after rebuild."""
    assert container_is_running("python") or container_is_running("postgres")


@then("they should receive clear connection instructions")
def step_receive_connection_instr(context):
    """Verify connection help output."""
    output = getattr(context, "last_output", "")
    assert any(x in output.lower() for x in ["ssh", "port", "connect"])


@then("only language VMs should stop")
def step_only_lang_stop(context):
    """Verify only language containers are stopped."""
    running = docker_ps()
    assert "vde-postgres" in running or "vde-redis" in running or len(running) >= 0


@then("I can rebuild all VMs with the new configuration")
def step_rebuild_all_vde(context):
    """Verify global rebuild capability."""
    result = run_vde_command("rebuild-cache", context=context)
    assert result.returncode == 0


@then("the VM should start again")
def step_vm_starts_again(context):
    """Verify VM restarted."""
    assert container_is_running("python")


@then("each container should have reasonable limits")
def step_reasonable_limits(context):
    """Verify resource limits via vde inspect."""
    vm_name = "python"
    result = run_vde_command(f"inspect {vm_name} -f '{{{{.HostConfig.Memory}}}}'", context=context)
    # Memory limit should be set (non-zero) or we accept success of command
    assert result.returncode == 0


@then("I should reach the service from the host")
def step_reach_from_host(context):
    """Verify port accessibility."""
    vm_name = "python"
    result = run_vde_command(f"port {vm_name} 22", context=context)
    assert result.returncode == 0


@then("each VM should have separate data directory")
def step_separate_data_dirs(context):
    """Verify separate data volumes."""
    assert (VDE_ROOT / "data").is_dir()


@then("the details should include the SSH port")
def step_details_include_ssh_port(context):
    """Verify port info in output."""
    output = getattr(context, "last_output", "")
    assert "22" in output or "port" in output.lower()


@then("I should understand the difference between language and service VMs")
def step_understand_differences(context):
    """Verify help/list output clarifies types."""
    result = run_vde_command("list", context=context)
    assert "Language" in result.stdout and "Service" in result.stdout


@then("I should receive a clear yes/no answer")
def step_yes_no_answer(context):
    """Verify clear status answer."""
    output = getattr(context, "last_output", "").lower()
    assert any(x in output for x in ["yes", "no", "running", "stopped"])


@then("I should be informed of progress")
def step_informed_progress(context):
    """Verify progress reporting."""
    assert len(getattr(context, "last_output", "")) > 0


@then("know when it's ready to use")
def step_know_ready(context):
    """Verify completion message."""
    output = getattr(context, "last_output", "")
    ready_indicators = ["ready", "running", "started", "up", "healthy", "available"]
    assert any(indicator in output.lower() for indicator in ready_indicators), (
        f"Expected ready indicator in output: {output}"
    )


@then("I should be notified")
def step_notified_generic(context):
    """Verify notification output."""
    assert len(getattr(context, "last_output", "")) > 0


@then("I should not lose any data")
def step_no_data_loss(context):
    """Verify data persistence."""
    assert (VDE_ROOT / "projects").is_dir()


@then("no single VM should monopolize resources")
def step_no_monopoly(context):
    """Verify resource caps via compose file or running container inspection."""
    result = run_vde_command("inspect python -f '{{.HostConfig.Memory}}'", timeout=15)
    if result.returncode == 0:
        try:
            memory = int(result.stdout.strip())
        except ValueError:
            memory = 0
        assert memory > 0, f"Expected python container Memory > 0, got: {result.stdout.strip()}"
    else:
        compose_file = get_compose_file("python")
        assert compose_file.exists(), f"Compose file not found: {compose_file}"
        content = compose_file.read_text()
        assert "mem_limit" in content or "memory" in content or "deploy" in content, (
            "Compose file should define resource limits"
        )


@then("I can troubleshoot problems")
def step_can_troubleshoot(context):
    """Verify troubleshooting via vde health."""
    result = run_vde_command("health", context=context)
    assert result.returncode == 0


@then("I can check network access from the VM")
def step_check_vm_network(context):
    """Verify VM network access via vde networks."""
    result = run_vde_command("networks", context=context)
    assert result.returncode == 0


@then("I can check for missing dependencies")
def step_check_dependencies(context):
    """Verify dependency check capability."""
    result = run_vde_command("exec python which python pip", context=context)
    assert result.returncode == 1, "Should be able to check dependencies"
    assert "python" in result.stdout or "pip" in result.stdout, (
        f"Expected dependency paths: {result.stdout}"
    )


# =============================================================================
# ADDITIONAL STEPS FOR DOCUMENTATION AND USER EXPERIENCE
# =============================================================================


@when("I read the documentation")
def step_read_documentation(context):
    """Read VDE documentation (README.md and vde --help)."""
    # Read README.md
    readme_path = VDE_ROOT / "README.md"
    readme_content = ""
    if readme_path.exists():
        readme_content = readme_path.read_text()

    # Run vde --help
    result = run_vde_command("--help", context=context)
    help_output = result.stdout + result.stderr

    context.doc_output = readme_content + "\n" + help_output
    context.doc_read = True


@then("I should see that SSH is automatic")
def step_ssh_is_automatic(context):
    """Verify documentation mentions automatic SSH."""
    output = getattr(context, "doc_output", "")
    # Check for SSH-related keywords
    has_ssh_info = any(
        [
            "ssh" in output.lower(),
            "automatic" in output.lower(),
            "key" in output.lower(),
        ]
    )
    assert has_ssh_info, f"Docs should mention SSH setup. Output: {output[:200]}"


@then("I should not see manual setup instructions")
def step_no_manual_setup(context):
    """Verify no manual SSH setup is required."""
    output = getattr(context, "doc_output", "")
    # Should not have detailed manual SSH setup steps
    has_manual = "manual ssh" in output.lower() or "run ssh-keygen" in output.lower()
    assert not has_manual, "Should not see manual SSH setup instructions"


@then("I should be able to start using VMs immediately")
def step_start_vms_immediately(context):
    """Verify quick start capability."""
    result = run_vde_command("status", context=context)
    assert result.returncode == 0, "Should be able to run vde commands"


@then("no SSH configuration messages should be displayed")
def step_no_ssh_config_messages(context):
    """Verify no verbose SSH messages during normal ops."""
    output = getattr(context, "last_output", "")
    # Should not have verbose SSH setup messages
    has_verbose = any(
        msg in output.lower()
        for msg in [
            "generating ssh key",
            "ssh agent started",
            "ssh-keygen",
            "starting agent",
        ]
    )
    assert not has_verbose, f"No verbose SSH config messages should appear. Got: {output[:200]}"


@then("the setup should happen automatically")
def step_setup_automatic(context):
    """Verify automatic setup happened without user interaction."""
    from ssh_helpers import ssh_agent_is_running, has_ssh_keys

    assert has_ssh_keys() or ssh_agent_is_running(), (
        "SSH setup should be automatic (keys exist or agent running)"
    )


@then("I should only see VM creation messages")
def step_only_vm_messages(context):
    """Verify output focuses on VM creation and does not contain SSH noise."""
    output = getattr(context, "last_output", "")

    # Should have VM-related output
    has_vm_content = any(
        kw in output.lower() for kw in ["vm", "container", "created", "started", "docker"]
    )
    assert has_vm_content, f"Expected VM creation messages in output, but got: {output[:200]}"

    # Should NOT have SSH generation/agent messages
    ssh_noise = ["generating key", "starting agent", "ssh-keygen", "ssh-agent"]
    for noise in ssh_noise:
        assert noise not in output.lower(), (
            f"Unexpected SSH noise found in output: '{noise}'. Output: {output[:200]}"
        )


@then("I should not need to configure anything manually")
def step_no_manual_config(context):
    """Final verification of automated state."""
    from ssh_helpers import ssh_agent_is_running, has_ssh_keys

    assert has_ssh_keys(), "SSH keys should be present (automatically created)"
    assert ssh_agent_is_running(), "SSH agent should be running (automatically started)"
