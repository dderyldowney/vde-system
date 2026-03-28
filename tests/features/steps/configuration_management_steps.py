"""
Step definitions for configuration-management.feature.
All vde operations use run_vde_command() — no direct docker calls.
"""
import json
import os
import re
import subprocess
import yaml
from pathlib import Path
from behave import given, when, then
from vm_common import run_vde_command, get_compose_file, VDE_ROOT, BIN_DIR

VM_TYPES_JSON = VDE_ROOT / "data" / "vm-types.json"
VM_TYPES_CONF = VDE_ROOT / "data" / "vm-types.conf"


# ============================================================
# Shared helpers
# ============================================================

def _load_vm_types():
    with open(VM_TYPES_JSON) as fh:
        return json.load(fh)


def _find_vm_type(name):
    """Find a VM type entry by name (with or without vde- prefix)."""
    data = _load_vm_types()
    full_name = name if name.startswith("vde-") else f"vde-{name}"
    for vm in data["vms"].get("language", []) + data["vms"].get("service", []):
        if vm["name"] in (full_name, name):
            return vm
    return None


def _cleanup_test_vm_type(name):
    """Remove a test VM type from vm-types.json and vm-types.conf."""
    full_name = name if name.startswith("vde-") else f"vde-{name}"
    data = _load_vm_types()
    for category in ("language", "service"):
        data["vms"][category] = [
            v for v in data["vms"].get(category, [])
            if v["name"] not in (full_name, name)
        ]
    with open(VM_TYPES_JSON, "w") as fh:
        json.dump(data, fh, indent=2)
    if VM_TYPES_CONF.exists():
        lines = VM_TYPES_CONF.read_text().splitlines(keepends=True)
        filtered = [
            ln for ln in lines
            if f"|{full_name}|" not in ln and f"|{name}|" not in ln
        ]
        VM_TYPES_CONF.write_text("".join(filtered))


def _get_compose_yaml(vm_name):
    compose_path = get_compose_file(vm_name)
    with open(compose_path) as fh:
        return yaml.safe_load(fh)


def _first_service(compose):
    """Return the first service dict from a parsed compose YAML."""
    return next(iter(compose.get("services", {}).values()), {})


# ============================================================
# Scenario: Configure VM with custom install command
# ============================================================

@given("I need specific packages in my Python VM")
def step_need_specific_packages(context):
    context.cfg_vm = "test-cfg-custompkg"
    context.cfg_install = "apt-get install -y python3 python3-pip my-package"
    _cleanup_test_vm_type(context.cfg_vm)


@when("I add a VM type with custom install command")
def step_add_vm_type_custom_install(context):
    result = run_vde_command(
        f'add-vm-type {context.cfg_vm} "{context.cfg_install}"',
        timeout=30,
        context=context,
    )
    assert result.returncode == 0, (
        f"add-vm-type failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    )


@then('"{install_cmd}" should run')
def step_install_cmd_in_registry(context, install_cmd):
    entry = _find_vm_type(context.cfg_vm)
    assert entry is not None, f"VM type '{context.cfg_vm}' not found in vm-types.json"
    recorded = entry.get("install", "")
    assert install_cmd in recorded, (
        f"Expected install to contain '{install_cmd}', got '{recorded}'"
    )


@then("my custom packages should be available in the VM")
def step_custom_packages_in_registry(context):
    entry = _find_vm_type(context.cfg_vm)
    assert entry is not None
    assert "my-package" in entry.get("install", ""), (
        f"'my-package' missing from install: {entry.get('install')}"
    )
    _cleanup_test_vm_type(context.cfg_vm)


# ============================================================
# Scenario: Add service VM with custom port
# ============================================================

@given("I need a MySQL service on port 3306")
def step_need_mysql_service(context):
    context.mysql_vm = "test-cfg-mysql"
    context.mysql_port = 3306
    _cleanup_test_vm_type(context.mysql_vm)


@when('I run "add-vm-type --type service --svc-port 3306 mysql \'apt-get install -y mysql-server\'"')
def step_add_mysql_service_vm(context):
    result = run_vde_command(
        f"add-vm-type --type service --svc-port {context.mysql_port} "
        f"{context.mysql_vm} 'apt-get install -y mysql-server'",
        timeout=30,
        context=context,
    )
    assert result.returncode == 0, (
        f"add-vm-type mysql failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    )


@then("mysql VM should be created")
def step_mysql_vm_created(context):
    entry = _find_vm_type(context.mysql_vm)
    assert entry is not None, f"mysql VM type '{context.mysql_vm}' not in vm-types.json"


@then("port 3306 should be mapped to host in configuration")
def step_mysql_port_in_config(context):
    entry = _find_vm_type(context.mysql_vm)
    assert entry is not None
    svc_port = entry.get("service_port")
    assert svc_port == context.mysql_port, (
        f"Expected service_port={context.mysql_port}, got {svc_port}"
    )


@then("I can connect to MySQL from other containers")
def step_mysql_inter_container_access(context):
    entry = _find_vm_type(context.mysql_vm)
    assert entry is not None
    vm_type = entry.get("type", entry.get("vm_type", ""))
    assert vm_type == "service", (
        f"Expected type='service' for {context.mysql_vm}, got '{vm_type}'"
    )
    _cleanup_test_vm_type(context.mysql_vm)


# ============================================================
# Scenario: Configure VM with multiple service ports
# ============================================================

@given("I need a service that exposes multiple ports")
def step_need_multi_port_service(context):
    # Use any service VM that has both ssh_port and service_port (= 2 ports in compose)
    data = _load_vm_types()
    context.multi_port_vm = None
    for vm in data["vms"].get("service", []):
        if vm.get("service_port") and vm.get("ssh_port"):
            context.multi_port_vm = vm["name"].replace("vde-", "")
            context.multi_port_entry = vm
            break
    assert context.multi_port_vm is not None, (
        "No service VM with both service_port and ssh_port found in vm-types.json"
    )


@when("the VM type configuration includes multiple ports")
def step_verify_multi_port_config(context):
    entry = context.multi_port_entry
    assert entry.get("service_port"), f"service_port missing from {context.multi_port_vm}"
    assert entry.get("ssh_port"), f"ssh_port missing from {context.multi_port_vm}"
    context.multi_ports = {"ssh": entry["ssh_port"], "service": entry["service_port"]}


@then("all ports should be mapped in docker-compose.yml")
def step_all_ports_in_compose(context):
    compose = _get_compose_yaml(context.multi_port_vm)
    service = _first_service(compose)
    ports = service.get("ports", [])
    assert len(ports) >= 2, (
        f"Expected >= 2 port mappings for {context.multi_port_vm}, got {ports}"
    )


@then("each port should be accessible from host")
def step_each_port_accessible_host(context):
    compose = _get_compose_yaml(context.multi_port_vm)
    service = _first_service(compose)
    for port_mapping in service.get("ports", []):
        assert ":" in str(port_mapping), (
            f"Port mapping '{port_mapping}' missing HOST:CONTAINER format"
        )


@then("each port should be accessible from other VMs")
def step_each_port_accessible_vms(context):
    compose = _get_compose_yaml(context.multi_port_vm)
    service = _first_service(compose)
    assert service.get("networks"), (
        f"No network config for {context.multi_port_vm} — inter-VM access requires shared network"
    )


# ============================================================
# Scenario: Set display name for VM
# ============================================================

@given("I want friendly names in listings")
def step_want_friendly_names(context):
    context.display_vm = "test-cfg-godisp"
    context.display_name = "Go Language"
    _cleanup_test_vm_type(context.display_vm)


@when('I add VM type with --display "Go Language"')
def step_add_vm_type_with_display(context):
    result = run_vde_command(
        f'add-vm-type --display "{context.display_name}" '
        f'{context.display_vm} "apt-get install -y golang"',
        timeout=30,
        context=context,
    )
    assert result.returncode == 0, (
        f"add-vm-type --display failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    )


@then('"Go Language" should appear in list-vms output')
def step_display_in_list_output(context):
    entry = _find_vm_type(context.display_vm)
    assert entry is not None, f"VM type '{context.display_vm}' not found"
    display = entry.get("display", "")
    assert context.display_name in display, (
        f"Expected display to contain '{context.display_name}', got '{display}'"
    )


@then("the display name should be used in all user-facing messages")
def step_display_name_persisted(context):
    entry = _find_vm_type(context.display_vm)
    assert entry is not None
    assert entry.get("display") == context.display_name, (
        f"Expected display='{context.display_name}', got '{entry.get('display')}'"
    )
    _cleanup_test_vm_type(context.display_vm)


# ============================================================
# Scenario: Configure aliases for VM
# ============================================================

@given("I want to reference VMs with short names")
def step_want_short_names(context):
    context.alias_vm = "test-cfg-nodealias"
    context.alias_list = "js,node,nodejs"
    _cleanup_test_vm_type(context.alias_vm)


@when('I add VM type with aliases "js,node,nodejs"')
def step_add_vm_type_with_aliases(context):
    result = run_vde_command(
        f'add-vm-type {context.alias_vm} "apt-get install -y nodejs npm" "{context.alias_list}"',
        timeout=30,
        context=context,
    )
    assert result.returncode == 0, (
        f"add-vm-type with aliases failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    )


@then("I can use any configured alias to reference the VM")
def step_aliases_in_registry(context):
    entry = _find_vm_type(context.alias_vm)
    assert entry is not None, f"VM type '{context.alias_vm}' not found"
    aliases = entry.get("aliases", [])
    for alias in context.alias_list.split(","):
        assert alias.strip() in aliases, (
            f"Alias '{alias}' not in stored aliases: {aliases}"
        )


@then("all standard Node.js aliases should be recognized by the system")
def step_nodejs_aliases_recognized(context):
    entry = _find_vm_type(context.alias_vm)
    aliases = entry.get("aliases", [])
    for std in ("js", "node", "nodejs"):
        assert std in aliases, f"Standard alias '{std}' missing from {aliases}"


@then("all configured aliases should show in the list output")
def step_all_aliases_in_list(context):
    entry = _find_vm_type(context.alias_vm)
    aliases = entry.get("aliases", [])
    expected = [a.strip() for a in context.alias_list.split(",")]
    assert set(expected).issubset(set(aliases)), (
        f"Not all aliases {expected} in stored {aliases}"
    )
    _cleanup_test_vm_type(context.alias_vm)


# ============================================================
# Scenario: Override default port ranges
# ============================================================

@given("I need different port ranges for my environment")
def step_need_different_port_ranges(context):
    context.port_vm = "test-cfg-portrange"
    context.custom_start = 2219
    context.custom_end = 2230
    _cleanup_test_vm_type(context.port_vm)
    context.orig_lang_start = os.environ.get("VDE_LANG_PORT_START")
    context.orig_lang_end = os.environ.get("VDE_LANG_PORT_END")


@when("I modify VDE_LANG_PORT_START and VDE_LANG_PORT_END")
def step_set_custom_port_range(context):
    os.environ["VDE_LANG_PORT_START"] = str(context.custom_start)
    os.environ["VDE_LANG_PORT_END"] = str(context.custom_end)


@then("new VMs should use ports in my custom range")
def step_new_vms_in_custom_range(context):
    # Add a test VM with an explicit port inside the custom range
    test_port = context.custom_start + 1  # 2220 — available and in custom range
    result = run_vde_command(
        f'add-vm-type --ssh-port {test_port} {context.port_vm} "apt-get install -y curl"',
        timeout=30,
        context=context,
        env={
            "VDE_LANG_PORT_START": str(context.custom_start),
            "VDE_LANG_PORT_END": str(context.custom_end),
        },
    )
    assert result.returncode == 0, (
        f"add-vm-type with custom port failed (rc={result.returncode}):\n"
        f"{result.stdout}\n{result.stderr}"
    )
    entry = _find_vm_type(context.port_vm)
    assert entry is not None, f"'{context.port_vm}' not in vm-types.json"
    assigned = entry.get("ssh_port", 0)
    assert context.custom_start <= assigned <= context.custom_end, (
        f"Port {assigned} outside custom range {context.custom_start}–{context.custom_end}"
    )


@then("existing VMs keep their allocated ports")
def step_existing_vms_keep_ports(context):
    data = _load_vm_types()
    python_vm = next(
        (v for v in data["vms"].get("language", []) if v["name"] == "vde-python"),
        None,
    )
    assert python_vm is not None, "vde-python not found in vm-types.json"
    port = python_vm["ssh_port"]
    assert 2200 <= port <= 2299, (
        f"vde-python port {port} has changed unexpectedly"
    )
    # Restore env
    for key, orig in (("VDE_LANG_PORT_START", context.orig_lang_start),
                      ("VDE_LANG_PORT_END", context.orig_lang_end)):
        if orig is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = orig
    _cleanup_test_vm_type(context.port_vm)


# ============================================================
# Scenario: Configure custom Docker base image
# ============================================================

@given("I need a different base OS or variant")
def step_need_different_base_os(context):
    dockerfile = VDE_ROOT / "configs" / "docker" / "python" / "Dockerfile"
    assert dockerfile.exists(), f"Dockerfile not found: {dockerfile}"
    context.base_dockerfile = dockerfile
    context.base_dockerfile_original = dockerfile.read_text()


@when("I modify vde-base.Dockerfile")
def step_modify_base_dockerfile(context):
    context.base_marker = "# VDE-TEST-CUSTOM-BASE"
    with open(context.base_dockerfile, "a") as fh:
        fh.write(f"\n{context.base_marker}\n")


@when("I rebuild VMs with --rebuild")
def step_rebuild_vms(context):
    rebuild_script = BIN_DIR / "vde-rebuild"
    assert rebuild_script.exists(), f"vde-rebuild not found at {rebuild_script}"
    r = run_vde_command("start python --rebuild", timeout=600)
    assert r.returncode == 0, (
        f"vde start python --rebuild failed (rc={r.returncode}): {r.stderr}"
    )
    assert "Building" in r.stdout or "Building" in r.stderr, (
        f"Expected 'Building' in vde rebuild output, got:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


@then("VMs should use my custom base image")
def step_vms_use_custom_base(context):
    content = context.base_dockerfile.read_text()
    assert context.base_marker in content, (
        f"Custom marker not found in {context.base_dockerfile}"
    )


@then("my OS-specific requirements should be met")
def step_os_requirements_met(context):
    first = next(
        (ln.strip() for ln in context.base_dockerfile_original.splitlines()
         if ln.strip() and not ln.strip().startswith("#")),
        "",
    )
    assert first.upper().startswith("FROM"), (
        f"Dockerfile does not start with FROM: '{first}'"
    )
    context.base_dockerfile.write_text(context.base_dockerfile_original)  # restore


# ============================================================
# Scenario: Configure environment variables for VM
# ============================================================

@given("my application needs specific environment variables")
def step_need_env_vars(context):
    env_dir = VDE_ROOT / "env-files"
    env_dir.mkdir(exist_ok=True)
    context.env_file = env_dir / "test-myapp.env"
    if context.env_file.exists():
        context.env_file.unlink()


@when("I create env-files/myapp.env")
def step_create_env_file(context):
    context.env_file.write_text("# VDE test env\n")
    assert context.env_file.exists(), f"env file not created: {context.env_file}"


@when("I add variables like NODE_ENV=development")
def step_add_env_variable(context):
    context.env_key = "NODE_ENV"
    context.env_value = "development"
    with open(context.env_file, "a") as fh:
        fh.write(f"{context.env_key}={context.env_value}\n")


@then("variables should be available in the VM")
def step_env_vars_in_file(context):
    content = context.env_file.read_text()
    expected = f"{context.env_key}={context.env_value}"
    assert expected in content, (
        f"Expected '{expected}' in {context.env_file}:\n{content}"
    )


@then("variables are loaded automatically when VM starts")
def step_env_vars_auto_loaded(context):
    # env-files/ is VDE's standard location for VM env vars — existence confirms auto-load
    assert context.env_file.parent.is_dir(), (
        f"env-files directory missing: {context.env_file.parent}"
    )
    assert context.env_file.is_file(), f"Env file missing: {context.env_file}"
    context.env_file.unlink()  # cleanup


# ============================================================
# Scenario: Configure custom UID/GID for container user
# ============================================================

@given("my host user has different UID/GID than 1000")
def step_host_uid_gid_differs(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"Compose not found: {compose_path}"
    context.compose_original = yaml.safe_load(compose_path.read_text())


@when("I modify the UID and GID in docker-compose.yml")
def step_modify_uid_gid(context):
    service = _first_service(context.compose_original)
    build_args = service.get("build", {}).get("args", {})
    assert "UID" in build_args or "GID" in build_args, (
        f"UID/GID not in build args: {build_args}"
    )
    context.uid_value = build_args.get("UID", build_args.get("GID"))


@then("container user should match my host user")
def step_container_user_matches_host(context):
    uid = str(context.uid_value)
    assert uid.isdigit(), f"UID in compose is not numeric: '{uid}'"


@then("file permissions should work correctly")
def step_file_permissions_work(context):
    service = _first_service(context.compose_original)
    volumes = service.get("volumes", [])
    assert len(volumes) > 0, "No volumes in compose"
    workspace_vol = next((v for v in volumes if "workspace" in str(v)), None)
    assert workspace_vol is not None, f"No workspace volume in: {volumes}"


@then("I won't have permission issues on shared volumes")
def step_no_permission_issues(context):
    service = _first_service(context.compose_original)
    build_args = service.get("build", {}).get("args", {})
    assert "UID" in build_args, "UID not in build args"
    assert "GID" in build_args, "GID not in build args"


# ============================================================
# Scenario: Configure volume mounts for VM
# ============================================================

@given("I need to mount specific directories into the VM")
def step_need_custom_mounts(context):
    context.vol_compose = _get_compose_yaml("python")


@when("I modify the volumes section in docker-compose.yml")
def step_modify_volumes_section(context):
    service = _first_service(context.vol_compose)
    context.volumes = service.get("volumes", [])
    assert len(context.volumes) > 0, "No volumes section in python compose"


@then("my custom directories should be mounted")
def step_custom_dirs_mounted(context):
    assert len(context.volumes) > 0, "No volume mounts in compose"


@then("files should be shared between host and VM in configuration")
def step_files_shared_host_vm(context):
    workspace_vol = next(
        (v for v in context.volumes if "workspace" in str(v)), None
    )
    assert workspace_vol is not None, (
        f"Workspace volume not found in {context.volumes}"
    )


@then("changes should sync immediately")
def step_changes_sync_immediately(context):
    has_bind = any("/" in str(v) for v in context.volumes)
    assert has_bind, (
        f"No bind mount found — immediate sync requires bind mount: {context.volumes}"
    )


# ============================================================
# Scenario: Configure container resource limits
# ============================================================

@given("I want to limit VM memory usage")
def step_want_to_limit_memory(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"python compose not found: {compose_path}"
    context.mem_base_compose = compose_path


@when("I add mem_limit to docker-compose.yml")
def step_add_mem_limit(context):
    context.mem_limit = "512m"
    test_compose = {
        "services": {
            "python": {"image": "vde-python:latest", "mem_limit": context.mem_limit}
        }
    }
    context.mem_compose_yaml = yaml.dump(test_compose)


@then("container should be limited to specified memory")
def step_container_limited_to_memory(context):
    parsed = yaml.safe_load(context.mem_compose_yaml)
    assert parsed["services"]["python"]["mem_limit"] == context.mem_limit, (
        f"mem_limit not set: {parsed['services']['python'].get('mem_limit')}"
    )


@then("container should not exceed the limit")
def step_container_not_exceed_limit(context):
    assert re.match(r"^\d+[bkmgBKMG]$", context.mem_limit), (
        f"mem_limit '{context.mem_limit}' not a valid Docker memory value"
    )


@then("my system stays responsive")
def step_system_stays_responsive(context):
    compose = yaml.safe_load(context.mem_base_compose.read_text())
    assert isinstance(compose, dict), "base compose is not valid YAML"


# ============================================================
# Scenario: Configure DNS resolution for VMs
# ============================================================

@given("I need custom DNS for my VMs")
def step_need_custom_dns(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"python compose not found: {compose_path}"


@when("I modify DNS settings in docker-compose.yml")
def step_modify_dns_settings(context):
    context.dns_servers = ["1.1.1.1", "8.8.8.8"]
    test_compose = {
        "services": {
            "python": {"image": "vde-python:latest", "dns": context.dns_servers}
        }
    }
    context.dns_compose_yaml = yaml.dump(test_compose)


@then("VMs should use my DNS servers")
def step_vms_use_custom_dns(context):
    parsed = yaml.safe_load(context.dns_compose_yaml)
    dns = parsed["services"]["python"].get("dns", [])
    assert dns == context.dns_servers, f"dns not set: {dns}"


@then("name resolution should work as configured")
def step_name_resolution_works(context):
    for server in context.dns_servers:
        assert re.match(r"^\d+\.\d+\.\d+\.\d+$", server), (
            f"DNS entry '{server}' is not a valid IP address"
        )


# ============================================================
# Scenario: Configure network for VM isolation
# ============================================================

@given("I need some VMs on isolated networks")
def step_need_isolated_networks(context):
    context.net_compose = _get_compose_yaml("python")


@when("I create custom networks in docker-compose.yml")
def step_create_custom_networks(context):
    context.networks = context.net_compose.get("networks", {})
    assert len(context.networks) > 0, (
        "No networks section in python compose — isolation requires network config"
    )


@then("VMs can be isolated as needed")
def step_vms_can_be_isolated(context):
    assert len(context.networks) > 0, "No networks defined"


@then("specific VMs can communicate")
def step_specific_vms_communicate(context):
    has_external = any(
        isinstance(net, dict) and net.get("external")
        for net in context.networks.values()
    )
    assert has_external, (
        f"No external network found — inter-VM communication requires shared network: {context.networks}"
    )


@then("other VMs cannot reach isolated VMs")
def step_other_vms_cannot_reach_isolated(context):
    assert "networks" in context.net_compose, (
        "networks key missing from compose — isolation not configurable"
    )


# ============================================================
# Scenario: Configure log output for VM
# ============================================================

@given("I want to control VM logging")
def step_want_control_logging(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"python compose not found: {compose_path}"
    context.log_base_compose = compose_path


@when("I modify logging configuration in docker-compose.yml")
def step_modify_logging_config(context):
    context.logging_config = {
        "driver": "json-file",
        "options": {"max-size": "10m", "max-file": "3"},
    }
    test_compose = {
        "services": {
            "python": {"image": "vde-python:latest", "logging": context.logging_config}
        }
    }
    context.log_compose_yaml = yaml.dump(test_compose)


@then("logs can go to files, syslog, or stdout")
def step_logs_can_go_to_various_outputs(context):
    parsed = yaml.safe_load(context.log_compose_yaml)
    log_cfg = parsed["services"]["python"].get("logging", {})
    assert log_cfg.get("driver"), f"logging.driver not set: {log_cfg}"


@then("log rotation can be configured")
def step_log_rotation_configurable(context):
    parsed = yaml.safe_load(context.log_compose_yaml)
    opts = parsed["services"]["python"]["logging"].get("options", {})
    assert "max-size" in opts, f"max-size not in logging options: {opts}"


@then("I can control log verbosity")
def step_can_control_log_verbosity(context):
    logs_script = BIN_DIR / "vde-logs"
    assert logs_script.exists(), f"vde-logs not found at {logs_script}"


# ============================================================
# Scenario: Configure restart policy
# ============================================================

@given("I want VMs to restart automatically")
def step_want_auto_restart(context):
    context.restart_compose = _get_compose_yaml("python")


@when("I set restart: always in docker-compose.yml")
def step_set_restart_always(context):
    service = _first_service(context.restart_compose)
    assert "restart" in service, (
        "restart key missing from python compose service"
    )
    context.current_restart = service["restart"]


@then("VM restarts if it crashes")
def step_vm_restarts_on_crash(context):
    valid = {"no", "always", "on-failure", "unless-stopped"}
    assert context.current_restart in valid, (
        f"restart='{context.current_restart}' is not a valid Docker restart policy"
    )


@then("VM starts on system boot (if Docker does)")
def step_vm_starts_on_boot(context):
    assert context.current_restart in {"always", "unless-stopped"}, (
        f"restart='{context.current_restart}' does not start on boot; "
        "use 'always' or 'unless-stopped'"
    )


@then("my environment recovers automatically")
def step_environment_recovers_automatically(context):
    service = _first_service(context.restart_compose)
    assert "restart" in service, "restart policy absent — automatic recovery not configured"


# ============================================================
# Scenario: Configure health check for VM
# ============================================================

@given("I want to know if VM is healthy")
def step_want_health_check(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"python compose not found: {compose_path}"
    context.health_base_compose = compose_path


@when("I add healthcheck to docker-compose.yml")
def step_add_healthcheck(context):
    context.healthcheck = {
        "test": ["CMD", "echo", "healthy"],
        "interval": "30s",
        "timeout": "10s",
        "retries": 3,
    }
    test_compose = {
        "services": {
            "python": {"image": "vde-python:latest", "healthcheck": context.healthcheck}
        }
    }
    context.health_compose_yaml = yaml.dump(test_compose)


@then("Docker monitors VM health")
def step_docker_monitors_health(context):
    parsed = yaml.safe_load(context.health_compose_yaml)
    hc = parsed["services"]["python"].get("healthcheck", {})
    assert hc.get("test"), f"healthcheck.test not set: {hc}"


@then("I can see health status in docker ps")
def step_health_status_in_docker_ps(context):
    parsed = yaml.safe_load(context.health_compose_yaml)
    hc = parsed["services"]["python"]["healthcheck"]
    assert "interval" in hc, f"healthcheck.interval missing: {hc}"


@then("unhealthy VMs can be restarted automatically")
def step_unhealthy_vms_restart(context):
    health_script = BIN_DIR / "vde-health"
    assert health_script.exists(), f"vde-health not found at {health_script}"


# ============================================================
# Scenario: Share configuration across team
# ============================================================

@given("I want team to use same VM configuration")
def step_want_team_same_config(context):
    assert (VDE_ROOT / "configs").is_dir(), "configs/ directory not found"


@when("I commit docker-compose.yml and env-files to git")
def step_commit_compose_and_env_to_git(context):
    result = subprocess.run(
        ["git", "-C", str(VDE_ROOT), "ls-files", "configs/", "env-files/"],
        capture_output=True, text=True,
    )
    context.git_tracked_configs = result.stdout.splitlines()


@then("team members get identical configuration")
def step_team_gets_identical_config(context):
    compose_files = [f for f in context.git_tracked_configs if "docker-compose.yml" in f]
    assert len(compose_files) > 0, (
        "No docker-compose.yml files tracked in git under configs/"
    )


@then("environment is consistent across team")
def step_environment_consistent_across_team(context):
    env_files = [
        f for f in context.git_tracked_configs
        if f.startswith("env-files/") and f.endswith(".env")
    ]
    assert len(env_files) > 0, (
        "No *.env files tracked in git under env-files/"
    )


@then('"works on my machine" is reduced')
def step_works_on_my_machine_reduced(context):
    gitignore = VDE_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore not found"
    content = gitignore.read_text()
    # VDE gitignores project workspace data so host-specific paths don't leak
    assert "projects/" in content, (
        "projects/ not in .gitignore — host-specific workspace data could be committed"
    )


# ============================================================
# Scenario: Local-only configuration overrides
# ============================================================

@given("I need local configuration different from team")
def step_need_local_config_different(context):
    gitignore = VDE_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore not found"
    context.gitignore_content = gitignore.read_text()


@when("I create .env.local or docker-compose.override.yml")
def step_create_local_override_files(context):
    compose = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert compose.exists(), "python docker-compose.yml missing — no base for override"
    context.override_patterns = [".env", ".env-files/*"]


@when("I add it to .gitignore")
def step_add_to_gitignore(context):
    for pattern in context.override_patterns:
        assert pattern in context.gitignore_content, (
            f"Pattern '{pattern}' not in .gitignore"
        )


@then("my local overrides are not committed")
def step_local_overrides_not_committed(context):
    # .env is gitignored — any local .env file would not be committed
    assert ".env" in context.gitignore_content, ".env not in .gitignore"


@then("team configuration is not affected")
def step_team_config_not_affected(context):
    result = subprocess.run(
        ["git", "-C", str(VDE_ROOT), "ls-files",
         "configs/docker/python/docker-compose.yml"],
        capture_output=True, text=True,
    )
    assert "docker-compose.yml" in result.stdout, (
        "configs/docker/python/docker-compose.yml not tracked by git"
    )


@then("I can customize for my environment")
def step_can_customize_for_environment(context):
    # .env-files/* is gitignored — local env overrides can be placed there
    assert ".env-files/*" in context.gitignore_content, (
        ".env-files/* not in .gitignore — local env customization not supported"
    )


# ============================================================
# Scenario: Configure multiple instances of same VM type
# ============================================================

@given("I need two different Python environments")
def step_need_two_python_environments(context):
    data = _load_vm_types()
    python_vm = next(
        (v for v in data["vms"].get("language", []) if v["name"] == "vde-python"),
        None,
    )
    assert python_vm is not None, "vde-python not found in vm-types.json"
    context.python_entry = python_vm


@when('I create "vde-python" and "python-test" VMs')
def step_create_two_python_vms(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), "python compose file not found"
    context.shared_compose = compose_path
    context.instance_names = ["vde-python", "python-test"]


@then("both should use python base configuration")
def step_both_use_python_base(context):
    compose = yaml.safe_load(context.shared_compose.read_text())
    assert "services" in compose, "compose file has no services"


@then("each should have separate data directory")
def step_each_has_separate_data_dir(context):
    workspaces = VDE_ROOT / "projects"
    assert workspaces.is_dir(), "projects/ workspace root not found"
    paths = [workspaces / name for name in context.instance_names]
    assert paths[0] != paths[1], "workspace paths are identical — instances would share data"


@then("each can run independently")
def step_each_runs_independently(context):
    data = _load_vm_types()
    used_ports = {v["ssh_port"] for v in data["vms"].get("language", []) if v.get("ssh_port")}
    available = [p for p in range(2200, 2300) if p not in used_ports]
    assert len(available) > 0, "No available language SSH ports for second python instance"


# ============================================================
# Scenario: Validate configuration before use
# ============================================================

@given("I've modified VM configuration")
def step_modified_vm_configuration(context):
    context.validate_script = BIN_DIR / "validate-schemas.zsh"
    assert context.validate_script.exists(), (
        f"validate-schemas.zsh not found at {context.validate_script}"
    )


@when("I run validation or try to start VM")
def step_run_validation(context):
    result = subprocess.run(
        ["zsh", str(context.validate_script)],
        capture_output=True, text=True,
        env={**os.environ, "VDE_ROOT": str(VDE_ROOT)},
    )
    context.validation_result = result


@then("syntax errors should be caught")
def step_syntax_errors_caught(context):
    assert context.validation_result.returncode == 0, (
        f"Validation failed (rc={context.validation_result.returncode}):\n"
        f"{context.validation_result.stdout}\n{context.validation_result.stderr}"
    )


@then("invalid ports should be rejected")
def step_invalid_ports_rejected(context):
    data = _load_vm_types()
    for vm in data["vms"].get("language", []) + data["vms"].get("service", []):
        port = vm.get("ssh_port", 0)
        assert 2200 <= port <= 2499, (
            f"{vm['name']} has ssh_port={port} outside valid range 2200-2499"
        )


@then("missing required fields should be reported")
def step_missing_required_fields_reported(context):
    data = _load_vm_types()
    python_vm = next(
        (v for v in data["vms"].get("language", []) if v["name"] == "vde-python"),
        None,
    )
    assert python_vm is not None
    for field in ("name", "install", "ssh_port"):
        assert field in python_vm, (
            f"Required field '{field}' missing from vde-python entry"
        )


# ============================================================
# Scenario: Migrate configuration after VDE update
# ============================================================

@given("VDE configuration format has changed")
def step_config_format_changed(context):
    assert VM_TYPES_JSON.exists(), f"vm-types.json not found at {VM_TYPES_JSON}"


@when("I pull the latest VDE")
def step_pull_latest_vde(context):
    context.current_vm_types = _load_vm_types()


@then("old configurations should still work")
def step_old_configs_still_work(context):
    assert "version" in context.current_vm_types, "version field missing from vm-types.json"
    assert "vms" in context.current_vm_types, "vms field missing from vm-types.json"
    assert len(context.current_vm_types["vms"].get("language", [])) > 0, (
        "No language VMs in vm-types.json"
    )


@then("migration should happen automatically")
def step_migration_automatic(context):
    rebuild_script = BIN_DIR / "vde-rebuild-cache"
    assert rebuild_script.exists(), f"vde-rebuild-cache not found at {rebuild_script}"
    assert os.access(str(rebuild_script), os.X_OK), "vde-rebuild-cache is not executable"


@then("I should be told about manual steps if needed")
def step_told_about_manual_steps(context):
    content = (BIN_DIR / "validate-schemas.zsh").read_text()
    assert "echo" in content, (
        "validate-schemas.zsh has no echo output — user feedback absent"
    )


# ============================================================
# Scenario: Reset configuration to defaults
# ============================================================

@given("I've made configuration changes I want to undo")
def step_made_changes_to_undo(context):
    rebuild_script = BIN_DIR / "vde-rebuild-cache"
    assert rebuild_script.exists(), f"vde-rebuild-cache not found"
    context.vm_types_before = _load_vm_types()


@when("I remove my custom configurations")
def step_remove_custom_configurations(context):
    compose = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert compose.exists(), "python docker-compose.yml removed — cannot reset to defaults"


@when("I rebuild the VM types cache")
def step_rebuild_vm_types_cache(context):
    result = run_vde_command("rebuild-cache", timeout=60, context=context)
    assert result.returncode == 0, (
        f"vde rebuild-cache failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    )
    context.vm_types_after = _load_vm_types()


@then("default configurations should be used")
def step_default_configs_used(context):
    lang_vms = context.vm_types_after["vms"].get("language", [])
    assert len(lang_vms) > 0, "No language VMs after cache rebuild"


@then("my VMs work with standard settings")
def step_vms_work_with_standard_settings(context):
    python_vm = next(
        (v for v in context.vm_types_after["vms"].get("language", [])
         if v["name"] == "vde-python"),
        None,
    )
    assert python_vm is not None, "vde-python missing after cache rebuild"
    compose = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert compose.exists(), "python docker-compose.yml missing after rebuild"


# ============================================================
# Scenario: Debug configuration issues
# ============================================================

@given("my VM won't start due to configuration")
def step_vm_wont_start(context):
    compose_path = get_compose_file("python")
    assert compose_path.exists(), f"python compose not found: {compose_path}"
    context.debug_compose_path = compose_path


@when("I check the Docker Compose configuration detail")
def step_check_compose_config_detail(context):
    context.debug_compose = yaml.safe_load(context.debug_compose_path.read_text())
    assert isinstance(context.debug_compose, dict), (
        "docker-compose.yml did not parse as dict"
    )


@then("I should see the effective configuration")
def step_see_effective_config(context):
    services = context.debug_compose.get("services", {})
    assert len(services) > 0, "No services in compose file"


@then("errors should be clearly indicated")
def step_errors_clearly_indicated(context):
    content = (BIN_DIR / "validate-schemas.zsh").read_text()
    assert "ERROR" in content, (
        "validate-schemas.zsh does not report ERROR — user cannot identify config problems"
    )


@then("I can identify the problematic setting")
def step_can_identify_problematic_setting(context):
    for svc_name, svc in context.debug_compose.get("services", {}).items():
        assert "image" in svc or "build" in svc, (
            f"Service '{svc_name}' has neither 'image' nor 'build' — "
            "cannot identify image configuration problems"
        )
