#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# githooks/gate-tree.zsh - certifies one tree for the pre-push gate (Signet #770).
#
# Usage: zsh githooks/gate-tree.zsh fast|full
# Run with cwd = the tree to certify (the pre-push gate uses a throwaway worktree). Everything checked
# is read from that tree; VDE_ROOT_DIR is the top level of the tree in cwd.
# The gate's own libraries (lib/vde-test-env, lib/vde-gate-commits) come from the tree that holds this
# script; everything else (audit, Gospel Audit, runner, unit suites, the Proof of Life feature) is the
# commit's own.
#
# Tiers:
#   fast  Sovereign Audit, Gospel Audit, then the unit suites this commit adds or changes, run exactly as
#         the Sovereign runner lists them (its exclusion list applies; a suite that uses docker uses it as
#         its own test does). It never runs the full suite, the Proof of Life or the Spoke smoke matrix.
#   full  Sovereign Audit, Sovereign suite, Proof of Life, Gospel Audit.
#
# Exit codes: 0 pass, 1 audit, 3 suite, 2 Proof of Life, 5 Gospel, 4 could not run.
typeset _ZSH_PURE=${(%):-%x}

# Timing (Signet #774): every run is timed. Each step announces itself with a wall-clock time and, when it
# ends (pass or fail), prints "[gate] <step> finished in <n>.<d>s"; the tier ends with
# "[gate] <tier> tier finished in <n>.<d>s". Durations are differences of vde_test_now (a float, monotonic
# where /proc/uptime exists); the wall-clock time of day comes from EPOCHSECONDS.
zmodload zsh/datetime

# _gate_ts: the wall-clock time, HH:MM:SS.
_gate_ts() { strftime '%H:%M:%S' ${EPOCHSECONDS}; }

# _gate_timed <label> <command...>: runs a step, prints how long it took, returns the step's status.
_gate_timed() {
    local label="$1"
    local -F t0 t1
    local -i rc=0
    t0=$(vde_test_now)
    shift
    "$@" || rc=$?
    t1=$(vde_test_now)
    print -r -- "[gate] ${label} finished in $(vde_test_fmt1 $(( t1 - t0 )))s"
    return ${rc}
}

typeset RED='\033[0;31m'
typeset GREEN='\033[0;32m'
typeset RESET='\033[0m'
typeset _SENTINEL=${(U):-"sentinel active"}

typeset _TIER="${1:-}"
case "${_TIER}" in
    fast|full) ;;
    *) echo -e "${RED}[ERROR] usage: gate-tree.zsh fast|full${RESET}"; exit 4 ;;
esac

typeset VDE_ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "${VDE_ROOT_DIR}" ]]; then
    echo -e "${RED}[ERROR] not inside a git tree. The gate could not run.${RESET}"
    exit 4
fi
export VDE_ROOT_DIR

# The repository-selecting GIT_* variable list lives in one place, lib/vde-gate-commits (_VDE_GATE_SCRUB).
# ${0:A:h:h} is the root holding this script (the pushing tree), not the throwaway tree the gate runs in.
source "${0:A:h:h}/lib/vde-gate-commits" || { echo "[ERROR] cannot load lib/vde-gate-commits"; exit 4; }

# The gate runs against its own scratch Projects base, never the caller's.
source "${0:A:h:h}/lib/vde-test-env" || { echo "[ERROR] cannot load lib/vde-test-env"; exit 4; }
source "${0:A:h:h}/lib/vde-junit-timing" || { echo "[ERROR] cannot load lib/vde-junit-timing"; exit 4; }
vde_test_env_enter || { echo "[ERROR] cannot create a scratch Projects base"; exit 4; }

# The suites run under a throwaway HOME inside the gate's scratch directory, never the caller's HOME.
typeset _GATE_SCRATCH="$(vde_test_env_dir)"
if [[ -z "${_GATE_SCRATCH}" ]]; then
    echo -e "${RED}[ERROR] no scratch directory for the suite. The gate could not run.${RESET}"
    vde_test_env_leave
    exit 4
fi
typeset _GATE_HOME="${_GATE_SCRATCH}/home"
mkdir -p "${_GATE_HOME}" || {
    echo -e "${RED}[ERROR] cannot create the scratch HOME ${_GATE_HOME}. The gate could not run.${RESET}"
    vde_test_env_leave
    exit 4
}

# _gate_scrubbed <command...>: runs a command under the scratch HOME. Git exports GIT_DIR and other
# repository-selecting variables into a hook; the suites build their own throwaway repositories, so with
# those variables set their git commands land in the REAL repository (Signet #656). The variables removed
# are the single list _VDE_GATE_SCRUB, defined in lib/vde-gate-commits.
_gate_scrubbed() {
    env "${_VDE_GATE_SCRUB[@]}" HOME="${_GATE_HOME}" "$@"
}

# _gate_audit: the Sovereign Audit (Rule A). 1 = failed, 4 = could not run.
_gate_audit() {
    echo "[${_SENTINEL}] [$(_gate_ts)] Running Sovereign Audit (Rule A)..."
    if [[ ! -f "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" ]]; then
        echo -e "${RED}[ERROR] bin/vde-enforce-uap.zsh is missing. The gate could not run. Push blocked.${RESET}"
        return 4
    fi
    typeset -i _rc=0
    # The push gate refreshes origin/develop (one best-effort, non-prompting fetch) so the shrink-only baseline check
    # is judged against the real base, not a stale cached ref (Signet #646).
    VDE_SHIB_REFRESH_BASE=1 zsh "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" --quiet || _rc=$?
    if (( _rc == 126 || _rc == 127 )); then
        echo -e "${RED}[ERROR] The Sovereign Audit could not be started (status ${_rc}). The gate could not run. Push blocked.${RESET}"
        return 4
    fi
    if (( _rc != 0 )); then
        echo -e "${RED}[ERROR] Sovereign Audit Failed. Push blocked.${RESET}"
        return 1
    fi
    return 0
}

# _gate_gospel: the Gospel Audit (Phase 32). Skipped when the audit script does not exist. 5 = failed.
_gate_gospel() {
    [[ -f "${VDE_ROOT_DIR}/bin/vde-gospel-audit.zsh" ]] || return 0
    echo "[${_SENTINEL}] [$(_gate_ts)] Running Gospel Audit (Phase 32)..."
    if ! zsh -e "${VDE_ROOT_DIR}/bin/vde-gospel-audit.zsh" --quiet; then
        echo -e "${RED}[ERROR] Pre-Push Blockade (Gospel Drift):${RESET}"
        echo -e "  The Gospel has drifted from the physical implementation."
        echo -e "  Run 'bin/vde-heal-docs.zsh' to restore synchronization."
        return 5
    fi
    return 0
}

# _gate_full_suite: the Sovereign suite (tests/run-sovereign-tests.zsh). 3 = failed or missing, 4 = could not start.
_gate_full_suite() {
    if [[ ! -f "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" ]]; then
        echo -e "${RED}[ERROR] tests/run-sovereign-tests.zsh is missing. Push blocked.${RESET}"
        return 3
    fi
    echo "[${_SENTINEL}] [$(_gate_ts)] Running the Sovereign suite (tests/run-sovereign-tests.zsh)..."
    typeset -i _rc=0
    _gate_scrubbed zsh "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" || _rc=$?
    if (( _rc == 126 || _rc == 127 )); then
        echo -e "${RED}[ERROR] The Sovereign suite runner could not be started (status ${_rc}). The gate could not run. Push blocked.${RESET}"
        return 4
    fi
    if (( _rc != 0 )); then
        echo -e "${RED}[ERROR] Sovereign suite failed. Push blocked.${RESET}"
        echo -e "  The failing suite is named above. Run 'zsh tests/run-sovereign-tests.zsh' for details."
        return 3
    fi
    return 0
}

# _gate_behave: the Proof of Life (Mandate L). 4 = behave unavailable, 2 = the contract failed.
_gate_behave() {
    echo "[${_SENTINEL}] [$(_gate_ts)] Running Proof of Life (Mandate L) Validation..."
    echo "[${_SENTINEL}] Feature: tests/features/core-infrastructure/proof-of-life-the-contract.feature"
    if ! python3 -c 'import behave' >/dev/null 2>&1; then
        echo -e "${RED}[ERROR] python3 with behave is unavailable. The gate could not run. Push blocked.${RESET}"
        return 4
    fi
    # Per-scenario timing (Signet #774): behave writes its JUnit XML into a scratch directory, which is
    # reported after the run (pass or fail) and removed. The behave status is kept for the return value.
    typeset _junit_base _junit_dir
    typeset -i _behave_rc=0
    _junit_base="$(vde_test_env_dir)"
    [[ -n "${_junit_base}" ]] || _junit_base="${TMPDIR:-/tmp}"
    _junit_dir="$(mktemp -d "${_junit_base}/pol-junit.XXXXXX")" || {
        echo -e "${RED}[ERROR] cannot create the JUnit directory for the timing report. The gate could not run. Push blocked.${RESET}"
        return 4
    }
    python3 -m behave "${VDE_ROOT_DIR}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" --quiet --no-summary --junit --junit-directory "${_junit_dir}" || _behave_rc=$?
    # The gate shows every scenario, not just the library's default top 10.
    vde_junit_timing_report "${_junit_dir}" 100000
    rm -rf -- "${_junit_dir}"
    if (( _behave_rc != 0 )); then
        echo -e "${RED}[ERROR] Mandate L Violation: Proof of Life Contract Failed.${RESET}"
        echo -e "  The core VM lifecycle is broken. Push blocked."
        echo -e "  Run 'python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature' for details."
        return 2
    fi
    return 0
}

# _gate_changed_suites: prints the basenames of the tests/unit/*.test.zsh files this commit adds or changes.
# A merge commit is compared against its first parent (git diff-tree alone lists nothing for a merge).
_gate_changed_suites() {
    typeset _diff _f
    if git rev-parse --verify --quiet 'HEAD^2' >/dev/null; then
        _diff="$(git diff --name-only --no-renames --diff-filter=AM HEAD^1 HEAD)" || return 4
    else
        _diff="$(git diff-tree --no-commit-id --name-only -r --no-renames --diff-filter=AM --root HEAD)" || return 4
    fi
    for _f in "${(@f)_diff}"; do
        [[ "${_f:h}" == tests/unit && "${_f:t}" == *.test.zsh ]] && print -r -- "${_f:t}"
    done
    return 0
}

# _gate_runnable_suites: prints the suites the Sovereign runner marks "run" (its --list plan).
_gate_runnable_suites() {
    typeset _plan _line
    typeset -a _words
    _plan="$(_gate_scrubbed zsh "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" --list 2>&1)" || return 4
    for _line in "${(@f)_plan}"; do
        _words=( ${(z)_line} )
        [[ "${_words[1]}" == run ]] && print -r -- "${_words[2]}"
    done
    return 0
}

# _gate_run_suite <name>: runs one unit suite. 3 = failed (named), 4 = could not start.
_gate_run_suite() {
    typeset -i _rc=0
    echo "[${_SENTINEL}] [$(_gate_ts)] Running unit suite ${1}..."
    _gate_scrubbed zsh "${VDE_ROOT_DIR}/tests/unit/${1}" || _rc=$?
    if (( _rc == 126 || _rc == 127 )); then
        echo -e "${RED}[ERROR] Unit suite ${1} could not be started (status ${_rc}). The gate could not run. Push blocked.${RESET}"
        return 4
    fi
    if (( _rc != 0 )); then
        echo -e "${RED}[ERROR] Unit suite ${1} failed. Push blocked.${RESET}"
        return 3
    fi
    return 0
}

# _gate_fast_suites: runs the unit suites this commit adds or changes, as the Sovereign runner plans them.
_gate_fast_suites() {
    typeset _changed_out _runnable_out _s
    typeset -a _changed _runnable _to_run
    _changed_out="$(_gate_changed_suites)" || {
        echo -e "${RED}[ERROR] cannot list the commit's changed files. The gate could not run. Push blocked.${RESET}"
        return 4
    }
    _changed=( ${(f)_changed_out} )
    if (( ${#_changed} )); then
        if [[ ! -f "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" ]]; then
            echo -e "${RED}[ERROR] tests/run-sovereign-tests.zsh is missing. Push blocked.${RESET}"
            return 3
        fi
        _runnable_out="$(_gate_runnable_suites)" || {
            echo -e "${RED}[ERROR] the Sovereign suite runner could not list its suites. The gate could not run. Push blocked.${RESET}"
            return 4
        }
        _runnable=( ${(f)_runnable_out} )
    fi
    for _s in "${_changed[@]}"; do
        (( ${_runnable[(Ie)${_s}]} )) && _to_run+=( "${_s}" )
    done
    echo "fast check: ${#_to_run} changed unit suite(s)"
    for _s in "${_to_run[@]}"; do
        _gate_timed "unit suite ${_s}" _gate_run_suite "${_s}" || return $?
    done
    return 0
}

# main: the steps of the chosen tier, stopping at the first failure. Returns that step's exit code.
main() {
    _gate_timed "Sovereign Audit" _gate_audit || return $?
    if [[ "${_TIER}" == full ]]; then
        _gate_timed "Sovereign suite" _gate_full_suite || return $?
        _gate_timed "Proof of Life" _gate_behave || return $?
        _gate_timed "Gospel Audit" _gate_gospel || return $?
    else
        _gate_timed "Gospel Audit" _gate_gospel || return $?
        _gate_timed "unit suites" _gate_fast_suites || return $?
    fi
    return 0
}

typeset -i _gate_rc=0
typeset -F _gate_t0 _gate_t1
_gate_t0=$(vde_test_now)
main "$@" || _gate_rc=$?
_gate_t1=$(vde_test_now)
print -r -- "[gate] ${_TIER} tier finished in $(vde_test_fmt1 $(( _gate_t1 - _gate_t0 )))s"
vde_test_env_leave
exit ${_gate_rc}
