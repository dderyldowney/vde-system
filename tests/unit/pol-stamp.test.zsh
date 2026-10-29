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

test_start "failed run propagates its status"
vde_pol_run_and_stamp pol_fail; typeset rc=$?
(( rc == 1 )) && test_pass "status" || test_fail "status" "rc=${rc}"

echo "Passed: ${TESTS_PASSED} Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
