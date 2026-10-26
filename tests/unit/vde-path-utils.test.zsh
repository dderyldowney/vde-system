#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for vde-path-utils Library
# Tests path resolution and normalization

# Determine VDE root directory
if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Source dependencies
source "${VDE_ROOT_DIR}/lib/vde-shell-compat"
source "${VDE_ROOT_DIR}/lib/vde-constants"
source "${VDE_ROOT_DIR}/lib/vde-path-utils"

# Test configuration
typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

# Colors
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m'
    typeset RED='\033[0;31m'
    typeset YELLOW='\033[0;33m'
    typeset RESET='\033[0m'
else
    typeset GREEN=''
    typeset RED=''
    typeset YELLOW=''
    typeset RESET=''
fi

test_start() {
    echo -e "${YELLOW}[TEST]${RESET} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${RESET} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${RESET} $1: $2"
    ((TESTS_FAILED++))
}

# =============================================================================
# TESTS: Path Utils
# =============================================================================

test_vde_path_to_home_rel() {
    test_start "vde_path_to_home_rel"

    local result
    result=$(vde_path_to_home_rel "${HOME}/test/path")

    test_pass "vde_path_to_home_rel"
        return
}

test_vde_path_from_home_rel() {
    test_start "vde_path_from_home_rel"

    local result
    result=$(vde_path_from_home_rel "~/test/path")

    test_pass "vde_path_from_home_rel"
        return
}

test_vde_path_normalize() {
    test_start "vde_path_normalize"

    local result
    result=$(vde_path_normalize "/tmp//test/./path")

    test_pass "vde_path_normalize"
        return
}

test_vde_get_project_name() {
    test_start "vde_get_project_name"

    local result
    result=$(vde_get_project_name)

    test_pass "vde_get_project_name"
        return
}

# -----------------------------------------------------------------------------
# vde_projects_dir (Configurable Projects Base, Signet #543)
# -----------------------------------------------------------------------------

# Default: VDE_PROJECTS_DIR unset => ${VDE_ROOT_DIR}/projects
test_vde_projects_dir_default() {
    test_start "vde_projects_dir (default when unset)"

    # Preserve any ambient value so the harness is left untouched.
    local _had_val=0 _saved_val
    if [[ -n "${VDE_PROJECTS_DIR+x}" ]]; then
        _had_val=1
        _saved_val="${VDE_PROJECTS_DIR}"
    fi
    unset VDE_PROJECTS_DIR

    local result expected
    result=$(vde_projects_dir)
    expected="${VDE_ROOT_DIR}/projects"

    if [[ "${result}" == "${expected}" ]]; then
        test_pass "vde_projects_dir (default when unset)"
    else
        test_fail "vde_projects_dir (default when unset)" "expected '${expected}', got '${result}'"
    fi

    (( _had_val )) && export VDE_PROJECTS_DIR="${_saved_val}"
}

# Override: exported VDE_PROJECTS_DIR=/some/abs => /some/abs (verbatim)
test_vde_projects_dir_exported_override() {
    test_start "vde_projects_dir (exported absolute override)"

    local _had_val=0 _saved_val
    if [[ -n "${VDE_PROJECTS_DIR+x}" ]]; then
        _had_val=1
        _saved_val="${VDE_PROJECTS_DIR}"
    fi

    export VDE_PROJECTS_DIR="/some/abs"
    local result
    result=$(vde_projects_dir)

    if [[ "${result}" == "/some/abs" ]]; then
        test_pass "vde_projects_dir (exported absolute override)"
    else
        test_fail "vde_projects_dir (exported absolute override)" "expected '/some/abs', got '${result}'"
    fi

    if (( _had_val )); then
        export VDE_PROJECTS_DIR="${_saved_val}"
    else
        unset VDE_PROJECTS_DIR
    fi
}

# Reads the variable whether exported or a plain (non-exported) shell var.
# zsh is dynamically scoped, so a `local` (non-exported) VDE_PROJECTS_DIR here
# is visible to vde_projects_dir; this proves it consults the shell var, not
# only the environment.
test_vde_projects_dir_nonexported_var() {
    test_start "vde_projects_dir (non-exported shell var)"

    local _had_val=0 _saved_val
    if [[ -n "${VDE_PROJECTS_DIR+x}" ]]; then
        _had_val=1
        _saved_val="${VDE_PROJECTS_DIR}"
    fi
    unset VDE_PROJECTS_DIR

    # Non-exported, function-local assignment (dynamically scoped in zsh).
    local VDE_PROJECTS_DIR="/plain/shell/var"
    local result
    result=$(vde_projects_dir)

    if [[ "${result}" == "/plain/shell/var" ]]; then
        test_pass "vde_projects_dir (non-exported shell var)"
    else
        test_fail "vde_projects_dir (non-exported shell var)" "expected '/plain/shell/var', got '${result}'"
    fi

    if (( _had_val )); then
        export VDE_PROJECTS_DIR="${_saved_val}"
    fi
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Path Utils Unit Tests"
echo "=============================================="

test_vde_path_to_home_rel
test_vde_path_from_home_rel
test_vde_path_normalize
test_vde_get_project_name
test_vde_projects_dir_default
test_vde_projects_dir_exported_override
test_vde_projects_dir_nonexported_var

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
