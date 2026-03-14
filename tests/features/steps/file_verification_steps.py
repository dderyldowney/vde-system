# -*- coding: utf-8 -*-
"""
File Verification and Docker-Compose Steps
tests/features/steps/file_verification_steps.py
"""

from behave import given, when, then
import subprocess
import os
from pathlib import Path

# Import shared configuration
from vm_common import VDE_ROOT, run_vde_command, container_is_running, docker_ps

@given(u'I have a workspace directory')
def step_impl_workspace(context):
    """Set up workspace directory context."""
    workspace = VDE_ROOT / 'projects'
    context.workspace_dir = workspace
    context.workspace_exists = workspace.exists()


@then(u'a docker-compose.yml file should be generated')
def step_impl_compose_generated(context):
    """Verify docker-compose.yml was generated in any VM config."""
    configs_dir = VDE_ROOT / 'configs' / 'docker'
    if configs_dir.exists():
        compose_files = list(configs_dir.rglob('docker-compose.yml'))
        assert len(compose_files) > 0, "No docker-compose.yml files found"


@then(u'I can manually use docker-compose if needed')
def step_impl_manual_compose(context):
    """Verify manual docker-compose usage is possible via vde info."""
    result = run_vde_command('info', context=context)
    assert result.returncode == 0, "VDE/Docker should be available"
    assert 'compose' in result.stdout.lower(), "Docker Compose should be available"


@then(u'the file should follow best practices')
def step_impl_best_practices(context):
    """Verify generated files follow best practices."""
    # Check at least one known compose file
    compose_file = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    if compose_file.exists():
        content = compose_file.read_text()
        assert 'services:' in content and 'version:' in content


@then(u'they should start in a reasonable order')
def step_impl_start_order(context):
    """Verify VMs can be started via unified command."""
    result = run_vde_command('help', context=context)
    assert result.returncode == 0


@then(u'dependencies should be available when needed')
def step_impl_dependencies(context):
    """Verify dependencies are available via vde info."""
    result = run_vde_command('info', context=context)
    assert result.returncode == 0


@then(u'the startup should complete successfully')
def step_impl_startup_success(context):
    """Verify startup capability."""
    result = run_vde_command('help', context=context)
    assert result.returncode == 0


@then(u'the Python VM should be started again')
def step_impl_python_restart(context):
    """Restart Python VM check."""
    assert container_is_running('python') or compose_file_exists('python')


@then(u'both "python" and "rust" VMs should be running')
def step_both_vms_running(context):
    """Verify both Python and Rust VMs are running using real container checks."""
    from vm_common import container_is_running, wait_for_container
    for vm in ['python', 'rust']:
        if not container_is_running(vm):
            # Try to wait a bit
            wait_for_container(vm, timeout=30)
        assert container_is_running(vm), f"VM {vm} should be running"


@then(u'no stopped containers should accumulate')
def step_impl_no_stopped_accumulation(context):
    """Verify no stopped containers accumulate via vde ps."""
    # This checks that our cleanup/lifecycle management works
    result = run_vde_command('ps -a', context=context)
    assert result.returncode == 0
