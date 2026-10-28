#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: language composes match a fresh render of the template (Signet #531).
#
# templates/compose-language.yml is the source of truth (Mandate B). Every
# registered language VM's tracked docker-compose.yml must equal what
# bin/generate-all-configs would render from the registry today, so a template
# edit without regeneration (or a hand-edited compose) fails here instead of
# surfacing later as a 30-file --force churn. dynamic-vm is the Proof of Life
# fixture, is not registered, and is intentionally outside this check.
#
# Renders in memory with the generator's own calls; no Docker, no writes.

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

source "${VDE_ROOT_DIR}/lib/vde-constants" &>/dev/null
source "${VDE_ROOT_DIR}/lib/vm-common"     &>/dev/null
source "${VDE_ROOT_DIR}/lib/vde-templates" &>/dev/null
typeset -g TEMPLATES_DIR="${TEMPLATES_DIR:-${VDE_ROOT_DIR}/templates}"

# render_registered NAME PKGS CMD SSH SVC -> the generator's language render
render_registered() {
    local name="${1}" pkgs="${2}" cmd="${3}" ssh="${4}" svc="${5}"
    [[ "${pkgs}" == "-" ]] && pkgs=""
    local out; out="$(render_language_template "${name}" "${ssh}" "${cmd}" "${svc}" "$(vde_workspace_subpath "${name}")")"
    print -r -- "${out//\{\{PKGS\}\}/${pkgs}}"
}

# first_diff A B -> "line N: <a> | <b>" for the first differing line
first_diff() {
    local -a a=("${(@f)1}") b=("${(@f)2}")
    local i
    for (( i = 1; i <= ${#a} || i <= ${#b}; i++ )); do
        [[ "${a[i]}" == "${b[i]}" ]] || { print -r -- "line ${i}: [${a[i]}] vs [${b[i]}]"; return; }
    done
}

test_start "drift detector: an altered render is reported (fixture)"
typeset base alt
base="$(render_registered go '-' 'zsh x' 2208 '-')"
alt="${base/restart: unless-stopped/restart: always}"
if [[ "${base}" != "${alt}" && -n "$(first_diff "${base}" "${alt}")" ]]; then
    test_pass "first_diff reports the changed line"
else
    test_fail "first_diff reports the changed line" "no difference detected"
fi

test_start "every registered language compose equals a fresh render"
typeset -a drifted
typeset type vm vmaliases display pkgs cmd svc ssh name tracked fresh
while IFS='|' read -r type vm vmaliases display pkgs cmd svc ssh; do
    [[ "${type}" == lang ]] || continue
    name="${vm#vde-}"
    tracked="configs/docker/languages/${name}/docker-compose.yml"
    if [[ ! -f "${tracked}" ]]; then drifted+=("${name}: compose missing"); continue; fi
    fresh="$(render_registered "${name}" "${pkgs}" "${cmd}" "${ssh}" "${svc}")"
    [[ "$(<${tracked})" == "${fresh}" ]] || drifted+=("${name} ($(first_diff "$(<${tracked})" "${fresh}"))")
done < <(grep '^lang|' data/vm-types.conf)
if (( ${#drifted} == 0 )); then
    test_pass "no language compose has drifted from the template"
else
    test_fail "drifted from template (${#drifted})" "${(j:; :)drifted}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
