#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests for rebuild flag/target separation (Signet #556).
#
# `vde rebuild --no-cache python` used to push "--no-cache" through target
# resolution as if it were a VM. vde_split_rebuild_args (lib/vde-core) now
# separates vde-rebuild's own flags from targets. These tests exercise that pure
# function directly: no Docker, no sync_keys, no writes to .env.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

source "${VDE_ROOT_DIR}/lib/vde-shell-compat"
source "${VDE_ROOT_DIR}/lib/vde-constants"
source "${VDE_ROOT_DIR}/lib/vde-core"

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

# expect <label> <want-flags> <want-rest> -- <args...>
# want-* are space-joined strings (empty string = none).
expect() {
    local label="$1" want_flags="$2" want_rest="$3"
    shift 4
    test_start "${label}"
    vde_split_rebuild_args "$@"
    local rc=$?
    if (( rc != 0 )); then
        test_fail "${label}" "unexpected rc=${rc}"
    elif [[ "${(j: :)VDE_REBUILD_FLAGS}" != "${want_flags}" ]]; then
        test_fail "${label}" "flags='${(j: :)VDE_REBUILD_FLAGS}' want '${want_flags}'"
    elif [[ "${(j: :)VDE_REBUILD_REST}" != "${want_rest}" ]]; then
        test_fail "${label}" "rest='${(j: :)VDE_REBUILD_REST}' want '${want_rest}'"
    else
        test_pass "${label}"
    fi
}

expect "--no-cache before target is a flag"      "--no-cache"  "python"  -- --no-cache python
expect "--no-cache after target is a flag"       "--no-cache"  "python"  -- python --no-cache
expect "no flags: target only"                   ""            "python"  -- python
expect "--pull is a flag"                        "--pull"      "python"  -- --pull python
expect "--regenerate-keys is a flag"             "--regenerate-keys" "go" -- --regenerate-keys go
expect "several flags, several targets"          "--no-cache --pull" "python go" -- --no-cache python --pull go
expect "--help is forwarded as a flag"           "--help"      ""        -- --help
expect "--vm value becomes a target"             ""            "default" -- --vm default
expect "--vm combined with --no-cache"           "--no-cache"  "python"  -- --no-cache --vm python
expect "no arguments"                            ""            ""        --
expect "-f is left for the caller's parser"      ""            "-f python" -- -f python

test_start "--vm without a value is rejected"
vde_split_rebuild_args --vm
if (( $? == VDE_ERR_INVALID_INPUT )); then
    test_pass "--vm without a value is rejected"
else
    test_fail "--vm without a value is rejected" "rc=$?"
fi

test_start "--vm followed by a flag is rejected"
vde_split_rebuild_args --vm --no-cache
if (( $? == VDE_ERR_INVALID_INPUT )); then
    test_pass "--vm followed by a flag is rejected"
else
    test_fail "--vm followed by a flag is rejected" "rc=$?"
fi

# Wiring guard: bin/vde must apply the splitter only to rebuild/create and
# forward the flags to vde-rebuild. Other commands keep their loud
# "Unknown VM type" error for an unrecognised --no-cache.
test_start "bin/vde wires the splitter for rebuild/create only"
typeset src="$(<"${VDE_ROOT_DIR}/bin/vde")"
if [[ "${src}" == *'if [[ "${ACTION}" == "rebuild" || "${ACTION}" == "create" ]]; then'*'vde_split_rebuild_args "$@"'* \
   && "${src}" == *'bin/vde-rebuild" "${VDE_REBUILD_FLAGS[@]}" "${targets[@]}"'* ]]; then
    test_pass "bin/vde wires the splitter for rebuild/create only"
else
    test_fail "bin/vde wires the splitter for rebuild/create only" "wiring not found"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
