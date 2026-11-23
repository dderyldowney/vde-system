#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit tests for the honesty of bin/coverage.zsh (Signet #725).
#
# bin/coverage.zsh derives its root from $0, so every case copies the REAL
# bin/coverage.zsh into a fixture tree <root>/bin/coverage.zsh, creates tiny
# fake *.test.zsh scripts under <root>/tests/{unit,integration}, and runs the
# script the way CI does: cd <root> && ./bin/coverage.zsh <mode>, with a stub
# kcov first on PATH, a scratch HOME, and stdin from /dev/null.
#
# The stub kcov logs every call to $STUB_LOG. A non-merge call takes the first
# non-option argument as the output directory, writes an index.html and a
# data-<dir name> file there, and runs the rest of its arguments as the command.
# A --merge <dest> <src>... call copies every data-* file from each source into
# the destination and writes an index.html there. Two switches exercise the
# failure paths: STUB_MERGE_FAIL=1 makes a merge exit 1 without writing anything,
# and STUB_NO_INDEX=1 suppresses every index.html.
#
# Cases 2-7 pin the behaviour the script must keep: a failing test fails the run,
# the exported root survives, the merge takes every directory, the exclusions
# file is validated. Each was shown failing against the pre-fix script (#725).

typeset REPO="${0:A:h:h:h}"
typeset REAL_COV="${REPO}/bin/coverage.zsh"
typeset REAL_EXCL="${REPO}/tests/ci-coverage-exclusions.txt"

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset -i TEST_NO=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }

# check <description> <condition> [detail]
# Numbers each check, evaluates the condition string, and reports PASS or FAIL.
check() {
    typeset desc="$1" cond="$2" detail="${3:-}"
    TEST_NO+=1
    test_start "${TEST_NO}: ${desc}"
    if eval "${cond}"; then
        test_pass "${desc}"
    else
        test_fail "${desc}" "${detail}"
    fi
}

typeset SCRATCH
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/coverage-honesty.XXXXXX") || { echo "mktemp failed"; exit 1; }
SCRATCH="${SCRATCH:A}"
trap 'rm -rf -- "${SCRATCH}"' EXIT

export HOME="${SCRATCH}/home"
mkdir -p "${HOME}"

# Stub kcov: see the header comment for its contract.
typeset STUBS="${SCRATCH}/stubs"
mkdir -p "${STUBS}"
cat > "${STUBS}/kcov" <<'EOF'
#!/usr/bin/env zsh
print -r -- "$*" >> "${STUB_LOG}"
if [[ "${1}" == "--merge" ]]; then
    if [[ "${STUB_MERGE_FAIL:-0}" == 1 ]]; then
        exit 1
    fi
    mkdir -p "${2}" || exit 1
    typeset src f
    for src in "${@[3,-1]}"; do
        for f in "${src}"/data-*(N); do
            cp -- "${f}" "${2}/" || exit 1
        done
    done
    if [[ "${STUB_NO_INDEX:-0}" != 1 ]]; then
        print -r -- '<html>covered">50.0<</html>' > "${2}/index.html"
    fi
    exit 0
fi
typeset out="" arg
typeset -a cmd
for arg in "$@"; do
    if [[ -z "${out}" ]]; then
        [[ "${arg}" == --* ]] && continue
        out="${arg}"
    else
        cmd+=("${arg}")
    fi
done
mkdir -p "${out}" || exit 1
print -r -- "${out:t}" > "${out}/data-${out:t}"
if [[ "${STUB_NO_INDEX:-0}" != 1 ]]; then
    print -r -- '<html>covered">50.0<</html>' > "${out}/index.html"
fi
"${cmd[@]}"
exit $?
EOF
chmod +x "${STUBS}/kcov"

# new_root <name> -> prints the fixture root, with the real coverage script in bin/
new_root() {
    typeset root="${SCRATCH}/$1"
    mkdir -p "${root}/bin" "${root}/tests/unit" "${root}/tests/integration"
    cp "${REAL_COV}" "${root}/bin/coverage.zsh"
    chmod +x "${root}/bin/coverage.zsh"
    ln -sfn "${REPO}/lib" "${root}/lib"
    print -r -- "${root}"
}

# make_test <file> <exit-status> [extra body line]
# A fake test: records its own name to $MARK_FILE, runs the optional body line,
# then exits with the given status.
make_test() {
    typeset file="$1" rc="$2" body="${3:-}"
    {
        print -r -- '#!/usr/bin/env zsh'
        print -r -- 'print -r -- "${0:t}" >> "${MARK_FILE}"'
        if [[ -n "${body}" ]]; then
            print -r -- "${body}"
        fi
        print -r -- "exit ${rc}"
    } > "${file}"
}

# run_coverage <root> <mode> [VAR=value ...] -> sets COV_OUT and COV_RC
run_coverage() {
    typeset root="$1" mode="$2"
    shift 2
    COV_OUT=$(cd "${root}" && env -u VDE_ROOT_DIR MARK_FILE="${root}/markers" STUB_LOG="${root}/stub.log" PATH="${STUBS}:${PATH}" HOME="${HOME}" "$@" timeout 120 ./bin/coverage.zsh "${mode}" </dev/null 2>&1)
    COV_RC=$?
}

# marked <root> <test name>: that fake test ran
marked() { [[ -f "$1/markers" ]] && grep -qxF -- "$2" "$1/markers"; }

# ran_any <root>: at least one fake test ran
ran_any() { [[ -s "$1/markers" ]]; }

#-------------------------------------------------------------------------------
# Case 1: all tests pass
typeset R1
R1=$(new_root case1)
make_test "${R1}/tests/unit/a.test.zsh" 0
make_test "${R1}/tests/unit/c.test.zsh" 0
make_test "${R1}/tests/integration/i.test.zsh" 0
run_coverage "${R1}" all
check "all passing: exit 0" "[[ \${COV_RC} == 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "all passing: a, c and i all ran" "marked '${R1}' a.test.zsh && marked '${R1}' c.test.zsh && marked '${R1}' i.test.zsh" "markers=$(cat "${R1}/markers" 2>/dev/null | tr '\n' ' ')"

#-------------------------------------------------------------------------------
# Case 2: one failing test is reported honestly and every test still runs
typeset R2
R2=$(new_root case2)
make_test "${R2}/tests/unit/a.test.zsh" 0
make_test "${R2}/tests/unit/b.test.zsh" 1 'print -r -- BOOM-OUTPUT'
make_test "${R2}/tests/unit/c.test.zsh" 0
make_test "${R2}/tests/integration/i.test.zsh" 0
run_coverage "${R2}" all
check "one failing test: exit status is non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "one failing test: c and i still ran" "marked '${R2}' c.test.zsh && marked '${R2}' i.test.zsh" "markers=$(cat "${R2}/markers" 2>/dev/null | tr '\n' ' ')"
check "one failing test: the failing test's output is shown" "[[ \"\${COV_OUT}\" == *BOOM-OUTPUT* ]]" "out=${COV_OUT}"
check "one failing test: the run names b.test.zsh" "[[ \"\${COV_OUT}\" == *b.test.zsh* ]]" "out=${COV_OUT}"

#-------------------------------------------------------------------------------
# Case 3: an exported, absolute VDE_ROOT_DIR is honoured even after cd /
typeset R3
R3=$(new_root case3)
typeset ROOT_BODY='cd / && print -r -- "ROOT=${VDE_ROOT_DIR}" >> "${MARK_FILE}" && [[ -f "${VDE_ROOT_DIR}/bin/coverage.zsh" ]] || exit 1'
make_test "${R3}/tests/unit/a.test.zsh" 0 "${ROOT_BODY}"
make_test "${R3}/tests/unit/c.test.zsh" 0 "${ROOT_BODY}"
make_test "${R3}/tests/integration/i.test.zsh" 0 "${ROOT_BODY}"
run_coverage "${R3}" all "VDE_ROOT_DIR=${R3}"
typeset ROOT_LINES BAD_ROOTS=""
ROOT_LINES=$(grep '^ROOT=' "${R3}/markers" 2>/dev/null)
if [[ -n "${ROOT_LINES}" ]]; then
    BAD_ROOTS=$(print -r -- "${ROOT_LINES}" | grep -v '^ROOT=/')
fi
check "exported VDE_ROOT_DIR: exit 0" "[[ \${COV_RC} == 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "exported VDE_ROOT_DIR: every test saw an absolute root" "[[ -n \"\${ROOT_LINES}\" && -z \"\${BAD_ROOTS}\" ]]" "roots=${ROOT_LINES} bad=${BAD_ROOTS}"

#-------------------------------------------------------------------------------
# Case 4: merge takes every coverage directory, and does not copy itself
typeset R4
R4=$(new_root case4)
make_test "${R4}/tests/unit/a.test.zsh" 0
make_test "${R4}/tests/unit/b.test.zsh" 0
make_test "${R4}/tests/unit/c.test.zsh" 0
run_coverage "${R4}" unit
typeset MERGE_LINES BOTH_LINE BAD_MERGE=""
MERGE_LINES=$(grep '^--merge' "${R4}/stub.log" 2>/dev/null)
BOTH_LINE=$(print -r -- "${MERGE_LINES}" | grep 'coverage/b.test.zsh' | grep 'coverage/c.test.zsh')
if [[ -n "${MERGE_LINES}" ]]; then
    # A call reads `--merge <dest> <source>...`: the destination may live under merged/, a SOURCE may not.
    typeset _ml; typeset -a _mw
    for _ml in "${(@f)MERGE_LINES}"; do
        _mw=( ${=_ml} )
        BAD_MERGE+=$(print -rl -- "${(@)_mw[3,-1]}" | grep -E '/merged(/|$)')
    done
fi
check "merge: one --merge call carries both the b and c coverage directories" "[[ -n \"\${BOTH_LINE}\" ]]" "merge calls: ${MERGE_LINES}"
check "merge: no merge SOURCE is the merged directory or inside it" "[[ -z \"\${BAD_MERGE}\" ]]" "bad args: ${BAD_MERGE}"
check "merge: merge output was not copied into itself" "[[ ! -e '${R4}/coverage/merged/merged' ]]" "merged/merged exists"
check "merge: merged/index.html exists after the run" "[[ -f '${R4}/coverage/merged/index.html' ]]" "merged/index.html missing"
check "merge: merged/ holds the data of a, b and c" "[[ -f '${R4}/coverage/merged/data-a.test.zsh' && -f '${R4}/coverage/merged/data-b.test.zsh' && -f '${R4}/coverage/merged/data-c.test.zsh' ]]" "merged/ contents: $(ls -A "${R4}/coverage/merged" 2>/dev/null | tr '\n' ' ')"

#-------------------------------------------------------------------------------
# Case 5: comprehensive mode fails loudly on a missing named file and runs all named files
typeset R5A R5B
R5A=$(new_root case5a)
run_coverage "${R5A}" comprehensive
check "comprehensive: missing named files make the run exit non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"

R5B=$(new_root case5b)
make_test "${R5B}/tests/unit/test_vde_parser_comprehensive.sh" 0
make_test "${R5B}/tests/unit/test_vde_commands_comprehensive.sh" 0
make_test "${R5B}/tests/integration/test_integration_comprehensive.sh" 0
run_coverage "${R5B}" comprehensive
check "comprehensive: all three named files exist and pass, so exit 0" "[[ \${COV_RC} == 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "comprehensive: all three named files ran" "marked '${R5B}' test_vde_parser_comprehensive.sh && marked '${R5B}' test_vde_commands_comprehensive.sh && marked '${R5B}' test_integration_comprehensive.sh" "markers=$(cat "${R5B}/markers" 2>/dev/null | tr '\n' ' ')"

#-------------------------------------------------------------------------------
# Case 6: the exclusions file
typeset R6A R6B R6C

R6A=$(new_root case6a)
make_test "${R6A}/tests/unit/a.test.zsh" 0
make_test "${R6A}/tests/integration/i.test.zsh" 0
print -r -- '# CI coverage exclusions' > "${R6A}/tests/ci-coverage-exclusions.txt"
print -r -- '' >> "${R6A}/tests/ci-coverage-exclusions.txt"
print -r -- 'integration/i.test.zsh needs Docker' >> "${R6A}/tests/ci-coverage-exclusions.txt"
run_coverage "${R6A}" all
check "exclusion with a reason: exit 0" "[[ \${COV_RC} == 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "exclusion with a reason: the excluded test does not run" "! marked '${R6A}' i.test.zsh" "markers=$(cat "${R6A}/markers" 2>/dev/null | tr '\n' ' ')"
check "exclusion with a reason: the reason is shown" "[[ \"\${COV_OUT}\" == *'needs Docker'* ]]" "out=${COV_OUT}"

R6B=$(new_root case6b)
make_test "${R6B}/tests/unit/a.test.zsh" 0
make_test "${R6B}/tests/integration/i.test.zsh" 0
print -r -- 'integration/i.test.zsh' > "${R6B}/tests/ci-coverage-exclusions.txt"
run_coverage "${R6B}" all
check "exclusion without a reason: exit non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "exclusion without a reason: no test ran" "! ran_any '${R6B}'" "markers=$(cat "${R6B}/markers" 2>/dev/null | tr '\n' ' ')"

R6C=$(new_root case6c)
make_test "${R6C}/tests/unit/a.test.zsh" 0
make_test "${R6C}/tests/integration/i.test.zsh" 0
print -r -- 'integration/ghost.test.zsh some reason' > "${R6C}/tests/ci-coverage-exclusions.txt"
run_coverage "${R6C}" all
check "exclusion naming a missing file: exit non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "exclusion naming a missing file: no test ran" "! ran_any '${R6C}'" "markers=$(cat "${R6C}/markers" 2>/dev/null | tr '\n' ' ')"

#-------------------------------------------------------------------------------
# Case 7: static checks against the real repository
typeset REAL_ENTRIES="" ENTRY_COUNT=0 ENTRY_NAMES="" BLANK_REASONS=0
typeset WANT_NAMES=$'integration/jupyterlab-spoke.test.zsh\nintegration/tech-stack-empirical.test.zsh\nunit/git-fixture-isolation.test.zsh'
if [[ -f "${REAL_EXCL}" ]]; then
    REAL_ENTRIES=$(grep -Ev '^[[:space:]]*(#|$)' "${REAL_EXCL}")
fi
ENTRY_COUNT=$(print -r -- "${REAL_ENTRIES}" | grep -c .)
ENTRY_NAMES=$(print -r -- "${REAL_ENTRIES}" | sed -E 's/[[:space:]].*$//' | sort)
typeset line n r
while IFS= read -r line; do
    read -r n r <<< "${line}"
    [[ -n "${r//[[:space:]]/}" ]] || BLANK_REASONS+=1
done <<< "${REAL_ENTRIES}"

check "static: tests/ci-coverage-exclusions.txt exists" "[[ -f '${REAL_EXCL}' ]]" "missing: ${REAL_EXCL}"
check "static: exactly three non-comment entries" "[[ \${ENTRY_COUNT} == 3 ]]" "count=${ENTRY_COUNT}"
check "static: the entries are the jupyterlab, tech-stack and git-fixture tests" "[[ \"\${ENTRY_NAMES}\" == \"\${WANT_NAMES}\" ]]" "names=${ENTRY_NAMES}"
check "static: every entry has a non-empty reason" "[[ \${BLANK_REASONS} == 0 ]]" "entries without a reason: ${BLANK_REASONS}"
check "static: all three named test files exist" "[[ -f '${REPO}/tests/integration/jupyterlab-spoke.test.zsh' && -f '${REPO}/tests/integration/tech-stack-empirical.test.zsh' && -f '${REPO}/tests/unit/git-fixture-isolation.test.zsh' ]]" "a named test file is missing"

#-------------------------------------------------------------------------------
# Case 8: a failed merge is reported honestly
typeset R8
R8=$(new_root case8)
make_test "${R8}/tests/unit/a.test.zsh" 0
make_test "${R8}/tests/unit/b.test.zsh" 0
make_test "${R8}/tests/unit/c.test.zsh" 0
run_coverage "${R8}" unit "STUB_MERGE_FAIL=1"
check "merge failure: exit status is non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"
check "merge failure: the output mentions merge" "[[ \"\${COV_OUT}\" == *merge* ]]" "out=${COV_OUT}"

#-------------------------------------------------------------------------------
# Case 9: a missing report is reported honestly (the merged report has no index.html)
typeset R9
R9=$(new_root case9)
make_test "${R9}/tests/unit/a.test.zsh" 0
make_test "${R9}/tests/unit/b.test.zsh" 0
make_test "${R9}/tests/unit/c.test.zsh" 0
run_coverage "${R9}" unit "STUB_NO_INDEX=1"
check "missing report: exit status is non-zero" "[[ \${COV_RC} != 0 ]]" "rc=${COV_RC} out=${COV_OUT}"

#-------------------------------------------------------------------------------
echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
