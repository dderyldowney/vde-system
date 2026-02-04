"""
BDD Step Definitions for Template System features.

These steps test the template rendering system for VM configurations.
"""
import os
import sys

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import os
import re
import subprocess
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# VDE_ROOT imported from config


# =============================================================================
# Template System GIVEN Steps
# =============================================================================

@given('language template exists at "{path}"')
def step_language_template_exists(context, path):
    """Language template exists at given path."""
    template_path = VDE_ROOT / "scripts" / "templates" / Path(path).name
    context.template_exists = template_path.exists()
    context.template_path = template_path


@given('template contains "{{{{NAME}}}}" placeholder')
def step_template_contains_name_placeholder(context):
    """Template contains NAME placeholder."""
    context.has_name_placeholder = True


@given('template contains "{{{{SSH_PORT}}}}" placeholder')
def step_template_contains_ssh_port_placeholder(context):
    """Template contains SSH_PORT placeholder."""
    context.has_ssh_port_placeholder = True


@given('service template exists at "{path}"')
def step_service_template_exists(context, path):
    """Service template exists at given path."""
    template_path = VDE_ROOT / "scripts" / "templates" / Path(path).name
    context.template_exists = template_path.exists()
    context.template_path = template_path


@given('template contains "{{{{SERVICE_PORT}}}}" placeholder')
def step_template_contains_service_port_placeholder(context):
    """Template contains SERVICE_PORT placeholder."""
    context.has_service_port_placeholder = True


@given('service VM has multiple ports "{ports}"')
def step_service_vm_multiple_ports(context, ports):
    """Service VM has multiple ports."""
    context.service_ports = ports.split(",")
    context.template_type = "service"  # Mark as service template


@given('template value contains special characters')
def step_template_special_chars(context):
    """Template value contains special characters."""
    context.has_special_chars = True


@when('template is rendered')
def step_template_rendered(context):
    """Template is rendered using real template."""
    template_type = getattr(context, 'template_type', 'language')

    if template_type == 'service':
        template_path = VDE_ROOT / "scripts/templates/compose-service.yml"
        if template_path.exists():
            # Render with SERVICE_PORT variable
            service_ports = getattr(context, 'service_ports', None)
            port_value = service_ports if service_ports else "8080"
            result = subprocess.run(
                f"source {VDE_ROOT}/scripts/lib/vm-common && "
                f"render_template '{template_path}' NAME 'test' SERVICE_PORT '{port_value}'",
                shell=True, capture_output=True, text=True, cwd=VDE_ROOT
            )
            context.rendered_output = result.stdout
            context.template_rendered = result.returncode == 0
        else:
            raise AssertionError(f"Template file not found: {template_path}")


@when('template is rendered with NAME="{name}" and SSH_PORT="{port}"')
def step_render_template_with_values(context, name, port):
    """Render template with specific NAME and SSH_PORT values."""
    template_path = VDE_ROOT / "scripts/templates/compose-language.yml"
    if template_path.exists():
        result = subprocess.run(
            f"source {VDE_ROOT}/scripts/lib/vm-common && "
            f"render_template '{template_path}' NAME '{name}' SSH_PORT '{port}'",
            shell=True, capture_output=True, text=True, cwd=VDE_ROOT
        )
        context.rendered_output = result.stdout
        context.template_rendered = result.returncode == 0
    else:
        context.template_rendered = False


# =============================================================================
# Template System THEN Steps (Missing - Added 2026-02-02)
# =============================================================================

@then('rendered output should contain "{value}"')
def step_rendered_contains_value(context, value):
    """Verify rendered output contains expected value."""
    rendered = getattr(context, 'rendered_output', '')
    assert value in rendered, f"Rendered output should contain '{value}'"


@then('rendered output should NOT contain "{value}"')
def step_rendered_not_contains_value(context, value):
    """Verify rendered output does NOT contain expected value."""
    rendered = getattr(context, 'rendered_output', '')
    assert value not in rendered, f"Rendered output should NOT contain '{value}'"


@then('rendered output should contain "{mapping}" port mapping')
def step_rendered_contains_port_mapping(context, mapping):
    """Verify rendered output contains expected port mapping."""
    rendered = getattr(context, 'rendered_output', '')
    assert mapping in rendered, f"Rendered output should contain port mapping '{mapping}'"


@then('rendered output should contain SSH_AUTH_SOCK mapping')
def step_rendered_contains_ssh_socket(context):
    """Verify rendered output contains SSH_AUTH_SOCK volume mapping."""
    rendered = getattr(context, 'rendered_output', '')
    assert 'SSH_AUTH_SOCK' in rendered or 'ssh-auth-sock' in rendered, \
        "Rendered output should contain SSH_AUTH_SOCK mapping"


@then('rendered output should contain public-ssh-keys volume')
def step_rendered_contains_ssh_keys_volume(context):
    """Verify rendered output contains public-ssh-keys volume mount."""
    rendered = getattr(context, 'rendered_output', '')
    assert 'public-ssh-keys' in rendered, \
        "Rendered output should contain public-ssh-keys volume"


@then('rendered template should be valid YAML')
def step_valid_yaml(context):
    """Verify rendered output is valid YAML."""
    rendered = getattr(context, 'rendered_output', '')
    if HAS_YAML:
        try:
            yaml.safe_load(rendered)
        except yaml.YAMLError as e:
            raise AssertionError(f"Rendered output is not valid YAML: {e}")
    else:
        # Basic syntax check without PyYAML
        assert ': ' in rendered, "Expected YAML key-value format"


@then('container restart policy should be "{policy}"')
def step_restart_policy(context, policy):
    """Verify container restart policy in rendered output."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'restart: {policy}' in rendered, \
        f"Expected restart policy '{policy}'"


@then('container should expose port {port}')
def step_expose_port(context, port):
    """Verify port exposure in rendered output."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'"{port}":' in rendered or f'{port}:' in rendered, \
        f"Expected port {port} to be exposed"


@then('template user should be "{user}"')
def step_template_user(context, user):
    """Verify user in rendered template."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'user: {user}' in rendered, \
        f"Expected user '{user}' in template"


@then('template should include install command')
def step_install_command(context):
    """Verify install command is present in rendered template."""
    rendered = getattr(context, 'rendered_output', '')
    assert 'install' in rendered.lower(), \
        "Expected install command in template"
