#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: Proof of Life stamp reuse (Signet #602; per-tree store from Signet #770).
#
# A throwaway git repo stands in for a project. The stamp store is per tree: a stamp is for one tree
# hash, judged by that hash and not by time, and the callers stamp only a tree that vde_pol_clean_tree
# has passed as clean. This file covers lib/vde-pol-stamp on its own. The commit, range and orchestrator
# rules are in tests/unit/pre-push-gate-commits.test.zsh (section A there covers the store's tiers,
# linked worktrees, symlinks, non-hex names and the clear step), so they are not repeated here.
# Nothing is run: no container, no network, no sleep.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Fixture isolation (Signet #656): git lets the GIT_* variables that select a repository, its index,
# its objects or its namespace (the eight bin/vde-spine-check.zsh unsets)
# beat `cd` and `git -C`, and a git hook or a linked-worktree shell exports them. Without this scrub the
# fixture repository below (and the scripts this suite runs) would write into the ENCLOSING repository.
# It also drops the variables that inject git config or install hooks: GIT_CONFIG_COUNT (with its
# GIT_CONFIG_KEY_n/GIT_CONFIG_VALUE_n), GIT_CONFIG_PARAMETERS (what a parent `git -c` exports) and GIT_TEMPLATE_DIR.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_POL_STAMP_TTL

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

source "${VDE_ROOT_DIR}/lib/vde-pol-stamp"

# Scratch fixtures: a repo with commits, and a scratch root holding a non-repo and an unborn repo.
# The fixture lives under the test scratch area (lib/vde-test-env), never the system temp directory.
typeset scratch_root repo gate_scratch
gate_scratch="$(vde_test_env_dir)" || exit 1
[[ -n "${gate_scratch}" ]] || exit 1
scratch_root="$(mktemp -d "${gate_scratch}/pol-stamp.XXXXXX")" || exit 1
trap 'rm -rf "${scratch_root}"' EXIT
test_start "scratch: the fixture lives under the test scratch area"
[[ "${scratch_root:A}" == "${gate_scratch:A}"/* ]] && test_pass "the fixture is under ${gate_scratch}" \
    || test_fail "scratch fixture" "fixture ${scratch_root} is outside ${gate_scratch}"
repo="${scratch_root}/repo"
mkdir -p "${repo}" && cd "${repo}" || exit 1
git init -q . && git config user.email t@t && git config user.name t
print 'ignored.log' > .gitignore
print one > f && git add f .gitignore && git commit -qm one

# expect_clean <label>: vde_pol_clean_tree must succeed in the fixture's current state.
expect_clean() {
    if vde_pol_clean_tree >/dev/null 2>&1; then test_pass "$1"; else test_fail "$1" "the tree was judged unclean"; fi
}

# expect_unclean <label>: vde_pol_clean_tree must fail in the fixture's current state.
expect_unclean() {
    if vde_pol_clean_tree >/dev/null 2>&1; then test_fail "$1" "the tree was judged clean"; else test_pass "$1"; fi
}

# =====================================================================================
# A. vde_pol_clean_tree: which trees count as clean
# =====================================================================================
test_start "clean tree: vde_pol_clean_tree prints HEAD's tree and succeeds"
typeset tree_head clean_out
tree_head="$(git rev-parse 'HEAD^{tree}')"
clean_out="$(vde_pol_clean_tree)" && [[ "${clean_out}" == "${tree_head}" ]] \
    && test_pass "clean tree prints HEAD's tree" \
    || test_fail "clean tree prints HEAD's tree" "got [${clean_out}], expected ${tree_head}"

test_start "modified tracked file: not clean"
print dirty >> f
expect_unclean "modified tracked file is unclean"
git checkout -q -- f

test_start "staged change: not clean"
print staged >> f && git add f
expect_unclean "staged change is unclean"
git reset -q --hard HEAD

test_start "assume-unchanged edit: not clean"
git update-index --assume-unchanged f; print hidden >> f
expect_unclean "assume-unchanged edit is unclean"
git update-index --no-assume-unchanged f; git checkout -q -- f

test_start "skip-worktree edit: not clean"
git update-index --skip-worktree f; print hidden >> f
expect_unclean "skip-worktree edit is unclean"
git update-index --no-skip-worktree f; git checkout -q -- f

test_start "untracked file matched by .gitignore: still clean"
print x > ignored.log
expect_clean "an ignored untracked file does not dirty the tree"
rm -f ignored.log

test_start "git failure: outside a repository, not clean"
mkdir -p "${scratch_root}/nonrepo"
( cd "${scratch_root}/nonrepo" && vde_pol_clean_tree >/dev/null 2>&1 ) \
    && test_fail "outside a repository" "a non-repository was judged clean" \
    || test_pass "outside a repository is not clean"

test_start "git failure: an unborn HEAD has no tree, so not clean"
mkdir -p "${scratch_root}/unborn" && git -C "${scratch_root}/unborn" init -q
( cd "${scratch_root}/unborn" && vde_pol_clean_tree >/dev/null 2>&1 ) \
    && test_fail "unborn HEAD" "an unborn HEAD was judged clean" \
    || test_pass "an unborn HEAD is not clean"
cd "${repo}" || exit 1

# =====================================================================================
# B. The store: a stamp is for one tree, judged by tree hash
# =====================================================================================
test_start "per-tree: a stamp is valid for the tree it was written for"
typeset tree_a
tree_a="$(vde_pol_clean_tree)" || exit 1
vde_stamp_write "${tree_a}" full
vde_stamp_valid "${tree_a}" full && test_pass "stamp valid for its own tree" \
    || test_fail "stamp valid for its own tree" "a fresh stamp for ${tree_a} was refused"

test_start "per-tree: after a commit changes the tree, the new tree has no valid stamp"
print two >> f && git commit -qam two
typeset tree_b
tree_b="$(vde_pol_clean_tree)" || exit 1
[[ "${tree_b}" != "${tree_a}" ]] || { test_fail "per-tree setup" "the commit did not change the tree"; exit 1; }
vde_stamp_valid "${tree_b}" full \
    && test_fail "new tree" "the new tree was accepted on the old tree's stamp" \
    || test_pass "the new tree is not covered by the old stamp"
vde_stamp_valid "${tree_a}" full && test_pass "the old tree's own stamp is still for the old tree" \
    || test_fail "old tree kept" "the old tree lost its own stamp"

test_start "tree hash, not time: a modified-then-reverted checkout is valid again"
vde_stamp_write "${tree_b}" full
print scratch >> f
expect_unclean "an edit makes the tree unclean, so no stamp can be taken for it"
git checkout -q -- f
touch -t 200101010000 f
typeset tree_reverted
tree_reverted="$(vde_pol_clean_tree)" || exit 1
[[ "${tree_reverted}" == "${tree_b}" ]] && test_pass "the reverted checkout has the same tree hash" \
    || test_fail "reverted tree" "got ${tree_reverted}, expected ${tree_b}"
vde_stamp_valid "${tree_reverted}" full \
    && test_pass "the stamp is still valid although the file's mtime changed" \
    || test_fail "reverted tree" "a reverted checkout with the stamped tree was refused"

# =====================================================================================
# C. The caller's rule: an unclean tree is never stamped
# =====================================================================================
# vde_stamp_write does not inspect the worktree. The rule is the caller's: vde_pol_clean_tree must
# succeed before vde_stamp_write is called, as githooks/proof-of-life-hook.zsh and lib/vde-gate-commits do.
# caller_stamp is that rule in one place.
caller_stamp() {
    local tree
    tree="$(vde_pol_clean_tree)" && vde_stamp_write "${tree}" full
}

test_start "caller rule: a dirty tree is not stamped"
print three >> f && git commit -qam three
typeset tree_c
tree_c="$(git rev-parse 'HEAD^{tree}')"
print dirty >> f
caller_stamp >/dev/null 2>&1 \
    && test_fail "dirty tree stamped" "the caller stamped an unclean tree" \
    || test_pass "the caller refused to stamp an unclean tree"
[[ ! -e "$(vde_stamp_dir)/${tree_c}" ]]; verdict_rc=$?
(( verdict_rc == 0 )) && test_pass "no stamp file exists for the unclean tree" \
    || test_fail "no stamp file exists for the unclean tree" "a stamp exists for ${tree_c}"
git checkout -q -- f

test_start "caller rule: once the tree is clean, the caller stamps it"
caller_stamp && vde_stamp_valid "${tree_c}" full \
    && test_pass "the clean tree is stamped by the caller" \
    || test_fail "clean tree stamped" "the caller did not stamp the clean tree"

# =====================================================================================
# D. TTL expiry: boundaries, future dates, the override and its fallback
# =====================================================================================
# stamp_at <tree> <epoch>: writes a full stamp dated <epoch> straight to the store (no clock involved).
stamp_at() {
    local dir
    dir="$(vde_stamp_dir)" || return 1
    mkdir -p -- "${dir}" || return 1
    print -r -- "$2 full" > "${dir}/$1"
}

typeset tree_d
tree_d="$(vde_pol_clean_tree)" || exit 1

test_start "TTL: a stamp inside the default 1800s window is valid; one past it is not"
stamp_at "${tree_d}" $(( EPOCHSECONDS - 1700 ))
vde_stamp_valid "${tree_d}" full && test_pass "a 1700s-old stamp is valid" \
    || test_fail "default TTL inside" "a 1700s-old stamp was refused"
stamp_at "${tree_d}" $(( EPOCHSECONDS - 1900 ))
vde_stamp_valid "${tree_d}" full && test_fail "default TTL expired" "a 1900s-old stamp was accepted" \
    || test_pass "a 1900s-old stamp is expired"

# The clock may tick between writing a stamp and checking it (a loaded machine makes that likely), so the
# edges are asserted with a few seconds of margin on each side, never on the exact second.
test_start "TTL: a stamp just inside the window is valid, one just past it is expired"
VDE_POL_STAMP_TTL=60
stamp_at "${tree_d}" $(( EPOCHSECONDS - 55 ))
vde_stamp_valid "${tree_d}" full && test_pass "a stamp 55s old (TTL 60) is valid" \
    || test_fail "TTL inside" "a stamp 55s old was refused with TTL 60"
stamp_at "${tree_d}" $(( EPOCHSECONDS - 66 ))
vde_stamp_valid "${tree_d}" full && test_fail "TTL past boundary" "a stamp 66s old was accepted with TTL 60" \
    || test_pass "a stamp 66s old (TTL 60) is expired"
unset VDE_POL_STAMP_TTL

test_start "TTL: a future-dated stamp is not valid"
stamp_at "${tree_d}" $(( EPOCHSECONDS + 600 ))
vde_stamp_valid "${tree_d}" full && test_fail "future-dated" "a stamp dated 600s in the future was accepted" \
    || test_pass "a future-dated stamp is refused"

test_start "TTL: VDE_POL_STAMP_TTL overrides the window; a non-numeric value falls back to 1800"
stamp_at "${tree_d}" $(( EPOCHSECONDS - 100 ))
VDE_POL_STAMP_TTL=50 vde_stamp_valid "${tree_d}" full \
    && test_fail "TTL override" "a 100s-old stamp was accepted with TTL 50" \
    || test_pass "the override shortens the window"
VDE_POL_STAMP_TTL=junk vde_stamp_valid "${tree_d}" full \
    && test_pass "a non-numeric TTL falls back to 1800 (a 100s-old stamp is valid)" \
    || test_fail "TTL fallback" "a non-numeric TTL did not fall back to 1800"
stamp_at "${tree_d}" $(( EPOCHSECONDS - 1900 ))
VDE_POL_STAMP_TTL=junk vde_stamp_valid "${tree_d}" full \
    && test_fail "TTL fallback expiry" "a 1900s-old stamp was accepted under a non-numeric TTL" \
    || test_pass "a non-numeric TTL still expires at 1800"
unset VDE_POL_STAMP_TTL

echo "Passed: ${TESTS_PASSED} Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
