#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1
#
# Move-safety tests for `vde set-projects-dir` (Signet #669, #545 items 6,7,8,10)
# =============================================================================
#   7. A running Spoke of an alias that WOULD be moved blocks the whole re-point
#      (nothing moved, .env unchanged). A running Spoke of an alias that is NOT
#      moved (collision / absent) never blocks.
#   6. A cross-filesystem move copies to <dest>.vde-moving and renames on
#      success; a failed copy leaves the source whole and nothing at the
#      destination; a stale temp is discarded; a symlinked temp is refused;
#      a same-filesystem move stays a plain rename (no copy).
#   8. An INT/TERM during the run prints how to finish; re-running the same
#      command completes the move.
#  10. vde_warn_stale_projects_env warns (stderr, never fails) when an exported
#      VDE_PROJECTS_DIR differs from the .env value, and is silent otherwise;
#      set-projects-dir and `vde start` call it.
#
# SAFETY: every run is a COPY of the script inside a throwaway mini-forge under
# one mktemp root (plus one under /dev/shm for the cross-device cases), with
# docker/cp/mv replaced by PATH stubs. The real repo, .env and Docker are never
# touched; every child runs under `env -u VDE_PROJECTS_DIR` unless a case sets it.
# =============================================================================

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
typeset -r REPO_ROOT="${VDE_ROOT_DIR}"
typeset -r SPD_SRC="${REPO_ROOT}/bin/vde-set-projects-dir"
typeset -r VDE_SRC="${REPO_ROOT}/bin/vde"

source "${REPO_ROOT}/lib/vde-shell-compat" &>/dev/null
source "${REPO_ROOT}/lib/vde-constants"    &>/dev/null
source "${REPO_ROOT}/lib/vde-errors"       &>/dev/null
zmodload zsh/stat

typeset TESTS_PASSED=0 TESTS_FAILED=0 TESTS_SKIPPED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }
test_skip()  { echo -e "${YELLOW}[SKIP]${RESET} $1"; ((TESTS_SKIPPED++)); }
assert_eq()    { if [[ "$3" == "$2" ]]; then test_pass "$1"; else test_fail "$1" "expected '$2', got '$3'"; fi; }
assert_true()  { if eval "$2"; then test_pass "$1"; else test_fail "$1" "condition false: $2"; fi; }
assert_false() { if eval "$2"; then test_fail "$1" "condition unexpectedly true: $2"; else test_pass "$1"; fi; }
assert_has()   { if [[ "$3" == *"$2"* ]]; then test_pass "$1"; else test_fail "$1" "output lacks '$2': ${3:0:300}"; fi; }

# -----------------------------------------------------------------------------
# Sandboxes: SANDBOX_ROOT (default tmp) and SHM_ROOT (/dev/shm, a different device)
# -----------------------------------------------------------------------------
typeset SANDBOX_ROOT SHM_ROOT=""
SANDBOX_ROOT="$(mktemp -d /tmp/vde-spd-move.XXXXXX)"
if [[ -d /dev/shm && -w /dev/shm ]]; then
    SHM_ROOT="$(mktemp -d /dev/shm/vde-spd-move.XXXXXX 2>/dev/null)"
fi
cleanup() {
    [[ -n "${SANDBOX_ROOT}" && "${SANDBOX_ROOT}" == /tmp/vde-spd-move.* ]] && rm -rf -- "${SANDBOX_ROOT}"
    [[ -n "${SHM_ROOT}" && "${SHM_ROOT}" == /dev/shm/vde-spd-move.* ]] && rm -rf -- "${SHM_ROOT}"
}
trap "cleanup; vde_test_env_leave" EXIT INT TERM

# The real mv, baked into stubs so a stub never recurses into itself.
typeset -r REAL_MV="$(whence -p mv)"

_dev() { local -a d; zstat -A d +device -- "$1"; print -r -- "${d[1]}"; }
_xdev_ok() {  # true when /dev/shm is a usable, different device from the sandbox
    [[ -n "${SHM_ROOT}" && -d "${SHM_ROOT}" && "$(_dev "${SANDBOX_ROOT}")" != "$(_dev "${SHM_ROOT}")" ]]
}
_env_val() { grep -E '^VDE_PROJECTS_DIR=' "${1}/.env" 2>/dev/null | tail -1 | sed 's/^VDE_PROJECTS_DIR=//'; }

_make_forge() {  # $1=dotenv_base ; echoes forge root (copied lib/ + data/)
    local forge; forge="$(mktemp -d "${SANDBOX_ROOT}/forge.XXXXXX")"
    mkdir -p "${forge}/bin" "${forge}/stubs"
    cp "${SPD_SRC}" "${forge}/bin/vde-set-projects-dir"
    cp -R "${REPO_ROOT}/lib"  "${forge}/lib"
    cp -R "${REPO_ROOT}/data" "${forge}/data"
    print -r -- "VDE_PROJECTS_DIR=${1}" > "${forge}/.env"
    _stub "${forge}" docker <<< 'exit 0'     # default: no Spoke running; never the real daemon
    print -r -- "${forge}"
}
_stub() {  # $1=forge $2=name ; body on stdin -> executable PATH stub
    { print -r -- '#!/usr/bin/env zsh'; cat; } > "${1}/stubs/${2}"
    chmod +x "${1}/stubs/${2}"
}
_stub_docker_running() {  # $1=forge ; $2...=container names `docker ps` reports
    local forge="$1"; shift
    print -r -- "${(F)@}" > "${forge}/running.txt"
    _stub "${forge}" docker <<EOF
[[ "\$1" == ps ]] && { cat "${forge}/running.txt"; exit 0; }
exit 0
EOF
}
typeset SPD_OUT SPD_RC
typeset -a SPD_ENV=()   # extra NAME=value pairs for the next _run_spd
_run_spd() {  # $1=forge ; rest=args ; PATH puts the forge's stubs first; 60s cap so a hang is a FAIL, not a stall
    local forge="$1"; shift
    SPD_OUT="$(timeout 60 env -u VDE_PROJECTS_DIR VDE_NO_CACHE=1 "${SPD_ENV[@]}" PATH="${forge}/stubs:${PATH}" \
        "${forge}/bin/vde-set-projects-dir" "$@" 2>&1)"
    SPD_RC=$?
}
_mk_alias() {  # $1=base $2=alias : a small tree with a nested file, mode 600 file, relative symlink
    mkdir -p "${1}/${2}/sub"
    print -r -- "hello-${2}" > "${1}/${2}/hello.txt"
    print -r -- "nested"     > "${1}/${2}/sub/deep.txt"
    print -r -- "secret"     > "${1}/${2}/private.txt"; chmod 600 "${1}/${2}/private.txt"
    ln -s hello.txt "${1}/${2}/link"
}

# =============================================================================
# 7. running Spokes
# =============================================================================
test_running_spoke_of_moved_alias_blocks() {
    test_start "7: a running Spoke of an alias that would move blocks the re-point, nothing touched"
    local old="${SANDBOX_ROOT}/run-old" new="${SANDBOX_ROOT}/run-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    local forge; forge="$(_make_forge "${old}")"
    _stub_docker_running "${forge}" vde-python
    _run_spd "${forge}" "${new}"

    assert_eq    "refuses with VDE_ERR_GENERAL" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_has   "names the running Spoke" "vde-python" "${SPD_OUT}"
    assert_has   "tells the student how to proceed" "vde stop python" "${SPD_OUT}"
    assert_true  "python still at old base" "[[ -f '${old}/python/hello.txt' ]]"
    assert_true  "rust (not running) also untouched" "[[ -f '${old}/rust/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
    assert_eq    ".env unchanged" "${old}" "$(_env_val "${forge}")"
}

test_running_spoke_of_unmoved_alias_does_not_block() {
    test_start "7: a running Spoke of an alias that is NOT moved (collision / absent) does not block"
    local old="${SANDBOX_ROOT}/run2-old" new="${SANDBOX_ROOT}/run2-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    mkdir -p "${new}/python"                       # collision: python will be skipped
    local forge; forge="$(_make_forge "${old}")"
    _stub_docker_running "${forge}" vde-python vde-ruby   # ruby has no folder at all
    _run_spd "${forge}" "${new}"

    assert_eq    "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "rust moved" "[[ -f '${new}/rust/hello.txt' ]]"
    assert_true  "colliding python left at old base" "[[ -f '${old}/python/hello.txt' ]]"
    assert_eq    ".env updated" "${new:A}" "$(_env_val "${forge}")"
}

# =============================================================================
# 6. cross-filesystem moves
# =============================================================================
_stub_failing_cp() {  # a cp that leaves a partial copy at its destination then fails (ENOSPC-like)
    _stub "$1" cp <<'EOF'
dest=${@[-1]}
mkdir -p -- "${dest}"
print partial > "${dest}/partial.bin"
exit 1
EOF
}

test_crossfs_failed_copy_leaves_source_authoritative() {
    test_start "6: a failed cross-filesystem copy leaves the source whole and nothing at the destination"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/x1-old" new="${SHM_ROOT}/x1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub_failing_cp "${forge}"
    _run_spd "${forge}" "${new}"

    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' && -f '${old}/python/sub/deep.txt' ]]"
    assert_false "no (partial) alias at destination" "[[ -e '${new}/python' ]]"
    assert_false "no .vde-moving temp left behind" "[[ -e '${new}/python.vde-moving' ]]"
    assert_has   "visibly reports the failed alias by name" "Could not move 'python'; left in place at ${old}/python" "${SPD_OUT}"
    assert_eq    "a failed move is a failed command (VDE_ERR_GENERAL), not success" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_has   "says action is required" "ACTION REQUIRED" "${SPD_OUT}"
    assert_has   "says .env was NOT switched" ".env was NOT changed" "${SPD_OUT}"
    assert_eq    ".env still names the old base (a re-run can finish the job)" "${old}" "$(_env_val "${forge}")"
    assert_false "no 'Re-pointed' banner after a failure" "[[ '${SPD_OUT}' == *'Projects Base Re-pointed'* ]]"

    # The student fixes the cause (here: the cp stub goes away) and re-runs the same command.
    rm -f "${forge}/stubs/cp"
    _run_spd "${forge}" "${new}"
    assert_eq    "re-run succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "python is now at the new base" "[[ -f '${new}/python/hello.txt' && -f '${new}/python/sub/deep.txt' ]]"
    assert_false "and gone from the old base" "[[ -e '${old}/python' ]]"
    assert_eq    ".env now names the new base" "${new:A}" "$(_env_val "${forge}")"
}

test_crossfs_real_move_completes() {
    test_start "6: a real cross-device move completes with identical content, mode and symlink"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/x2-old" new="${SHM_ROOT}/x2-new" ref="${SANDBOX_ROOT}/x2-ref"
    _mk_alias "${old}" python; cp -a "${old}/python" "${ref}"
    local forge; forge="$(_make_forge "${old}")"
    _run_spd "${forge}" "${new}"

    assert_eq    "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "tree identical" "diff -r '${ref}' '${new}/python' >/dev/null"
    assert_eq    "mode 600 preserved" "600" "$(command stat -c %a "${new}/python/private.txt")"
    assert_eq    "relative symlink preserved" "hello.txt" "$(readlink "${new}/python/link")"
    assert_false "source gone" "[[ -e '${old}/python' ]]"
    assert_false "no .vde-moving temp left" "[[ -e '${new}/python.vde-moving' ]]"
    assert_eq    ".env updated" "${new:A}" "$(_env_val "${forge}")"
}

test_crossfs_stale_temp_is_discarded() {
    test_start "6: a leftover <alias>.vde-moving from an interrupted run is discarded and the move retried"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/x3-old" new="${SHM_ROOT}/x3-new"
    _mk_alias "${old}" python
    mkdir -p "${new}/python.vde-moving"; print stale > "${new}/python.vde-moving/stale.txt"
    local forge; forge="$(_make_forge "${old}")"
    _run_spd "${forge}" "${new}"

    assert_true  "python moved" "[[ -f '${new}/python/hello.txt' ]]"
    assert_false "stale file did not leak into the result" "[[ -e '${new}/python/stale.txt' ]]"
    assert_false "temp gone" "[[ -e '${new}/python.vde-moving' ]]"
}

test_crossfs_symlinked_temp_is_refused() {
    test_start "6: a symlinked <alias>.vde-moving is refused; the link target is never touched"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/x4-old" new="${SHM_ROOT}/x4-new" victim="${SANDBOX_ROOT}/x4-victim"
    _mk_alias "${old}" python
    mkdir -p "${new}" "${victim}"; print keep > "${victim}/keep.txt"
    ln -s "${victim}" "${new}/python.vde-moving"
    local forge; forge="$(_make_forge "${old}")"
    _run_spd "${forge}" "${new}"

    assert_true  "victim file intact" "[[ -f '${victim}/keep.txt' ]]"
    assert_true  "source intact (alias left in place)" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "nothing created at <dest>/python" "[[ -e '${new}/python' ]]"
    assert_has   "explains the refusal" "vde-moving" "${SPD_OUT}"
}

test_samefs_move_is_a_plain_rename() {
    test_start "6: a same-filesystem move never invokes cp (atomic rename)"
    local old="${SANDBOX_ROOT}/s1-old" new="${SANDBOX_ROOT}/s1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub_failing_cp "${forge}"
    _run_spd "${forge}" "${new}"

    assert_true  "python moved despite a failing cp" "[[ -f '${new}/python/hello.txt' ]]"
    assert_false "source gone" "[[ -e '${old}/python' ]]"
}

# =============================================================================
# 8. interruption
# =============================================================================
test_interrupt_in_move_loop_then_rerun_completes() {
    test_start "8: SIGTERM mid-loop prints how to finish; re-running the same command completes"
    local old="${SANDBOX_ROOT}/i1-old" new="${SANDBOX_ROOT}/i1-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    local forge; forge="$(_make_forge "${old}")"
    # mv that performs the real move for the first alias, then TERMs the script.
    _stub "${forge}" mv <<EOF
${REAL_MV} "\$@" || exit \$?
# Only after moving the python alias (lib start-up also calls mv; that must not signal).
if [[ ! -e "${forge}/signaled" ]] && (( \${#\${(M)@:#*/python}} )); then : > "${forge}/signaled"; kill -TERM \$PPID; fi
EOF
    _run_spd "${forge}" "${new}"

    assert_true  "first run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "says it was interrupted while moving" "Interrupted while moving" "${SPD_OUT}"
    assert_has   "tells the student to re-run" "re-run the same command" "${SPD_OUT}"
    assert_has   "tells the student not to start Spokes" "do not start Spokes" "${SPD_OUT}"
    assert_true  "python (first) moved" "[[ -f '${new}/python/hello.txt' ]]"
    assert_true  "rust still at old base" "[[ -f '${old}/rust/hello.txt' ]]"
    assert_eq    ".env still names the old base" "${old}" "$(_env_val "${forge}")"

    rm -f "${forge}/stubs/mv"                    # re-run without the interrupting stub
    _run_spd "${forge}" "${new}"
    assert_eq    "re-run succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "rust now moved" "[[ -f '${new}/rust/hello.txt' ]]"
    assert_true  "python still there" "[[ -f '${new}/python/hello.txt' ]]"
    assert_eq    ".env now names the new base" "${new:A}" "$(_env_val "${forge}")"
}

test_interrupt_in_regen_phase_message() {
    test_start "8: SIGTERM during config regeneration says the base is updated and what to recreate"
    local old="${SANDBOX_ROOT}/i2-old" new="${SANDBOX_ROOT}/i2-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" generate-all-configs <<'EOF'
kill -TERM $PPID
EOF
    cp "${forge}/stubs/generate-all-configs" "${forge}/bin/generate-all-configs"   # the script runs ${ROOT}/bin/generate-all-configs
    _run_spd "${forge}" "${new}"

    assert_true  "run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "reports the post-update interruption" "Interrupted after the base was updated" "${SPD_OUT}"
    assert_has   "names the recreate remedy" "vde remove" "${SPD_OUT}"
    assert_eq    ".env was already updated" "${new:A}" "$(_env_val "${forge}")"
}

# =============================================================================
# 10. stale exported VDE_PROJECTS_DIR
# =============================================================================
_warn_out() {  # $1=exported value ('' = unset) $2=.env value ('' = no key) ; prints stderr, then "rc=N"
    local root; root="$(mktemp -d "${SANDBOX_ROOT}/warn.XXXXXX")"
    local envval="${2//@HOME@/${root}/home}"      # @HOME@ stands for this call's sandbox HOME
    [[ -n "${envval}" ]] && print -r -- "VDE_PROJECTS_DIR=${envval}" > "${root}/.env"
    local out
    out="$(HOME="${root}/home" VDE_ROOT_DIR="${root}" VAL="$1" LIBDIR="${REPO_ROOT}/lib" zsh -c '
        source "${LIBDIR}/vde-shell-compat" &>/dev/null; source "${LIBDIR}/vde-constants" &>/dev/null
        source "${LIBDIR}/vde-path-utils" &>/dev/null
        if [[ -n "${VAL}" ]]; then export VDE_PROJECTS_DIR="${VAL}"; else unset VDE_PROJECTS_DIR; fi
        vde_warn_stale_projects_env 2>&1 >/dev/null
        print -r -- "rc=$?"' 2>&1)"
    print -r -- "${out}"
}

test_warn_helper() {
    test_start "10: vde_warn_stale_projects_env warns only when the export differs from .env"
    local out
    out="$(_warn_out /x/stale /y/real)"
    assert_has "differing export warns with the exported value" "/x/stale" "${out}"
    assert_has "...and the .env value" "/y/real" "${out}"
    assert_has "...and the remedy" "unset VDE_PROJECTS_DIR" "${out}"
    assert_has "never fails" "rc=0" "${out}"

    out="$(_warn_out /y/real /y/real)";  assert_eq "equal export is silent" "rc=0" "${out}"
    out="$(_warn_out '' /y/real)";       assert_eq "unset export is silent" "rc=0" "${out}"
    out="$(_warn_out /x/only '')";       assert_eq "export with no .env key is silent" "rc=0" "${out}"
    out="$(_warn_out '~/p' '@HOME@/p')"
    assert_eq "'~/p' equals its absolute form (compared resolved)" "rc=0" "${out}"
}

test_spd_warns_on_stale_export() {
    test_start "10: set-projects-dir warns when an exported VDE_PROJECTS_DIR outranks the new .env value"
    local old="${SANDBOX_ROOT}/w-old" new="${SANDBOX_ROOT}/w-new"
    mkdir -p "${old}"; _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    SPD_OUT="$(env VDE_PROJECTS_DIR="${old}" VDE_NO_CACHE=1 PATH="${forge}/stubs:${PATH}" \
        "${forge}/bin/vde-set-projects-dir" "${new}" 2>&1)"; SPD_RC=$?
    assert_eq  "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_has "warns about the stale export" "unset VDE_PROJECTS_DIR" "${SPD_OUT}"

    local old2="${SANDBOX_ROOT}/w2-old" new2="${SANDBOX_ROOT}/w2-new"
    mkdir -p "${old2}"; _mk_alias "${old2}" python
    forge="$(_make_forge "${old2}")"
    _run_spd "${forge}" "${new2}"
    assert_false "no export => no warning" "[[ '${SPD_OUT}' == *'unset VDE_PROJECTS_DIR'* ]]"
}

test_vde_start_calls_the_helper() {
    test_start "10: bin/vde's start arm calls the helper before vde_action_start"
    # Comment lines are dropped first: a call that exists only in a comment must not count.
    local arm; arm="$(awk '/^    start\)/{f=1} f{print} f&&/;;/{exit}' "${VDE_SRC}" | grep -vE '^[[:space:]]*#')"
    assert_has "start arm warns" "vde_warn_stale_projects_env" "${arm}"
    local pre="${arm%%vde_action_start*}"
    assert_has "warning precedes the action" "vde_warn_stale_projects_env" "${pre}"
}

# =============================================================================
# Code-review findings (Signet #669): guard fails closed, start-during-copy,
# .env verified before the first move, interrupt while removing the old copy.
# =============================================================================
test_docker_query_failure_refuses() {
    test_start "7: a failing 'docker ps' cannot be read as 'nothing is running': refuse, move nothing"
    local old="${SANDBOX_ROOT}/f1-old" new="${SANDBOX_ROOT}/f1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" docker <<< 'exit 1'
    _run_spd "${forge}" "${new}"

    assert_eq    "refuses with VDE_ERR_GENERAL" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_has   "says it cannot tell what is running" "Cannot tell which Spokes are running" "${SPD_OUT}"
    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
    assert_eq    ".env unchanged" "${old}" "$(_env_val "${forge}")"

    # Nothing to move => Docker is never needed, so a broken Docker does not block.
    local old2="${SANDBOX_ROOT}/f2-old" new2="${SANDBOX_ROOT}/f2-new"
    mkdir -p "${old2}/notes"
    forge="$(_make_forge "${old2}")"
    _stub "${forge}" docker <<< 'exit 1'
    _run_spd "${forge}" "${new2}"
    assert_eq    "no movable alias => succeeds even with a broken docker" "${VDE_SUCCESS}" "${SPD_RC}"
}

test_running_match_is_exact() {
    test_start "7: only the exact container vde-<alias> blocks (vde-python2, python, vde-pythonx do not)"
    local old="${SANDBOX_ROOT}/e1-old" new="${SANDBOX_ROOT}/e1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub_docker_running "${forge}" vde-python2 python vde-pythonx
    _run_spd "${forge}" "${new}"
    assert_eq    "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "python moved" "[[ -f '${new}/python/hello.txt' ]]"
}

test_spoke_started_during_copy_discards_the_copy() {
    test_start "7: a Spoke that starts while a cross-filesystem copy runs: copy discarded, source kept"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/d1-old" new="${SHM_ROOT}/d1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    # cp performs the real copy, then 'starts' the Spoke; docker reports it from then on.
    _stub "${forge}" cp <<EOF
$(whence -p cp) "\$@" || exit \$?
: > "${forge}/started"
EOF
    _stub "${forge}" docker <<EOF
[[ "\$1" == ps && -e "${forge}/started" ]] && print vde-python
exit 0
EOF
    _run_spd "${forge}" "${new}"

    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "nothing at the destination" "[[ -e '${new}/python' ]]"
    assert_false "no .vde-moving temp left" "[[ -e '${new}/python.vde-moving' ]]"
    assert_has   "explains the discarded copy" "the copy was discarded" "${SPD_OUT}"
}

test_docker_unreadable_after_copy_discards_the_copy() {
    test_start "7: Docker becoming unreadable after a cross-filesystem copy counts as 'running': copy discarded"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/d3-old" new="${SHM_ROOT}/d3-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" cp <<EOF
$(whence -p cp) "\$@" || exit \$?
: > "${forge}/copied"
EOF
    _stub "${forge}" docker <<EOF
[[ "\$1" == ps && -e "${forge}/copied" ]] && exit 1
exit 0
EOF
    _run_spd "${forge}" "${new}"

    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "nothing at the destination" "[[ -e '${new}/python' ]]"
    assert_has   "explains the discarded copy" "the copy was discarded" "${SPD_OUT}"
}

test_unwritable_env_refuses_before_moving() {
    test_start "8: an unwritable .env is detected BEFORE the first move (nothing stranded)"
    if (( EUID == 0 )); then test_skip "running as root: file modes cannot make .env unwritable"; return; fi
    local old="${SANDBOX_ROOT}/w1-old" new="${SANDBOX_ROOT}/w1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    chmod 444 "${forge}/.env"
    _run_spd "${forge}" "${new}"
    chmod 644 "${forge}/.env"

    assert_eq    "refuses with VDE_ERR_PERMISSION" "${VDE_ERR_PERMISSION}" "${SPD_RC}"
    assert_has   "names the unwritable file" "Cannot write" "${SPD_OUT}"
    assert_true  "python still at the old base" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
}

test_interrupt_while_removing_old_copy_message() {
    test_start "8: SIGTERM while the old copy is being removed says so and what to do"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/d2-old" new="${SHM_ROOT}/d2-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    # rm that is 'interrupted' when asked to remove the SOURCE alias (it removes nothing).
    _stub "${forge}" rm <<EOF
if (( \${#\${(M)@:#*/d2-old/python}} )); then kill -TERM \$PPID; exit 0; fi
exec $(whence -p rm) "\$@"
EOF
    _run_spd "${forge}" "${new}"

    assert_true  "run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "says the old copy was not fully removed" "not fully removed" "${SPD_OUT}"
    assert_has   "tells the student to delete it by hand" "delete ${old}/python by hand" "${SPD_OUT}"
    assert_true  "the moved folder is complete at the new base" "[[ -f '${new}/python/hello.txt' ]]"
    assert_eq    ".env still names the old base" "${old}" "$(_env_val "${forge}")"
}

# =============================================================================
# Sourcery review of PR #670: each case below reproduces a verified finding.
# =============================================================================
test_noop_base_still_warns_about_stale_export() {
    test_start "10: the 'already the base' early exit still warns when the export outranks .env"
    local envbase="${SANDBOX_ROOT}/n-env" exp="${SANDBOX_ROOT}/n-exp"
    mkdir -p "${envbase}" "${exp}"
    local forge; forge="$(_make_forge "${envbase}")"
    SPD_OUT="$(env VDE_PROJECTS_DIR="${exp}" VDE_NO_CACHE=1 PATH="${forge}/stubs:${PATH}" \
        "${forge}/bin/vde-set-projects-dir" "${exp}" 2>&1)"; SPD_RC=$?
    assert_eq  "exits cleanly" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_has "reports nothing to move" "Nothing to move" "${SPD_OUT}"
    assert_has "warns the export outranks .env" "unset VDE_PROJECTS_DIR" "${SPD_OUT}"
}

test_running_jupyterlab_blocks_moving_python() {
    test_start "7: vde-jupyterlab mounts python/jupyterlabs, so it blocks moving the python folder"
    local old="${SANDBOX_ROOT}/j1-old" new="${SANDBOX_ROOT}/j1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub_docker_running "${forge}" vde-jupyterlab
    _run_spd "${forge}" "${new}"
    assert_eq    "refuses with VDE_ERR_GENERAL" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_has   "names the running JupyterLab Spoke" "vde-jupyterlab" "${SPD_OUT}"
    assert_true  "python untouched" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
}

test_hung_docker_query_times_out_and_refuses() {
    test_start "7: a Docker query that never answers times out and refuses (does not hang)"
    local old="${SANDBOX_ROOT}/h1-old" new="${SANDBOX_ROOT}/h1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    mkfifo "${forge}/never"
    _stub "${forge}" docker <<EOF
[[ "\$1" == ps ]] && cat "${forge}/never"
exit 0
EOF
    SPD_ENV=(VDE_SPD_DOCKER_TIMEOUT=2)
    _run_spd "${forge}" "${new}"
    SPD_ENV=()
    assert_eq    "refuses with VDE_ERR_GENERAL (not a 124 hang-kill)" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_has   "says it cannot tell what is running" "Cannot tell which Spokes are running" "${SPD_OUT}"
    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' ]]"
}

test_missing_docker_fails_closed() {
    test_start "7: no docker executable cannot be read as 'nothing is running'"
    local fn; fn="$(awk '/^vde_spd_running_spokes\(\) \{/,/^\}$/' "${SPD_SRC}")"
    local rc; rc="$(PATH=/nonexistent "$(whence -p zsh)" -fc "${fn}
vde_spd_running_spokes >/dev/null 2>&1; print \$?")"
    assert_eq "vde_spd_running_spokes fails when docker is not on PATH" "1" "${rc}"
}

test_hangup_prints_how_to_finish() {
    test_start "8: SIGHUP (terminal closed) prints the same recovery message as INT/TERM"
    local old="${SANDBOX_ROOT}/u1-old" new="${SANDBOX_ROOT}/u1-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" mv <<EOF
${REAL_MV} "\$@" || exit \$?
if [[ ! -e "${forge}/signaled" ]] && (( \${#\${(M)@:#*/python}} )); then : > "${forge}/signaled"; kill -HUP \$PPID; fi
EOF
    _run_spd "${forge}" "${new}"
    assert_true  "run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "says it was interrupted while moving" "Interrupted while moving" "${SPD_OUT}"
    assert_eq    ".env still names the old base" "${old}" "$(_env_val "${forge}")"
}

test_signal_right_after_env_write_reports_post_update() {
    test_start "8: a signal in the gap right after .env is written is reported as 'base updated'"
    local old="${SANDBOX_ROOT}/g1-old" new="${SANDBOX_ROOT}/g1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    local name
    for name in chmod mv; do                       # the last command of the .env writer, old or new
        _stub "${forge}" ${name} <<EOF
$(whence -p ${name}) "\$@" || exit \$?
if [[ ! -e "${forge}/envsig" ]] && grep -qF "VDE_PROJECTS_DIR=${new}" "${forge}/.env" 2>/dev/null; then : > "${forge}/envsig"; kill -TERM \$PPID; fi
EOF
    done
    _run_spd "${forge}" "${new}"
    assert_true  "run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "reports the post-update interruption" "Interrupted after the base was updated" "${SPD_OUT}"
    assert_eq    ".env names the new base" "${new:A}" "$(_env_val "${forge}")"
}

test_signal_right_after_publish_reports_old_copy() {
    test_start "8: a signal right after the temp is renamed into place names the old copy to delete"
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/p1-old" new="${SHM_ROOT}/p1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" mv <<EOF
${REAL_MV} "\$@" || exit \$?
if (( \${#\${(M)@:#*.vde-moving}} )); then kill -TERM \$PPID; fi
EOF
    _run_spd "${forge}" "${new}"
    assert_true  "run did not succeed" "(( ${SPD_RC} != 0 ))"
    assert_has   "says the old copy was not fully removed" "not fully removed" "${SPD_OUT}"
    assert_has   "names the folder to delete" "delete ${old}/python by hand" "${SPD_OUT}"
    assert_true  "the published copy is complete" "[[ -f '${new}/python/hello.txt' ]]"
}

test_unremovable_stale_temp_is_refused() {
    test_start "6: a stale <alias>.vde-moving that cannot be removed is refused (the copy never nests inside it)"
    if (( EUID == 0 )); then test_skip "running as root: file modes cannot make the temp unremovable"; return; fi
    _xdev_ok || { test_skip "no usable second device (/dev/shm)"; return; }
    local old="${SANDBOX_ROOT}/k1-old" new="${SHM_ROOT}/k1-new"
    _mk_alias "${old}" python
    mkdir -p "${new}/python.vde-moving/locked"
    print stale > "${new}/python.vde-moving/locked/f"
    chmod 555 "${new}/python.vde-moving/locked"
    local forge; forge="$(_make_forge "${old}")"
    _run_spd "${forge}" "${new}"
    chmod -R u+w "${new}/python.vde-moving"

    assert_true  "source intact" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "nothing published at <dest>/python" "[[ -e '${new}/python' ]]"
    assert_false "the copy did not nest inside the stale temp" "[[ -e '${new}/python.vde-moving/python' ]]"
    assert_has   "tells the student to remove the leftover" "leftover" "${SPD_OUT}"
}

test_unwritable_env_dir_refuses_before_moving() {
    test_start "8: an .env whose DIRECTORY is read-only (atomic rewrite impossible) is refused before moving"
    if (( EUID == 0 )); then test_skip "running as root: directory modes cannot block writes"; return; fi
    local old="${SANDBOX_ROOT}/q1-old" new="${SANDBOX_ROOT}/q1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    # .env is a symlink to a writable FILE inside a read-only directory: an in-place
    # write would work, but the temp+rename rewrite could not create its temp there.
    local rodir="${SANDBOX_ROOT}/q1-ro"; mkdir -p "${rodir}"
    print -r -- "VDE_PROJECTS_DIR=${old}" > "${rodir}/real.env"
    rm -f "${forge}/.env"; ln -s "${rodir}/real.env" "${forge}/.env"
    chmod 555 "${rodir}"
    _run_spd "${forge}" "${new}"
    chmod 755 "${rodir}"
    assert_eq    "refuses with VDE_ERR_PERMISSION" "${VDE_ERR_PERMISSION}" "${SPD_RC}"
    assert_true  "python still at the old base" "[[ -f '${old}/python/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
}

test_env_rewrite_is_atomic_and_follows_symlink() {
    test_start "8: .env is rewritten via temp+rename: other keys kept, symlink kept, no temp left"
    local old="${SANDBOX_ROOT}/s2-old" new="${SANDBOX_ROOT}/s2-new" real="${SANDBOX_ROOT}/s2-real.env"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    print -rl -- "KEEP_ME=1" "VDE_PROJECTS_DIR=${old}" "LAST=2" > "${real}"
    rm -f "${forge}/.env"; ln -s "${real}" "${forge}/.env"
    _run_spd "${forge}" "${new}"
    assert_eq    "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  ".env is still a symlink" "[[ -L '${forge}/.env' ]]"
    assert_eq    "target now names the new base" "VDE_PROJECTS_DIR=${new:A}" "$(grep '^VDE_PROJECTS_DIR=' "${real}")"
    assert_true  "other keys preserved" "grep -qx 'KEEP_ME=1' '${real}' && grep -qx 'LAST=2' '${real}'"
    assert_eq    "no temp file left beside .env" "0" "$(ls -A "${SANDBOX_ROOT}" | grep -c 's2-real.env.vde-tmp')"
    assert_eq    "no temp file left in the forge" "0" "$(ls -A "${forge}" | grep -c '\.env\.vde-tmp')"
}

# =============================================================================
# Per-Spoke locks: `vde start` claims .locks/vms/<alias>.lock before it brings a Spoke
# up, so holding the same locks for the whole re-point closes the start-during-move
# and re-point-vs-re-point races.
# =============================================================================
_lockfile() { print -r -- "${1}/.locks/vms/${2}.lock"; }

test_held_spoke_lock_blocks_the_repoint() {
    test_start "7: a Spoke operation in progress (its lock held) refuses the re-point, nothing moved"
    local old="${SANDBOX_ROOT}/l1-old" new="${SANDBOX_ROOT}/l1-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    local forge; forge="$(_make_forge "${old}")"
    local lk; lk="$(_lockfile "${forge}" python)"
    mkdir -p "${lk}"; print -r -- "$$:$$:$(date +%s)" > "${lk}/pid"     # a live owner: this test shell
    _run_spd "${forge}" "${new}"
    assert_eq    "refuses with VDE_ERR_LOCK" "${VDE_ERR_LOCK}" "${SPD_RC}"
    assert_has   "says which Spoke is busy" "python" "${SPD_OUT}"
    assert_true  "python untouched" "[[ -f '${old}/python/hello.txt' ]]"
    assert_true  "rust (unlocked) also untouched" "[[ -f '${old}/rust/hello.txt' ]]"
    assert_false "new base never created" "[[ -e '${new}' ]]"
    assert_eq    ".env unchanged" "${old}" "$(_env_val "${forge}")"
    assert_true  "the foreign lock was left alone" "[[ -d '${lk}' ]]"
}

test_locks_are_held_during_the_move_and_released_after() {
    test_start "7: the locks of the moving Spokes (and nested ones) are held while folders move, gone afterwards"
    local old="${SANDBOX_ROOT}/l2-old" new="${SANDBOX_ROOT}/l2-new"
    _mk_alias "${old}" python; _mk_alias "${old}" rust
    local forge; forge="$(_make_forge "${old}")"
    _stub "${forge}" mv <<EOF
for n in python jupyterlab rust; do [[ -d "${forge}/.locks/vms/\${n}.lock" ]] && : >> "${forge}/held-during-mv"; print \$n >> "${forge}/held-names" 2>/dev/null; done
exec ${REAL_MV} "\$@"
EOF
    _run_spd "${forge}" "${new}"
    assert_eq    "re-point succeeds" "${VDE_SUCCESS}" "${SPD_RC}"
    assert_true  "a lock existed while a folder was being moved" "[[ -e '${forge}/held-during-mv' ]]"
    local n
    for n in python jupyterlab rust; do
        assert_false "lock for ${n} released after success" "[[ -e '$(_lockfile "${forge}" ${n})' ]]"
    done
}

test_every_spoke_mounting_the_folder_is_locked() {
    test_start "7: moving python locks vde-jupyterlab too (its notebooks live in python/jupyterlabs)"
    local old="${SANDBOX_ROOT}/l3-old" new="${SANDBOX_ROOT}/l3-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    local lk; lk="$(_lockfile "${forge}" jupyterlab)"
    mkdir -p "${lk}"; print -r -- "$$:$$:$(date +%s)" > "${lk}/pid"
    _run_spd "${forge}" "${new}"
    assert_eq    "a busy jupyterlab lock refuses moving python" "${VDE_ERR_LOCK}" "${SPD_RC}"
    assert_true  "python untouched" "[[ -f '${old}/python/hello.txt' ]]"
}

test_locks_released_after_a_refusal() {
    test_start "7: the locks this run took are released even when it refuses (running Spoke)"
    local old="${SANDBOX_ROOT}/l4-old" new="${SANDBOX_ROOT}/l4-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    _stub_docker_running "${forge}" vde-python
    _run_spd "${forge}" "${new}"
    assert_eq    "refused (running Spoke)" "${VDE_ERR_GENERAL}" "${SPD_RC}"
    assert_false "python lock released" "[[ -e '$(_lockfile "${forge}" python)' ]]"
}

test_env_update_failure_is_reported_and_leaves_env_intact() {
    test_start "8: if the .env rewrite fails after the moves, say so, exit non-zero, and keep .env untouched"
    local old="${SANDBOX_ROOT}/z1-old" new="${SANDBOX_ROOT}/z1-new"
    _mk_alias "${old}" python
    local forge; forge="$(_make_forge "${old}")"
    # The rename that would publish the new .env fails (a full disk, an I/O error...).
    _stub "${forge}" mv <<EOF
if (( \${#\${(M)@:#*.env.vde-tmp.*}} )); then exit 1; fi
exec ${REAL_MV} "\$@"
EOF
    _run_spd "${forge}" "${new}"
    assert_eq    "exits VDE_ERR_PERMISSION" "${VDE_ERR_PERMISSION}" "${SPD_RC}"
    assert_has   "tells the student the exact line to set by hand" "Set VDE_PROJECTS_DIR=${new:A}" "${SPD_OUT}"
    assert_eq    ".env still holds its previous (complete) content" "${old}" "$(_env_val "${forge}")"
    assert_eq    "no temp file left behind" "0" "$(ls -A "${forge}" | grep -c '\.env\.vde-tmp')"
}

test_running_spoke_of_moved_alias_blocks
test_running_spoke_of_unmoved_alias_does_not_block
test_held_spoke_lock_blocks_the_repoint
test_locks_are_held_during_the_move_and_released_after
test_every_spoke_mounting_the_folder_is_locked
test_locks_released_after_a_refusal
test_env_update_failure_is_reported_and_leaves_env_intact
test_noop_base_still_warns_about_stale_export
test_running_jupyterlab_blocks_moving_python
test_hung_docker_query_times_out_and_refuses
test_missing_docker_fails_closed
test_hangup_prints_how_to_finish
test_signal_right_after_env_write_reports_post_update
test_signal_right_after_publish_reports_old_copy
test_unremovable_stale_temp_is_refused
test_unwritable_env_dir_refuses_before_moving
test_env_rewrite_is_atomic_and_follows_symlink
test_docker_query_failure_refuses
test_running_match_is_exact
test_spoke_started_during_copy_discards_the_copy
test_docker_unreadable_after_copy_discards_the_copy
test_unwritable_env_refuses_before_moving
test_interrupt_while_removing_old_copy_message
test_crossfs_failed_copy_leaves_source_authoritative
test_crossfs_real_move_completes
test_crossfs_stale_temp_is_discarded
test_crossfs_symlinked_temp_is_refused
test_samefs_move_is_a_plain_rename
test_interrupt_in_move_loop_then_rerun_completes
test_interrupt_in_regen_phase_message
test_warn_helper
test_spd_warns_on_stale_export
test_vde_start_calls_the_helper

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed, $TESTS_SKIPPED skipped"
echo "=============================================="
# A skipped case is an UNVERIFIED safety property (the cross-device cases need a
# second device): fail unless the runner opts in, so a green run never hides one.
if (( TESTS_SKIPPED > 0 && TESTS_FAILED == 0 )) && [[ "${VDE_TEST_ALLOW_SKIP:-0}" != "1" ]]; then
    echo "FAIL: ${TESTS_SKIPPED} case(s) skipped (set VDE_TEST_ALLOW_SKIP=1 to accept on a host without a second device)"
    exit 1
fi
exit $TESTS_FAILED
