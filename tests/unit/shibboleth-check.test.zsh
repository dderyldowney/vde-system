#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for the shibboleth literal sweep (lib/vde-shibboleth).
#
# Every in-scope zsh file must carry the Zsh expansion-flag shibboleth
#   typeset _ZSH_PURE=${(%):-%x}
# on one of its first 20 lines, anchored at column 1. These tests build
# throwaway git repos under one mktemp root and prove the sweep contract:
# detection, window, anchoring, scope, exclusions, baseline grandfathering,
# stale-baseline detection, the staged-additions guard, and a read-only sanity
# pass over the real repo. The real repo is never written.
#
# RED until lib/vde-shibboleth exists: the FATAL guard below exits 1.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset SHIB_LIB="${VDE_ROOT_DIR}/lib/vde-shibboleth"

if [[ ! -f "${SHIB_LIB}" ]]; then
    echo "FATAL: lib/vde-shibboleth missing (RED)"
    exit 1
fi

source "${SHIB_LIB}"

# Test configuration
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

typeset -g SHIB_LIT='typeset _ZSH_PURE=${(%):-%x}'
typeset -g SWEEP_OUT='' SWEEP_RC=0

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT

# ---------------------------------------------------------------------------
# Harness helpers
# ---------------------------------------------------------------------------

expect_eq() {  # expect_eq NAME GOT WANT
    if [[ "$2" == "$3" ]]; then
        test_pass "$1"
    else
        test_fail "$1" "got [$2] want [$3]"
    fi
}

new_repo() {  # new_repo NAME -> prints absolute path of a fresh git repo
    local r="${TMP_ROOT}/$1"
    mkdir -p "${r}"
    git -C "${r}" init -q
    print -r -- "${r}"
}

stage_all() {  # stage_all REPO
    git -C "$1" add -A
}

mk_zsh() {  # mk_zsh ABS_FILE TOTAL_LINES [LITERAL_LINE]
    local f="$1" total="$2" lit="${3:-0}" i
    mkdir -p "${f:h}"
    : > "${f}"
    for (( i = 1; i <= total; i++ )); do
        if (( i == 1 )); then
            print -r -- '#!/usr/bin/env zsh' >> "${f}"
        elif (( i == lit )); then
            print -r -- "${SHIB_LIT}" >> "${f}"
        else
            print -r -- "echo line ${i}" >> "${f}"
        fi
    done
}

sweep_into() {  # sweep_into ROOT [BASELINE_REL] -> sets SWEEP_OUT, SWEEP_RC
    SWEEP_OUT="$(vde_shib_sweep "$@" 2>&1)"
    SWEEP_RC=$?
}

make_baseline_repo() {  # make_baseline_repo NAME -> committed baseline with 2 entries
    local r
    r="$(new_repo "$1")"
    mk_zsh "${r}/lib/a.zsh" 3
    mk_zsh "${r}/lib/b.zsh" 3
    mkdir -p "${r}/docs/governance"
    print -rl -- lib/a.zsh lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    git -C "${r}" -c user.email=t@t -c user.name=t -c commit.gpgsign=false commit -q -m baseline
    print -r -- "${r}"
}

# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

test_case1_original_gap() {
    test_start "1: original gap - zsh file using \${(f)x} without the literal is MISSING"
    local r
    r="$(new_repo c1)"
    mkdir -p "${r}/lib"
    {
        print -r -- '#!/usr/bin/env zsh'
        for (( i = 2; i <= 39; i++ )); do print -r -- "echo line ${i}"; done
        print -r -- 'print -l ${(f)x}'
    } > "${r}/lib/gap.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case1 sweep output" "$SWEEP_OUT" "MISSING lib/gap.zsh"
    expect_eq "case1 sweep rc" "$SWEEP_RC" 1
}

test_case2_literal_line3() {
    test_start "2: literal on line 3 - clean sweep"
    local r
    r="$(new_repo c2)"
    mk_zsh "${r}/lib/ok.zsh" 10 3
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case2 sweep output" "$SWEEP_OUT" ""
    expect_eq "case2 sweep rc" "$SWEEP_RC" 0
}

test_case3_window_edge() {
    test_start "3: window edge - literal on line 20 ok, on line 21 MISSING"
    local r
    r="$(new_repo c3)"
    mk_zsh "${r}/lib/w20.zsh" 25 20
    mk_zsh "${r}/lib/w21.zsh" 25 21
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case3 sweep output" "$SWEEP_OUT" "MISSING lib/w21.zsh"
    expect_eq "case3 sweep rc" "$SWEEP_RC" 1
}

test_case4_comment_and_indent_do_not_count() {
    test_start "4: commented or indented literal does NOT count"
    local r expected
    r="$(new_repo c4)"
    mkdir -p "${r}/lib"
    print -r -- '#!/usr/bin/env zsh' "# ${SHIB_LIT}" 'echo a' > "${r}/lib/comment.zsh"
    print -r -- '#!/usr/bin/env zsh' "  ${SHIB_LIT}" 'echo a' > "${r}/lib/indent.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    expected=$'MISSING lib/comment.zsh\nMISSING lib/indent.zsh'
    expect_eq "case4 sweep output" "$SWEEP_OUT" "$expected"
    expect_eq "case4 sweep rc" "$SWEEP_RC" 1
}

test_case5_non_zsh_ignored() {
    test_start "5: non-zsh files (bash shebang, no-shebang non-.zsh file, empty .zsh file) are ignored"
    local r
    r="$(new_repo c5)"
    mkdir -p "${r}/tools"
    print -r -- '#!/bin/bash' 'echo a' 'echo b' 'echo c' 'echo d' > "${r}/tools/bashy.sh"
    # A shebang-less file is only a zsh file when its NAME ends in .zsh (case 23).
    print -r -- 'echo a' 'echo b' > "${r}/tools/noshebang"
    : > "${r}/tools/empty.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case5 sweep output" "$SWEEP_OUT" ""
    expect_eq "case5 sweep rc" "$SWEEP_RC" 0
}

test_case6_uniformity_short_file() {
    test_start "6: uniformity - 3-line zsh file lacking the literal is MISSING"
    local r
    r="$(new_repo c6)"
    mk_zsh "${r}/lib/tiny.zsh" 3
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case6 sweep output" "$SWEEP_OUT" "MISSING lib/tiny.zsh"
    expect_eq "case6 sweep rc" "$SWEEP_RC" 1
}

test_case7_exclusions() {
    test_start "7: exclusions - out-of-scope zsh files lacking the literal are silent"
    local r f p rc
    r="$(new_repo c7)"
    for f in plans/p.zsh conductor/c.zsh docs/d.zsh bin/archive/x/a.zsh tests/docker/t.zsh .github/g.zsh; do
        mk_zsh "${r}/${f}" 5
    done
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case7 sweep output" "$SWEEP_OUT" ""
    expect_eq "case7 sweep rc" "$SWEEP_RC" 0
    for p in docs/x.zsh bin/archive/x/y.zsh tests/docker/x.zsh .github/x.yml plans/x.zsh conductor/x.zsh; do
        vde_shib_excluded "$p"; rc=$?
        expect_eq "case7 excluded rc for ${p}" "$rc" 0
    done
    for p in bin/vde lib/x; do
        vde_shib_excluded "$p"; rc=$?
        expect_eq "case7 not-excluded rc for ${p}" "$rc" 1
    done
}

test_case8_baseline_grandfathers() {
    test_start "8: baseline grandfathers listed violators; unlisted ones still MISSING"
    local r
    # 8a: only a grandfathered violator
    r="$(new_repo c8a)"
    mk_zsh "${r}/lib/old.zsh" 5
    mkdir -p "${r}/docs/governance"
    print -r -- lib/old.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case8a grandfathered sweep output" "$SWEEP_OUT" ""
    expect_eq "case8a grandfathered sweep rc" "$SWEEP_RC" 0
    # 8b: grandfathered plus one unlisted violator
    r="$(new_repo c8b)"
    mk_zsh "${r}/lib/old.zsh" 5
    mk_zsh "${r}/lib/new.zsh" 5
    mkdir -p "${r}/docs/governance"
    print -r -- lib/old.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case8b unlisted sweep output" "$SWEEP_OUT" "MISSING lib/new.zsh"
    expect_eq "case8b unlisted sweep rc" "$SWEEP_RC" 1
}

test_case9_stale_entries() {
    test_start "9: stale baseline entries - four STALE lines, rc 1"
    local r p n
    r="$(new_repo c9)"
    mk_zsh "${r}/lib/has.zsh" 5 3
    mk_zsh "${r}/plans/p.zsh" 5
    mkdir -p "${r}/tools" "${r}/docs/governance"
    print -r -- '#!/bin/bash' 'echo a' > "${r}/tools/bash.sh"
    print -rl -- lib/has.zsh lib/gone.zsh tools/bash.sh plans/p.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case9 sweep rc" "$SWEEP_RC" 1
    n="$(print -r -- "$SWEEP_OUT" | grep -c '^STALE ')"
    expect_eq "case9 four STALE lines" "$n" 4
    for p in lib/has.zsh lib/gone.zsh tools/bash.sh plans/p.zsh; do
        if print -r -- "$SWEEP_OUT" | grep -qF -- "STALE ${p} "; then
            test_pass "case9 STALE names ${p}"
        else
            test_fail "case9 STALE names ${p}" "no STALE line for ${p}"
        fi
    done
}

test_case10_baseline_comments_and_blanks() {
    test_start "10: baseline comments and blank lines are ignored"
    local r
    r="$(new_repo c10)"
    mk_zsh "${r}/lib/old.zsh" 5
    mkdir -p "${r}/docs/governance"
    printf '%s\n' '# shibboleth baseline' '' 'lib/old.zsh' '# trailing comment' '' \
        > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case10 sweep output" "$SWEEP_OUT" ""
    expect_eq "case10 sweep rc" "$SWEEP_RC" 0
}

test_case11_baseline_print_sorted() {
    test_start "11: baseline_print lists only violators, sorted"
    local r out expected
    r="$(new_repo c11)"
    mk_zsh "${r}/lib/zeta.zsh" 5
    mk_zsh "${r}/lib/alpha.zsh" 5
    mk_zsh "${r}/lib/ok.zsh" 5 3
    mkdir -p "${r}/tools"
    print -r -- '#!/bin/bash' 'echo a' > "${r}/tools/bash.sh"
    stage_all "${r}"
    out="$(vde_shib_baseline_print "${r}" 2>&1)"
    expected=$'lib/alpha.zsh\nlib/zeta.zsh'
    expect_eq "case11 baseline_print output" "$out" "$expected"
}

test_case12_staged_additions_guard() {
    test_start "12: staged-additions guard - only added non-comment lines are reported"
    local r out rc
    # 12a: one added path staged
    r="$(make_baseline_repo c12a)"
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case12a added path output" "$out" "lib/c.zsh"
    expect_eq "case12a added path rc" "$rc" 1
    # 12b: one entry removed
    r="$(make_baseline_repo c12b)"
    print -rl -- lib/a.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case12b removal output" "$out" ""
    expect_eq "case12b removal rc" "$rc" 0
    # 12c: comment-only addition
    r="$(make_baseline_repo c12c)"
    print -rl -- lib/a.zsh lib/b.zsh '# new comment' > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case12c comment-only output" "$out" ""
    expect_eq "case12c comment-only rc" "$rc" 0
}

test_case13_real_repo_sanity() {
    test_start "13: real-repo sanity - no MISSING for files carrying the literal (read-only)"
    # NB: never name a local `path` in zsh; it is tied to $PATH and empties it.
    local line rel_path bad=0 tracked
    sweep_into "${VDE_ROOT_DIR}"
    if [[ "$SWEEP_RC" == 2 ]]; then
        test_fail "case13 real sweep" "git could not list the real repo (rc 2)"
        return
    fi
    while IFS= read -r line; do
        [[ "$line" == "MISSING "* ]] || continue
        rel_path="${line#MISSING }"
        if vde_shib_has_literal "${VDE_ROOT_DIR}/${rel_path}"; then
            bad=$(( bad + 1 ))
        fi
    done <<< "${SWEEP_OUT}"
    expect_eq "case13 MISSING lines for files carrying the literal" "$bad" 0
    tracked="$(git -C "${VDE_ROOT_DIR}" ls-files lib/vde-shibboleth 2>/dev/null)"
    if [[ -n "$tracked" ]]; then
        test_pass "case13 lib/vde-shibboleth is tracked"
    else
        test_fail "case13 lib/vde-shibboleth is tracked" "git ls-files lists nothing"
    fi
    if vde_shib_has_literal "${SHIB_LIB}"; then
        test_pass "case13 lib/vde-shibboleth carries the literal"
    else
        test_fail "case13 lib/vde-shibboleth carries the literal" "has_literal rc != 0"
    fi
}

test_case14_baseline_first_creation_is_allowed() {
    test_start "14: the guard allows CREATING the baseline (nothing in HEAD to shrink from)"
    local r out rc
    # 14a: brand-new repo, no commit yet, baseline staged for the first time
    r="$(new_repo c14a)"
    mkdir -p "${r}/docs/governance"
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case14a first creation (no HEAD) output" "$out" ""
    expect_eq "case14a first creation (no HEAD) rc" "$rc" 0
    # 14b: repo already has commits, baseline absent from HEAD, added now
    r="$(new_repo c14b)"
    mk_zsh "${r}/lib/a.zsh" 3
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm base
    mkdir -p "${r}/docs/governance"
    print -rl -- lib/a.zsh lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case14b creation after other commits output" "$out" ""
    expect_eq "case14b creation after other commits rc" "$rc" 0
}

test_case15_non_ascii_filename_is_swept() {
    test_start "15: a tracked zsh file with a non-ASCII name is not silently skipped"
    local r
    r="$(new_repo c15)"
    mk_zsh "${r}/lib/café.zsh" 3
    stage_all "${r}"
    sweep_into "${r}"
    if [[ "${SWEEP_OUT}" == *"MISSING lib/café.zsh"* ]]; then
        test_pass "case15 non-ASCII file reported"
    else
        test_fail "case15 non-ASCII file reported" "sweep said: [${SWEEP_OUT}] rc=${SWEEP_RC}"
    fi
}

test_case16_baseline_is_not_git_ignored() {
    test_start "16: the baseline file must be committable (not swallowed by .gitignore)"
    # Found by mutation-testing the real enforcer: .gitignore carries `*.txt`, which
    # silently excluded the baseline from every copy/commit, so after a merge the
    # sweep would have seen an EMPTY baseline and failed on every grandfathered file.
    # Use the exit status, not the -v text: -v also prints a matching `!` exception
    # (a rule that UN-ignores the file). rc 0 = ignored, rc 1 = not ignored.
    local rel="${VDE_SHIBBOLETH_BASELINE_REL}" rc=0
    git -C "${VDE_ROOT_DIR}" check-ignore -q -- "${rel}" 2>/dev/null || rc=$?
    if (( rc == 1 )); then
        test_pass "case16 baseline path is not git-ignored"
    else
        test_fail "case16 baseline path is not git-ignored" "check-ignore rc=${rc}: $(git -C "${VDE_ROOT_DIR}" check-ignore -v -- "${rel}" 2>&1)"
    fi
}

test_case17_enforcer_sweep_cannot_kill_the_script() {
    test_start "17: bin/vde-enforce-uap.zsh survives the sweep's non-zero status (set -e)"
    # Found by mutation-testing: the enforcer runs under `set -e`, so a bare
    # `out="$(vde_shib_sweep ...)"` aborted the whole audit with exit 1 and NO
    # message exactly when there were violations to report.
    local enforcer="${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" line found=0 guarded=0
    while IFS= read -r line; do
        [[ "${line}" == [[:space:]]#'#'* ]] && continue
        [[ "${line}" == *'$(vde_shib_sweep'* ]] || continue
        found=1
        [[ "${line}" == *'|| '* ]] && guarded=1
    done < "${enforcer}"
    if (( found == 0 )); then
        test_fail "case17 sweep call guarded against set -e" "no \$(vde_shib_sweep ...) call found in the enforcer"
    elif (( guarded == 0 )); then
        test_fail "case17 sweep call guarded against set -e" "the call is not followed by '|| ...' so set -e kills the script"
    else
        test_pass "case17 sweep call guarded against set -e"
    fi
}

run_hook_in() {  # run_hook_in REPO -> runs the REAL pre-commit hook there; sets HOOK_OUT, HOOK_RC
    local r="$1" hook="${SHIB_TEST_HOOK:-${VDE_ROOT_DIR}/githooks/pre-commit}"
    mkdir -p "${r}/lib"
    cp "${VDE_ROOT_DIR}/lib/vde-shibboleth" "${r}/lib/vde-shibboleth"
    HOOK_OUT="$(cd "${r}" && zsh "${hook}" 2>&1)"
    HOOK_RC=$?
}

test_case18_precommit_hook_blocks_baseline_growth() {
    test_start "18: the REAL pre-commit hook rejects baseline additions, allows removals and creation"
    local r
    # 18a: a commit that ADDS an entry to an existing baseline is rejected
    r="$(make_baseline_repo c18a)"
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add docs/governance/shibboleth-baseline.txt
    run_hook_in "${r}"
    expect_eq "case18a addition is blocked (rc)" "$HOOK_RC" 1
    if [[ "${HOOK_OUT}" == *"shrink-only"* && "${HOOK_OUT}" == *"lib/c.zsh"* ]]; then
        test_pass "case18a message names the rule and the added path"
    else
        test_fail "case18a message names the rule and the added path" "hook said: [${HOOK_OUT}]"
    fi
    # 18b: removing an entry is the intended direction and must pass
    r="$(make_baseline_repo c18b)"
    print -rl -- lib/a.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add docs/governance/shibboleth-baseline.txt
    run_hook_in "${r}"
    expect_eq "case18b removal is allowed (rc)" "$HOOK_RC" 0
    # 18c: first creation of the baseline must pass
    r="$(new_repo c18c)"
    mk_zsh "${r}/lib/a.zsh" 3
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm base
    mkdir -p "${r}/docs/governance"
    print -rl -- lib/a.zsh lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add docs/governance/shibboleth-baseline.txt
    run_hook_in "${r}"
    expect_eq "case18c first creation is allowed (rc)" "$HOOK_RC" 0
}

test_case19_guard_survives_color_config() {
    test_start "19: staged-additions guard is not fooled by color.ui=always (review: fail-open)"
    local r out rc
    r="$(make_baseline_repo c19)"
    git -C "${r}" config color.ui always
    git -C "${r}" config color.diff always
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add docs/governance/shibboleth-baseline.txt
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case19 colored diff still reports the addition" "$out" "lib/c.zsh"
    expect_eq "case19 colored diff rc" "$rc" 1
}

test_case20_deleting_the_baseline_is_blocked() {
    test_start "20: deleting the baseline is blocked (closes delete-then-recreate)"
    local r out rc
    r="$(make_baseline_repo c20)"
    git -C "${r}" rm -q docs/governance/shibboleth-baseline.txt
    out="$(vde_shib_staged_baseline_additions "${r}" 2>&1)"; rc=$?
    expect_eq "case20 deletion rc" "$rc" 1
    if [[ "${out}" == *"deleted"* ]]; then
        test_pass "case20 deletion message says deleted"
    else
        test_fail "case20 deletion message says deleted" "got [${out}]"
    fi
}

test_case21_growth_against_base_ref() {
    test_start "21: baseline growth vs a base ref is detected even when the hook was skipped"
    local r out rc
    # 21a: a branch committed (hook bypassed) an extra entry -> reported
    r="$(make_baseline_repo c21a)"
    git -C "${r}" branch -M base
    git -C "${r}" checkout -q -b feat
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm grow
    out="$(vde_shib_baseline_growth "${r}" base 2>&1)"; rc=$?
    expect_eq "case21a growth output" "$out" "lib/c.zsh"
    expect_eq "case21a growth rc" "$rc" 1
    # 21b: a shrink is fine
    r="$(make_baseline_repo c21b)"
    git -C "${r}" branch -M base
    git -C "${r}" checkout -q -b feat
    print -rl -- lib/a.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm shrink
    out="$(vde_shib_baseline_growth "${r}" base 2>&1)"; rc=$?
    expect_eq "case21b shrink output" "$out" ""
    expect_eq "case21b shrink rc" "$rc" 0
    # 21c: base ref has no baseline yet (first creation) -> allowed
    r="$(new_repo c21c)"
    mk_zsh "${r}/lib/a.zsh" 3
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm base
    git -C "${r}" branch -M base
    git -C "${r}" checkout -q -b feat
    mkdir -p "${r}/docs/governance"
    print -rl -- lib/a.zsh lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm create
    out="$(vde_shib_baseline_growth "${r}" base 2>&1)"; rc=$?
    expect_eq "case21c creation output" "$out" ""
    expect_eq "case21c creation rc" "$rc" 0
    # 21d: base ref cannot be resolved -> skipped with rc 3 (the caller prints a notice)
    r="$(make_baseline_repo c21d)"
    out="$(vde_shib_baseline_growth "${r}" no-such-ref 2>&1)"; rc=$?
    expect_eq "case21d unresolvable ref rc" "$rc" 3
}

test_case22_literal_must_be_its_own_line() {
    test_start "22: the literal must be its OWN line (a prefix match is not enough)"
    local r f
    r="$(new_repo c22)"
    f="${r}/lib/tail.zsh"
    mkdir -p "${f:h}"
    printf '#!/usr/bin/env zsh\n%s; echo hi\necho x\n' "${SHIB_LIT}" > "${f}"
    printf '#!/usr/bin/env zsh\n%s   \necho x\n' "${SHIB_LIT}" > "${r}/lib/spaces.zsh"
    printf '#!/usr/bin/env zsh\n%s # because\necho x\n' "${SHIB_LIT}" > "${r}/lib/cmt.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    [[ "${SWEEP_OUT}" == *"MISSING lib/tail.zsh"* ]] && test_pass "case22 'literal; echo hi' is MISSING" || test_fail "case22 'literal; echo hi' is MISSING" "got [${SWEEP_OUT}]"
    [[ "${SWEEP_OUT}" != *"MISSING lib/spaces.zsh"* ]] && test_pass "case22 trailing spaces are tolerated" || test_fail "case22 trailing spaces are tolerated" "got [${SWEEP_OUT}]"
    [[ "${SWEEP_OUT}" == *"MISSING lib/cmt.zsh"* ]] && test_pass "case22 trailing comment is MISSING (own line means own line)" || test_fail "case22 trailing comment is MISSING" "got [${SWEEP_OUT}]"
}

test_case23_dot_zsh_without_shebang_is_in_scope() {
    test_start "23: a *.zsh file with no shebang is still a zsh file"
    local r
    r="$(new_repo c23)"
    mkdir -p "${r}/lib"
    printf 'echo sourced helper\necho more\n' > "${r}/lib/helpers.zsh"
    printf 'echo not a zsh file\n' > "${r}/lib/notes"
    stage_all "${r}"
    sweep_into "${r}"
    [[ "${SWEEP_OUT}" == *"MISSING lib/helpers.zsh"* ]] && test_pass "case23 shebang-less .zsh is MISSING" || test_fail "case23 shebang-less .zsh is MISSING" "got [${SWEEP_OUT}]"
    [[ "${SWEEP_OUT}" != *"lib/notes"* ]] && test_pass "case23 shebang-less non-.zsh stays out of scope" || test_fail "case23 shebang-less non-.zsh stays out of scope" "got [${SWEEP_OUT}]"
}

test_case24_stale_line_survives_spaces_in_paths() {
    test_start "24: STALE lines separate path and reason unambiguously (paths may contain spaces)"
    local r
    r="$(new_repo c24)"
    mkdir -p "${r}/docs/governance"
    print -rl -- 'lib/my tool.zsh' > "${r}/docs/governance/shibboleth-baseline.txt"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case24 exact STALE line" "$SWEEP_OUT" "STALE lib/my tool.zsh :: file not found"
}

test_case25_suite_is_wired_into_the_ci_runner() {
    test_start "25: this suite is listed in tests/run-sovereign-tests.zsh (otherwise CI never runs it)"
    if grep -qF 'shibboleth-check.test.zsh' "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh"; then
        test_pass "case25 suite is in the CI runner list"
    else
        test_fail "case25 suite is in the CI runner list" "tests/run-sovereign-tests.zsh has an explicit file list without this suite"
    fi
}

test_case26_precommit_fails_closed_without_the_lib() {
    test_start "26: pre-commit blocks a staged baseline change when lib/vde-shibboleth is missing"
    local r hook="${SHIB_TEST_HOOK:-${VDE_ROOT_DIR}/githooks/pre-commit}"
    r="$(make_baseline_repo c26)"
    print -rl -- lib/a.zsh lib/b.zsh lib/c.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add docs/governance/shibboleth-baseline.txt
    HOOK_OUT="$(cd "${r}" && zsh "${hook}" 2>&1)"; HOOK_RC=$?
    expect_eq "case26 missing lib blocks the commit (rc)" "$HOOK_RC" 1
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

test_case1_original_gap
test_case2_literal_line3
test_case3_window_edge
test_case4_comment_and_indent_do_not_count
test_case5_non_zsh_ignored
test_case6_uniformity_short_file
test_case7_exclusions
test_case8_baseline_grandfathers
test_case9_stale_entries
test_case10_baseline_comments_and_blanks
test_case11_baseline_print_sorted
test_case12_staged_additions_guard
test_case13_real_repo_sanity
test_case14_baseline_first_creation_is_allowed
test_case15_non_ascii_filename_is_swept
test_case16_baseline_is_not_git_ignored
test_case17_enforcer_sweep_cannot_kill_the_script
test_case18_precommit_hook_blocks_baseline_growth
test_case19_guard_survives_color_config
test_case20_deleting_the_baseline_is_blocked
test_case21_growth_against_base_ref
test_case22_literal_must_be_its_own_line
test_case23_dot_zsh_without_shebang_is_in_scope
test_case24_stale_line_survives_spaces_in_paths
test_case25_suite_is_wired_into_the_ci_runner
test_case26_precommit_fails_closed_without_the_lib

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $TESTS_FAILED
