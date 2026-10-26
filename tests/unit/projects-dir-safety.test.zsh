#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
#
# Safety/guard regression tests — configurable Projects base (Signet #543)
# =============================================================================
# Covers the remaining code-review safety findings as REAL behavioral tests:
#
#   A. vde-init resolver REFUSES command substitution in a Projects path
#      (a typed "$(touch x)" must never execute; it falls back to the default).
#   B. `vde-init --projects-dir` with NO value gives a usage error and a clean
#      non-zero exit -- not a cryptic `shift 2` abort under `set -e`.
#   C. vde-set-projects-dir REFUSES command substitution in the target path.
#   D. vde-set-projects-dir REFUSES a new base nested inside the current base.
#   E. vde-set-projects-dir on a SHARED base moves ONLY folders VDE owns
#      (registered VMs) and leaves the student's unrelated directories untouched.
#
# SAFETY (why none of this can harm the real Forge or the student's data):
#   * vde-init is NEVER executed (it runs vde_security_init / Docker / ssh at
#     load). Instead its self-contained pieces are EXTRACTED verbatim from the
#     live source with awk and eval'd here -- staying in sync with the real code
#     while touching only temp dirs. The resolver exports VDE_PROJECTS_DIR, so it
#     is always called inside a subshell to keep that out of the harness.
#   * vde-set-projects-dir IS executed, but only as a COPY inside a throwaway
#     "mini-forge" (copied lib/ + data/, a sandbox .env, no generate-all-configs
#     so config regen is skipped). Every child runs under `env -u VDE_PROJECTS_DIR`
#     so OLD_BASE can ONLY come from the sandbox .env -- it can never resolve to
#     the real $HOME/GitHub or the separate /home/dderyldowney/VDE install.
#   * All sandboxes live under one mktemp root, torn down on exit. The repo's own
#     .env, configs/, and bin/ are never written.
# =============================================================================

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
typeset -r REPO_ROOT="${VDE_ROOT_DIR}"
typeset -r INIT_SRC="${REPO_ROOT}/bin/vde-init"
typeset -r SPD_SRC="${REPO_ROOT}/bin/vde-set-projects-dir"

# Real error-code values for faithful exit-status assertions (read-only).
source "${REPO_ROOT}/lib/vde-shell-compat" &>/dev/null
source "${REPO_ROOT}/lib/vde-constants"    &>/dev/null
source "${REPO_ROOT}/lib/vde-errors"       &>/dev/null

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

assert_eq() {  # <label> <expected> <actual>
    if [[ "$3" == "$2" ]]; then test_pass "$1"; else test_fail "$1" "expected '$2', got '$3'"; fi
}
assert_true()  { if eval "$2"; then test_pass "$1"; else test_fail "$1" "condition false: $2"; fi; }
assert_false() { if eval "$2"; then test_fail "$1" "condition unexpectedly true: $2"; else test_pass "$1"; fi; }

# Stub the logging helper the resolver may call.
vde_log_warn() { : ; }

# -----------------------------------------------------------------------------
# Sandbox lifecycle
# -----------------------------------------------------------------------------
typeset SANDBOX_ROOT
SANDBOX_ROOT="$(mktemp -d /tmp/vde-projects-safety.XXXXXX)"
cleanup() {
    if [[ -n "${SANDBOX_ROOT}" && -d "${SANDBOX_ROOT}" \
          && "${SANDBOX_ROOT}" == /tmp/vde-projects-safety.* ]]; then
        rm -rf -- "${SANDBOX_ROOT}"
    fi
}
trap cleanup EXIT INT TERM

_env_val() {  # echo the persisted VDE_PROJECTS_DIR from a forge's .env
    grep -E '^VDE_PROJECTS_DIR=' "${1}/.env" 2>/dev/null | tail -1 | sed 's/^VDE_PROJECTS_DIR=//'
}

# =============================================================================
# A. vde-init resolver — command-substitution refusal (extract + eval)
# =============================================================================
typeset RESOLVER_SRC
RESOLVER_SRC="$(awk '/^vde_init_resolve_projects_dir\(\) \{/,/^\}$/' "${INIT_SRC}")"
if [[ -z "${RESOLVER_SRC}" ]]; then
    echo "FATAL: could not extract vde_init_resolve_projects_dir from ${INIT_SRC}"; exit 1
fi
eval "${RESOLVER_SRC}"

# Drive the resolver in a subshell (keeps its exported VDE_PROJECTS_DIR local to
# the subshell) and echo the resolved base.
_run_init_resolver() {  # $1=root  $2=flag-value
    typeset QUIET=1
    typeset PROJECTS_DIR_FLAG="$2"
    typeset VDE_ROOT_DIR="$1"
    unset VDE_PROJECTS_DIR
    typeset VDE_PROJECTS_BASE=""
    vde_init_resolve_projects_dir >/dev/null 2>&1
    print -r -- "${VDE_PROJECTS_BASE}"
}

test_init_injection_refused() {
    test_start "vde-init resolver refuses command substitution (no code runs)"
    local root; root="$(mktemp -d "${SANDBOX_ROOT}/init.XXXXXX")"
    : > "${root}/.env"
    local marker="${SANDBOX_ROOT}/INJECTED_INIT"
    local payload='$(touch '"${marker}"')'           # literal: $(touch /.../INJECTED_INIT)

    local resolved; resolved="$(_run_init_resolver "${root}" "${payload}")"
    local expected="${root}/projects"; expected="${expected:A}"

    assert_false "no marker created (payload not executed)" "[[ -e '${marker}' ]]"
    assert_eq    "falls back to the default base"           "${expected}" "${resolved}"
}

# =============================================================================
# B. vde-init `--projects-dir` arg-parse guard (extract loop + eval)
# =============================================================================
typeset ARGPARSE_SRC
ARGPARSE_SRC="$(awk '/^while \[\[ \$\{#\} -gt 0 \]\] ; do/,/^done$/' "${INIT_SRC}")"
if [[ -z "${ARGPARSE_SRC}" ]]; then
    echo "FATAL: could not extract the --projects-dir arg loop from ${INIT_SRC}"; exit 1
fi

# Run the REAL arg-parser loop in a subshell with stubbed error/usage helpers.
# On the lone-flag guard it `exit`s (that becomes the subshell's status); on
# success it prints FLAG=<value>.
_run_argparse() {  # args = CLI args to feed
    (
        source "${REPO_ROOT}/lib/vde-shell-compat" &>/dev/null
        source "${REPO_ROOT}/lib/vde-constants"    &>/dev/null
        vde_error_simple() { print -r -- "ERR: $*"; }
        vde_init_usage()   { : ; }
        typeset NETWORKS_ONLY=0 TESTING=0 FORCE=0 QUIET=0 PROJECTS_DIR_FLAG=""
        set -- "$@"
        eval "${ARGPARSE_SRC}"
        print -r -- "FLAG=${PROJECTS_DIR_FLAG}"
    )
}

test_init_loneflag_usage_error() {
    test_start "vde-init --projects-dir with no value => usage error, clean exit"
    local out rc
    out="$(_run_argparse --projects-dir 2>&1)"; rc=$?
    assert_eq   "exit code is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${rc}"
    assert_true "message explains a path is required" "[[ '${out}' == *'requires a path argument'* ]]"
    assert_false "did not fall through to set the flag" "[[ '${out}' == *'FLAG='* ]]"
}

test_init_loneflag_positive_control() {
    test_start "vde-init --projects-dir <path> and =<path> set the flag (control)"
    local out1 rc1 out2 rc2
    out1="$(_run_argparse --projects-dir /some/path 2>&1)"; rc1=$?
    out2="$(_run_argparse --projects-dir=/eq/path 2>&1)"; rc2=$?
    assert_eq "space form sets flag"  "FLAG=/some/path" "${out1}"
    assert_eq "space form exits 0"    "0"               "${rc1}"
    assert_eq "equals form sets flag" "FLAG=/eq/path"   "${out2}"
}

# =============================================================================
# C/D/E. vde-set-projects-dir — sandboxed mini-forge
# =============================================================================
# Build a throwaway forge whose .env records <dotenv_base> as the current base.
_make_spd_forge() {  # $1=dotenv_base ; echoes forge root
    local forge; forge="$(mktemp -d "${SANDBOX_ROOT}/spd.XXXXXX")"
    mkdir -p "${forge}/bin"
    cp "${SPD_SRC}" "${forge}/bin/vde-set-projects-dir"
    cp -R "${REPO_ROOT}/lib"  "${forge}/lib"          # copied, never symlinked
    cp -R "${REPO_ROOT}/data" "${forge}/data"         # so is_known_vm sees the registry
    print -r -- "VDE_PROJECTS_DIR=${1}" > "${forge}/.env"
    print -r -- "${forge}"
}
# Run the forge's script with the ambient override stripped. Sets SPD_OUT/SPD_RC.
_run_spd() {  # $1=forge ; rest=args
    local forge="$1"; shift
    SPD_OUT="$(env -u VDE_PROJECTS_DIR VDE_NO_CACHE=1 "${forge}/bin/vde-set-projects-dir" "$@" 2>&1)"
    SPD_RC=$?
}

# A forge that ALSO carries the config smelter + templates, so a re-point can
# actually regenerate Spoke configs (the plain _make_spd_forge omits them, which
# makes set-projects-dir skip regen -- fine for the other tests).
_make_spd_forge_full() {  # $1=dotenv_base ; echoes forge root
    local forge; forge="$(_make_spd_forge "${1}")"
    cp "${REPO_ROOT}/bin/generate-all-configs" "${forge}/bin/generate-all-configs"
    chmod +x "${forge}/bin/generate-all-configs"
    cp -R "${REPO_ROOT}/templates" "${forge}/templates"
    print -r -- "${forge}"
}

test_spd_injection_refused() {
    test_start "vde-set-projects-dir refuses command substitution (no code runs)"
    local old; old="$(mktemp -d "${SANDBOX_ROOT}/spdold.XXXXXX")"
    local forge; forge="$(_make_spd_forge "${old}")"
    local marker="${SANDBOX_ROOT}/INJECTED_SPD"
    typeset SPD_OUT SPD_RC
    _run_spd "${forge}" '$(touch '"${marker}"')'

    assert_eq    "exit code is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${SPD_RC}"
    assert_false "no marker created (payload not executed)" "[[ -e '${marker}' ]]"
    assert_true  "error names command substitution" "[[ '${SPD_OUT}' == *'command substitution'* ]]"
    assert_eq    ".env left unchanged" "${old}" "$(_env_val "${forge}")"
}

test_spd_nested_base_refused() {
    test_start "vde-set-projects-dir refuses a new base nested inside the old base"
    local old; old="$(mktemp -d "${SANDBOX_ROOT}/spdnest.XXXXXX")"
    local new="${old}/inside"
    local forge; forge="$(_make_spd_forge "${old}")"
    typeset SPD_OUT SPD_RC
    _run_spd "${forge}" "${new}"

    assert_eq    "exit code is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${SPD_RC}"
    assert_true  "error explains the nesting" "[[ '${SPD_OUT}' == *'inside the current base'* ]]"
    assert_false "nested base was not created" "[[ -d '${new}' ]]"
    assert_eq    ".env left unchanged" "${old}" "$(_env_val "${forge}")"
}

test_spd_moves_only_known_vms() {
    test_start "vde-set-projects-dir moves ONLY registered VMs; unrelated dirs untouched"
    local old; old="$(mktemp -d "${SANDBOX_ROOT}/spdmoveold.XXXXXX")"
    local new="${SANDBOX_ROOT}/spdmovenew.$RANDOM"

    # Two registered VMs (python, rust) and two unrelated student dirs.
    mkdir -p "${old}/python" "${old}/rust" "${old}/dderyldowney" "${old}/notes"
    print -r -- "pyfile"   > "${old}/python/hello.txt"
    print -r -- "rustfile" > "${old}/rust/hello.txt"
    print -r -- "MINE"     > "${old}/dderyldowney/REPO_MARKER"
    print -r -- "keep"     > "${old}/notes/keep.txt"

    local forge; forge="$(_make_spd_forge "${old}")"
    typeset SPD_OUT SPD_RC
    _run_spd "${forge}" "${new}"

    assert_eq   "re-point succeeds (VDE_SUCCESS)" "${VDE_SUCCESS}" "${SPD_RC}"
    # Known VMs moved (whole dir + contents) ...
    assert_true  "python moved to new base"  "[[ -f '${new}/python/hello.txt' ]]"
    assert_true  "rust moved to new base"    "[[ -f '${new}/rust/hello.txt' ]]"
    assert_false "python gone from old base" "[[ -d '${old}/python' ]]"
    assert_false "rust gone from old base"   "[[ -d '${old}/rust' ]]"
    # ... unrelated student dirs left exactly where they were.
    assert_true  "dderyldowney untouched in old base" "[[ -f '${old}/dderyldowney/REPO_MARKER' ]]"
    assert_true  "notes untouched in old base"        "[[ -f '${old}/notes/keep.txt' ]]"
    assert_false "dderyldowney NOT moved to new base" "[[ -e '${new}/dderyldowney' ]]"
    assert_false "notes NOT moved to new base"        "[[ -e '${new}/notes' ]]"
    # Source of truth updated to the new base.
    assert_eq   ".env now records the new base" "${new:A}" "$(_env_val "${forge}")"
}

# -----------------------------------------------------------------------------
# .env REWRITE must preserve sed-special chars (code-review fix #1). The old
# `sed s|^VDE_PROJECTS_DIR=.*|VDE_PROJECTS_DIR=${base}|` mangled a base containing
# `&` (whole-match) or `|` (delimiter); the zsh-native rewrite stores it verbatim.
# These bases are legal on Linux. We assert the persisted .env value is exact.
# -----------------------------------------------------------------------------
test_spd_env_rewrite_preserves_special_chars() {
    test_start "vde-set-projects-dir .env rewrite keeps special chars (& |) intact"
    local old; old="$(mktemp -d "${SANDBOX_ROOT}/spdsc.XXXXXX")"
    local new="${SANDBOX_ROOT}/sc-base.${RANDOM}/a&b|c"
    local forge; forge="$(_make_spd_forge "${old}")"
    typeset SPD_OUT SPD_RC
    _run_spd "${forge}" "${new}"
    assert_eq "re-point succeeds"                         "${VDE_SUCCESS}" "${SPD_RC}"
    assert_eq ".env stores the exact special-char base"   "${new:A}"       "$(_env_val "${forge}")"
}

test_init_env_rewrite_preserves_special_chars() {
    test_start "vde-init resolver .env rewrite keeps special chars (& |) intact"
    local root; root="$(mktemp -d "${SANDBOX_ROOT}/initsc.XXXXXX")"
    # Pre-seed an existing key so the REWRITE path (not append) is exercised.
    print -r -- "VDE_PROJECTS_DIR=/old/placeholder" > "${root}/.env"
    local base="${SANDBOX_ROOT}/initsc-base.${RANDOM}/x&y|z"
    # Extracted resolver persists base to ${root}/.env; run in a subshell so its
    # exported VDE_PROJECTS_DIR does not leak into the harness.
    ( typeset QUIET=1
      typeset PROJECTS_DIR_FLAG="${base}"
      typeset VDE_ROOT_DIR="${root}"
      unset VDE_PROJECTS_DIR
      typeset VDE_PROJECTS_BASE=""
      vde_init_resolve_projects_dir >/dev/null 2>&1 )
    assert_eq ".env stores the exact special-char base" "${base:A}" "$(_env_val "${root}")"
}

# -----------------------------------------------------------------------------
# Re-point must REWRITE existing Spokes (Signet #546). The smelter skips Spokes
# whose compose/env already exist, so set-projects-dir must force-regenerate --
# otherwise an existing Spoke keeps its old literal mount and never reads the new
# base. We pre-seed a stale python Spoke (literal mount + env) and assert the
# re-point rewrites its mount to the ${VDE_PROJECTS_DIR:-...} interpolation.
# -----------------------------------------------------------------------------
test_spd_repoint_rewrites_existing_spoke_mount() {
    test_start "vde-set-projects-dir re-point force-regenerates an existing Spoke's mount"
    local old; old="$(mktemp -d "${SANDBOX_ROOT}/spdregen-old.XXXXXX")"
    local new="${SANDBOX_ROOT}/spdregen-new.${RANDOM}"
    local forge; forge="$(_make_spd_forge_full "${old}")"

    # Pre-seed a STALE python Spoke: a literal projects mount + its env file.
    # (Both existing is exactly what made the pre-fix, non-forced regen skip it.)
    mkdir -p "${forge}/configs/docker/languages/python" "${forge}/env-files"
    print -rl -- "    volumes:" \
        "      - ../../../../projects/python:/home/devuser/workspace" \
        > "${forge}/configs/docker/languages/python/docker-compose.yml"
    print -r -- "SSH_PORT=2201" > "${forge}/env-files/python.env"

    typeset SPD_OUT SPD_RC
    _run_spd "${forge}" "${new}"

    local pyc; pyc="$(find "${forge}/configs" -path '*languages/python*' -name 'docker-compose.yml' 2>/dev/null | head -1)"
    assert_eq   "re-point succeeds"                         "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true "python compose still present after regen"  "[[ -f '${pyc}' ]]"
    assert_true "mount is now the \${VDE_PROJECTS_DIR:-...} interpolation" "grep -q 'VDE_PROJECTS_DIR:-' '${pyc}'"
    assert_false "stale literal projects/python mount is gone" "grep -qE '^[[:space:]]*- [.][.]/[.][.]/[.][.]/[.][.]/projects/python:' '${pyc}'"
}

# =============================================================================
# Run
# =============================================================================
echo "=============================================="
echo "VDE Projects-dir Safety/Guard Regression Tests (#543)"
echo "=============================================="

test_init_injection_refused
test_init_loneflag_usage_error
test_init_loneflag_positive_control
test_spd_injection_refused
test_spd_nested_base_refused
test_spd_moves_only_known_vms
test_spd_env_rewrite_preserves_special_chars
test_init_env_rewrite_preserves_special_chars
test_spd_repoint_rewrites_existing_spoke_mount

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
