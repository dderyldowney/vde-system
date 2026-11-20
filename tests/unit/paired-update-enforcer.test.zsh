#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for the paired-update policy (Signet #641).
#
# Policy: .gemini/STATE/session_handover.md and plans/session_handover_remediation.md are
# a PAIR. A change that touches one MUST touch the other, and both keep a
# "Paired Update Policy" section that links to the other. bin/paired_update_enforcer
# enforces it by comparing the files changed against a base ref (VDE_PAIRED_BASE, default
# origin/${VDE_ANVIL_BRANCH:-develop}), and its CI step must be able to FAIL.
#
# Every case builds a throwaway git repo holding the REAL enforcer and lib/vde-constants,
# commits a good "base", then changes files on a branch and runs the enforcer.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset ENFORCER_SRC="${VDE_ROOT_DIR}/bin/paired_update_enforcer"
typeset WORKFLOW="${VDE_ROOT_DIR}/.github/workflows/paired-update-check.yml"
typeset H=".gemini/STATE/session_handover.md"
typeset R="plans/session_handover_remediation.md"

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

good_handover() {
    print -r -- "# Handover"
    print -r -- ""
    print -r -- "## Paired Update Policy"
    print -r -- "This file is paired with [the plan](../../plans/session_handover_remediation.md): update both together."
}

good_remediation() {
    print -r -- "# Remediation"
    print -r -- ""
    print -r -- "## Paired Update Policy"
    print -r -- "This file is paired with [the handover](../.gemini/STATE/session_handover.md): update both together."
}

# scrubbed like tests/unit/native-skills.test.zsh: a GIT_DIR inherited from a hook or a linked
# worktree must never make a fixture act on the enclosing repository
typeset -a GIT_SCRUB=( -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR
    -u GITHUB_ACTIONS -u GITHUB_EVENT_NAME -u GITHUB_BASE_REF -u GITHUB_HEAD_REF -u GITHUB_REF_NAME -u GITHUB_REF_TYPE -u GITHUB_REPOSITORY
    -u VDE_PAIRED_HEAD_REPO -u VDE_PAIRED_EVENT_BEFORE -u VDE_PAIRED_DIFF
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null )   # every -u BEFORE the first NAME=value: env stops parsing options there
git_in() { env "${GIT_SCRUB[@]}" git -C "$1" -c user.email=t@t -c user.name=t "${@:2}"; }

make_tree() {  # make_tree NAME -> a repo with the real enforcer and a good committed base (ref "base"); prints its path
    local t="${TMP_ROOT}/$1"
    mkdir -p "${t}/bin" "${t}/lib" "${t}/.gemini/STATE" "${t}/plans"
    cp "${ENFORCER_SRC}" "${t}/bin/paired_update_enforcer"
    cp "${VDE_ROOT_DIR}/lib/vde-constants" "${t}/lib/vde-constants"
    good_handover > "${t}/${H}"
    good_remediation > "${t}/${R}"
    git_in "${t}" init -q
    git_in "${t}" add -A
    git_in "${t}" commit -qm base
    git_in "${t}" branch -M base
    git_in "${t}" checkout -q -b feat
    print -r -- "${t}"
}

commit_all() { git_in "$1" add -A; git_in "$1" commit -qm "$2"; }

run_enf() {  # run_enf TREE [ENV=VAL ...] -> sets OUT and RC; VDE_PAIRED_BASE defaults to "base"
    local t="$1"; shift
    local raw
    raw="$(cd "${t}" && env "${GIT_SCRUB[@]}" VDE_PAIRED_BASE=base "$@" zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"
    OUT="${raw%ENFRC=*}"
}

# expect_fail NAME TREE_RUN_DONE SUBSTRING : exit status exactly 1 (VDE_ERR_GENERAL), message present, never "parameter not set"
expect_fail() {
    if [[ "${RC}" == 1 && "${OUT}" == *"$2"* && "${OUT}" != *"parameter not set"* ]]; then
        test_pass "$1"
    else
        test_fail "$1" "rc=${RC} wanted 1 with [$2] and no 'parameter not set'; out: ${OUT[1,300]}"
    fi
}

expect_ok() {  # expect_ok NAME [SUBSTRING]
    if [[ "${RC}" == 0 && "${OUT}" == *"${2:-}"* && "${OUT}" != *"parameter not set"* ]]; then
        test_pass "$1"
    else
        test_fail "$1" "rc=${RC} wanted 0${2:+ with [$2]}; out: ${OUT[1,300]}"
    fi
}

# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

test_case1_a_good_tree_with_no_changes_passes() {
    test_start "1: a good tree with nothing changed passes"
    local t; t="$(make_tree c1)"
    run_enf "${t}"
    expect_ok "case1 rc 0 and the policy is verified" "Paired-update policy verified"
}

test_case2_both_files_changed_passes() {
    test_start "2: a change touching BOTH files passes"
    local t; t="$(make_tree c2)"
    print -r -- "- update" >> "${t}/${H}"; print -r -- "- update" >> "${t}/${R}"
    commit_all "${t}" both
    run_enf "${t}"
    expect_ok "case2 both changed" "Paired-update policy verified"
}

test_case3_only_the_handover_changed_fails() {
    test_start "3: a change touching ONLY the handover fails and names the file that was not updated"
    local t; t="$(make_tree c3)"
    print -r -- "- update" >> "${t}/${H}"
    commit_all "${t}" handover-only
    run_enf "${t}"
    expect_fail "case3a rc 1 and the message says the remediation plan was not updated" "${R}"
    [[ "${OUT}" == *"${H} changed but ${R} did not"* ]] && test_pass "case3b the message says which file changed and which did not" || test_fail "case3b the message says which file changed and which did not" "out: ${OUT[1,300]}"
}

test_case4_only_the_remediation_plan_changed_fails() {
    test_start "4: a change touching ONLY the remediation plan fails (the check runs both ways)"
    local t; t="$(make_tree c4)"
    print -r -- "- update" >> "${t}/${R}"
    commit_all "${t}" remediation-only
    run_enf "${t}"
    expect_fail "case4a rc 1 and the message says the handover was not updated" "${H}"
    [[ "${OUT}" == *"${R} changed but ${H} did not"* ]] && test_pass "case4b the message says which file changed and which did not" || test_fail "case4b the message says which file changed and which did not" "out: ${OUT[1,300]}"
}

test_case5_unrelated_changes_pass() {
    test_start "5: a change touching neither file passes"
    local t; t="$(make_tree c5)"
    print -r -- x > "${t}/unrelated.txt"
    commit_all "${t}" unrelated
    run_enf "${t}"
    expect_ok "case5 unrelated change" "Paired-update policy verified"
}

test_case6_each_policy_and_cross_link_is_required() {
    test_start "6: both files must carry the Paired Update Policy section and a cross-link to the other"
    local t
    t="$(make_tree c6a)"; print -r -- "# Handover only" > "${t}/${H}"; good_remediation > "${t}/${R}"; commit_all "${t}" x
    # the handover lost its policy AND its link; the remediation plan is untouched-good: both changed -> pairing OK, static fails
    print -r -- "- also" >> "${t}/${R}"; commit_all "${t}" y
    run_enf "${t}"; expect_fail "case6a the handover without the policy section fails" "Paired Update Policy missing in ${H}"
    t="$(make_tree c6b)"; good_handover > "${t}/${H}"; print -r -- "# Remediation only" > "${t}/${R}"; commit_all "${t}" x
    print -r -- "- also" >> "${t}/${H}"; commit_all "${t}" y
    run_enf "${t}"; expect_fail "case6b the remediation plan without the policy section fails" "Paired Update Policy missing in ${R}"
    t="$(make_tree c6c)"; { print -r -- "## Paired Update Policy"; print -r -- "no link here"; } > "${t}/${H}"; print -r -- "- also" >> "${t}/${R}"; commit_all "${t}" x
    run_enf "${t}"; expect_fail "case6c the handover without a link to the remediation plan fails" "Handover missing cross-link"
    t="$(make_tree c6d)"; { print -r -- "## Paired Update Policy"; print -r -- "no link here"; } > "${t}/${R}"; print -r -- "- also" >> "${t}/${H}"; commit_all "${t}" x
    run_enf "${t}"; expect_fail "case6d the remediation plan without a link to the handover fails" "Remediation plan missing cross-link"
}

test_case6e_a_mention_is_not_a_section_and_a_filename_is_not_a_link() {
    test_start "6e: the policy must be a real heading and the cross-link a real markdown link, not a mention in prose"
    local t
    t="$(make_tree c6e)"; { print -r -- "# Handover"; print -r -- "see the Paired Update Policy notes, and [x](../../plans/session_handover_remediation.md)"; } > "${t}/${H}"; print -r -- "- u" >> "${t}/${R}"; commit_all "${t}" x
    run_enf "${t}"; expect_fail "case6e a phrase in body text is not a Paired Update Policy section" "Paired Update Policy missing in ${H}"
    t="$(make_tree c6f)"; { print -r -- "## Paired Update Policy"; print -r -- "pair of session_handover_remediation.md, no link"; } > "${t}/${H}"; print -r -- "- u" >> "${t}/${R}"; commit_all "${t}" x
    run_enf "${t}"; expect_fail "case6f a bare filename is not a cross-link" "Handover missing cross-link"
    t="$(make_tree c6g)"; { print -r -- "## Paired Update Policy"; print -r -- "pair of .gemini/STATE/session_handover.md, no link"; } > "${t}/${R}"; print -r -- "- u" >> "${t}/${H}"; commit_all "${t}" x
    run_enf "${t}"; expect_fail "case6g a bare path is not a cross-link in the remediation plan either" "Remediation plan missing cross-link"
}

test_case7_a_missing_file_is_a_clear_error_not_a_crash() {
    test_start "7: a missing remediation plan (wrong path) is a clear error, not a set -u crash"
    local t; t="$(make_tree c7)"
    git_in "${t}" rm -q "${R}"; commit_all "${t}" gone
    run_enf "${t}"
    expect_fail "case7 rc 1 and the missing file is named" "${R}"
}

test_case8_an_unresolvable_base_fails_closed() {
    test_start "8: a base ref that cannot be resolved FAILS (it never skips silently)"
    local t; t="$(make_tree c8)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only
    run_enf "${t}" VDE_PAIRED_BASE=no-such-ref
    expect_fail "case8a rc 1 and the message names the base ref" "no-such-ref"
    [[ "${OUT}" == *"cannot be resolved"* ]] \
        && test_pass "case8b the failure is the explicit 'cannot be resolved' check, not a downstream git error" \
        || test_fail "case8b the failure is the explicit 'cannot be resolved' check, not a downstream git error" "out: ${OUT[1,300]}"
}

test_case9_the_default_base_is_origin_develop() {
    test_start "9: without VDE_PAIRED_BASE the base is origin/\${VDE_ANVIL_BRANCH:-develop}"
    local t; t="$(make_tree c9)"
    git_in "${t}" update-ref refs/remotes/origin/develop "$(git_in "${t}" rev-parse base)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only
    local raw
    raw="$(cd "${t}" && env -u VDE_PAIRED_BASE "${GIT_SCRUB[@]}" zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    expect_fail "case9 the unpaired change is found against origin/develop" "${R}"
}

test_case9b_an_all_zero_base_means_no_base() {
    test_start "9b: an all-zero base (a new branch's github.event.before) is treated as unset, not as a broken ref"
    local t; t="$(make_tree c9b)"
    git_in "${t}" update-ref refs/remotes/origin/develop "$(git_in "${t}" rev-parse base)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only
    run_enf "${t}" VDE_PAIRED_BASE=0000000000000000000000000000000000000000
    expect_fail "case9b falls back to origin/develop and finds the unpaired change" "${R}"
}

test_case10_skip_is_explicit_and_loud_and_typos_fail() {
    test_start "10: VDE_PAIRED_DIFF=skip skips the diff check loudly; any other value is an error"
    local t; t="$(make_tree c10)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only
    run_enf "${t}" VDE_PAIRED_DIFF=skip
    expect_ok "case10a skip passes an unpaired change and says so" "diff check SKIPPED"
    run_enf "${t}" VDE_PAIRED_DIFF=sikp
    expect_fail "case10b a typo is an error, not a silent skip" "VDE_PAIRED_DIFF"
    t="$(make_tree c10c)"; print -r -- "# no policy" > "${t}/${H}"; print -r -- "- u" >> "${t}/${R}"; commit_all "${t}" x
    run_enf "${t}" VDE_PAIRED_DIFF=skip
    expect_fail "case10c skip still enforces the policy text and cross-links" "Paired Update Policy missing"
}

# The CI step: its last command decides the step (zsh {0} has no errexit).
workflow_run_block() {
    awk '/name: Run paired update enforcer/ {f=1; next} f && /^[[:space:]]*run: \|/ {r=1; next} r { if ($0 ~ /^[[:space:]]*$/) next; if ($0 ~ /^          /) {sub(/^          /,""); print} else exit }' "${WORKFLOW}"
}

test_case11_the_ci_step_can_fail() {
    test_start "11: the CI step ends with the enforcer and FAILS on a deliberately broken tree"
    local blk last t
    blk="$(workflow_run_block)"
    last="${blk##*$'\n'}"
    [[ "${last}" == "./bin/paired_update_enforcer" ]] \
        && test_pass "case11a the step's LAST command is the enforcer (no trailing echo)" \
        || test_fail "case11a the step's LAST command is the enforcer (no trailing echo)" "last line is [${last}] of: ${blk}"
    grep -q 'continue-on-error' "${WORKFLOW}" \
        && test_fail "case11c nothing in the workflow may swallow the enforcer's failure" "continue-on-error appears in ${WORKFLOW}" \
        || test_pass "case11c nothing in the workflow may swallow the enforcer's failure (no continue-on-error)"
    t="$(make_tree c11)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only      # the deliberately broken tree
    print -r -- "${blk}" > "${TMP_ROOT}/step.zsh"
    local raw
    raw="$(cd "${t}" && env "${GIT_SCRUB[@]}" VDE_PAIRED_BASE=base zsh "${TMP_ROOT}/step.zsh" 2>&1; print -r -- "STEPRC=$?")"
    RC="${raw##*STEPRC=}"; OUT="${raw%STEPRC=*}"
    [[ "${RC}" != 0 && "${OUT}" != *"Paired update check passed"* ]] \
        && test_pass "case11b the exact step logic exits non-zero on the broken tree and prints no success line" \
        || test_fail "case11b the exact step logic exits non-zero on the broken tree and prints no success line" "rc=${RC} out: ${OUT[1,300]}"
}

test_case12_the_enforcer_decides_skip_and_base_not_the_yaml() {
    test_start "12: the workflow passes raw context values; the REAL enforcer decides skip and base, case-sensitively"
    grep -qE 'fetch-depth:[[:space:]]*0' "${WORKFLOW}" \
        && test_pass "case12a checkout uses fetch-depth: 0" \
        || test_fail "case12a checkout uses fetch-depth: 0" "merge-base needs the history; the default checkout is shallow"
    if grep -qE 'VDE_PAIRED_HEAD_REPO:[[:space:]]*\$\{\{[[:space:]]*github\.event\.pull_request\.head\.repo\.full_name[[:space:]]*\}\}' "${WORKFLOW}" \
        && grep -qE 'VDE_PAIRED_EVENT_BEFORE:[[:space:]]*\$\{\{[[:space:]]*github\.event\.before[[:space:]]*\}\}' "${WORKFLOW}"; then
        test_pass "case12b the workflow passes the head repository and the previous tip as raw values"
    else
        test_fail "case12b the workflow passes the head repository and the previous tip as raw values" "VDE_PAIRED_HEAD_REPO / VDE_PAIRED_EVENT_BEFORE not found as plain expressions"
    fi
    if grep -qE 'VDE_PAIRED_[A-Z_]+:.*(&&|\|\|)' "${WORKFLOW}" || grep -qE '^[[:space:]]*VDE_PAIRED_(DIFF|BASE):' "${WORKFLOW}"; then
        test_fail "case12c no decision logic (and no VDE_PAIRED_DIFF/BASE override) in the workflow YAML" "Actions string comparison is case-insensitive; the decision belongs in the enforcer"
    else
        test_pass "case12c no decision logic (and no VDE_PAIRED_DIFF/BASE override) in the workflow YAML"
    fi

    local t sha r row want cmp ev base head refn rtype hrepo before raw
    local -a f
    t="$(make_tree c12)"
    sha="$(git_in "${t}" rev-parse base)"
    for r in develop stable main Stable Main fix/stack; do git_in "${t}" update-ref "refs/remotes/origin/${r}" "${sha}"; done
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only      # unpaired on purpose
    local -a rows=(
        "pull_request|stable|develop|1/merge|branch|o/r||-|skip"
        "pull_request|main|stable|2/merge|branch|o/r||-|skip"
        "pull_request|stable|develop|3/merge|branch|O/R||-|skip"
        "pull_request|develop|fix/x|4/merge|branch|o/r||origin/develop|viol"
        "pull_request|stable|fix/x|5/merge|branch|o/r||origin/stable|viol"
        "pull_request|main|develop|6/merge|branch|o/r||origin/main|viol"
        "pull_request|stable|develop|7/merge|branch|fork/r||origin/stable|viol"
        "pull_request|stable|develop|8/merge|branch|||origin/stable|viol"
        "pull_request|Stable|develop|9/merge|branch|o/r||origin/Stable|viol"
        "pull_request|stable|Develop|10/merge|branch|o/r||origin/stable|viol"
        "pull_request|main|Stable|11/merge|branch|o/r||origin/main|viol"
        "pull_request|Main|stable|12/merge|branch|o/r||origin/Main|viol"
        "pull_request|fix/stack|fix/y|13/merge|branch|o/r||origin/fix/stack|viol"
        "push|||develop|branch||SHA|SHA|viol"
        "push|||develop|tag||SHA|origin/develop|viol"
        "push|||stable|branch|||-|skip"
        "push|||main|branch|||-|skip"
        "push|||Stable|branch|||origin/develop|viol"
        "push|||1.5.7|tag|||-|skip"
        "push|||1.5.7|branch|||origin/develop|viol"
        "push|||v1.5.7|tag|||origin/develop|viol"
        "push|||1.5.7-rc1|tag|||origin/develop|viol"
        "push|||1.5|tag|||origin/develop|viol"
        "push|||main|tag|||origin/develop|viol"
        "push|||fix/x|branch|||origin/develop|viol"
    )
    for row in "${rows[@]}"; do
        f=( "${(@s:|:)row}" )
        ev="${f[1]}" base="${f[2]}" head="${f[3]}" refn="${f[4]}" rtype="${f[5]}" hrepo="${f[6]}" before="${f[7]}" cmp="${f[8]}" want="${f[9]}"
        [[ "${before}" == SHA ]] && before="${sha}"
        [[ "${cmp}" == SHA ]] && cmp="${sha}"
        raw="$(cd "${t}" && env -u VDE_PAIRED_BASE -u VDE_PAIRED_DIFF "${GIT_SCRUB[@]}" GITHUB_ACTIONS=true GITHUB_EVENT_NAME="${ev}" GITHUB_BASE_REF="${base}" GITHUB_HEAD_REF="${head}" GITHUB_REF_NAME="${refn}" GITHUB_REF_TYPE="${rtype}" GITHUB_REPOSITORY=o/r VDE_PAIRED_HEAD_REPO="${hrepo}" VDE_PAIRED_EVENT_BEFORE="${before}" zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
        RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
        case "${want}" in
            skip)   [[ "${RC}" == 0 && "${OUT}" == *"SKIPPED"* ]] ;;
            viol)   [[ "${RC}" == 1 && "${OUT}" == *"Paired Update violated"* && ( "${cmp}" == - || "${OUT}" == *"compared with ${cmp}"* ) ]] ;;
        esac \
            && test_pass "case12 [${want}] ${ev} base=${base:--} head=${head:--} ref=${refn:--} type=${rtype} headrepo=${hrepo:--}" \
            || test_fail "case12 [${want}] ${ev} base=${base:--} head=${head:--} ref=${refn:--} type=${rtype} headrepo=${hrepo:--}" "rc=${RC} out: ${OUT[1,260]}"
    done

    # an explicit setting beats the derived one, both ways
    raw="$(cd "${t}" && env -u VDE_PAIRED_BASE "${GIT_SCRUB[@]}" GITHUB_ACTIONS=true GITHUB_EVENT_NAME=push GITHUB_REF_NAME=fix/x VDE_PAIRED_DIFF=skip zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    [[ "${RC}" == 0 && "${OUT}" == *"SKIPPED"* ]] \
        && test_pass "case12d an explicit VDE_PAIRED_DIFF=skip beats the derived 'on' in CI" \
        || test_fail "case12d an explicit VDE_PAIRED_DIFF=skip beats the derived 'on' in CI" "rc=${RC} out: ${OUT[1,260]}"
    raw="$(cd "${t}" && env -u VDE_PAIRED_BASE "${GIT_SCRUB[@]}" GITHUB_ACTIONS=true GITHUB_EVENT_NAME=pull_request GITHUB_BASE_REF=stable GITHUB_HEAD_REF=develop GITHUB_REPOSITORY=o/r VDE_PAIRED_HEAD_REPO=o/r VDE_PAIRED_DIFF=on zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    [[ "${RC}" == 1 && "${OUT}" == *"Paired Update violated"* && "${OUT}" != *"SKIPPED"* ]] \
        && test_pass "case12e an explicit VDE_PAIRED_DIFF=on beats the derived 'skip' in CI" \
        || test_fail "case12e an explicit VDE_PAIRED_DIFF=on beats the derived 'skip' in CI" "rc=${RC} out: ${OUT[1,260]}"
    raw="$(cd "${t}" && env -u VDE_PAIRED_DIFF "${GIT_SCRUB[@]}" GITHUB_ACTIONS=true GITHUB_EVENT_NAME=pull_request GITHUB_BASE_REF=develop GITHUB_HEAD_REF=fix/x GITHUB_REPOSITORY=o/r VDE_PAIRED_HEAD_REPO=o/r VDE_PAIRED_BASE=base zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    [[ "${RC}" == 1 && "${OUT}" == *"compared with base)"* ]] \
        && test_pass "case12f an explicit VDE_PAIRED_BASE beats the base derived from the PR" \
        || test_fail "case12f an explicit VDE_PAIRED_BASE beats the base derived from the PR" "rc=${RC} out: ${OUT[1,260]}"
    raw="$(cd "${t}" && env -u VDE_PAIRED_BASE -u VDE_PAIRED_DIFF "${GIT_SCRUB[@]}" GITHUB_ACTIONS=true GITHUB_EVENT_NAME=pull_request GITHUB_BASE_REF=stable GITHUB_HEAD_REF=develop GITHUB_REPOSITORY= VDE_PAIRED_HEAD_REPO= zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    [[ "${RC}" == 1 && "${OUT}" == *"compared with origin/stable)"* && "${OUT}" != *"SKIPPED"* ]] \
        && test_pass "case12g two empty repository names are not 'the same repository'" \
        || test_fail "case12g two empty repository names are not 'the same repository'" "rc=${RC} out: ${OUT[1,260]}"
}

test_case12h_an_ambient_ci_context_cannot_decide_a_case() {
    test_start "12h: the harness scrubs the runner's own GITHUB_* context, so a case never depends on where the suite runs"
    local t out
    t="$(make_tree c12h)"
    print -r -- "- update" >> "${t}/${H}"; commit_all "${t}" handover-only      # unpaired on purpose
    out="$( export GITHUB_ACTIONS=true GITHUB_EVENT_NAME=push GITHUB_REF_NAME=main GITHUB_REF_TYPE=branch VDE_PAIRED_DIFF=skip; run_enf "${t}"; print -r -- "RC=${RC}"; print -r -- "${OUT}" )"
    [[ "${out}" == *"RC=1"* && "${out}" == *"Paired Update violated"* && "${out}" != *"SKIPPED"* ]] \
        && test_pass "case12h a runner that looks like a push to main does not turn a violation into a skip" \
        || test_fail "case12h a runner that looks like a push to main does not turn a violation into a skip" "out: ${out[1,300]}"
}

# The effective CHECK name of every job in a workflow file, one per line: the job's explicit
# `name:`, else its id. (A required status check is matched by this name.)
#
# This is a line reader for the plain spelling this repository's workflows use, NOT a YAML parser,
# and it is an ALLOWLIST: inside `jobs:` a 2-space line must be a plain or simply quoted job header,
# a 4-space line must be a plain `key:`, and a job `name:` must be a complete one-line scalar (plain,
# "double" or 'single' quoted, no escape, no expression). Anything else (flow mappings, quoted keys,
# merge keys, a value on the next line, a scalar split over lines, odd indentation, block scalars,
# anchors, tags) prints one `UNREADABLE: <why>` line instead, and callers treat that as a possible
# collision: it fails closed, it never reads such a file as "unique".
# Boundary, stated plainly: this guards against ACCIDENTAL collisions. It is not a YAML parser, and a
# deliberately adversarial spelling outside the allowlist could still evade it; ruling that out needs a
# real parser (PyYAML) installed in the CI test jobs, which they do not have today.
workflow_check_names() {  # workflow_check_names FILE
    awk '
      function bad(why) { print "UNREADABLE: " why; bad_seen = 1; exit }
      function ind(l) { match(l, /^ */); return RLENGTH }
      /^jobs:[[:space:]]*(#.*)?$/ { f = 1; next }
      !f { next }
      /^[[:space:]]*(#.*)?$/ { next }
      /^[^[:space:]]/ { exit }
      {
          n = ind($0)
          if (after_name) { after_name = 0; if (n > 4) bad("a job name continues on the next line") }
          if (n == 2) {
              if ($0 !~ /^  ("[^"\\]*"|\047[^\047]*\047|[A-Za-z0-9_-]+):[[:space:]]*(#.*)?$/) bad("a job header is not a plain or simply quoted id on its own line")
              if (id != "") print (nm != "" ? nm : id)
              id = $0; sub(/^  /, "", id)
              if (id ~ /^"/) { sub(/^"/, "", id); id = substr(id, 1, index(id, "\"") - 1) }
              else if (id ~ /^\047/) { sub(/^\047/, "", id); id = substr(id, 1, index(id, "\047") - 1) }
              else { sub(/:.*$/, "", id) }
              nm = ""; next
          }
          if (id == "") bad("jobs are not indented by exactly 2 spaces")
          if (n == 4) {
              if ($0 !~ /^    [A-Za-z_][A-Za-z0-9_-]*:([[:space:]]|$)/) bad("a job property is not a plain key")
              if ($0 !~ /^    name:/) next
              v = $0; sub(/^    name:[[:space:]]*/, "", v)
              if (v == "" || v ~ /^#/) bad("a job name has its value on the next line")
              if (v ~ /\\/) bad("a job name uses an escape sequence")
              if (v ~ /\$\{\{/) bad("a job name is an expression")
              if (v ~ /^(null|Null|NULL|~)([[:space:]]+#.*)?$/) bad("a job name is null, which GitHub resolves to the job id")
              if (v ~ /^[|>&*!%@`\[{]/) bad("a job name is a block scalar, anchor, alias, tag or flow collection")
              if (v ~ /^"/) {
                  sub(/^"/, "", v); q = index(v, "\"")
                  if (!q) bad("a quoted job name is not closed on its line")
                  if (substr(v, q + 1) !~ /^[[:space:]]*(#.*)?$/) bad("text follows a quoted job name")
                  v = substr(v, 1, q - 1)
                  if (v == "") bad("a quoted job name is empty")
              } else if (v ~ /^\047/) {
                  sub(/^\047/, "", v)
                  if (v ~ /\047\047/) bad("a quoted job name uses the doubled-quote escape")
                  q = index(v, "\047")
                  if (!q) bad("a quoted job name is not closed on its line")
                  if (substr(v, q + 1) !~ /^[[:space:]]*(#.*)?$/) bad("text follows a quoted job name")
                  v = substr(v, 1, q - 1)
                  if (v == "") bad("a quoted job name is empty")
              } else {
                  sub(/[[:space:]]+#.*$/, "", v); sub(/[[:space:]]+$/, "", v); after_name = 1
              }
              nm = v; next
          }
          if (n < 4) bad("a job line is indented by neither 2 nor 4 spaces")
      }
      END { if (bad_seen) exit; if (!f) print "UNREADABLE: no plain jobs: block"; else if (id != "") print (nm != "" ? nm : id) }
    ' "$1"
}

# every workflow file in DIR (.yml and .yaml, GitHub loads both) except EXCLUDE that has a job whose
# check name is NAME, OR that cannot be read exactly (fail closed)
workflow_name_holders() {  # workflow_name_holders DIR EXCLUDE NAME -> file basenames, one per line
    local f names
    for f in "$1"/*.yml(N) "$1"/*.yaml(N); do
        [[ "${f}" == "$2" ]] && continue
        names=$'\n'"$(workflow_check_names "${f}")"$'\n'
        if [[ "${names}" == *$'\n'"$3"$'\n'* || "${names}" == *$'\n'UNREADABLE:* ]]; then
            print -r -- "${f:t}"
        fi
    done
}

test_case14_the_check_has_one_unique_required_name() {
    test_start "14: the paired-update workflow has exactly one job, named paired-update, and no other workflow uses that check name (a required check is matched by name; Signet #658)"
    local names holders d
    names="$(workflow_check_names "${WORKFLOW}")"
    [[ "${names}" == "paired-update" ]] \
        && test_pass "case14a the workflow's only job has the check name paired-update" \
        || test_fail "case14a the workflow's only job has the check name paired-update" "check names: ${names//$'\n'/, }"
    grep -qE "^    name:[[:space:]]*[\"']?paired-update[\"']?[[:space:]]*(#.*)?\$" "${WORKFLOW}" \
        && test_pass "case14b the job sets its check name explicitly (name: paired-update)" \
        || test_fail "case14b the job sets its check name explicitly (name: paired-update)" "no job-level 'name: paired-update' line"
    holders="$(workflow_name_holders "${VDE_ROOT_DIR}/.github/workflows" "${WORKFLOW}" paired-update)"
    [[ -z "${holders}" ]] \
        && test_pass "case14c no other workflow has a check named paired-update" \
        || test_fail "case14c no other workflow has a check named paired-update" "also used in: ${holders//$'\n'/, }"

    # the helper itself, against violating and innocent fixtures (not only the live tree)
    d="${TMP_ROOT}/wf14"; mkdir -p "${d}"
    cat > "${d}/by-id.yml" <<'WFEOF'
name: x
jobs:
# a column-zero comment between jobs must not end the block

  other:
    runs-on: ubuntu-latest
# another one
  paired-update:
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/quoted-id.yaml" <<'WFEOF'
jobs:
  "paired-update":
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/by-name.yml" <<'WFEOF'
jobs:
  something:
    name: 'paired-update'   # the check name, whatever the id
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/innocent.yml" <<'WFEOF'
jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - name: paired-update
        uses: actions/upload-artifact@v4
        with:
          name: paired-update
WFEOF
    # spellings a line-based reader cannot resolve: each must be FLAGGED (fail closed), never read as "unique"
    cat > "${d}/dynamic.yml" <<'WFEOF'
jobs:
  matrix-job:
    name: ${{ matrix.check }}
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/indent4.yml" <<'WFEOF'
jobs:
    paired-update:
        runs-on: ubuntu-latest
WFEOF
    cat > "${d}/props3.yml" <<'WFEOF'
jobs:
  odd:
   name: paired-update
   runs-on: ubuntu-latest
WFEOF
    cat > "${d}/id-escape.yml" <<'WFEOF'
jobs:
  "paired-\u0075pdate":
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/nextline-name.yml" <<'WFEOF'
jobs:
  other:
    name:
      paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/flow-job.yml" <<'WFEOF'
jobs:
  a: {name: paired-update, runs-on: ubuntu-latest}
WFEOF
    cat > "${d}/colon-id.yml" <<'WFEOF'
jobs:
  "x:y":
    name: paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/quoted-key.yml" <<'WFEOF'
jobs:
  a:
    "name": paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/multiline-plain.yml" <<'WFEOF'
jobs:
  a:
    name: paired-
      update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/unterminated.yml" <<'WFEOF'
jobs:
  a:
    name: "paired-
      update"
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/squote-escape.yml" <<'WFEOF'
jobs:
  a:
    name: 'paired-update'''
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/merge-key.yml" <<'WFEOF'
jobs:
  a:
    <<: *defaults
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/jobs-flow.yml" <<'WFEOF'
jobs: {a: {name: paired-update, runs-on: ubuntu-latest}}
WFEOF
    cat > "${d}/jobs-quoted.yml" <<'WFEOF'
"jobs":
  a:
    name: paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/null-name.yml" <<'WFEOF'
jobs:
  paired-update:
    name: null
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/empty-name.yml" <<'WFEOF'
jobs:
  a:
    name: ""
    runs-on: ubuntu-latest
WFEOF
    # readable and distinct: the id contains ": #" and must be read in full, not cut at the first colon
    cat > "${d}/id-colon-hash.yml" <<'WFEOF'
jobs:
  "paired-update: #b":
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/anchor.yml" <<'WFEOF'
jobs:
  a:
    name: &n paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/tag.yml" <<'WFEOF'
jobs:
  a:
    name: !!str paired-update
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/block.yml" <<'WFEOF'
jobs:
  a:
    name: >
      paired-update
    runs-on: ubuntu-latest
WFEOF
    # readable and distinct although it contains a #: a comment is only a comment OUTSIDE quotes
    cat > "${d}/hash-in-quotes.yml" <<'WFEOF'
jobs:
  a:
    name: "paired-update # not a comment"   # but this is
    runs-on: ubuntu-latest
WFEOF
    cat > "${d}/escape.yml" <<'WFEOF'
jobs:
  a:
    name: "paired-\u0075pdate"
    runs-on: ubuntu-latest
WFEOF
    # readable and distinct: must NOT be flagged
    cat > "${d}/distinct.yml" <<'WFEOF'
jobs:
  b:
    name: "Paired Update (legacy)"
    runs-on: ubuntu-latest
WFEOF
    holders="$(workflow_name_holders "${d}" "" paired-update | LC_ALL=C sort | tr '\n' ' ')"
    [[ "${holders}" == "anchor.yml block.yml by-id.yml by-name.yml colon-id.yml dynamic.yml empty-name.yml escape.yml flow-job.yml id-escape.yml indent4.yml jobs-flow.yml jobs-quoted.yml merge-key.yml multiline-plain.yml nextline-name.yml null-name.yml props3.yml quoted-id.yaml quoted-key.yml squote-escape.yml tag.yml unterminated.yml " ]] \
        && test_pass "case14d the helper finds a collision by id (past column-0 comments), by quoted id in a .yaml file and by an explicit quoted name, FLAGS every spelling it cannot read (a missing plain jobs: block, dynamic or null or empty names, odd indentation, escapes, block scalars, anchors, tags, flow mappings, quoted keys, split or unterminated scalars, merge keys), and reads a quoted name or id containing # or a colon exactly, and ignores step names, artifact names and a distinct quoted name" \
        || test_fail "case14d the helper finds a collision by id (past column-0 comments), by quoted id in a .yaml file and by an explicit quoted name, FLAGS every spelling it cannot read (a missing plain jobs: block, dynamic or null or empty names, odd indentation, escapes, block scalars, anchors, tags, flow mappings, quoted keys, split or unterminated scalars, merge keys), and reads a quoted name or id containing # or a colon exactly, and ignores step names, artifact names and a distinct quoted name" "found: ${holders}"
}

test_case13_the_real_files_satisfy_the_static_policy() {
    test_start "13: the REAL handover and remediation plan carry the policy and the two cross-links"
    local raw
    raw="$(cd "${VDE_ROOT_DIR}" && env VDE_PAIRED_DIFF=skip zsh bin/paired_update_enforcer 2>&1; print -r -- "ENFRC=$?")"
    RC="${raw##*ENFRC=}"; OUT="${raw%ENFRC=*}"
    expect_ok "case13 the live files pass the static checks" "Paired-update policy verified"
}

test_case1_a_good_tree_with_no_changes_passes
test_case2_both_files_changed_passes
test_case3_only_the_handover_changed_fails
test_case4_only_the_remediation_plan_changed_fails
test_case5_unrelated_changes_pass
test_case6_each_policy_and_cross_link_is_required
test_case6e_a_mention_is_not_a_section_and_a_filename_is_not_a_link
test_case7_a_missing_file_is_a_clear_error_not_a_crash
test_case8_an_unresolvable_base_fails_closed
test_case9_the_default_base_is_origin_develop
test_case9b_an_all_zero_base_means_no_base
test_case10_skip_is_explicit_and_loud_and_typos_fail
test_case11_the_ci_step_can_fail
test_case12_the_enforcer_decides_skip_and_base_not_the_yaml
test_case12h_an_ambient_ci_context_cannot_decide_a_case
test_case13_the_real_files_satisfy_the_static_policy
test_case14_the_check_has_one_unique_required_name

echo
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
