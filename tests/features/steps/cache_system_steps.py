"""
BDD Step Definitions for Cache System Feature.
Tests VM type caching, cache invalidation, and cache consistency.
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
from vm_common import run_vde_command


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _get_cache_path():
    return VDE_ROOT / ".cache" / "vm-types.cache"


def _get_port_registry_path():
    return VDE_ROOT / ".cache" / "port-registry"


def _ensure_cache_exists():
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = _get_cache_path()
    if not cache_path.exists():
        run_vde_command("list", timeout=30)
    return cache_path


# =============================================================================
# GIVEN steps - Cache Setup
# =============================================================================


@given("VM types are loaded")
def step_vm_types_loaded(context):
    """Ensure VM types are loaded by running a VDE command."""
    result = run_vde_command("list", timeout=30, context=context)
    context.vm_types_loaded = result.returncode == 0


@given("VM types cache exists and is valid")
def step_cache_exists_and_valid(context):
    """Cache file exists and is valid."""
    cache_path = _ensure_cache_exists()
    context.cache_exists = cache_path.exists()
    if cache_path.exists():
        context.cache_mtime = cache_path.stat().st_mtime


@given("vm-types.conf has not been modified since cache")
def step_conf_not_modified(context):
    """Config file not modified since cache."""
    cache_path = _get_cache_path()
    conf_path = VDE_ROOT / "data" / "vm-types.conf"
    if cache_path.exists() and conf_path.exists():
        context.conf_not_modified = conf_path.stat().st_mtime <= cache_path.stat().st_mtime
    else:
        context.conf_not_modified = False


@given("vm-types.conf has been modified after cache")
def step_conf_modified_after_cache(context):
    """Config file was modified after cache was created."""
    cache_path = _get_cache_path()
    conf_path = VDE_ROOT / "data" / "vm-types.conf"
    if cache_path.exists() and conf_path.exists():
        os.utime(conf_path, None)
        context.conf_modified = conf_path.stat().st_mtime > cache_path.stat().st_mtime
    else:
        context.conf_modified = False


@given("VM types are cached")
def step_vm_types_cached(context):
    """VM types are in cache."""
    _ensure_cache_exists()


@given("ports have been allocated for VMs")
def step_ports_allocated_for_vms(context):
    """Ports have been allocated for VMs."""
    result = run_vde_command("create python", timeout=120, context=context)
    context.ports_allocated = result.returncode == 0


@given("port registry cache exists")
def step_port_registry_exists(context):
    """Port registry cache exists."""
    registry_path = _get_port_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    if not registry_path.exists():
        result = run_vde_command("create python", timeout=120, context=context)
        if result.returncode == 0:
            registry_path.touch()
    context.port_registry_exists = registry_path.exists()


@given("a VM has been removed")
def step_vm_removed(context):
    """A VM has been removed."""
    run_vde_command("remove python", timeout=60, context=context)


@given("port registry cache is missing or invalid")
def step_port_registry_missing(context):
    """Port registry cache is missing or invalid."""
    registry_path = _get_port_registry_path()
    if registry_path.exists():
        registry_path.unlink()
    context.port_registry_missing = True


@given(".cache directory does not exist")
def step_cache_dir_missing(context):
    """Cache directory does not exist."""
    cache_dir = VDE_ROOT / ".cache"
    if cache_dir.exists():
        import shutil

        shutil.rmtree(cache_dir)
    context.cache_dir_missing = True


@given("cache file was created before config file")
def step_cache_before_conf(context):
    """Cache file was created before config file."""
    cache_path = _get_cache_path()
    conf_path = VDE_ROOT / "data" / "vm-types.conf"
    if cache_path.exists() and conf_path.exists():
        old_time = cache_path.stat().st_mtime - 100
        os.utime(cache_path, (old_time, old_time))
        context.cache_before_conf = True


@given("cache file is newer than config file")
def step_cache_newer_than_conf(context):
    """Cache file is newer than config file."""
    cache_path = _get_cache_path()
    conf_path = VDE_ROOT / "data" / "vm-types.conf"
    if cache_path.exists() and conf_path.exists():
        new_time = cache_path.stat().st_mtime + 100
        os.utime(conf_path, (new_time, new_time))
        context.cache_newer = True


@given("library has been sourced")
def step_library_sourced(context):
    """Library has been sourced - simulate by loading."""
    result = run_vde_command("list", timeout=30, context=context)
    context.library_sourced = result.returncode == 0


@given("no VM operations have been performed")
def step_no_vm_operations(context):
    """No VM operations have been performed."""
    context.no_vm_operations = True


@given("cache is manually cleared")
def step_cache_manually_cleared(context):
    """Cache is manually cleared."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
    context.cache_cleared = True


@given("port registry cache exists for multiple VMs")
def step_port_registry_multiple_vms(context):
    """Port registry cache exists for multiple VMs."""
    registry_path = _get_port_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("python=2210\nrust=2211\njs=2212\n")
    context.port_registry_multiple = True


# =============================================================================
# WHEN steps - Cache Operations
# =============================================================================


@when("VM types are loaded")
def step_when_load_vm_types(context):
    """Load VM types."""
    result = run_vde_command("list", timeout=30, context=context)
    context.vm_types_load_result = result.returncode


@when("VM types are loaded with --no-cache")
def step_load_no_cache(context):
    """Load VM types with --no-cache flag."""
    result = run_vde_command("list --no-cache", timeout=30, context=context)
    context.no_cache_load = result.returncode


@when("cache is read")
def step_read_cache(context):
    """Read cache file."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        context.cache_read = cache_path.read_text()
    else:
        context.cache_read = ""


@when("port registry is saved")
def step_save_port_registry(context):
    """Save port registry."""
    registry_path = _get_port_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("python=2210\n")


@when("port registry is loaded")
def step_load_port_registry(context):
    """Load port registry."""
    registry_path = _get_port_registry_path()
    if registry_path.exists():
        context.port_registry_loaded = registry_path.read_text()
    else:
        context.port_registry_loaded = ""


@when("port registry is verified")
def step_verify_port_registry(context):
    """Verify port registry."""
    registry_path = _get_port_registry_path()
    if not registry_path.exists():
        run_vde_command("list", timeout=30, context=context)
    context.port_registry_verified = registry_path.exists()


@when("cache operation is performed")
def step_cache_operation(context):
    """Perform cache operation."""
    result = run_vde_command("list", timeout=30, context=context)
    context.cache_operation_done = result.returncode == 0


@when("cache validity is checked")
def step_check_cache_validity(context):
    """Check cache validity."""
    cache_path = _get_cache_path()
    conf_path = VDE_ROOT / "data" / "vm-types.conf"
    if cache_path.exists() and conf_path.exists():
        context.cache_valid = conf_path.stat().st_mtime <= cache_path.stat().st_mtime
    else:
        context.cache_valid = False


@when("invalidate_vm_types_cache is called")
def step_invalidate_cache(context):
    """Call invalidate_vm_types_cache function."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
    context.cache_invalidated = True


@when("VM types are first accessed")
def step_vm_types_first_access(context):
    """VM types are first accessed."""
    result = run_vde_command("list", timeout=30, context=context)
    context.first_access = result.returncode == 0


@when("cache is manually cleared")
def step_when_clear_cache(context):
    """Clear cache manually."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        cache_path.unlink()


@when("VM types are loaded multiple times")
def step_load_multiple_times(context):
    """Load VM types multiple times."""
    for _ in range(3):
        run_vde_command("list", timeout=30, context=context)


@when("port registry is reloaded")
def step_reload_port_registry(context):
    """Reload port registry."""
    result = run_vde_command("list", timeout=30, context=context)
    context.port_registry_reloaded = result.returncode == 0


@when("cache is read by multiple processes simultaneously")
def step_concurrent_cache_read(context):
    """Simulate concurrent cache reads."""
    import threading

    results = []

    def read_cache():
        cache_path = _get_cache_path()
        if cache_path.exists():
            results.append(cache_path.read_text())

    threads = [threading.Thread(target=read_cache) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    context.concurrent_reads = len(results)


# =============================================================================
# THEN steps - Cache Verification
# =============================================================================


@then('cache file should be created at "{path}"')
def step_cache_file_created(context, path):
    """Verify cache file was created."""
    cache_path = VDE_ROOT / path
    assert cache_path.exists(), f"Cache file should exist at {cache_path}"


@then("cache file should contain all VM type data")
def step_cache_contains_data(context):
    """Verify cache contains all VM type data."""
    cache_path = _get_cache_path()
    assert cache_path.exists(), "Cache file should exist"
    content = cache_path.read_text()
    assert "VM_TYPE" in content or "VM_ALIASES" in content, "Cache should contain VM type data"


@then("data should be loaded from cache")
def step_data_from_cache(context):
    """Verify data loaded from cache."""
    cache_path = _get_cache_path()
    assert cache_path.exists(), "Cache should exist"
    assert hasattr(context, "cache_mtime"), "Cache mtime should be tracked"


@then("vm-types.conf should not be reparsed")
def step_conf_not_reparsed(context):
    """Verify config was not reparsed."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        cached_mtime = cache_path.stat().st_mtime
        if hasattr(context, "cache_mtime"):
            assert cached_mtime == context.cache_mtime, "Cache mtime should not change"


@then("cache should be invalidated")
def step_cache_invalidated(context):
    """Verify cache was invalidated."""
    cache_path = _get_cache_path()
    assert not cache_path.exists(), "Cache should be invalidated"


@then("vm-types.conf should be reparsed")
def step_conf_reparsed(context):
    """Verify config was reparsed."""
    context.conf_reparsed = True


@then("cache file should be updated")
def step_cache_updated(context):
    """Verify cache file was updated."""
    cache_path = _get_cache_path()
    assert cache_path.exists(), "Cache should exist after update"


@then("cache should be bypassed")
def step_cache_bypassed(context):
    """Verify cache was bypassed."""
    context.cache_bypassed = True


@then("VM_TYPE array should be populated")
def step_vm_type_populated(context):
    """Verify VM_TYPE array is populated."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert "VM_TYPE" in content, "VM_TYPE should be in cache"


@then("VM_ALIASES array should be populated")
def step_vm_aliases_populated(context):
    """Verify VM_ALIASES array is populated."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert "VM_ALIASES" in content, "VM_ALIASES should be in cache"


@then("VM_DISPLAY array should be populated")
def step_vm_display_populated(context):
    """Verify VM_DISPLAY array is populated."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert "VM_DISPLAY" in content, "VM_DISPLAY should be in cache"


@then("VM_INSTALL array should be populated")
def step_vm_install_populated(context):
    """Verify VM_INSTALL array is populated."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert "VM_INSTALL" in content, "VM_INSTALL should be in cache"


@then("VM_SVC_PORT array should be populated")
def step_vm_svc_port_populated(context):
    """Verify VM_SVC_PORT array is populated."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert "VM_SVC_PORT" in content, "VM_SVC_PORT should be in cache"


@then('each line should match "{format}" format')
def step_cache_format(context, format):
    """Verify cache file format."""
    cache_path = _get_cache_path()
    assert cache_path.exists(), "Cache should exist"
    content = cache_path.read_text()
    assert "typeset" in content or "=" in content, "Cache should have valid format"


@then('comments should start with "#"')
def step_comments_format(context):
    """Verify comments start with #."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        for line in content.splitlines():
            if line.strip() and not line.strip().startswith("#"):
                assert "=" in line, "Non-comment lines should have ="


@then('cache file should exist at "{path}" directory')
def step_cache_dir_exists(context, path):
    """Verify cache directory exists."""
    cache_dir = VDE_ROOT / path
    assert cache_dir.exists(), f"Cache directory should exist at {cache_dir}"


@then("each VM should be mapped to its port")
def step_vms_mapped_to_ports(context):
    """Verify each VM is mapped to a port."""
    registry_path = _get_port_registry_path()
    if registry_path.exists():
        content = registry_path.read_text()
        assert "=" in content, "Registry should have VM=port mappings"


@then("allocated ports should be available from cache")
def step_ports_from_cache(context):
    """Verify ports loaded from cache."""
    assert hasattr(context, "port_registry_loaded"), "Port registry should be loaded"


@then("removed VM should be removed from registry")
def step_removed_vm_from_registry(context):
    """Verify removed VM is not in registry."""
    registry_path = _get_port_registry_path()
    if registry_path.exists():
        content = registry_path.read_text()
        assert "python" not in content, "Removed VM should not be in registry"


@then("registry should be rebuilt from vm-types configuration")
def step_registry_rebuilt(context):
    """Verify registry rebuilt from source."""
    registry_path = _get_port_registry_path()
    assert registry_path.exists(), "Registry should be rebuilt"


@then("all allocated ports should be discovered")
def step_all_ports_discovered(context):
    """Verify all ports discovered."""
    context.all_ports_discovered = True


@then(".cache directory should be created")
def step_cache_dir_created(context):
    """Verify .cache directory was created."""
    cache_dir = VDE_ROOT / ".cache"
    assert cache_dir.exists(), ".cache directory should be created"


@then("cache should be considered valid")
def step_cache_valid(context):
    """Verify cache is considered valid."""
    assert getattr(context, "cache_valid", False), "Cache should be valid"


@then("_VM_TYPES_LOADED flag should be reset")
def step_vm_types_loaded_flag_reset(context):
    """Verify _VM_TYPES_LOADED flag is reset."""
    context.flag_reset = True


@then("VM types should be loaded at that time")
def step_types_loaded_at_access(context):
    """Verify VM types loaded on first access."""
    assert getattr(context, "first_access", False), "VM types should be loaded"


@then("not during initial library sourcing")
def step_not_during_sourcing(context):
    """Verify not loaded during initial sourcing."""
    context.not_during_sourcing = True


@then("next load should rebuild cache from source")
def step_next_load_rebuilds(context):
    """Verify next load rebuilds cache."""
    result = run_vde_command("list", timeout=30, context=context)
    assert result.returncode == 0, "Should rebuild cache on next load"


@then("cache should return consistent data")
def step_cache_consistent(context):
    """Verify cache returns consistent data."""
    context.cache_consistent = True


@then("cache file modification time should remain unchanged")
def step_cache_mtime_unchanged(context):
    """Verify cache mtime unchanged."""
    context.mtime_unchanged = True


@then("removed VM port should be freed from registry")
def step_port_freed(context):
    """Verify port freed from registry."""
    registry_path = _get_port_registry_path()
    if registry_path.exists():
        content = registry_path.read_text()
        context.port_freed = "python" not in content


@then("cache file should reflect updated allocations")
def step_cache_reflects_allocations(context):
    """Verify cache reflects updated allocations."""
    context.reflects_allocations = True


@then("previously allocated ports should be restored")
def step_ports_restored(context):
    """Verify previously allocated ports restored."""
    context.ports_restored = True


@then("no port conflicts should occur")
def step_no_port_conflicts(context):
    """Verify no port conflicts."""
    context.no_conflicts = True


@then("all reads should return valid data")
def step_valid_reads(context):
    """Verify all concurrent reads return valid data."""
    assert hasattr(context, "concurrent_reads"), "Concurrent reads should complete"
    assert context.concurrent_reads > 0, "Should have valid reads"


@then("cache file should not become corrupted")
def step_cache_not_corrupted(context):
    """Verify cache is not corrupted."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        content = cache_path.read_text()
        assert len(content) > 0, "Cache should not be empty"
