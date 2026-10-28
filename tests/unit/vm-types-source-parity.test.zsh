#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: load_vm_types yields identical arrays from either registry source
# (Signet #576).
#
# The JSON path is primary; the .conf parser is the fallback. A registry "-"
# means "none" and must load as the same value from both, otherwise
# generate-all-configs renders different composes depending on which source
# happened to load. Each source is loaded in its own child zsh with a private
# cache and no lock, so the repo's real cache and locks are never touched.

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

typeset scratch; scratch="$(mktemp -d)"
trap 'command rm -rf -- "${scratch}"' EXIT

# dump_registry JSON_OVERRIDE -> one "name|type|aliases|display|install|cmd|svc|ssh" line per VM
dump_registry() {
    VDE_VM_TYPES_JSON="${1}" VDE_VM_TYPES_CACHE="${scratch}/cache.$$.${RANDOM}" \
    VDE_LOCKS_DIR="${scratch}/locks" VDE_NO_LOCK=1 VDE_NO_CACHE=1 \
    VDE_ROOT_DIR="${VDE_ROOT_DIR}" zsh -c '
        source "${VDE_ROOT_DIR}/lib/vde-constants" &>/dev/null
        source "${VDE_ROOT_DIR}/lib/vm-common" &>/dev/null
        load_vm_types >/dev/null 2>&1 || exit 3
        local n
        for n in ${(ok)VM_TYPE}; do
            print -r -- "${n}|${VM_TYPE[$n]}|${VM_ALIASES[$n]}|${VM_DISPLAY[$n]}|${VM_INSTALL[$n]}|${VM_CUSTOM_CMD[$n]}|${VM_SVC_PORTS[$n]}|${VM_SSH_PORT[$n]}"
        done
    '
}

test_start "JSON and CONF sources load identical registry arrays"
typeset json_dump conf_dump
json_dump="$(dump_registry "${VDE_ROOT_DIR}/data/vm-types.json")"
conf_dump="$(dump_registry "${scratch}/absent.json")"
typeset -a jl=("${(@f)json_dump}") cl=("${(@f)conf_dump}")
if (( ${#jl} < 20 || ${#cl} < 20 )); then
    test_fail "both sources loaded" "json rows=${#jl}, conf rows=${#cl}"
elif [[ "${json_dump}" == "${conf_dump}" ]]; then
    test_pass "${#jl} VMs identical across sources"
else
    typeset -a bad
    typeset i
    for (( i = 1; i <= ${#jl} || i <= ${#cl}; i++ )); do
        [[ "${jl[i]}" == "${cl[i]}" ]] || bad+=("json[${jl[i]}] conf[${cl[i]}]")
    done
    test_fail "sources differ (${#bad})" "${(j:; :)bad[1,3]}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
