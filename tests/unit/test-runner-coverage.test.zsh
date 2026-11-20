#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for the Sovereign Test Runner's suite discovery (Signet #630).
#
# CI's "Sovereign Tests" job runs tests/run-sovereign-tests.zsh. It used to run an EXPLICIT list of
# unit suites, so a suite nobody added to the list never ran in CI (9 of 44 at the time of the
# Signet) and a regression in it went unnoticed. The runner now DISCOVERS tests/unit/*.test.zsh and
# takes its only exclusions from tests/ci-unit-exclusions.txt, where every entry carries a reason.
# `--list` prints what the runner would do and exits BEFORE the audit and before running anything:
#   run  <suite>
#   skip <suite> :: <reason>
# Anything inconsistent (an exclusion with no reason, an exclusion naming a suite that does not
# exist) is an error with exit status 1.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset RUNNER_SRC="${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh"
if [[ ! -f "${RUNNER_SRC}" ]]; then
    echo "FATAL: tests/run-sovereign-tests.zsh missing"
    exit 1
fi

typeset TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
# not ((x++)): that returns 1 when x was 0 and would trip the `&& pass || fail` pattern
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT

typeset -g OUT='' RC=0

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

make_root() {  # make_root NAME SUITE... -> a fake repo root holding the REAL runner and the named suites; prints its path
    local r="${TMP_ROOT}/$1" s; shift
    mkdir -p "${r}/tests/unit" "${r}/bin"
    cp "${RUNNER_SRC}" "${r}/tests/run-sovereign-tests.zsh"
    for s in "$@"; do
        # every fixture suite leaves a marker when it is EXECUTED, so "--list never runs anything" is observable
        printf '#!/usr/bin/env zsh\ntouch "%s/ran-%s"\nexit 0\n' "${r}" "${s%.test.zsh}" > "${r}/tests/unit/${s}"
    done
    print -r -- "${r}"
}

list_in() {  # list_in ROOT -> sets OUT and RC from `--list`; a runner without --list would start the audit, so it is capped
    local raw
    raw="$(cd "$1" && timeout 15 zsh tests/run-sovereign-tests.zsh --list 2>&1; print -r -- "LISTRC=$?")"
    RC="${raw##*LISTRC=}"
    OUT="${raw%LISTRC=*}"
}

# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

test_case1_list_mode_is_cheap_and_runs_nothing() {
    test_start "1: --list prints the plan and exits before the audit and before running any suite"
    local r; r="$(make_root c1 alpha.test.zsh beta.test.zsh)"
    list_in "${r}"
    [[ "${RC}" == 0 ]] \
        && test_pass "case1a --list exits 0 in a root with no bin/vde-enforce-uap.zsh (so it never reached the audit)" \
        || test_fail "case1a --list exits 0 in a root with no bin/vde-enforce-uap.zsh (so it never reached the audit)" "rc=${RC} out: ${OUT[1,300]}"
    [[ ! -e "${r}/ran-alpha" && ! -e "${r}/ran-beta" ]] \
        && test_pass "case1b --list executed no suite" \
        || test_fail "case1b --list executed no suite" "a fixture suite left its marker"
    [[ "${OUT}" == *$'run  alpha.test.zsh'* && "${OUT}" == *$'run  beta.test.zsh'* ]] \
        && test_pass "case1c each discovered suite is reported as 'run  <suite>'" \
        || test_fail "case1c each discovered suite is reported as 'run  <suite>'" "out: ${OUT[1,300]}"
}

test_case2_a_new_suite_is_discovered_without_touching_the_runner() {
    test_start "2: a suite added to tests/unit/ is discovered with no edit to the runner; files that are not suites are ignored"
    local r; r="$(make_root c2 alpha.test.zsh)"
    printf '#!/usr/bin/env zsh\nexit 0\n' > "${r}/tests/unit/gamma.test.zsh"
    printf '# a helper, not a suite\n' > "${r}/tests/unit/helper.zsh"
    printf 'notes\n' > "${r}/tests/unit/README.md"
    list_in "${r}"
    [[ "${OUT}" == *$'run  gamma.test.zsh'* ]] \
        && test_pass "case2a the new suite is listed" \
        || test_fail "case2a the new suite is listed" "out: ${OUT[1,300]}"
    [[ "${OUT}" != *helper.zsh* && "${OUT}" != *README* ]] \
        && test_pass "case2b a helper and a README are not suites" \
        || test_fail "case2b a helper and a README are not suites" "out: ${OUT[1,300]}"
}

test_case3_exclusions_need_a_reason_and_must_name_a_real_suite() {
    test_start "3: tests/ci-unit-exclusions.txt: an entry is skipped WITH its reason; no reason or a missing suite is an error"
    local r
    r="$(make_root c3a alpha.test.zsh beta.test.zsh)"
    printf '# comment line\n\nbeta.test.zsh   needs a docker daemon, which the CI job does not have\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 0 && "${OUT}" == *$'skip beta.test.zsh :: needs a docker daemon, which the CI job does not have'* && "${OUT}" == *$'run  alpha.test.zsh'* && "${OUT}" != *$'run  beta.test.zsh'* ]] \
        && test_pass "case3a an excluded suite is skipped with its reason and the others still run" \
        || test_fail "case3a an excluded suite is skipped with its reason and the others still run" "rc=${RC} out: ${OUT[1,300]}"
    r="$(make_root c3b alpha.test.zsh)"
    printf 'alpha.test.zsh\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 1 && "${OUT}" == *"alpha.test.zsh"*"no reason"* ]] \
        && test_pass "case3b an exclusion without a reason fails the runner" \
        || test_fail "case3b an exclusion without a reason fails the runner" "rc=${RC} out: ${OUT[1,300]}"
    r="$(make_root c3c alpha.test.zsh)"
    printf 'ghost.test.zsh   this suite was deleted long ago\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 1 && "${OUT}" == *"ghost.test.zsh"*"stale exclusion"* ]] \
        && test_pass "case3c an exclusion naming a suite that does not exist fails the runner" \
        || test_fail "case3c an exclusion naming a suite that does not exist fails the runner" "rc=${RC} out: ${OUT[1,300]}"
}

test_case3_more_validation_comment_markers_non_suites_and_duplicates() {
    test_start "3 (more): a reason may not be a comment marker, an exclusion must name a *.test.zsh suite, and a suite may be listed only once"
    local r
    r="$(make_root c3d alpha.test.zsh)"
    printf 'alpha.test.zsh # flaky on CI\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 1 && "${OUT}" == *"alpha.test.zsh"*"reason"* ]] \
        && test_pass "case3d a reason that starts with # (an inline comment) is not a reason" \
        || test_fail "case3d a reason that starts with # (an inline comment) is not a reason" "rc=${RC} out: ${OUT[1,300]}"
    r="$(make_root c3e alpha.test.zsh)"
    printf '#!/usr/bin/env zsh\n' > "${r}/tests/unit/helper.zsh"
    printf 'helper.zsh   this is a helper, not a suite\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 1 && "${OUT}" == *"helper.zsh"*"not a unit suite"* ]] \
        && test_pass "case3e an exclusion naming a file that is not a *.test.zsh suite fails the runner" \
        || test_fail "case3e an exclusion naming a file that is not a *.test.zsh suite fails the runner" "rc=${RC} out: ${OUT[1,300]}"
    r="$(make_root c3f alpha.test.zsh)"
    printf 'alpha.test.zsh first reason\nalpha.test.zsh second reason\n' > "${r}/tests/ci-unit-exclusions.txt"
    list_in "${r}"
    [[ "${RC}" == 1 && "${OUT}" == *"alpha.test.zsh"*"twice"* ]] \
        && test_pass "case3f a suite listed twice fails the runner (the earlier reason is not silently lost)" \
        || test_fail "case3f a suite listed twice fails the runner (the earlier reason is not silently lost)" "rc=${RC} out: ${OUT[1,300]}"
}

test_case4_the_run_mode_executes_every_discovered_suite_and_fails_on_a_failing_one() {
    test_start "4: a real run executes each discovered suite (including one nobody listed) and a failing suite fails the run"
    local r raw rc
    r="$(make_root c4 alpha.test.zsh unlisted.test.zsh)"
    printf '#!/usr/bin/env zsh\nexit 0\n' > "${r}/bin/vde-enforce-uap.zsh"; chmod +x "${r}/bin/vde-enforce-uap.zsh"
    raw="$(cd "${r}" && timeout 60 zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RUNRC=$?")"
    rc="${raw##*RUNRC=}"
    [[ "${rc}" == 0 && -e "${r}/ran-alpha" && -e "${r}/ran-unlisted" ]] \
        && test_pass "case4a both suites ran, including the one that was never listed anywhere, and the run passed" \
        || test_fail "case4a both suites ran, including the one that was never listed anywhere, and the run passed" "rc=${rc} markers: $(ls "${r}" | tr '\n' ' ') out: ${raw[1,300]}"
    printf '#!/usr/bin/env zsh\nexit 3\n' > "${r}/tests/unit/broken.test.zsh"
    raw="$(cd "${r}" && timeout 60 zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RUNRC=$?")"
    rc="${raw##*RUNRC=}"
    [[ "${rc}" != 0 && "${raw}" == *"broken.test.zsh"* ]] \
        && test_pass "case4b a failing suite fails the run and is named" \
        || test_fail "case4b a failing suite fails the run and is named" "rc=${rc} out: ${raw[1,300]}"
}

test_case4c_the_run_mode_skips_an_excluded_suite_loudly() {
    test_start "4c: a real run does NOT execute an excluded suite, says so, and still runs the others"
    local r raw rc
    r="$(make_root c4c alpha.test.zsh beta.test.zsh)"
    printf '#!/usr/bin/env zsh\nexit 0\n' > "${r}/bin/vde-enforce-uap.zsh"; chmod +x "${r}/bin/vde-enforce-uap.zsh"
    printf 'beta.test.zsh   needs a docker daemon the CI job does not have\n' > "${r}/tests/ci-unit-exclusions.txt"
    raw="$(cd "${r}" && timeout 60 zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RUNRC=$?")"
    rc="${raw##*RUNRC=}"
    [[ "${rc}" == 0 && -e "${r}/ran-alpha" && ! -e "${r}/ran-beta" ]] \
        && test_pass "case4c the excluded suite did not run, the other did, and the run passed" \
        || test_fail "case4c the excluded suite did not run, the other did, and the run passed" "rc=${rc} markers: $(ls "${r}" | tr '\n' ' ') out: ${raw[1,300]}"
    [[ "${raw}" == *"Excluded from CI: beta.test.zsh :: needs a docker daemon the CI job does not have"* ]] \
        && test_pass "case4d the run announces the exclusion and its reason (never silent)" \
        || test_fail "case4d the run announces the exclusion and its reason (never silent)" "out: ${raw[1,400]}"
}

test_case5_in_the_real_repo_every_suite_is_run_or_excluded_with_a_reason() {
    test_start "5: in this repository every tests/unit/*.test.zsh is either run or on the exclusion list with a reason (the drift guard)"
    local raw rc f name hits
    local -a on_disk listed_run listed_skip missing extra
    raw="$(cd "${VDE_ROOT_DIR}" && timeout 30 zsh tests/run-sovereign-tests.zsh --list 2>&1; print -r -- "LISTRC=$?")"
    rc="${raw##*LISTRC=}"
    on_disk=( "${VDE_ROOT_DIR}"/tests/unit/*.test.zsh(N:t) )
    listed_run=( ${(f)"$(print -r -- "${raw%LISTRC=*}" | sed -n 's/^run  //p')"} )
    listed_skip=( ${(f)"$(print -r -- "${raw%LISTRC=*}" | sed -n 's/^skip \([^ ]*\) :: .*/\1/p')"} )
    for name in "${on_disk[@]}"; do
        hits=0
        (( ${listed_run[(Ie)${name}]} > 0 )) && hits=$(( hits + 1 ))
        (( ${listed_skip[(Ie)${name}]} > 0 )) && hits=$(( hits + 1 ))
        (( hits == 1 )) || missing+=( "${name}" )
    done
    for name in "${listed_run[@]}" "${listed_skip[@]}"; do
        (( ${on_disk[(Ie)${name}]} )) || extra+=( "${name}" )
    done
    [[ "${rc}" == 0 && ${#on_disk} -gt 30 && ${#missing} == 0 && ${#extra} == 0 ]] \
        && test_pass "case5 all ${#on_disk} suites on disk are accounted for exactly once (${#listed_run} run, ${#listed_skip} excluded with a reason)" \
        || test_fail "case5 every suite on disk is accounted for exactly once" "rc=${rc} on_disk=${#on_disk} not-accounted-for: ${missing[*]:-none} listed-but-absent: ${extra[*]:-none}"
}

test_case1_list_mode_is_cheap_and_runs_nothing
test_case2_a_new_suite_is_discovered_without_touching_the_runner
test_case3_exclusions_need_a_reason_and_must_name_a_real_suite
test_case3_more_validation_comment_markers_non_suites_and_duplicates
test_case4_the_run_mode_executes_every_discovered_suite_and_fails_on_a_failing_one
test_case4c_the_run_mode_skips_an_excluded_suite_loudly
test_case5_in_the_real_repo_every_suite_is_run_or_excluded_with_a_reason

echo
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
