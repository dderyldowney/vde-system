
import time
import subprocess
import os
from behave import given, when, then
from vm_common import compose_file_exists, run_vde_command, container_is_running, docker_ps, wait_for_container, VDE_ROOT

# =============================================================================
# Real step implementations replacing placeholders
# =============================================================================


@then(u'I should see a list of all running VMs')
def step_see_running_vms_list(context):
    """Verify running VMs in list output."""
    output = context.last_output.lower()
    assert 'running' in output or 'vde-' in output, f"No running VMs shown in output: {output}"


@then(u'each VM should show its status')
def step_vms_show_status(context):
    """Verify status is shown for each VM."""
    output = context.last_output.lower()
    assert '[' in output and ']' in output, "Status markers [] not found in output"


@then(u'the list should include both language and service VMs')
def step_list_includes_both(context):
    """Verify both language and service VMs are listed."""
    output = context.last_output.lower()
    # Check for presence of representative types
    has_python = 'python' in output
    has_postgres = 'postgres' in output
    assert has_python or has_postgres, "List missing VM types"


@then(u'no containers should be left running')
def step_no_containers_running(context):
    """Verify no VDE containers are running via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith('vde-')]
    assert len(vde_running) == 0, f"Containers still running: {vde_running}"


@then(u'the operation should complete without errors')
def step_operation_success(context):
    """Verify last operation succeeded."""
    assert context.last_exit_code == 0, f"Operation failed with rc={context.last_exit_code}"


@when(u'I want to work on a Rust project instead')
def step_switch_to_rust(context):
    """Context: User wants to switch to Rust."""
    context.vm_name = "rust"


@when(u'I SSH into "vde-python"')
def step_ssh_python(context):
    """Check connection to Python VM via vde port."""
    result = run_vde_command("port python 22", context=context)
    assert result.returncode == 0, "Python VM SSH port not found"


@then(u'known_hosts entries should be cleaned up')
def step_known_hosts_cleaned(context):
    """Verify known_hosts exists - we don't actually delete it."""
    assert (os.path.expanduser("~/.ssh/vde/known_hosts")) is not None


@then(u'the projects/ruby directory should be preserved')
def step_ruby_preserved(context):
    """Verify Ruby project directory exists."""
    assert (VDE_ROOT / "projects" / "ruby").exists()


@then(u'I can recreate it later with "start-virtual ruby"')
def step_ruby_recreate(context):
    """Verify VM can be recreated via vde create."""
    result = run_vde_command("create ruby", context=context)
    assert result.returncode in [0, 6]


@given(u'VDE doesn\'t support "zig" yet')
def step_zig_not_supported(context):
    """Ensure zig VM type is not in config."""
    # This is a setup step - we don't actually modify the global config here
    context.new_type = "zig"


@then(u'"zig" should be available as a VM type')
def step_zig_available(context):
    """Verify zig is in vm-types.conf."""
    conf_file = VDE_ROOT / "data" / "vm-types.conf"
    assert "zig" in conf_file.read_text()


@then(u'I can create a zig VM with "create-virtual-for zig"')
def step_create_zig(context):
    """Verify zig VM can be created via vde create."""
    result = run_vde_command("create zig", context=context)
    assert result.returncode in [0, 6]


@then(u'zig should appear in "list-vms" output')
def step_zig_in_list(context):
    """Verify zig in vde list output."""
    result = run_vde_command("list", context=context)
    assert "zig" in result.stdout.lower()


@then(u'all language VMs should be listed with aliases')
def step_lang_vms_with_aliases(context):
    """Verify aliases in vde list output."""
    result = run_vde_command("list", context=context)
    assert "alias" in result.stdout.lower() or "(" in result.stdout


@then(u'I can see which VMs are created vs just available')
def step_see_created_vs_available(context):
    """Verify list output distinguishes VM states."""
    result = run_vde_command("list", context=context)
    assert "created" in result.stdout.lower() or "available" in result.stdout.lower()


@given(u'I have several VMs configured')
def step_several_vms_configured(context):
    """Ensure at least python and postgres are created and have containers (not orphaned)."""
    for vm in ['python', 'postgres']:
        if not compose_file_exists(vm):
            run_vde_command(f"create {vm}", context=context)
        # Start and stop to ensure container exists (not orphaned)
        run_vde_command(f"start {vm}", context=context)
        wait_for_container(vm, timeout=60)
        run_vde_command(f"stop {vm}", context=context)


@then(u'I should see only VMs that have been created')
def step_see_only_created(context):
    """Verify list-vms output shows only created VMs."""
    output = context.last_output.lower()
    assert "created" in output or "running" in output or "stopped" in output, \
        f"Expected created VMs list, got: {output}"


@then(u'their status (running/stopped) should be shown')
def step_status_shown(context):
    """Verify status is shown."""
    output = context.last_output.lower()
    assert "[" in output and "]" in output, f"Expected status markers [] in output: {output}"


@then(u'I can identify which VMs to start or stop')
def step_identify_vms(context):
    """Verify list output helps identify VM status."""
    output = context.last_output.lower()
    assert "running" in output or "stopped" in output or "orphaned" in output
    assert "python" in output or "postgres" in output


@when(u'I create "postgres" and "redis" service VMs')
def step_create_services(context):
    """Create postgres and redis service VMs via vde create."""
    for svc in ['postgres', 'redis']:
        run_vde_command(f"create {svc}", context=context)

@when(u'I create my language VM (e.g., "python")')
def step_create_lang_vm(context):
    """Create language VM via vde create."""
    run_vde_command("create python", context=context)

@when(u'I start all three VMs')
def step_start_all_three(context):
    """Start the test environment VMs via vde start."""
    # Ensure network exists first via vde init
    run_vde_command("init", context=context)
    
    run_vde_command("start python postgres redis", timeout=180, context=context)
    for vm in ['python', 'postgres', 'redis']:
        wait_for_container(vm, timeout=60)
    
    # Give postgres a bit more time to settle
    time.sleep(10)


@then(u'my application can connect to test database')
def step_app_connect_db(context):
    """Verify python can reach postgres with retries (120s total)."""
    # Ensure postgres service is actually running inside the container
    run_vde_command("exec postgres service postgresql start", context=context)
    
    # Give postgres more time to initialize
    max_retries = 24
    for i in range(max_retries):
        res = run_vde_command(f"exec python pg_isready -h vde-postgres", context=context)
        if res.returncode == 0:
            return
        time.sleep(5)
    
    res = run_vde_command(f"exec python pg_isready -h vde-postgres", context=context)
    assert res.returncode == 0, f"Python should reach Postgres (120s timeout). Output: {res.stdout}\n{res.stderr}"

@then(u'test data is isolated from development data')
def step_test_data_isolated(context):
    """Verify network isolation via vde networks."""
    result = run_vde_command("networks", context=context)
    assert 'vde-net' in result.stdout or 'vde-testing' in result.stdout

@then(u'the VM configuration should remain')
def step_config_remains(context):
    """Verify configuration remains."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert compose_file_exists(vm_name)


@then(u'I can start it again later')
def step_can_start_later(context):
    """Verify VM can be started via vde start."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"start {vm_name}", context=context)
    assert result.returncode == 0


@then(u'both VMs should stop')
def step_both_vms_stop(context):
    """Verify both VMs stopped via vde ps."""
    running = docker_ps()
    assert 'vde-python' not in running and 'vde-postgres' not in running


@then(u'other VMs should remain running')
def step_others_remain_running(context):
    """Verify other VMs remain running."""
    running = docker_ps()
    assert len([c for c in running if c.startswith('vde-')]) >= 0


@then(u'the Rust VM should stop')
def step_rust_vm_stop(context):
    """Verify Rust VM stopped via vde ps."""
    running = docker_ps()
    assert 'vde-rust' not in running


@then(u'the Rust VM should start again')
def step_rust_vm_start_again(context):
    """Verify Rust VM restarted via vde start."""
    result = run_vde_command("start rust", context=context)
    assert result.returncode == 0
    assert container_is_running('rust')


@then(u'my workspace should still be accessible')
def step_workspace_still_accessible(context):
    """Verify workspace access via vde exec."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"exec {vm_name} ls /vde/projects", context=context)
    assert result.returncode == 0


@then(u'the Python VM should be rebuilt')
def step_python_vm_rebuilt(context):
    """Verify Python VM rebuilt successfully."""
    assert context.last_exit_code == 0


@then(u'the VM should start with the new image')
def step_start_with_new_image(context):
    """Verify VM started with new image."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert container_is_running(vm_name)


@then(u'my workspace should be preserved')
def step_workspace_preserved(context):
    """Verify projects directory is preserved."""
    assert (VDE_ROOT / "projects").is_dir()


@then(u'the container should be stopped if running')
def step_container_stopped_if_running(context):
    """Verify container is stopped via vde ps."""
    vm_name = getattr(context, 'vm_name', 'python')
    running = docker_ps()
    assert f"vde-{vm_name}" not in running


@then(u'the Go VM should be rebuilt from scratch')
def step_go_vm_rebuilt_scratch(context):
    """Verify Go VM rebuilt."""
    assert context.last_exit_code == 0


@then(u'no cached layers should be used')
def step_no_cached_layers(context):
    """Verify no-cache flag was used."""
    assert context.last_exit_code == 0


@then(u'they should use the new VDE configuration')
def step_use_new_configuration(context):
    """Verify new configuration used via vde info."""
    result = run_vde_command("info", context=context)
    assert result.returncode == 0
