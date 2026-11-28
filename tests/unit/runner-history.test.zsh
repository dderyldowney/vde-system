#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: the run history of the Sovereign runner (Signet #779, step B).
#
# After each suite is reported, the runner appends ONE JSON line to the run history:
#   {"v":1,"run":"<ts>-<pid>-<nonce>","ts":"<UTC>","tree":"<sha>","dirty":bool,"suite":"..","seconds":<n.n>,
#    "containers":"<str>","result":"pass|fail|flaky","flaky":bool}
# The file is VDE_TEST_HISTORY_FILE (a path, or the word off for none). With it unset, the history is kept only when
# the runner is the one of the git repository it sits in (the git common directory), so a fixture copy writes nothing.
#
# The runner runs in a stub fixture (stub audit, stub integration suite, stub docker on PATH, no containers, no network),
# the same harness as tests/unit/runner-flaky.test.zsh. Results are read back with zsh pattern matching only (no jq,
# no python): each line is checked against one strict regex for the exact line shape, and fields are read by key.
#
# Cases:
#   H1  serial: one line per suite in report order (sovereign-audit, the unit suites, the integration suite,
#       BDD-Metadata); results pass/fail/flaky; flaky true only for the flaky suite; v 1, one run id, the tree of the
#       fixture, seconds with one decimal; the flaky suite has ONE line and no "[rerun]" line.
#   H2  pool (VDE_TEST_JOBS=3): the same suite lines in any order; containers "n/a" for the pool suites.
#   H3  appends: two runs into one file give 2x lines and two run ids; the earlier lines are unchanged.
#   H4  survives a killed run: a suite SIGKILLs the runner after an earlier suite finished; that suite's line is in the file.
#   H5  a failing sovereign audit still records: one sovereign-audit line, result fail, no suite lines, exit 1.
#   H6  VDE_TEST_HISTORY_FILE=off writes no file (the fixture root gains no entry at all, not even ./off); unset in a
#       fixture that is not a repository top writes no *.jsonl anywhere and leaves the real repository's history untouched;
#       exit codes unchanged.
#   H6b unset with the runner in a subdirectory of a real git repository (the repository top is not the runner's root):
#       no vde-test-history.jsonl anywhere in that repository's .git, rc 0. Fails if the top-level guard is removed.
#   H7  an unwritable history path (its parent is a regular file) prints the WARNING once; the run still passes (rc 0).
#   H8  decimal-comma locale LC_ALL=en_DK.utf8 (skips loudly when the locale is missing): seconds keep a dot, lines valid.
#   H9  default location in a real git repository: <repo>/.git/vde-test-history.jsonl, tree = HEAD^{tree}; dirty false on the
#       clean tree; dirty true after a tracked-file edit and after an untracked non-ignored file; dirty false again when the
#       only untracked file is one .gitignore ignores.
#   H10 every line matches the exact line shape; a malformed copy of a line does not (negative controls).
#   H11 a suite whose file name holds a tab, and one whose name holds a newline (where the filesystem allows it): ONE
#       physical line per suite, the control characters written as \u0009 / \u000a, no raw control character in the file;
#       a raw tab in a suite name does not match the shape (negative control).
#   H12 serial fail-then-pass suite whose first run creates 2 containers and whose rerun creates 3 (a docker stub
#       answers the events query per --since/--until window): the history line's containers is the sum, "5", one line.
#   H13 two runs back to back: each run's lines carry one well-formed run id, and the two runs' whole ids differ.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_TEST_JOBS VDE_TEST_TIMING_FILE VDE_DOCKER_EVENTS_TIMEOUT VDE_POL_STAMP_TTL VDE_TEST_HISTORY_FILE VDE_FLAKE_RERUN

typeset ROOT="${0:A:h:h:h}"
typeset RUNNER_SRC="${ROOT}/tests/run-sovereign-tests.zsh"
typeset LIBENV_SRC="${ROOT}/lib/vde-test-env"
typeset REAL_HIST="${ROOT}/.git/vde-test-history.jsonl"
typeset -g OUT='' RC=0 FWHY='' RUNS=0 JV='' CNT=0 LCNT=0
typeset -ga HL=()
typeset TESTS_PASSED=0 TESTS_FAILED=0
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
SCRATCH="$(mktemp -d "${SCRATCH}/runner-history.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT

# ---------------------------------------------------------------------------
# Harness (as runner-flaky.test.zsh)
# ---------------------------------------------------------------------------

new_fixture() {  # new_fixture NAME -> SCRATCH/NAME: the REAL runner and lib, a stub audit, a stub integration suite, a stub docker; no unit suites yet
    local f="${SCRATCH}/$1"
    mkdir -p "${f}/tests/unit" "${f}/tests/integration" "${f}/tests/features/core-infrastructure" \
        "${f}/bin" "${f}/lib" "${f}/stubs" "${f}/callerhome" "${f}/state" "${f}/tmproot" || return 1
    cp "${RUNNER_SRC}" "${f}/tests/run-sovereign-tests.zsh" || return 1
    cp "${LIBENV_SRC}" "${f}/lib/vde-test-env" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/bin/vde-enforce-uap.zsh" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/tests/integration/vm-lifecycle-integration.test.zsh" || return 1
    print -l -- '@forge' 'Feature: stub' > "${f}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/stubs/docker" || return 1
    print -l -- '# Serial unit suites (fixture): header only' > "${f}/tests/serial-unit-suites.txt" || return 1
    chmod +x "${f}/bin/vde-enforce-uap.zsh" "${f}/tests/integration/vm-lifecycle-integration.test.zsh" \
        "${f}/stubs/docker" || return 1
}

write_suite() {  # write_suite FILE: the suite body arrives on stdin; the file is made executable
    cat > "$1" && chmod +x "$1"
}

count_suite() {  # count_suite FILE FIRST LATER: a stub suite that counts its runs in RP_STATE/run-count.<suite>, exits FIRST on its first run and LATER after
    {
        print -r -- '#!/usr/bin/env zsh'
        print -r -- "typeset -i first_rc=$2 later_rc=$3"
        cat <<'STUB'
# runner-history fixture: counts its runs in RP_STATE, exits first_rc on the first run and later_rc after it
typeset f="${RP_STATE}/run-count.${0:t}" n=0
[[ -f "${f}" ]] && n="$(<"${f}")"
n=$(( n + 1 ))
print -r -- "${n}" > "${f}"
print -r -- "HISTORY-STUB ${0:t} run ${n}"
(( n == 1 )) && exit ${first_rc}
exit ${later_rc}
STUB
    } > "$1" && chmod +x "$1"
}

run_par() {  # run_par FIXTURE [NAME=value ...] -> OUT (colour codes removed) and RC (the runner's exit status); clean environment
    setopt localoptions extendedglob
    local fix="$1" raw
    shift
    raw="$(cd "${fix}" && timeout 120 env -i HOME="${fix}/callerhome" PATH="${fix}/stubs:${PATH}" \
        TMPDIR="${fix}/tmproot" RP_STATE="${fix}/state" FIXTURE_CALLER_HOME="${fix}/callerhome" \
        "$@" zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RC=$?")"
    RC="${raw##*RC=}"
    OUT="${raw%RC=*}"
    OUT="${OUT//$'\e'\[[0-9\;]#m/}"
}

has_line() {  # has_line TEXT: status 0 when a line of OUT contains TEXT literally
    local line
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *"$1"* ]] && return 0
    done
    return 1
}

count_has() {  # count_has TEXT -> CNT: how many lines of OUT contain TEXT literally
    local line
    CNT=0
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *"$1"* ]] && CNT=$(( CNT + 1 ))
    done
}

# ---------------------------------------------------------------------------
# History readers: zsh pattern matching only (Mandate G: no jq, no python)
# ---------------------------------------------------------------------------

# The strict shape of one history line: every key, in order, with its value's form. Any other line is malformed.
typeset -r SHAPE_RE='^\{"v":1,"run":"[0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]{5}","ts":"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z","tree":"([0-9a-f]{40}|unknown)","dirty":(true|false),"suite":"([^"\\[:cntrl:]]|\\["\\]|\\u[0-9a-f]{4})+","seconds":[0-9]+\.[0-9],"containers":"[^"]+","result":"(pass|fail|flaky)","flaky":(true|false)\}$'
typeset -r SEC_RE='^[0-9]+\.[0-9]$'

hist_lines() {  # hist_lines FILE -> HL: the non-empty lines of FILE (none when it is missing)
    HL=()
    [[ -f "$1" ]] || return 0
    HL=( "${(@f)$(<"$1")}" )
    HL=( ${HL:#} )
}

line_count() {  # line_count FILE -> LCNT: the number of lines in FILE (0 when it is missing)
    hist_lines "$1"
    LCNT=${#HL}
}

jfield() {  # jfield LINE KEY -> JV: the value of KEY in one history line (a string without its quotes, or a bare token)
    local pat="\"$2\":" rest
    rest="${1#*"${pat}"}"
    if [[ "${rest}" == \"* ]]; then
        rest="${rest#\"}"
        JV="${rest%%\"*}"
    else
        JV="${rest%%,*}"
        JV="${JV%%\}*}"
    fi
}

# The expectations of mixed_fixture's run, set per case: the report order (EXP_SEQ), and each suite's result (EXP_RES).
typeset -ga EXP_SEQ=()
typeset -gA EXP_RES=()

# hist_check FILE TREEDIR ORDER -> FWHY: every line has the exact shape, the expected suite (ORDER serial: in EXP_SEQ order;
# set: any order), its result from EXP_RES, flaky true only for a flaky result, one run id, v 1, the HEAD^{tree} of TREEDIR,
# and seconds with one decimal. FWHY is empty when all hold.
hist_check() {
    local file="$1" tdir="$2" order="$3" want_tree run0='' line s r fl t run sec
    local -i i=0 n
    local -a seen=()
    FWHY=''
    # A fixture that is not a repository records the runner's own "unknown"; a repository records HEAD^{tree}.
    want_tree="$(cd "${tdir}" && git rev-parse 'HEAD^{tree}' 2>/dev/null)" || want_tree=unknown
    hist_lines "${file}"
    n=${#HL}
    (( n == ${#EXP_SEQ} )) || FWHY+=" lines=${n}(want ${#EXP_SEQ})"
    for line in "${HL[@]}"; do
        i+=1
        if ! [[ "${line}" =~ ${SHAPE_RE} ]]; then
            FWHY+=" line ${i} has the wrong shape"
            continue
        fi
        jfield "${line}" suite;  s="${JV}"
        jfield "${line}" result; r="${JV}"
        jfield "${line}" flaky;  fl="${JV}"
        jfield "${line}" tree;   t="${JV}"
        jfield "${line}" run;    run="${JV}"
        jfield "${line}" seconds; sec="${JV}"
        jfield "${line}" v;      [[ "${JV}" == 1 ]] || FWHY+=" line ${i} v=${JV}"
        seen+=( "${s}" )
        if [[ "${order}" == serial ]]; then
            [[ "${s}" == "${EXP_SEQ[i]:-}" ]] || FWHY+=" line ${i} suite=${s}(want ${EXP_SEQ[i]:-none})"
        fi
        [[ "${r}" == "${EXP_RES[${s}]:-none}" ]] || FWHY+=" ${s} result=${r}(want ${EXP_RES[${s}]:-none})"
        if [[ "${r}" == flaky ]]; then
            [[ "${fl}" == true ]] || FWHY+=" ${s} flaky=${fl}(want true)"
        else
            [[ "${fl}" == false ]] || FWHY+=" ${s} flaky=${fl}(want false)"
        fi
        [[ "${t}" == "${want_tree}" ]] || FWHY+=" ${s} tree=${t}"
        (( i == 1 )) && run0="${run}"
        [[ "${run}" == "${run0}" ]] || FWHY+=" ${s} run=${run}(want ${run0})"
        [[ "${sec}" =~ ${SEC_RE} ]] || FWHY+=" ${s} seconds=${sec}"
    done
    if [[ "${order}" == set ]]; then
        # sorted copies first: a nested ${(j)${(o)x}} does not sort, which made this comparison order-sensitive
        local -a sorted_seen=( ${(o)seen} ) sorted_exp=( ${(o)EXP_SEQ} )
        [[ "${sorted_seen[*]}" == "${sorted_exp[*]}" ]] || FWHY+=" suites=[${(j:,:)seen}]"
    fi
    FWHY="${FWHY# }"
}

# mixed_fixture NAME: a fixture with a passing (a-pass), a failing (b-fail) and a fail-then-pass (c-flaky) unit suite.
# Its standard run: report order sovereign-audit, a-pass, b-fail, c-flaky, the integration suite, BDD-Metadata; RC 1.
mixed_fixture() {
    local d="${SCRATCH}/$1"
    new_fixture "$1" || return 1
    count_suite "${d}/tests/unit/a-pass.test.zsh" 0 0 || return 1
    count_suite "${d}/tests/unit/b-fail.test.zsh" 3 3 || return 1
    count_suite "${d}/tests/unit/c-flaky.test.zsh" 7 0 || return 1
}

set_mixed_expect() {  # the standard expectations of mixed_fixture
    EXP_SEQ=( sovereign-audit a-pass.test.zsh b-fail.test.zsh c-flaky.test.zsh vm-lifecycle-integration.test.zsh BDD-Metadata )
    EXP_RES=( sovereign-audit pass a-pass.test.zsh pass b-fail.test.zsh fail c-flaky.test.zsh flaky \
        vm-lifecycle-integration.test.zsh pass BDD-Metadata pass )
}

# ---------------------------------------------------------------------------
# H1: serial, one line per suite in report order, with the results, flaky flags, tree, run id and seconds
# ---------------------------------------------------------------------------

test_start "H1 serial: one line per suite in report order (audit, a-pass, b-fail, c-flaky, integration, BDD-Metadata); results, flaky flags, one run id, tree, seconds; the flaky suite has one line"
mixed_fixture h1s || exit 1
typeset FIX1="${SCRATCH}/h1s" HIST1
HIST1="${FIX1}/hist.jsonl"
set_mixed_expect
run_par "${FIX1}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST1}"
typeset WHY1=''
hist_check "${HIST1}" "${FIX1}" serial
[[ -n "${FWHY}" ]] && WHY1+=" ${FWHY}"
[[ "$(<"${HIST1}")" == *'[rerun]'* ]] && WHY1+=" a [rerun] line is in the file"
[[ "${RC}" == 1 ]] || WHY1+=" rc=${RC}(want 1: b-fail fails)"
if [[ -z "${WHY1}" ]]; then
    test_pass "H1 serial: 6 lines in report order, b-fail fail, c-flaky flaky (one line, flaky true), others pass, one run id, tree and seconds valid"
else
    test_fail "H1 serial: one line per suite in report order with the right results" "${WHY1# }"
fi

# ---------------------------------------------------------------------------
# H2: pool (VDE_TEST_JOBS=3): the same suite lines in any order; containers n/a for the pool suites
# ---------------------------------------------------------------------------

test_start "H2 pool (VDE_TEST_JOBS=3): the same suite lines (any order), the same results, containers n/a for the pool suites"
mixed_fixture h2p || exit 1
typeset FIX2="${SCRATCH}/h2p" HIST2
HIST2="${FIX2}/hist.jsonl"
set_mixed_expect
run_par "${FIX2}" VDE_TEST_JOBS=3 VDE_TEST_HISTORY_FILE="${HIST2}"
typeset WHY2=''
hist_check "${HIST2}" "${FIX2}" set
[[ -n "${FWHY}" ]] && WHY2+=" ${FWHY}"
hist_lines "${HIST2}"
typeset line2 s2
for line2 in "${HL[@]}"; do
    jfield "${line2}" suite; s2="${JV}"
    case "${s2}" in
        a-pass.test.zsh|b-fail.test.zsh|c-flaky.test.zsh)
            jfield "${line2}" containers
            [[ "${JV}" == n/a ]] || WHY2+=" ${s2} containers=${JV}(want n/a)"
            ;;
    esac
done
[[ "${RC}" == 1 ]] || WHY2+=" rc=${RC}(want 1)"
if [[ -z "${WHY2}" ]]; then
    test_pass "H2 pool: the same 6 suite lines and results as serial, containers n/a for the 3 pool suites"
else
    test_fail "H2 pool: the same suite lines, results and n/a containers" "${WHY2# }"
fi

# ---------------------------------------------------------------------------
# H3: appends: two runs into one file give 2x lines and two run ids; the earlier lines are byte-identical afterwards
# ---------------------------------------------------------------------------

test_start "H3 appends: two runs into one file: 2x lines, two distinct run ids, the earlier lines unchanged"
mixed_fixture h3s || exit 1
typeset FIX3="${SCRATCH}/h3s" HIST3
HIST3="${FIX3}/hist.jsonl"
run_par "${FIX3}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST3}"
typeset FIRST3='' SECOND3='' WHY3=''
FIRST3="$(<"${HIST3}")"
line_count "${HIST3}"
typeset -i N3A=${LCNT}
hist_lines "${HIST3}"
jfield "${HL[1]}" run; typeset RUN3A="${JV}"
run_par "${FIX3}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST3}"
SECOND3="$(<"${HIST3}")"
line_count "${HIST3}"
typeset -i N3B=${LCNT}
hist_lines "${HIST3}"
jfield "${HL[$(( N3A + 1 ))]}" run; typeset RUN3B="${JV}"
(( N3A > 0 )) || WHY3+=" first run wrote ${N3A} lines"
(( N3B == 2 * N3A )) || WHY3+=" lines ${N3A} then ${N3B}(want ${N3A} then $(( 2 * N3A )))"
[[ "${SECOND3}" == "${FIRST3}"$'\n'* ]] || WHY3+=" the earlier lines changed"
[[ "${RUN3A}" != "${RUN3B}" ]] || WHY3+=" both runs have run id ${RUN3A}"
if [[ -z "${WHY3}" ]]; then
    test_pass "H3 appends: ${N3A} then ${N3B} lines, run ids ${RUN3A} and ${RUN3B}, the earlier lines byte-identical"
else
    test_fail "H3 the history is append-only with one run id per run" "${WHY3# }"
fi

# ---------------------------------------------------------------------------
# H4: survives a killed run: a suite SIGKILLs the runner after an earlier suite finished; that suite's line is in the file
# ---------------------------------------------------------------------------

test_start "H4 survives a killed run: the suite that finished before the runner was SIGKILLed has its line in the file"
new_fixture h4s || exit 1
typeset FIX4="${SCRATCH}/h4s" HIST4
HIST4="${FIX4}/hist.jsonl"
count_suite "${FIX4}/tests/unit/a-first.test.zsh" 0 0 || exit 1
write_suite "${FIX4}/tests/unit/b-killer.test.zsh" <<'STUB' || exit 1
#!/usr/bin/env zsh
# runner-history H4 fixture: SIGKILLs the runner (its parent), so no later suite and no exit hook runs
kill -KILL ${PPID}
exit 0
STUB
run_par "${FIX4}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST4}"
typeset WHY4=''
EXP_SEQ=( sovereign-audit a-first.test.zsh )
EXP_RES[a-first.test.zsh]=pass
hist_check "${HIST4}" "${FIX4}" serial
[[ -n "${FWHY}" ]] && WHY4+=" ${FWHY}"
[[ "${RC}" != 0 ]] || WHY4+=" rc=0 after a SIGKILL of the runner"
[[ "$(<"${HIST4}")" == *b-killer* ]] && WHY4+=" the killed suite has a line"
if [[ -z "${WHY4}" ]]; then
    test_pass "H4 the audit and a-first lines survived the SIGKILL (rc ${RC}); the killed suite has no line"
else
    test_fail "H4 each suite's line is written when the suite is reported, so a killed run keeps its earlier lines" "${WHY4# }"
fi
EXP_SEQ=()
EXP_RES=()

# ---------------------------------------------------------------------------
# H5: a failing sovereign audit still records: one sovereign-audit line with result fail, no suite lines, exit 1
# ---------------------------------------------------------------------------

test_start "H5 a failing sovereign audit still records: one sovereign-audit line (fail), no suite lines, exit 1"
new_fixture h5s || exit 1
typeset FIX5="${SCRATCH}/h5s" HIST5
HIST5="${FIX5}/hist.jsonl"
print -l -- '#!/usr/bin/env zsh' 'exit 1' > "${FIX5}/bin/vde-enforce-uap.zsh" || exit 1
count_suite "${FIX5}/tests/unit/a-pass.test.zsh" 0 0 || exit 1
run_par "${FIX5}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST5}"
typeset WHY5=''
EXP_SEQ=( sovereign-audit )
EXP_RES=( sovereign-audit fail )
hist_check "${HIST5}" "${FIX5}" serial
[[ -n "${FWHY}" ]] && WHY5+=" ${FWHY}"
[[ "${RC}" == 1 ]] || WHY5+=" rc=${RC}(want 1)"
[[ -f "${FIX5}/state/run-count.a-pass.test.zsh" ]] && WHY5+=" a suite ran after the failed audit"
EXP_SEQ=()
EXP_RES=()
if [[ -z "${WHY5}" ]]; then
    test_pass "H5 failed audit: one sovereign-audit line with result fail, no suite lines, rc 1"
else
    test_fail "H5 a failed audit is recorded before the exit" "${WHY5# }"
fi

# ---------------------------------------------------------------------------
# H6: off writes nothing; unset in a fixture that is not a repository top writes no *.jsonl; exit codes unchanged
# ---------------------------------------------------------------------------

test_start "H6 VDE_TEST_HISTORY_FILE=off and an unset history in a non-repository fixture write nothing; exit codes unchanged"
typeset WHY6=''
typeset -a found6=()
# The marker suite is named with this test's pid: the runner records every suite it reports, so a marker line in the
# repository's real history would mean a fixture run wrote there. The real history is NOT compared by size, because the
# real runner may append its own lines while this suite runs in its pool.
typeset MARK6="h6-marker-$$.test.zsh"
new_fixture h6o || exit 1
typeset FIX6O="${SCRATCH}/h6o"
count_suite "${FIX6O}/tests/unit/${MARK6}" 0 0 || exit 1
# The run's cwd is the fixture root: 'off' read as a path would create ./off there, so the root's entries are compared.
# .test-tmp is the runner's own scratch directory, made on every run, so it is the one entry excluded from both listings.
typeset -a before6o=( "${FIX6O}"/*(DN) )
before6o=( ${before6o:#"${FIX6O}/.test-tmp"} )
run_par "${FIX6O}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE=off
typeset -a after6o=( "${FIX6O}"/*(DN) )
after6o=( ${after6o:#"${FIX6O}/.test-tmp"} )
[[ "${RC}" == 0 ]] || WHY6+=" off: rc=${RC}(want 0)"
found6=( "${FIX6O}"/**/*.jsonl(N) )
(( ${#found6} == 0 )) || WHY6+=" off: a *.jsonl file exists (${found6[1]})"
[[ -e "${FIX6O}/off" ]] && WHY6+=" off: a file named off was written to the fixture root"
[[ "${(j:\n:)before6o}" == "${(j:\n:)after6o}" ]] || WHY6+=" off: the fixture root gained entries"

new_fixture h6u || exit 1
typeset FIX6U="${SCRATCH}/h6u"
count_suite "${FIX6U}/tests/unit/${MARK6}" 0 0 || exit 1
run_par "${FIX6U}" VDE_TEST_JOBS=1
[[ "${RC}" == 0 ]] || WHY6+=" unset: rc=${RC}(want 0)"
found6=( "${FIX6U}"/**/*.jsonl(N) )
(( ${#found6} == 0 )) || WHY6+=" unset: a *.jsonl file exists (${found6[1]})"
[[ -f "${REAL_HIST}" && "$(<"${REAL_HIST}")" == *"${MARK6}"* ]] && WHY6+=" unset: the repository history has a line from the fixture"
if [[ -z "${WHY6}" ]]; then
    test_pass "H6 off: no file, the fixture root unchanged, rc 0; unset in a non-repository fixture: no *.jsonl anywhere, no line in the repository history, rc 0"
else
    test_fail "H6 off and unset write no history in a fixture" "${WHY6# }"
fi

# H6b: the runner sits in a subdirectory of a real repository, so the repository top is not the runner's root
test_start "H6b unset with the runner in a subdirectory of a real git repository: no history file in its .git, rc 0"
typeset REPO6B="${SCRATCH}/h6br" MARK6B="h6b-marker-$$.test.zsh"
new_fixture h6br/sub || exit 1
typeset FIX6B="${REPO6B}/sub"
count_suite "${FIX6B}/tests/unit/${MARK6B}" 0 0 || exit 1
( cd "${REPO6B}" && git init -q && git add -A && \
    git -c user.name='History Test' -c user.email='history-test@example.invalid' commit -q -m 'fixture' ) || exit 1
run_par "${FIX6B}" VDE_TEST_JOBS=1
typeset WHY6B=''
[[ "${RC}" == 0 ]] || WHY6B+=" rc=${RC}(want 0)"
[[ -e "${REPO6B}/.git/vde-test-history.jsonl" ]] && WHY6B+=" a vde-test-history.jsonl exists in the repository's .git"
typeset -a found6b=( "${REPO6B}"/**/*.jsonl(DN) )
(( ${#found6b} == 0 )) || WHY6B+=" a *.jsonl file exists (${found6b[1]})"
if [[ -z "${WHY6B}" ]]; then
    test_pass "H6b unset in a repository subdirectory: no history file in the repository's .git, rc 0"
else
    test_fail "H6b the top-level guard keeps a fixture copy out of the repository's history" "${WHY6B# }"
fi

# ---------------------------------------------------------------------------
# H7: an unwritable history path prints the WARNING once to stderr; the run still passes
# ---------------------------------------------------------------------------

test_start "H7 an unwritable history path (its parent is a regular file): WARNING once on stderr, the run still passes (rc 0)"
new_fixture h7s || exit 1
typeset FIX7="${SCRATCH}/h7s"
count_suite "${FIX7}/tests/unit/a-pass.test.zsh" 0 0 || exit 1
count_suite "${FIX7}/tests/unit/b-pass.test.zsh" 0 0 || exit 1
print -r -- blocker > "${FIX7}/blocker" || exit 1
run_par "${FIX7}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${FIX7}/blocker/hist.jsonl"
typeset WHY7=''
count_has 'WARNING: cannot append to the run history'
(( CNT == 1 )) || WHY7+=" WARNING lines=${CNT}(want 1)"
[[ "${RC}" == 0 ]] || WHY7+=" rc=${RC}(want 0)"
[[ -e "${FIX7}/blocker/hist.jsonl" || -d "${FIX7}/blocker" ]] && WHY7+=" a path under the blocker exists"
if [[ -z "${WHY7}" ]]; then
    test_pass "H7 unwritable history: the WARNING printed once, both suites passed, rc 0"
else
    test_fail "H7 an unwritable history path warns once and never fails the run" "${WHY7# }"
fi

# ---------------------------------------------------------------------------
# H8: decimal-comma locale (en_DK.utf8): seconds keep a dot and every line is valid (skips loudly without the locale)
# ---------------------------------------------------------------------------

typeset LOC_PROBE=''
LOC_PROBE="$(LC_ALL=en_DK.utf8 zsh -c 'printf "%.1f" 1.5' 2>/dev/null)"
if [[ "${LOC_PROBE}" != '1,5' ]]; then
    print -r -- "[SKIP] H8: no decimal-comma locale (en_DK.utf8) on this host; install the locales package and run locale-gen. H8 did not run and is not counted."
else
    test_start "H8 LC_ALL=en_DK.utf8: seconds keep a dot, every line has the exact shape, the flaky suite has one line"
    mixed_fixture h8s || exit 1
    typeset FIX8="${SCRATCH}/h8s" HIST8
    HIST8="${FIX8}/hist.jsonl"
    set_mixed_expect
    run_par "${FIX8}" VDE_TEST_JOBS=1 LC_ALL=en_DK.utf8 VDE_TEST_HISTORY_FILE="${HIST8}"
    typeset WHY8=''
    hist_check "${HIST8}" "${FIX8}" serial
    [[ -n "${FWHY}" ]] && WHY8+=" ${FWHY}"
    [[ "${RC}" == 1 ]] || WHY8+=" rc=${RC}(want 1)"
    if [[ -z "${WHY8}" ]]; then
        test_pass "H8 en_DK.utf8: 6 valid lines, seconds keep the dot"
    else
        test_fail "H8 under LC_ALL=en_DK.utf8 the seconds keep a dot and the lines stay valid" "${WHY8# }"
    fi
fi

# ---------------------------------------------------------------------------
# H9: default location in a real git repository: <repo>/.git/vde-test-history.jsonl; dirty false, then true after an edit
# ---------------------------------------------------------------------------

test_start "H9 default location in a real git repo: <repo>/.git/vde-test-history.jsonl; dirty false when clean, true after a tracked edit and after an untracked non-ignored file, false for an ignored untracked file"
new_fixture h9r || exit 1
typeset FIX9="${SCRATCH}/h9r" HIST9
HIST9="${FIX9}/.git/vde-test-history.jsonl"
print -r -- one > "${FIX9}/NOTES.txt" || exit 1
# .test-tmp is the runner's own scratch directory (created in the repository root on every run); scratch-ignored.txt is
# the untracked file that case (c) expects to stay ignored. The fixture must be clean after this commit.
print -l -- '.test-tmp/' 'scratch-ignored.txt' > "${FIX9}/.gitignore" || exit 1
( cd "${FIX9}" && git init -q && git add -A && \
    git -c user.name='History Test' -c user.email='history-test@example.invalid' commit -q -m 'fixture' ) || exit 1
typeset WHY9=''
[[ -z "$(cd "${FIX9}" && git status --porcelain)" ]] || WHY9+=" the fixture is not clean after its first commit"
EXP_SEQ=( sovereign-audit vm-lifecycle-integration.test.zsh BDD-Metadata )
EXP_RES=( sovereign-audit pass vm-lifecycle-integration.test.zsh pass BDD-Metadata pass )
run_par "${FIX9}"
[[ -f "${HIST9}" ]] || WHY9+=" no ${HIST9}"
hist_check "${HIST9}" "${FIX9}" serial
[[ -n "${FWHY}" ]] && WHY9+=" run1: ${FWHY}"
hist_lines "${HIST9}"
typeset -i N9A=${#HL} i9
for (( i9 = 1; i9 <= N9A; i9++ )); do
    jfield "${HL[i9]}" dirty
    [[ "${JV}" == false ]] || WHY9+=" run1 line ${i9} dirty=${JV}(want false)"
done
EXP_SEQ=()
EXP_RES=()
# h9_run LABEL WANT: one run of the H9 fixture; the lines it adds must all have the shape and dirty WANT (true|false)
h9_run() {
    local label="$1" want="$2"
    local -i from i
    hist_lines "${HIST9}"
    from=${#HL}
    run_par "${FIX9}"
    [[ "${RC}" == 0 ]] || WHY9+=" ${label}: rc=${RC}(want 0)"
    hist_lines "${HIST9}"
    (( ${#HL} > from )) || WHY9+=" ${label}: no line added"
    for (( i = from + 1; i <= ${#HL}; i++ )); do
        [[ "${HL[i]}" =~ ${SHAPE_RE} ]] || WHY9+=" ${label} line ${i} has the wrong shape"
        jfield "${HL[i]}" dirty
        [[ "${JV}" == "${want}" ]] || WHY9+=" ${label} line ${i} dirty=${JV}(want ${want})"
    done
}
# (a) a tracked edit: dirty true
print -r -- two >> "${FIX9}/NOTES.txt" || exit 1
h9_run "a tracked edit" true
# revert it: the tracked files are back at the commit
print -r -- one > "${FIX9}/NOTES.txt" || exit 1
[[ -z "$(cd "${FIX9}" && git diff --name-only HEAD)" ]] || WHY9+=" the tracked edit was not reverted"
# (b) an untracked, non-ignored file: dirty true (the old --untracked-files=no reported false here)
print -r -- extra > "${FIX9}/extra-untracked.txt" || exit 1
h9_run "an untracked, non-ignored file" true
rm -f -- "${FIX9}/extra-untracked.txt"
# (c) an untracked file that .gitignore ignores: git status shows nothing, so dirty false
print -r -- ignored > "${FIX9}/scratch-ignored.txt" || exit 1
[[ -z "$(cd "${FIX9}" && git status --porcelain)" ]] || WHY9+=" the ignored file shows in git status"
h9_run "an untracked file that .gitignore ignores" false
if [[ -z "${WHY9}" ]]; then
    test_pass "H9 repo history: clean tree dirty false (${N9A} lines); a tracked edit and an untracked non-ignored file dirty true; an ignored untracked file dirty false"
else
    test_fail "H9 the default history lives in the repository's git directory and records dirty over tracked and untracked files" "${WHY9# }"
fi
EXP_SEQ=()
EXP_RES=()

# ---------------------------------------------------------------------------
# H10: every line matches the exact line shape; malformed copies of a line do not (negative controls)
# ---------------------------------------------------------------------------

test_start "H10 every line of the H1 history matches the exact line shape; malformed copies of a line do not match"
typeset WHY10=''
typeset -i bad10=0
hist_lines "${HIST1}"
typeset -i n10=${#HL} k10
typeset line10
for line10 in "${HL[@]}"; do
    [[ "${line10}" =~ ${SHAPE_RE} ]] || bad10+=1
done
(( n10 > 0 )) || WHY10+=" no lines to check"
(( bad10 == 0 )) || WHY10+=" ${bad10} line(s) of the shape"
typeset GOOD10="${HL[1]}"
typeset -a NEG10=(
    "${GOOD10},"
    "${GOOD10%\}}"
    "${GOOD10/\"v\":1/\"v\":2}"
    "${GOOD10/\"flaky\":false/\"flaky\":maybe}"
    "${GOOD10/\"seconds\":[0-9].[0-9]/\"seconds\":1.50}"
    '{"v":1,"run":"x"}'
)
for line10 in "${NEG10[@]}"; do
    if [[ "${line10}" =~ ${SHAPE_RE} ]]; then
        WHY10+=" a malformed line matched: ${line10}"
    fi
done
if [[ -z "${WHY10}" ]]; then
    test_pass "H10 ${n10} lines match the exact shape; ${#NEG10} malformed copies do not"
else
    test_fail "H10 the line shape is exact in both directions" "${WHY10# }"
fi

# ---------------------------------------------------------------------------
# H11: suite names with a tab and a newline: one physical line per suite, the control characters escaped as \uXXXX
# ---------------------------------------------------------------------------

test_start "H11 suite file names with a tab and a newline: one physical line per suite, control characters written as escapes, no raw control character"
typeset FIX11="${SCRATCH}/h11c" HIST11
HIST11="${FIX11}/hist.jsonl"
typeset TAB11=$'t\tab.test.zsh' NL11=$'n\nl.test.zsh' TABK11='t\u0009ab.test.zsh' NLK11='n\u000al.test.zsh'
typeset -i HAVE_NL11=1
new_fixture h11c || exit 1
count_suite "${FIX11}/tests/unit/${TAB11}" 0 0 || exit 1
count_suite "${FIX11}/tests/unit/${NL11}" 0 0 || HAVE_NL11=0
if (( HAVE_NL11 )); then
    typeset -i EXP11=5
    EXP_SEQ=( sovereign-audit "${TABK11}" "${NLK11}" vm-lifecycle-integration.test.zsh BDD-Metadata )
    EXP_RES=( sovereign-audit pass "${TABK11}" pass "${NLK11}" pass vm-lifecycle-integration.test.zsh pass BDD-Metadata pass )
else
    typeset -i EXP11=4
    print -r -- "[SKIP] H11: the filesystem refuses a newline in a file name; the newline half of H11 did not run and is not counted."
    EXP_SEQ=( sovereign-audit "${TABK11}" vm-lifecycle-integration.test.zsh BDD-Metadata )
    EXP_RES=( sovereign-audit pass "${TABK11}" pass vm-lifecycle-integration.test.zsh pass BDD-Metadata pass )
fi
run_par "${FIX11}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST11}"
typeset WHY11=''
hist_check "${HIST11}" "${FIX11}" set
[[ -n "${FWHY}" ]] && WHY11+=" ${FWHY}"
line_count "${HIST11}"
(( LCNT == EXP11 )) || WHY11+=" physical lines=${LCNT}(want ${EXP11}, one per suite)"
[[ "$(<"${HIST11}")" == *'"suite":"t\u0009ab.test.zsh"'* ]] || WHY11+=" the tab is not written as \\u0009"
(( HAVE_NL11 == 0 )) || [[ "$(<"${HIST11}")" == *'"suite":"n\u000al.test.zsh"'* ]] || WHY11+=" the newline is not written as \\u000a"
typeset -i cc11
cc11="$(tr -d '\n' < "${HIST11}" | grep -c '[[:cntrl:]]')"
(( cc11 == 0 )) || WHY11+=" ${cc11} raw control character(s) in the file"
[[ "${RC}" == 0 ]] || WHY11+=" rc=${RC}(want 0)"
# negative control: a raw tab inside a suite name must not match the shape
hist_lines "${HIST11}"
typeset TABX11=$'\t' NEG11=''
NEG11="${HL[1]/sovereign-audit/a${TABX11}b}"
[[ "${NEG11}" =~ ${SHAPE_RE} ]] && WHY11+=" a raw tab in a suite name matched the shape"
[[ "${HL[1]}" =~ ${SHAPE_RE} ]] || WHY11+=" the unmodified first line does not match the shape"
EXP_SEQ=()
EXP_RES=()
if [[ -z "${WHY11}" ]]; then
    test_pass "H11 ${EXP11} physical lines, one per suite; the tab and the newline written as the escapes; no raw control character; a raw tab does not match"
else
    test_fail "H11 one physical line per suite, control characters escaped" "${WHY11# }"
fi

# ---------------------------------------------------------------------------
# H12: a serial fail-then-pass suite: the history line's containers is the SUM of both attempts' creates (2 + 3 = 5)
# ---------------------------------------------------------------------------

test_start "H12 serial fail-then-pass suite: one history line, flaky, containers is the sum of both attempts (2 + 3 = 5)"
new_fixture h12d || exit 1
typeset FIX12="${SCRATCH}/h12d" HIST12
HIST12="${FIX12}/hist.jsonl"
# The first run creates 2 containers and fails; the rerun creates 3 and passes. Each create is recorded by the stub docker.
write_suite "${FIX12}/tests/unit/d-docker.test.zsh" <<'STUB' || exit 1
#!/usr/bin/env zsh
# runner-history H12 fixture: the first run creates 2 containers and fails, the rerun creates 3 and passes
typeset f="${RP_STATE}/run-count.${0:t}" n=0
[[ -f "${f}" ]] && n="$(<"${f}")"
n=$(( n + 1 ))
print -r -- "${n}" > "${f}"
typeset -i creates=3 k=0
(( n == 1 )) && creates=2
while (( k < creates )); do
    k+=1
    docker create --name "h12-${n}-${k}" busybox >/dev/null 2>&1
done
(( n == 1 )) && exit 3
exit 0
STUB
# The stub docker: create records its epoch time; events answers with the creates inside its --since/--until window.
write_suite "${FIX12}/stubs/docker" <<'STUB' || exit 1
#!/usr/bin/env zsh
# runner-history H12 stub docker: create records its epoch time in DOCKER_EVENTS; events lists the creates in its window
zmodload zsh/datetime
print -r -- "$*" >> "${DOCKER_LOG}"
case "$1" in
    create)
        print -r -- "${EPOCHREALTIME}" >> "${DOCKER_EVENTS}"
        exit 0 ;;
    events)
        typeset t_from=0 t_to=99999999999 k
        typeset ts
        for (( k = 1; k <= $#; k++ )); do
            case "${argv[k]}" in
                --since) t_from="${argv[k+1]}" ;;
                --until) t_to="${argv[k+1]}" ;;
            esac
        done
        if [[ -f "${DOCKER_EVENTS}" ]]; then
            while read -r ts; do
                (( ts >= t_from && ts <= t_to )) && print -r -- "container create ${ts}"
            done < "${DOCKER_EVENTS}"
        fi
        exit 0 ;;
esac
exit 0
STUB
EXP_SEQ=( sovereign-audit d-docker.test.zsh vm-lifecycle-integration.test.zsh BDD-Metadata )
EXP_RES=( sovereign-audit pass d-docker.test.zsh flaky vm-lifecycle-integration.test.zsh pass BDD-Metadata pass )
run_par "${FIX12}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST12}" \
    DOCKER_EVENTS="${FIX12}/docker.events" DOCKER_LOG="${FIX12}/docker.log"
typeset WHY12=''
hist_check "${HIST12}" "${FIX12}" serial
[[ -n "${FWHY}" ]] && WHY12+=" ${FWHY}"
[[ "${RC}" == 0 ]] || WHY12+=" rc=${RC}(want 0: the suite passed on its rerun)"
[[ "$(<"${FIX12}/state/run-count.d-docker.test.zsh")" == 2 ]] || WHY12+=" the suite did not run exactly twice"
# The pinned design: serial mode queries docker events once per timed window (audit, both attempts, integration)
typeset -i EVN=0
typeset DLL12
while IFS= read -r DLL12; do
    [[ "${DLL12}" == events* ]] && EVN+=1
done < "${FIX12}/docker.log"
(( EVN == 4 )) || WHY12+=" docker events calls=${EVN}(want 4: audit, two attempts, integration)"
typeset -i found12=0
typeset line12 s12
hist_lines "${HIST12}"
for line12 in "${HL[@]}"; do
    jfield "${line12}" suite; s12="${JV}"
    [[ "${s12}" == d-docker.test.zsh ]] || continue
    found12+=1
    jfield "${line12}" containers
    [[ "${JV}" == 5 ]] || WHY12+=" containers=${JV}(want 5: 2 from the first run plus 3 from the rerun)"
done
(( found12 == 1 )) || WHY12+=" d-docker has ${found12} history lines (want 1)"
EXP_SEQ=()
EXP_RES=()
if [[ -z "${WHY12}" ]]; then
    test_pass "H12 fail-then-pass suite: one flaky line, containers 5 = 2 (first run) + 3 (rerun); 4 docker events calls in serial mode"
else
    test_fail "H12 the history containers is the sum of both attempts' creates" "${WHY12# }"
fi

# ---------------------------------------------------------------------------
# H13: two runs back to back: every line of a run carries one well-formed run id; the two runs' whole ids differ
# ---------------------------------------------------------------------------

test_start "H13 two runs back to back: each run's lines carry one well-formed run id; the two runs' whole ids differ"
new_fixture h13r || exit 1
typeset FIX13="${SCRATCH}/h13r" HIST13
HIST13="${FIX13}/hist.jsonl"
typeset WHY13=''
run_par "${FIX13}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST13}"
[[ "${RC}" == 0 ]] || WHY13+=" run A rc=${RC}(want 0)"
hist_lines "${HIST13}"
typeset -i N13A=${#HL}
run_par "${FIX13}" VDE_TEST_JOBS=1 VDE_TEST_HISTORY_FILE="${HIST13}"
[[ "${RC}" == 0 ]] || WHY13+=" run B rc=${RC}(want 0)"
hist_lines "${HIST13}"
typeset -i N13B=${#HL} i13
typeset -a ids13=()
typeset RUNID13_RE='^[0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]{5}$'
(( N13A > 0 && N13B > N13A )) || WHY13+=" lines ${N13A} then ${N13B}"
for (( i13 = 1; i13 <= N13B; i13++ )); do
    [[ "${HL[i13]}" =~ ${SHAPE_RE} ]] || WHY13+=" line ${i13} has the wrong shape"
    jfield "${HL[i13]}" run
    ids13+=( "${JV}" )
done
if (( N13A > 0 && N13B > N13A )); then
    for (( i13 = 1; i13 <= N13B; i13++ )); do
        if (( i13 <= N13A )); then typeset want13="${ids13[1]}"; else typeset want13="${ids13[N13A+1]}"; fi
        [[ "${ids13[i13]}" == "${want13}" ]] || WHY13+=" line ${i13} has run ${ids13[i13]}(want ${want13})"
    done
    [[ "${ids13[1]}" =~ ${RUNID13_RE} ]] || WHY13+=" run A id ${ids13[1]} is not well formed"
    [[ "${ids13[N13A+1]}" =~ ${RUNID13_RE} ]] || WHY13+=" run B id ${ids13[N13A+1]} is not well formed"
    [[ "${ids13[1]}" != "${ids13[N13A+1]}" ]] || WHY13+=" both runs have the run id ${ids13[1]}"
fi
if [[ -z "${WHY13}" ]]; then
    test_pass "H13 two back-to-back runs: ids ${ids13[1]} and ${ids13[N13A+1]} differ; each run's ${N13A} and $(( N13B - N13A )) lines carry one id"
else
    test_fail "H13 two back-to-back runs have different whole run ids" "${WHY13# }"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
