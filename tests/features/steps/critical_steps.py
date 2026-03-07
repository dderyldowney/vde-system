"""
Step definitions for @critical-path and @critical-infrastructure features.

All steps invoke the ACTUAL VDE implementation — no mocks, no fakes.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

# ── paths ──────────────────────────────────────────────────────────────────
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from config import VDE_ROOT

BIN_DIR = VDE_ROOT / "bin"
TEMPLATES_DIR = VDE_ROOT / "templates"
LIB_DIR = VDE_ROOT / "lib"
VM_TYPES_JSON = VDE_ROOT / "data" / "vm-types.json"


# ── helpers ────────────────────────────────────────────────────────────────

def _zsh(script: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a zsh snippet with VDE libraries sourced."""
    full = f"""
export VDE_ROOT_DIR="{VDE_ROOT}"
source "{LIB_DIR}/vde-constants"
source "{LIB_DIR}/vde-naming"
{script}
"""
    return subprocess.run(
        ["zsh", "-c", full],
        capture_output=True, text=True, timeout=timeout
    )


def _zsh_with_common(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a zsh snippet with vde-constants + vm-common sourced (for render_template)."""
    full = f"""
export VDE_ROOT_DIR="{VDE_ROOT}"
source "{LIB_DIR}/vde-constants" 2>/dev/null
source "{LIB_DIR}/vm-common" 2>/dev/null
{script}
"""
    return subprocess.run(
        ["zsh", "-c", full],
        capture_output=True, text=True, timeout=timeout
    )


def _vde_cli(command: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run `vde <command>` with VDE_ROOT_DIR set. Logs go to stderr, stdout is clean output."""
    return subprocess.run(
        [str(BIN_DIR / "vde")] + command.split(),
        capture_output=True, text=True, timeout=timeout,
        env={**os.environ, "VDE_ROOT_DIR": str(VDE_ROOT), "VDE_LOG_OUTPUT": "stderr"},
    )


def _ssh_port_from_compose(vm_name: str) -> int | None:
    """Extract the host SSH port from a VM's docker-compose.yml."""
    compose = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if not compose.exists():
        return None
    m = re.search(r'"(\d+):22"', compose.read_text())
    return int(m.group(1)) if m else None


def _load_vm_types() -> tuple[list[str], list[str]]:
    """Return (lang_names, svc_names) as raw names (no vde- prefix)."""
    data = json.loads(VM_TYPES_JSON.read_text())
    langs = [v["name"].removeprefix("vde-") for v in data["vms"].get("language", [])]
    svcs  = [v["name"].removeprefix("vde-") for v in data["vms"].get("service", [])]
    return langs, svcs


# =============================================================================
# GIVEN steps
# =============================================================================

@given('VM "{vm_name}" config exists at "{path}"')
def step_vm_config_exists(context, vm_name, path):
    full = VDE_ROOT / path
    assert full.exists(), f"compose file not found: {full}"
    context.compose_path = full


@given('all language VM configs are loaded from vm-types.json')
def step_load_lang_vms(context):
    langs, _ = _load_vm_types()
    context.lang_vms = langs


@given('all service VM configs are loaded from vm-types.json')
def step_load_svc_vms(context):
    _, svcs = _load_vm_types()
    context.svc_vms = svcs


@given('all VM configs are loaded from vm-types.json')
def step_load_all_vms(context):
    langs, svcs = _load_vm_types()
    context.lang_vms = langs
    context.svc_vms = svcs


@given('container "{container_name}" is running')
def step_container_running(context, container_name):
    r = subprocess.run(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=10
    )
    if container_name not in r.stdout:
        # Try to start it
        vde_name = container_name.removeprefix("vde-")
        result = _vde_cli(f"start {vde_name}", timeout=120)
        assert result.returncode == 0, f"Could not start {vde_name}: {result.stderr}"
    context.container_name = container_name


# =============================================================================
# WHEN steps
# =============================================================================

@when('I run the list-vms script with "{args}"')
def step_run_list_vms(context, args):
    result = subprocess.run(
        [str(BIN_DIR / "list-vms")] + args.split(),
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "VDE_ROOT_DIR": str(VDE_ROOT)},
    )
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@when('I run vde-cli "{command}"')
def step_run_vde_cli(context, command):
    result = _vde_cli(command)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@when('I call vde_get_container_name with "{name}"')
def step_call_get_container_name(context, name):
    r = _zsh(f'vde_get_container_name "{name}"')
    assert r.returncode == 0, f"vde_get_container_name failed: {r.stderr}"
    context.zsh_result = r.stdout.strip()


@when('I call vde_get_ssh_host with "{name}"')
def step_call_get_ssh_host(context, name):
    r = _zsh(f'vde_get_ssh_host "{name}"')
    assert r.returncode == 0, f"vde_get_ssh_host failed: {r.stderr}"
    context.zsh_result = r.stdout.strip()


@when('I call vde_normalize_name with "{name}"')
def step_call_normalize_name(context, name):
    r = _zsh(f'vde_normalize_name "{name}"')
    assert r.returncode == 0, f"vde_normalize_name failed: {r.stderr}"
    context.zsh_result = r.stdout.strip()


@when('I read {constant} from vde-constants')
def step_read_constant(context, constant):
    r = _zsh(f'echo "${constant}"')
    assert r.returncode == 0, f"Failed reading {constant}: {r.stderr}"
    context.zsh_result = r.stdout.strip()


@when('I render the language template with NAME="{name}" SSH_PORT="{port}"')
def step_render_lang_template(context, name, port):
    template = TEMPLATES_DIR / "compose-language.yml"
    assert template.exists(), f"Template not found: {template}"
    r = _zsh_with_common(
        f'render_template "{template}" NAME "{name}" SSH_PORT "{port}" '
        f'INSTALL_CMD "echo test" SERVICE_PORT "" 2>/dev/null'
    )
    assert r.returncode == 0, f"render_template failed: {r.stderr}"
    # Strip log lines (lines starting with date or [INFO])
    lines = [ln for ln in r.stdout.splitlines()
             if not re.match(r'^\d{4}-\d{2}-\d{2}|^\[INFO\]', ln)]
    context.rendered_output = "\n".join(lines)


@when('I render the SSH entry template with VM_NAME="{vm_name}" SSH_PORT="{port}"')
def step_render_ssh_entry(context, vm_name, port):
    template = TEMPLATES_DIR / "ssh-entry.txt"
    assert template.exists(), f"Template not found: {template}"
    host = f"vde-{vm_name}"
    identity = "~/.ssh/vde/id_ed25519"
    known_hosts = "~/.ssh/vde/known_hosts"
    r = _zsh_with_common(
        f'render_template "{template}" HOST "{host}" SSH_PORT "{port}" '
        f'IDENTITY_FILE "{identity}" KNOWN_HOSTS_FILE "{known_hosts}" COMMENT "{vm_name}" 2>/dev/null'
    )
    assert r.returncode == 0, f"render_template failed: {r.stderr}"
    lines = [ln for ln in r.stdout.splitlines()
             if not re.match(r'^\d{4}-\d{2}-\d{2}|^\[INFO\]', ln)]
    context.rendered_output = "\n".join(lines)


@when('I check the VDE SSH directory path from vde-constants')
def step_check_ssh_dir(context):
    r = _zsh('echo "$VDE_SSH_DIR"')
    assert r.returncode == 0
    context.zsh_result = r.stdout.strip()


@when('I check the VDE SSH config path from vde-constants')
def step_check_ssh_config(context):
    r = _zsh('echo "$VDE_SSH_CONFIG"')
    assert r.returncode == 0
    context.zsh_result = r.stdout.strip()


@when('I check the VDE SSH known_hosts path from vde-constants')
def step_check_ssh_known_hosts(context):
    r = _zsh('echo "$VDE_SSH_KNOWN_HOSTS"')
    assert r.returncode == 0
    context.zsh_result = r.stdout.strip()


# =============================================================================
# THEN steps
# =============================================================================

@then('the compose file should contain "{text}"')
def step_compose_contains(context, text):
    content = context.compose_path.read_text()
    assert text in content, (
        f"Expected '{text}' in {context.compose_path}\n"
        f"Got:\n{content[:500]}"
    )


@then('every language VM compose file should have SSH port between {lo:d} and {hi:d}')
def step_lang_ports_in_range(context, lo, hi):
    errors = []
    for vm in context.lang_vms:
        port = _ssh_port_from_compose(vm)
        if port is None:
            continue  # VM not created yet; only check existing compose files
        elif not (lo <= port <= hi):
            errors.append(f"{vm}: port {port} not in {lo}-{hi}")
    assert not errors, "Port range violations:\n" + "\n".join(errors)


@then('every service VM compose file should have SSH port between {lo:d} and {hi:d}')
def step_svc_ports_in_range(context, lo, hi):
    errors = []
    for vm in context.svc_vms:
        port = _ssh_port_from_compose(vm)
        if port is None:
            continue  # VM not created yet; only check existing compose files
        elif not (lo <= port <= hi):
            errors.append(f"{vm}: port {port} not in {lo}-{hi}")
    assert not errors, "Port range violations:\n" + "\n".join(errors)


@then('no two VMs should share the same SSH port')
def step_unique_ports(context):
    all_vms = list(context.lang_vms) + list(context.svc_vms)
    ports: dict[int, str] = {}
    duplicates = []
    for vm in all_vms:
        port = _ssh_port_from_compose(vm)
        if port is None:
            continue
        if port in ports:
            duplicates.append(f"port {port} used by both '{ports[port]}' and '{vm}'")
        else:
            ports[port] = vm
    assert not duplicates, "Duplicate SSH ports:\n" + "\n".join(duplicates)


@then('the output should contain "{text}"')
def step_output_contains(context, text):
    assert text in context.command_output, (
        f"Expected '{text}' in output\nGot:\n{context.command_output}"
    )


@then('the output should NOT contain "{text}"')
def step_output_not_contains(context, text):
    assert text not in context.command_output, (
        f"Expected '{text}' NOT in output\nGot:\n{context.command_output}"
    )


@then('the exit code should be {code:d}')
def step_exit_code(context, code):
    assert context.command_exit_code == code, (
        f"Expected exit code {code}, got {context.command_exit_code}\n"
        f"Output:\n{context.command_output}"
    )


@then('container "{container_name}" should be running')
def step_container_is_running(context, container_name):
    r = _vde_cli(f"ps --filter name={container_name} -q", timeout=10)
    assert container_name in r.stdout, (
        f"Container '{container_name}' is not running.\nvde ps output: {r.stdout}"
    )


@then('container "{container_name}" should not be running')
def step_container_not_running(context, container_name):
    r = _vde_cli(f"ps --filter name={container_name} -q", timeout=10)
    assert container_name not in r.stdout, (
        f"Container '{container_name}' is still running."
    )


@then('container "{container_name}" should not exist')
def step_container_not_exist(context, container_name):
    r = _vde_cli(f"ps -a --filter name={container_name} -q", timeout=10)
    assert container_name not in r.stdout, (
        f"Container '{container_name}' still exists."
    )


@then('"{path}" should still exist')
def step_path_still_exists(context, path):
    full = VDE_ROOT / path
    assert full.exists(), f"Expected '{full}' to still exist but it is gone."


@then('VM "python" should be running')
def step_vm_python_running(context):
    step_container_is_running(context, "vde-python")


@then('VM "{vm_name}" should not be running')
def step_vm_not_running(context, vm_name):
    container = f"vde-{vm_name}" if not vm_name.startswith("vde-") else vm_name
    step_container_not_running(context, container)


@then('running container should be named "vde-python"')
def step_running_container_named(context):
    step_container_is_running(context, "vde-python")


@then('VM config should still exist for "python"')
def step_python_config_still_exists(context):
    compose = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert compose.exists(), f"compose file gone after stop: {compose}"


# ── critical-infrastructure THEN steps ────────────────────────────────────

@then('the result should be "{expected}"')
def step_result_equals(context, expected):
    assert context.zsh_result == expected, (
        f"Expected '{expected}', got '{context.zsh_result}'"
    )


@then('the value should be "{expected}"')
def step_value_equals(context, expected):
    assert context.zsh_result == expected, (
        f"Expected '{expected}', got '{context.zsh_result}'"
    )


@then('every VM compose file should have container_name starting with "vde-"')
def step_all_container_names_prefixed(context):
    all_vms = list(context.lang_vms) + list(context.svc_vms)
    errors = []
    for vm in all_vms:
        compose = VDE_ROOT / "configs" / "docker" / vm / "docker-compose.yml"
        if not compose.exists():
            continue  # VM not created yet; only check existing compose files
        text = compose.read_text()
        m = re.search(r'container_name:\s*(\S+)', text)
        if not m:
            errors.append(f"{vm}: no container_name in compose file")
        elif not m.group(1).startswith("vde-"):
            errors.append(f"{vm}: container_name '{m.group(1)}' missing vde- prefix")
    assert not errors, "Naming violations:\n" + "\n".join(errors)


@then('the rendered output should contain "{text}"')
def step_rendered_contains(context, text):
    assert text in context.rendered_output, (
        f"Expected '{text}' in rendered output\nGot:\n{context.rendered_output}"
    )


@then('the rendered output should NOT contain "{text}"')
def step_rendered_not_contains(context, text):
    assert text not in context.rendered_output, (
        f"Expected '{text}' NOT in rendered output\nGot:\n{context.rendered_output}"
    )


@then('the VDE_SSH_DIR should end with "{suffix}"')
def step_ssh_dir_suffix(context, suffix):
    assert context.zsh_result.endswith(suffix), (
        f"VDE_SSH_DIR '{context.zsh_result}' should end with '{suffix}'"
    )


@then('the VDE_SSH_CONFIG should end with "{suffix}"')
def step_ssh_config_suffix(context, suffix):
    assert context.zsh_result.endswith(suffix), (
        f"VDE_SSH_CONFIG '{context.zsh_result}' should end with '{suffix}'"
    )


@then('the VDE_SSH_KNOWN_HOSTS should end with "{suffix}"')
def step_ssh_known_hosts_suffix(context, suffix):
    assert context.zsh_result.endswith(suffix), (
        f"VDE_SSH_KNOWN_HOSTS '{context.zsh_result}' should end with '{suffix}'"
    )


@then('VDE directory "{rel_path}" should exist')
def step_vde_dir_exists(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.is_dir(), f"VDE directory '{full}' does not exist"


@then('VDE file "{rel_path}" should exist')
def step_vde_file_exists(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.is_file(), f"VDE file '{full}' does not exist"


# =============================================================================
# Error-path steps
# =============================================================================

@then('the exit code should not be 0')
def step_exit_code_nonzero(context):
    assert context.command_exit_code != 0, (
        f"Expected non-zero exit code, got 0\nOutput:\n{context.command_output}"
    )


@then('the command output should mention "{text}"')
def step_output_mentions(context, text):
    assert text.lower() in context.command_output.lower(), (
        f"Expected '{text}' (case-insensitive) in output\nGot:\n{context.command_output}"
    )


# =============================================================================
# Shell-compatibility steps (spec section 3.2)
# =============================================================================

_SHELL_COMPAT_INIT = f"""
export VDE_ROOT_DIR="{VDE_ROOT}"
source "{LIB_DIR}/vde-constants" 2>/dev/null
source "{LIB_DIR}/vde-shell-compat" 2>/dev/null || source "{LIB_DIR}/vm-common" 2>/dev/null
"""


def _zsh_compat(script: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["zsh", "-c", _SHELL_COMPAT_INIT + "\n" + script],
        capture_output=True, text=True, timeout=timeout
    )


@given('a new associative array "{arr_name}"')
def step_new_assoc_array(context, arr_name):
    context.assoc_array = arr_name


@given('key "{key}" is set to "{value}" in "{arr_name}"')
def step_key_preset(context, key, value, arr_name):
    r = _zsh_compat(f'_assoc_init "{arr_name}"; _assoc_set "{arr_name}" "{key}" "{value}"')
    assert r.returncode == 0, f"_assoc_set failed: {r.stderr}"
    if not hasattr(context, 'assoc_array'):
        context.assoc_array = arr_name
    if not hasattr(context, 'assoc_presets'):
        context.assoc_presets = []
    context.assoc_presets.append((arr_name, key, value))


@when('I set key "{key}" to value "{value}" in "{arr_name}"')
def step_assoc_set(context, key, value, arr_name):
    # Build init + all preset sets + this set
    presets = getattr(context, 'assoc_presets', [])
    preset_cmds = "".join(
        f'_assoc_set "{a}" "{k}" "{v}"\n' for a, k, v in presets
    )
    r = _zsh_compat(
        f'_assoc_init "{arr_name}"\n{preset_cmds}'
        f'_assoc_set "{arr_name}" "{key}" "{value}"\n'
        f'_assoc_get "{arr_name}" "{key}"'
    )
    assert r.returncode == 0, f"_assoc_set/_assoc_get failed: {r.stderr}"
    context.last_set_key = key
    context.last_set_arr = arr_name
    context.last_set_value = value
    # Track all sets for multi-step scenarios
    if not hasattr(context, 'assoc_sets'):
        context.assoc_sets = []
    context.assoc_sets.append((arr_name, key, value))


@then('getting key "{key}" from "{arr_name}" should return "{expected}"')
def step_assoc_get_expected(context, key, arr_name, expected):
    sets = getattr(context, 'assoc_sets', [])
    presets = getattr(context, 'assoc_presets', [])
    all_sets = presets + sets
    set_cmds = "".join(f'_assoc_set "{a}" "{k}" "{v}"\n' for a, k, v in all_sets)
    r = _zsh_compat(
        f'_assoc_init "{arr_name}"\n{set_cmds}'
        f'_assoc_get "{arr_name}" "{key}"'
    )
    assert r.returncode == 0, f"_assoc_get failed: {r.stderr}"
    actual = r.stdout.strip()
    assert actual == expected, f"key '{key}': expected '{expected}', got '{actual}'"


@when('I check if key "{key}" exists in "{arr_name}"')
def step_assoc_has_key_check(context, key, arr_name):
    presets = getattr(context, 'assoc_presets', [])
    set_cmds = "".join(f'_assoc_set "{a}" "{k}" "{v}"\n' for a, k, v in presets)
    r = _zsh_compat(
        f'_assoc_init "{arr_name}"\n{set_cmds}'
        f'_assoc_has_key "{arr_name}" "{key}"; echo $?'
    )
    assert r.returncode == 0, f"_assoc_has_key failed: {r.stderr}"
    context.has_key_result = r.stdout.strip()


@then('the key existence check should return true')
def step_key_exists_true(context):
    assert context.has_key_result == "0", (
        f"Expected key to exist (exit 0), got {context.has_key_result}"
    )


@then('the key existence check should return false')
def step_key_exists_false(context):
    assert context.has_key_result != "0", (
        f"Expected key not to exist (non-zero exit), got {context.has_key_result}"
    )


@when('I clear "{arr_name}"')
def step_assoc_clear(context, arr_name):
    presets = getattr(context, 'assoc_presets', [])
    set_cmds = "".join(f'_assoc_set "{a}" "{k}" "{v}"\n' for a, k, v in presets)
    r = _zsh_compat(
        f'_assoc_init "{arr_name}"\n{set_cmds}'
        f'_assoc_clear "{arr_name}"'
    )
    assert r.returncode == 0, f"_assoc_clear failed: {r.stderr}"
    context.cleared_array = arr_name
    context.assoc_presets = []


@then('key "{key}" should not exist in "{arr_name}"')
def step_key_not_in_array(context, key, arr_name):
    r = _zsh_compat(
        f'_assoc_init "{arr_name}"\n'
        f'_assoc_has_key "{arr_name}" "{key}"; echo $?'
    )
    result = r.stdout.strip()
    assert result != "0", f"Key '{key}' should not exist in '{arr_name}' but it does"


# =============================================================================
# Cache-system steps (spec section 2.3, 2.4)
# =============================================================================

@when('VM types are loaded via the vde script')
def step_load_vm_types(context):
    # Running any vde command triggers VM type loading and cache creation
    result = subprocess.run(
        [str(BIN_DIR / "list-vms"), "--all"],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "VDE_ROOT_DIR": str(VDE_ROOT)},
    )
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@given('"{rel_path}" exists')
def step_rel_path_exists(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.exists(), f"'{full}' does not exist — run 'list-vms' first to generate cache"
    context.cache_path = full


@when('I read the cache file')
def step_read_cache_file(context):
    cache = VDE_ROOT / ".cache" / "vm-types.cache"
    assert cache.exists(), f"Cache file not found: {cache}"
    context.cache_content = cache.read_text()


@then('the cache should contain "{text}"')
def step_cache_contains(context, text):
    assert text in context.cache_content, (
        f"Expected '{text}' in cache\nCache preview:\n{context.cache_content[:300]}"
    )


@then('"{rel_path}" should exist')
def step_rel_path_file_exists(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.exists(), f"'{full}' does not exist"


@then('"{rel_path}" should be a file inside the VDE root')
def step_rel_path_is_file(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.is_file(), f"'{full}' is not a regular file"
    assert str(full).startswith(str(VDE_ROOT)), f"'{full}' is outside VDE root"


@then('"{rel_path}" should exist as a directory')
def step_rel_path_is_dir(context, rel_path):
    full = VDE_ROOT / rel_path
    assert full.is_dir(), f"'{full}' is not a directory"


# =============================================================================
# Service template rendering steps (spec section 5.2)
# =============================================================================

@when('I render the service template with NAME="{name}" SSH_PORT="{port}" SERVICE_PORT="{svc_port}"')
def step_render_svc_template(context, name, port, svc_port):
    template = TEMPLATES_DIR / "compose-service.yml"
    assert template.exists(), f"Template not found: {template}"
    r = _zsh_with_common(
        f'render_template "{template}" NAME "{name}" SSH_PORT "{port}" '
        f'INSTALL_CMD "echo test" SERVICE_PORT "{svc_port}" 2>/dev/null'
    )
    assert r.returncode == 0, f"render_template failed: {r.stderr}"
    lines = [ln for ln in r.stdout.splitlines()
             if not re.match(r'^\d{4}-\d{2}-\d{2}|^\[INFO\]', ln)]
    context.rendered_output = "\n".join(lines)


# =============================================================================
# Permission policy steps (spec section 14.1)
# =============================================================================

@then('VDE directory "{rel_path}" should have permissions {octal}')
def step_vde_dir_permissions(context, rel_path, octal):
    full = VDE_ROOT / rel_path
    assert full.is_dir(), f"Directory '{full}' does not exist"
    mode = oct(full.stat().st_mode & 0o777)
    expected = oct(int(octal, 8))
    assert mode == expected, (
        f"'{rel_path}' has permissions {mode}, expected {expected}"
    )


@then('VDE SSH file "{filename}" should have permissions {octal}')
def step_vde_ssh_file_permissions(context, filename, octal):
    r = _zsh(f'echo "$VDE_SSH_DIR"')
    assert r.returncode == 0
    ssh_dir = Path(r.stdout.strip())
    full = ssh_dir / filename
    if not full.exists():
        context.scenario.skip(f"SSH file '{full}' does not exist (SSH not yet configured)")
        return
    mode = oct(full.stat().st_mode & 0o777)
    expected = oct(int(octal, 8))
    assert mode == expected, (
        f"'{filename}' has permissions {mode}, expected {expected}"
    )


# =============================================================================
# Network isolation steps (spec section 14.2)
# =============================================================================

@then('the Docker network "{network_name}" should exist')
def step_docker_network_exists(context, network_name):
    r = subprocess.run(
        ["docker", "network", "inspect", network_name],
        capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0, (
        f"Docker network '{network_name}' does not exist.\n"
        "Run 'vde setup' or 'vde start <vm>' to create it."
    )


@then('the Docker network "{network_name}" should be a bridge network')
def step_docker_network_is_bridge(context, network_name):
    r = subprocess.run(
        ["docker", "network", "inspect", network_name, "--format", "{{.Driver}}"],
        capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0, f"Could not inspect network '{network_name}'"
    driver = r.stdout.strip()
    assert driver == "bridge", (
        f"Network '{network_name}' driver is '{driver}', expected 'bridge'"
    )
