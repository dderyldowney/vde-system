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
