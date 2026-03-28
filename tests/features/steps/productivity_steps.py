"""
BDD Step definitions for Productivity Features (O-8).
Covers: data seeding, clean-state teardown, backup creation,
        and background service verification.
"""
import os
import sys
import shutil
import time
from datetime import datetime
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, when, then
from vm_common import run_vde_command, VDE_ROOT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_postgres_table(table_name, val):
    """Create table and insert a sentinel row in postgres.

    Returns the run_vde_command result for the INSERT; raises AssertionError
    on failure.
    """
    create_r = run_vde_command(
        f"exec postgres psql -U postgres -c "
        f"CREATE TABLE IF NOT EXISTS {table_name} "
        f"(id serial PRIMARY KEY, val text)",
        timeout=30,
    )
    assert create_r.returncode == 0, (
        f"Failed to create table '{table_name}': {create_r.stderr}"
    )
    insert_r = run_vde_command(
        f"exec postgres psql -U postgres -c "
        f"INSERT INTO {table_name} (val) VALUES ('{val}')",
        timeout=30,
    )
    assert insert_r.returncode == 0, (
        f"Failed to insert into '{table_name}': {insert_r.stderr}"
    )
    return insert_r


# ---------------------------------------------------------------------------
# Scenario 1 helper: "I have data in postgres"
# (used by both Scenario 1 and Scenario 3)
# ---------------------------------------------------------------------------

@given("I have data in postgres")
def step_have_data_in_postgres(context):
    """Start postgres and seed a test row so later steps can verify persistence."""
    start_r = run_vde_command("start postgres", timeout=300)
    assert start_r.returncode == 0, (
        f"vde start postgres failed (rc={start_r.returncode}): {start_r.stderr}"
    )
    context._docker_cleanup_needed = True
    context.pg_test_table = "vde_test"
    context.pg_test_val = "persistence-check"
    _seed_postgres_table(context.pg_test_table, context.pg_test_val)


# ---------------------------------------------------------------------------
# Scenario 2: Test with clean state quickly
# ---------------------------------------------------------------------------

@given("I need to test with fresh database")
def step_need_fresh_database(context):
    """Record intent to test with a clean postgres database."""
    # Guarantee clean state regardless of prior scenario residue
    run_vde_command("stop postgres", timeout=60)
    run_vde_command("remove postgres", timeout=60)
    context.fresh_db_test = True
    context._docker_cleanup_needed = True


@when("I stop and remove postgres")
def step_stop_and_remove_postgres(context):
    """Stop and remove the postgres VM."""
    stop_r = run_vde_command("stop postgres", timeout=60)
    assert stop_r.returncode == 0, (
        f"vde stop postgres failed (rc={stop_r.returncode}): {stop_r.stderr}"
    )
    remove_r = run_vde_command("remove postgres", timeout=60)
    assert remove_r.returncode == 0, (
        f"vde remove postgres failed (rc={remove_r.returncode}): {remove_r.stderr}"
    )
    context.pg_removed = True


@when("I recreate and start it")
def step_recreate_and_start_postgres(context):
    """Recreate and start a fresh postgres VM."""
    create_r = run_vde_command("create postgres", timeout=120)
    assert create_r.returncode == 0, (
        f"vde create postgres failed (rc={create_r.returncode}): {create_r.stderr}"
    )
    start_r = run_vde_command("start postgres", timeout=300)
    assert start_r.returncode == 0, (
        f"vde start postgres failed after recreate (rc={start_r.returncode}): {start_r.stderr}"
    )
    context.pg_recreated = True


@then("I should have a fresh database")
def step_should_have_fresh_database(context):
    """Verify the recreated postgres has no vde_test table (clean state)."""
    assert getattr(context, "fresh_db_test", False), (
        "step_need_fresh_database was not called — fresh_db_test flag not set"
    )
    r = run_vde_command(
        "exec postgres psql -U postgres -c SELECT * FROM vde_test",
        timeout=30,
    )
    # A fresh database will not have the table; we expect an error
    table_absent = r.returncode != 0 or "does not exist" in r.stderr or "does not exist" in r.stdout
    assert table_absent, (
        "Expected vde_test table to be absent in fresh database, but it was found.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# Scenario 3: Database backups and restores
# ---------------------------------------------------------------------------

@when("I create a backup of data/postgres/")
def step_create_backup_of_postgres_data(context):
    """Copy VDE_ROOT/data/postgres/ to a timestamped backup directory."""
    src = VDE_ROOT / "data" / "postgres"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = VDE_ROOT / "backup"
    backup_root.mkdir(parents=True, exist_ok=True)
    dest = backup_root / f"postgres_{timestamp}"

    assert src.exists(), (
        f"data/postgres/ not found at {src} — postgres was never started or has no data"
    )
    shutil.copytree(str(src), str(dest))

    context.backup_path = dest


@then("my data should be restored")
def step_data_should_be_restored(context):
    """Restore postgres from backup and verify the sentinel row survives."""
    assert hasattr(context, "backup_path"), (
        "context.backup_path not set — did the backup step run?"
    )
    bp = Path(context.backup_path)
    assert bp.exists(), f"Backup directory does not exist: {bp}"
    assert any(bp.iterdir()), f"Backup directory is empty: {bp}"

    # Stop postgres before touching its data volume
    stop_r = run_vde_command("stop postgres", timeout=60)
    assert stop_r.returncode == 0, (
        f"vde stop postgres failed before restore (rc={stop_r.returncode}): {stop_r.stderr}"
    )

    # Swap the live data directory with the backup
    live = VDE_ROOT / "data" / "postgres"
    if live.exists():
        shutil.rmtree(str(live))
    shutil.copytree(str(bp), str(live))

    # Restart postgres with the restored data
    start_r = run_vde_command("start postgres", timeout=300)
    assert start_r.returncode == 0, (
        f"vde start postgres failed after restore (rc={start_r.returncode}): {start_r.stderr}"
    )

    # Verify the sentinel row that was seeded before backup
    table = getattr(context, "pg_test_table", "vde_test")
    val = getattr(context, "pg_test_val", "persistence-check")
    query_r = run_vde_command(
        f"exec postgres psql -U postgres -c SELECT val FROM {table} WHERE val='{val}'",
        timeout=30,
    )
    assert query_r.returncode == 0 and val in query_r.stdout, (
        f"Sentinel row '{val}' not found in restored database.\n"
        f"stdout: {query_r.stdout}\nstderr: {query_r.stderr}"
    )


# ---------------------------------------------------------------------------
# Scenario 4: Run services in background
# ---------------------------------------------------------------------------

@given("I have background services running")
def step_have_background_services_running(context):
    """Start postgres as a representative background service."""
    start_r = run_vde_command("start postgres", timeout=300)
    assert start_r.returncode == 0, (
        f"vde start postgres failed (rc={start_r.returncode}): {start_r.stderr}"
    )
    context._docker_cleanup_needed = True
    context.bg_vm = "postgres"


@when("I continue my work on host")
def step_continue_work_on_host(context):
    """Simulate host-side work by sleeping briefly."""
    time.sleep(1)


@then("services should keep running in background")
def step_services_keep_running_in_background(context):
    """Assert that the background VM is still running after host-side work."""
    assert hasattr(context, "bg_vm"), (
        "context.bg_vm not set — did the @given step run?"
    )
    r = run_vde_command("ps -q", timeout=30)
    container_name = f"vde-{context.bg_vm}"
    is_running = (
        r.returncode == 0
        and (container_name in r.stdout or context.bg_vm in r.stdout)
    )
    assert is_running, (
        f"Expected '{container_name}' to still be running, but it was not found.\n"
        f"vde ps -q output:\n{r.stdout}\n{r.stderr}"
    )
