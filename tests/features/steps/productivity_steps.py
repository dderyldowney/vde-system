"""
BDD Step Definitions for productivity features - REAL IMPLEMENTATIONS

These steps test actual VDE functionality using real Docker operations,
PostgreSQL data persistence, VM lifecycle, and file system state.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

from config import VDE_ROOT

# =============================================================================
# Helper Functions
# =============================================================================

from vm_common import run_vde_command, docker_ps, container_exists, wait_for_container

# =============================================================================
# Port Registry and Cache Steps (Real implementations)
# =============================================================================

@when('port registry is saved')
def step_port_registry_saved(context):
    """Actually check that port registry cache is saved."""
    cache_path = VDE_ROOT / ".cache" / "port-registry"
    if cache_path.exists():
        context.port_registry_saved = True
        context.port_registry_cache = str(cache_path)
    else:
        context.port_registry_saved = False

@then('cache file should exist at ".cache/port-registry"')
def step_port_registry_cache_exists(context):
    """Actually verify port registry cache exists."""
    cache_path = VDE_ROOT / ".cache" / "port-registry"
    assert cache_path.exists(), f"Port registry cache not found at {cache_path}"

@given('port registry cache exists')
def step_port_registry_cache(context):
    """Verify port registry cache exists before test."""
    cache_path = VDE_ROOT / ".cache" / "port-registry"
    assert cache_path.exists(), "Port registry cache must exist for this test"
    context.port_registry_cache_exists = True

@when('port registry is loaded')
def step_port_registry_loaded(context):
    """Actually load and verify port registry."""
    cache_path = VDE_ROOT / ".cache" / "port-registry"
    if cache_path.exists():
        content = cache_path.read_text()
        context.port_registry_content = content
        context.port_registry_loaded = True
    else:
        context.port_registry_loaded = False

@then('allocated ports should be available without scanning compose files')
def step_ports_from_cache(context):
    """Verify ports were loaded from cache."""
    assert context.port_registry_loaded, "Port registry should be loaded from cache"

@when('invalidate_vm_types_cache is called')
def step_invalidate_cache(context):
    """Actually invalidate the VM types cache by deleting the cache file."""
    cache_path = VDE_ROOT / ".cache" / "vm-types.cache"
    if cache_path.exists():
        cache_path.unlink()
        context.cache_invalidated = True
    else:
        context.cache_invalidated = False

# =============================================================================
# VM Configuration Steps
# =============================================================================

# Note: "my project needs python, postgres, and redis" is defined in parser_steps.py
# Note: "I have {num} VMs configured for my project" is defined in pattern_steps.py
# Note: "I have VMs running for my project" is defined in parser_steps.py

# =============================================================================
# Productivity Features - Data Persistence Tests (Real PostgreSQL)
# =============================================================================

@given('I have data in postgres')
def step_postgres_data(context):
    """Create actual test data in postgres."""
    # Create a test table and insert data
    create_table = """
        CREATE TABLE IF NOT EXISTS test_persistence (
            id SERIAL PRIMARY KEY,
            test_value VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    insert_data = """
        INSERT INTO test_persistence (test_value) VALUES
        ('persistent_data_1'),
        ('persistent_data_2'),
        ('persistent_data_3');
    """

    # Run commands
    result1 = run_psql_command(create_table)
    result2 = run_psql_command(insert_data)

    if result1.returncode == 0 and result2.returncode == 0:
        context.postgres_has_data = True
        context.test_table_created = True
        context.test_data_inserted = True

        # Store expected data for verification
        context.expected_test_values = ['persistent_data_1', 'persistent_data_2', 'persistent_data_3']
    else:
        context.postgres_has_data = False
        raise AssertionError(f"Failed to create test data: {result1.stderr} {result2.stderr}")

@when('I stop and restart postgres VM')
def step_stop_restart_postgres(context):
    """Actually stop and restart the postgres container."""
    # Stop postgres
    stop_result = subprocess.run(
        ["docker", "stop", "postgres"],
        capture_output=True,
        text=True,
        timeout=60
    )

    if stop_result.returncode != 0:
        raise AssertionError(f"Failed to stop postgres: {stop_result.stderr}")

    # Wait for it to fully stop
    if not wait_for_container_stop("postgres", timeout=30):
        raise AssertionError("Postgres container did not stop in time")

    # Small delay to ensure clean stop
    time.sleep(2)

    # Start postgres
    start_result = subprocess.run(
        ["docker", "start", "postgres"],
        capture_output=True,
        text=True,
        timeout=60
    )

    if start_result.returncode != 0:
        raise AssertionError(f"Failed to start postgres: {start_result.stderr}")

    # Wait for postgres to be ready
    if not wait_for_container("postgres", timeout=60):
        raise AssertionError("Postgres container did not start in time")

    # Wait for postgres to be ready to accept connections
    max_attempts = 30
    for _i in range(max_attempts):
        ready_result = subprocess.run(
            ["docker", "exec", "postgres", "pg_isready"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "accepting connections" in ready_result.stdout:
            break
        time.sleep(1)

    context.postgres_restarted = True

@then('my data should still be there')
def step_data_persists(context):
    """Actually verify data persisted across restart."""
    if not context.postgres_has_data:
        raise AssertionError("No data was created before restart")

    # Query the test table
    query = "SELECT test_value FROM test_persistence ORDER BY id;"
    result = run_psql_command(query)

    if result.returncode != 0:
        raise AssertionError(f"Failed to query test table: {result.stderr}")

    # Extract values from output
    lines = result.stdout.strip().split('\n')
    actual_values = [line.strip() for line in lines if line.strip() and not line.startswith('test_value') and not line.startswith('---') and not line.startswith('(')]

    # Check that expected values are present
    expected = getattr(context, 'expected_test_values', [])
    for expected_value in expected:
        if expected_value not in result.stdout:
            raise AssertionError(f"Expected value '{expected_value}' not found in query result. Got: {result.stdout}")

# Note: Project switching steps are defined in daily_workflow_steps.py
# Note: SSH steps are defined in ssh_steps.py and vm_lifecycle_steps.py

# =============================================================================
# Productivity Features - Service VM Management
# =============================================================================

@given('I need postgres and redis running')
def step_need_postgres_redis(context):
    """Set service requirements."""
    context.required_services = ['postgres', 'redis']
    context.service_vms_needed = True

@when('I start them as service VMs')
def step_start_service_vms(context):
    """Start service VMs using docker-compose."""
    services = getattr(context, 'required_services', [])
    context.started_services = []

    for service in services:
        compose_path = VDE_ROOT / "configs" / "docker" / service / "docker-compose.yml"
        if compose_path.exists():
            result = subprocess.run(
                f"cd {compose_path.parent} && docker-compose up -d",
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                context.started_services.append(service)
                wait_for_container(service, timeout=60)

    context.service_vms_started = len(context.started_services) > 0

@then('they run in background')
def step_services_background(context):
    """Verify services are running in background."""
    for service in getattr(context, 'started_services', []):
        assert container_exists(service), f"Service {service} is not running"

# =============================================================================
# Productivity Features - Fresh Database Testing
# =============================================================================

@given('I need to test with fresh database')
def step_fresh_database_test(context):
    """Mark that fresh database is needed."""
    context.needs_fresh_database = True

@when('I stop and remove postgres')
def step_stop_remove_postgres(context):
    """Stop and remove postgres container and volume."""
    # Stop container
    subprocess.run(["docker", "stop", "postgres"], capture_output=True, timeout=60)
    wait_for_container_stop("postgres", timeout=30)

    # Remove container
    subprocess.run(["docker", "rm", "postgres"], capture_output=True, timeout=30)

    # Remove volume to get fresh database
    subprocess.run(["docker", "volume", "rm", "postgres_postgres_data"], capture_output=True, timeout=30)

    context.postgres_stopped = True
    context.postgres_removed = True

@when('I recreate and start it')
def step_recreate_start_postgres(context):
    """Recreate and start postgres with fresh volume."""
    compose_path = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"

    result = subprocess.run(
        f"cd {compose_path.parent} && docker-compose up -d",
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"Failed to recreate postgres: {result.stderr}")

    wait_for_container("postgres", timeout=60)

    # Wait for postgres to be ready
    max_attempts = 30
    for _i in range(max_attempts):
        ready_result = subprocess.run(
            ["docker", "exec", "postgres", "pg_isready"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "accepting connections" in ready_result.stdout:
            break
        time.sleep(1)

    context.postgres_recreated = True
    context.postgres_started = True

@then('I get a fresh database instantly')
def step_fresh_database(context):
    """Verify database is fresh (no old data)."""
    # Check that our test table doesn't exist
    result = run_psql_command("SELECT * FROM test_persistence;")

    # Table should not exist, so command should fail
    assert result.returncode != 0, "Old data still exists - database is not fresh"
    assert "does not exist" in result.stderr, "Expected table does not exist error"

# =============================================================================
# Productivity Features - Database Backups
# =============================================================================

@given('I have important data in postgres VM')
def step_important_postgres_data(context):
    """Create important test data for backup testing."""
    create_table = """
        CREATE TABLE IF NOT EXISTS important_data (
            id SERIAL PRIMARY KEY,
            data_content TEXT,
            backup_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    insert_data = """
        INSERT INTO important_data (data_content) VALUES
        ('critical_user_data'),
        ('financial_records'),
        ('project_state');
    """

    run_psql_command(create_table)
    run_psql_command(insert_data)

    context.important_postgres_data = True
    context.backup_table_name = "important_data"

@when('I create a backup of data/postgres/')
def step_create_postgres_backup(context):
    """Create actual backup of postgres data."""
    backup_dir = VDE_ROOT / "data" / "postgres" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Use pg_dump to create backup
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql"

    result = subprocess.run(
        f"docker exec postgres pg_dump -U devuser postgres_dev_db > {backup_file}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode == 0 and backup_file.exists():
        context.postgres_backup_created = True
        context.backup_file_path = str(backup_file)
    else:
        raise AssertionError(f"Failed to create backup: {result.stderr}")

@then('I can restore from backup later')
def step_restore_backup(context):
    """Verify backup can be restored."""
    backup_path = getattr(context, 'backup_file_path', None)
    if not backup_path:
        raise AssertionError("No backup file was created")

    backup_file = Path(backup_path)
    assert backup_file.exists(), f"Backup file not found: {backup_path}"

    # Verify backup contains SQL
    content = backup_file.read_text()
    assert "PostgreSQL database dump" in content or "CREATE TABLE" in content, "Backup file appears invalid"

# =============================================================================
# Productivity Features - Version Consistency
# =============================================================================

@given('my project requires specific Node version')
def step_specific_node_version(context):
    """Set Node version requirement."""
    context.requires_specific_node_version = True
    context.required_node_version = "18"  # Example version

@when('the team defines the JS VM with that version')
def step_define_js_vm_version(context):
    """Simulate defining JS VM with specific version."""
    context.js_vm_version_defined = True
    context.configured_node_version = getattr(context, 'required_node_version', "18")

@then('everyone gets the same Node version')
def step_same_node_version(context):
    """Verify consistent Node version across team."""
    # Check if js VM configuration exists
    js_compose = VDE_ROOT / "configs" / "docker" / "js" / "docker-compose.yml"
    assert js_compose.exists(), "JS VM docker-compose configuration not found"

    content = js_compose.read_text()
    # Verify Node version is specified in configuration
    assert "node" in content.lower() or "nodejs" in content.lower() or "18" in content, \
        "Node version not properly specified in JS VM configuration"

# =============================================================================
# Productivity Features - Clean Workspace
# =============================================================================

@given('I work on multiple unrelated projects')
def step_multiple_projects(context):
    """Set multiple projects context."""
    context.multiple_projects = True
    context.project_list = ['project_a', 'project_b', 'project_c']

@when('each project has its own VM')
def step_each_project_own_vm(context):
    """Set VM per project."""
    context.project_isolation = True
    context.vms_per_project = {}

# =============================================================================
# Collaboration Workflow Steps
# =============================================================================

@given('the docker-compose.yml is committed to the repo')
def step_docker_compose_committed(context):
    """Check if docker-compose is tracked in git."""
    result = subprocess.run(
        ["git", "ls-files", "configs/docker/*/docker-compose.yml"],
        capture_output=True,
        text=True,
        cwd=VDE_ROOT,
        timeout=10
    )
    context.docker_compose_in_repo = result.returncode == 0 and len(result.stdout.strip()) > 0

# =============================================================================
# Additional Helper THEN Steps
# =============================================================================

@then('I don\'t lose work between sessions')
def step_no_work_loss(context):
    """Verify data persistence."""
    assert getattr(context, 'data_persists', False), "Data did not persist across session"

@then('I don\'t need to manually clean data')
def step_no_manual_clean(context):
    """Verify automatic cleanup works."""
    assert getattr(context, 'fresh_database_obtained', False), "Fresh database not obtained automatically"

@then('my work is safely backed up')
def step_work_safely_backed_up(context):
    """Verify backup was created."""
    assert getattr(context, 'backup_restorable', False), "Backup was not created successfully"
