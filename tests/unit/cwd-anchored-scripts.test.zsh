#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit Tests for the root anchoring of the five maintenance scripts (Signet #661).
#
# bin/vde-armor-heal.zsh, vde-heal-docs.zsh, vde-gospel-audit.zsh, vde-sync-version
# and vde-rebuild-cache used to take ./lib, ./data, ./docs and ./bin from the
# CALLER's current directory (or a root that is "." when started by bare name from
# bin/). docs/governance/vde-spec.md (Pure Relative Pathing) says artifacts are
# reached relative to VDE_ROOT_DIR. Same decoy technique as the Tetrad gate's test
# (Signet #655): where a case needs it, the script runs from a DECOY directory, a
# complete-looking tree that differs from the real root in exactly one way, so a
# cwd-bound script reads the decoy and an anchored one ignores it.
#
# Safety: every case runs a COPY of the tracked tree (never the real tree), with
# HOME pointed at a scratch directory because vde-sync-version edits $HOME/.zshrc.

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
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }

# The tree under test is the one this file lives in, never an inherited VDE_ROOT_DIR.
typeset SRC_ROOT="${0:A:h:h:h}"
typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }
SCRATCH="${SCRATCH:A}"
trap 'rm -rf -- "${SCRATCH}"' EXIT

typeset FAKEHOME="${SCRATCH}/home"
mkdir -p "${FAKEHOME}"

# make_tree <dir>: a copy of the tracked tree (working-tree content), no .git.
make_tree() {
    mkdir -p "$1"
    git -C "${SRC_ROOT}" ls-files -z \
        | tar -c -C "${SRC_ROOT}" --null -T - -f - | tar -x -C "$1" -f -
}

# Variables scrubbed from every run: git's repository selectors, the cache override
# VM_TYPES_CACHE, and EVERY exported VDE_* variable (VDE_ROOT_DIR, VDE_CACHE_DIR,
# VDE_VM_TYPES_CACHE, ... are all honoured by the libs, so an inherited one could
# point a script at state outside the scratch tree).
typeset -a SCRUB
typeset _v
compute_scrub() {
    SCRUB=(-u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR -u VM_TYPES_CACHE)
    for _v in ${(f)"$(env | sed -n 's/^\(VDE_[A-Za-z0-9_]*\)=.*/\1/p')"}; do
        SCRUB+=(-u "${_v}")
    done
}
compute_scrub

# run_script <cwd> <script as typed> -> sets OUT and RC
typeset OUT RC
run_script() {
    OUT=$(cd "$1" && env "${SCRUB[@]}" HOME="${FAKEHOME}" zsh "$2" 2>&1)
    RC=$?
}

# a registry that is valid JSON?
json_ok() { python3 -c "import json,sys; json.load(sys.stdin)" < "$1" 2>/dev/null }

typeset -a SCRIPTS
SCRIPTS=(vde-armor-heal.zsh vde-heal-docs.zsh vde-gospel-audit.zsh vde-sync-version vde-rebuild-cache)

#-------------------------------------------------------------------------------
# 1 + 2: same behaviour from an empty directory (absolute path) and from bin/ by
# bare name. One tree per script; the empty directory must stay empty.
typeset s T E before after
for s in ${SCRIPTS}; do
    T="${SCRATCH}/tree-${s}"
    E="${SCRATCH}/empty-${s}"
    make_tree "${T}"
    mkdir -p "${E}"

    test_start "${s} succeeds from an unrelated empty directory and leaves it empty"
    run_script "${E}" "${T}/bin/${s}"
    if [[ "${RC}" == "0" && -z "$(ls -A "${E}")" && "${OUT}" != *"no such file or directory"* ]]; then
        test_pass "${s}: exit 0, nothing written to the caller's directory"
    else
        test_fail "${s} depends on the caller's directory" \
            "rc=${RC} found=[$(ls -A "${E}" | tr '\n' ' ')] out=${OUT[1,200]}"
    fi

    test_start "${s} succeeds when started from bin/ by bare name"
    before="$(ls -A "${T}/bin" | tr '\n' ' ')"
    run_script "${T}/bin" "${s}"
    after="$(ls -A "${T}/bin" | tr '\n' ' ')"
    if [[ "${RC}" == "0" && "${before}" == "${after}" && "${OUT}" != *"no such file or directory"* ]]; then
        test_pass "${s}: exit 0 from bin/, bin/ unchanged"
    else
        test_fail "${s} breaks when started from bin/" \
            "rc=${RC} bin-changed=$([[ ${before} == ${after} ]] && echo no || echo yes) out=${OUT[1,200]}"
    fi
done

#-------------------------------------------------------------------------------
test_start "vde-heal-docs.zsh repairs the ROOT's registry and leaves a decoy's corrupt registry byte-identical"
typeset R1="${SCRATCH}/r-heal" D1="${SCRATCH}/d-heal"
make_tree "${R1}"
mkdir -p "${D1}/data" "${D1}/docs/reference"
print -r -- '{corrupt' > "${R1}/data/vm-types.json"
print -r -- '{corrupt' > "${D1}/data/vm-types.json"
cp "${R1}/data/vm-types.conf" "${D1}/data/vm-types.conf"
cp "${R1}/docs/reference/scripts.md" "${D1}/docs/reference/scripts.md"
ln -s "${R1}/lib" "${D1}/lib"
ln -s "${R1}/bin" "${D1}/bin"
typeset decoy_sum="$(cksum < "${D1}/data/vm-types.json")"
run_script "${D1}" "${R1}/bin/vde-heal-docs.zsh"
if [[ "${RC}" == "0" && "$(cksum < "${D1}/data/vm-types.json")" == "${decoy_sum}" ]] && json_ok "${R1}/data/vm-types.json"; then
    test_pass "root registry restored, decoy registry untouched"
else
    test_fail "heal-docs acted on the caller's directory" \
        "rc=${RC} decoy-same=$([[ $(cksum < ${D1}/data/vm-types.json) == ${decoy_sum} ]] && echo yes || echo NO) root-valid=$(json_ok ${R1}/data/vm-types.json && echo yes || echo NO) out=${OUT[1,160]}"
fi

#-------------------------------------------------------------------------------
test_start "vde-sync-version corrects the ROOT's registry version and never the decoy's"
typeset R2="${SCRATCH}/r-sync" D2="${SCRATCH}/d-sync"
make_tree "${R2}"
make_tree "${D2}"
typeset SPEC_VERSION
SPEC_VERSION=$(grep -m1 '^# VDE-SPEC ' "${R2}/docs/governance/vde-spec.md" \
    | sed -E 's/^# VDE-SPEC v?([0-9]+\.[0-9]+\.[0-9]+(-sp[0-9]+)?).*/\1/' | tr -d '[:space:]')
if [[ -z "${SPEC_VERSION}" ]]; then
    echo "setup error: no version found in docs/governance/vde-spec.md"; exit 1
fi
printf '{"version": "9.9.9"}\n' > "${R2}/data/vm-types.json"
printf '{"version": "8.8.8"}\n' > "${D2}/data/vm-types.json"
run_script "${D2}" "${R2}/bin/vde-sync-version"
if [[ "${RC}" == "0" && "$(<"${R2}/data/vm-types.json")" == *"\"${SPEC_VERSION}\""* \
      && "$(<"${D2}/data/vm-types.json")" == *'"8.8.8"'* ]]; then
    test_pass "root registry now at ${SPEC_VERSION}, decoy registry still 8.8.8"
else
    test_fail "sync-version acted on the caller's directory" \
        "rc=${RC} root=$(<${R2}/data/vm-types.json) decoy=$(<${D2}/data/vm-types.json) out=${OUT[1,160]}"
fi

#-------------------------------------------------------------------------------
test_start "vde-gospel-audit fails when the ROOT's script doc is missing, even if the caller's tree has one"
typeset R3="${SCRATCH}/r-audit" D3="${SCRATCH}/d-audit"
make_tree "${R3}"
make_tree "${D3}"
rm "${R3}/docs/reference/scripts.md"
run_script "${D3}" "${R3}/bin/vde-gospel-audit.zsh"
if [[ "${RC}" != "0" && "${OUT}" == *"scripts.md"* ]]; then
    test_pass "exit ${RC}, names scripts.md"
else
    test_fail "gospel-audit judged the caller's tree, not the root" "rc=${RC} out=${OUT[-200,-1]}"
fi

#-------------------------------------------------------------------------------
test_start "harness: inherited cache overrides cannot point a script at state outside the scratch tree"
typeset EXT="${SCRATCH}/external-cache" R4="${SCRATCH}/r-cache"
mkdir -p "${EXT}"
print -r -- "sentinel" > "${EXT}/vm-types.cache"
make_tree "${R4}"
typeset ext_sum="$(cksum < "${EXT}/vm-types.cache")"
export VDE_CACHE_DIR="${EXT}" VDE_VM_TYPES_CACHE="${EXT}/vm-types.cache" VM_TYPES_CACHE="${EXT}/vm-types.cache"
compute_scrub   # as at startup, now seeing the hostile overrides exported above
run_script "${SCRATCH}" "${R4}/bin/vde-rebuild-cache"
unset VDE_CACHE_DIR VDE_VM_TYPES_CACHE VM_TYPES_CACHE
compute_scrub
if [[ "${RC}" == "0" && "$(cksum < "${EXT}/vm-types.cache")" == "${ext_sum}" && -f "${R4}/.cache/vm-types.cache" ]]; then
    test_pass "the external cache is byte-identical; the scratch root's own cache was rebuilt"
else
    test_fail "an inherited override leaked into a run" \
        "rc=${RC} external-same=$([[ $(cksum < ${EXT}/vm-types.cache) == ${ext_sum} ]] && echo yes || echo NO) scratch-cache=$([[ -f ${R4}/.cache/vm-types.cache ]] && echo yes || echo NO) out=${OUT[1,160]}"
fi

#-------------------------------------------------------------------------------
echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
