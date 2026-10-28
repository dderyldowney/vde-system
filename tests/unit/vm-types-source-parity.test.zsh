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

# dump_registry JSON [CONF] [CACHE] [NO_CACHE] -> one "name|type|aliases|display|install|cmd|svc|ssh" line per VM
dump_registry() {
    VDE_VM_TYPES_JSON="${1}" VDE_VM_TYPES_CONF="${2:-${VDE_ROOT_DIR}/data/vm-types.conf}" \
    VDE_VM_TYPES_CACHE="${3:-${scratch}/cache.$$.${RANDOM}}" \
    VDE_LOCKS_DIR="${scratch}/locks" VDE_NO_LOCK=1 VDE_NO_CACHE="${4:-1}" \
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
typeset -a want_names got_json got_conf
want_names=(${(o)${(f)"$(awk -F'|' '$1=="lang"||$1=="service"{print $2}' data/vm-types.conf)"}})
got_json=(${(o)${jl%%|*}}); got_conf=(${(o)${cl%%|*}})
if (( ${#want_names} == 0 )) || [[ "${got_json}" != "${want_names}" || "${got_conf}" != "${want_names}" ]]; then
    test_fail "both sources load exactly the registered VMs" "expected ${#want_names}, json=${#got_json}, conf=${#got_conf}"
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

test_start "JSON null and CONF '-' both load as empty (nullable fields)"
typeset fx_conf="${scratch}/fx.conf" fx_json="${scratch}/fx.json"
print -r -- 'lang|vde-fx|fx|Fx|-|zsh /vde/scripts/setup/fx-init.zsh|-|2290' > "${fx_conf}"
print -r -- '{"version":"1.5.6","vms":{"language":[{"name":"vde-fx","aliases":["fx"],"display":"Fx","pkgs":null,"custom_cmd":"zsh /vde/scripts/setup/fx-init.zsh","service_ports":null,"ssh_port":2290}],"service":[]}}' > "${fx_json}"
typeset fxj fxc
fxj="$(dump_registry "${fx_json}" "${fx_conf}")"; fxc="$(dump_registry "${scratch}/absent.json" "${fx_conf}")"
if [[ -n "${fxj}" && "${fxj}" == "${fxc}" ]]; then
    test_pass "null and '-' agree: ${fxj}"
else
    test_fail "nullable parity" "json[${fxj}] conf[${fxc}]"
fi

test_start "an explicit JSON '-' also loads as empty"
sed -i 's/"pkgs":null/"pkgs":"-"/; s/"service_ports":null/"service_ports":"-"/' "${fx_json}"
fxj="$(dump_registry "${fx_json}" "${fx_conf}")"
if [[ -n "${fxj}" && "${fxj}" == "${fxc}" ]]; then
    test_pass "explicit '-' agrees with CONF"
else
    test_fail "explicit '-' parity" "json[${fxj}] conf[${fxc}]"
fi

test_start "a cache older than the loader is not trusted (stale '-' values)"
typeset old_conf="${scratch}/old.conf" poison="${scratch}/poison.cache"
cp data/vm-types.conf "${old_conf}"; touch -d '2001-01-01' "${old_conf}"
dump_registry "${scratch}/absent.json" "${old_conf}" "${poison}" 1 >/dev/null
if [[ -f "${poison}" ]]; then
    sed -i -E "s/^(VM_INSTALL|VM_SVC_PORTS)\[(.*)\]=''\$/\1[\2]='-'/" "${poison}"
    touch -d '2002-01-01' "${poison}"
    typeset stale_dump; stale_dump="$(dump_registry "${scratch}/absent.json" "${old_conf}" "${poison}" 0)"
    if [[ "${stale_dump}" == "${conf_dump}" ]]; then
        test_pass "loader ignored the pre-fix cache and reloaded"
    else
        test_fail "stale cache trusted" "cache older than lib/vm-common still served '-' values"
    fi
else
    test_fail "cache fixture" "loader did not write ${poison}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
