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
typeset -a GIT_SCRUB=( -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null )
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

test_case12_the_ci_job_has_the_history_the_diff_needs() {
    test_start "12: the CI job checks out full history and skips the diff only for main and stable promotions"
    grep -qE 'fetch-depth:[[:space:]]*0' "${WORKFLOW}" \
        && test_pass "case12a checkout uses fetch-depth: 0" \
        || test_fail "case12a checkout uses fetch-depth: 0" "merge-base needs the history; the default checkout is shallow"
    local res
    # NOTE: this evaluates a Python MODEL of the two expressions (and/or, format()), not the real
    # Actions evaluator; an expression using a function the model lacks fails loudly below.
    res="$(python3 -I - "${WORKFLOW}" 2>&1 <<'INNEREOF'
import re, sys
text = open(sys.argv[1]).read()
def expr(key):
    m = re.search(r"^\s*" + key + r":\s*\$\{\{(.*)\}\}\s*$", text, re.M)
    if not m:
        sys.exit("no expression for " + key)
    e = m.group(1).strip()
    e = re.sub(r"format\('([^']*)\{0\}',\s*([^)]+)\)", r"('\1' + \2)", e)
    for a, b in (("github.event.pull_request.head.repo.full_name", "head_repo"), ("github.repository", "repo"), ("github.ref_type", "ref_type"), ("github.event.before", "ev_before"), ("github.event_name", "ev_name"), ("github.base_ref", "base_ref"), ("github.head_ref", "head_ref"), ("github.ref_name", "ref_name")):
        e = e.replace(a, b)
    return e.replace("&&", " and ").replace("||", " or ")
def ev(e, **k):
    return eval(e, {"__builtins__": {}}, k)
d = expr("VDE_PAIRED_DIFF"); b = expr("VDE_PAIRED_BASE")
Z = "0" * 40
cases = [
 ("diff", dict(ev_name="pull_request", base_ref="stable", head_ref="develop", ref_name="1/merge"), "skip"),
 ("diff", dict(ev_name="pull_request", base_ref="main", head_ref="stable", ref_name="2/merge"), "skip"),
 ("diff", dict(ev_name="pull_request", base_ref="stable", head_ref="develop", ref_name="9/merge", head_repo="fork/r"), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="main", head_ref="stable", ref_name="10/merge", head_repo="fork/r"), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="stable", head_ref="develop", ref_name="11/merge", head_repo=None), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="develop", head_ref="fix/x", ref_name="3/merge"), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="stable", head_ref="fix/x", ref_name="4/merge"), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="main", head_ref="develop", ref_name="5/merge"), "on"),
 ("diff", dict(ev_name="pull_request", base_ref="main", head_ref="fix/x", ref_name="6/merge"), "on"),
 ("diff", dict(ev_name="push", base_ref="", head_ref="", ref_name="develop"), "on"),
 ("diff", dict(ev_name="push", base_ref="", head_ref="", ref_name="stable"), "skip"),
 ("diff", dict(ev_name="push", base_ref="", head_ref="", ref_name="main"), "skip"),
 ("diff", dict(ev_name="push", base_ref="", head_ref="", ref_name="1.5.7", ref_type="tag"), "skip"),
 ("diff", dict(ev_name="push", base_ref="", head_ref="", ref_name="fix/x"), "on"),
 ("base", dict(ev_name="pull_request", base_ref="develop", head_ref="fix/x", ref_name="7/merge", ev_before=""), "origin/develop"),
 ("base", dict(ev_name="pull_request", base_ref="fix/stack", head_ref="fix/y", ref_name="8/merge", ev_before=""), "origin/fix/stack"),
 ("base", dict(ev_name="push", base_ref="", head_ref="", ref_name="develop", ev_before="abc123"), "abc123"),
 ("base", dict(ev_name="push", base_ref="", head_ref="", ref_name="fix/x", ev_before="abc123"), ""),
 ("base", dict(ev_name="push", base_ref="", head_ref="", ref_name="develop", ev_before=Z), Z),
]
bad = []
for kind, env, want in cases:
    env.setdefault("ev_before", "")
    env.setdefault("repo", "o/r")
    env.setdefault("ref_type", "branch")
    env.setdefault("head_repo", "o/r")
    got = ev(d if kind == "diff" else b, **env)
    if got != want:
        bad.append("%s %s -> %r wanted %r" % (kind, {k: v for k, v in env.items() if v is not None and v != ""}, got, want))
print("OK" if not bad else "; ".join(bad))
INNEREOF
)"
    [[ "${res}" == OK ]] \
        && test_pass "case12b the workflow expressions give skip only for same-repo stable<-develop, main<-stable and pushes to main/stable or a tag, and the right base for PRs and develop pushes" \
        || test_fail "case12b the workflow expressions give skip only for same-repo stable<-develop, main<-stable and pushes to main/stable or a tag, and the right base for PRs and develop pushes" "${res[-400,-1]}"
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
test_case12_the_ci_job_has_the_history_the_diff_needs
test_case13_the_real_files_satisfy_the_static_policy

echo
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
