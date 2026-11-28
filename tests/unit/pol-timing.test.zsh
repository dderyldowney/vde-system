#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: per-scenario Proof of Life timing (Signet #774, step 1b).
#
# lib/vde-junit-timing provides vde_junit_timing_report DIR [TOP]. It reads every *.xml junit file in DIR (hand-written
# fixtures here; behave is never run) and prints the PROOF OF LIFE TIMING table, slowest scenario first.
#
# R cases check the report. G cases check the wiring in githooks/gate-tree.zsh and the shape of the library file.
# Until lib/vde-junit-timing exists, every R case FAILS (RED): the library is not sourced, so the function is undefined.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

typeset ROOT="${0:A:h:h:h}"
typeset LIB_SRC="${ROOT}/lib/vde-junit-timing"
typeset GATE_SRC="${ROOT}/githooks/gate-tree.zsh"
typeset TESTS_PASSED=0 TESTS_FAILED=0
typeset -g REP_OUT='' REP_RC=127 REP_LC=''
typeset -ga REP_LINES=()
typeset -a SNAP_BEFORE SNAP_AFTER
typeset -g out9a='' out9b=''
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { print -P "${YELLOW}[TEST]${RESET} $1"; }
# not ((x++)): that returns 1 when x was 0 and would trip the `&& pass || fail` pattern
test_pass()  { print -P "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }
test_fail()  { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset SCRATCH
SCRATCH="$(vde_test_env_dir)" && [[ -n "${SCRATCH}" ]] || exit 1
SCRATCH="$(mktemp -d "${SCRATCH}/pol-timing.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT

# ---------------------------------------------------------------------------
# Library: a missing file is recorded as a failure, and every R case then fails through the undefined function.
# ---------------------------------------------------------------------------

if [[ -f "${LIB_SRC}" ]]; then
    source "${LIB_SRC}" || test_fail "lib/vde-junit-timing sources" "source returned an error"
else
    test_fail "lib/vde-junit-timing exists" "missing: ${LIB_SRC}; every R case below fails"
fi

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

# tc NAME TIME STATUS: one behave-style testcase element (two lines)
tc() {
    print -r -- "<testcase classname=\"pol.features\" name=\"$1\" status=\"$3\" time=\"$2\">" "</testcase>"
}

# xml_write FILE ELEMENT...: a junit file holding the given elements
xml_write() {
    local f="$1"
    shift
    print -r -- '<?xml version="1.0" encoding="utf-8"?>' '<testsuite name="pol">' "$@" '</testsuite>' > "${f}"
}

# report_capture DIR [TOP]: runs the report in a subshell and sets REP_OUT, REP_RC and REP_LINES. REP_LC, when set,
# is the LC_ALL for that call only. A missing function leaves REP_RC at 127 and the output empty.
report_capture() {
    REP_OUT='' REP_RC=127
    if (( ! $+functions[vde_junit_timing_report] )); then
        REP_LINES=()
        return 0
    fi
    if [[ -n "${REP_LC}" ]]; then
        REP_OUT="$( export LC_ALL="${REP_LC}"; vde_junit_timing_report "$@" 2>&1 )"
    else
        REP_OUT="$( vde_junit_timing_report "$@" 2>&1 )"
    fi
    REP_RC=$?
    REP_LINES=("${(@f)REP_OUT}")
}

# line_of PATTERN: 1-based index of the first REP_LINES line containing PATTERN (a literal), 0 if none
line_of() {
    typeset -i i
    for (( i = 1; i <= ${#REP_LINES}; i++ )); do
        [[ "${REP_LINES[i]}" == *"$1"* ]] && { print -r -- "${i}"; return 0; }
    done
    print -r -- 0
}

# in_range VALUE LO HI: exit 0 when LO <= VALUE <= HI (float arithmetic)
in_range() {
    (( $1 >= $2 && $1 <= $3 ))
}

# line_idx ARRAY_NAME LITERAL: 1-based index of the exact element LITERAL in the named array, 0 if none
line_idx() {
    typeset -a src
    src=("${(P@)1}")
    print -r -- "${src[(Ie)${2}]}"
}

# gate_idx PATTERN [FROM]: 1-based index of the first GATE_TXT line at or after FROM matching the glob PATTERN, 0 if none
typeset -a GATE_LINES=()
typeset GATE_TXT=''
gate_idx() {
    typeset -i i from=${2:-1}
    for (( i = from; i <= ${#GATE_LINES}; i++ )); do
        [[ "${GATE_LINES[i]}" == ${~1} ]] && { print -r -- "${i}"; return 0; }
    done
    print -r -- 0
}

if [[ -f "${GATE_SRC}" ]]; then
    GATE_TXT="$(<"${GATE_SRC}")"
    GATE_LINES=("${(@f)GATE_TXT}")
fi

typeset LIBW_TXT=''
typeset -a LIBW_LINES=()
if [[ -f "${LIB_SRC}" ]]; then
    LIBW_TXT="$(<"${LIB_SRC}")"
    LIBW_LINES=("${(@f)LIBW_TXT}")
fi

# ---------------------------------------------------------------------------
# Case R1: scenarios are listed slowest first
# ---------------------------------------------------------------------------

typeset d1="${SCRATCH}/r1"
mkdir -p "${d1}" || exit 1
xml_write "${d1}/pol.xml" "$(tc Alpha 10.5 passed)" "$(tc Beta 120.25 failed)" "$(tc Gamma 0.5 skipped)"
report_capture "${d1}"

test_start "R1 the report lists the scenarios slowest first (Beta 120.25, Alpha 10.5, Gamma 0.5)"
typeset -i b1 a1 g1
b1="$(line_of Beta)"; a1="$(line_of Alpha)"; g1="$(line_of Gamma)"
if (( b1 > 0 && a1 > b1 && g1 > a1 )); then
    test_pass "R1 row order is Beta, Alpha, Gamma"
else
    test_fail "R1 row order Beta, Alpha, Gamma" "rc=${REP_RC} lines: Beta=${b1} Alpha=${a1} Gamma=${g1} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R2: the header counts every scenario and the total sums ALL of them, not only the shown rows
# ---------------------------------------------------------------------------

typeset d2="${SCRATCH}/r2"
mkdir -p "${d2}" || exit 1
xml_write "${d2}/pol.xml" "$(tc S1 100.0 passed)" "$(tc S2 50.0 passed)" "$(tc S3 25.0 passed)" \
    "$(tc S4 10.0 passed)" "$(tc S5 5.0 passed)" "$(tc S6 2.0 failed)" "$(tc S7 1.0 skipped)"
report_capture "${d2}" 2

test_start "R2 the header counts 7 scenarios and totals all of them (193.0s), though only 2 are shown"
if [[ "${REP_OUT}" =~ 'PROOF OF LIFE TIMING: 7 scenarios, ([0-9]+\.[0-9])s in total, slowest 2 shown' ]] \
    && in_range "${match[1]}" 192.9 193.1; then
    test_pass "R2 header: 7 scenarios, ${match[1]}s in total, slowest 2 shown"
else
    test_fail "R2 header '7 scenarios, <total ~193.0>s in total, slowest 2 shown'" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R3: TOP limits the rows; the header says how many are shown
# ---------------------------------------------------------------------------

test_start "R3 TOP=2 shows S1 and S2 only; TOP=50 shows all 7 and the header says so"
report_capture "${d2}" 2
typeset -i s1_3 s2_3 s3_3
s1_3="$(line_of S1)"; s2_3="$(line_of S2)"; s3_3="$(line_of S3)"
typeset r3a=0 r3b=0
(( s1_3 > 0 && s2_3 > s1_3 && s3_3 == 0 )) && r3a=1
report_capture "${d2}" 50
[[ "${REP_OUT}" == *'slowest 7 shown'* ]] && r3b=1
if (( r3a && r3b )); then
    test_pass "R3 TOP=2 limits the rows, TOP=50 header reads slowest 7 shown"
else
    test_fail "R3 TOP=2 shows 2 rows and TOP=50 says slowest 7 shown" "S1=${s1_3} S2=${s2_3} S3=${s3_3} r3b=${r3b} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R4: XML-escaped names are unescaped
# ---------------------------------------------------------------------------

typeset d4="${SCRATCH}/r4"
mkdir -p "${d4}" || exit 1
xml_write "${d4}/pol.xml" '<testcase classname="pol.features" name="Tom &amp; Jerry &quot;quoted&quot; &lt;x&gt; &apos;y&apos;" status="passed" time="7.0">' '</testcase>'
report_capture "${d4}"
typeset want4="Tom & Jerry \"quoted\" <x> 'y'"

test_start "R4 xml-escaped names are shown unescaped (& \" < > ')"
if [[ "${REP_OUT}" == *"${want4}"* && "${REP_OUT}" != *'&amp;'* ]]; then
    test_pass "R4 name unescaped: ${want4}"
else
    test_fail "R4 name shows as: ${want4}" "out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R5: a testcase with an empty or non-numeric time is skipped and not counted
# ---------------------------------------------------------------------------

typeset d5="${SCRATCH}/r5"
mkdir -p "${d5}" || exit 1
xml_write "${d5}/pol.xml" "$(tc Valid1 4.0 passed)" "$(tc BadEmpty '' passed)" "$(tc BadWord abc passed)" "$(tc Valid2 6.0 passed)"
report_capture "${d5}"

test_start "R5 testcases with time=\"\" or time=\"abc\" are skipped (2 scenarios, 10.0s)"
if [[ "${REP_OUT}" =~ '2 scenarios, ([0-9]+\.[0-9])s in total' ]] && in_range "${match[1]}" 9.9 10.1 \
    && [[ "${REP_OUT}" != *BadEmpty* && "${REP_OUT}" != *BadWord* ]]; then
    test_pass "R5 invalid times skipped: 2 scenarios, ${match[1]}s"
else
    test_fail "R5 2 scenarios, 10.0s, no BadEmpty or BadWord row" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R6: an empty directory and a nonexistent directory print the no-timings line and return 0
# ---------------------------------------------------------------------------

typeset d6a="${SCRATCH}/r6-empty" d6b="${SCRATCH}/r6-missing"
mkdir -p "${d6a}" || exit 1

test_start "R6a an empty directory prints the no-timings line and returns 0"
report_capture "${d6a}"
if [[ "${REP_OUT}" == *'PROOF OF LIFE TIMING: no scenario timings found in'* && "${REP_RC}" == 0 ]]; then
    test_pass "R6a empty directory: no-timings line, rc=0"
else
    test_fail "R6a no-timings line and rc=0" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

test_start "R6b a nonexistent directory prints the no-timings line and returns 0"
report_capture "${d6b}"
if [[ "${REP_OUT}" == *'PROOF OF LIFE TIMING: no scenario timings found in'* && "${REP_RC}" == 0 ]]; then
    test_pass "R6b missing directory: no-timings line, rc=0"
else
    test_fail "R6b no-timings line and rc=0" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R7: a decimal-comma locale still prints dots and no commas
# ---------------------------------------------------------------------------

typeset LOC_PROBE=''
LOC_PROBE="$(LC_ALL=en_DK.utf8 zsh -c 'printf "%.1f" 1.5' 2>/dev/null)"
if [[ "${LOC_PROBE}" != '1,5' ]]; then
    print -r -- "[SKIP] R7: no decimal-comma locale (en_DK.utf8) on this host; install the locales package and run locale-gen"
else
    typeset d7="${SCRATCH}/r7"
    mkdir -p "${d7}" || exit 1
    xml_write "${d7}/pol.xml" "$(tc Alpha 120.25 passed)" "$(tc Beta 80.0 failed)"
    REP_LC=en_DK.utf8
    report_capture "${d7}"
    REP_LC=''

    test_start "R7 under LC_ALL=en_DK.utf8 the table keeps its dots and has no comma"
    if [[ ! "${REP_OUT}" =~ '[0-9],[0-9]' && "${REP_OUT}" =~ '120\.[0-9]' && "${REP_OUT}" == *'80.0'* ]]; then
        test_pass "R7 dotted seconds, no decimal comma under en_DK.utf8"
    else
        test_fail "R7 dotted seconds (120.x, 80.0) and no comma under en_DK.utf8" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
    fi
fi

# ---------------------------------------------------------------------------
# Case R8: every *.xml file in DIR is read; other files are not
# ---------------------------------------------------------------------------

typeset d8="${SCRATCH}/r8"
mkdir -p "${d8}" || exit 1
xml_write "${d8}/a.xml" "$(tc Alpha 3.0 passed)"
xml_write "${d8}/b.xml" "$(tc Beta 4.0 passed)"
xml_write "${d8}/notes.txt" "$(tc Ignored 9.0 passed)"
report_capture "${d8}"

test_start "R8 both *.xml files are read (2 scenarios, 7.0s) and notes.txt is not"
if [[ "${REP_OUT}" =~ '2 scenarios, ([0-9]+\.[0-9])s in total' ]] && in_range "${match[1]}" 6.9 7.1 \
    && [[ "${REP_OUT}" == *Alpha* && "${REP_OUT}" == *Beta* && "${REP_OUT}" != *Ignored* ]]; then
    test_pass "R8 Alpha and Beta read, notes.txt ignored"
else
    test_fail "R8 2 scenarios, 7.0s, Alpha and Beta present, Ignored absent" "rc=${REP_RC} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R9: the function is defined, repeated calls print the same output, and it leaks no parameters
# ---------------------------------------------------------------------------

typeset d9="${SCRATCH}/r9"
mkdir -p "${d9}" || exit 1
xml_write "${d9}/pol.xml" "$(tc Alpha 3.0 passed)" "$(tc Beta 4.0 failed)"

test_start "R9 the function is defined, two calls print identical output, and no parameter is leaked"
# The library runs in THIS shell (a redirect, not a command substitution), so a parameter it leaks stays visible here.
typeset d9out1="${SCRATCH}/r9a.out" d9out2="${SCRATCH}/r9b.out"
typeset r9_defined=0 r9_same=0 r9_nonempty=0 r9_noleak=0
if (( $+functions[vde_junit_timing_report] )); then
    r9_defined=1
    SNAP_BEFORE=("${(@ko)parameters}")
    vde_junit_timing_report "${d9}" > "${d9out1}"
    vde_junit_timing_report "${d9}" > "${d9out2}"
    SNAP_AFTER=("${(@ko)parameters}")
    cmp -s "${d9out1}" "${d9out2}" && r9_same=1
    [[ -s "${d9out1}" ]] && r9_nonempty=1
    [[ "${(j:,:)SNAP_BEFORE}" == "${(j:,:)SNAP_AFTER}" ]] && r9_noleak=1
fi
if (( r9_defined && r9_same && r9_nonempty && r9_noleak )); then
    test_pass "R9 defined, repeatable, no new parameters"
else
    typeset r9_first="$(<"${d9out1}" 2>/dev/null)"
    test_fail "R9 function defined, identical output on repeat, no leaked parameters" "defined=${r9_defined} same=${r9_same} nonempty=${r9_nonempty} noleak=${r9_noleak} first: ${r9_first[1,200]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R10: zero padding: a 3 ms scenario sorts after a 1200.5 s scenario
# ---------------------------------------------------------------------------

typeset d10="${SCRATCH}/r10"
mkdir -p "${d10}" || exit 1
xml_write "${d10}/pol.xml" "$(tc Tiny 0.003 passed)" "$(tc Huge 1200.5 passed)"
report_capture "${d10}"

test_start "R10 Huge (1200.5s) sorts before Tiny (0.003s) and both print with a dot"
typeset -i h10 t10
h10="$(line_of Huge)"; t10="$(line_of Tiny)"
if (( h10 > 0 && t10 > h10 )) && [[ "${REP_OUT}" == *'1200.5'* ]] && [[ "$(print -r -- "${REP_LINES[t10]:-}")" == *'0.0'* ]]; then
    test_pass "R10 Huge before Tiny, 1200.5 and 0.0 printed"
else
    test_fail "R10 Huge (1200.5) row before Tiny (0.0) row" "Huge=${h10} Tiny=${t10} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi


# ---------------------------------------------------------------------------
# Case R11: behave writes small times in exponent notation (4.9e-05, 1.5e+01); they must count, not vanish
# ---------------------------------------------------------------------------

typeset d11="${SCRATCH}/r11"
mkdir -p "${d11}" || exit 1
xml_write "${d11}/pol.xml" "$(tc Quick 4.9e-05 passed)" "$(tc Mid 1.5e+01 passed)" "$(tc Plain 2.5 passed)"
report_capture "${d11}"

test_start "R11 exponent-notation times are counted (3 scenarios) and 1.5e+01 sorts first as 15.0"
typeset -i m11 q11
m11="$(line_of Mid)"; q11="$(line_of Quick)"
if [[ "${REP_OUT}" == *'3 scenarios'* ]] && [[ "${REP_OUT}" == *'17.5s in total'* ]] && (( m11 > 0 && q11 > m11 )) \
    && [[ "$(print -r -- "${REP_LINES[m11]:-}")" == *'15.0'* ]]; then
    test_pass "R11 3 scenarios, 17.5s in total, Mid (15.0) before Quick"
else
    test_fail "R11 exponent times counted, 17.5s total, Mid before Quick" "Mid=${m11} Quick=${q11} out: ${REP_OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case R12: the real thing: a tiny feature run through behave --junit, reported by the library.
# Hand-written fixtures can drift from what behave really writes; this one cannot.
# ---------------------------------------------------------------------------

test_start "R12 a real behave --junit run is read by the library: 2 scenarios, names unescaped"
if ! python3 -c 'import behave' >/dev/null 2>&1; then
    print -r -- "[SKIP] R12 python3 with behave is unavailable: the real-format check did not run"
else
    typeset d12="${SCRATCH}/r12"
    mkdir -p "${d12}/features/steps" "${d12}/out" || exit 1
    print -l -- 'Feature: Tiny timing check' '  Scenario: first quick one' '    Given a step' '  Scenario: second with "quotes" & ampersand' '    Given a step' > "${d12}/features/t.feature"
    print -l -- 'from behave import given' '@given("a step")' 'def step(ctx):' '    pass' > "${d12}/features/steps/s.py"
    ( cd "${d12}" && env -i HOME="${CHK_HOME:-${SCRATCH}}" PATH="${PATH}" python3 -m behave features --quiet --no-summary --junit --junit-directory out >/dev/null 2>&1 )
    report_capture "${d12}/out"
    if [[ "${REP_OUT}" == *'2 scenarios'* && "${REP_OUT}" == *'first quick one'* && "${REP_OUT}" == *'second with "quotes" & ampersand'* ]]; then
        test_pass "R12 real behave output: 2 scenarios read, names unescaped"
    else
        test_fail "R12 real behave --junit output read by the library" "out: ${REP_OUT[1,300]//$'\n'/ | }"
    fi
fi
# ---------------------------------------------------------------------------
# Wiring (static) checks on githooks/gate-tree.zsh and the library file
# ---------------------------------------------------------------------------

test_start "G1 githooks/gate-tree.zsh sources lib/vde-junit-timing"
typeset -i g1_src
g1_src="$(gate_idx '*source*vde-junit-timing*')"
if (( g1_src > 0 )); then
    test_pass "G1 gate sources the library (line ${g1_src})"
else
    test_fail "G1 gate-tree.zsh has a source line naming lib/vde-junit-timing" "gate file: ${GATE_SRC}"
fi

test_start "G2 the behave call passes --junit and --junit-directory"
typeset -i g2_b
g2_b="$(gate_idx '*python3 -m behave*')"
if (( g2_b > 0 )) && [[ "${GATE_LINES[g2_b]}" == *' --junit '* && "${GATE_LINES[g2_b]}" == *' --junit-directory '* ]]; then
    test_pass "G2 behave line carries --junit and --junit-directory (line ${g2_b})"
else
    test_fail "G2 the behave line carries --junit and --junit-directory" "behave line: ${g2_b}"
fi

test_start "G3 the timing report is called after behave, at the same indentation (not inside its if body)"
typeset -i g3_r
g3_r="$(gate_idx '*vde_junit_timing_report*')"
if (( g2_b > 0 && g3_r > g2_b )); then
    typeset lead_b="${GATE_LINES[g2_b]%%[^[:space:]]*}" lead_r="${GATE_LINES[g3_r]%%[^[:space:]]*}"
    if [[ "${lead_b}" == "${lead_r}" ]]; then
        test_pass "G3 report at line ${g3_r}, after behave line ${g2_b}, same indentation"
    else
        test_fail "G3 report at the same indentation as the behave call" "behave indent ${#lead_b}, report indent ${#lead_r}"
    fi
else
    test_fail "G3 vde_junit_timing_report called after the behave call" "behave=${g2_b} report=${g3_r}"
fi

test_start "G4 the junit directory is removed after the report"
typeset -i g4_rm
g4_rm="$(gate_idx '*rm -rf*junit*' $(( g3_r > 0 ? g3_r : 1 )))"
if (( g3_r > 0 && g4_rm > g3_r )); then
    test_pass "G4 junit directory removed at line ${g4_rm}"
else
    test_fail "G4 an rm -rf of the junit directory after the report call" "report=${g3_r} rm=${g4_rm}"
fi

test_start "G5 lib/vde-junit-timing has the @forge tag on line 2 and the shibboleth within 20 lines"
typeset -i g5_shib
g5_shib="$(line_idx LIBW_LINES 'typeset _ZSH_PURE=${(%):-%x}')"
if [[ "${LIBW_LINES[2]:-}" == '# @forge (Governance Sentinel)' ]] && (( g5_shib > 0 && g5_shib <= 20 )); then
    test_pass "G5 @forge on line 2, shibboleth at line ${g5_shib}"
else
    test_fail "G5 @forge tag on line 2 and shibboleth line within 20" "line2: ${LIBW_LINES[2]:-none} shibboleth line: ${g5_shib}"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
