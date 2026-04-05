#!/usr/bin/env zsh
# Unit Tests for VDE Schema Update Mechanisms
# Tests schema version detection, compatibility checking, and update workflows

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/lib/vde-shell-compat"
source "$PROJECT_ROOT/lib/vde-constants"
source "$PROJECT_ROOT/lib/vde-core"

# Test configuration
VERBOSE=${VERBOSE:-false}
TESTS_PASSED=0
TESTS_FAILED=0
TEST_TMP_DIR=""

# Test helpers
test_setup() {
    TEST_TMP_DIR=$(mktemp -d)
    [[ "$VERBOSE" == "true" ]] && echo "Test temp dir: $TEST_TMP_DIR"
}

test_teardown() {
    if [[ -n "$TEST_TMP_DIR" && -d "$TEST_TMP_DIR" ]]; then
        rm -rf "$TEST_TMP_DIR"
    fi
}

test_assert() {
    local condition="$1"
    local message="${2:-Assertion failed}"

    if eval "$condition"; then
        ((TESTS_PASSED++))
        [[ "$VERBOSE" == "true" ]] && echo "  ✓ $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo "  ✗ $message"
        return 1
    fi
}

run_test() {
    local test_name="$1"
    echo "  Running: $test_name"
    $test_name || true
}

# =============================================================================
# Version Detection Tests
# =============================================================================

test_get_config_version_valid() {
    local config_file="$PROJECT_ROOT/data/vm-types.json"
    local version
    version=$(vde_get_config_version "$config_file" 2>/dev/null)

    test_assert "[ -n '$version' ]" "Config version detected"
    test_assert "[ '$version' = '1.1' ]" "Config version is 1.1"
}

test_get_config_version_missing_file() {
    local config_file="$TEST_TMP_DIR/missing.json"

    vde_get_config_version "$config_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_ERR_NOT_FOUND ]" "Missing file returns NOT_FOUND"
}

test_get_config_version_no_version_field() {
    local config_file="$TEST_TMP_DIR/no-version.json"
    echo '{"data": "test"}' > "$config_file"

    vde_get_config_version "$config_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_ERR_NOT_FOUND ]" "No version field returns NOT_FOUND"
}

test_get_schema_version_valid() {
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"
    local version
    version=$(vde_get_schema_version "$schema_file" 2>/dev/null)

    test_assert "[ -n '$version' ]" "Schema version pattern detected"
}

test_get_schema_version_missing_file() {
    local schema_file="$TEST_TMP_DIR/missing.schema.json"

    vde_get_schema_version "$schema_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_ERR_NOT_FOUND ]" "Missing schema returns NOT_FOUND"
}

# =============================================================================
# Schema Compatibility Tests
# =============================================================================

test_check_compatibility_valid() {
    local config_file="$PROJECT_ROOT/data/vm-types.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"

    vde_check_schema_compatibility "$config_file" "$schema_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_SUCCESS ]" "Compatible config and schema"
}

test_check_compatibility_version_mismatch() {
    local config_file="$TEST_TMP_DIR/wrong-version.json"
    local schema_file="$TEST_TMP_DIR/strict-schema.schema.json"

    # Create config with version 2.0
    cat > "$config_file" <<'EOF'
{
  "version": "2.0",
  "data": {}
}
EOF

    # Create schema requiring version 1.0
    cat > "$schema_file" <<'EOF'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^1\\.0$"
    }
  }
}
EOF

    vde_check_schema_compatibility "$config_file" "$schema_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_ERR_INVALID_DATA ]" "Version mismatch detected"
}

# =============================================================================
# Schema Change Detection Tests
# =============================================================================

test_detect_schema_changes_no_change() {
    local config_file="$TEST_TMP_DIR/config.json"
    local schema_file="$TEST_TMP_DIR/config.schema.json"

    # Create config
    echo '{"version": "1.0"}' > "$config_file"
    # Wait for mtime to change (high-precision)
    zmodload zsh/zselect 2>/dev/null && zselect -t 110
    # Create schema (newer than config)
    echo '{"type": "object"}' > "$schema_file"

    vde_detect_schema_changes "$config_file" >/dev/null 2>&1
    local result=$?

    # Schema newer than config means change detected
    test_assert "[ $result -eq $VDE_ERR_CACHE_INVALID ]" "Schema change detected when schema is newer"
}

test_detect_schema_changes_config_newer() {
    local config_file="$TEST_TMP_DIR/config2.json"
    local schema_file="$TEST_TMP_DIR/config2.schema.json"

    # Create schema first
    echo '{"type": "object"}' > "$schema_file"
    # Wait for mtime to change (high-precision)
    zmodload zsh/zselect 2>/dev/null && zselect -t 110
    # Create config (newer)
    echo '{"version": "1.0"}' > "$config_file"

    vde_detect_schema_changes "$config_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_SUCCESS ]" "No change when config is newer"
}

# =============================================================================
# Config Backup Tests
# =============================================================================

test_backup_config_creates_backup() {
    local config_file="$TEST_TMP_DIR/test-config.json"
    echo '{"version": "1.0"}' > "$config_file"

    local backup_file
    backup_file=$(vde_backup_config "$config_file" 2>/dev/null)

    test_assert "[ -f '$backup_file' ]" "Backup file created"
    test_assert "[ -n '$backup_file' ]" "Backup path returned"
}

test_backup_config_missing_file() {
    local config_file="$TEST_TMP_DIR/missing.json"

    vde_backup_config "$config_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_ERR_NOT_FOUND ]" "Missing file returns NOT_FOUND"
}

test_backup_config_preserves_content() {
    local config_file="$TEST_TMP_DIR/content-config.json"
    local test_content='{"version": "1.0", "data": "test"}'
    echo "$test_content" > "$config_file"

    local backup_file
    backup_file=$(vde_backup_config "$config_file" 2>/dev/null)

    local backup_content
    backup_content=$(cat "$backup_file")

    test_assert "[ '$backup_content' = '$test_content' ]" "Backup preserves content"
}

# =============================================================================
# Validate and Update Tests
# =============================================================================

test_validate_and_update_valid_config() {
    local config_file="$PROJECT_ROOT/data/vm-types.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"
    local cache_file="$TEST_TMP_DIR/test.cache"

    vde_validate_and_update "$config_file" "$schema_file" "$cache_file" >/dev/null 2>&1
    local result=$?

    # Should return CACHE_INVALID since cache doesn't exist
    test_assert "[ $result -eq $VDE_ERR_CACHE_INVALID ]" "Returns CACHE_INVALID when cache missing"
}

test_validate_and_update_with_valid_cache() {
    local config_file="$TEST_TMP_DIR/config-with-cache.json"
    local schema_file="$TEST_TMP_DIR/config-with-cache.schema.json"
    local cache_file="$TEST_TMP_DIR/config.cache"

    # Create valid config
    cat > "$config_file" <<'EOF'
{
  "version": "1.0",
  "vms": {
    "language": [],
    "service": []
  }
}
EOF

    # Create schema
    cat > "$schema_file" <<'EOF'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "vms"],
  "properties": {
    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+$"},
    "vms": {"type": "object"}
  }
}
EOF

    # Create cache (newer than config and schema)
    # Wait for mtime to change (high-precision)
    zmodload zsh/zselect 2>/dev/null && zselect -t 110
    echo "# cache" > "$cache_file"

    vde_validate_and_update "$config_file" "$schema_file" "$cache_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_SUCCESS ]" "Returns SUCCESS with valid cache"
}

# =============================================================================
# Integration Tests
# =============================================================================

test_full_update_workflow() {
    local config_file="$TEST_TMP_DIR/workflow-config.json"
    local schema_file="$TEST_TMP_DIR/workflow-config.schema.json"

    # Create config
    cat > "$config_file" <<'EOF'
{
  "version": "1.0",
  "data": "test"
}
EOF

    # Create schema
    cat > "$schema_file" <<'EOF'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string", "pattern": "^1\\.0$"}
  }
}
EOF

    # Step 1: Get version
    local version
    version=$(vde_get_config_version "$config_file" 2>/dev/null)
    test_assert "[ '$version' = '1.0' ]" "Workflow: Version detected"

    # Step 2: Check compatibility
    vde_check_schema_compatibility "$config_file" "$schema_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_SUCCESS ]" "Workflow: Compatibility check passed"

    # Step 3: Backup
    local backup
    backup=$(vde_backup_config "$config_file" 2>/dev/null)
    test_assert "[ -f '$backup' ]" "Workflow: Backup created"

    # Step 4: Validate
    vde_validate_json_schema "$config_file" "$schema_file" >/dev/null 2>&1
    test_assert "[ $? -eq $VDE_SUCCESS ]" "Workflow: Validation passed"
}

# =============================================================================
# Run Test Suite
# =============================================================================

run_test_suite() {
    echo "========================================"
    echo "VDE Schema Update Mechanisms Test Suite"
    echo "========================================"
    echo ""

    test_setup

    echo "Version Detection Tests:"
    run_test test_get_config_version_valid
    run_test test_get_config_version_missing_file
    run_test test_get_config_version_no_version_field
    run_test test_get_schema_version_valid
    run_test test_get_schema_version_missing_file

    echo ""
    echo "Schema Compatibility Tests:"
    run_test test_check_compatibility_valid
    run_test test_check_compatibility_version_mismatch

    echo ""
    echo "Schema Change Detection Tests:"
    run_test test_detect_schema_changes_no_change
    run_test test_detect_schema_changes_config_newer

    echo ""
    echo "Config Backup Tests:"
    run_test test_backup_config_creates_backup
    run_test test_backup_config_missing_file
    run_test test_backup_config_preserves_content

    echo ""
    echo "Validate and Update Tests:"
    run_test test_validate_and_update_valid_config
    run_test test_validate_and_update_with_valid_cache

    echo ""
    echo "Integration Tests:"
    run_test test_full_update_workflow

    test_teardown

    echo ""
    echo "========================================"
    echo "Test Results"
    echo "========================================"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        echo "✓ All tests passed!"
        return 0
    else
        echo ""
        echo "✗ Some tests failed"
        return 1
    fi
}

# Run the test suite
run_test_suite
