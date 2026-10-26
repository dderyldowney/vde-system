#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
#
# Regression tests — vde_projects_dir() .env fallback (Signet #543)
# =============================================================================
# WHY THIS FILE EXISTS (the code-review's root-cause bug):
#
#   VDE_PROJECTS_DIR is persisted as an absolute path in ${VDE_ROOT_DIR}/.env,
#   but the vde CLI runs in a FRESH shell that never sources .env. The original
#   vde_projects_dir() read only the shell/env var, so bin/vde, lib/vm-common and
#   bin/vde-set-projects-dir resolved the DEFAULT base while Docker mounted the
#   CONFIGURED base from .env -- a split that left a root-owned workspace. The fix
#   added the .env fallback at lib/vde-path-utils (env var -> .env key -> default).
#
#   The pre-existing vde_projects_dir tests in vde-path-utils.test.zsh all SET the
#   shell var, so they exercised precedence rung #1 only and could never catch
#   this regression. These tests drive the resolver the way the CLI really hits
#   it: the var is UNSET, the truth lives in .env ONLY, and resolution runs in a
#   fresh `zsh` subshell with VDE_ROOT_DIR pointed at a throwaway sandbox.
#
#   SELF-RESTORING: every sandbox is created under mktemp and torn down on exit.
#   The repo's own .env is never read, created, or modified by this suite.
# =============================================================================

# Determine VDE root (where the real lib lives).
if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
typeset -r REPO_ROOT="${VDE_ROOT_DIR}"

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

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

assert_eq() {
    # assert_eq <label> <expected> <actual>
    local label="$1" expected="$2" actual="$3"
    if [[ "${actual}" == "${expected}" ]]; then
        test_pass "${label}"
    else
        test_fail "${label}" "expected '${expected}', got '${actual}'"
    fi
}

# =============================================================================
# SANDBOX LIFECYCLE
# =============================================================================
typeset SANDBOX_ROOT
SANDBOX_ROOT="$(mktemp -d /tmp/vde-env-fallback.XXXXXX)"

cleanup() {
    # Explicit, pattern-guarded teardown (never a bare variable rm -rf).
    if [[ -n "${SANDBOX_ROOT}" && -d "${SANDBOX_ROOT}" \
          && "${SANDBOX_ROOT}" == /tmp/vde-env-fallback.* ]]; then
        rm -rf -- "${SANDBOX_ROOT}"
    fi
}
trap cleanup EXIT INT TERM

# Make a fresh sandbox VDE_ROOT_DIR; echoes its path.
new_sandbox() {
    local d
    d="$(mktemp -d "${SANDBOX_ROOT}/root.XXXXXX")"
    echo "${d}"
}

# =============================================================================
# RESOLVER DRIVER
# Runs vde_projects_dir() in a FRESH zsh, exactly as the CLI would:
#   $1 = sandbox VDE_ROOT_DIR (where this child looks for .env)
#   $2 = var mode: "unset"            -> VDE_PROJECTS_DIR guaranteed absent
#                  "export:<value>"   -> VDE_PROJECTS_DIR exported to the child
# The child sources ONLY the real lib and prints the resolved base.
# =============================================================================
resolve_fresh() {
    local sandbox="$1" mode="$2"
    if [[ "${mode}" == export:* ]]; then
        local val="${mode#export:}"
        VDE_ROOT_DIR="${sandbox}" VDE_PROJECTS_DIR="${val}" \
            zsh -c 'source "$1/lib/vde-path-utils"; vde_projects_dir' _ "${REPO_ROOT}"
    else
        # Kill any ambient VDE_PROJECTS_DIR the parent shell may export, so the
        # child truly resolves with the var absent -- the real CLI condition.
        VDE_ROOT_DIR="${sandbox}" \
            zsh -c 'unset VDE_PROJECTS_DIR; source "$1/lib/vde-path-utils"; vde_projects_dir' \
            _ "${REPO_ROOT}"
    fi
}

# =============================================================================
# TESTS
# =============================================================================

# CORE REGRESSION: var unset, base persisted in .env ONLY => .env value wins.
# This is the exact scenario the old code got wrong (it returned the default).
test_env_fallback_core() {
    test_start "vde_projects_dir reads .env when the var is unset (CORE regression)"
    local root; root="$(new_sandbox)"
    printf 'VDE_PROJECTS_DIR=%s\n' "/home/student/GitHub" > "${root}/.env"
    assert_eq "env-only base resolves (not the default)" \
        "/home/student/GitHub" "$(resolve_fresh "${root}" unset)"
}

# PRECEDENCE: an exported var must still beat the .env key (rung #1 > rung #2),
# proving the fix did not over-correct into always reading .env.
test_env_var_beats_env_file() {
    test_start "exported VDE_PROJECTS_DIR overrides the .env key"
    local root; root="$(new_sandbox)"
    printf 'VDE_PROJECTS_DIR=%s\n' "/from/env/file" > "${root}/.env"
    assert_eq "env var wins over .env" \
        "/the/exported/one" "$(resolve_fresh "${root}" "export:/the/exported/one")"
}

# BOTTOM OF CHAIN: no .env and var unset => in-tree default ${VDE_ROOT_DIR}/projects.
test_default_when_no_env_file() {
    test_start "default base when no .env and var unset"
    local root; root="$(new_sandbox)"   # deliberately no .env written
    assert_eq "falls to <root>/projects" \
        "${root}/projects" "$(resolve_fresh "${root}" unset)"
}

# EMPTY VALUE: `VDE_PROJECTS_DIR=` in .env is not a real override => fall through
# to the default (helper's `[[ -n $val ]]` guard).
test_empty_env_value_falls_through() {
    test_start "empty .env value falls through to default"
    local root; root="$(new_sandbox)"
    printf 'VDE_PROJECTS_DIR=\n' > "${root}/.env"
    assert_eq "empty value does not win" \
        "${root}/projects" "$(resolve_fresh "${root}" unset)"
}

# CRLF TOLERANCE: a .env edited on Windows carries a trailing \r; the resolver
# strips it so the mounted path is not "<base>\r".
test_crlf_value_is_stripped() {
    test_start ".env value with CRLF line ending is trimmed"
    local root; root="$(new_sandbox)"
    printf 'VDE_PROJECTS_DIR=%s\r\n' "/home/student/Projects" > "${root}/.env"
    assert_eq "trailing CR stripped" \
        "/home/student/Projects" "$(resolve_fresh "${root}" unset)"
}

# LAST ASSIGNMENT WINS: a .env with two VDE_PROJECTS_DIR lines resolves to the
# last (matches shell .env semantics / the helper's `tail -1`).
test_last_assignment_wins() {
    test_start "last VDE_PROJECTS_DIR assignment in .env wins"
    local root; root="$(new_sandbox)"
    printf 'VDE_PROJECTS_DIR=%s\nVDE_PROJECTS_DIR=%s\n' "/old/base" "/new/base" \
        > "${root}/.env"
    assert_eq "tail -1 assignment used" \
        "/new/base" "$(resolve_fresh "${root}" unset)"
}

# =============================================================================
# RUN
# =============================================================================
echo "=============================================="
echo "VDE projects-dir .env Fallback Regression Tests (#543)"
echo "=============================================="

test_env_fallback_core
test_env_var_beats_env_file
test_default_when_no_env_file
test_empty_env_value_falls_through
test_crlf_value_is_stripped
test_last_assignment_wins

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
