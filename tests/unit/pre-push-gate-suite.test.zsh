#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: the local pre-push gate runs the code's own tests (Signet #769).
#
# The gate certifies the patchset before it leaves the machine: the Sovereign Audit,
# then the Sovereign suite (tests/run-sovereign-tests.zsh), then the Proof of Life.
# A failing suite blocks the push and names the suite; the Proof of Life does not start
# after it. One stamp covers the suite and the Proof of Life, so an unchanged clean tree
# is not rerun. The real hook runs in a throwaway git repo with stubs for the audit,
# the suite runner and python3 (no containers, no network).

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Fixture isolation (Signet #656): the GIT_* variables that select a repository would make the
# fixture below write into the ENCLOSING repository.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

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

typeset HOOK="${VDE_ROOT_DIR}/githooks/proof-of-life-hook.zsh"

# --- static: the hook calls the suite, before the Proof of Life --------------------
test_start "static: the hook has an active line that runs tests/run-sovereign-tests.zsh"
typeset -a active=("${(@f)$(awk '!/^[[:space:]]*#/ { print NR ": " $0 }' "${HOOK}")}")
typeset suite_line pol_line
typeset -a suite_hits=("${(@M)active:#*zsh*run-sovereign-tests.zsh*}")
typeset -a pol_hits=("${(@M)active:#*python3 -m behave*}")
suite_line="${suite_hits[1]%%:*}"
pol_line="${pol_hits[1]%%:*}"
if [[ -n "${suite_line}" ]]; then test_pass "an active line runs the suite"; else test_fail "suite call" "no active line names tests/run-sovereign-tests.zsh"; fi
test_start "static: the suite runs before the Proof of Life"
if [[ -n "${suite_line}" && -n "${pol_line}" ]] && (( suite_line < pol_line )); then
    test_pass "the suite (line ${suite_line}) runs before the Proof of Life (line ${pol_line})"
else
    test_fail "order" "suite line [${suite_line}], Proof of Life line [${pol_line}]"
fi

# --- the fixture --------------------------------------------------------------------
typeset fix out rc
fix="$(mktemp -d)" || exit 1
trap 'rm -rf "${fix}"' EXIT
mkdir -p "${fix}/githooks" "${fix}/lib" "${fix}/bin" "${fix}/tests/features/core-infrastructure" "${fix}/.stubs"
cp "${HOOK}" "${fix}/githooks/"
cp "${VDE_ROOT_DIR}/lib/vde-test-env" "${VDE_ROOT_DIR}/lib/vde-pol-stamp" "${fix}/lib/"
print -r -- 'feature stub' > "${fix}/tests/features/core-infrastructure/proof-of-life-the-contract.feature"
# The audit passes. The suite counts its runs and fails when .suite-rc says so, naming one suite.
print -r -- '#!/usr/bin/env zsh
exit 0' > "${fix}/bin/vde-enforce-uap.zsh"
print -r -- '#!/usr/bin/env zsh
print x >> "${0:A:h:h}/.suite-runs"
print -r -- "GIT_DIR=${GIT_DIR-unset} GIT_WORK_TREE=${GIT_WORK_TREE-unset} GIT_INDEX_FILE=${GIT_INDEX_FILE-unset} GIT_COMMON_DIR=${GIT_COMMON_DIR-unset} GIT_PREFIX=${GIT_PREFIX-unset} GIT_OBJECT_DIRECTORY=${GIT_OBJECT_DIRECTORY-unset} GIT_NAMESPACE=${GIT_NAMESPACE-unset} GIT_CONFIG_PARAMETERS=${GIT_CONFIG_PARAMETERS-unset}" > "${0:A:h:h}/.suite-env"
if [[ "$(cat "${0:A:h:h}/.suite-rc" 2>/dev/null)" == fail ]]; then print "✗ widget-check.test.zsh failed (exit code: 1)"; exit 1; fi
print "✓ all suites passed"; exit 0' > "${fix}/tests/run-sovereign-tests.zsh"
# python3 stands in for the Proof of Life: it counts its runs.
print -r -- '#!/usr/bin/env zsh
print x >> "'"${fix}"'/.pol-runs"
[[ "$(cat "'"${fix}"'/.pol-rc" 2>/dev/null)" == fail ]] && exit 1
exit 0' > "${fix}/.stubs/python3"
chmod +x "${fix}/.stubs/python3"
cd "${fix}" || exit 1
git init -q . && git config user.email t@t && git config user.name t
print -r -- '/.suite-runs
/.pol-runs
/.suite-rc
/.pol-rc
/.stubs/' > .gitignore
print one > f && git add -A && git commit -qm one

count() { [[ -f "${fix}/$1" ]] && wc -l < "${fix}/$1" | tr -d ' ' || print 0; }
run_hook() { out="$(PATH="${fix}/.stubs:${PATH}" zsh githooks/proof-of-life-hook.zsh < /dev/null 2>&1)"; rc=$?; }

# --- a failing suite blocks the push and names the suite ------------------------------
print fail > .suite-rc
run_hook
test_start "a failing suite blocks the push (non-zero exit)"
if (( rc != 0 )); then test_pass "blocked (exit ${rc})"; else test_fail "failing suite" "the hook exited 0"; fi
test_start "the output names the failing suite and says the push is blocked"
if [[ "${out}" == *widget-check.test.zsh* && "${out}" == *"Push blocked"* ]]; then test_pass "names the suite and blocks"; else test_fail "output" "${out:0:200}"; fi
test_start "the Proof of Life does not start after a suite failure"
if [[ "$(count .pol-runs)" == 0 ]]; then test_pass "Proof of Life not run"; else test_fail "order" "the Proof of Life ran after a failing suite"; fi

# --- a failing Proof of Life blocks the push with its own message ---------------------
print pass > .suite-rc
print fail > .pol-rc
run_hook
test_start "a passing suite then a failing Proof of Life blocks the push and says so"
if (( rc != 0 )) && [[ "${out}" == *"Mandate L Violation"* && "${out}" != *widget-check* ]]; then
    test_pass "blocked with the Proof of Life message, the suite is not blamed"
else
    test_fail "Proof of Life failure" "rc=${rc} ${out:0:200}"
fi
test_start "after the failing-suite push and the failing-Proof-of-Life push the suite ran twice and the Proof of Life once"
print pass > .pol-rc
if [[ "$(count .suite-runs)" == 2 && "$(count .pol-runs)" == 1 ]]; then test_pass "run counts: suite 2, Proof of Life 1 (no stamp is written by a failed run; the rerun checks below prove the reuse rules)"; else test_fail "counts" "suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi

# --- a missing runner blocks the push, with a message that says so -------------------
mv tests/run-sovereign-tests.zsh tests/run-sovereign-tests.zsh.off
run_hook
test_start "a missing tests/run-sovereign-tests.zsh blocks the push and says it is missing"
if (( rc != 0 )) && [[ "${out}" == *"run-sovereign-tests.zsh is missing"* ]]; then test_pass "blocked: the runner is missing"; else test_fail "missing runner" "rc=${rc} ${out:0:200}"; fi
mv tests/run-sovereign-tests.zsh.off tests/run-sovereign-tests.zsh

# --- a passing suite reaches the Proof of Life ----------------------------------------
print pass > .suite-rc
run_hook
test_start "a passing suite then a passing Proof of Life certifies"
if (( rc == 0 )) && [[ "${out}" == *"Proof of Life Certified"* ]]; then test_pass "certified"; else test_fail "pass" "rc=${rc} ${out:0:200}"; fi
test_start "both ran exactly once"
if [[ "$(count .suite-runs)" == 3 && "$(count .pol-runs)" == 2 ]]; then test_pass "suite ran once per push that reached it, Proof of Life ran twice (one failed)"; else test_fail "counts" "suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi

# --- an unchanged clean tree is not rerun ---------------------------------------------
run_hook
test_start "a second push of the same clean tree reruns neither"
if (( rc == 0 )) && [[ "$(count .suite-runs)" == 3 && "$(count .pol-runs)" == 2 ]]; then test_pass "stamp reused for both"; else test_fail "reuse" "rc=${rc} suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi

# --- a new tree reruns both -----------------------------------------------------------
print two > f && git commit -qam two
run_hook
test_start "a new tree reruns the suite and the Proof of Life"
if (( rc == 0 )) && [[ "$(count .suite-runs)" == 4 && "$(count .pol-runs)" == 3 ]]; then test_pass "both reran"; else test_fail "rerun" "rc=${rc} suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi

# --- the suite never sees the git environment a hook is given -------------------------
# Git exports GIT_DIR (and others) into a hook, and in a linked worktree GIT_DIR names the
# worktree's git directory. The suites build their own throwaway git repositories, so with
# those variables set their git commands land in the REAL repository (observed: staged
# deletions in the worktree's index and core.bare flipped in the shared config). The gate
# must scrub them before it runs the suite. A fresh commit makes the tree new, so the run
# is not skipped by the stamp.
print three > f && git commit -qam three
rm -f "${fix}/.suite-env"
out="$(PATH="${fix}/.stubs:${PATH}" GIT_DIR="${fix}/.git" GIT_WORK_TREE="${fix}" GIT_INDEX_FILE="${fix}/.git/index" GIT_COMMON_DIR="${fix}/.git" GIT_PREFIX="sub/" GIT_OBJECT_DIRECTORY="${fix}/.git/objects" GIT_NAMESPACE=ns GIT_CONFIG_PARAMETERS="'core.bare=true'" zsh githooks/proof-of-life-hook.zsh < /dev/null 2>&1)"; rc=$?
test_start "the Sovereign suite runs with the repository-selecting git variables removed"
typeset seen="$(cat "${fix}/.suite-env" 2>/dev/null)"
if [[ "${seen}" == "GIT_DIR=unset GIT_WORK_TREE=unset GIT_INDEX_FILE=unset GIT_COMMON_DIR=unset GIT_PREFIX=unset GIT_OBJECT_DIRECTORY=unset GIT_NAMESPACE=unset GIT_CONFIG_PARAMETERS=unset" ]]; then
    test_pass "the suite saw none of them"
else
    test_fail "git environment" "the suite saw: ${seen:-nothing (the suite did not run: rc=${rc} ${out:0:120})}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_PASSED > 0 && TESTS_FAILED == 0 ))
