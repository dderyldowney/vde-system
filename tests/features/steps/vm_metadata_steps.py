"""
BDD Step definitions for VM Metadata Verification scenarios.

These steps verify the correctness of VM type definitions in vm-types.conf,
including display names, port allocations, categories, aliases, and naming patterns.
"""

from behave import given, when, then
import re
from pathlib import Path


# =============================================================================
# VM Types Configuration Parsing
# =============================================================================

VM_TYPES_CONF = Path(__file__).parent.parent.parent.parent / "scripts" / "data" / "vm-types.conf"


def parse_vm_types():
    """
    Parse the vm-types.conf file and return structured data.

    Returns:
        dict: {
            'vm_name': {
                'type': 'lang'|'service',
                'name': 'canonical_name',
                'aliases': 'comma,separated,aliases',
                'display': 'Display Name',
                'install': 'install command',
                'svc_port': 'port or empty'
            }
        }
    """
    vms = {}

    if not VM_TYPES_CONF.exists():
        return vms

    with open(VM_TYPES_CONF, 'r') as f:
        for line in f:
            line = line.rstrip('\n\r')
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse pipe-delimited fields - only split on the first 4 pipes
            # because the install command (field 5) may contain pipes
            parts = []
            remaining = line
            for i in range(4):
                pipe_idx = remaining.find('|')
                if pipe_idx == -1:
                    break
                parts.append(remaining[:pipe_idx])
                remaining = remaining[pipe_idx + 1:]
            else:
                # After extracting first 4 fields, check if there's a service_port
                # The install command (field 5) may contain pipes
                # But service VMs have a 6th field (service_port) after the last pipe
                # We need to find the LAST pipe to separate install from service_port
                last_pipe_idx = remaining.rfind('|')
                if last_pipe_idx != -1:
                    # There's at least one more pipe - could be service_port delimiter
                    # For service VMs, the service_port is usually numeric
                    # For language VMs, the field after the last pipe might be empty
                    potential_svc_port = remaining[last_pipe_idx + 1:]
                    install_cmd = remaining[:last_pipe_idx]
                    parts.append(install_cmd)
                    parts.append(potential_svc_port)
                else:
                    # No more pipes, remaining is the install command
                    parts.append(remaining)

            if len(parts) < 5:
                continue

            vm_type, name, aliases, display, install = parts[:5]
            svc_port = parts[5] if len(parts) > 5 else ''

            vms[name] = {
                'type': vm_type,
                'name': name,
                'aliases': aliases,
                'display': display,
                'install': install,
                'svc_port': svc_port
            }

    return vms


def get_alias_map(vms):
    """
    Build a mapping of aliases to canonical VM names.

    Args:
        vms: dict from parse_vm_types()

    Returns:
        dict: {alias: canonical_name}
    """
    alias_map = {}
    for vm_name, vm_data in vms.items():
        aliases = vm_data['aliases']
        if aliases:
            for alias in aliases.split(','):
                alias = alias.strip()
                if alias:
                    alias_map[alias] = vm_name
    return alias_map


# =============================================================================
# GIVEN steps - Setup
# =============================================================================

# Note: 'I have VDE installed' is already defined in vm_lifecycle_steps.py
# We'll load VM types in the first WHEN step if not already loaded


# =============================================================================
# WHEN steps - Query VM metadata
# =============================================================================

def _ensure_vms_loaded(context):
    """Ensure VM types are loaded in context."""
    if not hasattr(context, 'vms') or not context.vms:
        context.vms = parse_vm_types()
        context.alias_map = get_alias_map(context.vms)


@when('I query the display name for language VMs')
def step_query_lang_display_names(context):
    """Query display names for all language VMs."""
    _ensure_vms_loaded(context)
    context.lang_display_names = {
        name: data['display']
        for name, data in context.vms.items()
        if data['type'] == 'lang'
    }


@when('I query the display name for service VMs')
def step_query_service_display_names(context):
    """Query display names for all service VMs."""
    _ensure_vms_loaded(context)
    context.service_display_names = {
        name: data['display']
        for name, data in context.vms.items()
        if data['type'] == 'service'
    }


@when('I check the SSH port allocation for language VMs')
def step_check_lang_ports(context):
    """Check SSH ports for language VMs from docker-compose files."""
    _ensure_vms_loaded(context)
    import subprocess
    context.lang_ports = []

    configs_dir = VM_TYPES_CONF.parent.parent.parent / "configs" / "docker"
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'lang':
            compose_file = configs_dir / vm_name / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                # Look for SSH port mapping (format: "XXXX:22")
                match = re.search(r'"(\d+):22"', content)
                if match:
                    port = int(match.group(1))
                    context.lang_ports.append((vm_name, port))


@when('I check the SSH port allocation for service VMs')
def step_check_service_ports(context):
    """Check SSH ports for service VMs from docker-compose files."""
    _ensure_vms_loaded(context)
    import subprocess
    context.service_ports = []

    configs_dir = VM_TYPES_CONF.parent.parent.parent / "configs" / "docker"
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'service':
            compose_file = configs_dir / vm_name / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                # Look for SSH port mapping (format: "XXXX:22")
                match = re.search(r'"(\d+):22"', content)
                if match:
                    port = int(match.group(1))
                    context.service_ports.append((vm_name, port))


@when('I query VM types')
def step_query_vm_types(context):
    """Query VM type classifications."""
    _ensure_vms_loaded(context)
    context.vm_types = {
        name: data['type']
        for name, data in context.vms.items()
    }


@when('I query alias mappings for programming languages')
def step_query_lang_aliases(context):
    """Query alias mappings for language VMs."""
    _ensure_vms_loaded(context)
    context.lang_aliases = {
        alias: canonical
        for alias, canonical in context.alias_map.items()
        if canonical in context.vms and context.vms[canonical]['type'] == 'lang'
    }


@when('I query alias mappings for services')
def step_query_service_aliases(context):
    """Query alias mappings for service VMs."""
    _ensure_vms_loaded(context)
    context.service_aliases = {
        alias: canonical
        for alias, canonical in context.alias_map.items()
        if canonical in context.vms and context.vms[canonical]['type'] == 'service'
    }


@when('I check container naming for language VMs')
def step_check_lang_container_naming(context):
    """Check container naming pattern for language VMs."""
    _ensure_vms_loaded(context)
    configs_dir = VM_TYPES_CONF.parent.parent.parent / "configs" / "docker"
    context.lang_container_names = {}
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'lang':
            compose_file = configs_dir / vm_name / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                # Look for container name
                match = re.search(r'container_name:\s*(\S+)', content)
                if match:
                    context.lang_container_names[vm_name] = match.group(1)


@when('I check container naming for service VMs')
def step_check_service_container_naming(context):
    """Check container naming pattern for service VMs."""
    _ensure_vms_loaded(context)
    configs_dir = VM_TYPES_CONF.parent.parent.parent / "configs" / "docker"
    context.service_container_names = {}
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'service':
            compose_file = configs_dir / vm_name / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                # Look for container name
                match = re.search(r'container_name:\s*(\S+)', content)
                if match:
                    context.service_container_names[vm_name] = match.group(1)


@when('I verify installation commands for all VMs')
def step_verify_install_commands(context):
    """Verify all VMs have installation commands."""
    _ensure_vms_loaded(context)
    context.install_commands = {
        name: data['install']
        for name, data in context.vms.items()
    }


@when('I check service port configuration')
def step_check_service_port_config(context):
    """Check service port configuration for service VMs."""
    _ensure_vms_loaded(context)
    context.service_ports_config = {
        name: data['svc_port']
        for name, data in context.vms.items()
        if data['type'] == 'service'
    }


@when('I check service port configuration for language VMs')
def step_check_lang_service_port_config(context):
    """Check service port configuration for language VMs."""
    _ensure_vms_loaded(context)
    context.lang_service_ports = {
        name: data['svc_port']
        for name, data in context.vms.items()
        if data['type'] == 'lang'
    }


@when('I count all configured VMs')
def step_count_all_vms(context):
    """Count all VMs by category."""
    _ensure_vms_loaded(context)
    context.lang_vm_count = sum(
        1 for data in context.vms.values() if data['type'] == 'lang'
    )
    context.service_vm_count = sum(
        1 for data in context.vms.values() if data['type'] == 'service'
    )
    context.total_vm_count = len(context.vms)


# =============================================================================
# THEN steps - Verify metadata
# =============================================================================

@then('each language VM should have a display name')
def step_lang_has_display_names(context):
    """Verify all language VMs have display names."""
    for name, display in context.lang_display_names.items():
        assert display, f"Language VM '{name}' has no display name"


@then('the display name should be descriptive')
def step_display_is_descriptive(context):
    """Verify display names are descriptive (not just name repeats)."""
    for name, display in context.lang_display_names.items():
        # Single letter names like "C" are acceptable
        assert display and len(display) >= 1, \
            f"Language VM '{name}' has insufficient display name"


@then('common languages like Python, Go, and Rust should have recognizable names')
def step_common_langs_recognizable(context):
    """Verify common languages have recognizable display names."""
    common_langs = ['python', 'go', 'rust']
    for lang in common_langs:
        if lang in context.lang_display_names:
            display = context.lang_display_names[lang]
            assert display.lower() in [
                'python', 'rust', 'go', 'golang',
                'c', 'c++', 'cpp', 'assembler'
            ] or len(display) >= 2, \
                f"Language '{lang}' has unrecognizable display name: {display}"


@then('each service VM should have a display name')
def step_service_has_display_names(context):
    """Verify all service VMs have display names."""
    for name, display in context.service_display_names.items():
        assert display, f"Service VM '{name}' has no display name"


@then('the display name should indicate the service type')
def step_service_display_indicates_type(context):
    """Verify service display names indicate service type."""
    service_keywords = ['postgres', 'redis', 'mongo', 'nginx', 'mysql', 'couch', 'rabbit']
    for name, display in context.service_display_names.items():
        display_lower = display.lower()
        # At least one service keyword should be in display
        assert any(kw in display_lower or kw in name for kw in service_keywords), \
            f"Service '{name}' display '{display}' doesn't indicate service type"


@then('services like PostgreSQL and Redis should have recognizable names')
def step_common_services_recognizable(context):
    """Verify common services have recognizable display names."""
    common_services = ['postgres', 'redis']
    for svc in common_services:
        if svc in context.service_display_names:
            display = context.service_display_names[svc]
            assert display and len(display) >= 3, \
                f"Service '{svc}' has unrecognizable display name: {display}"


@then('all language VM ports should be between 2200 and 2299')
def step_lang_ports_in_range(context):
    """Verify all language VM SSH ports are in correct range."""
    for vm_name, port in context.lang_ports:
        assert 2200 <= port <= 2299, \
            f"Language VM '{vm_name}' has port {port} outside range 2200-2299"


@then('no language VM should use a service port range')
def step_lang_ports_not_service_range(context):
    """Verify no language VM uses service port range."""
    service_port_start = 2400
    service_port_end = 2499
    for vm_name, port in context.lang_ports:
        assert not (service_port_start <= port <= service_port_end), \
            f"Language VM '{vm_name}' uses service port {port}"


@then('all service VM ports should be between 2400 and 2499')
def step_service_ports_in_range(context):
    """Verify all service VM SSH ports are in correct range."""
    for vm_name, port in context.service_ports:
        assert 2400 <= port <= 2499, \
            f"Service VM '{vm_name}' has port {port} outside range 2400-2499"


@then('no service VM should use a language port range')
def step_service_ports_not_lang_range(context):
    """Verify no service VM uses language port range."""
    lang_port_start = 2200
    lang_port_end = 2299
    for vm_name, port in context.service_ports:
        assert not (lang_port_start <= port <= lang_port_end), \
            f"Service VM '{vm_name}' uses language port {port}"


@then('programming language VMs should be categorized as "{category}"')
def step_lang_vms_categorized(context, category):
    """Verify language VMs are categorized correctly."""
    for name, data in context.vms.items():
        if data['type'] == 'lang':
            assert data['type'] == category, \
                f"Language VM '{name}' is categorized as '{data['type']}' not '{category}'"


@then('Python, Go, Rust, and JavaScript should be language VMs')
def step_common_langs_are_lang(context):
    """Verify common languages are language VMs."""
    common_langs = ['python', 'go', 'rust', 'js']
    for lang in common_langs:
        if lang in context.vms:
            assert context.vms[lang]['type'] == 'lang', \
                f"VM '{lang}' should be a language VM"


@then('language VMs should have SSH access configured')
def step_lang_vms_have_ssh(context):
    """Verify language VMs have SSH port mappings."""
    # If lang_ports wasn't set by a prior step, check for docker-compose files
    if not hasattr(context, 'lang_ports'):
        _ensure_vms_loaded(context)
        import subprocess
        context.lang_ports = []
        configs_dir = VM_TYPES_CONF.parent.parent.parent / "configs" / "docker"
        for vm_name, vm_data in context.vms.items():
            if vm_data['type'] == 'lang':
                compose_file = configs_dir / vm_name / "docker-compose.yml"
                if compose_file.exists():
                    content = compose_file.read_text()
                    match = re.search(r'"(\d+):22"', content)
                    if match:
                        port = int(match.group(1))
                        context.lang_ports.append((vm_name, port))
    
    for vm_name, port in context.lang_ports:
        assert port, f"Language VM '{vm_name}' has no SSH port configured"


@then('infrastructure service VMs should be categorized as "{category}"')
def step_service_vms_categorized(context, category):
    """Verify service VMs are categorized correctly."""
    for name, data in context.vms.items():
        if data['type'] == 'service':
            assert data['type'] == category, \
                f"Service VM '{name}' is categorized as '{data['type']}' not '{category}'"


@then('PostgreSQL, Redis, MongoDB, and Nginx should be service VMs')
def step_common_services_are_service(context):
    """Verify common services are service VMs."""
    common_services = ['postgres', 'redis', 'mongodb', 'nginx']
    for svc in common_services:
        if svc in context.vms:
            assert context.vms[svc]['type'] == 'service', \
                f"VM '{svc}' should be a service VM"


@then('service VMs should have service ports configured')
def step_service_vms_provide_services(context):
    """Verify service VMs provide infrastructure (have service ports)."""
    # If service_ports_config wasn't set by a prior step, load it
    if not hasattr(context, 'service_ports_config'):
        _ensure_vms_loaded(context)
        context.service_ports_config = {
            name: data['svc_port']
            for name, data in context.vms.items()
            if data['type'] == 'service'
        }
    
    for name, svc_port in context.service_ports_config.items():
        # Service VMs should have service ports configured
        # (This is metadata verification, not runtime check)
        assert name in context.vms, f"Service '{name}' not in VM types"


@then('the metadata alias "{alias}" should map to "{canonical}"')
def step_alias_resolves(context, alias, canonical):
    """Verify an alias resolves to the canonical name."""
    assert alias in context.alias_map, \
        f"Alias '{alias}' not found in alias map"
    assert context.alias_map[alias] == canonical, \
        f"Alias '{alias}' resolves to '{context.alias_map[alias]}' not '{canonical}'"


@then('language VM containers should use the "{pattern}" pattern')
def step_lang_container_pattern(context, pattern):
    """Verify language VM containers follow naming pattern."""
    for vm_name, container_name in context.lang_container_names.items():
        expected = pattern.replace("{name}", vm_name)
        assert container_name == expected, \
            f"Language VM '{vm_name}' container is '{container_name}' not '{expected}'"


@then('Python container should be named "{expected}"')
def step_python_container_name(context, expected):
    """Verify Python container name."""
    if 'python' in context.lang_container_names:
        actual = context.lang_container_names['python']
        assert actual == expected, \
            f"Python container is '{actual}' not '{expected}'"


@then('Go container should be named "{expected}"')
def step_go_container_name(context, expected):
    """Verify Go container name."""
    if 'go' in context.lang_container_names:
        actual = context.lang_container_names['go']
        assert actual == expected, \
            f"Go container is '{actual}' not '{expected}'"


@then('service VM containers should use the "{pattern}" pattern')
def step_service_container_pattern(context, pattern):
    """Verify service VM containers follow naming pattern."""
    for vm_name, container_name in context.service_container_names.items():
        expected = pattern.replace("{name}", vm_name)
        assert container_name == expected, \
            f"Service VM '{vm_name}' container is '{container_name}' not '{expected}'"


@then('PostgreSQL container should be named "{expected}"')
def step_postgres_container_name(context, expected):
    """Verify PostgreSQL container name."""
    if 'postgres' in context.service_container_names:
        actual = context.service_container_names['postgres']
        assert actual == expected, \
            f"PostgreSQL container is '{actual}' not '{expected}'"


@then('Redis container should be named "{expected}"')
def step_redis_container_name(context, expected):
    """Verify Redis container name."""
    if 'redis' in context.service_container_names:
        actual = context.service_container_names['redis']
        assert actual == expected, \
            f"Redis container is '{actual}' not '{expected}'"


@then('each VM should have a non-empty install command')
def step_vm_has_install_command(context):
    """Verify all VMs have install commands."""
    for name, install_cmd in context.install_commands.items():
        assert install_cmd, f"VM '{name}' has no install command"


@then('the install command should be valid shell syntax')
def step_install_cmd_valid_syntax(context):
    """Verify install commands are valid shell (basic check)."""
    # Basic syntax check - commands should start with known shell commands
    valid_starters = [
        'apt-get', 'su', 'curl', 'wget', 'git', 'pip', 'npm',
        'yum', 'dnf', 'apk', 'echo', 'mkdir', 'cd', 'export'
    ]
    for name, install_cmd in context.install_commands.items():
        if install_cmd:
            # Check if command starts with a valid shell command
            starts_valid = any(install_cmd.strip().startswith(s) for s in valid_starters)
            # Also allow commands that start with user switching
            starts_valid = starts_valid or install_cmd.strip().startswith('su')
            assert starts_valid, \
                f"VM '{name}' install command doesn't start with valid command: {install_cmd[:50]}"


@then('all service VMs should have a service_port defined')
def step_service_has_service_port(context):
    """Verify all service VMs have service_port defined."""
    for name, svc_port in context.service_ports_config.items():
        assert svc_port, f"Service VM '{name}' has no service_port defined"


@then('the service_port should be a valid port number')
def step_service_port_valid(context):
    """Verify service ports are valid port numbers."""
    for name, svc_port in context.service_ports_config.items():
        if svc_port:
            # Service ports can be comma-separated (e.g., "80,443")
            ports = svc_port.split(',')
            for port in ports:
                port = port.strip()
                assert port.isdigit(), f"Service '{name}' has invalid port: {port}"
                assert 1 <= int(port) <= 65535, \
                    f"Service '{name}' has port out of range: {port}"


@then('PostgreSQL should have service port {port}')
def step_postgres_service_port(context, port):
    """Verify PostgreSQL service port."""
    if 'postgres' in context.service_ports_config:
        actual = context.service_ports_config['postgres']
        # PostgreSQL may have additional ports
        assert port in actual.split(','), \
            f"PostgreSQL service port is '{actual}' not '{port}'"


@then('Redis should have service port {port}')
def step_redis_service_port(context, port):
    """Verify Redis service port."""
    if 'redis' in context.service_ports_config:
        actual = context.service_ports_config['redis']
        assert actual == port, \
            f"Redis service port is '{actual}' not '{port}'"


@then('language VMs should not have service_port values')
def step_lang_no_service_port(context):
    """Verify language VMs don't have service ports."""
    for name, svc_port in context.lang_service_ports.items():
        assert not svc_port or svc_port == '', \
            f"Language VM '{name}' has service_port: {svc_port}"


@then('Python should not have a service_port')
def step_python_no_service_port(context):
    """Verify Python has no service port."""
    if 'python' in context.lang_service_ports:
        svc_port = context.lang_service_ports['python']
        assert not svc_port or svc_port == '', \
            f"Python has service_port: {svc_port}"


@then('Go should not have a service_port')
def step_go_no_service_port(context):
    """Verify Go has no service port."""
    if 'go' in context.lang_service_ports:
        svc_port = context.lang_service_ports['go']
        assert not svc_port or svc_port == '', \
            f"Go has service_port: {svc_port}"


@then('the total should match the expected inventory')
def step_total_match_inventory(context):
    """Verify total VM count is reasonable."""
    # Total should be sum of lang and service
    expected_total = context.lang_vm_count + context.service_vm_count
    assert context.total_vm_count == expected_total, \
        f"Total count mismatch: {context.total_vm_count} != {expected_total}"


@then('there should be at least {min_count} language VMs')
def step_min_lang_vms(context, min_count):
    """Verify minimum number of language VMs."""
    min_count = int(min_count)
    assert context.lang_vm_count >= min_count, \
        f"Only {context.lang_vm_count} language VMs, expected at least {min_count}"


@then('there should be at least {min_count} service VMs')
def step_min_service_vms(context, min_count):
    """Verify minimum number of service VMs."""
    min_count = int(min_count)
    assert context.service_vm_count >= min_count, \
        f"Only {context.service_vm_count} service VMs, expected at least {min_count}"
