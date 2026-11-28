#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: the full tier of githooks/gate-tree.zsh (Signet #769, #770).
#
# The full tier certifies the tip of a push: the Sovereign Audit, then the Sovereign suite
# (tests/run-sovereign-tests.zsh), then the Proof of Life (behave), then the Gospel Audit.
# A failing suite blocks the push and names the suite; the Proof of Life does not start after it.
# This file drives gate-tree.zsh directly in a stub fixture (no containers, no network): the audit,
# the suite runner and python3 are stubs. The orchestrator, ranges, stamps and the fast tier are
# covered by tests/unit/pre-push-gate-commits.test.zsh and are not repeated here.

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

typeset GATE="${VDE_ROOT_DIR}/githooks/gate-tree.zsh"

# --- static: gate-tree.zsh runs the suite, before the Proof of Life -------------------
test_start "static: gate-tree.zsh has an active line that runs tests/run-sovereign-tests.zsh"
typeset -a _lines=("${(@f)$(<"${GATE}")}")
typeset _l suite_line=0 pol_line=0
typeset -i _n
for (( _n = 1; _n <= ${#_lines}; _n++ )); do
    _l="${_lines[_n]}"
    [[ "${_l}" == [[:space:]]#'#'* ]] && continue
    if (( ! suite_line )) && [[ "${_l}" == *'zsh "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh"'* ]]; then suite_line=${_n}; fi
    if (( ! pol_line )) && [[ "${_l}" == *'python3 -m behave "${VDE_ROOT_DIR}'* ]]; then pol_line=${_n}; fi
done
if (( suite_line )); then test_pass "an active line runs the suite (line ${suite_line})"; else test_fail "suite call" "no active line runs tests/run-sovereign-tests.zsh"; fi
test_start "static: the suite runs before the Proof of Life"
if (( suite_line && pol_line && suite_line < pol_line )); then
    test_pass "the suite (line ${suite_line}) runs before the Proof of Life (line ${pol_line})"
else
    test_fail "order" "suite line [${suite_line}], Proof of Life line [${pol_line}]"
fi

# --- the fixture --------------------------------------------------------------------
typeset fix out rc
typeset gate_scratch="$(vde_test_env_dir)"
[[ -n "${gate_scratch}" ]] || exit 1
fix="$(mktemp -d "${gate_scratch}/gate-tree-fix.XXXXXX")" || exit 1
trap 'rm -rf "${fix}"' EXIT
test_start "the fixture lives under the test scratch area"
if [[ "${fix}" == "${gate_scratch}"/* ]]; then test_pass "fixture under ${gate_scratch}"; else test_fail "fixture location" "fix=${fix}"; fi
mkdir -p "${fix}/githooks" "${fix}/lib" "${fix}/bin" "${fix}/tests/features/core-infrastructure" "${fix}/.stubs" "${fix}/callerhome"
cp "${GATE}" "${fix}/githooks/"
cp "${VDE_ROOT_DIR}/lib/vde-test-env" "${fix}/lib/"
cp "${VDE_ROOT_DIR}/lib/vde-gate-commits" "${fix}/lib/"
cp "${VDE_ROOT_DIR}/lib/vde-junit-timing" "${fix}/lib/"
print -r -- 'feature stub' > "${fix}/tests/features/core-infrastructure/proof-of-life-the-contract.feature"
# The audit passes.
print -r -- '#!/usr/bin/env zsh
exit 0' > "${fix}/bin/vde-enforce-uap.zsh"
# The suite counts its runs, records its HOME and git environment, and reads .suite-rc:
# fail = one named failing suite, start = a runner that cannot start (status 127), else pass.
print -r -- '#!/usr/bin/env zsh
print x >> "${0:A:h:h}/.suite-runs"
print -r -- "${HOME}" > "${0:A:h:h}/.suite-home"
print -r -- "GIT_DIR=${GIT_DIR-unset} GIT_WORK_TREE=${GIT_WORK_TREE-unset} GIT_INDEX_FILE=${GIT_INDEX_FILE-unset} GIT_COMMON_DIR=${GIT_COMMON_DIR-unset} GIT_PREFIX=${GIT_PREFIX-unset} GIT_OBJECT_DIRECTORY=${GIT_OBJECT_DIRECTORY-unset} GIT_NAMESPACE=${GIT_NAMESPACE-unset} GIT_CONFIG_PARAMETERS=${GIT_CONFIG_PARAMETERS-unset}" > "${0:A:h:h}/.suite-env"
if [[ "$(cat "${0:A:h:h}/.suite-rc" 2>/dev/null)" == start ]]; then exit 127; fi
if [[ "$(cat "${0:A:h:h}/.suite-rc" 2>/dev/null)" == fail ]]; then print "✗ widget-check.test.zsh failed (exit code: 1)"; exit 1; fi
print "✓ all suites passed"; exit 0' > "${fix}/tests/run-sovereign-tests.zsh"
# python3 stands in for behave: it counts its Proof of Life runs; .pol-rc = fail fails it,
# .pol-nobehave makes the "import behave" probe fail.
print -r -- '#!/usr/bin/env zsh
if [[ "$1" == -c ]]; then [[ -f "'"${fix}"'/.pol-nobehave" ]] && exit 1; exit 0; fi
print x >> "'"${fix}"'/.pol-runs"
[[ "$(cat "'"${fix}"'/.pol-rc" 2>/dev/null)" == fail ]] && exit 1
exit 0' > "${fix}/.stubs/python3"
chmod +x "${fix}/.stubs/python3"
(cd "${fix}" && git init -q .) || exit 1

count() { [[ -f "${fix}/$1" ]] && wc -l < "${fix}/$1" | tr -d ' ' || print 0; }
# run_gate: runs the full tier in the fixture with the stubs first on PATH.
run_gate() { out="$(cd "${fix}" && PATH="${fix}/.stubs:${PATH}" zsh githooks/gate-tree.zsh full < /dev/null 2>&1)"; rc=$?; }

# --- a failing suite blocks the push, names the suite, and the Proof of Life never starts ----
print fail > "${fix}/.suite-rc"
typeset -i s0 p0
s0=$(count .suite-runs); p0=$(count .pol-runs)
run_gate
test_start "a failing suite blocks the full tier (exit 3)"
if (( rc == 3 )); then test_pass "blocked (exit ${rc})"; else test_fail "failing suite" "exit ${rc}, expected 3 (${out[1,200]})"; fi
test_start "the output names the failing suite and says the suite failed"
if [[ "${out}" == *widget-check.test.zsh* && "${out}" == *"Sovereign suite failed"* ]]; then test_pass "names the suite"; else test_fail "output" "${out[1,200]}"; fi
test_start "the Proof of Life does not start after a suite failure"
if (( $(count .pol-runs) == p0 && $(count .suite-runs) == s0 + 1 )); then test_pass "Proof of Life not run, suite ran once"; else test_fail "order" "suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi

# --- a passing suite then a failing Proof of Life gives the Mandate L message --------------
print pass > "${fix}/.suite-rc"
print fail > "${fix}/.pol-rc"
p0=$(count .pol-runs)
run_gate
test_start "a passing suite then a failing Proof of Life blocks the full tier (exit 2)"
if (( rc == 2 )); then test_pass "blocked (exit ${rc})"; else test_fail "Proof of Life failure" "exit ${rc}, expected 2 (${out[1,200]})"; fi
test_start "the failure is the Mandate L message, and the suite is not blamed"
if [[ "${out}" == *"Mandate L Violation"* && "${out}" != *widget-check* ]]; then test_pass "Mandate L message, no suite named"; else test_fail "Mandate L message" "${out[1,200]}"; fi
test_start "the Proof of Life ran once after the passing suite"
if (( $(count .pol-runs) == p0 + 1 )); then test_pass "Proof of Life ran once"; else test_fail "Proof of Life count" "pol=$(count .pol-runs)"; fi
print pass > "${fix}/.pol-rc"

# --- a full pass, under a hostile git environment and a caller HOME -----------------------
# Git exports GIT_DIR (and others) into a hook, and the suites build their own throwaway git repositories,
# so the gate must scrub them before it runs the suite (Signet #656). The suite must also never see the
# caller's HOME, and never a HOME inside the repository.
rm -f "${fix}/.suite-env" "${fix}/.suite-home"
s0=$(count .suite-runs); p0=$(count .pol-runs)
out="$(cd "${fix}" && HOME="${fix}/callerhome" PATH="${fix}/.stubs:${PATH}" GIT_DIR="${fix}/.git" GIT_WORK_TREE="${fix}" GIT_INDEX_FILE="${fix}/.git/index" GIT_COMMON_DIR="${fix}/.git" GIT_PREFIX="sub/" GIT_OBJECT_DIRECTORY="${fix}/.git/objects" GIT_NAMESPACE=ns GIT_CONFIG_PARAMETERS="'core.bare=true'" zsh githooks/gate-tree.zsh full < /dev/null 2>&1)"; rc=$?
test_start "a passing suite then a passing Proof of Life certifies the full tier (exit 0)"
if (( rc == 0 )); then test_pass "certified (exit 0)"; else test_fail "full pass" "exit ${rc} (${out[1,200]})"; fi
test_start "a full pass runs the suite once and the Proof of Life once"
if (( $(count .suite-runs) == s0 + 1 && $(count .pol-runs) == p0 + 1 )); then test_pass "suite once, Proof of Life once"; else test_fail "full pass counts" "suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi
test_start "the Sovereign suite sees none of the repository-selecting GIT_* variables"
typeset seen="$(cat "${fix}/.suite-env" 2>/dev/null)"
if [[ "${seen}" == "GIT_DIR=unset GIT_WORK_TREE=unset GIT_INDEX_FILE=unset GIT_COMMON_DIR=unset GIT_PREFIX=unset GIT_OBJECT_DIRECTORY=unset GIT_NAMESPACE=unset GIT_CONFIG_PARAMETERS=unset" ]]; then
    test_pass "the suite saw none of them"
else
    test_fail "git environment" "the suite saw: ${seen:-nothing (the suite did not run)}"
fi
test_start "the Sovereign suite runs under a scratch HOME, not the caller's or one inside the repository"
typeset seen_home="$(cat "${fix}/.suite-home" 2>/dev/null)"
if [[ -n "${seen_home}" && "${seen_home}" != "${fix}/callerhome" && "${seen_home}" != "${HOME}" && "${seen_home}" != "${fix}"* ]]; then
    test_pass "the suite saw HOME=${seen_home}"
else
    test_fail "scratch HOME" "the suite saw: ${seen_home:-nothing}"
fi

# --- a missing runner blocks the full tier, with a message that says so ----------------
mv "${fix}/tests/run-sovereign-tests.zsh" "${fix}/tests/run-sovereign-tests.zsh.off"
s0=$(count .suite-runs); p0=$(count .pol-runs)
run_gate
test_start "a missing tests/run-sovereign-tests.zsh blocks the full tier (exit 3) and says it is missing"
if (( rc == 3 )) && [[ "${out}" == *"run-sovereign-tests.zsh is missing"* ]]; then test_pass "blocked: the runner is missing"; else test_fail "missing runner" "rc=${rc} ${out[1,200]}"; fi
test_start "a missing runner runs neither the suite nor the Proof of Life"
if (( $(count .suite-runs) == s0 && $(count .pol-runs) == p0 )); then test_pass "nothing ran"; else test_fail "missing runner counts" "suite=$(count .suite-runs) pol=$(count .pol-runs)"; fi
mv "${fix}/tests/run-sovereign-tests.zsh.off" "${fix}/tests/run-sovereign-tests.zsh"

# --- a runner that cannot start (status 127) is "could not run" (exit 4) -----------------
print start > "${fix}/.suite-rc"
p0=$(count .pol-runs)
run_gate
test_start "a runner that cannot start is reported as could not run (exit 4)"
if (( rc == 4 )) && [[ "${out}" == *"could not run"* ]]; then test_pass "could not run (exit ${rc})"; else test_fail "runner cannot start" "rc=${rc} ${out[1,200]}"; fi
test_start "a runner that cannot start is not a test or Proof of Life failure, and the Proof of Life does not start"
if [[ "${out}" != *"Mandate L Violation"* && "${out}" != *widget-check* ]] && (( $(count .pol-runs) == p0 )); then
    test_pass "no Mandate L message, Proof of Life not run"
else
    test_fail "runner cannot start" "pol=$(count .pol-runs) ${out[1,200]}"
fi
print pass > "${fix}/.suite-rc"

# --- behave unavailable is "could not run" (exit 4), not a Proof of Life failure ----------
touch "${fix}/.pol-nobehave"
p0=$(count .pol-runs)
run_gate
test_start "behave unavailable is reported as could not run (exit 4)"
if (( rc == 4 )) && [[ "${out}" == *"could not run"* ]]; then test_pass "could not run (exit ${rc})"; else test_fail "behave unavailable" "rc=${rc} ${out[1,200]}"; fi
test_start "behave unavailable is not a Mandate L violation, and no Proof of Life run happens"
if [[ "${out}" != *"Mandate L Violation"* ]] && (( $(count .pol-runs) == p0 )); then test_pass "no Mandate L message, no run"; else test_fail "behave unavailable" "pol=$(count .pol-runs) ${out[1,200]}"; fi
rm -f "${fix}/.pol-nobehave"

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_PASSED > 0 && TESTS_FAILED == 0 ))
