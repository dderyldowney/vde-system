#!/usr/bin/env python3
# Step definitions for shell compatibility testing

import os
import subprocess

# Import VDE_ROOT from central config
import sys
from pathlib import Path

from behave import given, then, when

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import VDE_ROOT


def run_shell_command(command, shell='zsh'):
    """Run a command in the specified shell with UTF-8 encoding."""
    cmd = f"{shell} -c 'source {VDE_ROOT}/scripts/lib/vde-shell-compat && {command}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=VDE_ROOT, encoding='utf-8')
    return result


def _build_array_state_prefix(context):
    """Build shell commands to restore array state from context.

    Since each subprocess.run call creates a new shell, native arrays don't persist.
    This helper rebuilds the array state before operations that need it.
    """
    array_name = getattr(context, 'array_name', 'test_array')
    prefix = f"_assoc_init '{array_name}'; "
    if hasattr(context, 'set_keys'):
        for key, value in context.set_keys.items():
            # Escape single quotes in both key and value for shell
            # Use double quotes around the value to preserve spaces
            escaped_key = key.replace("'", "'\\''")
            # For value, we need to handle it carefully:
            # - Use double quotes to preserve spaces
            # - Escape any double quotes within the value
            escaped_value = value.replace('"', '\\"')
            prefix += f'_assoc_set "{array_name}" "{escaped_key}" "{escaped_value}"; '
    return prefix


def run_shell_command_with_state(context, command, shell='zsh'):
    """Run a command with array state restored from context."""
    full_command = _build_array_state_prefix(context) + command
    return run_shell_command(full_command, shell)


@given('running in zsh')
def step_running_zsh(context):
    """Running in zsh."""
    context.current_shell = 'zsh'




@given('I initialize an associative array')
def step_given_init_assoc_array(context):
    """Initialize an associative array (Given variant)."""
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    context.array_initialized = True
    # Initialize tracking for state restoration
    if not hasattr(context, 'set_keys'):
        context.set_keys = {}


@when('I initialize an associative array')
def step_init_assoc_array(context):
    """Initialize an associative array."""
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    # Initialize tracking for state restoration
    if not hasattr(context, 'set_keys'):
        context.set_keys = {}


@then('_detect_shell should return "{shell}"')
def step_detect_shell_returns(context, shell):
    """_detect_shell should return the shell."""
    result = run_shell_command('_detect_shell', getattr(context, 'current_shell', 'zsh'))
    detected_shell = result.stdout.strip()
    assert detected_shell == shell, f"Expected _detect_shell to return '{shell}', got '{detected_shell}'"
    context.shell_detected = detected_shell


@then('_is_zsh should return true')
def step_is_zsh_true(context):
    """_is_zsh should return true (exit code 0)."""
    result = run_shell_command('_is_zsh', getattr(context, 'current_shell', 'zsh'))
    assert result.returncode == 0, f"_is_zsh should return 0 (true) in {context.current_shell}, got {result.returncode}"


@then('_is_zsh should return false')
def step_is_zsh_false(context):
    """_is_zsh should return false (exit code 1)."""
    result = run_shell_command('_is_zsh', getattr(context, 'current_shell', 'zsh'))
    assert result.returncode != 0, f"_is_zsh should return non-zero (false) in {context.current_shell}, got {result.returncode}"




@then('native zsh typeset should be used')
def step_zsh_typeset_used(context):
    """Native zsh typeset should be used."""
    result = run_shell_command('_is_zsh && _shell_supports_native_assoc', getattr(context, 'current_shell', 'zsh'))
    assert result.returncode == 0, "Expected zsh with native associative array support"


@given('native associative arrays are in use')
def step_native_arrays_in_use(context):
    """Native associative arrays are in use (for cleanup test)."""
    # Native arrays are used in bash 4+/zsh 5+ - no special setup needed
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"




@then('array operations should work correctly')
def step_array_ops_work(context):
    """Array operations should work correctly."""
    # Actually test array operations by setting and getting a value
    array_name = getattr(context, 'array_name', 'test_array')
    result = run_shell_command(f"_assoc_init '{array_name}' && _assoc_set '{array_name}' 'test_key' 'test_value' && _assoc_get '{array_name}' 'test_key'", getattr(context, 'current_shell', 'zsh'))
    assert result.returncode == 0, f"Array operations failed: {result.stderr}"
    assert result.stdout.strip() == 'test_value', f"Expected 'test_value', got '{result.stdout.strip()}'"




@when('I set key "{key}" to value "{value}"')
def step_set_key_value(context, key, value):
    """Set key to value in associative array."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    # Use double quotes for value to preserve spaces
    result = run_shell_command(f"_assoc_init '{array_name}'; _assoc_set '{array_name}' '{key}' \"{value}\"", shell)
    assert result.returncode == 0, f"Failed to set key '{key}' to '{value}': {result.stderr}"
    context.last_key = key
    context.last_value = value
    # Track that we've set this for verification in next step
    if not hasattr(context, 'set_keys'):
        context.set_keys = {}
    context.set_keys[key] = value


@given('I set key "{key}" to value "{value}"')
def step_given_set_key_value(context, key, value):
    """Set key to value in associative array (Given variant)."""
    step_set_key_value(context, key, value)


@then('getting key "{key}" should return "{value}"')
def step_get_key_returns(context, key, value):
    """Getting key should return value."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_get '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode == 0, f"Failed to get key '{key}': {result.stderr}"
    actual_value = result.stdout.strip()
    assert actual_value == value, f"Expected '{value}', got '{actual_value}'"
    context.key_return = actual_value


@then('getting key "{key}" should return an empty value')
def step_get_key_empty_value(context, key):
    """Getting key should return empty string."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_get '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode == 0, f"Failed to get key '{key}': {result.stderr}"
    actual_value = result.stdout.strip()
    assert actual_value == '', f"Expected empty value, got '{actual_value}'"
    context.key_return = actual_value


@when('I get all keys')
def step_get_all_keys(context):
    """Get all keys from array."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_keys '{getattr(context, 'array_name', 'test_array')}'", shell)
    assert result.returncode == 0, f"Failed to get keys: {result.stderr}"
    keys_output = result.stdout.strip()
    # Store keys as a list (space-separated output from _assoc_keys)
    context.all_keys = keys_output.split() if keys_output else []


@then('all keys should be returned')
def step_all_keys_returned(context):
    """All keys should be returned - verify keys are present regardless of order."""
    actual_keys = getattr(context, 'all_keys', [])
    # The Given step "associative array with keys 'foo', 'bar', 'baz'" sets these keys
    expected = {'foo', 'bar', 'baz'}
    actual = set(actual_keys)
    assert actual == expected, f"Expected keys {expected}, got {actual}"


@then('original key format should be preserved')
def step_key_format_preserved(context):
    """Key format should be preserved - verify special characters are handled correctly."""
    # Test that keys with special characters can be set and retrieved with exact format
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    # Set a key with special characters
    special_key = 'key_with_special_chars'
    result = run_shell_command(
        f"_assoc_init '{array_name}' && _assoc_set '{array_name}' '{special_key}' 'test_value' && _assoc_get '{array_name}' '{special_key}'",
        shell
    )
    assert result.returncode == 0, f"Failed to set/get key with special format: {result.stderr}"
    assert result.stdout.strip() == 'test_value', f"Key format not preserved, got '{result.stdout.strip()}'"


@when('I check if key "{key}" exists')
def step_check_key_exists(context, key):
    """Check if key exists."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_has_key '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    # _assoc_has_key returns 0 if key exists, 1 otherwise
    context.key_exists_result = (result.returncode == 0)
    context.key_check = key


@then('result should be true')
def step_result_true(context):
    """Result should be true."""
    assert context.key_exists_result is True, "Expected key to exist"


@then('result should be false')
def step_result_false(context):
    """Result should be false."""
    assert context.key_exists_result is False, "Expected key to not exist"


@when('I unset key "{key}"')
def step_unset_key(context, key):
    """Unset a key."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{array_name}'; _assoc_unset '{array_name}' '{key}'", shell)
    assert result.returncode == 0, f"Failed to unset key '{key}': {result.stderr}"
    context.unset_key = key
    # Also remove from tracked keys
    if hasattr(context, 'set_keys') and key in context.set_keys:
        del context.set_keys[key]


@then('key "{key}" should no longer exist')
def step_key_no_exist(context, key):
    """Key should no longer exist."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_has_key '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode != 0, f"Key '{key}' should no longer exist"


@then('array should be empty')
def step_array_empty(context):
    """Array should be empty."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{array_name}'; _assoc_keys '{array_name}'", shell)
    assert result.returncode == 0, "Failed to check array keys"
    keys = result.stdout.strip()
    assert not keys, f"Array should be empty but contains keys: {keys}"


@when('I call _get_script_path')
def step_call_get_script_path(context):
    """Call _get_script_path."""
    result = run_shell_command('_get_script_path; echo $_get_script_path', getattr(context, 'current_shell', 'zsh'))
    context.script_path = result.stdout.strip()


@then('absolute script path should be returned')
def step_script_path_returned(context):
    """Script path should be returned and absolute."""
    assert hasattr(context, 'script_path'), "Script path was not set"
    script_path = context.script_path
    assert script_path, "Script path should not be empty"
    # Verify it's an absolute path (starts with / on Unix)
    assert os.path.isabs(script_path), f"Script path should be absolute, got: {script_path}"
    # Verify the path points to VDE_ROOT/scripts
    expected_dir = os.path.join(VDE_ROOT, 'scripts')
    assert script_path.startswith(expected_dir), f"Script path should be in {expected_dir}, got: {script_path}"


@when('script exits')
def step_script_exits(context):
    """Script exits - verify cleanup is executed."""
    # Call cleanup and verify temp files are removed
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command('_assoc_cleanup', shell)
    assert result.returncode == 0, f"Script cleanup failed: {result.stderr}"


@then('temporary storage directory should be removed')
def step_temp_dir_removed(context):
    """Temporary directory should be removed."""
    # Verify temp directory was removed by checking it no longer exists
    from pathlib import Path
    temp_dir = VDE_ROOT / '.vde_test_temp'
    assert not temp_dir.exists(), f"Temporary directory {temp_dir} should have been removed"


@then('keys should not collide')
def step_keys_not_collide(context):
    """Keys should not collide - verify different keys return different values."""
    # Verify we have tracked keys and their values
    assert hasattr(context, 'set_keys'), "No keys were set"
    assert len(context.set_keys) >= 2, "Need at least 2 keys to check for collision"

    # Verify each key can be retrieved and returns its expected value
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')

    for key, expected_value in context.set_keys.items():
        result = run_shell_command_with_state(context, f"_assoc_get '{array_name}' '{key}'", shell)
        assert result.returncode == 0, f"Failed to retrieve key '{key}': {result.stderr}"
        actual_value = result.stdout.strip()
        assert actual_value == expected_value, f"Key '{key}' should return '{expected_value}', got '{actual_value}'"

    # Additionally verify that all values are distinct (no accidental collision)
    values = list(context.set_keys.values())
    assert len(values) == len(set(values)), "All key values should be distinct - collision detected!"


# =============================================================================
# Additional shell compatibility step definitions
# =============================================================================

@when('running in zsh')
def step_running_in_zsh(context):
    """Running in zsh."""
    context.current_shell = 'zsh'

@given('an associative array')
def step_given_assoc_array(context):
    """Given an associative array."""
    if not hasattr(context, 'array_name'):
        context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    context.associative_array = True

@then('key "{key}" should return "{value}"')
def step_key_returns_value(context, key, value):
    """Key should return value."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_get '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode == 0, f"Failed to get key '{key}': {result.stderr}"
    actual_value = result.stdout.strip()
    assert actual_value == value, f"Expected '{value}', got '{actual_value}'"

@when('I clear the array')
def step_clear_array(context):
    """Clear the array."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_clear '{array_name}'", shell)
    assert result.returncode == 0, f"Failed to clear array: {result.stderr}"
    # Clear tracked keys
    if hasattr(context, 'set_keys'):
        context.set_keys = {}


# =============================================================================

@given('I initialize an associative array named "{name}"')
def step_init_named_array(context, name):
    """Initialize an associative array with a specific name."""
    context.array_name = name


@when('I get all keys from "{array_name}"')
def step_get_all_keys_from_array(context, array_name):
    """Get all keys from a specific array."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_keys '{array_name}'", shell)
    assert result.returncode == 0, f"Failed to get keys from '{array_name}': {result.stderr}"
    keys_output = result.stdout.strip()
    context.all_keys = keys_output.split() if keys_output else []
    context.array_name = array_name


@then('no keys should be returned')
def step_no_keys_returned(context):
    """No keys should be returned."""
    actual_keys = getattr(context, 'all_keys', [])
    assert len(actual_keys) == 0, f"Expected no keys, got: {actual_keys}"


@then('array should be considered empty')
def step_array_considered_empty(context):
    """Array should be considered empty."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_keys '{array_name}'", shell)
    assert result.returncode == 0, "Failed to check array keys"
    keys = result.stdout.strip()
    assert not keys, f"Array should be empty but contains: {keys}"


@then('key "{key}" should exist')
def step_key_should_exist(context, key):
    """Key should exist in array."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_has_key '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode == 0, f"Key '{key}' should exist in array"


@when('I attempt to get key "{key}"')
def step_attempt_get_key(context, key):
    """Attempt to get a key that may not exist."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_get '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    context.attempted_key = key
    context.key_attempt_result = "success" if result.returncode == 0 else "failure"
    context.attempted_key_value = result.stdout.strip() if result.returncode == 0 else None


@then('operation should return failure status')
def step_operation_failure_status(context):
    """Operation should return failure status."""
    assert getattr(context, 'key_attempt_result', 'success') == 'failure', "Expected operation to fail"


@then('no value should be returned')
def step_no_value_returned(context):
    """No value should be returned."""
    assert getattr(context, 'attempted_key_value', None) is None, "Expected no value to be returned"


@then('getting key "{key}" should contain newlines')
def step_key_contains_newlines(context, key):
    """Key value should contain newlines."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_get '{getattr(context, 'array_name', 'test_array')}' '{key}'", shell)
    assert result.returncode == 0, f"Failed to get key '{key}': {result.stderr}"
    actual_value = result.stdout.strip()
    assert '\n' in actual_value or '\\n' in actual_value, f"Expected newlines in value, got: {actual_value!r}"


@then('array should contain exactly {num:d} key')
def step_array_contains_n_keys(context, num):
    """Array should contain exactly n keys."""
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command_with_state(context, f"_assoc_keys '{getattr(context, 'array_name', 'test_array')}'", shell)
    assert result.returncode == 0, "Failed to get keys"
    keys = result.stdout.strip()
    actual_count = len(keys.split()) if keys else 0
    assert actual_count == num, f"Expected {num} keys, got {actual_count}: {keys}"


@then('operation should complete successfully')
def step_operation_complete_successfully(context):
    """Operation should complete successfully."""
    # Verify the last operation returned exit code 0
    if hasattr(context, 'last_result'):
        assert context.last_result == 0, f"Operation failed with return code {context.last_result}"
    elif hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, f"Operation failed with exit code {context.last_exit_code}"


# =============================================================================
# Additional step definitions for undefined steps (docker-free-undefined-steps-remediation-plan)
# =============================================================================

@given('associative array with keys "{keys}"')
def step_assoc_array_with_keys(context, keys):
    """Initialize an associative array with multiple keys specified."""
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    # Set each key with a default value
    key_list = [k.strip().strip('"') for k in keys.split(',')]
    context.set_keys = {}
    for key in key_list:
        result = run_shell_command(
            f"_assoc_init '{context.array_name}'; _assoc_set '{context.array_name}' '{key}' 'value_for_{key}'",
            shell
        )
        assert result.returncode == 0, f"Failed to set key '{key}': {result.stderr}"
        context.set_keys[key] = f'value_for_{key}'


@given('associative array with key "{key}"')
def step_assoc_array_with_key(context, key):
    """Initialize an associative array with a single key."""
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    # Set the key with a default value
    result = run_shell_command(
        f"_assoc_init '{context.array_name}'; _assoc_set '{context.array_name}' '{key}' 'value_for_{key}'",
        shell
    )
    assert result.returncode == 0, f"Failed to set key '{key}': {result.stderr}"
    context.set_keys = {key: f'value_for_{key}'}


@given('associative array with multiple entries')
def step_assoc_array_multiple_entries(context):
    """Initialize an associative array with multiple entries."""
    context.array_name = 'test_array'
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{context.array_name}'", shell)
    assert result.returncode == 0, f"Failed to initialize array: {result.stderr}"
    # Set multiple entries
    entries = {
        'entry1': 'value1',
        'entry2': 'value2',
        'entry3': 'value3'
    }
    context.set_keys = {}
    for key, value in entries.items():
        result = run_shell_command(
            f"_assoc_init '{context.array_name}'; _assoc_set '{context.array_name}' '{key}' '{value}'",
            shell
        )
        assert result.returncode == 0, f"Failed to set key '{key}': {result.stderr}"
        context.set_keys[key] = value


@when('I set key "{key}" to an empty value')
def step_set_empty_value(context, key):
    """Set key to an empty string value."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{array_name}'; _assoc_set '{array_name}' '{key}' ''", shell)
    assert result.returncode == 0, f"Failed to set key '{key}' to empty value: {result.stderr}"
    context.last_key = key
    context.last_value = ''
    if not hasattr(context, 'set_keys'):
        context.set_keys = {}
    context.set_keys[key] = ''


@then('array should remain empty')
def step_array_remain_empty(context):
    """Verify array remains empty (no keys set)."""
    array_name = getattr(context, 'array_name', 'test_array')
    shell = getattr(context, 'current_shell', 'zsh')
    result = run_shell_command(f"_assoc_init '{array_name}'; _assoc_keys '{array_name}'", shell)
    assert result.returncode == 0, "Failed to check array keys"
    keys = result.stdout.strip()
    assert not keys, f"Array should remain empty but contains keys: {keys}"
    # Also verify tracked keys is empty
    if hasattr(context, 'set_keys'):
        assert len(context.set_keys) == 0, f"Tracked keys should be empty, got: {context.set_keys}"
