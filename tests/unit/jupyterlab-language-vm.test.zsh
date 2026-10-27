#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: jupyterlab is a hybrid LANGUAGE VM (Signet #572).
#
# Python workspace + Jupyter Lab on 8888. It must be registered as a language,
# its compose must publish SSH 2225 and 8888, mount projects/python/jupyterlabs,
# and no service-flavoured compose may remain for it.
#
# Reads the registry, templates and tracked files; no Docker, no writes.

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
check() { [[ "$2" == "$3" ]] && test_pass "$1" || test_fail "$1" "expected [$2] got [$3]"; }

source "${VDE_ROOT_DIR}/lib/vde-constants" &>/dev/null
source "${VDE_ROOT_DIR}/lib/vm-common"     &>/dev/null
source "${VDE_ROOT_DIR}/lib/vde-templates" &>/dev/null
typeset -g TEMPLATES_DIR="${TEMPLATES_DIR:-${VDE_ROOT_DIR}/templates}"

typeset -a row=("${(@s:|:)$(grep '^[a-z]*|vde-jupyterlab|' data/vm-types.conf)}")
test_start "registry: jupyterlab is category lang with ports 8888 / ssh 2225"
check "category" "lang" "${row[1]}"
check "service ports" "8888" "${row[7]}"
check "ssh port" "2225" "${row[8]}"

test_start "json registry: jupyterlab is listed under language, not service"
typeset js; js="$(<data/vm-types.json)"
typeset lang_part="${js%%\"service\"*}"
[[ "${lang_part}" == *vde-jupyterlab* ]] && test_pass "in language list" || test_fail "in language list" "not found before the service key"
[[ "${js#*\"service\"}" == *vde-jupyterlab* ]] && test_fail "not in service list" "still listed after the service key" || test_pass "not in service list"

test_start "template: service ports are published alongside SSH"
typeset out; out="$(render_language_template jupyterlab 2225 'x' 8888 python/jupyterlabs)"
[[ "${out}" == *'- "2225:2225"'* && "${out}" == *'- "8888:8888"'* ]] && test_pass "publishes 2225 and 8888" || test_fail "publishes 2225 and 8888" "ports missing"
[[ "${out}" == */python/jupyterlabs:/home/devuser/workspace* ]] && test_pass "workspace subpath honored" || test_fail "workspace subpath honored" "mount not python/jupyterlabs"

test_start "template: a plain language VM renders unchanged (no extra port line, name workspace)"
out="$(render_language_template go 2208 'x' '-')"
typeset portpat='*- "<->:<->"'
typeset -a portlines=(${(M)${(f)out}:#${~portpat}})
check "port lines" "1" "${#portlines}"
[[ "${out}" == *'/go:/home/devuser/workspace'* ]] && test_pass "default workspace" || test_fail "default workspace" "mount not /go"

test_start "tracked compose: jupyterlab is a language compose with 2225 + 8888, no service boilerplate"
typeset f=configs/docker/languages/jupyterlab/docker-compose.yml
[[ -f "${f}" ]] || test_fail "compose exists" "${f} missing"
typeset c; c="$(<${f})"
[[ "${c}" == *'"2225:2225"'* && "${c}" == *'"8888:8888"'* && "${c}" != *2407* && "${c}" != *2401* ]] && test_pass "ports" || test_fail "ports" "expected 2225+8888, no 2407"
[[ "${c}" == *'/python/jupyterlabs:/home/devuser/workspace'* ]] && test_pass "workspace" || test_fail "workspace" "not python/jupyterlabs"
[[ -z "$(git ls-files configs/docker/services/jupyterlab)" ]] && test_pass "no services/jupyterlab compose" || test_fail "no services/jupyterlab compose" "still tracked"

test_start "vde-init no longer creates a data/jupyterlab service dir"
typeset sd_line; sd_line="$(grep -m1 'local service_dirs=' bin/vde-init)"
typeset -a sd=(${=${${sd_line#*\(}%\)*}})
if [[ -z "${sd_line}" ]]; then test_fail "service_dirs" "array not found"
elif (( ${sd[(Ie)jupyterlab]} )); then test_fail "service_dirs" "jupyterlab still listed"
else test_pass "service_dirs clean (${#sd} entries)"; fi

test_start "get_vm_mounts agrees with the compose workspace"
[[ "$(get_vm_mounts jupyterlab)" == *python/jupyterlabs:/home/devuser/workspace* ]] && test_pass "mount" || test_fail "mount" "$(get_vm_mounts jupyterlab)"

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
