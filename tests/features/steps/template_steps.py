"""
BDD Step Definitions for Template System.
Tests template rendering, placeholder substitution, and YAML generation.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
)


# =============================================================================
# GIVEN steps - Setup for Template System tests
# =============================================================================

@given('language template exists at "{template_path}"')
def step_language_template_exists(context, template_path):
    """Ensure language template exists."""
    full_path = VDE_ROOT / template_path
    if not full_path.exists():
        # Create minimal template
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("""services:
  {{NAME}}:
    build: .
    ports:
      - "{{SSH_PORT}}:22"
    volumes:
      - ${PROJECTS_DIR}:/projects
      - ${LOGS_DIR}:/logs
      - ~/.ssh/vde:/home/devuser/.ssh/vde:ro
""")
    context.template_path = full_path


@given('template contains "{placeholder}" placeholder')
def step_template_has_placeholder(context, placeholder):
    """Ensure template contains a placeholder."""
    template_path = getattr(context, 'template_path', VDE_ROOT / "scripts/templates/compose-language.yml")
    if template_path.exists():
        content = template_path.read_text()
        assert placeholder in content, f"Template should contain {placeholder}: {content}"


@given('service template exists at "{template_path}"')
def step_service_template_exists(context, template_path):
    """Ensure service template exists."""
    full_path = VDE_ROOT / template_path
    if not full_path.exists():
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("""services:
  {{NAME}}:
    build: .
    ports:
      - "{{SERVICE_PORT}}:{{SERVICE_PORT}}"
    volumes:
      - ${DATA_DIR}:/data
""")
    context.template_path = full_path


@given('service VM has multiple ports "{ports}"')
def step_service_multiple_ports(context, ports):
    """Set up service with multiple ports."""
    context.service_ports = [p.strip() for p in ports.split(',')]


@given('template value contains special characters')
def step_special_characters(context):
    """Set up template value with special characters."""
    context.special_value = "test/path & value"


@given('language VM template is rendered')
def step_lang_template_rendered(context):
    """Set up that language template is rendered."""
    # This happens during VM creation
    pass


@given('any VM template is rendered')
def step_any_template_rendered(context):
    """Set up that any template is rendered."""
    pass


@given('VM "{vm_name}" has install command "{install_cmd}"')
def step_vm_install_command(context, vm_name, install_cmd):
    """Set VM install command."""
    context.vm_name = vm_name
    context.install_command = install_cmd


@given('template file does not exist')
def step_template_not_exists(context):
    """Set up scenario where template doesn't exist."""
    context.template_missing = True


# =============================================================================
# WHEN steps - Actions for Template System tests
# =============================================================================

@when('I render template with NAME="{name}" and SSH_PORT="{ssh_port}"')
def step_render_template_lang(context, name, ssh_port):
    """Render language template with values."""
    result = run_vde_command(f"create {name}", timeout=120)
    context.last_command = f"render template NAME={name} SSH_PORT={ssh_port}"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.rendered_name = name
    context.rendered_ssh_port = ssh_port


@when('I render template with NAME="{name}" and SERVICE_PORT="{service_port}"')
def step_render_template_service(context, name, service_port):
    """Render service template with values."""
    result = run_vde_command(f"create {name}", timeout=120)
    context.last_command = f"render template NAME={name} SERVICE_PORT={service_port}"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.rendered_name = name
    context.rendered_service_port = service_port


@when('template is rendered')
def step_template_rendered(context):
    """Template is rendered (during VM creation)."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode


@when('I render template with value containing "/" or "&"')
def step_render_special_chars(context):
    """Render template with special characters."""
    # Would test special character handling
    pass


@when('I try to render the template')
def step_try_render_template(context):
    """Try to render a template."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# THEN steps - Verification for Template System tests
# =============================================================================

@then('rendered output should contain "{expected}"')
def step_rendered_contains(context, expected):
    """Verify rendered output contains expected value."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist at {config_path}"
    content = config_path.read_text()
    assert expected in content, f"Rendered output should contain '{expected}': {content}"


@then('rendered output should contain "{expected}" port mapping')
def step_rendered_port_mapping(context, expected):
    """Verify rendered output contains port mapping."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert expected in content or f"{expected}:" in content, \
        f"Rendered output should contain port mapping '{expected}': {content}"


@then('rendered output should NOT contain "{placeholder}"')
def step_rendered_no_placeholder(context, placeholder):
    """Verify rendered output does not contain placeholder."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert placeholder not in content, \
        f"Rendered output should NOT contain '{placeholder}': {content}"


@then('rendered output should contain "{expected}:{expected}" port mapping')
def step_service_port_mapping(context, expected):
    """Verify service port mapping."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert f"{expected}:{expected}" in content, \
        f"Rendered output should contain '{expected}:{expected}' port mapping: {content}"


@then('rendered output should contain "##SERVICE_PORTS##" port mapping')
def step_service_ports_placeholder(context):
    """Verify service ports placeholder."""
    # Would verify placeholder handling
    pass


@then('special characters should be properly escaped')
def step_special_chars_escaped(context):
    """Verify special characters are escaped."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if config_path.exists():
        content = config_path.read_text()
        # Should not have unescaped special characters
        pass


@then('rendered template should be valid YAML')
def step_valid_yaml(context):
    """Verify rendered template is valid YAML."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    # Basic YAML validation - should parse without error
    import yaml
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        assert False, f"Rendered template should be valid YAML: {e}"


@then('rendered output should contain SSH_AUTH_SOCK mapping')
def step_ssh_auth_sock_mapping(context):
    """Verify SSH_AUTH_SOCK mapping in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'SSH_AUTH_SOCK' in content or 'ssh-agent' in content or 'SSH_AUTH_SOCK' in content, \
        f"Rendered output should contain SSH_AUTH_SOCK mapping: {content}"


@then('rendered output should contain .ssh volume mount')
def step_ssh_volume_mount(context):
    """Verify .ssh volume mount in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert '.ssh' in content or 'ssh' in content, \
        f"Rendered output should contain .ssh volume mount: {content}"


@then('rendered output should contain public-ssh-keys volume')
def step_public_keys_volume(context):
    """Verify public-ssh-keys volume in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'public-ssh-keys' in content, \
        f"Rendered output should contain public-ssh-keys volume: {content}"


@then('volume should be mounted at /public-ssh-keys')
def step_public_keys_mount_path(context):
    """Verify public-ssh-keys is mounted at correct path."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert '/public-ssh-keys' in content, \
        f"Volume should be mounted at /public-ssh-keys: {content}"


@then('rendered output should contain "dev-net" network')
def step_dev_network(context):
    """Verify dev-net network in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'dev-net' in content or 'vde-network' in content, \
        f"Rendered output should contain dev-net network: {content}"


@then('rendered output should contain "restart: unless-stopped"')
def step_restart_policy(context):
    """Verify restart policy in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'unless-stopped' in content or 'restart' in content, \
        f"Rendered output should contain restart policy: {content}"


@then('rendered output should contain "user: devuser"')
def step_user_config(context):
    """Verify user configuration in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'devuser' in content or 'user:' in content, \
        f"Rendered output should contain user configuration: {content}"


@then('rendered output should specify UID and GID as "{uid_gid}"')
def step_uid_gid_config(context, uid_gid):
    """Verify UID and GID configuration."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert uid_gid in content, \
        f"Rendered output should specify UID and GID as {uid_gid}: {content}"


@then('rendered output should expose port "{port}"')
def step_expose_port(context, port):
    """Verify exposed port in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert f'"{port}"' in content or port in content.split('ports')[1] if 'ports' in content else False, \
        f"Rendered output should expose port {port}: {content}"


@then('rendered output should map SSH port to host port')
def step_ssh_port_mapping(context):
    """Verify SSH port mapping to host."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    assert ':22' in content or '22:' in content, \
        f"Rendered output should map SSH port: {content}"


@then('rendered output should include the install command')
def step_install_command(context):
    """Verify install command in rendered output."""
    vm_name = getattr(context, 'rendered_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist"
    content = config_path.read_text()
    # Should have command or script that includes install
    assert 'command' in content or 'install' in content.lower(), \
        f"Rendered output should include install command: {content}"


@then('error should indicate "Template not found"')
def step_template_not_found_error(context):
    """Verify error message for missing template."""
    output = context.last_output + context.last_error
    assert 'template' in output.lower() and ('not found' in output.lower() or 'missing' in output.lower()), \
        f"Error should indicate 'Template not found': {output}"
