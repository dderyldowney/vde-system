#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for `vde init` Projects-base PRECEDENCE (Signet #543 follow-up).
#
# `vde init --projects-dir <path>` must resolve the base in this order:
#   1. --projects-dir flag    (PROJECTS_DIR_FLAG)   -- highest
#   2. exported VDE_PROJECTS_DIR
#   3. VDE_PROJECTS_DIR already recorded in .env
# ... and persist the resolved ABSOLUTE base to .env.
#
# Running real `vde init` is unsafe here (it also runs ssh-setup, builds the
# base image, installs git hooks and registers clusters -- side effects that
# cannot be byte-restored). So the self-contained resolver function
# vde_init_resolve_projects_dir is EXTRACTED verbatim from bin/vde-init at
# runtime and eval'd in this harness. Extracting the live definition keeps the
# test in sync with the real implementation while touching only temp dirs.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset INIT_SRC="${VDE_ROOT_DIR}/bin/vde-init"

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

# Stub the one logging helper the resolver may call.
vde_log_warn() { : ; }

# Extract and load the real resolver from bin/vde-init.
typeset _fn_text
_fn_text="$(awk '/^vde_init_resolve_projects_dir\(\) \{/,/^\}/' "${INIT_SRC}")"
if [[ -z "${_fn_text}" ]]; then
    echo "FATAL: could not extract vde_init_resolve_projects_dir from ${INIT_SRC}"
    exit 1
fi
source "${VDE_ROOT_DIR}/lib/vde-path-utils" &>/dev/null   # resolver dependency (#564)
eval "${_fn_text}"

# Harness scratch area (all temp; removed at the end).
typeset HARNESS_TMP
HARNESS_TMP="$(mktemp -d "${TMPDIR:-/tmp}/vde-init-resolver.XXXXXX")"

# _reset_env_root <dotenv-value-or-empty>
# Build a fresh fake VDE_ROOT with an .env that optionally carries a key.
_reset_env_root() {
    local dotenv_val="${1}"
    local root="${HARNESS_TMP}/root.$$.${RANDOM}"
    mkdir -p "${root}"
    if [[ -n "${dotenv_val}" ]]; then
        print -r -- "VDE_PROJECTS_DIR=${dotenv_val}" > "${root}/.env"
    else
        : > "${root}/.env"
    fi
    print -r -- "${root}"
}

# _read_env_key <root>
_read_env_key() {
    grep -E '^VDE_PROJECTS_DIR=' "${1}/.env" 2>/dev/null | tail -1 | sed 's/^VDE_PROJECTS_DIR=//'
}

# =============================================================================
# TEST 1: --projects-dir flag beats exported env AND .env
# =============================================================================
test_flag_wins() {
    test_start "resolver: --projects-dir flag beats exported env and .env"

    local flag_base="${HARNESS_TMP}/flag_base"
    local env_base="${HARNESS_TMP}/env_base"
    local dotenv_base="${HARNESS_TMP}/dotenv_base"
    local root; root="$(_reset_env_root "${dotenv_base}")"

    typeset QUIET=1
    typeset PROJECTS_DIR_FLAG="${flag_base}"
    typeset VDE_ROOT_DIR="${root}"
    export VDE_PROJECTS_DIR="${env_base}"
    typeset VDE_PROJECTS_BASE=""

    vde_init_resolve_projects_dir >/dev/null 2>&1

    local expected="${flag_base:A}"
    local persisted; persisted="$(_read_env_key "${root}")"

    if [[ "${VDE_PROJECTS_BASE}" == "${expected}" && "${persisted}" == "${expected}" ]]; then
        test_pass "flag precedence"
    else
        test_fail "flag precedence" "base='${VDE_PROJECTS_BASE}' persisted='${persisted}' expected='${expected}'"
    fi
    unset VDE_PROJECTS_DIR
}

# =============================================================================
# TEST 2: exported VDE_PROJECTS_DIR beats .env (no flag)
# =============================================================================
test_env_beats_dotenv() {
    test_start "resolver: exported VDE_PROJECTS_DIR beats .env"

    local env_base="${HARNESS_TMP}/env_base2"
    local dotenv_base="${HARNESS_TMP}/dotenv_base2"
    local root; root="$(_reset_env_root "${dotenv_base}")"

    typeset QUIET=1
    typeset PROJECTS_DIR_FLAG=""
    typeset VDE_ROOT_DIR="${root}"
    export VDE_PROJECTS_DIR="${env_base}"
    typeset VDE_PROJECTS_BASE=""

    vde_init_resolve_projects_dir >/dev/null 2>&1

    local expected="${env_base:A}"
    if [[ "${VDE_PROJECTS_BASE}" == "${expected}" ]]; then
        test_pass "env over .env precedence"
    else
        test_fail "env over .env precedence" "base='${VDE_PROJECTS_BASE}' expected='${expected}'"
    fi
    unset VDE_PROJECTS_DIR
}

# =============================================================================
# TEST 3: .env value honored when no flag and no exported env
# =============================================================================
test_dotenv_honored() {
    test_start "resolver: recorded .env value honored when flag/env absent"

    local dotenv_base="${HARNESS_TMP}/dotenv_base3"
    mkdir -p "${dotenv_base}"
    local root; root="$(_reset_env_root "${dotenv_base}")"

    typeset QUIET=1
    typeset PROJECTS_DIR_FLAG=""
    typeset VDE_ROOT_DIR="${root}"
    unset VDE_PROJECTS_DIR
    typeset VDE_PROJECTS_BASE=""

    vde_init_resolve_projects_dir >/dev/null 2>&1

    local expected="${dotenv_base:A}"
    if [[ "${VDE_PROJECTS_BASE}" == "${expected}" ]]; then
        test_pass ".env honored"
    else
        test_fail ".env honored" "base='${VDE_PROJECTS_BASE}' expected='${expected}'"
    fi
}

# =============================================================================
# Run All Tests
# =============================================================================
echo "=============================================="
echo "VDE init Projects-base Resolver Unit Tests"
echo "=============================================="

test_flag_wins
test_env_beats_dotenv
test_dotenv_honored

rm -rf "${HARNESS_TMP}"

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
