#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: Proof of Life stamp reuse (Signet #602).
#
# A throwaway git repo and a stub PoL command stand in for the real contract:
# the stamp may only skip a rerun for the exact tree that passed, clean.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

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

typeset repo
repo="$(mktemp -d)" || exit 1
trap 'rm -rf "${repo}"' EXIT
cd "${repo}" || exit 1
git init -q . && git config user.email t@t && git config user.name t
print one > f && git add f && git commit -qm one

pol_pass() { return 0; }
pol_fail() { return 1; }
pol_edits() { print edited >> f; return 0; }

test_start "no stamp: not valid"
vde_pol_stamp_valid && test_fail "no stamp" "valid without a stamp" || test_pass "no stamp"

test_start "passing clean run writes a stamp that then validates"
vde_pol_run_and_stamp pol_pass
vde_pol_stamp_valid && test_pass "stamp valid" || test_fail "stamp valid" "stamp missing after pass"

test_start "new commit (tree changed): stamp no longer valid"
print two > f && git commit -qam two
vde_pol_stamp_valid && test_fail "tree changed" "stale stamp accepted" || test_pass "tree changed"

test_start "dirty tracked worktree: stamp not valid even for matching tree"
vde_pol_run_and_stamp pol_pass
print dirty >> f
vde_pol_stamp_valid && test_fail "dirty tree" "dirty worktree accepted" || test_pass "dirty tree"
git checkout -q -- f

test_start "dirty tree during run: no stamp written"
print dirty >> f
vde_pol_run_and_stamp pol_pass
git checkout -q -- f
vde_pol_stamp_valid && test_fail "dirty run" "stamped a dirty run" || test_pass "dirty run"

test_start "edit during run: no stamp written"
vde_pol_run_and_stamp pol_edits
git checkout -q -- f
vde_pol_stamp_valid && test_fail "edit during run" "stamped a run with edits" || test_pass "edit during run"

test_start "failed run clears an existing stamp and writes none"
vde_pol_run_and_stamp pol_pass
vde_pol_run_and_stamp pol_fail
vde_pol_stamp_valid && test_fail "failed run" "stamp survived a failed run" || test_pass "failed run"

test_start "fresh stamp inside the TTL is valid; expired or future-dated stamp is not"
vde_pol_run_and_stamp pol_pass
typeset tree_now; tree_now="$(vde_pol_clean_tree)"
typeset stamp_file; stamp_file="$(vde_pol_stamp_path)"
print -r -- "${tree_now} $(( EPOCHSECONDS - 1700 ))" > "${stamp_file}"
vde_pol_stamp_valid && test_pass "inside TTL" || test_fail "inside TTL" "29m-old stamp rejected"
print -r -- "${tree_now} $(( EPOCHSECONDS - 1900 ))" > "${stamp_file}"
vde_pol_stamp_valid && test_fail "expired" "31m-old stamp accepted" || test_pass "expired"
print -r -- "${tree_now} $(( EPOCHSECONDS + 600 ))" > "${stamp_file}"
vde_pol_stamp_valid && test_fail "future" "future-dated stamp accepted" || test_pass "future"
print -r -- "${tree_now}" > "${stamp_file}"
vde_pol_stamp_valid && test_fail "legacy" "timestamp-less stamp accepted" || test_pass "legacy"

test_start "VDE_POL_STAMP_TTL overrides the window; junk falls back to 1800"
print -r -- "${tree_now} $(( EPOCHSECONDS - 100 ))" > "${stamp_file}"
VDE_POL_STAMP_TTL=50 vde_pol_stamp_valid && test_fail "ttl override" "100s-old accepted at 50s" || test_pass "ttl override"
VDE_POL_STAMP_TTL=junk vde_pol_stamp_valid && test_pass "ttl junk" || test_fail "ttl junk" "no fallback"

test_start "assume-unchanged edit is not clean"
vde_pol_run_and_stamp pol_pass
git update-index --assume-unchanged f; print hidden >> f
vde_pol_stamp_valid && test_fail "assume-unchanged" "hidden edit accepted" || test_pass "assume-unchanged"
git update-index --no-assume-unchanged f; git checkout -q -- f

test_start "skip-worktree edit is not clean"
git update-index --skip-worktree f; print hidden >> f
vde_pol_clean_tree >/dev/null && test_fail "skip-worktree" "hidden edit accepted" || test_pass "skip-worktree"
git update-index --no-skip-worktree f; git checkout -q -- f

test_start "outgoing ref with a different tree is not covered"
vde_pol_run_and_stamp pol_pass
vde_pol_push_covered HEAD && test_pass "head covered" || test_fail "head covered" "rejected stamped HEAD"
git branch -q other && git checkout -q other && print x > g && git add g && git commit -qm x && git checkout -q -
vde_pol_push_covered HEAD other && test_fail "other ref" "unstamped ref accepted" || test_pass "other ref"
git branch -q same && vde_pol_push_covered HEAD same && test_pass "same tree ref" || test_fail "same tree ref" "rejected"

test_start "undeletable stamp aborts before running PoL"
vde_pol_run_and_stamp pol_pass
typeset ran=0; pol_marks() { ran=1; return 0; }
chmod 500 "$(dirname "$(vde_pol_stamp_path)")"
if [[ -w "$(dirname "$(vde_pol_stamp_path)")" ]]; then
    test_pass "undeletable stamp (skipped: running as owner with write access)"
else
    vde_pol_run_and_stamp pol_marks 2>/dev/null; (( ran == 0 )) && test_pass "undeletable stamp" || test_fail "undeletable stamp" "PoL ran"
fi
chmod 700 "$(dirname "$(vde_pol_stamp_path)")"

test_start "failed run propagates its status"
vde_pol_run_and_stamp pol_fail; typeset rc=$?
(( rc == 1 )) && test_pass "status" || test_fail "status" "rc=${rc}"

echo "Passed: ${TESTS_PASSED} Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
