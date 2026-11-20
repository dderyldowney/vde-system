#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit Tests for the Tetrad gate's root anchoring (Signet #655).
#
# docs/governance/vde-spec.md (Pure Relative Pathing) says artifacts are reached
# relative to VDE_ROOT_DIR, not relative to the caller's directory. The gate
# (bin/vde-check-tetrad.zsh) used to read ./data, ./lib, ./scripts, ./.cache,
# ./lib/vde-core and ./data/vm-types.json against the CALLER's cwd, so it passed
# or failed according to where it was started.
#
# Each case below runs the gate from a DECOY directory: a complete-looking tree
# that differs from the real root in exactly one way. A cwd-bound gate reads the
# decoy and gets a different answer; an anchored gate ignores it. (An empty
# unrelated directory would not do: the old gate fails there too, which would
# hide whether a given anchor is present.)

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

typeset REAL_ROOT="${VDE_ROOT_DIR}"
typeset GATE_SRC="${REAL_ROOT}/bin/vde-check-tetrad.zsh"
typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }
SCRATCH="${SCRATCH:A}"
trap 'rm -rf -- "${SCRATCH}"' EXIT

# The gate only checks that the pillars exist; stubs make the cases independent
# of whether the machine running them has Docker or an ssh client installed.
typeset STUBS="${SCRATCH}/stubs"
mkdir -p "${STUBS}"
for _tool in docker ssh; do
    printf '#!/usr/bin/env zsh\nexit 1\n' > "${STUBS}/${_tool}"
    chmod +x "${STUBS}/${_tool}"
done

typeset SPEC_VERSION
SPEC_VERSION=$(grep -m1 '^# VDE-SPEC ' "${REAL_ROOT}/docs/governance/vde-spec.md" \
    | sed -E 's/^# VDE-SPEC v?([0-9]+\.[0-9]+\.[0-9]+(-sp[0-9]+)?).*/\1/' | tr -d '[:space:]')
if [[ -z "${SPEC_VERSION}" ]]; then
    echo "setup error: no version found in docs/governance/vde-spec.md; every case would fail for the wrong reason"
    exit 1
fi

# make_root <dir> [json-version]
# A complete miniature root: the real gate and the real lib/ (linked), a spec
# file, a registry whose version matches the spec (or the one given).
make_root() {
    typeset dir="$1" json_ver="${2:-${SPEC_VERSION}}"
    mkdir -p "${dir}/bin" "${dir}/data" "${dir}/scripts" "${dir}/docs/governance"
    cp "${GATE_SRC}" "${dir}/bin/vde-check-tetrad.zsh"
    ln -s "${REAL_ROOT}/lib" "${dir}/lib"
    cp "${REAL_ROOT}/docs/governance/vde-spec.md" "${dir}/docs/governance/vde-spec.md"
    printf '{"version": "%s"}\n' "${json_ver}" > "${dir}/data/vm-types.json"
}

# run_gate <cwd> <gate path as typed>  -> sets GATE_OUT and GATE_RC
typeset GATE_OUT GATE_RC
run_gate() {
    GATE_OUT=$(cd "$1" && env -u VDE_ROOT_DIR PATH="${STUBS}:${PATH}" zsh "$2" 2>&1)
    GATE_RC=$?
}

#-------------------------------------------------------------------------------
test_start "The gate gives the same verdict from the root, from bin/ by bare name, and from an unrelated directory"
typeset R1="${SCRATCH}/r1" ELSEWHERE="${SCRATCH}/elsewhere"
make_root "${R1}"
mkdir -p "${ELSEWHERE}"
typeset -a rcs outs
run_gate "${R1}"      "bin/vde-check-tetrad.zsh";   rcs+=(${GATE_RC}); outs+=("${GATE_OUT}")
run_gate "${R1}/bin"  "vde-check-tetrad.zsh";       rcs+=(${GATE_RC}); outs+=("${GATE_OUT}")
run_gate "${ELSEWHERE}" "${R1}/bin/vde-check-tetrad.zsh"; rcs+=(${GATE_RC}); outs+=("${GATE_OUT}")
typeset bad=""
for i in 1 2 3; do
    [[ "${rcs[$i]}" == "0" ]] || bad+=" case${i}:rc=${rcs[$i]}"
    [[ "${outs[$i]}" != *"Missing core"* ]] || bad+=" case${i}:reported-missing"
    [[ "${outs[$i]}" == *"Technical Integrity Verified"* ]] || bad+=" case${i}:no-verified-line"
done
if [[ -z "${bad}" ]]; then
    test_pass "all three runs exit 0 and verify the root"
else
    test_fail "verdict depends on the caller's directory" "${bad} | bin/ output: ${outs[2]}"
fi

#-------------------------------------------------------------------------------
test_start "The caller's directory is left untouched (no .cache, nothing written)"
typeset UNTOUCHED="${SCRATCH}/untouched"
mkdir -p "${UNTOUCHED}"
run_gate "${UNTOUCHED}" "${R1}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_RC}" == "0" && -z "$(ls -A "${UNTOUCHED}")" ]]; then
    test_pass "the gate succeeded and the unrelated directory is still empty"
else
    test_fail "the gate wrote into the caller's directory" "rc=${GATE_RC} found: $(ls -A "${UNTOUCHED}" | tr '\n' ' ')"
fi

#-------------------------------------------------------------------------------
test_start "A root missing data/ fails and names data, even when the cwd holds a data/ of its own"
typeset R2="${SCRATCH}/r2" DECOY2="${SCRATCH}/decoy2"
make_root "${R2}"; rm -rf "${R2}/data"
make_root "${DECOY2}"
run_gate "${DECOY2}" "${R2}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_RC}" == "1" && "${GATE_OUT}" == *"Missing core directory: data"* \
      && "${GATE_OUT}" != *"${R2}"* ]]; then
    test_pass "exit 1, 'Missing core directory: data', no host path in the message"
else
    test_fail "dir check is not anchored to the root" "rc=${GATE_RC} out=${GATE_OUT}"
fi

#-------------------------------------------------------------------------------
test_start "A root missing lib/vm-common fails and names it, even when the cwd holds one"
typeset R3="${SCRATCH}/r3" DECOY3="${SCRATCH}/decoy3"
make_root "${R3}"; rm "${R3}/lib"; mkdir "${R3}/lib"; : > "${R3}/lib/vde-core"
make_root "${DECOY3}"
run_gate "${DECOY3}" "${R3}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_RC}" == "1" && "${GATE_OUT}" == *"Missing core artifact: lib/vm-common"* ]]; then
    test_pass "exit 1, 'Missing core artifact: lib/vm-common'"
else
    test_fail "file check is not anchored to the root" "rc=${GATE_RC} out=${GATE_OUT}"
fi

#-------------------------------------------------------------------------------
test_start ".cache is created under the root, never under the caller's directory"
typeset R4="${SCRATCH}/r4" DECOY4="${SCRATCH}/decoy4"
make_root "${R4}"
make_root "${DECOY4}"
run_gate "${DECOY4}" "${R4}/bin/vde-check-tetrad.zsh"
if [[ -d "${R4}/.cache" && ! -e "${DECOY4}/.cache" ]]; then
    test_pass ".cache exists in the root and not in the caller's directory"
else
    test_fail ".cache landed in the wrong place" "root:$([[ -d ${R4}/.cache ]] && echo yes || echo no) caller:$([[ -e ${DECOY4}/.cache ]] && echo yes || echo no) rc=${GATE_RC}"
fi

#-------------------------------------------------------------------------------
test_start "The gate sources the root's lib/vde-core, not the caller's"
typeset R5="${SCRATCH}/r5" DECOY5="${SCRATCH}/decoy5"
make_root "${R5}"
make_root "${DECOY5}"
rm "${DECOY5}/lib"; mkdir "${DECOY5}/lib"
print -r -- 'echo DECOY-CORE-SOURCED' > "${DECOY5}/lib/vde-core"
print -r -- "vde_get_version() { echo ${SPEC_VERSION} }" >> "${DECOY5}/lib/vde-core"
print -r -- "vde_query_json() { echo '\"${SPEC_VERSION}\"' }" >> "${DECOY5}/lib/vde-core"
: > "${DECOY5}/lib/vm-common"
run_gate "${DECOY5}" "${R5}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_OUT}" != *"DECOY-CORE-SOURCED"* && "${GATE_RC}" == "0" ]]; then
    test_pass "the decoy lib/vde-core was never sourced"
else
    test_fail "source is not anchored to the root" "rc=${GATE_RC} out=${GATE_OUT}"
fi

#-------------------------------------------------------------------------------
test_start "The version handshake reads the root's data/vm-types.json, not the caller's"
typeset R6="${SCRATCH}/r6" DECOY6="${SCRATCH}/decoy6"
make_root "${R6}"
make_root "${DECOY6}" "9.9.9"
run_gate "${DECOY6}" "${R6}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_RC}" == "0" && "${GATE_OUT}" != *"Baseline Drift"* ]]; then
    test_pass "no drift reported: the root's registry matched the root's spec"
else
    test_fail "registry read is not anchored to the root" "rc=${GATE_RC} out=${GATE_OUT}"
fi

#-------------------------------------------------------------------------------
test_start "On real drift the gate runs the root's heal script, from the root"
typeset R7="${SCRATCH}/r7" DECOY7="${SCRATCH}/decoy7"
make_root "${R7}" "9.9.9"
make_root "${DECOY7}"
print -r -- '#!/usr/bin/env zsh' > "${R7}/bin/vde-armor-heal.zsh"
print -r -- 'echo "HEAL-RAN-IN:${PWD:A}"' >> "${R7}/bin/vde-armor-heal.zsh"
run_gate "${DECOY7}" "${R7}/bin/vde-check-tetrad.zsh"
if [[ "${GATE_OUT}" == *"HEAL-RAN-IN:${R7}"* && "${GATE_RC}" == "0" ]]; then
    test_pass "the heal script ran with the root as its working directory"
else
    test_fail "heal call is not anchored to the root" "rc=${GATE_RC} out=${GATE_OUT}"
fi

#-------------------------------------------------------------------------------
echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
