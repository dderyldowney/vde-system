#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: per-commit gate certification (Signet #770, revision 2026-11-26: two tiers).
#
# A push certifies every commit of its range, oldest first. Each earlier commit gets the fast tier;
# the tip gets the full tier. Each tree is checked in a throwaway detached worktree and stamped per
# tree (lib/vde-pol-stamp, lib/vde-gate-commits, githooks/proof-of-life-hook.zsh, githooks/gate-tree.zsh).
# Every check run here is a stub: no containers, no network, and every fixture lives in the scratch area.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Fixture isolation (Signet #656): the GIT_* variables that select a repository would send the fixtures
# into the ENCLOSING repository. The ones that inject config or hooks are dropped too.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
# An inherited stamp TTL would change every expiry check: each check starts from the default (1800 s).
unset VDE_POL_STAMP_TTL

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { print -P "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { print -P "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; ((TESTS_FAILED++)); return 0; }

# verdict <label> <status> <detail>: status 0 means the assertion holds.
verdict() {
    if (( $2 == 0 )); then test_pass "$1"; else test_fail "$1" "$3"; fi
    return 0
}

# The libraries under test. A missing library makes the checks that need it fail, by name.
typeset LIB_STAMP="${VDE_ROOT_DIR}/lib/vde-pol-stamp"
typeset LIB_COMMITS="${VDE_ROOT_DIR}/lib/vde-gate-commits"
[[ -f "${LIB_STAMP}" ]] && source "${LIB_STAMP}"
[[ -f "${LIB_COMMITS}" ]] && source "${LIB_COMMITS}"

typeset gate_scratch
gate_scratch="$(vde_test_env_dir)" || exit 1
[[ -n "${gate_scratch}" ]] || exit 1

typeset ZERO40="0000000000000000000000000000000000000000"
typeset UNKNOWN40="1111111111111111111111111111111111111111"
typeset OUT="" RC=0

# run_in <dir> <command...>: runs the command in <dir>; output goes to OUT, status to RC.
run_in() {
    typeset dir="$1"; shift
    OUT="$(cd "${dir}" && "$@" 2>&1)"; RC=$?
}

# expect_rc <label> ok|fail <detail>: checks RC from the last run_in.
expect_rc() {
    typeset label="$1" want="$2" detail="$3"
    # 127 is "command not found" (the function is missing): never a pass, even for an expected refusal.
    if (( RC == 127 )); then
        test_fail "${label}" "${detail}: the function is not defined (${OUT[1,200]})"
    elif [[ "${want}" == ok ]]; then
        if (( RC == 0 )); then test_pass "${label}"; else test_fail "${label}" "${detail} (rc ${RC}: ${OUT[1,200]})"; fi
    else
        if (( RC != 0 )); then test_pass "${label}"; else test_fail "${label}" "${detail} (rc ${RC}, a refusal was expected)"; fi
    fi
}

make_repo() {
    mkdir -p "$1" && git -C "$1" init -q 2>/dev/null && git -C "$1" config user.email t@t && git -C "$1" config user.name t
}

# commit_in <dir> <subject> [content]: appends the content to f and commits; no content = an empty commit.
commit_in() {
    typeset dir="$1" subject="$2" content="$3"
    if [[ -n "${content}" ]]; then
        print -r -- "${content}" >> "${dir}/f"
        git -C "${dir}" add f && git -C "${dir}" commit -qm "${subject}"
    else
        git -C "${dir}" commit -q --allow-empty -m "${subject}"
    fi
}

# =====================================================================================
# A. Stamp store (lib/vde-pol-stamp): per-tree stamps, tiers, expiry, symlinks, common dir
# =====================================================================================
typeset srepo="${gate_scratch}/stamp-repo"
make_repo "${srepo}"
commit_in "${srepo}" one one
typeset T1="$(git -C "${srepo}" rev-parse 'HEAD^{tree}')"
typeset SDIR="${srepo:A}/.git/vde-gate-stamps"
typeset LINKED="${gate_scratch}/stamp-linked"

test_start "stamp store: vde_stamp_dir names <git common dir>/vde-gate-stamps"
run_in "${srepo}" vde_stamp_dir
[[ "${OUT:A}" == "${SDIR}" ]]; verdict "the store is the common dir's vde-gate-stamps" $? "vde_stamp_dir printed [${OUT[1,200]}], expected ${SDIR}"

test_start "stamp store: a linked worktree resolves to the same store"
git -C "${srepo}" worktree add -q --detach "${LINKED}" HEAD 2>/dev/null
run_in "${LINKED}" vde_stamp_dir
[[ "${OUT:A}" == "${SDIR}" ]]; verdict "the linked worktree shares the common store" $? "vde_stamp_dir in the linked worktree printed [${OUT[1,200]}], expected ${SDIR}"

test_start "stamp write: a full stamp is written for one tree and validates for that tree"
run_in "${srepo}" vde_stamp_write "${T1}" full
expect_rc "vde_stamp_write of a valid tree succeeds" ok "the write was refused"
typeset stamp_text=""
[[ -f "${SDIR}/${T1}" ]] && stamp_text="$(<"${SDIR}/${T1}")"
[[ "${stamp_text}" == <->" full" ]]; verdict "the stamp file holds '<epoch> full'" $? "stamp file content was [${stamp_text}]"
run_in "${srepo}" vde_stamp_valid "${T1}" full
expect_rc "the full stamp validates for its own tree" ok "a fresh full stamp was not valid"

test_start "stamp write: a stamp does not validate for another tree"
commit_in "${srepo}" two two
typeset T2="$(git -C "${srepo}" rev-parse 'HEAD^{tree}')"
run_in "${srepo}" vde_stamp_valid "${T2}" fast
expect_rc "a tree with no stamp is not valid" fail "tree T2 was accepted with only T1 stamped"

test_start "stamp expiry: a backdated stamp is not valid"
mkdir -p "${SDIR}"
print -r -- "1000 full" > "${SDIR}/${T1}"
run_in "${srepo}" vde_stamp_valid "${T1}" full
expect_rc "an expired stamp is refused" fail "a stamp from epoch 1000 was still valid"
run_in "${srepo}" vde_stamp_write "${T1}" full
expect_rc "the tree is restamped after the expired stamp" ok "the rewrite was refused"

test_start "stamp tree argument: a non-hex name is refused for read and for write"
run_in "${srepo}" vde_stamp_valid "not-a-tree" fast
expect_rc "vde_stamp_valid refuses a non-hex tree" fail "a non-hex tree name was accepted"
run_in "${srepo}" vde_stamp_valid "../x" full
expect_rc "vde_stamp_valid refuses a path-like tree name" fail "a path-like tree name was accepted"
run_in "${srepo}" vde_stamp_write "not-a-tree" full
expect_rc "vde_stamp_write refuses a non-hex tree" fail "a non-hex tree name was written"
[[ ! -e "${SDIR}/not-a-tree" ]]; verdict "no file was written for the non-hex name" $? "a file named not-a-tree exists in the store"

test_start "stamp symlink: a symlink in the store is refused even when its target is fresh"
typeset FAKE="0123456789abcdef0123456789abcdef01234567"
print -r -- "$(date +%s) full" > "${gate_scratch}/sym-target"
mkdir -p "${SDIR}"
ln -sf "${gate_scratch}/sym-target" "${SDIR}/${FAKE}"
run_in "${srepo}" vde_stamp_valid "${FAKE}" full
expect_rc "a symlinked stamp is refused" fail "a symlink stamp with a fresh target was accepted"

test_start "stamp store: a stamp written from a linked worktree lands in the common store, and validates there"
run_in "${srepo}" vde_stamp_write "${T1}" full
run_in "${LINKED}" vde_stamp_valid "${T1}" full
expect_rc "a linked worktree validates the main worktree's stamp" ok "the linked worktree did not see the stamp"
typeset TIP2="$(git -C "${srepo}" rev-parse HEAD)"
run_in "${LINKED}" vde_stamp_write "${T2}" fast "${TIP2}"
expect_rc "a linked worktree writes a fast stamp for T2 at its commit" ok "the linked worktree could not write"
[[ -f "${SDIR}/${T2}.${TIP2}" ]]; verdict "the linked worktree's fast stamp is in the common store, named <tree>.<commit>" $? "no ${T2}.${TIP2} in ${SDIR}"

test_start "stamp tiers: a fast stamp satisfies a fast request for its own commit"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${TIP2}"
expect_rc "the fast stamp satisfies a fast request for its commit" ok "the fast stamp was not valid for its own commit"

test_start "stamp tiers: a fast stamp does not satisfy a fast request for another commit with the same tree"
commit_in "${srepo}" two-empty ""
typeset E2="$(git -C "${srepo}" rev-parse HEAD)"
[[ "$(git -C "${srepo}" rev-parse "${E2}^{tree}")" == "${T2}" ]]; verdict "fixture: the empty commit has tree T2" $? "the empty commit's tree differs from T2"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${E2}"
expect_rc "a fast stamp for another commit with the same tree is refused" fail "the fast stamp for TIP2 satisfied a fast request for E2"

test_start "stamp tiers: a fast stamp never satisfies a full request"
run_in "${srepo}" vde_stamp_valid "${T2}" full "${TIP2}"
expect_rc "a fast stamp does not satisfy a full request" fail "a fast stamp satisfied a full request"

test_start "stamp tiers: a fast request without a commit is refused for read and for write"
run_in "${srepo}" vde_stamp_valid "${T2}" fast
expect_rc "vde_stamp_valid refuses a fast request with no commit" fail "a fast request with no commit was accepted"
run_in "${srepo}" vde_stamp_write "${T2}" fast
expect_rc "vde_stamp_write refuses a fast write with no commit" fail "a fast write with no commit was accepted"
[[ ! -e "${SDIR}/${T2}" ]]; verdict "no bare-tree stamp was written by the refused fast write" $? "a file named ${T2} exists in the store"

test_start "stamp tamper: a fast record planted under the bare tree name is refused"
print -r -- "$(( EPOCHSECONDS )) fast" > "${SDIR}/${T2}"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${E2}"
expect_rc "a bare-name fast record does not satisfy a fast request for another commit" fail "a fast record under the bare tree name was accepted"
run_in "${srepo}" vde_stamp_valid "${T2}" full "${TIP2}"
expect_rc "a bare-name fast record does not satisfy a full request" fail "a fast record under the bare tree name satisfied a full request"
rm -f -- "${SDIR}/${T2}"

test_start "stamp tiers: a full stamp satisfies a fast request for any commit with that tree"
run_in "${srepo}" vde_stamp_write "${T2}" full
expect_rc "the full stamp for T2 is written" ok "the full stamp for T2 was refused"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${E2}"
expect_rc "a full stamp satisfies a fast request for the empty commit" ok "a full stamp did not satisfy a fast request for E2"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${TIP2}"
expect_rc "a full stamp satisfies a fast request for TIP2" ok "a full stamp did not satisfy a fast request for TIP2"
run_in "${srepo}" vde_stamp_valid "${T2}" full
expect_rc "a full stamp satisfies a full request" ok "a full stamp did not satisfy a full request"

test_start "stamp tiers: a fast write leaves an existing fresh full stamp untouched"
print -r -- "$(( EPOCHSECONDS - 100 )) full" > "${SDIR}/${T2}"
typeset full_before="$(<"${SDIR}/${T2}")"
run_in "${srepo}" vde_stamp_write "${T2}" fast "${TIP2}"
typeset full_after="$(<"${SDIR}/${T2}")"
[[ "${full_after}" == "${full_before}" ]]; verdict "the full stamp content is unchanged by a fast write" $? "before [${full_before}] after [${full_after}]"
run_in "${srepo}" vde_stamp_valid "${T2}" full
expect_rc "the full stamp still validates after a fast write" ok "the full stamp no longer validates after a fast write"

test_start "stamp clear: vde_stamp_clear removes that tree's full stamp and every fast stamp of it, and no other tree's"
run_in "${srepo}" vde_stamp_clear "${T2}"
expect_rc "vde_stamp_clear succeeds" ok "the clear was refused"
typeset -a left_over
left_over=( "${SDIR}/${T2}"(N) "${SDIR}/${T2}".*(N) )
(( ${#left_over} == 0 )); verdict "no stamp of T2 remains (bare, <tree>.<commit>)" $? "remaining: ${left_over[*]}"
run_in "${srepo}" vde_stamp_valid "${T2}" fast "${TIP2}"
expect_rc "the cleared tree is no longer valid for its fast commit" fail "the cleared tree still validates"
run_in "${srepo}" vde_stamp_valid "${T1}" full
expect_rc "the other tree's stamp is kept" ok "clearing T2 removed T1's stamp"

# =====================================================================================
# B. Range (lib/vde-gate-commits): vde_gate_range_commits
# =====================================================================================
typeset rrepo="${gate_scratch}/range-repo"
make_repo "${rrepo}"
commit_in "${rrepo}" r0 v0
commit_in "${rrepo}" r1 v1
commit_in "${rrepo}" r2 v2
typeset R0="$(git -C "${rrepo}" rev-parse HEAD~2)" R1="$(git -C "${rrepo}" rev-parse HEAD~1)" R2="$(git -C "${rrepo}" rev-parse HEAD)"

# range_in <dir> <remote> <ref lines>: feeds the lines on stdin, output in OUT, status in RC.
range_in() {
    OUT="$(print -r -- "$3" | (cd "$1" && vde_gate_range_commits "$2") 2>&1)"; RC=$?
}

test_start "range: two new commits over the remote sha are listed oldest first"
range_in "${rrepo}" origin "refs/heads/main ${R2} refs/heads/main ${R0}"
(( RC == 0 )) && [[ "${OUT}" == "${R1}"$'\n'"${R2}" ]]; verdict "two commits, oldest first" $? "got [${OUT}] rc ${RC}"

test_start "range: empty stdin lists nothing and returns 0"
OUT="$(cd "${rrepo}" && vde_gate_range_commits origin </dev/null 2>&1)"; RC=$?
(( RC == 0 )) && [[ -z "${OUT}" ]]; verdict "nothing, rc 0" $? "got [${OUT}] rc ${RC}"

test_start "range: a delete (local sha all zeros) contributes nothing"
range_in "${rrepo}" origin "refs/heads/main ${ZERO40} refs/heads/main ${R2}"
(( RC == 0 )) && [[ -z "${OUT}" ]]; verdict "a delete lists nothing, rc 0" $? "got [${OUT}] rc ${RC}"

test_start "range: two ref lines that share a commit list it once"
range_in "${rrepo}" origin "refs/heads/a ${R2} refs/heads/a ${R0}"$'\n'"refs/heads/b ${R2} refs/heads/b ${R0}"
(( RC == 0 )) && [[ "${OUT}" == "${R1}"$'\n'"${R2}" ]]; verdict "each commit once, oldest first" $? "got [${OUT}] rc ${RC}"

git -C "${rrepo}" update-ref refs/remotes/origin/main "${R1}"

test_start "range: a new branch lists only the commits not on the remote"
range_in "${rrepo}" origin "refs/heads/feat ${R2} refs/heads/feat ${ZERO40}"
(( RC == 0 )) && [[ "${OUT}" == "${R2}" ]]; verdict "only R2 (R1 is on origin/main)" $? "got [${OUT}] rc ${RC}"

test_start "range: an unknown remote sha takes the new-branch rule"
range_in "${rrepo}" origin "refs/heads/feat ${R2} refs/heads/feat ${UNKNOWN40}"
(( RC == 0 )) && [[ "${OUT}" == "${R2}" ]]; verdict "only R2 for an unknown remote sha" $? "got [${OUT}] rc ${RC}"

# =====================================================================================
# C. Orchestrator (githooks/proof-of-life-hook.zsh) over a fixture with a stub gate-tree
# =====================================================================================
# The stub records "<tier> <full sha>" for every run. A control file keyed by the subject
# (fail.<tier>.<subject> holds an exit code; dirty.<subject> makes the checkout's tracked file dirty).
typeset GATE_TREE_STUB='#!/usr/bin/env zsh
# Stub gate-tree: records the tier and the commit it ran for, and fails by control file.
typeset _ZSH_PURE=${(%):-%x}
typeset tier="$1" sha subj rc=0
sha="$(git rev-parse HEAD)" || exit 4
subj="$(git log -1 --format=%s HEAD)"
print -r -- "${tier} ${sha}" >> "@STATE@/runs.log"
[[ -f "@STATE@/dirty.${subj}" ]] && print -r -- dirt >> f
[[ -f "@STATE@/fail.${tier}.${subj}" ]] && rc="$(<"@STATE@/fail.${tier}.${subj}")"
exit ${rc}'

# put_stub <destination> <body> [name]: @STATE@ becomes the fixture state dir, @NAME@ the name.
put_stub() {
    typeset body="${2//@STATE@/${GSTATE}}"
    print -r -- "${body//@NAME@/${3}}" > "$1"
}

typeset GATE_OUT="" GATE_RC=0
typeset GBASE="" GFIX="" GSTATE=""

# mk_gate_fixture <name>: a repo holding the real hook and libraries, the stub gate-tree, and base commit c0.
mk_gate_fixture() {
    GBASE="${gate_scratch}/gate-$1"
    GFIX="${GBASE}/repo"
    GSTATE="${GBASE}/state"
    mkdir -p "${GFIX}/githooks" "${GFIX}/lib" "${GSTATE}" "${GBASE}/callerhome"
    cp "${VDE_ROOT_DIR}/githooks/proof-of-life-hook.zsh" "${GFIX}/githooks/"
    typeset lib
    for lib in vde-shell-compat vde-log vde-test-env vde-pol-stamp vde-gate-commits; do
        [[ -f "${VDE_ROOT_DIR}/lib/${lib}" ]] && cp "${VDE_ROOT_DIR}/lib/${lib}" "${GFIX}/lib/"
    done
    put_stub "${GFIX}/githooks/gate-tree.zsh" "${GATE_TREE_STUB}"
    make_repo "${GFIX}"
    print -r -- "v0" > "${GFIX}/f"
    git -C "${GFIX}" add -A && git -C "${GFIX}" commit -qm c0
}

# gate_push <ref lines>: a push, as git feeds the pre-push hook.
gate_push() {
    GATE_OUT="$(cd "${GFIX}" && print -r -- "$1" | HOME="${GBASE}/callerhome" zsh githooks/proof-of-life-hook.zsh origin 2>&1)"; GATE_RC=$?
}

# gate_manual: a manual run, with nothing on stdin.
gate_manual() {
    GATE_OUT="$(cd "${GFIX}" && HOME="${GBASE}/callerhome" zsh githooks/proof-of-life-hook.zsh </dev/null 2>&1)"; GATE_RC=$?
}

# gate_runs: the stub's run log (empty when nothing ran).
gate_runs() {
    [[ -f "${GSTATE}/runs.log" ]] && print -r -- "$(<"${GSTATE}/runs.log")"
    return 0
}

# gate_runs_is <label> <expected runs>
gate_runs_is() {
    [[ "$(gate_runs)" == "$2" ]]; verdict "$1" $? "runs were [$(gate_runs)], expected [$2]"
}

wt_count() { git -C "$1" worktree list --porcelain | grep -c '^worktree '; }

# --- C1: the three-commit push -----------------------------------------------------
test_start "orchestrator: a three-commit push checks each earlier commit fast and the tip in full, oldest first"
mk_gate_fixture std
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
typeset C0="$(git -C "${GFIX}" rev-parse HEAD~3)" C1="$(git -C "${GFIX}" rev-parse HEAD~2)" C2="$(git -C "${GFIX}" rev-parse HEAD~1)" C3="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
typeset FIRST_OUT="${GATE_OUT}"
(( GATE_RC == 0 )); verdict "the push certifies (rc 0)" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gate_runs_is "exactly fast C1, fast C2, full C3 (the stub ran once per commit, the suite and Proof of Life once, on the tip)" "fast ${C1}"$'\n'"fast ${C2}"$'\n'"full ${C3}"

test_start "orchestrator: the plan line names the earlier commits and the tip"
[[ "${FIRST_OUT}" == *"2 earlier commit(s): fast check; tip ${C3[1,7]}: full certification"* ]]; verdict "plan line printed" $? "output was [${FIRST_OUT[1,300]}]"

test_start "orchestrator: the success line reports the tip as fully certified"
[[ "${FIRST_OUT}" == *"tip fully certified"* ]]; verdict "final line says the tip is fully certified" $? "output was [${FIRST_OUT[1,300]}]"

test_start "orchestrator: no throwaway worktree remains after a successful push"
[[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "only the main worktree is listed" $? "worktrees: $(git -C "${GFIX}" worktree list)"

test_start "orchestrator: an identical second push reruns nothing"
typeset before_rerun="$(gate_runs)"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC == 0 )) && [[ "$(gate_runs)" == "${before_rerun}" ]]; verdict "the stamps satisfy every commit" $? "rc ${GATE_RC}, runs [$(gate_runs)]"

test_start "orchestrator: an expired stamp reruns the check"
typeset stamp_file
for stamp_file in "${GFIX}/.git/vde-gate-stamps"/*(N); do print -r -- "1000 full" > "${stamp_file}"; done
before_expiry="$(gate_runs)"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
gate_runs_is "all three checks rerun after the backdating" "${before_expiry}"$'\n'"fast ${C1}"$'\n'"fast ${C2}"$'\n'"full ${C3}"

test_start "orchestrator: a push with only a delete or an up-to-date ref certifies nothing"
typeset before_empty="$(gate_runs)"
gate_push "refs/heads/main ${ZERO40} refs/heads/main ${C3}"
(( GATE_RC == 0 )) && [[ "${GATE_OUT}" == *"nothing to certify"* ]] && [[ "$(gate_runs)" == "${before_empty}" ]]; verdict "a delete says nothing to certify, rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,200]}"
gate_push "refs/heads/main ${C3} refs/heads/main ${C3}"
(( GATE_RC == 0 )) && [[ "${GATE_OUT}" == *"nothing to certify"* ]] && [[ "$(gate_runs)" == "${before_empty}" ]]; verdict "an up-to-date ref says nothing to certify, rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,200]}"

# --- C2: a fast failure on the first commit ---------------------------------------
test_start "orchestrator: a fast failure on the first commit refuses the push and names commit, subject, tier and step"
mk_gate_fixture failfast
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
print -r -- 3 > "${GSTATE}/fail.fast.c1"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC != 0 )) && [[ "${GATE_OUT}" == *"${C1[1,7]}"* && "${GATE_OUT}" == *'"c1"'* && "${GATE_OUT}" == *fast* && "${GATE_OUT}" == *"the Sovereign suite"* ]]; verdict "refused, naming c1, fast and the failing step" $? "rc ${GATE_RC}: ${GATE_OUT[1,400]}"
gate_runs_is "the tip's full check never ran and nothing after the failure ran" "fast ${C1}"
test_start "orchestrator: no throwaway worktree remains after a refused push"
[[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "only the main worktree is listed" $? "worktrees: $(git -C "${GFIX}" worktree list)"

# --- C3: the tiers -----------------------------------------------------------------
test_start "orchestrator: a full stamp on an earlier commit's tree makes its fast check rerun nothing"
mk_gate_fixture tiers
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C2="$(git -C "${GFIX}" rev-parse HEAD~1)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push "refs/heads/main ${C2} refs/heads/main ${C0}"
gate_runs_is "push one: fast C1 then full C2 (C2 is the tip)" "fast ${C1}"$'\n'"full ${C2}"
before_b="$(gate_runs)"
gate_push "refs/heads/main ${C3} refs/heads/main ${C1}"
gate_runs_is "push two: C2 (earlier, full stamp) is not rechecked; only full C3 runs" "${before_b}"$'\n'"full ${C3}"
test_start "orchestrator: a fast stamp on the tip's tree does not satisfy the tip's full request"
before_c="$(gate_runs)"
gate_push "refs/heads/main ${C1} refs/heads/main ${C0}"
gate_runs_is "push three: C1 is the tip now, its fast stamp is not enough, so full C1 runs" "${before_c}"$'\n'"full ${C1}"

# --- C4: a fast result is per (tree, commit): two commits with one tree are checked separately ---
test_start "orchestrator: two different commits with the same tree each get their own fast run"
mk_gate_fixture same
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 ""
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C2="$(git -C "${GFIX}" rev-parse HEAD~1)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
[[ "$(git -C "${GFIX}" rev-parse "${C1}^{tree}")" == "$(git -C "${GFIX}" rev-parse "${C2}^{tree}")" ]]; verdict "fixture: C2 has C1's tree" $? "the trees differ"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
gate_runs_is "fast C1, fast C2 (same tree, own run), full C3" "fast ${C1}"$'\n'"fast ${C2}"$'\n'"full ${C3}"
test_start "orchestrator: the same commit retried reruns nothing"
before_retry="$(gate_runs)"
gate_push "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC == 0 )) && [[ "$(gate_runs)" == "${before_retry}" ]]; verdict "no run for the retried push" $? "rc ${GATE_RC}, runs [$(gate_runs)]"

test_start "orchestrator: a full stamp on a tree makes an earlier same-tree commit skip its fast check"
mk_gate_fixture fullfirst
commit_in "${GFIX}" c1 v1
C0="$(git -C "${GFIX}" rev-parse HEAD~1)"; C1="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push "refs/heads/main ${C1} refs/heads/main ${C0}"
gate_runs_is "push one: full C1 (the tip)" "full ${C1}"
commit_in "${GFIX}" c2 ""
C2="$(git -C "${GFIX}" rev-parse HEAD)"
before_full_first="$(gate_runs)"
gate_push "refs/heads/main ${C2} refs/heads/main ${C0}"
gate_runs_is "push two: C1 (earlier, full stamp on its tree) and C2 (tip, same tree) run nothing" "${before_full_first}"

test_start "orchestrator: a fast result for one commit is never reused for a different commit with the same tree"
mk_gate_fixture seq
mkdir -p "${GFIX}/tests/unit"
print -r -- "# suite added by c1" > "${GFIX}/tests/unit/new.test.zsh"
git -C "${GFIX}" add -A && git -C "${GFIX}" commit -qm c1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 ""
commit_in "${GFIX}" c4 v4
C0="$(git -C "${GFIX}" rev-parse HEAD~4)"; C1="$(git -C "${GFIX}" rev-parse HEAD~3)"; C2="$(git -C "${GFIX}" rev-parse HEAD~2)"; C3="$(git -C "${GFIX}" rev-parse HEAD~1)"; C4="$(git -C "${GFIX}" rev-parse HEAD)"
[[ "$(git -C "${GFIX}" rev-parse "${C2}^{tree}")" == "$(git -C "${GFIX}" rev-parse "${C3}^{tree}")" ]]; verdict "fixture: C3 has C2's tree" $? "the trees differ"
gate_push "refs/heads/main ${C4} refs/heads/main ${C0}"
gate_runs_is "fast C1, fast C2, fast C3 (not reused from C2), full C4" "fast ${C1}"$'\n'"fast ${C2}"$'\n'"fast ${C3}"$'\n'"full ${C4}"

# --- C5: a dirty throwaway checkout gets no stamp ----------------------------------
test_start "orchestrator: a stub that dirties its checkout gets no stamp and the commit is refused"
mk_gate_fixture dirty
commit_in "${GFIX}" c1 v1
C0="$(git -C "${GFIX}" rev-parse HEAD~1)"; C1="$(git -C "${GFIX}" rev-parse HEAD)"
: > "${GSTATE}/dirty.c1"
gate_push "refs/heads/main ${C1} refs/heads/main ${C0}"
(( GATE_RC != 0 )) && [[ "${GATE_OUT}" == *"left its tree dirty"* ]]; verdict "refused with 'left its tree dirty'" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
typeset T_DIRTY="$(git -C "${GFIX}" rev-parse "${C1}^{tree}")"
typeset -a dirty_stamps
dirty_stamps=( "${GFIX}/.git/vde-gate-stamps/${T_DIRTY}"(N) "${GFIX}/.git/vde-gate-stamps/${T_DIRTY}".*(N) )
(( ${#dirty_stamps} == 0 )); verdict "no stamp (full or fast) was written for the dirty tree" $? "stamps exist: ${dirty_stamps[*]}"
test_start "orchestrator: no throwaway worktree remains after the dirty refusal"
[[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "only the main worktree is listed" $? "worktrees: $(git -C "${GFIX}" worktree list)"

# --- C6: manual run certifies HEAD in full and refuses a dirty tracked tree ---------
test_start "orchestrator: a manual run certifies HEAD in full"
mk_gate_fixture manual
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
typeset C2M="$(git -C "${GFIX}" rev-parse HEAD)"
gate_manual
(( GATE_RC == 0 )) && [[ "$(gate_runs)" == "full ${C2M}" ]]; verdict "HEAD certified in full, rc 0" $? "rc ${GATE_RC}, runs [$(gate_runs)]: ${GATE_OUT[1,200]}"
test_start "orchestrator: a manual run refuses a dirty tracked worktree"
print -r -- dirt >> "${GFIX}/f"
before_manual="$(gate_runs)"
gate_manual
(( GATE_RC != 0 )) && [[ "$(gate_runs)" == "${before_manual}" ]]; verdict "refused, and nothing ran" $? "rc ${GATE_RC}, runs [$(gate_runs)]"
git -C "${GFIX}" checkout -q -- f

# --- C7: every pushed ref's tip gets the full tier (a push of several refs) -------------
# gate_runs_set_is <label> <expected runs...>: the run log as a sorted set. Git does not promise the
# order of the refs, so the order is not asserted; each expected run must appear exactly once.
gate_runs_set_is() {
    typeset label="$1"; shift
    typeset -a got want
    got=("${(@f)$(gate_runs)}")
    want=("$@")
    got=("${(@o)got}"); want=("${(@o)want}")
    [[ "${(j:|:)got}" == "${(j:|:)want}" ]]; verdict "${label}" $? "runs were [${(j:|:)got}], expected [${(j:|:)want}]"
}

test_start "orchestrator: two branches pushed together, each with its own commits: both tips full once, the earlier commits fast"
mk_gate_fixture twobr
typeset BASE_B="$(git -C "${GFIX}" rev-parse HEAD)"
git -C "${GFIX}" checkout -q -b bra "${BASE_B}"
commit_in "${GFIX}" a1 a1
commit_in "${GFIX}" a2 a2
typeset BA1="$(git -C "${GFIX}" rev-parse HEAD~1)" BA2="$(git -C "${GFIX}" rev-parse HEAD)"
git -C "${GFIX}" checkout -q -b brb "${BASE_B}"
commit_in "${GFIX}" b1 b1
commit_in "${GFIX}" b2 b2
typeset BB1="$(git -C "${GFIX}" rev-parse HEAD~1)" BB2="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push "refs/heads/bra ${BA2} refs/heads/bra ${BASE_B}"$'\n'"refs/heads/brb ${BB2} refs/heads/brb ${BASE_B}"
(( GATE_RC == 0 )); verdict "the push certifies (rc 0)" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gate_runs_set_is "a1 and b1 fast, a2 and b2 full, each exactly once" "fast ${BA1}" "fast ${BB1}" "full ${BA2}" "full ${BB2}"

test_start "orchestrator: the plan line counts two tips when two refs are pushed"
[[ "${GATE_OUT}" == *"2 earlier commit(s): fast check; 2 tip(s) full certification"* ]]; verdict "plan line counts the two tips" $? "output was [${GATE_OUT[1,300]}]"

test_start "orchestrator: branch A's tip is an ancestor of branch B's tip, both pushed: each tip full, the rest fast, nothing twice"
mk_gate_fixture chain
typeset CH0="$(git -C "${GFIX}" rev-parse HEAD)"
commit_in "${GFIX}" x1 x1
commit_in "${GFIX}" x2 x2
typeset CX1="$(git -C "${GFIX}" rev-parse HEAD~1)" CX2="$(git -C "${GFIX}" rev-parse HEAD)"
git -C "${GFIX}" branch brx "${CX2}"
commit_in "${GFIX}" y1 y1
commit_in "${GFIX}" y2 y2
typeset CY1="$(git -C "${GFIX}" rev-parse HEAD~1)" CY2="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push "refs/heads/brx ${CX2} refs/heads/brx ${CH0}"$'\n'"refs/heads/main ${CY2} refs/heads/main ${CH0}"
(( GATE_RC == 0 )); verdict "the push certifies (rc 0)" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gate_runs_set_is "x1 and y1 fast, x2 (an ancestor tip) full and y2 full, each exactly once" "fast ${CX1}" "fast ${CY1}" "full ${CX2}" "full ${CY2}"
test_start "orchestrator: the plan line counts both tips in the ancestor case too"
[[ "${GATE_OUT}" == *"2 earlier commit(s): fast check; 2 tip(s) full certification"* ]]; verdict "plan line counts the two tips" $? "output was [${GATE_OUT[1,300]}]"

test_start "orchestrator: an annotated tag pushed with its commit already in range: the tagged commit runs full, nothing twice"
mk_gate_fixture tagged
typeset TG0="$(git -C "${GFIX}" rev-parse HEAD)"
git -C "${GFIX}" update-ref refs/remotes/origin/main "${TG0}"
commit_in "${GFIX}" t1 t1
commit_in "${GFIX}" t2 t2
typeset TG1="$(git -C "${GFIX}" rev-parse HEAD~1)" TG2="$(git -C "${GFIX}" rev-parse HEAD)"
git -C "${GFIX}" tag -a v1 -m v1 "${TG1}"
typeset TAGOBJ="$(git -C "${GFIX}" rev-parse refs/tags/v1)"
[[ "$(git -C "${GFIX}" cat-file -t "${TAGOBJ}")" == tag ]]; verdict "the tag ref is an annotated tag object" $? "tag object type was [$(git -C "${GFIX}" cat-file -t "${TAGOBJ}")]"
gate_push "refs/heads/main ${TG2} refs/heads/main ${TG0}"$'\n'"refs/tags/v1 ${TAGOBJ} refs/tags/v1 ${ZERO40}"
(( GATE_RC == 0 )); verdict "the push certifies (rc 0)" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gate_runs_set_is "t1 (tagged, in range) full, t2 full, each exactly once" "full ${TG1}" "full ${TG2}"
test_start "orchestrator: the plan line counts the tag's commit as a tip, not an earlier commit"
[[ "${GATE_OUT}" == *"0 earlier commit(s): fast check; 2 tip(s) full certification"* ]]; verdict "plan line counts two tips and no earlier commits" $? "output was [${GATE_OUT[1,300]}]"

# --- C8: the pre-push wrapper runs the orchestrator under zsh -e (ERREXIT) ----------
# githooks/pre-push runs the orchestrator as `zsh -e`. A failing certification must still reach its
# failure line and clean up its throwaway worktree; errexit must not end the shell at the failing command.
# gate_push_e <ref lines>: a push as githooks/pre-push runs the orchestrator.
gate_push_e() {
    GATE_OUT="$(cd "${GFIX}" && print -r -- "$1" | HOME="${GBASE}/callerhome" zsh -e githooks/proof-of-life-hook.zsh origin 2>&1)"; GATE_RC=$?
}

test_start "orchestrator under zsh -e: a fast failure on the first commit prints its failure line and refuses the push"
mk_gate_fixture errexit-fast
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
print -r -- 3 > "${GSTATE}/fail.fast.c1"
gate_push_e "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC != 0 )) && [[ "${GATE_OUT}" == *"Commit ${C1[1,7]} \"c1\" failed the fast check: the Sovereign suite. Push blocked."* ]]; verdict "refused with the commit's failure line" $? "rc ${GATE_RC}: ${GATE_OUT[1,400]}"

test_start "orchestrator under zsh -e: the tip's full check never ran after the fast failure"
gate_runs_is "only fast C1 ran" "fast ${C1}"

test_start "orchestrator under zsh -e: no throwaway worktree remains after the fast failure"
[[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "only the main worktree is listed" $? "worktrees: $(git -C "${GFIX}" worktree list)"

test_start "orchestrator under zsh -e: a full failure on the tip prints its failure line and removes its worktree"
mk_gate_fixture errexit-full
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C2="$(git -C "${GFIX}" rev-parse HEAD~1)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
print -r -- 3 > "${GSTATE}/fail.full.c3"
gate_push_e "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC != 0 )) && [[ "${GATE_OUT}" == *"Commit ${C3[1,7]} \"c3\" failed the full check: the Sovereign suite. Push blocked."* ]]; verdict "refused with the tip's failure line" $? "rc ${GATE_RC}: ${GATE_OUT[1,400]}"
gate_runs_is "fast C1, fast C2, then the tip's full check ran once" "fast ${C1}"$'\n'"fast ${C2}"$'\n'"full ${C3}"
[[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "no throwaway worktree remains after the tip failure" $? "worktrees: $(git -C "${GFIX}" worktree list)"

test_start "orchestrator under zsh -e: a passing three-commit push still exits 0 with the usual success lines"
mk_gate_fixture errexit-pass
commit_in "${GFIX}" c1 v1
commit_in "${GFIX}" c2 v2
commit_in "${GFIX}" c3 v3
C0="$(git -C "${GFIX}" rev-parse HEAD~3)"; C1="$(git -C "${GFIX}" rev-parse HEAD~2)"; C2="$(git -C "${GFIX}" rev-parse HEAD~1)"; C3="$(git -C "${GFIX}" rev-parse HEAD)"
gate_push_e "refs/heads/main ${C3} refs/heads/main ${C0}"
(( GATE_RC == 0 )) && [[ "${GATE_OUT}" == *"Proof of Life Certified."* && "${GATE_OUT}" == *"tip fully certified"* ]]; verdict "rc 0 with the success lines" $? "rc ${GATE_RC}: ${GATE_OUT[1,400]}"
gate_runs_is "fast C1, fast C2, full C3" "fast ${C1}"$'\n'"fast ${C2}"$'\n'"full ${C3}"

# --- C9: an interrupt during the tip's check (TERM; INT only if it is deliverable, see below) ---
# BLOCK_STUB: a gate-tree that records its scratch base and its checkout, then waits (bounded) for a
# release file, so a signal can land while a throwaway worktree exists.
typeset BLOCK_STUB='#!/usr/bin/env zsh
# Stub gate-tree: announces its scratch base and checkout, then blocks until the release file appears.
typeset _ZSH_PURE=${(%):-%x}
zmodload zsh/zselect
print -r -- "${VDE_PROJECTS_DIR}" > "@STATE@/scratch.path"
print -r -- "${PWD}" > "@STATE@/started"
typeset -i n=0
while [[ ! -e "@STATE@/release" ]] && (( n < 1200 )); do zselect -t 5; (( n++ )); done
exit 0'

# wait_for_file <path>: polls with zselect (no sleep) for up to 20 seconds. Succeeds when the path exists.
wait_for_file() {
    typeset -i _n=0
    zmodload zsh/zselect
    while [[ ! -e "$1" ]] && (( _n < 400 )); do zselect -t 5; (( _n++ )); done
    [[ -e "$1" ]]
}

# gate_push_bg <ref lines>: starts the push in the background. zsh -c execs the hook, so $! is the hook's pid.
gate_push_bg() {
    print -r -- "$1" > "${GBASE}/bg-refs.txt"
    HOME="${GBASE}/callerhome" zsh -c 'cd "$1" && exec zsh githooks/proof-of-life-hook.zsh origin' _ "${GFIX}" \
        < "${GBASE}/bg-refs.txt" > "${GBASE}/bg.out" 2>&1 &
    GATE_PID=$!
}

# interrupt_case <signal> <expected status> <label>: a push interrupted while the tip's check runs.
interrupt_case() {
    typeset sig="$1" want="$2" label="$3"
    typeset INT_WT="" INT_SCRATCH="" INT_OUT=""
    typeset -a left
    mk_gate_fixture "int-${sig}"
    commit_in "${GFIX}" c1 v1
    typeset IC0="$(git -C "${GFIX}" rev-parse HEAD~1)" IC1="$(git -C "${GFIX}" rev-parse HEAD)"
    put_stub "${GFIX}/githooks/gate-tree.zsh" "${BLOCK_STUB}"
    gate_push_bg "refs/heads/main ${IC1} refs/heads/main ${IC0}"
    if wait_for_file "${GSTATE}/started"; then
        verdict "${label}: the tip's check is running when the signal lands" 0 ""
        INT_WT="$(<"${GSTATE}/started")"
        INT_SCRATCH="$(<"${GSTATE}/scratch.path")"
    else
        verdict "${label}: the tip's check is running when the signal lands" 1 "the gate-tree stub never started"
    fi
    kill -"${sig}" "${GATE_PID}" 2>/dev/null
    wait "${GATE_PID}"; GATE_RC=$?
    : > "${GSTATE}/release"
    INT_OUT="$(<"${GBASE}/bg.out")"
    (( GATE_RC == want )); verdict "${label}: exit status ${want}" $? "rc ${GATE_RC}: ${INT_OUT[1,300]}"
    [[ "${INT_OUT}" == *"The gate was interrupted. Push blocked."* ]]; verdict "${label}: the interrupt message is printed" $? "output: ${INT_OUT[1,300]}"
    [[ "$(wt_count "${GFIX}")" == 1 ]]; verdict "${label}: no throwaway worktree is registered" $? "worktrees: $(git -C "${GFIX}" worktree list)"
    if [[ -n "${INT_WT}" ]]; then
        [[ ! -e "${INT_WT}" ]]; verdict "${label}: the throwaway checkout is removed" $? "still present: ${INT_WT}"
    fi
    if [[ -n "${INT_SCRATCH}" ]]; then
        left=( "${INT_SCRATCH}"/gate-wt.*(N) )
        (( ${#left} == 0 )); verdict "${label}: no gate-wt directory is left under the scratch area" $? "left: ${left[*]}"
    fi
    return 0
}

test_start "orchestrator interrupted by TERM during the tip's check: exit 143, the interrupt message, no worktree or scratch left"
interrupt_case TERM 143 "TERM"

test_start "orchestrator interrupted by INT during the tip's check: exit 130, the interrupt message, no worktree or scratch left"
interrupt_case INT 130 "INT"

# --- C10: a subject with a literal backslash sequence is printed verbatim -------------
test_start "orchestrator: a failing commit whose subject holds a literal backslash sequence prints it verbatim (no tab)"
mk_gate_fixture subjesc
print -r -- v1 >> "${GFIX}/f"
typeset ESC_SUBJ="$(cat <<<'a\tb')"
git -C "${GFIX}" add f && git -C "${GFIX}" commit -qm "${ESC_SUBJ}"
commit_in "${GFIX}" c3 v3
typeset ES0="$(git -C "${GFIX}" rev-parse HEAD~2)" ES1="$(git -C "${GFIX}" rev-parse HEAD~1)" ES2="$(git -C "${GFIX}" rev-parse HEAD)"
[[ "$(git -C "${GFIX}" log -1 --format=%s "${ES1}")" == 'a\tb' ]]; verdict "fixture precondition: the commit subject is the literal a backslash t b" $? "subject was [$(git -C "${GFIX}" log -1 --format=%s "${ES1}")]"
print -r -- 3 > "${GSTATE}/fail.fast.${ESC_SUBJ}"
gate_push "refs/heads/main ${ES2} refs/heads/main ${ES0}"
(( GATE_RC != 0 )) && [[ "${GATE_OUT}" == *'"a\tb" failed the fast check'* ]]; verdict "the failure line holds the subject verbatim, backslash and t" $? "rc ${GATE_RC}: ${GATE_OUT[1,400]}"

# =====================================================================================
# D. Fast and full tiers (githooks/gate-tree.zsh) with stub audit, Gospel, suites and behave
# =====================================================================================
typeset STEP_STUB='#!/usr/bin/env zsh
# Stub step: logs its name to the shared steps log and exits with the code in its control file.
typeset _ZSH_PURE=${(%):-%x}
print -r -- "@NAME@" >> "@STATE@/steps.log"
print -r -- "@NAME@=${LC_ALL-unset}" >> "@STATE@/env.log"
typeset rc=0
[[ -f "@STATE@/@NAME@.rc" ]] && rc="$(<"@STATE@/@NAME@.rc")"
(( rc == 0 )) || print -r -- "✗ @NAME@ failed (exit code: ${rc})"
exit ${rc}'

typeset SUITE_RUNNER_STUB='#!/usr/bin/env zsh
# Stub Sovereign runner: --list names the suites; a full run logs "suite" and fails by control file.
typeset _ZSH_PURE=${(%):-%x}
if [[ "$1" == --list ]]; then
    print -r -- "run  a.test.zsh"
    print -r -- "run  b.test.zsh"
    print -r -- "skip c.test.zsh :: reason"
    exit 0
fi
print -r -- suite >> "@STATE@/steps.log"
print -r -- "suite=${LC_ALL-unset}" >> "@STATE@/env.log"
typeset rc=0
[[ -f "@STATE@/suite.rc" ]] && rc="$(<"@STATE@/suite.rc")"
(( rc == 0 )) || print -r -- "✗ widget-check.test.zsh failed (exit code: ${rc})"
exit ${rc}'

typeset PYTHON_STUB='#!/usr/bin/env zsh
# Stub python3: "-c import behave" reports availability; "-m behave" logs and fails by control file.
typeset _ZSH_PURE=${(%):-%x}
if [[ "$1" == -c ]]; then
    [[ -f "@STATE@/nobehave" ]] && exit 1
    exit 0
fi
print -r -- behave >> "@STATE@/steps.log"
print -r -- "behave=${LC_ALL-unset}" >> "@STATE@/env.log"
typeset rc=0
[[ -f "@STATE@/behave.rc" ]] && rc="$(<"@STATE@/behave.rc")"
exit ${rc}'

typeset GT_BASE="${gate_scratch}/gate-tree"
typeset GT="${GT_BASE}/repo"
typeset GT_STUBS="${GT_BASE}/stubs"
GSTATE="${GT_BASE}/state"
mkdir -p "${GT}/githooks" "${GT}/lib" "${GT}/bin" "${GT}/tests/unit" \
    "${GT}/tests/features/core-infrastructure" "${GSTATE}" "${GT_STUBS}" "${GT_BASE}/callerhome"
[[ -f "${VDE_ROOT_DIR}/githooks/gate-tree.zsh" ]] && cp "${VDE_ROOT_DIR}/githooks/gate-tree.zsh" "${GT}/githooks/"
[[ -f "${VDE_ROOT_DIR}/lib/vde-test-env" ]] && cp "${VDE_ROOT_DIR}/lib/vde-test-env" "${GT}/lib/"
[[ -f "${VDE_ROOT_DIR}/lib/vde-gate-commits" ]] && cp "${VDE_ROOT_DIR}/lib/vde-gate-commits" "${GT}/lib/"
put_stub "${GT}/bin/vde-enforce-uap.zsh" "${STEP_STUB}" audit
put_stub "${GT}/bin/vde-gospel-audit.zsh" "${STEP_STUB}" gospel
put_stub "${GT}/tests/run-sovereign-tests.zsh" "${SUITE_RUNNER_STUB}"
put_stub "${GT}/tests/unit/a.test.zsh" "${STEP_STUB}" a.test.zsh
put_stub "${GT}/tests/unit/b.test.zsh" "${STEP_STUB}" b.test.zsh
put_stub "${GT}/tests/unit/c.test.zsh" "${STEP_STUB}" c.test.zsh
put_stub "${GT}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" 'feature stub'
put_stub "${GT_STUBS}/python3" "${PYTHON_STUB}"
chmod +x "${GT_STUBS}/python3"
print -r -- "readme" > "${GT}/README.md"
make_repo "${GT}"
git -C "${GT}" add -A && git -C "${GT}" commit -qm base

# gt_reset: clears the step log and every control file.
gt_reset() {
    rm -f "${GSTATE}/steps.log" "${GSTATE}"/*.rc(N) "${GSTATE}/nobehave"
}
# gt_run <tier>: runs the real gate-tree on HEAD of the fixture.
gt_run() {
    GATE_OUT="$(cd "${GT}" && PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh "$1" 2>&1)"; GATE_RC=$?
}
# gt_steps: the steps that ran, in order, one per line.
gt_steps() {
    [[ -f "${GSTATE}/steps.log" ]] && print -r -- "$(<"${GSTATE}/steps.log")"
    return 0
}
gt_steps_is() {
    [[ "$(gt_steps)" == "$2" ]]; verdict "$1" $? "steps were [$(gt_steps)], expected [$2]"
}
# gt_timing_labels: the step label of each "[gate] <label> finished in <n>.<d>s" line of GATE_OUT, in order.
gt_timing_labels() {
    print -r -- "${GATE_OUT}" | sed -n 's/^\[gate\] \(.*\) finished in [0-9][0-9]*\.[0-9]s$/\1/p'
}

# --- the fast tier, one changed commit at a time -----------------------------------
print -r -- "# change a" >> "${GT}/tests/unit/a.test.zsh"
git -C "${GT}" commit -qam "x1 change a"
test_start "gate-tree fast: a commit that changes a unit suite runs audit, Gospel and that suite only"
gt_reset
gt_run fast
gt_steps_is "audit, Gospel, then a.test.zsh; no full suite, no behave" "audit"$'\n'"gospel"$'\n'"a.test.zsh"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
[[ "${GATE_OUT}" == *"fast check: 1 changed unit suite"* ]]; verdict "prints the fast check count" $? "output: ${GATE_OUT[1,300]}"

test_start "gate-tree fast: a commit that changes no unit suite runs only audit and Gospel"
print -r -- "docs" >> "${GT}/README.md"
git -C "${GT}" commit -qam "x2 docs"
gt_reset
gt_run fast
gt_steps_is "audit and Gospel only" "audit"$'\n'"gospel"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

test_start "gate-tree fast: a changed suite that the runner marks skip is not run"
print -r -- "# change c" >> "${GT}/tests/unit/c.test.zsh"
git -C "${GT}" commit -qam "x3 change c (skipped)"
gt_reset
gt_run fast
gt_steps_is "c.test.zsh is not run" "audit"$'\n'"gospel"

test_start "gate-tree fast: a failing changed suite exits 3 and its name is in the output"
print -r -- "# change b" >> "${GT}/tests/unit/b.test.zsh"
git -C "${GT}" commit -qam "x4 change b"
gt_reset
print -r -- 1 > "${GSTATE}/b.test.zsh.rc"
gt_run fast
(( GATE_RC == 3 )); verdict "exit 3 for a failing changed suite" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
[[ "${GATE_OUT}" == *"b.test.zsh"* ]]; verdict "the failing suite is named" $? "output: ${GATE_OUT[1,300]}"
gt_steps_is "audit, Gospel, then b.test.zsh" "audit"$'\n'"gospel"$'\n'"b.test.zsh"

test_start "gate-tree fast: an audit failure exits 1 before anything else runs"
gt_reset
print -r -- 1 > "${GSTATE}/audit.rc"
gt_run fast
(( GATE_RC == 1 )); verdict "exit 1 for an audit failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "only audit ran" "audit"

test_start "gate-tree fast: a Gospel failure exits 5 before the suites run"
gt_reset
print -r -- 1 > "${GSTATE}/gospel.rc"
gt_run fast
(( GATE_RC == 5 )); verdict "exit 5 for a Gospel failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "audit then gospel only" "audit"$'\n'"gospel"

# --- merge commits: the fast tier diffs a merge against its first parent ------------
typeset GT_MAIN="$(git -C "${GT}" symbolic-ref --short HEAD)"
git -C "${GT}" checkout -q -b mrg-a
print -r -- "# merge side a" >> "${GT}/tests/unit/a.test.zsh"
git -C "${GT}" commit -qam "m1 side change a"
git -C "${GT}" checkout -q "${GT_MAIN}"
git -C "${GT}" merge -q --no-ff -m "m1 merge side a" mrg-a >/dev/null 2>&1
typeset mp_line="$(git -C "${GT}" rev-list --parents -n 1 HEAD)"
typeset -a mparents
mparents=( ${(z)mp_line} )
test_start "gate-tree fast: fixture precondition, HEAD is a two-parent merge"
(( ${#mparents} == 3 )); verdict "HEAD has two parents" $? "rev-list --parents gave [${mp_line}]"

test_start "gate-tree fast: a merge that brings in a changed unit suite (relative to its first parent) runs audit, Gospel and that suite only"
gt_reset
gt_run fast
gt_steps_is "audit, Gospel, then a.test.zsh; no full suite, no behave" "audit"$'\n'"gospel"$'\n'"a.test.zsh"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
[[ "${GATE_OUT}" == *"fast check: 1 changed unit suite"* ]]; verdict "prints the fast check count" $? "output: ${GATE_OUT[1,300]}"

test_start "gate-tree fast: a merge that changes no unit suite relative to its first parent runs only audit and Gospel"
git -C "${GT}" checkout -q -b mrg-b
print -r -- "docs b" >> "${GT}/README.md"
git -C "${GT}" commit -qam "m2 side docs"
git -C "${GT}" checkout -q "${GT_MAIN}"
git -C "${GT}" merge -q --no-ff -m "m2 merge side docs" mrg-b >/dev/null 2>&1
mp_line="$(git -C "${GT}" rev-list --parents -n 1 HEAD)"
mparents=( ${(z)mp_line} )
(( ${#mparents} == 3 )); verdict "HEAD has two parents (docs merge)" $? "rev-list --parents gave [${mp_line}]"
gt_reset
gt_run fast
gt_steps_is "audit and Gospel only" "audit"$'\n'"gospel"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

# --- renames: a suite renamed on the merge path and on a plain commit ----------------
# git diff (porcelain) reports a rename as R, not A; the fast tier must still run the suite under its new name.
# b.test.zsh is freed first (x5), so the side branch can rename a.test.zsh onto it as a real rename with edits.
git -C "${GT}" rm -q tests/unit/b.test.zsh
git -C "${GT}" commit -qm "x5 drop b.test.zsh (frees the name for the rename)"
git -C "${GT}" checkout -q -b mrg-c
git -C "${GT}" mv tests/unit/a.test.zsh tests/unit/b.test.zsh
print -r -- "# renamed and edited" >> "${GT}/tests/unit/b.test.zsh"
# The stub logs its own name; the renamed file must log the new one (a one-line edit keeps git's rename detection firing).
print -r -- "${$(<"${GT}/tests/unit/b.test.zsh")//a.test.zsh/b.test.zsh}" > "${GT}/tests/unit/b.test.zsh"
git -C "${GT}" commit -qam "m3 side: rename a.test.zsh to b.test.zsh with edits"
git -C "${GT}" checkout -q "${GT_MAIN}"
git -C "${GT}" merge -q --no-ff -m "m3 merge: rename a.test.zsh to b.test.zsh" mrg-c >/dev/null 2>&1
typeset rn_line="$(git -C "${GT}" rev-list --parents -n 1 HEAD)"
typeset -a rn_parents
rn_parents=( ${(z)rn_line} )
test_start "gate-tree fast: fixture precondition, HEAD is a two-parent merge that renames a unit suite"
(( ${#rn_parents} == 3 )) && [[ -f "${GT}/tests/unit/b.test.zsh" && ! -e "${GT}/tests/unit/a.test.zsh" ]]; verdict "HEAD is the rename merge" $? "rev-list --parents gave [${rn_line}]"

test_start "gate-tree fast: a merge that renames a unit suite (a to b, with edits) runs the renamed suite b.test.zsh"
gt_reset
gt_run fast
gt_steps_is "audit, Gospel, then b.test.zsh (the renamed suite)" "audit"$'\n'"gospel"$'\n'"b.test.zsh"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
[[ "${GATE_OUT}" == *"fast check: 1 changed unit suite"* ]]; verdict "prints the fast check count" $? "output: ${GATE_OUT[1,300]}"

test_start "gate-tree fast: a plain (non-merge) commit that renames a unit suite (b to a, with edits) runs the renamed suite a.test.zsh"
git -C "${GT}" mv tests/unit/b.test.zsh tests/unit/a.test.zsh
print -r -- "# renamed back and edited" >> "${GT}/tests/unit/a.test.zsh"
print -r -- "${$(<"${GT}/tests/unit/a.test.zsh")//b.test.zsh/a.test.zsh}" > "${GT}/tests/unit/a.test.zsh"
git -C "${GT}" commit -qam "x6 plain commit: rename b.test.zsh to a.test.zsh with edits"
gt_reset
gt_run fast
gt_steps_is "audit, Gospel, then a.test.zsh (the renamed suite)" "audit"$'\n'"gospel"$'\n'"a.test.zsh"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

# --- the full tier-----------------------------------------------------------------
test_start "gate-tree full: audit, suite, behave, Gospel run in that order and pass with rc 0"
gt_reset
gt_run full
gt_steps_is "audit, suite, behave, gospel" "audit"$'\n'"suite"$'\n'"behave"$'\n'"gospel"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

test_start "gate-tree full: a failing suite exits 3 and stops before behave"
gt_reset
print -r -- 1 > "${GSTATE}/suite.rc"
gt_run full
(( GATE_RC == 3 )); verdict "exit 3 for a suite failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
[[ "${GATE_OUT}" == *"widget-check"* ]]; verdict "the failing suite is named" $? "output: ${GATE_OUT[1,300]}"
gt_steps_is "audit then suite only" "audit"$'\n'"suite"

test_start "gate-tree full: a Proof of Life failure exits 2"
gt_reset
print -r -- 1 > "${GSTATE}/behave.rc"
gt_run full
(( GATE_RC == 2 )); verdict "exit 2 for a Proof of Life failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "audit, suite, behave" "audit"$'\n'"suite"$'\n'"behave"

test_start "gate-tree full: a Gospel failure exits 5 after the Proof of Life"
gt_reset
print -r -- 1 > "${GSTATE}/gospel.rc"
gt_run full
(( GATE_RC == 5 )); verdict "exit 5 for a Gospel failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "audit, suite, behave, gospel" "audit"$'\n'"suite"$'\n'"behave"$'\n'"gospel"

test_start "gate-tree full: an audit failure exits 1 before anything else"
gt_reset
print -r -- 1 > "${GSTATE}/audit.rc"
gt_run full
(( GATE_RC == 1 )); verdict "exit 1 for an audit failure" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "only audit ran" "audit"

test_start "gate-tree full: behave unavailable exits 4 (could not run)"
gt_reset
touch "${GSTATE}/nobehave"
gt_run full
(( GATE_RC == 4 )); verdict "exit 4 when behave is unavailable" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"
gt_steps_is "audit then suite, no behave" "audit"$'\n'"suite"

# --- D2: a scratch HOME that cannot be created stops the gate with exit 4 before any step runs ---
# A stub mkdir fails for any path ending in /home and runs the real mkdir for every other call.
typeset GT_MKDIR_STUBS="${GT_BASE}/mkdir-stub"
typeset REAL_MKDIR="$(whence -p mkdir)"
mkdir -p "${GT_MKDIR_STUBS}"
{
    print -rl -- '#!/usr/bin/env zsh' \
        'typeset _ZSH_PURE=${(%):-%x}' \
        'for a in "$@"; do [[ "$a" == */home ]] && exit 1; done'
    print -r -- "exec ${REAL_MKDIR} \"\$@\""
} > "${GT_MKDIR_STUBS}/mkdir"
chmod +x "${GT_MKDIR_STUBS}/mkdir"

typeset MKDIR_OUT="" MKDIR_RC=0
for tier in fast full; do
    gt_reset
    MKDIR_OUT="$(cd "${GT}" && PATH="${GT_MKDIR_STUBS}:${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh "${tier}" 2>&1)"; MKDIR_RC=$?
    test_start "gate-tree ${tier}: a scratch HOME that cannot be created exits 4, says could not run, naming the scratch HOME"
    (( MKDIR_RC == 4 )) && [[ "${MKDIR_OUT}" == *"could not run"* ]] && [[ "${MKDIR_OUT}" == *"scratch HOME"* ]]
    verdict "exit 4 with 'could not run' naming the scratch HOME" $? "rc ${MKDIR_RC}: ${MKDIR_OUT[1,300]}"
    test_start "gate-tree ${tier}: a scratch HOME that cannot be created runs no audit, suite or behave step"
    [[ -z "$(gt_steps)" ]]; verdict "the steps log is empty" $? "steps were [$(gt_steps)]"
done
gt_reset

# --- D3: step timing (Signet #774): every step prints its elapsed time, and the tier prints its total ---
test_start "gate-tree full timing: each step prints a finished-in line in order, and the full tier line is last"
gt_reset
gt_run full
[[ "$(gt_timing_labels)" == "Sovereign Audit"$'\n'"Sovereign suite"$'\n'"Proof of Life"$'\n'"Gospel Audit"$'\n'"full tier" ]]; verdict "four step lines in order, then the full tier line" $? "labels were [$(gt_timing_labels)]: ${GATE_OUT[1,300]}"

test_start "gate-tree fast timing: the audit, Gospel, each changed suite, the unit suites aggregate and the fast tier line print finished-in lines"
gt_reset
gt_run fast
[[ "$(gt_timing_labels)" == "Sovereign Audit"$'\n'"Gospel Audit"$'\n'"unit suite a.test.zsh"$'\n'"unit suites"$'\n'"fast tier" ]]; verdict "the audit, Gospel, the changed suite's own line, the aggregate, then the fast tier line" $? "labels were [$(gt_timing_labels)]: ${GATE_OUT[1,300]}"

test_start "gate-tree full timing: a failing suite still prints its finished-in line and the full tier line, and exits 3"
gt_reset
print -r -- 1 > "${GSTATE}/suite.rc"
gt_run full
(( GATE_RC == 3 )) && [[ "$(gt_timing_labels)" == "Sovereign Audit"$'\n'"Sovereign suite"$'\n'"full tier" ]]; verdict "exit 3, with the finished-in lines up to the failure and the tier line" $? "rc ${GATE_RC}, labels [$(gt_timing_labels)]: ${GATE_OUT[1,300]}"

test_start "gate-tree timing: every step start line carries a wall-clock [HH:MM:SS]"
gt_reset
gt_run full
typeset GT_RUNNING="$(print -r -- "${GATE_OUT}" | grep -a 'Running ')"
[[ -n "${GT_RUNNING}" && -z "$(print -r -- "${GT_RUNNING}" | grep -a -v '\[[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\]')" ]]; verdict "every Running line has [HH:MM:SS]" $? "lines: ${GT_RUNNING[1,300]}"

test_start "gate-tree timing: a step that waits about one second reports at least 0.9s"
typeset SLOW_STUB='#!/usr/bin/env zsh
typeset _ZSH_PURE=${(%):-%x}
zmodload zsh/zselect && zselect -t 100
exit 0'
put_stub "${GT}/bin/vde-enforce-uap.zsh" "${SLOW_STUB}" audit
gt_reset
gt_run full
put_stub "${GT}/bin/vde-enforce-uap.zsh" "${STEP_STUB}" audit
typeset GT_SLOW="$(print -r -- "${GATE_OUT}" | sed -n 's/^\[gate\] Sovereign Audit finished in \([0-9][0-9]*\.[0-9]\)s$/\1/p')"
[[ -n "${GT_SLOW}" ]] && (( GT_SLOW >= 0.9 )); verdict "the Sovereign Audit step reports at least 0.9s" $? "reported [${GT_SLOW}]: ${GATE_OUT[1,300]}"
gt_reset

# --- D4: a decimal-comma locale cannot print commas in the timing lines (LC_ALL overrides LC_NUMERIC) ---
typeset D4_LOCALE="en_DK.utf8"
typeset D4_PROBE="$(LC_ALL=${D4_LOCALE} zsh -c 'printf "%.1f" 1.5' 2>/dev/null)"
if [[ "${D4_PROBE}" != "1,5" ]]; then
    print -r -- "[SKIP] D4: no decimal-comma locale (en_DK.utf8) on this host; install the locales package and run locale-gen"
else
    test_start "gate-tree full timing under LC_ALL=en_DK.utf8: every finished-in line has a dot and no comma"
    gt_reset
    GATE_OUT="$(cd "${GT}" && env "${_VDE_GATE_SCRUB[@]}" LC_ALL=${D4_LOCALE} PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh full 2>&1)"; GATE_RC=$?
    typeset D4_LINES="$(print -r -- "${GATE_OUT}" | grep -a 'finished in ')"
    typeset D4_BAD="$(print -r -- "${D4_LINES}" | grep -a -v -E 'finished in [0-9]+\.[0-9]s$')"
    [[ -n "${D4_LINES}" && -z "${D4_BAD}" && -z "$(print -r -- "${D4_LINES}" | grep -a ',')" ]]; verdict "every finished-in line has a dot and no comma" $? "lines: ${D4_LINES[1,400]}"

    test_start "gate-tree full timing under LC_ALL=en_DK.utf8: the full tier finished-in line has a dot"
    typeset D4_TIER="$(print -r -- "${GATE_OUT}" | grep -a 'full tier finished in ')"
    [[ "${D4_TIER}" =~ 'finished in [0-9]+\.[0-9]s$' ]]; verdict "the full tier line has a dot and no comma" $? "tier line: ${D4_TIER[1,200]}"

    test_start "gate-tree full timing under LC_ALL=en_DK.utf8: exit code is unchanged (0 for the passing stubs)"
    (( GATE_RC == 0 )); verdict "exit 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

    test_start "gate-tree timing under LC_ALL=en_DK.utf8: a one-second audit reports at least 0.9 with a dot"
    put_stub "${GT}/bin/vde-enforce-uap.zsh" "${SLOW_STUB}" audit
    gt_reset
    GATE_OUT="$(cd "${GT}" && env "${_VDE_GATE_SCRUB[@]}" LC_ALL=${D4_LOCALE} PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh full 2>&1)"; GATE_RC=$?
    put_stub "${GT}/bin/vde-enforce-uap.zsh" "${STEP_STUB}" audit
    typeset D4_SLOW="$(print -r -- "${GATE_OUT}" | sed -n 's/^\[gate\] Sovereign Audit finished in \([0-9][0-9]*[.,][0-9]\)s$/\1/p')"
    [[ "${D4_SLOW}" == *.* ]] && (( ${D4_SLOW/,/.} >= 0.9 )); verdict "the audit step reports at least 0.9 with a dot" $? "reported [${D4_SLOW}]: ${GATE_OUT[1,300]}"
    gt_reset

    # gate-tree's locale pin (_gate_fmt1) covers its number formatting only: every step it runs must keep the caller's LC_ALL.
    test_start "gate-tree full under LC_ALL=en_DK.utf8: every step (audit, suite, Proof of Life, Gospel) sees the caller's LC_ALL, never C"
    gt_reset
    rm -f "${GSTATE}/env.log"
    GATE_OUT="$(cd "${GT}" && env "${_VDE_GATE_SCRUB[@]}" LC_ALL=${D4_LOCALE} PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh full 2>&1)"; GATE_RC=$?
    typeset D4_ENV=""
    [[ -f "${GSTATE}/env.log" ]] && D4_ENV="$(<"${GSTATE}/env.log")"
    typeset D4_ENV_BAD="$(print -r -- "${D4_ENV}" | grep -a -v -E '=en_DK\.utf8$')"
    [[ -n "${D4_ENV}" && -z "${D4_ENV_BAD}" ]]; verdict "every recorded step saw LC_ALL=en_DK.utf8" $? "env log [${D4_ENV[1,300]}], not matching: [${D4_ENV_BAD[1,300]}]"

    test_start "gate-tree full under no LC_ALL in the environment: every step sees LC_ALL unset, never C"
    gt_reset
    rm -f "${GSTATE}/env.log"
    GATE_OUT="$(cd "${GT}" && env -u LC_ALL "${_VDE_GATE_SCRUB[@]}" PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh full 2>&1)"; GATE_RC=$?
    D4_ENV=""
    [[ -f "${GSTATE}/env.log" ]] && D4_ENV="$(<"${GSTATE}/env.log")"
    D4_ENV_BAD="$(print -r -- "${D4_ENV}" | grep -a -v -E '=unset$')"
    [[ -n "${D4_ENV}" && -z "${D4_ENV_BAD}" ]]; verdict "every recorded step saw LC_ALL unset" $? "env log [${D4_ENV[1,300]}], not matching: [${D4_ENV_BAD[1,300]}]"
    gt_reset
fi

# --- D5: the fast tier prints a finished-in line for each changed unit suite (Signet #774, F8) -----
# A commit that changes two runnable suites: each suite gets its own line, in run order, before the
# aggregate "unit suites" line. A failing changed suite still prints its own line, and the tier exits 3.
print -r -- "# two a" >> "${GT}/tests/unit/a.test.zsh"
put_stub "${GT}/tests/unit/b.test.zsh" "${STEP_STUB}" b.test.zsh
print -r -- "# two b" >> "${GT}/tests/unit/b.test.zsh"
git -C "${GT}" add tests/unit/a.test.zsh tests/unit/b.test.zsh && git -C "${GT}" commit -qm "x7 change a and b"

test_start "gate-tree fast timing: a commit that changes two unit suites prints a finished-in line for each suite, in run order, before the aggregate"
gt_reset
gt_run fast
[[ "$(gt_timing_labels)" == "Sovereign Audit"$'\n'"Gospel Audit"$'\n'"unit suite a.test.zsh"$'\n'"unit suite b.test.zsh"$'\n'"unit suites"$'\n'"fast tier" ]]; verdict "a line per changed suite, then the aggregate, then the fast tier line" $? "labels were [$(gt_timing_labels)]: ${GATE_OUT[1,300]}"
(( GATE_RC == 0 )); verdict "passes with rc 0" $? "rc ${GATE_RC}: ${GATE_OUT[1,300]}"

test_start "gate-tree fast timing: a failing changed suite still prints its own finished-in line, and the tier exits 3"
gt_reset
print -r -- 1 > "${GSTATE}/b.test.zsh.rc"
gt_run fast
(( GATE_RC == 3 )) && [[ "$(gt_timing_labels)" == "Sovereign Audit"$'\n'"Gospel Audit"$'\n'"unit suite a.test.zsh"$'\n'"unit suite b.test.zsh"$'\n'"unit suites"$'\n'"fast tier" ]]; verdict "exit 3, with a line for each suite, the aggregate and the tier line" $? "rc ${GATE_RC}, labels [$(gt_timing_labels)]: ${GATE_OUT[1,300]}"
gt_reset

# D4_PROBE (above) decides whether the decimal-comma locale is usable on this host.
if [[ "${D4_PROBE}" != "1,5" ]]; then
    print -r -- "[SKIP] F8: no decimal-comma locale (en_DK.utf8) on this host; the per-suite dot check is not run"
else
    test_start "gate-tree fast timing under LC_ALL=en_DK.utf8: each per-suite finished-in line has a dot and no comma"
    gt_reset
    GATE_OUT="$(cd "${GT}" && env "${_VDE_GATE_SCRUB[@]}" LC_ALL=${D4_LOCALE} PATH="${GT_STUBS}:${PATH}" HOME="${GT_BASE}/callerhome" zsh githooks/gate-tree.zsh fast 2>&1)"; GATE_RC=$?
    typeset F8_LINES="$(print -r -- "${GATE_OUT}" | grep -a '^\[gate\] unit suite ')"
    typeset F8_BAD="$(print -r -- "${F8_LINES}" | grep -a -v -E 'unit suite [a-z.]+ finished in [0-9]+\.[0-9]s$')"
    [[ "$(print -r -- "${F8_LINES}" | grep -a -c .)" == 2 && -z "${F8_BAD}" && -z "$(print -r -- "${F8_LINES}" | grep -a ',')" ]]; verdict "two per-suite lines, each with a dot and no comma" $? "lines: ${F8_LINES[1,400]}"
    gt_reset
fi

# --- E: the scratch-base library comes from the pushing tree, never from the commit under test -----
# gate-tree.zsh runs inside the commit's throwaway checkout, so VDE_ROOT_DIR names the commit under test.
# Its lib/vde-test-env must be the pushing tree's (${0:A:h:h}). Here the commit ships a lib/vde-test-env
# that is just `exit 0` and an audit that fails; the gate must still run the audit and refuse.
typeset EG_BASE="${gate_scratch}/gate-src-root"
typeset EG="${EG_BASE}/gate"
typeset ET="${EG_BASE}/commit-tree"
typeset EG_STUBS="${EG_BASE}/stubs"
mkdir -p "${EG}/githooks" "${EG}/lib" "${EG_STUBS}" "${EG_BASE}/callerhome" \
    "${ET}/lib" "${ET}/bin" "${ET}/tests"
cp "${VDE_ROOT_DIR}/githooks/gate-tree.zsh" "${EG}/githooks/"
cp "${VDE_ROOT_DIR}/lib/vde-test-env" "${VDE_ROOT_DIR}/lib/vde-gate-commits" "${EG}/lib/"
put_stub "${EG_STUBS}/python3" "${PYTHON_STUB}"
chmod +x "${EG_STUBS}/python3"
print -rl -- '#!/usr/bin/env zsh' 'exit 0' > "${ET}/lib/vde-test-env"
print -rl -- '#!/usr/bin/env zsh' 'exit 1' > "${ET}/bin/vde-enforce-uap.zsh"
print -rl -- '#!/usr/bin/env zsh' 'exit 0' > "${ET}/bin/vde-gospel-audit.zsh"
print -rl -- '#!/usr/bin/env zsh' 'exit 0' > "${ET}/tests/run-sovereign-tests.zsh"
make_repo "${ET}"
git -C "${ET}" add -A && git -C "${ET}" commit -qm hostile

# run_gate_in_commit <tier>: runs the pushing tree's gate-tree in the commit's checkout (cwd), scrubbed.
run_gate_in_commit() {
    OUT="$(cd "${ET}" && env "${_VDE_GATE_SCRUB[@]}" PATH="${EG_STUBS}:${PATH}" HOME="${EG_BASE}/callerhome" zsh "${EG}/githooks/gate-tree.zsh" "$1" 2>&1)"; RC=$?
}

test_start "gate-tree fast: a commit's own lib/vde-test-env (exit 0) cannot pass; the pushing tree's audit runs and refuses"
run_gate_in_commit fast
(( RC == 1 )) && [[ "${OUT}" == *"Sovereign Audit Failed"* ]]; verdict "exit 1 with the audit failure" $? "rc ${RC}: ${OUT[1,300]}"

test_start "gate-tree full: a commit's own lib/vde-test-env (exit 0) cannot pass; the pushing tree's audit runs and refuses"
run_gate_in_commit full
(( RC == 1 )) && [[ "${OUT}" == *"Sovereign Audit Failed"* ]]; verdict "exit 1 with the audit failure" $? "rc ${RC}: ${OUT[1,300]}"

gt_reset

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_PASSED > 0 && TESTS_FAILED == 0 ))
