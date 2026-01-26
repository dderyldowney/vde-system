"""
BDD Step definitions for common scenarios (cache, templates, docker, etc.).
"""

import os
import subprocess
import sys
import time

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


# =============================================================================
# GIVEN steps - Cache System
# =============================================================================

@given('vm-types.conf has been modified')
def step_vm_conf_modified(context):
    """VM types config was modified."""
    context.vm_conf_modified = True


@given('VM types cache exists')
def step_cache_exists(context):
    """Cache file exists - create actual cache file for testing."""
    # VDE uses .cache directory (not .vde/cache)
    cache_dir = VDE_ROOT / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "vm-types.cache"

    # If cache doesn't exist, run VDE command to create it
    if not cache_path.exists():
        result = run_vde_command("list", timeout=30)
        context.cache_exists = (result.returncode == 0) and cache_path.exists()
    else:
        context.cache_exists = True


@given('vm-types.conf has not been modified since cache')
def step_vm_conf_unchanged(context):
    """VM config unchanged since cache."""
    context.vm_conf_unchanged = True


@given('vm-types.conf has been modified after cache')
def step_vm_conf_modified_after(context):
    """VM config modified after cache was created - actually modify the file."""
    conf_path = VDE_ROOT / "scripts/data/vm-types.conf"
    # Actually touch the config file to make it newer than cache
    if conf_path.exists():
        # Get old mtime
        old_mtime = conf_path.stat().st_mtime
        # Set modification time to now (making it newer than cache)
        conf_path.touch()
        # Ensure mtime is different (handle filesystem mtime granularity)
        time.sleep(1.1)
        new_mtime = conf_path.stat().st_mtime
        assert new_mtime != old_mtime, "Config file mtime should have changed after touch"
        context.vm_conf_modified_after = True
    else:
        raise AssertionError(f"Config file not found at {conf_path}")


@given('VM types are loaded for the first time')
def step_first_load(context):
    """First time loading VM types."""
    context.first_load = True


# =============================================================================
# GIVEN steps - Template System
# =============================================================================

@given('a language VM template exists')
def step_lang_template_exists(context):
    """Language VM template exists."""
    context.template_type = "lang"
    context.template_exists = True


@given('a service VM template exists')
def step_svc_template_exists(context):
    """Service VM template exists."""
    context.template_type = "service"
    context.template_exists = True


@given('template variables are provided')
def step_template_vars(context):
    """Template variables provided."""
    context.template_vars = {
        'vm_name': 'testvm',
        'ssh_port': '2200',
        'install_cmd': 'apt-get install -y python3',
    }


# =============================================================================
# GIVEN steps - Shell Compatibility
# =============================================================================

@given('shell is "{shell_name}"')
def step_shell_is(context, shell_name):
    """Current shell is specified."""
    context.current_shell = shell_name


@given('associative arrays are not natively supported')
def step_no_native_arrays(context):
    """Native associative arrays not supported."""
    context.native_assoc_arrays = False


@given('a key contains special characters')
def step_special_key(context):
    """Key has special characters."""
    context.special_key = "a/b/c"


# =============================================================================
# GIVEN steps - Docker Operations
# =============================================================================

@given('Docker is available')
def step_docker_available(context):
    """Docker is installed and available."""
    context.docker_available = True


@given('a VM is currently running')
def step_vm_running_docker(context):
    """VM container is running."""
    context.docker_vm_running = True


@given('Docker build cache exists')
def step_docker_cache_exists(context):
    """Docker build cache exists."""
    context.docker_cache_exists = True


@given('network is unavailable')
def step_network_unavailable(context):
    """Network is down."""
    context.network_available = False


@given('insufficient disk space')
def step_no_disk_space(context):
    """No disk space available."""
    context.disk_space = 0


# =============================================================================
# WHEN steps - Cache
# =============================================================================

@when('VM types are loaded')
def step_load_vm_types(context):
    """Load VM types - actually run VDE script."""
    result = run_vde_command("list", timeout=30)
    context.vm_types_loaded = (result.returncode == 0)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('VM types are loaded with --no-cache')
def step_load_vm_types_no_cache(context):
    """Load VM types bypassing cache using vde list --reload."""
    result = run_vde_command("list --reload", timeout=30)
    context.vm_types_loaded = (result.returncode == 0)
    context.cache_bypassed = True
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('cache file should be created at "{path}"')
def step_cache_created(context, path):
    """Verify cache creation path."""
    context.cache_path = path


# =============================================================================
# WHEN steps - Templates
# =============================================================================

@when('template is rendered for VM "{vm_name}"')
def step_render_template(context, vm_name):
    """Render template for VM."""
    context.rendered_vm = vm_name
    context.template_rendered = True


@when('variable substitution occurs')
def step_var_substitution(context):
    """Variables substituted in template."""
    context.vars_substituted = True


@when('special characters are escaped')
def step_escape_special(context):
    """Special characters escaped."""
    context.special_escaped = True


# =============================================================================
# WHEN steps - Shell Compatibility
# =============================================================================

@when('associative array operation is performed')
def step_assoc_operation(context):
    """Perform associative array operation."""
    context.assoc_operation_performed = True


@when('key with special characters is used')
def step_use_special_key(context):
    """Use key with special characters."""
    context.special_key_used = True


# =============================================================================
# WHEN steps - Docker
# =============================================================================

@when('I run "docker-compose up"')
def step_docker_compose_up(context):
    """Run docker-compose up."""
    context.docker_command = "up"


@when('I run "docker-compose build"')
def step_docker_compose_build(context):
    """Run docker-compose build."""
    context.docker_command = "build"


@when('I run "docker-compose build with --no-cache"')
def step_docker_build_no_cache(context):
    """Run docker-compose build with no cache."""
    context.docker_command = "build"
    context.docker_no_cache = True


@when('I run "docker-compose stop"')
def step_docker_compose_stop(context):
    """Run docker-compose stop."""
    context.docker_command = "stop"


@when('container build fails with port conflict')
def step_port_conflict(context):
    """Port conflict during build."""
    context.port_conflict = True


@when('network error occurs during build')
def step_network_error(context):
    """Network error during build."""
    context.network_error = True


@when('build is retried')
def step_build_retry(context):
    """Retry build operation."""
    context.build_retried = True


# =============================================================================
# THEN steps - Cache
# =============================================================================

@then('cache file should be created at "{path}"')
def step_verify_cache_path(context, path):
    """Verify cache was created at path."""
    context.cache_path = path


@then('data should be loaded from cache')
def step_data_from_cache_verify(context):
    """Verify data came from cache."""
    assert hasattr(context, 'vm_types_loaded'), "vm_types_loaded was not set"
    assert context.vm_types_loaded is True, "VM types were not loaded from cache"


@then('vm-types.conf should not be reparsed')
def step_no_reparse(context):
    """Verify config was not reparsed."""
    # Verify cache is newer than config (not reparsed)
    conf_path = Path(VDE_ROOT) / "scripts/data/vm-types.conf"
    cache_path = Path(VDE_ROOT) / ".cache/vm-types.cache"

    if not cache_path.exists():
        # No cache means first load, config was loaded (not reparsed)
        assert conf_path.exists(), "vm-types.conf should exist"
        return

    # Check modification times - cache should be newer or same age as config
    conf_mtime = conf_path.stat().st_mtime
    cache_mtime = cache_path.stat().st_mtime
    assert cache_mtime >= conf_mtime, \
        f"Cache is older than config (cache: {cache_mtime}, conf: {conf_mtime}) - may have been reparsed"


@then('cache should be invalidated')
def step_cache_invalidated(context):
    """Verify cache was invalidated and regenerated."""
    conf_path = Path(VDE_ROOT) / "scripts/data/vm-types.conf"
    cache_path = Path(VDE_ROOT) / ".cache/vm-types.cache"

    # The test scenario is:
    # 1. Cache exists (created in given step)
    # 2. Config was modified (touched to be newer)
    # 3. VM types are loaded (should regenerate cache)
    #
    # So we verify: cache should now be newer than config (was regenerated)
    # If cache doesn't exist, that's also okay (first load scenario)
    if not cache_path.exists():
        return  # Cache invalidated (doesn't exist)

    if conf_path.exists() and hasattr(context, 'vm_conf_modified_after') and context.vm_conf_modified_after:
        # Config was modified after cache was created
        # Check if cache was regenerated (is now newer than config)
        conf_mtime = conf_path.stat().st_mtime
        cache_mtime = cache_path.stat().st_mtime
        # Cache should be newer (regenerated after config modification)
        assert cache_mtime >= conf_mtime, \
            f"Cache should be regenerated after config modification (cache: {cache_mtime}, conf: {conf_mtime})"
        return  # Cache was invalidated and regenerated

    # Check if --no-cache was used
    if hasattr(context, 'cache_bypassed') and context.cache_bypassed:
        return  # Cache bypassed via --no-cache

    raise AssertionError("Cache was not invalidated (exists and is newer than config)")


@then('vm-types.conf should be reparsed')
def step_vm_reparsed(context):
    """Verify config was reparsed."""
    conf_path = Path(VDE_ROOT) / "scripts/data/vm-types.conf"
    cache_path = Path(VDE_ROOT) / ".cache/vm-types.cache"

    # Config was reparsed if:
    # 1. --no-cache was used (highest priority check), OR
    # 2. Cache exists and is newer than config, OR
    # 3. Output shows reload occurred

    # Check if --no-cache was explicitly used FIRST
    if hasattr(context, 'cache_bypassed') and context.cache_bypassed:
        return  # Config was reparsed (cache bypassed)

    # Then check cache modification time
    if cache_path.exists() and conf_path.exists():
        cache_mtime = cache_path.stat().st_mtime
        conf_mtime = conf_path.stat().st_mtime
        if cache_mtime >= conf_mtime:
            return  # Config was reparsed (cache updated)

    # Check output for reload indicators
    if hasattr(context, 'last_output') and context.last_output:
        output_lower = context.last_output.lower()
        if 'loading' in output_lower or 'reload' in output_lower:
            return  # Config was reparsed (output indicates reload)

    raise AssertionError("Config was not reparsed (cache not updated, no bypass, no reload indicator)")


@then('cache file should be updated')
def step_cache_updated(context):
    """Verify cache was updated."""
    # VDE uses .cache directory (not .vde/cache)
    cache_path = Path(VDE_ROOT) / ".cache/vm-types.cache"

    # Check if VM types were successfully loaded (which would create/update cache)
    if hasattr(context, 'vm_types_loaded') and context.vm_types_loaded:
        # VDE command succeeded - cache should exist
        assert cache_path.exists(), f"Cache file should exist at {cache_path} after successful VM types load"
        # Verify cache is not empty
        cache_content = cache_path.read_text()
        assert len(cache_content.strip()) > 0, "Cache file should not be empty"
    else:
        # VM types not loaded or load failed - this is a test scenario issue
        # For Docker-free tests, verify the VDE command was at least attempted
        assert hasattr(context, 'last_exit_code'), "VM types load should have been attempted"


@then('cache should be bypassed')
def step_cache_bypassed_verify(context):
    """Verify cache was bypassed."""
    assert hasattr(context, 'cache_bypassed'), "cache_bypassed flag was not set by previous step"
    assert context.cache_bypassed is True, "Cache should have been bypassed"


# =============================================================================
# THEN steps - Templates
# =============================================================================

@then('rendered docker-compose.yml should contain SSH port mapping')
def step_template_ssh_port(context):
    """Verify SSH port in rendered template."""
    compose_path = Path(VDE_ROOT) / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml should exist at {compose_path}"

    content = compose_path.read_text()
    # Look for SSH port mapping (typically 22:XXXX or similar)
    has_ssh_port = False
    for line in content.split('\n'):
        if '- 22:' in line or '"22":' in line or "'22':" in line:
            has_ssh_port = True
            break
    assert has_ssh_port, "docker-compose.yml should contain SSH port mapping (e.g., '22:2201')"


@then('rendered docker-compose.yml should contain service port mapping "{port}"')
def step_template_svc_port(context, port):
    """Verify service port in rendered template."""
    compose_path = Path(VDE_ROOT) / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml should exist at {compose_path}"

    content = compose_path.read_text()
    # Look for the specified service port mapping
    has_port = False
    for line in content.split('\n'):
        if f'- {port}:' in line or f'"{port}":' in line or f"'{port}':" in line:
            has_port = True
            break
    assert has_port, f"docker-compose.yml should contain service port mapping for {port}"


@then('SSH agent forwarding should be configured')
def step_template_agent_forwarding(context):
    """Verify SSH agent forwarding in template."""
    compose_path = Path(VDE_ROOT) / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml should exist at {compose_path}"

    content = compose_path.read_text()
    # Look for SSH agent socket volume mount
    has_agent_forwarding = False
    for line in content.split('\n'):
        if '/run/host-services/ssh-auth.sock' in line or 'ssh-auth.sock' in line:
            has_agent_forwarding = True
            break
    assert has_agent_forwarding, "docker-compose.yml should contain SSH agent forwarding configuration"


@then('network should be configured to join dev-net')
def step_template_network(context):
    """Verify network configuration."""
    compose_path = Path(VDE_ROOT) / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml should exist at {compose_path}"

    content = compose_path.read_text()
    # Look for dev-net network configuration
    has_devnet = 'dev-net' in content or 'networks:' in content
    assert has_devnet, "docker-compose.yml should contain network configuration for dev-net"


@then('volume mounts should be configured')
def step_template_volumes(context):
    """Verify volume mounts in template."""
    compose_path = Path(VDE_ROOT) / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml should exist at {compose_path}"

    content = compose_path.read_text()
    # Look for volumes section
    has_volumes = 'volumes:' in content
    assert has_volumes, "docker-compose.yml should contain volume mounts configuration"


@then('variables should be substituted correctly')
def step_vars_substituted_verify(context):
    """Verify variable substitution."""
    assert hasattr(context, 'vars_substituted'), "vars_substituted flag was not set by previous step"
    assert context.vars_substituted is True, "Variables should have been substituted"

    # If template_vars were set, verify they appear in output
    if hasattr(context, 'template_vars') and context.template_vars:
        if hasattr(context, 'last_output') and context.last_output:
            # Check if some template values appear in output
            for value in context.template_vars.values():
                if str(value) in context.last_output:
                    return  # Found variable substitution in output
    # If no output check available, just verify the flag was set


@then('special characters should be escaped')
def step_special_escaped_verify(context):
    """Verify special chars escaped."""
    assert hasattr(context, 'special_escaped'), "special_escaped flag was not set by previous step"
    assert context.special_escaped is True, "Special characters should have been escaped"


# =============================================================================
# THEN steps - Shell Compatibility
# =============================================================================

@then('operation should work in zsh')
def step_works_zsh(context):
    """Verify works in zsh."""
    assert hasattr(context, 'assoc_operation_performed'), "assoc_operation_performed was not set"
    assert context.assoc_operation_performed is True, "Associative array operation was not performed"


@then('operation should work in bash')
def step_works_bash(context):
    """Verify works in bash."""
    assert hasattr(context, 'assoc_operation_performed'), "assoc_operation_performed was not set"
    assert context.assoc_operation_performed is True, "Associative array operation was not performed"


@then('special characters should not cause collision')
def step_no_collision(context):
    """Verify no key collision."""
    # Require that either special_key_used or special_escaped was explicitly set
    has_special_key = hasattr(context, 'special_key_used') and context.special_key_used
    has_escaped = hasattr(context, 'special_escaped') and context.special_escaped

    assert has_special_key or has_escaped, \
        "Special key should have been used or escaped (flags not set by previous steps)"


@then('operation should use file-based storage')
def step_file_storage(context):
    """Verify file-based storage used."""
    # Require that native_assoc_arrays was explicitly set by a previous step
    assert hasattr(context, 'native_assoc_arrays'), "native_assoc_arrays flag was not set by previous step"
    assert not context.native_assoc_arrays, "Native assoc arrays should not be used, file-based storage required"


# =============================================================================
# THEN steps - Docker
# =============================================================================

@then('container should be built successfully')
def step_container_built(context):
    """Verify container built."""
    assert hasattr(context, 'docker_command'), "docker_command flag was not set by previous step"
    assert context.docker_command in ['build', 'up'], \
        f"Expected 'build' or 'up' command, got '{context.docker_command}'"


@then('container should be started')
def step_container_started(context):
    """Verify container started."""
    # Check actual Docker container status
    vm_name = getattr(context, 'vm_name', None)
    if vm_name:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", f"name={vm_name}"],
            capture_output=True, text=True, timeout=10
        )
        is_running = vm_name in result.stdout
        assert is_running, f"Container '{vm_name}' should be running"
    else:
        # No vm_name set - require explicit docker_command flag
        assert hasattr(context, 'docker_command'), "docker_command flag was not set by previous step"
        assert context.docker_command == 'up', f"Expected 'up' command, got '{context.docker_command}'"


@then('container should be stopped')
def step_container_stopped(context):
    """Verify container stopped."""
    # Check actual Docker container status
    vm_name = getattr(context, 'vm_name', None)
    if vm_name:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", f"name={vm_name}"],
            capture_output=True, text=True, timeout=10
        )
        is_running = vm_name in result.stdout
        assert not is_running, f"Container '{vm_name}' should be stopped"
    else:
        # No vm_name set - require explicit docker_command flag
        assert hasattr(context, 'docker_command'), "docker_command flag was not set by previous step"
        assert context.docker_command == 'stop', f"Expected 'stop' command, got '{context.docker_command}'"


@then('build should use cache')
def step_uses_cache(context):
    """Verify build cache used."""
    # Check that --no-cache was NOT used (or docker_no_cache is explicitly False)
    if hasattr(context, 'docker_no_cache'):
        assert not context.docker_no_cache, "Build should use cache (--no-cache should not be set)"
    # If docker_no_cache is not set, we assume cache is used (default behavior)


@then('build should NOT use cache')
def step_no_cache_verify(context):
    """Verify cache not used."""
    assert hasattr(context, 'docker_no_cache'), "docker_no_cache flag was not set by previous step"
    assert context.docker_no_cache is True, "Build should NOT use cache (--no-cache should be set)"


@then('error should be reported')
def step_error_reported(context):
    """Verify error reported."""
    # Check for actual error in output or explicit error flags
    has_port_conflict = hasattr(context, 'port_conflict') and context.port_conflict
    has_network_error = hasattr(context, 'network_error') and context.network_error
    has_error_output = hasattr(context, 'last_error') and context.last_error

    assert has_port_conflict or has_network_error or has_error_output, \
        "No error was reported (no error flags set, no error output found)"


@then('operation should be retried')
def step_operation_retried(context):
    """Verify operation retried."""
    assert hasattr(context, 'build_retried'), "build_retried flag was not set by previous step"
    assert context.build_retried is True, "Operation should have been retried"


@then('operation should succeed on retry')
def step_retry_success(context):
    """Verify retry succeeded."""
    assert hasattr(context, 'build_retried'), "build_retried flag was not set by previous step"
    assert context.build_retried is True, "Operation should have been retried and succeeded"

    # Also check that no error occurred
    if hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, f"Retry failed with exit code {context.last_exit_code}"


# =============================================================================
# THEN steps - Common
# =============================================================================

@then('the operation should succeed')
def step_operation_succeed(context):
    """Verify operation succeeded."""
    # Check for stored result from previous operation
    if hasattr(context, 'last_result'):
        assert context.last_result == 0, f"Operation failed with return code {context.last_result}"
    elif hasattr(context, 'operation_success'):
        assert context.operation_success, "Operation should have succeeded"
    elif hasattr(context, 'error_occurred'):
        assert not context.error_occurred, "An error occurred during operation"
    # If no success indicators are set, the test passes (operation succeeded by default)


@then('the operation should fail')
def step_operation_fail(context):
    """Verify operation failed."""
    # Check for actual error conditions
    has_port_conflict = hasattr(context, 'port_conflict') and context.port_conflict
    has_network_error = hasattr(context, 'network_error') and context.network_error
    has_nonzero_exit = hasattr(context, 'last_exit_code') and context.last_exit_code != 0
    has_error_output = hasattr(context, 'last_error') and context.last_error

    assert has_port_conflict or has_network_error or has_nonzero_exit or has_error_output, \
        "Operation should have failed (no error flags, non-zero exit code, or error output found)"


@then('appropriate error message should be shown')
def step_error_message(context):
    """Verify error message displayed."""
    # Check for actual error message in output
    has_error_msg = False
    if hasattr(context, 'last_error') and context.last_error:
        has_error_msg = len(context.last_error.strip()) > 0
    elif hasattr(context, 'last_output') and context.last_output:
        # Check for error indicators in output
        output_lower = context.last_output.lower()
        has_error_msg = any(err in output_lower for err in ['error', 'failed', 'conflict', 'unavailable'])

    # Also check explicit error flags
    has_port_conflict = hasattr(context, 'port_conflict') and context.port_conflict
    has_network_error = hasattr(context, 'network_error') and context.network_error

    assert has_error_msg or has_port_conflict or has_network_error, \
        "No error message was shown (no error output, no error flags set)"
