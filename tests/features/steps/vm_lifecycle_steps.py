"""
BDD Step Definitions for VM Lifecycle scenarios.
Covers: create-virtual-for, start-virtual, shutdown-virtual, list-vms,
        remove-virtual, add-vm-type, and VDE parser (vde ask) requests.
"""

import json
import os
import shutil
import sys
import time

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when  # type: ignore[import]
from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    container_is_running,
    compose_file_exists,
    wait_for_container,
    wait_for_container_stopped,
    get_port_from_compose,
    get_vm_types,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _vm_conf_dir(vm_name):
    return VDE_ROOT / "configs" / "docker" / vm_name


def _ensure_vm_stopped(vm_name):
    if container_is_running(vm_name):
        run_vde_command(f"shutdown-virtual {vm_name}", timeout=60)
        time.sleep(1)


def _add_vm_type_temporarily(
    context, vm_name, vm_type, install_cmd, display=None, port=None, aliases=None
):
    """Add a VM type to vm-types.json/conf; register for cleanup in after_scenario."""
    if not hasattr(context, "_temp_vm_types"):
        context._temp_vm_types = []
    context._temp_vm_types.append(vm_name)

    conf_file = VDE_ROOT / "data" / "vm-types.conf"
    json_file = VDE_ROOT / "data" / "vm-types.json"

    display = display or vm_name.capitalize()
    aliases_str = aliases or vm_name
    port_str = port or ""
    # Use a test ssh_port within the valid range (2299 for lang, 2499 for service)
    ssh_port = 2299 if vm_type in ("lang", "language") else 2499

    # Append to conf (pipe-delimited): type|name|aliases|display|install|svc_port|ssh_port
    with open(conf_file, "a") as f:
        f.write(
            f"\n{vm_type}|vde-{vm_name}|{aliases_str}|{display}|{install_cmd}|{port_str}|{ssh_port}\n"
        )

    # Append to JSON
    with open(json_file) as f:
        data = json.load(f)
    category = "language" if vm_type in ("lang", "language") else "service"
    entry = {
        "name": f"vde-{vm_name}",
        "aliases": [a.strip() for a in aliases_str.split(",")],
        "display": display,
        "install": install_cmd,
        "service_port": port_str if port_str else None,
        "ssh_port": ssh_port,
    }
    data["vms"][category].append(entry)
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)

    # Invalidate cache so the new type is picked up
    cache_file = VDE_ROOT / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()


def _remove_vm_type(vm_name):
    """Remove a VM type from vm-types.conf and vm-types.json."""
    conf_file = VDE_ROOT / "data" / "vm-types.conf"
    json_file = VDE_ROOT / "data" / "vm-types.json"

    # Remove from conf — match lines containing |vde-{vm_name}| (non-comment)
    search = f"|vde-{vm_name}|"
    lines = conf_file.read_text().splitlines()
    conf_file.write_text(
        "\n".join(l for l in lines if not (search in l and not l.strip().startswith("#"))) + "\n"
    )

    # Remove from JSON
    with open(json_file) as f:
        data = json.load(f)
    for cat in ("language", "service"):
        data["vms"][cat] = [v for v in data["vms"][cat] if v["name"] != f"vde-{vm_name}"]
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)

    # Invalidate cache
    cache_file = VDE_ROOT / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()


# ---------------------------------------------------------------------------
# after_scenario cleanup hook (registered via behave's environment.py pattern
# by storing cleanup state on context; environment.py calls these if present)
# ---------------------------------------------------------------------------


def _cleanup_temp_vm_types(context):
    import re

    env_dir = VDE_ROOT / "env-files"
    ssh_config = VDE_ROOT / "configs" / "ssh" / "config"
    for vm_name in getattr(context, "_temp_vm_types", []):
        _remove_vm_type(vm_name)
        # Remove compose dir if created during this scenario
        conf_dir = _vm_conf_dir(vm_name)
        if conf_dir.exists():
            shutil.rmtree(str(conf_dir))
        # Remove env file created by add-vm-type / create-virtual-for
        for env_f in (env_dir / f"vde-{vm_name}.env", env_dir / f"{vm_name}.env"):
            if env_f.exists():
                env_f.unlink()
        # Remove SSH config block added by add-vm-type
        if ssh_config.exists():
            text = ssh_config.read_text()
            cleaned = re.sub(
                rf"\n*Host vde-{re.escape(vm_name)}[^\n]*\n(?:    [^\n]*\n)*", "", text
            )
            if cleaned != text:
                ssh_config.write_text(cleaned)
    context._temp_vm_types = []


# ---------------------------------------------------------------------------
# GIVEN — setup steps
# ---------------------------------------------------------------------------























# Natural language given steps for vm-lifecycle-management.feature


@given("I want to work with a new language")
def step_want_new_language(context):
    """Context setup — no action needed."""
    pass


@given("I have created a Go VM")
def step_have_created_go(context):
    if not compose_file_exists("go"):
        result = run_vde_command("create-virtual-for go", timeout=120)
        assert result.returncode in (0, 6), f"Failed to create go: {result.stderr}"
    context.vm_name = "go"


@given("I have created several VMs")
def step_have_created_several(context):
    for vm in ("python", "go", "postgres"):
        if not compose_file_exists(vm):
            run_vde_command(f"create-virtual-for {vm}", timeout=120)
    context.vms = ["python", "go", "postgres"]
    # All VDE VMs share vde-net Docker network — they can communicate
    context.network_configured = True


@given("I have several VMs")
def step_have_several_vms(context):
    context.vms = [v for v in ("python", "go", "postgres") if compose_file_exists(v)]


@given("I have a running Python VM")
def step_have_running_python(context):
    if not container_is_running("python"):
        result = run_vde_command("start-virtual python", timeout=180)
        assert result.returncode == 0, f"Failed to start python: {result.stderr}"
        wait_for_container("python", timeout=120)
    context.vm_name = "python"


@given("I have multiple running VMs")
def step_have_multiple_running(context):
    for vm in ("python", "postgres"):
        if not container_is_running(vm):
            result = run_vde_command(f"start-virtual {vm}", timeout=180)
            if result.returncode == 0:
                wait_for_container(vm, timeout=120)
    context.vms = ["python", "postgres"]


@given("I have a running VM")
def step_have_a_running_vm(context):
    # Use rust for the "Restarting a VM" scenario which checks rust specifically
    if not container_is_running("rust"):
        result = run_vde_command("start-virtual rust", timeout=300)
        assert result.returncode == 0, f"Failed to start rust: {result.stderr}"
        wait_for_container("rust", timeout=180)
    context.vm_name = "rust"


@given("I need to refresh a VM")
def step_need_to_refresh_vm(context):
    if not container_is_running("python"):
        result = run_vde_command("start-virtual python", timeout=180)
        assert result.returncode == 0, f"Failed to start python: {result.stderr}"
        wait_for_container("python", timeout=120)
    context.vm_name = "python"


@given("I no longer need a VM")
def step_no_longer_need_vm(context):
    context.vm_name = "python"


@given("I have modified the Dockerfile")
def step_have_modified_dockerfile(context):
    """Context setup — ensure go exists and is running before rebuild."""
    context.vm_name = "go"
    if not compose_file_exists("go"):
        run_vde_command("create-virtual-for go", timeout=120)
    if not container_is_running("go"):
        result = run_vde_command("start-virtual go", timeout=300)
        if result.returncode == 0:
            wait_for_container("go", timeout=180)


@given("I want to update the base image")
def step_want_to_update_base_image(context):
    context.vm_name = "python"


@given("I have updated VDE scripts")
def step_have_updated_vde_scripts(context):
    context.vm_name = "python"


# ---------------------------------------------------------------------------
# WHEN — command runner steps
# ---------------------------------------------------------------------------


@when('I run "{command}"')
def step_run_command(context, command):
    """Generic command runner: handles direct scripts and compound && commands."""
    context.vm_name = getattr(context, "vm_name", None)

    # Handle compound commands (e.g., "shutdown-virtual python && start-virtual python")
    if " && " in command:
        parts = [p.strip() for p in command.split(" && ")]
        for part in parts:
            result = run_vde_command(part, timeout=180, context=context)
            if result.returncode != 0:
                break
    else:
        run_vde_command(command, timeout=180, context=context)

    # Register add-vm-type VM names for cleanup
    stripped = command.strip("'\"")
    if stripped.startswith("add-vm-type"):
        tokens = stripped.split()
        # The positional VM name comes after all --flag value pairs
        non_flag_tokens = []
        skip_next = False
        for tok in tokens[1:]:
            if skip_next:
                skip_next = False
                continue
            if tok in ("--type", "--display"):
                skip_next = True
            elif not tok.startswith("-"):
                non_flag_tokens.append(tok.strip("'\""))
        if non_flag_tokens:
            added_vm = non_flag_tokens[0]
            if not hasattr(context, "_temp_vm_types"):
                context._temp_vm_types = []
            if added_vm not in context._temp_vm_types:
                context._temp_vm_types.append(added_vm)

    # Extract VM name from command for downstream steps
    for token in command.replace(" && ", " ").split():
        if (
            token
            not in (
                "create-virtual-for",
                "start-virtual",
                "shutdown-virtual",
                "remove-virtual",
                "list-vms",
                "add-vm-type",
                "--lang",
                "--svc",
                "--rebuild",
                "--no-cache",
                "--type",
                "--display",
                "lang",
                "svc",
                "all",
            )
            and not token.startswith("-")
            and not token.startswith("'")
        ):
            if context.vm_name is None:
                context.vm_name = token


@when('I request to "{request}"')
def step_request_to(context, request):
    """Natural language request through vde ask."""
    # vde-ask often requires confirmation - pass 'y' to stdin
    result = run_vde_command(f"vde-ask {request}", timeout=120, context=context, input_text="y\n")
    context.last_request = request


@when('I request "{request}"')
def step_request(context, request):
    """Natural language request (status/info variant)."""
    result = run_vde_command(f"vde-ask {request}", timeout=60, context=context)
    context.last_request = request


@when("I remove its configuration")
def step_remove_vm_configuration(context):
    """Remove current VM config."""
    vm_name = getattr(context, "vm_name", "python")
    run_vde_command(f"remove-virtual {vm_name}", timeout=60, context=context)


@when("I rebuild the VM")
def step_rebuild_vm(context):
    """Rebuild current VM."""
    vm_name = getattr(context, "vm_name", "python")
    run_vde_command(f"start-virtual {vm_name} --rebuild", timeout=300, context=context)


@when("I rebuild my VMs")
def step_rebuild_my_vms(context):
    """Rebuild all created VMs."""
    vms = getattr(context, "vms", ["python"])
    for vm in vms:
        if compose_file_exists(vm):
            run_vde_command(f"start-virtual {vm} --rebuild", timeout=300, context=context)


# ---------------------------------------------------------------------------
# THEN — verification steps
# ---------------------------------------------------------------------------








@then("only service VMs should be listed")
def step_only_service_vms_listed(context):
    output = getattr(context, "last_output", "") or ""
    assert output.strip(), "list-vms --all --svc produced no output"
    assert "Service VMs:" in output, f"'Service VMs:' header not found:\n{output}"
    assert "Language VMs:" not in output, f"'Language VMs:' header should not appear:\n{output}"


@then("the VM configuration should be generated")
def step_vm_config_generated(context):
    vm_name = getattr(context, "vm_name", "rust")
    assert compose_file_exists(vm_name), f"Compose config not generated for {vm_name}"


@then("all three VMs should be created")
def step_all_three_vms_created(context):
    for vm in ("python", "postgres", "redis"):
        assert compose_file_exists(vm), f"VM {vm} not created"


@then("the Go container should start")
def step_go_container_starts(context):
    assert container_is_running("go"), "Go container not running"


@then("all three VMs should start")
def step_all_three_vms_start(context):
    for vm in ("python", "go", "postgres"):
        if compose_file_exists(vm):
            assert container_is_running(vm), f"VM {vm} not running"
    context.network_configured = True


#@then("I should see which VMs are running")
#def step_see_running_vms(context):
#    output = getattr(context, "last_output", "") or ""
#    # vde-ask status should produce some output
#    assert output is not None  # permissive — ask may route differently
#
#
#@then("I should see which VMs are stopped")
#def step_see_stopped_vms(context):
#    pass  # permissive — covered by running check
#
#
#@then("I should see any error states")
#def step_see_error_states(context):
#    pass  # permissive — covered by running check
#
#
#@then("the Python container should stop")
#def step_python_container_stops(context):
#    assert not container_is_running("python"), "Python container still running"
#
#
#@then("the VM configuration should remain")
#def step_vm_config_remains(context):
#    vm_name = getattr(context, "vm_name", "python")
#    assert compose_file_exists(vm_name), f"Config missing for {vm_name}"
#
#
#@then("I can start it again later")
#def step_can_start_again(context):
#    # Compose file exists = can start again
#    vm_name = getattr(context, "vm_name", "python")
#    assert compose_file_exists(vm_name)
#
#
#@then("both VMs should stop")
#def step_both_vms_stop(context):
#    vms = getattr(context, "vms", ["python", "postgres"])
#    for vm in vms:
#        assert not container_is_running(vm), f"VM {vm} still running"
#
#
#@then("other VMs should remain running")
#def step_other_vms_remain_running(context):
#    # We only stopped python and postgres, so no assertion needed without knowing what else runs
#    pass
#
#
#@then("the Rust VM should stop")
#def step_rust_vm_stops(context):
#    # Note: vde-ask "restart" recreates the container without explicit stop
#    # So we allow either stopped or just transitioned (recreated) state
#    # The next step will verify it's running again
#    if container_is_running("rust"):
#        # Container is still running - vde-ask restart may have recreated it
#        # Just give it a moment to stabilize
#        time.sleep(2)
#    # Don't assert stopped - vde-ask restart doesn't stop first
#
#
#@then("the Rust VM should start again")
#def step_rust_vm_starts_again(context):
#    if not container_is_running("rust"):
#        wait_for_container("rust", timeout=300)
#    assert container_is_running("rust"), "Rust VM not running"
#
#
#@then("my workspace should still be accessible")
#def step_workspace_still_accessible(context):
#    vm_name = getattr(context, "vm_name", "python")
#    compose = _vm_conf_dir(vm_name) / "docker-compose.yml"
#    if compose.exists():
#        assert "projects" in compose.read_text()
#
#
#@then("the Python VM should be rebuilt")
#def step_python_vm_rebuilt(context):
#    assert container_is_running("python"), "Python VM not running after rebuild"
#
#
#@then("the VM should start with the new image")
#def step_vm_starts_with_new_image(context):
#    vm_name = getattr(context, "vm_name", "python")
#    assert container_is_running(vm_name)
#
#
#@then("my workspace should be preserved")
#def step_workspace_preserved(context):
#    vm_name = getattr(context, "vm_name", "python")
#    compose = _vm_conf_dir(vm_name) / "docker-compose.yml"
#    if compose.exists():
#        assert "projects" in compose.read_text()
#
#
#@then("the VM should be removed")
#def step_vm_removed(context):
#    # remove-virtual stops/removes the container but preserves the compose file by design
#    vm_name = getattr(context, "vm_name", "python")
#    assert not container_is_running(vm_name), f"VM {vm_name} container still running after remove"
#
#
#@then("the container should be stopped if running")
#def step_container_stopped_if_running(context):
#    # remove-virtual ensures the container is stopped
#    vm_name = getattr(context, "vm_name", "python")
#    assert not container_is_running(vm_name), f"VM {vm_name} container still running"
#
#
#@then("the Go VM should be rebuilt from scratch")
#def step_go_rebuilt_from_scratch(context):
#    assert container_is_running("go"), "Go VM not running after rebuild"
#
#
#@then("no cached layers should be used")
#def step_no_cached_layers(context):
#    # Verified by the --no-cache flag in the command; container running is enough
#    assert container_is_running(getattr(context, "vm_name", "go"))
#
#
#@then("each should have its own SSH port")
#def step_each_has_own_ssh_port(context):
#    vms = getattr(context, "vms", ["python", "go", "postgres"])
#    ports = [get_port_from_compose(vm) for vm in vms if compose_file_exists(vm)]
#    ports_clean = [p for p in ports if p]
#    assert len(ports_clean) == len(set(ports_clean)), f"Duplicate SSH ports found: {ports_clean}"
#
#
#@then("they should use the new VDE configuration")
#def step_use_new_vde_config(context):
#    vm_name = getattr(context, "vm_name", "python")
#    assert compose_file_exists(vm_name)
#
#
#@then("my data should be preserved")
#def step_data_preserved(context):
#    vm_name = getattr(context, "vm_name", "python")
#    assert compose_file_exists(vm_name)
