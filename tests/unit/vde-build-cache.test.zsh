#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests for the Docker build-cache cleanup (Signet #617).
#
# A --no-cache rebuild round left 38 GB of BuildKit cache behind and filled a
# disk to 99%. VDE now prunes the build cache after a successful rebuild/create
# (--keep-cache opts out) and offers `vde clean` for the cases the automatic
# prune cannot cover. These tests pin, with a stub `docker` that records every
# call:
#   1. the ONLY destructive call is `builder prune --all -f` (never images,
#      containers, volumes or `system prune`)
#   2. dry-run, empty cache, failure, keep-cache and docker-missing behaviour
#   3. the flags, the router (`clean`, `cleanup`, `cache clean`), the
#      did-you-mean hints, the low-disk hint and the corrected error text
# No real Docker daemon is touched.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }
trap 'rm -rf -- "${SCRATCH}"' EXIT

# --- a stub docker on PATH: records every call, answers the three we use -------
mkdir -p "${SCRATCH}/bin"
cat > "${SCRATCH}/bin/docker" <<'STUB'
#!/usr/bin/env zsh
print -r -- "$*" >> "${STUB_CALLS:-/dev/null}"
case "$1" in
    info)    [[ "$2" == --format* ]] && print -r -- "${STUB_ROOT:-}"; exit ${STUB_INFO_RC:-0} ;;
    context)
        case "$2" in
            show)    print -r -- "${STUB_CONTEXT:-default}" ;;
            inspect) print -r -- "${STUB_CTX_HOST:-unix:///var/run/docker.sock}" ;;
        esac
        ;;
    system)
        (( ${STUB_DF_RC:-0} )) && exit ${STUB_DF_RC}
        print -r -- "Images|1GB"; print -r -- "Build Cache|${STUB_CACHE_SIZE:-4.855GB}"
        ;;
    builder)
        if (( ${STUB_PRUNE_RC:-0} )); then print -u2 -r -- "boom: cannot prune"; exit ${STUB_PRUNE_RC}; fi
        print -r -- "Deleted build cache objects:"; print -r -- "abc123"; print -r -- ""
        print -r -- "Total:	${STUB_PRUNE_TOTAL:-${STUB_CACHE_SIZE:-4.855GB}}"
        ;;
esac
STUB
chmod +x "${SCRATCH}/bin/docker"

typeset -gx STUB_CALLS="${SCRATCH}/calls"
export PATH="${SCRATCH}/bin:${PATH}"
reset_stub() { : > "${STUB_CALLS}"; unset STUB_PRUNE_RC STUB_CACHE_SIZE STUB_CONTEXT STUB_CTX_HOST STUB_DF_RC STUB_INFO_RC STUB_ROOT STUB_PRUNE_TOTAL DOCKER_HOST VDE_QUIET VDE_DISK_HINT_THRESHOLD; }
calls() { <"${STUB_CALLS}"; }

# --- the library under test (absent until the change lands) -------------------
if [[ -f "${VDE_ROOT_DIR}/lib/vde-build-cache" ]]; then
    source "${VDE_ROOT_DIR}/lib/vde-build-cache"
fi
if ! typeset -f vde_prune_build_cache >/dev/null; then
    test_start "lib/vde-build-cache defines vde_prune_build_cache"
    test_fail "vde_prune_build_cache is not defined" "lib/vde-build-cache missing or empty"
    echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
    exit 1
fi

typeset out rc

#-------------------------------------------------------------------------------
test_start "prune: runs exactly 'builder prune --all -f', reports what it freed, returns 0"
reset_stub
out=$(vde_prune_build_cache 2>&1); rc=$?
if [[ $rc -eq 0 && "$(calls)" == *"builder prune --all -f"* && "${out}" == *"Freed 4.855GB of"* && "${out}" != *$'\t'* ]]; then
    test_pass "pruned, and said how much, with no stray whitespace"
else
    test_fail "prune" "rc=${rc} calls=$(calls) out=$(print -r -- "${out}" | cat -A)"
fi

#-------------------------------------------------------------------------------
test_start "a prune that frees 0B says the cache is in use by a running build, not 'Freed 0B'"
reset_stub
# Measured on a real daemon (2026-11-17): `docker builder prune` during a running
# build reported "Total: 0B" because BuildKit skips cache records in use. The stub
# reproduces that: a non-empty cache whose prune frees nothing.
out=$(STUB_PRUNE_TOTAL=0B vde_prune_build_cache 2>&1); rc=$?
if [[ $rc -eq 0 && "${out}" == *"in use by a running build"* && "${out}" != *"Freed"* ]]; then
    test_pass "honest message"
else
    test_fail "in-use prune" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "prune: NEVER touches images, containers, volumes or 'system prune'"
reset_stub
vde_prune_build_cache >/dev/null 2>&1
vde_prune_build_cache --dry-run >/dev/null 2>&1
if [[ "$(calls)" =~ '(image|container|volume|system prune|rmi|[[:space:]]rm[[:space:]])' ]]; then
    test_fail "destructive scope" "forbidden docker call recorded: $(calls)"
else
    test_pass "only context/system df/builder prune were called"
fi

#-------------------------------------------------------------------------------
test_start "dry-run: removes nothing, reports the size it would free"
reset_stub
out=$(vde_prune_build_cache --dry-run 2>&1); rc=$?
if [[ $rc -eq 0 && "$(calls)" != *"builder prune"* && "${out}" == *"4.855GB"* && "${out}" == *"dry run"* ]]; then
    test_pass "no prune call; size reported"
else
    test_fail "dry-run" "rc=${rc} calls=$(calls) out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "an empty cache: the dry run says 'already empty'; a real run says there is nothing to free"
reset_stub; export STUB_CACHE_SIZE=0B
out=$(vde_prune_build_cache --dry-run 2>&1); rc=$?
typeset real_out; real_out=$(STUB_PRUNE_TOTAL=0B vde_prune_build_cache 2>&1)
if [[ $rc -eq 0 && "${out}" == *"already empty"* && "${real_out}" == *"Nothing to free"* && "${real_out}" != *"Freed"* ]]; then
    test_pass "both honest, neither says 'Freed 0B'"
else
    test_fail "empty cache" "rc=${rc} dry=${out} real=${real_out}"
fi

#-------------------------------------------------------------------------------
test_start "the automatic path does NOT run 'docker system df' (it walks every image/container/volume)"
reset_stub
vde_prune_build_cache >/dev/null 2>&1
[[ "$(calls)" != *"system df"* ]] && test_pass "size is read only for --dry-run" || test_fail "system df" "$(calls)"

#-------------------------------------------------------------------------------
test_start "quiet mode (-q) silences the informational lines but not errors"
reset_stub
out=$(VDE_QUIET=1 vde_prune_build_cache --dry-run 2>&1)
typeset qerr; qerr=$(VDE_QUIET=1 STUB_INFO_RC=1 vde_prune_build_cache 2>&1)
if [[ -z "${out}" && "${qerr}" == *"daemon is not running"* ]]; then
    test_pass "quiet output empty; errors still shown"
else
    test_fail "quiet" "out='${out}' err='${qerr}'"
fi

#-------------------------------------------------------------------------------
test_start "low-disk hint: fires AT the real usage of Docker's data root, and stays silent just above it (a healthy disk)"
# Control the input: measure the real usage of the stub's data root, then bracket it.
# usage_now is what df reports for ${SCRATCH}; the threshold is set to exactly that
# (must fire) and to 2 above it (must be silent). A hint emitted at every ordinary
# threshold would fail the second half.
reset_stub; export STUB_ROOT="${SCRATCH}"
typeset -a _rows=( "${(@f)$(df -P -- "${SCRATCH}")}" ) _f
_f=( ${=_rows[2]} ); typeset usage_now="${_f[5]%\%}"
out=$(VDE_DISK_HINT_THRESHOLD=${usage_now} vde_build_low_disk_hint 2>&1); rc=$?
typeset healthy_out; healthy_out=$(VDE_DISK_HINT_THRESHOLD=$(( usage_now + 2 )) vde_build_low_disk_hint 2>&1)
if [[ $rc -eq 0 && "${out}" == *"vde clean"* && -z "${healthy_out}" ]]; then
    test_pass "hint at ${usage_now}% (threshold ${usage_now}), silent at threshold $(( usage_now + 2 ))"
else
    test_fail "low-disk hint" "usage=${usage_now} rc=${rc} fires='${out}' healthy='${healthy_out}'"
fi

test_start "low-disk hint: stays silent for a REMOTE daemon set by DOCKER_HOST"
reset_stub; export STUB_ROOT="${SCRATCH}" DOCKER_HOST=ssh://build.example
out=$(VDE_DISK_HINT_THRESHOLD=0 vde_build_low_disk_hint 2>&1); rc=$?
[[ $rc -eq 0 && -z "${out}" ]] && test_pass "silent for ssh://" || test_fail "remote daemon" "rc=${rc} out=${out}"

test_start "low-disk hint: stays silent for a REMOTE daemon set by the active Docker context (DOCKER_HOST unset)"
reset_stub; export STUB_ROOT="${SCRATCH}" STUB_CTX_HOST=tcp://build.example:2376
out=$(VDE_DISK_HINT_THRESHOLD=0 vde_build_low_disk_hint 2>&1); rc=$?
[[ $rc -eq 0 && -z "${out}" ]] && test_pass "silent for a remote context" || test_fail "remote context" "rc=${rc} out=${out}"

test_start "low-disk hint: stays silent when Docker's data root is not visible on this host (Docker Desktop VM), never measuring / instead"
reset_stub; export STUB_ROOT=/definitely/not/a/path
out=$(VDE_DISK_HINT_THRESHOLD=0 vde_build_low_disk_hint 2>&1); rc=$?
[[ $rc -eq 0 && -z "${out}" ]] && test_pass "silent: no wrong-disk hint" || test_fail "invisible root" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "a misspelled option is REFUSED and never read as 'do the real prune'"
reset_stub
out=$(vde_prune_build_cache --dry-rnu 2>&1); rc=$?
typeset out2; out2=$(vde_prune_build_cache --dry-run extra 2>&1); typeset rc2=$?
typeset out3; out3=$(vde_prune_build_cache "" 2>&1); typeset rc3=$?
if [[ $rc -eq 2 && $rc2 -eq 2 && $rc3 -eq 2 && "$(calls)" != *"builder prune"* && "${out}" == *"unknown option"* ]]; then
    test_pass "rc 2 for a typo, extra args and an explicit empty string; nothing pruned"
else
    test_fail "option typo" "rc=${rc}/${rc2}/${rc3} calls=$(calls) out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "a dry run that cannot read the size FAILS (rc 1), visibly, even under -q"
reset_stub; export STUB_DF_RC=1
out=$(VDE_QUIET=1 vde_prune_build_cache --dry-run 2>&1); rc=$?
[[ $rc -eq 1 && "${out}" == *"Could not read the build cache size"* ]] && test_pass "rc 1, warned despite -q" || test_fail "unreadable size" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "the Docker context being cleaned is printed (never silently prune a remote daemon)"
reset_stub; export STUB_CONTEXT=remote-builder DOCKER_HOST=ssh://build.example
out=$(vde_prune_build_cache --dry-run 2>&1)
if [[ "${out}" == *"remote-builder"* && "${out}" == *"ssh://build.example"* ]]; then
    test_pass "context and DOCKER_HOST named"
else
    test_fail "context" "${out}"
fi

#-------------------------------------------------------------------------------
test_start "a failing prune returns non-zero (manual command) with the daemon's message"
reset_stub; export STUB_PRUNE_RC=1
out=$(vde_prune_build_cache 2>&1); rc=$?
if [[ $rc -ne 0 && "${out}" == *"boom: cannot prune"* ]]; then
    test_pass "non-zero, cause shown"
else
    test_fail "failing prune" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "the AUTOMATIC prune never fails the build: a prune failure only warns"
reset_stub; export STUB_PRUNE_RC=1
out=$(vde_maybe_prune_build_cache false 2>&1); rc=$?
if [[ $rc -eq 0 && "${out}" == *"boom: cannot prune"* ]]; then
    test_pass "rc 0, warned"
else
    test_fail "auto prune failure" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "--keep-cache: no prune, and the message names 'vde clean'"
reset_stub
out=$(vde_maybe_prune_build_cache true 2>&1); rc=$?
if [[ $rc -eq 0 && "$(calls)" != *"builder prune"* && "${out}" == *"vde clean"* ]]; then
    test_pass "kept, and says how to free it later"
else
    test_fail "keep-cache" "rc=${rc} calls=$(calls) out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "automatic prune (default): prunes once"
reset_stub
vde_maybe_prune_build_cache false >/dev/null 2>&1
typeset n; n=$(grep -c 'builder prune' "${STUB_CALLS}")
[[ "${n}" == "1" ]] && test_pass "one prune call" || test_fail "auto prune" "prune calls=${n}"

#-------------------------------------------------------------------------------
test_start "docker not installed: a clear message and a distinct status, not a crash"
reset_stub
out=$( PATH=/nonexistent; vde_prune_build_cache 2>&1 ); rc=$?
[[ $rc -eq 3 && "${out}" == *"Docker is not installed"* ]] && test_pass "rc 3, clear message" || test_fail "no docker" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "a stopped daemon is reported as such, never as an 'already empty' cache"
reset_stub; export STUB_INFO_RC=1
out=$(vde_prune_build_cache 2>&1); rc=$?
if [[ $rc -eq 1 && "${out}" == *"daemon is not running"* && "${out}" != *"already empty"* && "$(calls)" != *"builder prune"* ]]; then
    test_pass "rc 1, daemon named, no prune attempted"
else
    test_fail "daemon down" "rc=${rc} calls=$(calls) out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "clean flags: --dry-run / -n are consumed, an unknown flag is rejected"
vde_split_clean_args --dry-run; rc=$?
[[ $rc -eq 0 && "${VDE_CLEAN_DRY_RUN}" == "1" && ${#VDE_CLEAN_REST} -eq 0 ]] && test_pass "--dry-run" || test_fail "--dry-run" "rc=${rc} dry=${VDE_CLEAN_DRY_RUN} rest=${VDE_CLEAN_REST[*]}"
vde_split_clean_args -n; [[ "${VDE_CLEAN_DRY_RUN}" == "1" ]] && test_pass "-n" || test_fail "-n" "dry=${VDE_CLEAN_DRY_RUN}"
vde_split_clean_args --bogus 2>/dev/null; rc=$?
[[ $rc -eq 2 ]] && test_pass "unknown flag -> 2" || test_fail "unknown flag" "rc=${rc}"
vde_split_clean_args -q --dry-run; rc=$?
[[ $rc -eq 0 && "${VDE_CLEAN_DRY_RUN}" == "1" && "${VDE_CLEAN_REST[*]}" == "-q" ]] && test_pass "-q is handed on to the router, not rejected" || test_fail "-q" "rc=${rc} rest=${VDE_CLEAN_REST[*]}"

#-------------------------------------------------------------------------------
# Rebuild flag plumbing
source "${VDE_ROOT_DIR}/lib/vde-shell-compat"
source "${VDE_ROOT_DIR}/lib/vde-constants"
source "${VDE_ROOT_DIR}/lib/vde-core"

test_start "vde_split_rebuild_args forwards --keep-cache as a flag, never as a target"
vde_split_rebuild_args --keep-cache python base; rc=$?
if [[ $rc -eq 0 && "${VDE_REBUILD_FLAGS[*]}" == "--keep-cache" && "${VDE_REBUILD_REST[*]}" == "python base" ]]; then
    test_pass "flag peeled off"
else
    test_fail "--keep-cache split" "flags='${VDE_REBUILD_FLAGS[*]}' rest='${VDE_REBUILD_REST[*]}'"
fi

#-------------------------------------------------------------------------------
# Wiring pins: EXECUTABLE lines only, so a comment cannot satisfy them.
exec_lines() { grep -nvE '^[[:space:]]*(#|$)' "$1" }
first_line_no() { local hit; hit=$(exec_lines "$1" | grep -m1 -- "$2") || return 1; print -r -- "${hit%%:*}" }
fn_body() {
    local line in_fn=0
    for line in "${(@f)$(<"$1")}"; do
        if (( ! in_fn )); then [[ "${line}" == "$2() {"* ]] && in_fn=1; continue; fi
        [[ "${line}" == "}" ]] && break
        [[ "${line}" =~ '^[[:space:]]*(#|$)' ]] || print -r -- "${line}"
    done
}
typeset REB="${VDE_ROOT_DIR}/bin/vde-rebuild"

test_start "wiring: vde-rebuild parses --keep-cache and sources the build-cache library"
if exec_lines "${REB}" | grep -q -- '--keep-cache)' \
    && exec_lines "${REB}" | grep -q 'KEEP_CACHE=true' \
    && exec_lines "${REB}" | grep -q 'lib/vde-build-cache'; then
    test_pass "flag, variable and source present"
else
    test_fail "vde-rebuild wiring" "missing --keep-cache parsing or the lib source"
fi

test_start "wiring: vde-rebuild prunes ONLY after every build has run (set -e keeps the cache on failure)"
typeset last_build loop_done prune_line
last_build=$(first_line_no "${REB}" 'build_vm_image "\${spoke}"')
# The prune must come after the `done` that CLOSES the spoke loop, not merely after the
# first build: pruning inside the loop would discard the cache a later failing build keeps.
loop_done=""
typeset _row
for _row in "${(@f)$(exec_lines "${REB}")}"; do
    if (( ${_row%%:*} > last_build )) && [[ "${_row#*:}" == "done" ]]; then loop_done="${_row%%:*}"; break; fi
done
prune_line=$(first_line_no "${REB}" 'vde_maybe_prune_build_cache')
if [[ -n "${last_build}" && -n "${loop_done}" && -n "${prune_line}" && ${last_build} -lt ${loop_done} && ${loop_done} -lt ${prune_line} ]] \
    && exec_lines "${REB}" | grep -q '^[0-9]*:set -e'; then
    test_pass "builds (${last_build}) < end of spoke loop (${loop_done}) < prune (${prune_line}), under set -e"
else
    test_fail "prune placement" "builds='${last_build}' loop_done='${loop_done}' prune='${prune_line}'"
fi

test_start "behaviour: vde-rebuild --keep-cache is consumed by the option loop (a branch without shift would hang)"
# Run the real option loop: a --keep-cache branch that forgets `shift` spins forever,
# which the timeout turns into a non-zero status. --help exits right after parsing.
out=$(timeout 30 zsh "${REB}" --keep-cache --help 2>&1); rc=$?
if [[ $rc -eq 0 && "${out}" == *"--keep-cache"* && "${out}" == *"Usage: vde-rebuild"* ]]; then
    test_pass "parsed and exited (rc 0)"
else
    test_fail "--keep-cache parse loop" "rc=${rc} (124 = hung) out=${out}"
fi

test_start "wiring: both failure branches print the low-disk hint"
# The hint must sit in the FAILURE branch: after the line that reports the failure and
# before that branch returns. Present somewhere in the function is not enough.
typeset fn_name branch_ok=1
for fn_name in build_base_image build_vm_image; do
    typeset body; body="$(fn_body "${REB}" ${fn_name})"
    typeset after_fail="${body#*Failed to }"          # text after the failure echo
    if [[ "${body}" != *"Failed to "* || "${after_fail}" != *"vde_build_low_disk_hint"* ]]; then
        branch_ok=0
        test_fail "hint placement" "${fn_name}: vde_build_low_disk_hint is not after the 'Failed to ...' line"
    elif [[ "${after_fail%%vde_build_low_disk_hint*}" == *"return"* ]]; then
        branch_ok=0
        test_fail "hint placement" "${fn_name}: the failure branch returns before the hint"
    fi
done
(( branch_ok )) && test_pass "both functions print the hint after the failure message and before returning"

test_start "the disk-full error recommends 'vde clean', not 'docker image prune -a'"
typeset errbody
errbody=$(sed -n '/^vde_error_insufficient_disk/,/^}/p' "${VDE_ROOT_DIR}/lib/vde-errors")
if [[ "${errbody}" == *"vde clean"* && "${errbody}" != *"image prune -a"* ]]; then
    test_pass "names vde clean; the image-deleting command is gone"
else
    test_fail "error text" "${errbody}"
fi

#-------------------------------------------------------------------------------
# Router behaviour (real bin/vde, stub docker on PATH)
typeset rc so_text se_text
typeset _err_file="${SCRATCH}/err"
run_vde() { reset_stub; so_text="$(zsh "${VDE_ROOT_DIR}/bin/vde" "$@" 2>"${_err_file}")"; rc=$?; se_text="$(<"${_err_file}")"; }

for cmd in "clean --dry-run" "cleanup --dry-run" "cache clean --dry-run" "cache cleanup --dry-run"; do
    test_start "router: 'vde ${cmd}' reports the build cache and removes nothing"
    run_vde ${=cmd}
    if (( rc == 0 )) && [[ "${so_text}${se_text}" == *"4.855GB"* && "$(calls)" != *"builder prune"* ]]; then
        test_pass "exit 0, size reported, no prune"
    else
        test_fail "vde ${cmd}" "rc=${rc} so=${so_text} se=${se_text} calls=$(calls)"
    fi
done

test_start "router: 'vde clean' (no flag) prunes the build cache and nothing else"
run_vde clean
if (( rc == 0 )) && [[ "$(calls)" == *"builder prune --all -f"* && ! "$(calls)" =~ '(image|container|volume|system prune)' ]]; then
    test_pass "pruned, scope limited"
else
    test_fail "vde clean" "rc=${rc} se=${se_text} calls=$(calls)"
fi

test_start "router: 'vde clean python' rejects the stray argument and prunes nothing"
run_vde clean python
if (( rc == 2 )) && [[ "${se_text}" == *"takes no arguments"* && "$(calls)" != *"builder prune"* ]]; then
    test_pass "exit 2, nothing pruned"
else
    test_fail "vde clean python" "rc=${rc} se=${se_text} calls=$(calls)"
fi

test_start "router: 'vde clean -q' is accepted (the router's own quiet flag) and prints nothing"
run_vde clean -q --dry-run
if (( rc == 0 )) && [[ "${so_text}" != *"4.855GB"* ]]; then
    test_pass "exit 0, quiet"
else
    test_fail "vde clean -q" "rc=${rc} so=${so_text} se=${se_text}"
fi

test_start "router: 'vde cache' alone is a usage error (2) that names the right command"
run_vde cache
if (( rc == 2 )) && [[ "${se_text}" == *"vde clean"* ]]; then
    test_pass "exit 2, points at vde clean"
else
    test_fail "vde cache" "rc=${rc} se=${se_text}"
fi

for guess in disk df space free gc clear-cache; do
    test_start "did-you-mean: 'vde ${guess}' points at 'vde clean' and still exits 2"
    run_vde ${guess}
    if (( rc == 2 )) && [[ "${se_text}" == *"Unknown command '${guess}'"* && "${se_text}" == *"vde clean"* ]]; then
        test_pass "hint shown"
    else
        test_fail "vde ${guess}" "rc=${rc} se=${se_text}"
    fi
done

test_start "did-you-mean: 'vde build python' points at 'vde rebuild'"
run_vde build python
if (( rc == 2 )) && [[ "${se_text}" == *"vde rebuild"* ]]; then
    test_pass "hint shown"
else
    test_fail "vde build" "rc=${rc} se=${se_text}"
fi

test_start "did-you-mean: an unrelated unknown command gets NO suggestion"
run_vde definitely-not-a-command
if (( rc == 2 )) && [[ "${se_text}" == *"Unknown command 'definitely-not-a-command'"* && "${se_text}" != *"Did you mean"* ]]; then
    test_pass "no false hint"
else
    test_fail "no suggestion" "rc=${rc} se=${se_text}"
fi

test_start "help lists vde clean and the --keep-cache flag"
run_vde help
if [[ "${so_text}" == *"clean"* && "${so_text}" == *"--keep-cache"* ]]; then
    test_pass "both documented in vde help"
else
    test_fail "help" "clean/--keep-cache missing from vde help"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
