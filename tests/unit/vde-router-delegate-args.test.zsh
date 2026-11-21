#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: bin/vde forwards typed arguments to its delegates (Signet #584).
#
# audit, check-tetrad/spine-check and heal were dispatched with "$@", which the
# parse loop had already emptied, so the delegates never saw what was typed.
# A copy of bin/vde runs against stub delegates that echo their argv.

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
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Sandbox root: real bin/vde and lib/data, stub delegates that print their argv.
typeset _root="$(mktemp -d)"
trap 'rm -rf "${_root}"' EXIT
mkdir -p "${_root}/bin"
cp "${VDE_ROOT_DIR}/bin/vde" "${_root}/bin/vde"
for _d in lib data scripts templates docs; do
    [[ -e "${VDE_ROOT_DIR}/${_d}" ]] && ln -s "${VDE_ROOT_DIR}/${_d}" "${_root}/${_d}"
done
for _s in vde-gospel-audit.zsh vde-check-tetrad.zsh vde-heal-docs.zsh; do
    printf '#!/usr/bin/env zsh\nprint -r -- "ARGS=[$*]"\n' > "${_root}/bin/${_s}"
    chmod +x "${_root}/bin/${_s}"
done

check_forward() {
    local label="$1" cmd="$2" stub="$3"
    local out
    test_start "${label}: typed args reach the delegate"
    out="$(zsh "${_root}/bin/vde" "${cmd}" --probe-arg 2>/dev/null)"
    if [[ "${out}" == *"ARGS=[--probe-arg]"* ]]; then
        test_pass "${cmd} forwards typed args to ${stub}"
    else
        test_fail "${cmd} args" "expected ARGS=[--probe-arg], got [${out[1,160]}]"
    fi
}

check_forward "audit" audit vde-gospel-audit.zsh
check_forward "check-tetrad" check-tetrad vde-check-tetrad.zsh
check_forward "spine-check" spine-check vde-check-tetrad.zsh
check_forward "heal" heal vde-heal-docs.zsh

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
