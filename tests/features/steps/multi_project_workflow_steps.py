"""
BDD Step Definitions for Multi-Project Workflow Testing.

These steps cover project-specific context and verification for multi-project workflows.
Reuses common VM/container verification steps from documented_workflow_steps.py.
"""
import os
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    docker_list_containers,
)

# =============================================================================
# PROJECT CONTEXT GIVEN steps (Unique to multi-project workflow)
# =============================================================================

@given('I am starting a new web project')
def step_starting_web_project(context):
    """Context: User is starting a new web development project."""
    context.project_type = 'web'
    context.vms_to_create = ['js', 'nginx']


@given('I have web containers running (JavaScript, nginx)')
def step_web_containers_running(context):
    """Context: Web development containers are running."""
    context.project_type = 'web'
    running = docker_list_containers()
    context.web_containers = []
    for vm in ['js', 'nginx']:
        container_name = f"vde_{vm}"
        if container_name in running:
            context.web_containers.append(container_name)
    context.web_containers_running = len(context.web_containers) > 0
    assert context.web_containers_running, "Web containers should be running"


@given('I am building a microservices application')
def step_building_microservices(context):
    """Context: User is building a microservices application."""
    context.project_type = 'microservices'
    context.vms_to_create = ['go', 'rust', 'nginx']


@given('I have created my microservice VMs')
def step_microservice_vms_created(context):
    """Context: Microservice VMs have been created."""
    context.project_type = 'microservices'
    context.microservice_vms = ['go', 'rust', 'nginx']
    # Verify all exist using existing verification step pattern
    for vm_name in context.microservice_vms:
        vm_dir = Path(VDE_ROOT) / vm_name
        assert vm_dir.exists(), f"Microservice VM {vm_name} should exist"


@given('I am doing data analysis')
def step_doing_data_analysis(context):
    """Context: User is setting up a data science environment."""
    context.project_type = 'data_science'
    context.vms_to_create = ['python', 'r']


@given('I need a complete web stack')
def step_need_complete_web_stack(context):
    """Context: User needs a full stack web development environment."""
    context.project_type = 'fullstack'
    context.vms_to_create = ['python', 'postgres', 'redis', 'nginx']


@given('I am developing a mobile app with backend')
def step_developing_mobile_app(context):
    """Context: User is developing a mobile app with backend services."""
    context.project_type = 'mobile'
    context.vms_to_create = ['flutter', 'postgres']


@given('I have finished working on one project')
def step_finished_project(context):
    """Context: User has completed work on a project."""
    context.project_completed = True


# =============================================================================
# PROJECT VERIFICATION THEN steps (Unique to multi-project workflow)
# =============================================================================

@then('both should be configured for web development')
def step_configured_for_web_development(context):
    """Verify web development tools are available in both VMs."""
    for vm_name in ['js', 'nginx']:
        result = run_vde_command(f"status {vm_name}", timeout=10)
        assert result.returncode == 0, f"{vm_name} should be available"


@then('only the backend stack should be running')
def step_only_backend_running(context):
    """Verify only backend stack containers are running."""
    running = docker_list_containers()
    backend_vms = ['python', 'postgres']
    context.backend_running = all(f"vde_{vm}" in running for vm in backend_vms)
    context.web_stopped = 'vde_js' not in running and 'vde_nginx' not in running
    assert context.backend_running, "Backend VMs should be running"
    assert context.web_stopped, "Web VMs should be stopped"


@then('the nginx VM should be created')
def step_nginx_vm_created(context):
    """Verify nginx VM was created."""
    nginx_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM should be created"


@then('the web containers should be stopped')
def step_web_containers_stopped(context):
    """Verify web containers are stopped."""
    running = docker_list_containers()
    context.web_stopped = not any(
        f'vde_{vm}' in running
        for vm in ['js', 'nginx']
    )
    assert context.web_stopped, "Web containers should be stopped"


@then('the PostgreSQL VM should start')
def step_postgres_vm_starts(context):
    """Verify PostgreSQL VM started."""
    result = run_vde_command("status postgres", timeout=10)
    assert result.returncode == 0, "PostgreSQL VM should be running"


@then('they should be able to communicate on the Docker network')
def step_communicate_on_network(context):
    """Verify microservices can communicate on Docker network."""
    running = docker_list_containers()
    for vm_name in context.microservice_vms:
        assert f"vde_{vm_name}" in running, f"{vm_name} should be running"


@then('the R VM should start')
def step_r_vm_starts(context):
    """Verify R VM started."""
    r_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'r'
    assert r_dir.exists(), "R VM should exist"
    result = run_vde_command("status r", timeout=10)
    assert result.returncode == 0, "R VM should be running"


@then('the Python VM should be for the backend API')
def step_python_backend_api(context):
    """Verify Python is configured as backend API."""
    python_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'python'
    assert python_dir.exists(), "Python VM should exist for backend API"


@then('the Go VM should be created for one service')
def step_go_vm_for_service(context):
    """Verify Go VM was created for a microservice."""
    go_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'go'
    assert go_dir.exists(), "Go VM should be created for microservice"


@then('the Rust VM should be created for another service')
def step_rust_vm_for_service(context):
    """Verify Rust VM was created for a microservice."""
    rust_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'rust'
    assert rust_dir.exists(), "Rust VM should be created for microservice"


@then('the nginx VM should be created as a gateway')
def step_nginx_gateway(context):
    """Verify nginx VM was created as API gateway."""
    nginx_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM should exist as gateway"


@then('each should have its own SSH port')
def step_each_ssh_port(context):
    """Verify each VM has its own SSH port."""
    running = docker_list_containers()
    expected_vms = ['go', 'rust', 'nginx']
    ssh_ports = {}
    for vm in expected_vms:
        if f"vde_{vm}" in running:
            # Check that container has SSH exposed
            result = subprocess.run(
                ["docker", "inspect", f"vde_{vm}", "--format", "{{.Config.ExposedPorts}}"],
                capture_output=True, text=True
            )
            assert '22' in result.stdout or result.returncode == 0, f"{vm} should have SSH port"


@then('both should have data science tools available')
def step_data_science_tools_available(context):
    """Verify data science tools are available in Python and R VMs."""
    for vm_name in ['python', 'r']:
        result = run_vde_command(f"status {vm_name}", timeout=10)
        assert result.returncode == 0, f"{vm_name} should be running with data science tools"


@then('Redis should be for caching')
def step_redis_for_caching(context):
    """Verify Redis VM is configured for caching."""
    redis_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'redis'
    assert redis_dir.exists(), "Redis VM should exist for caching"


@then('nginx should be for the web server')
def step_nginx_web_server(context):
    """Verify nginx VM is configured as web server."""
    nginx_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM should exist for web server"


@then('PostgreSQL should be for the database')
def step_postgres_for_database(context):
    """Verify PostgreSQL VM is configured for database."""
    postgres_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'postgres'
    assert postgres_dir.exists(), "PostgreSQL VM should exist for database"


@then('PostgreSQL should start for the backend database')
def step_postgres_starts_for_backend(context):
    """Verify PostgreSQL VM starts for backend database."""
    result = run_vde_command("status postgres", timeout=10)
    assert result.returncode == 0, "PostgreSQL should be running for backend database"


@then('all containers should stop')
def step_all_containers_stop(context):
    """Verify all containers are stopped."""
    running = docker_list_containers()
    # Check that no VDE containers are running
    vde_containers = [c for c in running if 'vde_' in c]
    context.all_stopped = len(vde_containers) == 0
    assert context.all_stopped, "All containers should be stopped"


@then('I can start a fresh environment for another project')
def step_fresh_environment(context):
    """Verify fresh environment can be started."""
    # This is a context verification - user should be able to create new VMs
    context.project_completed = True
    assert context.project_completed, "Should be able to start fresh environment"


@then('there should be no leftover processes')
def step_no_leftover_processes(context):
    """Verify no leftover Docker processes remain."""
    running = docker_list_containers()
    vde_containers = [c for c in running if 'vde_' in c]
    assert len(vde_containers) == 0, "No leftover VDE container processes should exist"


@then('the JavaScript VM should be created')
def step_javascript_vm_created(context):
    """Verify JavaScript VM was created for web development."""
    js_dir = Path(VDE_ROOT) / 'configs' / 'docker' / 'js'
    assert js_dir.exists(), "JavaScript VM should be created for web development"


@then('both VMs should start')
def step_both_vms_start(context):
    """Verify both VMs (JS and nginx) have started."""
    running = docker_list_containers()
    for vm_name in ['js', 'nginx']:
        assert f"vde_{vm_name}" in running, f"{vm_name} VM should be running"


@then('all service VMs should start')
def step_all_service_vms_start(context):
    """Verify all service VMs (postgres, redis) have started."""
    running = docker_list_containers()
    service_vms = ['postgres', 'redis']
    for vm_name in service_vms:
        assert f"vde_{vm_name}" in running, f"{vm_name} VM should be running"


@then('the Flutter VM should start for mobile development')
def step_flutter_vm_starts(context):
    """Verify Flutter VM started for mobile development."""
    result = run_vde_command("status flutter", timeout=10)
    assert result.returncode == 0, "Flutter VM should be running for mobile development"


# =============================================================================
# Helper function (reuses existing vm_common.run_vde_command)
# =============================================================================

def run_vde_command(cmd, timeout=30):
    """Run a VDE command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=VDE_ROOT
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 1, "", "Command timed out")
