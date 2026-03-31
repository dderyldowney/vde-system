"""
Step definitions for VDE installation and setup.
"""

import os
import shutil
import subprocess
from pathlib import Path

from behave import given, then, when

from vm_common import VDE_ROOT, run_vde_command


# =============================================================================
# GIVEN steps
# =============================================================================

@given('I have a new computer with Docker installed')
def step_impl_docker_installed(context):
    """Verify docker info."""
    result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker is not running or installed: {result.stderr}"
    context.docker_info = result.stdout


# =============================================================================
# WHEN steps
# =============================================================================

@when('I run the initial setup script')
def step_impl_run_init(context):
    """Run 'vde init'."""
    # Use run_vde_command which handles the path to bin/vde
    result = run_vde_command('init', context=context)
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    context.last_output = context.command_output


# =============================================================================
# THEN steps
# =============================================================================

@then('VDE should properly installed')
@then('VDE should be properly installed')
def step_impl_vde_installed(context):
    """Verify 'bin/vde' executable."""
    vde_bin = VDE_ROOT / 'bin' / 'vde'
    assert vde_bin.exists(), f"VDE binary not found at {vde_bin}"
    assert os.access(vde_bin, os.X_OK), f"VDE binary at {vde_bin} is not executable"


@then('required directories should be created')
def step_impl_req_dirs(context):
    """Assert exist: configs, data, lib, templates."""
    for d in ['configs', 'data', 'lib', 'templates']:
        path = VDE_ROOT / d
        assert path.exists() and path.is_dir(), f"Required directory missing: {path}"


@then('it should verify Docker is installed')
def step_impl_verify_docker(context):
    """Check for 'docker' in PATH."""
    docker_path = shutil.which('docker')
    assert docker_path is not None, "Docker executable not found in PATH"


@then('it should verify docker-compose is available')
def step_impl_verify_docker_compose(context):
    """Check 'docker compose version'."""
    result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker Compose is not available: {result.stderr}"


@then('it should verify zsh is available')
def step_impl_verify_zsh(context):
    """Verify zsh --version."""
    result = subprocess.run(['zsh', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, f"zsh is not installed or not accessible: {result.stderr}"


@then('configs/ directory should exist')
def step_impl_configs_exists(context):
    """Verify path via VDE_ROOT."""
    path = VDE_ROOT / 'configs'
    assert path.exists() and path.is_dir(), f"Configs directory missing at {path}"


@then('vde-net should be created automatically')
def step_impl_vde_net_created(context):
    """Verify 'vde networks' output."""
    result = run_vde_command('networks', context=context)
    assert 'vde-net' in result.stdout, f"vde-net network not found in: {result.stdout}"


@then('all VMs should use this network')
def step_impl_all_vms_use_network(context):
    """Verify configs reference vde-net."""
    configs_dir = VDE_ROOT / 'configs'
    assert configs_dir.exists(), "configs directory missing"
    # Check at least one compose file references vde-net
    found = False
    for f in configs_dir.rglob('docker-compose.yml'):
        if 'vde-net' in f.read_text():
            found = True
            break
    assert found, "No docker-compose.yml found referencing vde-net"


@then('VMs can communicate with each other')
def step_impl_vms_communicate(context):
    """Verify network is bridge type."""
    result = subprocess.run(['docker', 'network', 'inspect', 'vde-net'], capture_output=True, text=True)
    assert result.returncode == 0, "Failed to inspect vde-net"
    assert '"driver": "bridge"' in result.stdout, "vde-net is not a bridge network"


@then('I should see helpful progress messages')
def step_impl_progress_messages(context):
    """Assert output is not empty."""
    output = getattr(context, 'command_output', '')
    assert len(output.strip()) > 0, "Expected progress messages, but output was empty"


@then('README.md should provide overview')
def step_impl_readme_overview(context):
    """Assert file exists and has content."""
    readme = VDE_ROOT / 'README.md'
    assert readme.exists(), "README.md not found"
    content = readme.read_text()
    assert len(content.strip()) > 10, "README.md is empty or too short"
    assert "VDE" in content, "README.md does not seem to mention VDE"
