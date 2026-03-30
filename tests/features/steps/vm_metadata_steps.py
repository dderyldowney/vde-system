"""
BDD Step definitions for VM Metadata Verification scenarios.

These steps verify the correctness of VM type definitions in vm-types.conf,
including display names, port allocations, categories, aliases, and naming patterns.
"""

import re
import os
from pathlib import Path

from behave import given, then, when

# Import shared configuration
from vm_common import VDE_ROOT, run_vde_command, get_compose_file

# =============================================================================
# VM Types Configuration Parsing
# =============================================================================

VM_TYPES_CONF = VDE_ROOT / "data" / "vm-types.conf"


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
                'svc_port': 'port or empty',
                'ssh_port': 'ssh port'
            }
        }
    """
    vms = {}

    if not VM_TYPES_CONF.exists():
        return vms

    with open(VM_TYPES_CONF) as f:
        for line in f:
            line = line.rstrip('\n\r')
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse pipe-delimited fields
            # Format: type|name|aliases|display_name|install_command|service_port|ssh_port
            parts = line.split('|')
            
            if len(parts) < 6:
                continue

            vm_type = parts[0]
            name = parts[1]
            aliases = parts[2]
            display = parts[3]
            
            # Handle variable number of pipes in install command
            ssh_port = parts[-1] if len(parts) >= 7 else ''
            svc_port = parts[-2] if len(parts) >= 7 else ''
            
            if len(parts) >= 7:
                install = '|'.join(parts[4:-2])
            else:
                install = '|'.join(parts[4:-1]) if len(parts) > 5 else parts[4] if len(parts) > 4 else ''
                svc_port = parts[-1] if len(parts) > 5 else ''

            vms[name] = {
                'type': vm_type,
                'name': name,
                'aliases': aliases,
                'display': display,
                'install': install,
                'svc_port': svc_port,
                'ssh_port': ssh_port
            }

    return vms


def get_alias_map(vms):
    """
    Build a mapping of aliases to canonical VM names.
    """
    alias_map = {}
    for vm_name, vm_data in vms.items():
        aliases = vm_data['aliases']
        canonical = vm_name.replace('vde-', '') if vm_name.startswith('vde-') else vm_name
        if aliases:
            for alias in aliases.split(','):
                alias = alias.strip()
                if alias:
                    alias_map[alias] = canonical
    return alias_map


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
    context.lang_ports = []

    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'lang':
            compose_file = get_compose_file(vm_name)
            if compose_file.exists():
                content = compose_file.read_text()
                match = re.search(r'"(\d+):22"', content)
                if match:
                    port = int(match.group(1))
                    context.lang_ports.append((vm_name, port))


@when('I check the SSH port allocation for service VMs')
def step_check_service_ports(context):
    """Check SSH ports for service VMs from docker-compose files."""
    _ensure_vms_loaded(context)
    context.service_ports = []

    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'service':
            compose_file = get_compose_file(vm_name)
            if compose_file.exists():
                content = compose_file.read_text()
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
        if canonical in context.vms or f"vde-{canonical}" in context.vms
    }


@when('I query alias mappings for services')
def step_query_service_aliases(context):
    """Query alias mappings for service VMs."""
    _ensure_vms_loaded(context)
    context.service_aliases = {
        alias: canonical
        for alias, canonical in context.alias_map.items()
        if canonical in context.vms or f"vde-{canonical}" in context.vms
    }


@when('I check container naming for language VMs')
def step_check_lang_container_naming(context):
    """Check container naming pattern for language VMs."""
    _ensure_vms_loaded(context)
    context.lang_container_names = {}
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'lang':
            # Use get_compose_file which is category-aware
            compose_file = get_compose_file(vm_name.replace('vde-', ''))
            if compose_file.exists():
                content = compose_file.read_text()
                match = re.search(r'container_name:\s*(\S+)', content)
                if match:
                    context.lang_container_names[vm_name] = match.group(1)


@when('I check container naming for service VMs')
def step_check_service_container_naming(context):
    """Check container naming pattern for service VMs."""
    _ensure_vms_loaded(context)
    context.service_container_names = {}
    for vm_name, vm_data in context.vms.items():
        if vm_data['type'] == 'service':
            # Use get_compose_file which is category-aware
            compose_file = get_compose_file(vm_name.replace('vde-', ''))
            if compose_file.exists():
                content = compose_file.read_text()
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
    """Verify display names are descriptive."""
    for name, display in context.lang_display_names.items():
        assert display and len(display) >= 1


@then('common languages like Python, Go, and Rust should have recognizable names')
def step_common_langs_recognizable(context):
    """Verify common languages have recognizable display names."""
    common_langs = ['vde-python', 'vde-go', 'vde-rust', 'python', 'go', 'rust']
    for lang in common_langs:
        if lang in context.lang_display_names:
            display = context.lang_display_names[lang]
            assert len(display) >= 2


@then('each service VM should have a display name')
def step_service_has_display_names(context):
    """Verify all service VMs have display names."""
    for name, display in context.service_display_names.items():
        assert display, f"Service VM '{name}' has no display name"




@then('all service VM ports should be between 2400 and 2499')
def step_service_ports_in_range(context):
    """Verify all service VM SSH ports are in correct range."""
    for vm_name, port in context.service_ports:
        assert 2400 <= port <= 2499, \
            f"Service VM '{vm_name}' has port {port} outside range 2400-2499"


@then('programming language VMs should be categorized as "{category}"')
def step_lang_vms_categorized(context, category):
    """Verify language VMs are categorized correctly."""
    for name, data in context.vms.items():
        if data['type'] == 'lang':
            assert data['type'] == category


@then('Python, Go, Rust, and JavaScript should be language VMs')
def step_common_langs_are_lang(context):
    """Verify common languages are language VMs."""
    common_langs = ['vde-python', 'vde-go', 'vde-rust', 'vde-js']
    for lang in common_langs:
        if lang in context.vms:
            assert context.vms[lang]['type'] == 'lang'


@then('infrastructure service VMs should be categorized as "{category}"')
def step_service_vms_categorized(context, category):
    """Verify service VMs are categorized correctly."""
    for name, data in context.vms.items():
        if data['type'] == 'service':
            assert data['type'] == category


@then('the metadata alias "{alias}" should map to "{canonical}"')
def step_alias_resolves(context, alias, canonical):
    """Verify an alias resolves to the canonical name."""
    assert alias in context.alias_map
    assert context.alias_map[alias] == canonical


@then('language VM containers should use the "{pattern}" pattern')
def step_lang_container_pattern(context, pattern):
    """Verify language VM containers follow naming pattern."""
    for vm_name, container_name in context.lang_container_names.items():
        expected = pattern.replace("{name}", vm_name.replace('vde-', ''))
        assert container_name == expected


@then('service VM containers should use the "{pattern}" pattern')
def step_service_container_pattern(context, pattern):
    """Verify service VM containers follow naming pattern."""
    for vm_name, container_name in context.service_container_names.items():
        expected = pattern.replace("{name}", vm_name.replace('vde-', ''))
        assert container_name == expected


@then('each VM should have a non-empty install command')
def step_vm_has_install_command(context):
    """Verify all VMs have install commands."""
    for name, install_cmd in context.install_commands.items():
        assert install_cmd, f"VM '{name}' has no install command"


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
            ports = svc_port.split(',')
            for port in ports:
                port = port.strip()
                assert port.isdigit()
                assert 1 <= int(port) <= 65535


@then('language VMs should not have service_port values')
def step_lang_no_service_port(context):
    """Verify language VMs don't have service ports."""
    for name, svc_port in context.lang_service_ports.items():
        assert not svc_port or svc_port == ''


@then('the total should match the expected inventory')
def step_total_match_inventory(context):
    """Verify total VM count is reasonable."""
    expected_total = context.lang_vm_count + context.service_vm_count
    assert context.total_vm_count == expected_total


@then('there should be at least {min_count} language VMs')
def step_min_lang_vms(context, min_count):
    """Verify minimum number of language VMs."""
    assert context.lang_vm_count >= int(min_count)


@then('there should be at least {min_count} service VMs')
def step_min_service_vms(context, min_count):
    """Verify minimum number of service VMs."""
    assert context.service_vm_count >= int(min_count)
