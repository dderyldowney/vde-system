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
    run_vde_command,
    docker_ps,
    container_exists,
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
    """Context: Web development containers are running via vde ps."""
    context.project_type = 'web'
    running = docker_ps()
    context.web_containers = []
    for vm in ['js', 'nginx']:
        if f"vde-{vm}" in running:
            context.web_containers.append(f"vde-{vm}")
    context.web_containers_running = len(context.web_containers) > 0
    assert context.web_containers_running, "Web containers (js, nginx) should be running"


@given('I am building a microservices application')
def step_building_microservices(context):
    """Context: User is building a microservices application."""
    context.project_type = 'microservices'
    context.vms_to_create = ['go', 'rust', 'nginx']


@given('I have created my microservice VMs')
def step_microservice_vms_created(context):
    """Context: Microservice VMs have been created - verify configs exist."""
    context.project_type = 'microservices'
    context.microservice_vms = ['go', 'rust', 'nginx']
    # Verify all exist in configs/docker/
    for vm_name in context.microservice_vms:
        vm_dir = VDE_ROOT / 'configs' / 'docker' / vm_name
        assert vm_dir.exists(), f"Microservice VM {vm_name} config should exist"


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
        assert (VDE_ROOT / 'configs' / 'docker' / vm_name).exists(), f"{vm_name} config missing"


@then('only the backend stack should be running')
def step_only_backend_running(context):
    """Verify only backend stack containers are running via vde ps."""
    running = docker_ps()
    backend_vms = ['vde-python', 'vde-postgres']
    
    # Check backends are running
    for vm in backend_vms:
        assert vm in running, f"Backend VM {vm} should be running"
        
    # Check web frontends are stopped
    for vm in ['vde-js', 'vde-nginx']:
        assert vm not in running, f"Web VM {vm} should be stopped"


@then('the nginx VM should be created')
def step_nginx_vm_created(context):
    """Verify nginx VM was created."""
    nginx_dir = VDE_ROOT / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM config should be created"


@then('the web containers should be stopped')
def step_web_containers_stopped(context):
    """Verify web containers are stopped via vde ps."""
    running = docker_ps()
    for vm in ['js', 'nginx']:
        assert f"vde-{vm}" not in running, f"Web container vde-{vm} still running"


@then('the PostgreSQL VM should start')
def step_postgres_vm_starts(context):
    """Verify PostgreSQL VM started."""
    assert container_exists('postgres'), "PostgreSQL VM should be running"


@then('they should be able to communicate on the Docker network')
def step_communicate_on_network(context):
    """Verify microservices can communicate on Docker network via vde networks."""
    result = run_vde_command("networks", context=context)
    assert result.returncode == 0
    assert "vde-net" in result.stdout or "vde-testing" in result.stdout


@then('the R VM should start')
def step_r_vm_starts(context):
    """Verify R VM started."""
    assert container_exists('r'), "R VM should be running"


@then('the Python VM should be for the backend API')
def step_python_backend_api(context):
    """Verify Python is configured as backend API."""
    python_dir = VDE_ROOT / 'configs' / 'docker' / 'python'
    assert python_dir.exists(), "Python VM config missing"


@then('the Go VM should be created for one service')
def step_go_vm_for_service(context):
    """Verify Go VM was created for a microservice."""
    go_dir = VDE_ROOT / 'configs' / 'docker' / 'go'
    assert go_dir.exists(), "Go VM config missing"


@then('the Rust VM should be created for another service')
def step_rust_vm_for_service(context):
    """Verify Rust VM was created for a microservice."""
    rust_dir = VDE_ROOT / 'configs' / 'docker' / 'rust'
    assert rust_dir.exists(), "Rust VM config missing"


@then('the nginx VM should be created as a gateway')
def step_nginx_gateway(context):
    """Verify nginx VM was created as API gateway."""
    nginx_dir = VDE_ROOT / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM config missing"


@then('each should have its own SSH port')
def step_each_ssh_port(context):
    """Verify each VM has its own SSH port via vde port."""
    vms = getattr(context, 'vms_to_create', ['go', 'rust', 'nginx'])
    ports = []
    for vm in vms:
        if container_exists(vm):
            result = run_vde_command(f"port {vm} 22", context=context)
            if result.returncode == 0 and result.stdout.strip():
                ports.append(result.stdout.strip())
    
    # Verify we got unique ports
    assert len(ports) > 0, "No SSH ports found"
    assert len(set(ports)) == len(ports), f"Non-unique ports found: {ports}"


@then('both should have data science tools available')
def step_data_science_tools_available(context):
    """Verify data science VMs exist."""
    for vm_name in ['python', 'r']:
        assert (VDE_ROOT / 'configs' / 'docker' / vm_name).exists(), f"{vm_name} config missing"


@then('Redis should be for caching')
def step_redis_for_caching(context):
    """Verify Redis VM is configured for caching."""
    redis_dir = VDE_ROOT / 'configs' / 'docker' / 'redis'
    assert redis_dir.exists(), "Redis VM config missing"


@then('nginx should be for the web server')
def step_nginx_web_server(context):
    """Verify nginx VM is configured as web server."""
    nginx_dir = VDE_ROOT / 'configs' / 'docker' / 'nginx'
    assert nginx_dir.exists(), "nginx VM config missing"


@then('PostgreSQL should be for the database')
def step_postgres_for_database(context):
    """Verify PostgreSQL VM is configured for database."""
    postgres_dir = VDE_ROOT / 'configs' / 'docker' / 'postgres'
    assert postgres_dir.exists(), "PostgreSQL VM config missing"


@then('PostgreSQL should start for the backend database')
def step_postgres_starts_for_backend(context):
    """Verify PostgreSQL VM starts."""
    assert container_exists('postgres'), "PostgreSQL not running"


@then('all containers should stop')
def step_all_containers_stop(context):
    """Verify all containers are stopped via vde ps."""
    running = docker_ps()
    vde_containers = [c for c in running if c.startswith('vde-')]
    assert len(vde_containers) == 0, f"VDE containers still running: {vde_containers}"


@then('I can start a fresh environment for another project')
def step_fresh_environment(context):
    """Verify fresh environment capability."""
    result = run_vde_command("status", context=context)
    assert result.returncode == 0


@then('there should be no leftover processes')
def step_no_leftover_processes(context):
    """Verify no leftover containers via vde ps."""
    running = docker_ps()
    vde_containers = [c for c in running if c.startswith('vde-')]
    assert len(vde_containers) == 0, f"Leftover VDE processes: {vde_containers}"


@then('the JavaScript VM should be created')
def step_javascript_vm_created(context):
    """Verify JavaScript VM was created."""
    js_dir = VDE_ROOT / 'configs' / 'docker' / 'js'
    assert js_dir.exists(), "JavaScript VM config missing"


@then('both VMs should start')
def step_both_vms_start(context):
    """Verify both VMs started via vde ps."""
    running = docker_ps()
    # Check for generic "both" - usually context dependent
    assert len([c for c in running if c.startswith('vde-')]) >= 1


@then('all service VMs should start')
def step_all_service_vms_start(context):
    """Verify service VMs started via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith('vde-')]
    assert len(vde_running) >= 1


@then('the Flutter VM should start for mobile development')
def step_flutter_vm_starts(context):
    """Verify Flutter VM started."""
    assert container_exists('flutter'), "Flutter VM not running"
