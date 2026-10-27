#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: tracked language compose baseline (Signet #561).
#
# No tracked compose may hardcode "../../../../projects/<name>" (it ignores the
# configured Projects base); the workspace volume must use the
# ${VDE_PROJECTS_DIR:-...} interpolation. dynamic-vm is the Proof of Life fixture
# and is intentionally tracked.
# "--custom" is not a VM: a tracked "--custom" compose/env is a stray artifact
# of passing the add-vm-type --custom flag where a VM name belongs.
#
# Reads only git's index and the working tree; no Docker, no writes.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

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

test_start "no tracked '--custom' VM artifacts"
typeset -a stray
stray=(${(f)"$(git ls-files | grep -e '--custom')"})
if (( ${#stray} == 0 )); then
    test_pass "no tracked '--custom' VM artifacts"
else
    test_fail "no tracked '--custom' VM artifacts" "${(j:, :)stray}"
fi

test_start "dynamic-vm (Proof of Life fixture) compose stays tracked"
if git ls-files --error-unmatch configs/docker/languages/dynamic-vm/docker-compose.yml &>/dev/null; then
    test_pass "dynamic-vm (Proof of Life fixture) compose stays tracked"
else
    test_fail "dynamic-vm compose stays tracked" "not in the index"
fi

test_start "no tracked compose hardcodes the projects/ workspace volume (dynamic-vm included)"
typeset -a bad
typeset f
for f in ${(f)"$(git ls-files 'configs/docker/*docker-compose*.yml')"}; do
    [[ -f "${f}" ]] || continue
    grep -qE '^\s*-\s+"?(\.\./)+projects/' "${f}" && bad+=("${f}")
done
if (( ${#bad} == 0 )); then
    test_pass "no tracked compose hardcodes the projects/ workspace volume (dynamic-vm included)"
else
    test_fail "hardcoded projects/ volume" "${(j:, :)bad}"
fi

test_start "dynamic-vm compose uses the \${VDE_PROJECTS_DIR:-...} interpolation"
if grep -qF '${VDE_PROJECTS_DIR:-../../../../projects}/dynamic-vm:/home/devuser/workspace' configs/docker/languages/dynamic-vm/docker-compose.yml; then
    test_pass "dynamic-vm compose uses the interpolation"
else
    test_fail "dynamic-vm compose uses the interpolation" "interpolated volume line not found"
fi

test_start "no registered service VM is filed under configs/docker/languages/"
typeset -a misfiled
typeset svc
for svc in ${(f)"$(awk -F'|' '$1=="service"{sub(/^vde-/,"",$2); print $2}' data/vm-types.conf)"}; do
    # jupyterlab is a hybrid LANGUAGE VM mislabeled a service in the registry;
    # its reclassification is tracked in #572, so its languages/ compose is exempt.
    [[ "${svc}" == "jupyterlab" ]] && continue
    [[ -n "$(git ls-files "configs/docker/languages/${svc}")" ]] && misfiled+=("${svc}")
done
if (( ${#misfiled} == 0 )); then
    test_pass "no registered service VM is filed under configs/docker/languages/"
else
    test_fail "services misfiled under languages/" "${(j:, :)misfiled}"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
