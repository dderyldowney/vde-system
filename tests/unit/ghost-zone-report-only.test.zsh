#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for the Ghost Zone rule (Signet #643): the audit's "Rule 3: plans/
# Subdirectory Lock" is REPORT-ONLY. An unauthorized plans/<subdir> (anything other
# than scripts/ and archive/) still fails the audit (zero tolerance) and is named,
# but the audit NEVER deletes it.
#
# The REAL bin/vde-enforce-uap.zsh is copied into a throwaway tree and run there.
# The Ghost Zone rule is the first check the enforcer performs, so no other part of
# the repo is needed. Every assertion about "not deleted" looks at the filesystem
# AFTER the audit ran.
#
# Each case asserts on the filesystem or on the audit's own output after a real run;
# the mutants that prove they can fail are listed in the Strike's PR (Signet #643).

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset ENFORCER_SRC="${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh"
if [[ ! -f "${ENFORCER_SRC}" ]]; then
    echo "FATAL: bin/vde-enforce-uap.zsh missing"
    exit 1
fi

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }  # not ((x++)): that returns 1 when x was 0 and trips the || fail
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT

typeset -g AUD_OUT='' AUD_RC=0

# ---------------------------------------------------------------------------
# Harness helpers
# ---------------------------------------------------------------------------

make_tree() {  # make_tree NAME -> a git repo holding only the real enforcer; prints its path
    local t="${TMP_ROOT}/$1"
    mkdir -p "${t}/bin" "${t}/plans"
    cp "${ENFORCER_SRC}" "${t}/bin/vde-enforce-uap.zsh"
    git -C "${t}" init -q
    print -r -- "${t}"
}

commit_tree() {  # commit_tree TREE -> commits everything currently in TREE
    git -C "$1" add -A
    git -C "$1" -c user.email=t@t -c user.name=t commit -qm fixture
}

run_audit() {  # run_audit TREE -> sets AUD_OUT (colours stripped) and AUD_RC (the audit's own status)
    local raw
    raw="$(cd "$1" && zsh bin/vde-enforce-uap.zsh 2>&1; print -r -- "AUDRC=$?")"
    AUD_RC="${raw##*AUDRC=}"
    AUD_OUT="$(print -r -- "${raw%AUDRC=*}" | sed 's/\x1b\[[0-9;]*m//g')"
}

# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

test_case1_unauthorized_subdir_fails_and_nothing_is_deleted() {
    test_start "1: an unauthorized plans/<subdir> fails the audit and BOTH its tracked and untracked files survive"
    local t; t="$(make_tree c1)"
    mkdir -p "${t}/plans/mywork"
    print -r -- "committed work" > "${t}/plans/mywork/tracked.md"
    commit_tree "${t}"
    print -r -- "work that exists nowhere else" > "${t}/plans/mywork/untracked.md"   # not in git: no way back if deleted
    run_audit "${t}"
    [[ "${AUD_RC}" != 0 ]] \
        && test_pass "case1a the audit exits non-zero (zero tolerance kept)" \
        || test_fail "case1a the audit exits non-zero (zero tolerance kept)" "rc=${AUD_RC}"
    [[ "${AUD_OUT}" == *"Ghost Zone 'plans/mywork/' detected"* ]] \
        && test_pass "case1b the offending directory is named" \
        || test_fail "case1b the offending directory is named" "out: ${AUD_OUT[1,300]}"
    [[ -f "${t}/plans/mywork/untracked.md" && "$(<"${t}/plans/mywork/untracked.md")" == "work that exists nowhere else" ]] \
        && test_pass "case1c the UNTRACKED file survives with its content" \
        || test_fail "case1c the UNTRACKED file survives with its content" "plans/mywork/untracked.md is gone or changed"
    [[ -f "${t}/plans/mywork/tracked.md" && -z "$(git -C "${t}" status --porcelain -- plans/mywork/tracked.md)" ]] \
        && test_pass "case1d the TRACKED file survives and git sees no deletion" \
        || test_fail "case1d the TRACKED file survives and git sees no deletion" "status: $(git -C "${t}" status --porcelain | head -3)"
    # The fixture is a bare tree, so later checks would fail the audit anyway: the exit
    # status alone cannot show that the RULE halted. Reaching the next check can.
    [[ "${AUD_OUT}" != *"Verifying mandatory configurations"* ]] \
        && test_pass "case1e the audit halts at the rule and never reaches the next check" \
        || test_fail "case1e the audit halts at the rule and never reaches the next check" "out: ${AUD_OUT[1,300]}"
}

test_case2_the_message_says_nothing_was_deleted_and_how_to_resolve() {
    test_start "2: the failure message says nothing was deleted and tells the operator how to resolve it"
    local t; t="$(make_tree c2)"
    mkdir -p "${t}/plans/mywork"
    print -r -- x > "${t}/plans/mywork/a.md"
    run_audit "${t}"
    [[ "${AUD_OUT}" == *"Nothing was deleted"* ]] \
        && test_pass "case2a the message states that nothing was deleted" \
        || test_fail "case2a the message states that nothing was deleted" "out: ${AUD_OUT[1,400]}"
    [[ "${AUD_OUT}" == *"plans/archive/"* && "${AUD_OUT}" == *"remove it deliberately"* ]] \
        && test_pass "case2b the message names both resolutions (move under plans/archive/, or remove deliberately)" \
        || test_fail "case2b the message names both resolutions (move under plans/archive/, or remove deliberately)" "out: ${AUD_OUT[1,400]}"
    [[ "${AUD_OUT}" != *"Purging"* ]] \
        && test_pass "case2c the message no longer promises a purge" \
        || test_fail "case2c the message no longer promises a purge" "out still says Purging"
}

test_case3_every_offender_is_named_and_survives() {
    test_start "3: with several unauthorized subdirectories every one is named and every one survives"
    local t; t="$(make_tree c3)"
    mkdir -p "${t}/plans/alpha" "${t}/plans/beta" "${t}/plans/scripts" "${t}/plans/archive"
    print -r -- a > "${t}/plans/alpha/a.md"
    print -r -- b > "${t}/plans/beta/b.md"
    print -r -- s > "${t}/plans/scripts/keep.zsh"
    print -r -- r > "${t}/plans/archive/old.md"
    run_audit "${t}"
    [[ "${AUD_RC}" != 0 && "${AUD_OUT}" == *"'plans/alpha/'"* && "${AUD_OUT}" == *"'plans/beta/'"* ]] \
        && test_pass "case3a both offenders are named and the audit fails" \
        || test_fail "case3a both offenders are named and the audit fails" "rc=${AUD_RC} out: ${AUD_OUT[1,400]}"
    [[ "${AUD_OUT}" != *"'plans/scripts/'"* && "${AUD_OUT}" != *"'plans/archive/'"* ]] \
        && test_pass "case3b the authorized scripts/ and archive/ are never named as offenders" \
        || test_fail "case3b the authorized scripts/ and archive/ are never named as offenders" "out: ${AUD_OUT[1,400]}"
    [[ -f "${t}/plans/alpha/a.md" && -f "${t}/plans/beta/b.md" && -f "${t}/plans/scripts/keep.zsh" && -f "${t}/plans/archive/old.md" ]] \
        && test_pass "case3c all four directories still hold their files" \
        || test_fail "case3c all four directories still hold their files" "$(cd "${t}" && find plans -type f | sort | tr '\n' ' ')"
}

test_case4_an_authorized_tree_passes_the_rule() {
    test_start "4: an authorized plans/ (scripts/, archive/, plain files) passes the rule and the audit moves on"
    local t; t="$(make_tree c4)"
    mkdir -p "${t}/plans/scripts" "${t}/plans/archive"
    print -r -- s > "${t}/plans/scripts/keep.zsh"
    print -r -- r > "${t}/plans/archive/old.md"
    print -r -- p > "${t}/plans/session_handover_remediation.md"
    run_audit "${t}"
    [[ "${AUD_OUT}" != *"Ghost Zone"* ]] \
        && test_pass "case4a no Ghost Zone report on an authorized tree" \
        || test_fail "case4a no Ghost Zone report on an authorized tree" "out: ${AUD_OUT[1,300]}"
    [[ "${AUD_OUT}" == *"Verifying mandatory configurations"* ]] \
        && test_pass "case4b the audit went past the rule to the next check" \
        || test_fail "case4b the audit went past the rule to the next check" "out: ${AUD_OUT[1,300]}"
    [[ -f "${t}/plans/scripts/keep.zsh" && -f "${t}/plans/archive/old.md" && -f "${t}/plans/session_handover_remediation.md" ]] \
        && test_pass "case4c nothing under plans/ was touched" \
        || test_fail "case4c nothing under plans/ was touched" "$(cd "${t}" && find plans -type f | sort | tr '\n' ' ')"
}

test_case5_no_plans_directory_is_fine() {
    test_start "5: a tree with no plans/ at all passes the rule (armor-only mode)"
    local t; t="$(make_tree c5)"
    rmdir "${t}/plans"
    run_audit "${t}"
    [[ "${AUD_OUT}" != *"Ghost Zone"* && "${AUD_OUT}" == *"Verifying mandatory configurations"* ]] \
        && test_pass "case5 no plans/ means no Ghost Zone report and the audit proceeds" \
        || test_fail "case5 no plans/ means no Ghost Zone report and the audit proceeds" "out: ${AUD_OUT[1,300]}"
}

test_case6_a_hidden_subdirectory_is_an_offender_too() {
    test_start "6: a hidden plans/.<subdir> is reported like any other and survives"
    local t; t="$(make_tree c6)"
    mkdir -p "${t}/plans/.cache"
    print -r -- "hidden work" > "${t}/plans/.cache/note.md"
    run_audit "${t}"
    [[ "${AUD_RC}" != 0 && "${AUD_OUT}" == *"Ghost Zone 'plans/.cache/' detected"* ]] \
        && test_pass "case6a the hidden directory is named and the audit fails" \
        || test_fail "case6a the hidden directory is named and the audit fails" "rc=${AUD_RC} out: ${AUD_OUT[1,300]}"
    [[ -f "${t}/plans/.cache/note.md" ]] \
        && test_pass "case6b the hidden directory survives" \
        || test_fail "case6b the hidden directory survives" "plans/.cache/note.md is gone"
}

test_case1_unauthorized_subdir_fails_and_nothing_is_deleted
test_case2_the_message_says_nothing_was_deleted_and_how_to_resolve
test_case3_every_offender_is_named_and_survives
test_case4_an_authorized_tree_passes_the_rule
test_case5_no_plans_directory_is_fine
test_case6_a_hidden_subdirectory_is_an_offender_too

echo
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
