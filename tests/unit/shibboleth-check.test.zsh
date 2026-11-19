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
    test_start "7: exclusions - only plans/, conductor/ and bin/archive/ are out of scope; docs/, tests/docker/ and .github/ are swept"
    local r f p rc
    r="$(new_repo c7)"
    for f in plans/p.zsh conductor/c.zsh bin/archive/x/a.zsh; do
        mk_zsh "${r}/${f}" 5
    done
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case7 sweep output" "$SWEEP_OUT" ""
    expect_eq "case7 sweep rc" "$SWEEP_RC" 0
    # Clan Leader decision (2026-11-18): docs/, tests/docker/ and .github/ hold no zsh file
    # today, so excluding them hid nothing now but would silently exempt any zsh file added
    # there later. A zsh file in those folders must be reported like any other.
    r="$(new_repo c7b)"
    for f in docs/d.zsh tests/docker/t.zsh .github/g.zsh; do
        mk_zsh "${r}/${f}" 5
    done
    stage_all "${r}"
    sweep_into "${r}"
    # Compared as a sorted set: the sweep's own ordering follows the locale, so the test must not depend on it.
    local -a got_lines=("${(@f)SWEEP_OUT}") want_lines=("MISSING .github/g.zsh" "MISSING docs/d.zsh" "MISSING tests/docker/t.zsh")
    expect_eq "case7 swept-folder output" "${(j:|:)${(@o)got_lines}}" "${(j:|:)${(@o)want_lines}}"
    expect_eq "case7 swept-folder rc" "$SWEEP_RC" 1
    for p in bin/archive/x/y.zsh plans/x.zsh conductor/x.zsh; do
        vde_shib_excluded "$p"; rc=$?
        expect_eq "case7 excluded rc for ${p}" "$rc" 0
    done
    for p in docs/x.zsh tests/docker/x.zsh .github/x.zsh bin/vde lib/x; do
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
    # --no-index: by default git skips TRACKED paths, so a tracked baseline would look
    # "not ignored" even when a rule matches it (Sourcery, PR #635).
    git -C "${VDE_ROOT_DIR}" check-ignore --no-index -q -- "${rel}" 2>/dev/null || rc=$?
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

# --- Sourcery review of PR #635 (each case failed against the code it reviewed) ---

test_case27_special_characters_in_filenames() {
    test_start "27: a tracked zsh file whose name git would QUOTE (tab, backslash) is still swept"
    local r
    r="$(new_repo c27)"
    mkdir -p "${r}/lib"
    printf '#!/usr/bin/env zsh\necho a\necho b\n' > "${r}/lib/tab"$'\t'"name.zsh"
    printf '#!/usr/bin/env zsh\necho a\necho b\n' > "${r}/lib/back\\slash.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    [[ "${SWEEP_OUT}" == *"MISSING lib/tab"$'\t'"name.zsh"* ]] && test_pass "case27 tab in the name is reported" || test_fail "case27 tab in the name is reported" "sweep said: [${SWEEP_OUT}]"
    [[ "${SWEEP_OUT}" == *'MISSING lib/back\slash.zsh'* ]] && test_pass "case27 backslash in the name is reported" || test_fail "case27 backslash in the name is reported" "sweep said: [${SWEEP_OUT}]"
}

test_case28_deleted_baseline_is_growth() {
    test_start "28: deleting the baseline (hook bypassed) is reported against the base ref"
    local r out rc
    r="$(make_baseline_repo c28)"
    git -C "${r}" branch -M base
    git -C "${r}" checkout -q -b feat
    git -C "${r}" rm -q docs/governance/shibboleth-baseline.txt
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm "delete baseline"
    out="$(vde_shib_baseline_growth "${r}" base 2>&1)"; rc=$?
    expect_eq "case28 deleted baseline rc" "$rc" 1
    [[ "${out}" == *deleted* ]] && test_pass "case28 message says deleted" || test_fail "case28 message says deleted" "got [${out}]"
}

test_case29_include_guard_cannot_be_forged_by_the_environment() {
    test_start "29: an exported _VDE_SHIBBOLETH_LOADED=1 must not stop the library from defining its functions"
    local out
    out="$(env _VDE_SHIBBOLETH_LOADED=1 zsh -c "source '${VDE_ROOT_DIR}/lib/vde-shibboleth'; typeset -f vde_shib_sweep >/dev/null && print DEFINED || print MISSING" 2>&1)"
    expect_eq "case29 functions defined despite the forged guard" "$out" "DEFINED"
}

test_case30_ignore_rule_is_tested_even_when_tracked() {
    test_start "30: the ignore check ignores TRACKED status, otherwise a tracked file hides a matching ignore rule"
    local r rc_default=0 rc_noindex=0
    r="$(new_repo c30)"
    print -r -- '*.txt' > "${r}/.gitignore"
    print -r -- x > "${r}/a.txt"
    git -C "${r}" add -f a.txt .gitignore
    git -C "${r}" check-ignore -q -- a.txt 2>/dev/null || rc_default=$?
    git -C "${r}" check-ignore --no-index -q -- a.txt 2>/dev/null || rc_noindex=$?
    expect_eq "case30 default check-ignore skips the tracked file (rc 1: the blind spot)" "$rc_default" 1
    expect_eq "case30 --no-index sees the matching rule (rc 0)" "$rc_noindex" 0
    # and case 16 must use the sensitive form (look only inside case 16's own body,
    # otherwise this very test would satisfy the pin by mentioning the flag)
    awk '/^test_case16_baseline_is_not_git_ignored\(\)/ { f = 1 } f { print } f && /^}/ { exit }' "${VDE_ROOT_DIR}/tests/unit/shibboleth-check.test.zsh" \
        | grep -qE 'check-ignore --no-index -q' \
        && test_pass "case30 case 16 uses check-ignore --no-index" \
        || test_fail "case30 case 16 uses check-ignore --no-index" "case 16 still uses the default form that skips tracked files"
}

test_case31_base_branch_follows_the_configured_anvil() {
    test_start "31: the enforcer's default base ref follows VDE_ANVIL_BRANCH, not a hard-coded develop"
    local l; l="$(grep -m1 -E 'shib_base=' "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh")"
    [[ "${l}" == *VDE_ANVIL_BRANCH* ]] && test_pass "default base ref uses VDE_ANVIL_BRANCH" || test_fail "default base ref uses VDE_ANVIL_BRANCH" "line is: ${l}"
}

test_case32_charter_states_what_the_enforcer_really_does_to_plans() {
    test_start "32: the Sovereign Charter says the enforcer DELETES stray plans/ subfolders (it runs rm -rf there)"
    local enf="${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" ch="${VDE_ROOT_DIR}/docs/governance/sovereign-charter.md" sub
    # only the Forge-only subsection counts (the word "delete" appears elsewhere in the charter)
    sub="$(awk '/^### Forge-only development artifacts/ { f = 1; next } f && /^(##|###) / { exit } f { print }' "${ch}")"
    if grep -qE 'rm -rf "\$\{item\}"' "${enf}" && ! print -r -- "${sub}" | grep -qiE 'delet'; then
        test_fail "charter describes the plans/ ghost-zone deletion" "the enforcer deletes plans/<subdir> (other than scripts and archive) but the charter only says it 'checks'"
    else
        test_pass "charter describes the plans/ ghost-zone deletion"
    fi
}

test_case42_no_doc_calls_the_swept_folders_out_of_scope() {
    test_start "42: no governance doc or library comment lists tests/docker/ (and so docs/, .github/) as out of scope"
    local f line msg=""
    # Clan Leader decision (2026-11-18): docs/, tests/docker/ and .github/ are swept. The old
    # exclusion list was restated in five places and one was missed in review, so every line that
    # names tests/docker (it only ever appeared in that list) must say the folder is swept.
    for f in AGENTS.md .gemini/instructions.md docs/governance/sovereign-charter.md docs/governance/shibboleth-baseline.txt lib/vde-shibboleth; do
        while IFS= read -r line; do
            [[ "${line}" == *swept* ]] || msg+="${f}: ${line[1,60]} | "
        done < <(grep -F 'tests/docker' "${VDE_ROOT_DIR}/${f}")
    done
    expect_eq "case42 stale out-of-scope wording" "${msg}" ""
}

# End to end: the REAL enforcer in a throwaway copy of the tracked tree. Only the
# shibboleth lines are asserted (the other audits are not under test here).
make_forge() {  # make_forge NAME -> prints a git repo holding a copy of this tree, branch "base"
    local f="${TMP_ROOT}/$1"
    mkdir -p "${f}"
    ( cd "${VDE_ROOT_DIR}" && git ls-files -z | xargs -0 cp -a --parents -t "${f}" 2>/dev/null )
    git -C "${f}" init -q
    git -C "${f}" add -A
    git -C "${f}" -c user.email=t@t -c user.name=t commit -qm base
    git -C "${f}" branch -M base
    print -r -- "${f}"
}

run_enforcer_in() {  # run_enforcer_in FORGE BASE_REF -> sets ENF_OUT
    ENF_OUT="$(cd "$1" && VDE_SHIB_BASE_REF="$2" zsh bin/vde-enforce-uap.zsh 2>&1 | sed 's/\x1b\[[0-9;]*m//g')"
}

test_case33_enforcer_end_to_end() {
    test_start "33: the REAL enforcer, end to end in a throwaway copy of the tree"
    local f
    f="$(make_forge e2e)"
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *"Shibboleth sweep clean"* && "${ENF_OUT}" != *"[UAP-ERROR] Shibboleth"* ]] \
        && test_pass "case33a unmodified tree: sweep clean, no shibboleth error" \
        || test_fail "case33a unmodified tree: sweep clean, no shibboleth error" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
    # new unlisted zsh file without the literal
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho hi\n' > "${f}/lib/zz-newfile"
    git -C "${f}" add -A
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *"[UAP-ERROR] Shibboleth MISSING in lib/zz-newfile"* ]] \
        && test_pass "case33b a new unlisted file is reported by the enforcer" \
        || test_fail "case33b a new unlisted file is reported by the enforcer" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
    git -C "${f}" reset -q --hard
    # base ref unavailable: the check must FAIL CLOSED, not skip silently
    run_enforcer_in "${f}" no-such-ref
    [[ "${ENF_OUT}" == *"[UAP-ERROR] Shibboleth baseline growth could not be checked"* ]] \
        && test_pass "case33c an unavailable base ref is an error, not a skip" \
        || test_fail "case33c an unavailable base ref is an error, not a skip" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
    # a commit that grew the baseline (hook bypassed)
    git -C "${f}" checkout -q -b feat
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho hi\n' > "${f}/lib/zz-grown"
    print -r -- 'lib/zz-grown' >> "${f}/docs/governance/shibboleth-baseline.txt"
    git -C "${f}" add -A
    git -C "${f}" -c user.email=t@t -c user.name=t commit -qm grow
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *"[UAP-ERROR] Shibboleth baseline GREW"* ]] \
        && test_pass "case33d a baseline grown by a commit is reported" \
        || test_fail "case33d a baseline grown by a commit is reported" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
}

# --- second review of the hardening (each case failed against the code it reviewed) ---

test_case34_an_unreadable_index_is_an_error_not_clean() {
    test_start "34: a corrupt git index makes the sweep fail (rc 2), it must not report clean"
    local r out rc
    r="$(new_repo c34)"
    mk_zsh "${r}/lib/a.zsh" 3
    stage_all "${r}"
    head -c 10 "${r}/.git/index" > "${r}/.git/index.cut" && mv -f "${r}/.git/index.cut" "${r}/.git/index"
    out="$(vde_shib_sweep "${r}" 2>&1)"; rc=$?
    expect_eq "case34 corrupt index rc" "$rc" 2
}

test_case35_literal_on_an_unterminated_last_line() {
    test_start "35: the literal on a final line WITHOUT a trailing newline still counts"
    local r
    r="$(new_repo c35)"
    mkdir -p "${r}/lib"
    printf '#!/usr/bin/env zsh\necho a\n%s' "${SHIB_LIT}" > "${r}/lib/nonl.zsh"
    stage_all "${r}"
    sweep_into "${r}"
    [[ "${SWEEP_OUT}" != *"MISSING lib/nonl.zsh"* ]] && test_pass "case35 unterminated last line is accepted" || test_fail "case35 unterminated last line is accepted" "sweep said: [${SWEEP_OUT}]"
}

test_case36_an_unreadable_zsh_file_is_reported() {
    test_start "36: a tracked *.zsh file that cannot be read is reported, not silently skipped"
    if (( EUID == 0 )); then echo "[SKIP] running as root: chmod 000 does not stop root from reading"; return 0; fi
    local r
    r="$(new_repo c36)"
    mk_zsh "${r}/lib/locked.zsh" 3
    stage_all "${r}"
    chmod 000 "${r}/lib/locked.zsh"
    sweep_into "${r}"
    chmod 644 "${r}/lib/locked.zsh"
    [[ "${SWEEP_OUT}" == *"UNREADABLE lib/locked.zsh"* ]] && test_pass "case36 unreadable file is reported" || test_fail "case36 unreadable file is reported" "sweep said: [${SWEEP_OUT}] rc=${SWEEP_RC}"
}

test_case37_fetching_the_base_ref_never_truncates_history() {
    test_start "37: ensuring the base ref keeps a FULL clone full and a SHALLOW clone shallow"
    local o w full shallow
    o="${TMP_ROOT}/c37-origin.git"
    w="$(new_repo c37-work)"
    git init -q --bare "${o}"
    # The bare origin's HEAD must name the only branch we push, otherwise a clone checks
    # out an unborn `main` and holds nothing to measure.
    git --git-dir="${o}" symbolic-ref HEAD refs/heads/develop
    mk_zsh "${w}/lib/a.zsh" 3
    git -C "${w}" add -A
    git -C "${w}" -c user.email=t@t -c user.name=t commit -qm one
    echo 'echo more' >> "${w}/lib/a.zsh"
    git -C "${w}" -c user.email=t@t -c user.name=t commit -qam two
    echo 'echo more2' >> "${w}/lib/a.zsh"
    git -C "${w}" -c user.email=t@t -c user.name=t commit -qam three
    git -C "${w}" branch -M develop
    git -C "${w}" remote add origin "file://${o}"
    git -C "${w}" push -q origin develop
    # (a) full clone, remote-tracking ref removed
    full="${TMP_ROOT}/c37-full"
    git clone -q "file://${o}" "${full}"
    git -C "${full}" update-ref -d refs/remotes/origin/develop
    vde_shib_ensure_base_ref "${full}" origin/develop; local rc_full=$?
    expect_eq "case37a base ref resolves (rc)" "$rc_full" 0
    expect_eq "case37a a full clone stays full" "$(git -C "${full}" rev-parse --is-shallow-repository)" "false"
    expect_eq "case37a all 3 commits are still there" "$(git -C "${full}" rev-list --count HEAD)" "3"
    # (b) shallow clone stays shallow (CI)
    shallow="${TMP_ROOT}/c37-shallow"
    git clone -q --depth=1 "file://${o}" "${shallow}"
    git -C "${shallow}" update-ref -d refs/remotes/origin/develop
    vde_shib_ensure_base_ref "${shallow}" origin/develop; local rc_sh=$?
    expect_eq "case37b base ref resolves in a shallow clone (rc)" "$rc_sh" 0
    expect_eq "case37b a shallow clone stays shallow" "$(git -C "${shallow}" rev-parse --is-shallow-repository)" "true"
    # (c) a ref that cannot exist is rc 3
    vde_shib_ensure_base_ref "${full}" origin/no-such-branch; local rc_missing=$?
    expect_eq "case37c a missing ref is rc 3" "$rc_missing" 3
}

test_case38_enforcer_messages_keep_backslashes_in_file_names() {
    test_start "38: the enforcer prints a file name containing a backslash exactly as it is (no echo -e mangling)"
    local f
    f="$(make_forge e2e-bs)"
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho hi\n' > "${f}/lib/zz-b\\nz.zsh"
    git -C "${f}" add -A
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *'Shibboleth MISSING in lib/zz-b\nz.zsh'* ]] \
        && test_pass "case38 backslash-n in a file name is printed literally" \
        || test_fail "case38 backslash-n in a file name is printed literally" "$(print -r -- "${ENF_OUT}" | grep -i 'zz-b' | head -2)"
}

# --- third review (each case failed against the code it reviewed) ---

test_case39_a_stale_branch_is_not_blamed_for_the_base_shrinking() {
    test_start "39: growth is measured from the MERGE-BASE, so a branch cut before the base shrank is not reported as growth"
    local r out rc
    r="$(make_baseline_repo c39)"
    git -C "${r}" branch -M base
    git -C "${r}" checkout -q -b feat
    mk_zsh "${r}/lib/unrelated.zsh" 3 3
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm "unrelated work on the feature branch"
    git -C "${r}" checkout -q base
    print -rl -- lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    git -C "${r}" add -A
    git -C "${r}" -c user.email=t@t -c user.name=t commit -qm "base shrinks the baseline (lib/a.zsh gained the line)"
    git -C "${r}" checkout -q feat
    out="$(vde_shib_baseline_growth "${r}" base 2>&1)"; rc=$?
    expect_eq "case39 an untouched stale baseline is not growth (rc)" "$rc" 0
    expect_eq "case39 nothing is reported" "$out" ""
}

test_case40_precommit_does_not_call_a_deletion_an_addition() {
    test_start "40: the pre-commit message for a deleted baseline must not say a line was ADDED"
    local r
    r="$(make_baseline_repo c40)"
    git -C "${r}" rm -q docs/governance/shibboleth-baseline.txt
    run_hook_in "${r}"
    expect_eq "case40 deleting the baseline is blocked (rc)" "$HOOK_RC" 1
    [[ "${HOOK_OUT}" != *"Added to"* ]] && test_pass "case40 the message does not claim an addition" || test_fail "case40 the message does not claim an addition" "hook said: [${HOOK_OUT}]"
}

test_case41_the_base_fetch_never_prompts() {
    test_start "41: the best-effort base fetch cannot hang on a credential prompt"
    awk '/^vde_shib_ensure_base_ref\(\)/ { f = 1 } f { print } f && /^}/ { exit }' "${VDE_ROOT_DIR}/lib/vde-shibboleth" | grep -q 'GIT_TERMINAL_PROMPT=0' \
        && test_pass "case41 the fetch sets GIT_TERMINAL_PROMPT=0" \
        || test_fail "case41 the fetch sets GIT_TERMINAL_PROMPT=0" "a pre-push hook could block on a prompt"
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
test_case27_special_characters_in_filenames
test_case28_deleted_baseline_is_growth
test_case29_include_guard_cannot_be_forged_by_the_environment
test_case30_ignore_rule_is_tested_even_when_tracked
test_case31_base_branch_follows_the_configured_anvil
test_case32_charter_states_what_the_enforcer_really_does_to_plans
test_case33_enforcer_end_to_end
test_case34_an_unreadable_index_is_an_error_not_clean
test_case35_literal_on_an_unterminated_last_line
test_case36_an_unreadable_zsh_file_is_reported
test_case37_fetching_the_base_ref_never_truncates_history
test_case38_enforcer_messages_keep_backslashes_in_file_names
test_case39_a_stale_branch_is_not_blamed_for_the_base_shrinking
test_case40_precommit_does_not_call_a_deletion_an_addition
test_case41_the_base_fetch_never_prompts
test_case42_no_doc_calls_the_swept_folders_out_of_scope

# ---------------------------------------------------------------------------
# Signet #645: the sweep judges the right bytes and classifies files by interpreter
# ---------------------------------------------------------------------------

commit_all() {  # commit_all REPO MESSAGE
    git -C "$1" add -A
    git -C "$1" -c user.email=t@t -c user.name=t -c commit.gpgsign=false commit -q -m "$2"
}

snap_into() {  # snap_into ROOT SOURCE [BASELINE_REL] -> sets SNAP_OUT, SNAP_RC
    SNAP_OUT="$(vde_shib_sweep_snapshot "$@" 2>&1)"
    SNAP_RC=$?
}

test_case43_shebang_matches_the_interpreter_not_a_substring() {
    test_start "43: the shebang test matches the zsh INTERPRETER, not the word zsh anywhere on line 1"
    local line f rc r n=0
    local -a yes=('#!/usr/bin/env zsh' '#!/bin/zsh' '#!/usr/bin/zsh' '#!/usr/bin/env -S zsh -f' '#! /bin/zsh -f' '#!/opt/homebrew/bin/zsh' '#!/usr/bin/env zsh -f' '#!/usr/bin/env -- zsh' '#!/usr/bin/env ZDOTDIR=/tmp zsh' '#!/usr/bin/env -S ZDOTDIR=/tmp zsh -f' '#!/usr/local/bin/zsh-5.9' '#!/usr/bin/zsh5' '#!/usr/bin/env zsh5' '#!/usr/bin/zsh-static')
    local -a no=('#!/bin/bash # zsh is not used here' '#!/usr/bin/env bash' '#!/bin/sh' '#!/usr/bin/env python3 # zsh' '#!/bin/zshfoo' '#!/usr/bin/env bash -c zsh' '#!/usr/bin/env zshfoo' '#!/usr/bin/env FOO=bar bash')
    for line in "${yes[@]}"; do
        f="${TMP_ROOT}/sb43-${n}"; (( ++n ))
        printf '%s\necho hi\n' "${line}" > "${f}"
        vde_shib_is_zsh "${f}"; rc=$?
        expect_eq "case43 accepts [${line}]" "${rc}" 0
    done
    for line in "${no[@]}"; do
        f="${TMP_ROOT}/sb43-${n}"; (( ++n ))
        printf '%s\necho hi\n' "${line}" > "${f}"
        vde_shib_is_zsh "${f}"; rc=$?
        expect_eq "case43 rejects [${line}]" "${rc}" 1
    done
    # at sweep level: a bash script that merely mentions zsh is not asked for the literal
    r="$(new_repo c43)"
    mkdir -p "${r}/lib"
    printf '#!/bin/bash # zsh is not used here\necho hi\n' > "${r}/lib/tool"
    chmod +x "${r}/lib/tool"
    stage_all "${r}"
    sweep_into "${r}"
    expect_eq "case43 sweep output for a bash script that mentions zsh" "${SWEEP_OUT}" ""
    expect_eq "case43 sweep rc for a bash script that mentions zsh" "${SWEEP_RC}" 0
}

test_case44_an_unreadable_baseline_entry_is_not_also_called_stale() {
    test_start "44: an unreadable baseline entry is reported once, as UNREADABLE, and never as STALE 'not a zsh file'"
    local r
    r="$(make_baseline_repo c44)"
    chmod 000 "${r}/lib/a.zsh"
    if [[ -r "${r}/lib/a.zsh" ]]; then
        chmod 644 "${r}/lib/a.zsh"
        test_pass "case44 skipped: this user can read a mode-000 file (running as root)"
        return
    fi
    sweep_into "${r}"
    chmod 644 "${r}/lib/a.zsh"
    expect_eq "case44 output" "${SWEEP_OUT}" "UNREADABLE lib/a.zsh"
    expect_eq "case44 rc" "${SWEEP_RC}" 1
    # the same for an entry without the .zsh suffix: it cannot be classified (its shebang cannot be
    # read), so it is neither UNREADABLE nor 'STALE: not a zsh file' (review, Signet #645)
    r="$(new_repo c44b)"
    mkdir -p "${r}/lib" "${r}/docs/governance"
    printf '#!/usr/bin/env zsh\necho hi\n' > "${r}/lib/tool"
    print -r -- 'lib/tool' > "${r}/docs/governance/shibboleth-baseline.txt"
    commit_all "${r}" base
    chmod 000 "${r}/lib/tool"
    sweep_into "${r}"
    chmod 644 "${r}/lib/tool"
    expect_eq "case44b an unreadable extensionless baseline entry is not called stale" "${SWEEP_OUT}" ""
    # but an unreadable entry that is not even a tracked file is still reported (nothing else reports it)
    r="$(new_repo c44c)"
    mkdir -p "${r}/lib" "${r}/docs/governance"
    print -r -- readme > "${r}/README"
    commit_all "${r}" base
    printf '#!/usr/bin/env zsh\necho hi\n' > "${r}/lib/ghost.zsh"
    print -r -- 'lib/ghost.zsh' > "${r}/docs/governance/shibboleth-baseline.txt"
    chmod 000 "${r}/lib/ghost.zsh"
    sweep_into "${r}"
    chmod 644 "${r}/lib/ghost.zsh"
    [[ "${SWEEP_OUT}" == "STALE lib/ghost.zsh :: unreadable"* ]] \
        && test_pass "case44c an unreadable, untracked baseline entry is reported stale for the TRUE reason" \
        || test_fail "case44c an unreadable, untracked baseline entry is reported stale for the TRUE reason" "output [${SWEEP_OUT}]"
}

test_case45_committed_and_staged_content_is_judged_not_the_working_copy() {
    test_start "45: vde_shib_sweep_snapshot judges the COMMITTED (head) or STAGED (index) bytes, not the working copy"
    local r
    r="$(new_repo c45)"
    mk_zsh "${r}/lib/x.zsh" 3
    commit_all "${r}" base
    # a: the literal is only in the UNSTAGED working copy
    mk_zsh "${r}/lib/x.zsh" 3 2
    sweep_into "${r}"
    expect_eq "case45a the working-tree sweep is clean" "${SWEEP_OUT}" ""
    snap_into "${r}" head
    expect_eq "case45a the committed version still lacks it" "${SNAP_OUT}" "COMMITTED lib/x.zsh"
    expect_eq "case45a rc" "${SNAP_RC}" 1
    snap_into "${r}" index
    expect_eq "case45a nothing is staged, so the index view is silent" "${SNAP_OUT}" ""
    # b: staged (still not committed)
    git -C "${r}" add -A
    snap_into "${r}" index
    expect_eq "case45b the staged version carries it" "${SNAP_OUT}" ""
    snap_into "${r}" head
    expect_eq "case45b the committed version still lacks it" "${SNAP_OUT}" "COMMITTED lib/x.zsh"
    # c: committed
    commit_all "${r}" fix
    snap_into "${r}" head
    expect_eq "case45c clean once the fix is committed" "${SNAP_OUT}" ""
    expect_eq "case45c rc" "${SNAP_RC}" 0
    # d: a NEW staged file without the literal
    mk_zsh "${r}/lib/new.zsh" 3
    git -C "${r}" add -A
    snap_into "${r}" index
    expect_eq "case45d a new staged violator is reported by the index view" "${SNAP_OUT}" "STAGED lib/new.zsh"
    snap_into "${r}" head
    expect_eq "case45d it is not in HEAD, so the head view is silent" "${SNAP_OUT}" ""
    # d2: the index holds a good version, the working copy was stripped afterwards
    mk_zsh "${r}/lib/new.zsh" 3 2
    git -C "${r}" add -A
    mk_zsh "${r}/lib/new.zsh" 3
    snap_into "${r}" index
    expect_eq "case45d2 the index view judges the staged bytes, not the stripped working copy" "${SNAP_OUT}" ""
    # e: an uncommitted deletion of a file whose committed version violates
    r="$(new_repo c45e)"
    mk_zsh "${r}/lib/v.zsh" 3
    commit_all "${r}" base
    command rm -- "${r}/lib/v.zsh"
    snap_into "${r}" head
    expect_eq "case45e a deleted-but-committed violator is still reported (the push carries it)" "${SNAP_OUT}" "COMMITTED lib/v.zsh"
    # f: excluded paths stay out of scope
    r="$(new_repo c45f)"
    mk_zsh "${r}/plans/p.zsh" 3
    commit_all "${r}" base
    mk_zsh "${r}/plans/p.zsh" 4
    snap_into "${r}" head
    expect_eq "case45f an excluded path is silent" "${SNAP_OUT}" ""
    # g: a grandfathered violator listed in the COMMITTED baseline is silent
    r="$(make_baseline_repo c45g)"
    mk_zsh "${r}/lib/a.zsh" 4
    snap_into "${r}" head
    expect_eq "case45g a baseline-listed file is silent in the head view" "${SNAP_OUT}" ""
    # i: a staged RENAME of a committed violator: the old path is still what HEAD carries
    r="$(new_repo c45i)"
    mk_zsh "${r}/lib/old.zsh" 3
    commit_all "${r}" base
    git -C "${r}" mv lib/old.zsh lib/new.zsh
    mk_zsh "${r}/lib/new.zsh" 3 2
    git -C "${r}" add -A
    snap_into "${r}" head
    expect_eq "case45i a renamed committed violator is still reported under its old path" "${SNAP_OUT}" "COMMITTED lib/old.zsh"
    snap_into "${r}" index
    expect_eq "case45i the staged new path carries the literal" "${SNAP_OUT}" ""
    # j: the check must FAIL CLOSED: an error is rc 2 with a message, never an empty clean result
    r="$(new_repo c45j)"
    mk_zsh "${r}/lib/x.zsh" 3
    commit_all "${r}" base
    SNAP_OUT="$(TMPDIR=/nonexistent-dir vde_shib_sweep_snapshot "${r}" head 2>&1)"; SNAP_RC=$?
    expect_eq "case45j no temp dir: rc 2" "${SNAP_RC}" 2
    [[ "${SNAP_OUT}" == *"ERROR cannot create a temporary directory"* ]] \
        && test_pass "case45j no temp dir: an ERROR line is printed" \
        || test_fail "case45j no temp dir: an ERROR line is printed" "output [${SNAP_OUT}]"
    printf 'not an index' > "${r}/.git/index"
    snap_into "${r}" head
    expect_eq "case45j a broken index: rc 2" "${SNAP_RC}" 2
    [[ "${SNAP_OUT}" == *"ERROR cannot list the files changed since HEAD"* ]] \
        && test_pass "case45j a broken index: an ERROR line is printed" \
        || test_fail "case45j a broken index: an ERROR line is printed" "output [${SNAP_OUT}]"
    # k: the baseline that grandfathers a file must be HEAD's, not an uncommitted edit of it
    r="$(make_baseline_repo c45k)"
    print -r -- lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    commit_all "${r}" "shrink: a.zsh leaves the baseline although it still violates"
    print -rl -- lib/a.zsh lib/b.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    sweep_into "${r}"
    expect_eq "case45k the working-tree sweep is clean (the uncommitted baseline grandfathers a.zsh)" "${SWEEP_OUT}" ""
    snap_into "${r}" head
    expect_eq "case45k the committed bytes still violate: HEAD's baseline does not list a.zsh" "${SNAP_OUT}" "COMMITTED lib/a.zsh"
    # l: a committed blob that exists in the tree but cannot be read is an ERROR (rc 2), never "clean"
    r="$(new_repo c45l)"
    mk_zsh "${r}/lib/y.zsh" 3
    commit_all "${r}" base
    local sha
    sha="$(git -C "${r}" rev-parse HEAD:lib/y.zsh)"
    # The file is looked at because an UNCOMMITTED baseline entry names it (so `git diff` itself,
    # which would also fail on a damaged blob, is not the thing that notices).
    mkdir -p "${r}/docs/governance"
    print -r -- lib/y.zsh > "${r}/docs/governance/shibboleth-baseline.txt"
    command rm -f -- "${r}/.git/objects/${sha[1,2]}/${sha[3,-1]}"
    snap_into "${r}" head
    expect_eq "case45l an unreadable committed blob: rc 2" "${SNAP_RC}" 2
    [[ "${SNAP_OUT}" == *"ERROR cannot read the committed content of lib/y.zsh"* ]] \
        && test_pass "case45l an unreadable committed blob: the file is named in an ERROR line" \
        || test_fail "case45l an unreadable committed blob: the file is named in an ERROR line" "output [${SNAP_OUT}]"
    # m: a symlink is not file content: its target is judged as its own path
    r="$(new_repo c45m)"
    mk_zsh "${r}/lib/other.zsh" 3 2
    ln -s other.zsh "${r}/lib/link.zsh"
    git -C "${r}" add -A
    snap_into "${r}" index
    expect_eq "case45m a staged symlink is not judged by its link text" "${SNAP_OUT}" ""
    # n: under set -e (the pre-commit hook runs with it) a clean blob must not end the sweep early
    r="$(new_repo c45n)"
    mk_zsh "${r}/lib/a.zsh" 3 2
    mk_zsh "${r}/lib/b.zsh" 3
    git -C "${r}" add -A
    # Called plainly: errexit is suspended inside anything on the left of `||`, which would hide the abort.
    SNAP_OUT="$(zsh -e -c 'source "$1"; vde_shib_sweep_snapshot "$2" index' _ "${SHIB_LIB}" "${r}" 2>&1)"
    expect_eq "case45n under set -e the violator after a clean file is still reported" "${SNAP_OUT}" "STAGED lib/b.zsh"
    # h: an unknown source is an error; an unborn HEAD has nothing committed to judge
    snap_into "${r}" bogus
    expect_eq "case45h an unknown source is rc 2" "${SNAP_RC}" 2
    r="$(new_repo c45h)"
    mk_zsh "${r}/lib/u.zsh" 3
    git -C "${r}" add -A
    snap_into "${r}" head
    expect_eq "case45h unborn HEAD: nothing committed to judge" "${SNAP_RC}" 0
    snap_into "${r}" index
    expect_eq "case45h unborn HEAD: the staged file is still judged" "${SNAP_OUT}" "STAGED lib/u.zsh"
}

test_case46_the_audit_reports_a_violation_only_the_commit_has() {
    test_start "46: the REAL audit fails when the commit lacks the shibboleth even though the working copy has it"
    local f
    f="$(make_forge e2e46)"
    git -C "${f}" checkout -q -b feat46
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho hi\n' > "${f}/lib/zz-committed.zsh"
    commit_all "${f}" "violating commit"
    printf '#!/usr/bin/env zsh\n# @forge (t)\n%s\necho hi\n' "${SHIB_LIT}" > "${f}/lib/zz-committed.zsh"
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *"[UAP-ERROR] Shibboleth MISSING in the COMMITTED version of lib/zz-committed.zsh"* && "${ENF_OUT}" != *"Shibboleth sweep clean"* ]] \
        && test_pass "case46a an uncommitted fix does not hide the committed violation" \
        || test_fail "case46a an uncommitted fix does not hide the committed violation" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
    commit_all "${f}" "fix"
    run_enforcer_in "${f}" base
    [[ "${ENF_OUT}" == *"Shibboleth sweep clean"* && "${ENF_OUT}" != *"[UAP-ERROR] Shibboleth MISSING"* ]] \
        && test_pass "case46b the audit is clean once the fix is committed" \
        || test_fail "case46b the audit is clean once the fix is committed" "$(print -r -- "${ENF_OUT}" | grep -i shibboleth | head -3)"
    # a file that violates in BOTH the working copy and the commit is reported once, not twice
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho one\n' > "${f}/lib/zz-both.zsh"
    commit_all "${f}" "second violator"
    printf '#!/usr/bin/env zsh\n# @forge (t)\necho two\n' > "${f}/lib/zz-both.zsh"
    run_enforcer_in "${f}" base
    local -i seen
    seen=$(print -r -- "${ENF_OUT}" | grep -c -F 'Shibboleth MISSING') || true
    expect_eq "case46c a violator in both the working copy and the commit is reported once" "${seen}" 1
    # the committed-bytes check cannot run (no temp dir): the audit must fail, never print "clean"
    f="$(make_forge e2e46d)"
    ENF_OUT="$(cd "${f}" && TMPDIR=/nonexistent-dir VDE_SHIB_BASE_REF=base zsh bin/vde-enforce-uap.zsh 2>&1 | sed 's/\x1b\[[0-9;]*m//g')"
    # Either layer may report it: the library's own ERROR line, or the audit's guard for a silent rc 2.
    [[ ( "${ENF_OUT}" == *"[UAP-ERROR] ERROR"* || "${ENF_OUT}" == *"[UAP-ERROR] Shibboleth committed-content check failed"* ) && "${ENF_OUT}" != *"Shibboleth sweep clean"* ]] \
        && test_pass "case46d a committed-bytes check that cannot run fails the audit" \
        || test_fail "case46d a committed-bytes check that cannot run fails the audit" "$(print -r -- "${ENF_OUT}" | grep -i -E 'shibboleth|ERROR' | head -3)"
}

test_case43_shebang_matches_the_interpreter_not_a_substring
test_case44_an_unreadable_baseline_entry_is_not_also_called_stale
test_case45_committed_and_staged_content_is_judged_not_the_working_copy
test_case46_the_audit_reports_a_violation_only_the_commit_has

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $TESTS_FAILED
