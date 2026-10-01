#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for VDE Schema Validation Functions
# Tests centralized JSON schema validation in vde-core

typeset SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
typeset PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/lib/vde-shell-compat"
source "$PROJECT_ROOT/lib/vde-constants"
source "$PROJECT_ROOT/lib/vde-core"

# Test configuration
typeset VERBOSE=${VERBOSE:-false}
typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset TESTS_SKIPPED=0
typeset TEST_TMP_DIR=""

# Test helpers
test_setup() {
    # Create temporary test directory
    TEST_TMP_DIR=$(mktemp -d)
    [[ "$VERBOSE" == "true" ]] && echo "Test temp dir: $TEST_TMP_DIR"

    # Create atomic copies of production data and schema for real-time check
    cp "$PROJECT_ROOT/data/vm-types.json" "$TEST_TMP_DIR/vm-types.json"
    cp "$PROJECT_ROOT/data/vm-types.schema.json" "$TEST_TMP_DIR/vm-types.schema.json"
}

test_teardown() {
    # Clean up temporary test directory
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
# Schema Integrity Tests
# =============================================================================

test_check_schema_integrity_valid() {
    local schema_file="$TEST_TMP_DIR/vm-types.schema.json"

    vde_check_schema_integrity "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "Valid schema passes integrity check"
}

test_check_schema_integrity_missing() {
    local schema_file="$TEST_TMP_DIR/missing.schema.json"

    vde_check_schema_integrity "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_NOT_FOUND ]]" "Missing schema returns NOT_FOUND"
}

test_check_schema_integrity_invalid_json() {
    local schema_file="$TEST_TMP_DIR/invalid.schema.json"
    echo "{ invalid json" > "$schema_file"

    vde_check_schema_integrity "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "Invalid JSON returns INVALID_DATA"
}

test_check_schema_integrity_missing_fields() {
    local schema_file="$TEST_TMP_DIR/incomplete.schema.json"
    echo '{"title": "Test"}' > "$schema_file"

    vde_check_schema_integrity "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "Schema without required fields returns INVALID_DATA"
}

# =============================================================================
# JSON Schema Validation Tests
# =============================================================================

test_validate_json_schema_valid() {
    local json_file="$TEST_TMP_DIR/vm-types.json"
    local schema_file="$TEST_TMP_DIR/vm-types.schema.json"

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "Real vm-types.json passes schema validation"
}

test_validate_json_schema_missing_json() {
    local json_file="$TEST_TMP_DIR/missing.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_NOT_FOUND ]]" "Missing JSON returns NOT_FOUND"
}

test_validate_json_schema_missing_schema() {
    local json_file="$PROJECT_ROOT/data/vm-types.json"
    local schema_file="$TEST_TMP_DIR/missing.schema.json"

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_NOT_FOUND ]]" "Missing schema returns NOT_FOUND"
}

test_validate_json_schema_invalid_data() {
    local json_file="$TEST_TMP_DIR/invalid-vm-types.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"

    # Create JSON missing required fields and with invalid name
    cat > "$json_file" <<'EOF'
{
  "version": "1.0",
  "vms": {
    "language": [
      {
        "name": "invalid-name"
      }
    ],
    "service": []
  }
}
EOF

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "Invalid data returns INVALID_DATA"
}

test_validate_json_schema_language_vm_with_port() {
    local json_file="$TEST_TMP_DIR/lang-with-port.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"

    # Create language VM with invalid ssh_port (out of range)
    cat > "$json_file" <<'EOF'
{
  "version": "1.0",
  "vms": {
    "language": [
      {
        "name": "vde-test-lang",
        "display": "Test Language",
        "ssh_port": 9999
      }
    ],
    "service": []
  }
}
EOF

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "Language VM with invalid port returns INVALID_DATA"
}

test_validate_json_schema_service_vm_without_port() {
    local json_file="$TEST_TMP_DIR/service-without-port.json"
    local schema_file="$PROJECT_ROOT/data/vm-types.schema.json"

    # Create service VM without ssh_port (invalid)
    cat > "$json_file" <<'EOF'
{
  "version": "1.0",
  "vms": {
    "language": [],
    "service": [
      {
        "name": "vde-test-service",
        "display": "Test Service"
      }
    ]
  }
}
EOF

    vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "Service VM without port returns INVALID_DATA"
}

# =============================================================================
# Built-in Validator Tests (no jsonschema required)
# =============================================================================
# Without the jsonschema module the built-in validator must be exactly as strict
# as jsonschema for the keywords the project schemas use, and must refuse (not
# ignore) keywords it does not implement.

typeset LANG_OK='{"name":"vde-test","display":"Test","ssh_port":2201}'
typeset SVC_OK='{"name":"vde-svc","display":"Svc","ssh_port":2401}'

# Fixtures: name|expected|language array|service array|extra top-level members
typeset -a VALIDATOR_FIXTURES=(
    "valid_minimal|ok|[${LANG_OK}]|[${SVC_OK}]|"
    "valid_empty_lists|ok|[]|[]|"
    "valid_null_pkgs|ok|[{\"name\":\"vde-test\",\"display\":\"T\",\"ssh_port\":2201,\"pkgs\":null}]|[]|"
    "bad_name_pattern|bad|[{\"name\":\"invalid-name\",\"display\":\"T\",\"ssh_port\":2201}]|[]|"
    "missing_required_fields|bad|[{\"name\":\"vde-a\"}]|[]|"
    "port_out_of_range|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":9999}]|[]|"
    "port_wrong_type_string|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":\"2201\"}]|[]|"
    "port_boolean_not_integer|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":true}]|[]|"
    "language_port_in_service_range|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":2401}]|[]|"
    "service_without_port|bad|[]|[{\"name\":\"vde-svc\",\"display\":\"S\"}]|"
    "display_empty|bad|[{\"name\":\"vde-a\",\"display\":\"\",\"ssh_port\":2201}]|[]|"
    "extra_vm_property|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":2201,\"bogus\":1}]|[]|"
    "extra_top_level_property|bad|[]|[]|,\"extra\":1"
    "pkgs_wrong_type|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":2201,\"pkgs\":5}]|[]|"
    "alias_wrong_item_type|bad|[{\"name\":\"vde-a\",\"display\":\"T\",\"ssh_port\":2201,\"aliases\":[1]}]|[]|"
)

_write_fixture() {
    local file="$1" language="$2" service="$3" extra="$4"
    print -r -- "{\"version\":\"1.0\"${extra},\"vms\":{\"language\":${language},\"service\":${service}}}" > "$file"
}

_validate_with() {
    local mode="$1" json_file="$2" schema_file="$3"
    ( export VDE_SCHEMA_VALIDATOR="$mode"; vde_validate_json_schema "$json_file" "$schema_file" >/dev/null 2>&1 )
}

test_builtin_validator_matches_expected_verdicts() {
    local schema_file="$TEST_TMP_DIR/vm-types.schema.json"
    local entry name expected language service extra file rc want
    for entry in "${VALIDATOR_FIXTURES[@]}"; do
        local -a parts=("${(@s:|:)entry}")
        name="${parts[1]}"; expected="${parts[2]}"; language="${parts[3]}"; service="${parts[4]}"; extra="${parts[5]}"
        file="$TEST_TMP_DIR/fixture-${name}.json"
        _write_fixture "$file" "$language" "$service" "$extra"
        _validate_with builtin "$file" "$schema_file"; rc=$?
        if [[ "$expected" == ok ]]; then want="$VDE_SUCCESS"; else want="$VDE_ERR_INVALID_DATA"; fi
        test_assert "[[ $rc -eq $want ]]" "built-in validator: ${name} -> ${expected} (rc=${rc})"
    done
}

test_builtin_validator_accepts_real_vm_types() {
    _validate_with builtin "$TEST_TMP_DIR/vm-types.json" "$TEST_TMP_DIR/vm-types.schema.json"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "built-in validator accepts the real vm-types.json"
}

test_builtin_validator_fails_closed_on_unsupported_keyword() {
    local schema_file="$TEST_TMP_DIR/allof.schema.json"
    local output rc
    python3 - "$TEST_TMP_DIR/vm-types.schema.json" "$schema_file" <<'PY'
import json, sys
schema = json.load(open(sys.argv[1]))
schema["allOf"] = []
json.dump(schema, open(sys.argv[2], "w"))
PY
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$TEST_TMP_DIR/vm-types.json" "$schema_file" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_INVALID_DATA ]]" "built-in validator rejects a schema using an unsupported keyword (allOf)"
    [[ $output == *unsupported* ]]
    test_assert "[[ $? -eq 0 ]]" "unsupported-keyword failure says so explicitly"
}

# A $ref may point into a subtree no walk of properties/items/definitions
# reaches; an unsupported keyword there must still fail closed.
test_builtin_validator_fails_closed_on_keyword_behind_ref() {
    local schema_file="$TEST_TMP_DIR/ref-bypass.schema.json"
    local json_file="$TEST_TMP_DIR/ref-bypass.json"
    local output rc
    # "default" is an annotation key, so nothing walks it, but a $ref can point into it.
    print -r -- '{"type":"object","properties":{"port":{"$ref":"#/default/port"}},"default":{"port":{"type":"integer","enum":[2201]}}}' > "$schema_file"
    print -r -- '{"port": 9999}' > "$json_file"
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$json_file" "$schema_file" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_INVALID_DATA ]]" "built-in validator rejects an unsupported keyword reached only through a \$ref"
    [[ $output == *unsupported* ]]
    test_assert "[[ $? -eq 0 ]]" "the \$ref-reached keyword failure says unsupported"
}

# jsonschema picks its semantics from "$schema"; the built-in implements one
# fixed draft, so any other declared draft must be refused, not approximated.
test_builtin_validator_fails_closed_on_other_draft() {
    local schema_file="$TEST_TMP_DIR/draft07.schema.json"
    local json_file="$TEST_TMP_DIR/draft07.json"
    local output rc
    print -r -- '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object"}' > "$schema_file"
    print -r -- '{}' > "$json_file"
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$json_file" "$schema_file" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_INVALID_DATA ]]" "built-in validator rejects a schema declaring a draft it does not implement"
    [[ $output == *unsupported* ]]
    test_assert "[[ $? -eq 0 ]]" "the draft refusal says unsupported"
}

# "$schema" URLs are often written with a trailing "#"; that is the same draft.
test_builtin_validator_accepts_schema_url_with_trailing_hash() {
    local schema_file="$TEST_TMP_DIR/hash.schema.json"
    local json_file="$TEST_TMP_DIR/hash.json"
    print -r -- '{"$schema":"https://json-schema.org/draft/2020-12/schema#","type":"object"}' > "$schema_file"
    print -r -- '{}' > "$json_file"
    _validate_with builtin "$json_file" "$schema_file"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "built-in validator accepts a 2020-12 \$schema URL with a trailing #"
}

# A nested "$id" changes the base URI for "$ref" resolution, which the built-in
# does not model, so it must be refused rather than ignored.
test_builtin_validator_fails_closed_on_nested_id() {
    local schema_file="$TEST_TMP_DIR/nested-id.schema.json"
    local json_file="$TEST_TMP_DIR/nested-id.json"
    local output rc
    print -r -- '{"type":"object","properties":{"a":{"$id":"https://example.test/a","type":"integer"}}}' > "$schema_file"
    print -r -- '{"a": 1}' > "$json_file"
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$json_file" "$schema_file" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_INVALID_DATA ]]" "built-in validator rejects a nested \$id"
    [[ $output == *unsupported* ]]
    test_assert "[[ $? -eq 0 ]]" "the nested \$id refusal says unsupported"
}

# JSON-pointer fragments in a "$ref" are percent-decoded ("%25" is "%").
test_builtin_validator_resolves_percent_encoded_ref() {
    local schema_file="$TEST_TMP_DIR/pct.schema.json"
    local good="$TEST_TMP_DIR/pct-good.json" bad="$TEST_TMP_DIR/pct-bad.json"
    print -r -- '{"type":"object","properties":{"a":{"$ref":"#/definitions/a%25b"}},"definitions":{"a%b":{"type":"integer"}}}' > "$schema_file"
    print -r -- '{"a": 1}' > "$good"
    print -r -- '{"a": "x"}' > "$bad"
    _validate_with builtin "$good" "$schema_file"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "a percent-encoded \$ref resolves and accepts valid data"
    _validate_with builtin "$bad" "$schema_file"
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "a percent-encoded \$ref resolves and rejects invalid data"
}

# A recursive schema ("$ref": "#") with a root "$id" is valid: the root is not a
# nested $id.
test_builtin_validator_accepts_recursive_ref_with_root_id() {
    local schema_file="$TEST_TMP_DIR/recursive.schema.json"
    local good="$TEST_TMP_DIR/recursive-good.json" bad="$TEST_TMP_DIR/recursive-bad.json"
    print -r -- '{"$id":"https://example.test/tree","type":"object","properties":{"child":{"$ref":"#"},"n":{"type":"integer"}}}' > "$schema_file"
    print -r -- '{"n":1,"child":{"n":2,"child":{}}}' > "$good"
    print -r -- '{"n":1,"child":{"n":"x"}}' > "$bad"
    _validate_with builtin "$good" "$schema_file"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "a recursive \$ref to the root with a root \$id accepts valid data"
    _validate_with builtin "$bad" "$schema_file"
    test_assert "[[ $? -eq $VDE_ERR_INVALID_DATA ]]" "a recursive \$ref to the root rejects invalid nested data"
}

test_missing_validator_helper_is_reported() {
    local output rc
    output=$( ( _VDE_CORE_LIB_DIR="$TEST_TMP_DIR/no-such-dir"; vde_validate_json_schema "$TEST_TMP_DIR/vm-types.json" "$TEST_TMP_DIR/vm-types.schema.json" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_NOT_FOUND ]]" "a missing validator helper returns NOT_FOUND, not INVALID_DATA"
    [[ $output == *vde-json-validate.py* ]]
    test_assert "[[ $? -eq 0 ]]" "the missing-helper message names the helper file"
}

test_deeply_nested_json_gives_message_not_traceback() {
    local json_file="$TEST_TMP_DIR/deep.json"
    local output rc
    python3 -c "import sys; sys.stdout.write('[' * 60000 + ']' * 60000)" > "$json_file"
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$json_file" "$TEST_TMP_DIR/vm-types.schema.json" ) 2>&1 )
    rc=$?
    test_assert "[[ $rc -eq $VDE_ERR_INVALID_DATA ]]" "deeply nested JSON is rejected"
    [[ $output != *Traceback* ]]
    test_assert "[[ $? -eq 0 ]]" "deeply nested JSON gives a one-line message, not a traceback"
}

test_builtin_validator_handles_quote_in_schema_path() {
    local dir="$TEST_TMP_DIR/o'brien"
    mkdir -p "$dir"
    cp "$TEST_TMP_DIR/vm-types.schema.json" "$dir/vm-types.schema.json"
    _validate_with builtin "$TEST_TMP_DIR/vm-types.json" "$dir/vm-types.schema.json"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "a quote in the schema path does not break validation"
}

test_builtin_validator_handles_quote_in_json_path() {
    local file="$TEST_TMP_DIR/it's-valid.json"
    cp "$TEST_TMP_DIR/vm-types.json" "$file"
    _validate_with builtin "$file" "$TEST_TMP_DIR/vm-types.schema.json"
    test_assert "[[ $? -eq $VDE_SUCCESS ]]" "a quote in the JSON file name does not break validation"
}

test_validator_name_is_reported() {
    local output
    output=$( ( export VDE_SCHEMA_VALIDATOR=builtin; vde_validate_json_schema "$TEST_TMP_DIR/vm-types.json" "$TEST_TMP_DIR/vm-types.schema.json" ) 2>&1 )
    [[ $output == *"(builtin)"* ]]
    test_assert "[[ $? -eq 0 ]]" "success message names the validator used (builtin)"
}

test_builtin_matches_jsonschema_on_all_fixtures() {
    if ! python3 -c "import jsonschema" 2>/dev/null; then
        echo "  SKIP: jsonschema not installed; built-in vs jsonschema comparison not run"
        ((TESTS_SKIPPED++))
        return 0
    fi
    local schema_file="$TEST_TMP_DIR/vm-types.schema.json"
    local entry name language service extra file rc_builtin rc_js
    for entry in "${VALIDATOR_FIXTURES[@]}"; do
        local -a parts=("${(@s:|:)entry}")
        name="${parts[1]}"; language="${parts[3]}"; service="${parts[4]}"; extra="${parts[5]}"
        file="$TEST_TMP_DIR/diff-${name}.json"
        _write_fixture "$file" "$language" "$service" "$extra"
        _validate_with builtin "$file" "$schema_file"; rc_builtin=$?
        _validate_with jsonschema "$file" "$schema_file"; rc_js=$?
        test_assert "[[ $rc_builtin -eq $rc_js ]]" "built-in and jsonschema agree on ${name} (${rc_builtin} vs ${rc_js})"
    done
}

# =============================================================================
# Schema Discovery Tests
# =============================================================================

test_get_schema_for_json_found() {
    local json_file="$PROJECT_ROOT/data/vm-types.json"
    local schema_file

    schema_file=$(vde_get_schema_for_json "$json_file" 2>/dev/null)
    test_assert "[[ -f '$schema_file' ]]" "Schema file found for vm-types.json"
}

test_get_schema_for_json_not_found() {
    local json_file="$TEST_TMP_DIR/no-schema.json"
    echo '{}' > "$json_file"

    vde_get_schema_for_json "$json_file" >/dev/null 2>&1
    test_assert "[[ $? -eq $VDE_ERR_NOT_FOUND ]]" "Missing schema returns NOT_FOUND"
}

# =============================================================================
# Error Code Tests
# =============================================================================

test_error_codes_defined() {
    test_assert "[[ -n '$VDE_ERR_INVALID_DATA' ]]" "VDE_ERR_INVALID_DATA is defined"
    test_assert "[[ -n '$VDE_ERR_CACHE_INVALID' ]]" "VDE_ERR_CACHE_INVALID is defined"
    test_assert "[[ '$VDE_ERR_INVALID_DATA' -eq 10 ]]" "VDE_ERR_INVALID_DATA equals 10"
    test_assert "[[ '$VDE_ERR_CACHE_INVALID' -eq 11 ]]" "VDE_ERR_CACHE_INVALID equals 11"
}

# =============================================================================
# Integration Tests
# =============================================================================

test_vm_common_uses_validation() {
    # Test that vm-common has validation functions available
    source "$PROJECT_ROOT/lib/vm-common" >/dev/null 2>&1

    # Check that validate_vm_types_config function exists
    if typeset -f validate_vm_types_config >/dev/null 2>&1; then
        test_assert "[[ 0 -eq 0 ]]" "vm-common validation functions available"
        return 0
    else
        test_assert "[[ 1 -eq 0 ]]" "vm-common validation functions available"
        return 1
    fi
}

# =============================================================================
# Run Test Suite
# =============================================================================

run_test_suite() {
    echo "========================================"
    echo "VDE Schema Validation Test Suite"
    echo "========================================"
    echo ""

    test_setup

    echo "Schema Integrity Tests:"
    run_test test_check_schema_integrity_valid
    run_test test_check_schema_integrity_missing
    run_test test_check_schema_integrity_invalid_json
    run_test test_check_schema_integrity_missing_fields

    echo ""
    echo "JSON Schema Validation Tests:"
    run_test test_validate_json_schema_valid
    run_test test_validate_json_schema_missing_json
    run_test test_validate_json_schema_missing_schema
    run_test test_validate_json_schema_invalid_data
    run_test test_validate_json_schema_language_vm_with_port
    run_test test_validate_json_schema_service_vm_without_port

    echo ""
    echo "Built-in Validator Tests:"
    run_test test_builtin_validator_matches_expected_verdicts
    run_test test_builtin_validator_accepts_real_vm_types
    run_test test_builtin_validator_fails_closed_on_unsupported_keyword
    run_test test_builtin_validator_fails_closed_on_keyword_behind_ref
    run_test test_builtin_validator_fails_closed_on_other_draft
    run_test test_builtin_validator_accepts_schema_url_with_trailing_hash
    run_test test_builtin_validator_fails_closed_on_nested_id
    run_test test_builtin_validator_resolves_percent_encoded_ref
    run_test test_builtin_validator_accepts_recursive_ref_with_root_id
    run_test test_missing_validator_helper_is_reported
    run_test test_deeply_nested_json_gives_message_not_traceback
    run_test test_builtin_validator_handles_quote_in_schema_path
    run_test test_builtin_validator_handles_quote_in_json_path
    run_test test_validator_name_is_reported
    run_test test_builtin_matches_jsonschema_on_all_fixtures

    echo ""
    echo "Schema Discovery Tests:"
    run_test test_get_schema_for_json_found
    run_test test_get_schema_for_json_not_found

    echo ""
    echo "Error Code Tests:"
    run_test test_error_codes_defined

    echo ""
    echo "Integration Tests:"
    run_test test_vm_common_uses_validation

    test_teardown

    echo ""
    echo "========================================"
    echo "Test Results"
    echo "========================================"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo "Skipped: $TESTS_SKIPPED"

    if [[ $TESTS_FAILED -eq 0 ]]; then
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
