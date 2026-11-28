#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: per-suite timing in the Sovereign runner (Signet #774, step 1). Timing is ALWAYS ON: no variable enables it.
#
# A default run of the runner (no variable set):
#   - announces each suite with a wall-clock time ("➤ Running: <suite>" carries HH:MM:SS) and reports its duration on
#     the result line ("✓ <suite> passed (12.3s)" / "✗ <suite> failed (exit code: N) (12.3s)");
#   - times the Sovereign Audit and every suite, and prints a SUITE TIMING table before the final summary, even when a
#     suite failed: one row per step, slowest first, "<name> <seconds>s <containers>", then
#     "Total suite time: <seconds>s (<n> suites)";
#   - takes the containers column from `docker events --filter type=container --filter event=create --since <t0>
#     --until <t1>` (epoch seconds), and shows n/a when docker is missing or the call fails. A docker failure never
#     changes the runner's exit code;
#   - with VDE_TEST_TIMING_FILE=<path> also writes one line per row, "<seconds> <containers> <suite>", in table order.
#
# This file runs a copy of the real runner in a stub fixture (no containers, no network). The audit, the unit suites
# and the integration suite are stubs; docker is a stub on PATH. Suite b creates two containers through the stub
# (`docker create`); the stub records each create with its epoch time and answers `docker events` with the creates
# inside the --since/--until window. Until the timing lands these checks FAIL (RED): the runner has no timing yet.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_POL_STAMP_TTL VDE_TEST_TIMING_FILE

typeset ROOT="${0:A:h:h:h}"
typeset RUNNER_SRC="${ROOT}/tests/run-sovereign-tests.zsh"
typeset LIBENV_SRC="${ROOT}/lib/vde-test-env"
typeset -g OUT='' RC=0 SECTION='' TOTAL_LINE=''
typeset -ga ROW_NAMES=()
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
SCRATCH="$(mktemp -d "${SCRATCH}/runner-timing.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

new_fixture() {  # new_fixture NAME -> SCRATCH/NAME: the REAL runner and lib, stub audit and suites, a stub docker in stubs/
    local f="${SCRATCH}/$1"
    mkdir -p "${f}/tests/unit" "${f}/tests/integration" "${f}/tests/features/core-infrastructure" \
        "${f}/bin" "${f}/lib" "${f}/stubs" "${f}/callerhome" || return 1
    cp "${RUNNER_SRC}" "${f}/tests/run-sovereign-tests.zsh" || return 1
    cp "${LIBENV_SRC}" "${f}/lib/vde-test-env" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/bin/vde-enforce-uap.zsh"
    print -l -- '#!/usr/bin/env zsh' \
        'print -l -- "${LC_ALL-unset}" "${LC_NUMERIC-unset}" > "${0:A:h:h:h}/suite-a-locale-seen.txt"' \
        'exit 0' > "${f}/tests/unit/a.test.zsh"
    print -l -- '#!/usr/bin/env zsh' 'zmodload zsh/zselect zsh/datetime' \
        'if command -v docker >/dev/null 2>&1; then' \
        '    docker create --name b-one busybox >/dev/null 2>&1' \
        '    docker create --name b-two busybox >/dev/null 2>&1' \
        'fi' \
        'typeset -i bx=0' \
        'while (( bx++ < ${B_EXTRA:-0} )); do print -r -- "${EPOCHREALTIME}" >> "${DOCKER_EVENTS}"; done' \
        'zselect -t 100' \
        'exit 0' > "${f}/tests/unit/b.test.zsh"
    print -l -- '#!/usr/bin/env zsh' 'exit 1' > "${f}/tests/unit/c.test.zsh"
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/tests/integration/vm-lifecycle-integration.test.zsh"
    print -l -- '@forge' 'Feature: stub' > "${f}/tests/features/core-infrastructure/proof-of-life-the-contract.feature"
    print -l -- '#!/usr/bin/env zsh' \
        'zmodload zsh/datetime' \
        'print -r -- "$*" >> "${DOCKER_LOG}"' \
        'case "$1" in' \
        '    create)' \
        '        print -r -- "${EPOCHREALTIME}" >> "${DOCKER_EVENTS}"' \
        '        exit 0 ;;' \
        '    events)' \
        '        [[ -n "${DOCKER_FAIL:-}" ]] && exit 2' \
        '        typeset t_from=0 t_to=99999999999 k' \
        '        typeset ts' \
        '        for (( k = 1; k <= $#; k++ )); do' \
        '            case "${argv[k]}" in' \
        '                --since) t_from="${argv[k+1]}" ;;' \
        '                --until) t_to="${argv[k+1]}" ;;' \
        '            esac' \
        '        done' \
        '        if [[ -f "${DOCKER_EVENTS}" ]]; then' \
        '            while read -r ts; do' \
        '                (( ts >= t_from && ts <= t_to )) && print -r -- "container create ${ts}"' \
        '            done < "${DOCKER_EVENTS}"' \
        '        fi' \
        '        exit 0 ;;' \
        'esac' \
        'exit 0' > "${f}/stubs/docker"
    chmod +x "${f}/bin/vde-enforce-uap.zsh" "${f}/tests/unit/"*.test.zsh \
        "${f}/tests/integration/"*.test.zsh "${f}/stubs/docker"
}

build_nodocker_path() {  # build_nodocker_path DIR -> DIR holds symlinks to every command on PATH except docker
    local d x
    mkdir -p "$1" || return 1
    for d in ${(s.:.)PATH}; do
        [[ -d "${d}" ]] || continue
        for x in "${d}"/*(N); do
            [[ "${x:t}" == docker || -e "$1/${x:t}" ]] && continue
            ln -s "${x}" "$1/${x:t}"
        done
    done
}

build_path_without_timeouts() {  # build_path_without_timeouts DIR -> DIR holds symlinks to every command on PATH except docker, timeout and gtimeout
    local d x
    mkdir -p "$1" || return 1
    for d in ${(s.:.)PATH}; do
        [[ -d "${d}" ]] || continue
        for x in "${d}"/*(N); do
            [[ "${x:t}" == docker || "${x:t}" == timeout || "${x:t}" == gtimeout || -e "$1/${x:t}" ]] && continue
            ln -s "${x}" "$1/${x:t}"
        done
    done
}

slow_suite() {  # slow_suite FILE: a passing suite that takes about 0.5s, so two runners started together overlap
    print -l -- '#!/usr/bin/env zsh' 'zmodload zsh/zselect' 'zselect -t 50' 'exit 0' > "$1" && chmod +x "$1"
}

hang_docker_stub() {  # hang_docker_stub FIXTURE: stubs/docker whose events subcommand holds for about 8s (80 x 0.1s); create still records
    print -l -- '#!/usr/bin/env zsh' \
        'zmodload zsh/datetime zsh/zselect' \
        'print -r -- "$*" >> "${DOCKER_LOG}"' \
        'case "$1" in' \
        '    create)' \
        '        print -r -- "${EPOCHREALTIME}" >> "${DOCKER_EVENTS}"' \
        '        exit 0 ;;' \
        '    events)' \
        '        typeset -i k' \
        '        for (( k = 0; k < 80; k++ )); do zselect -t 10; done' \
        '        exit 0 ;;' \
        'esac' \
        'exit 0' > "$1/stubs/docker" || return 1
    chmod +x "$1/stubs/docker"
}

run_in() {  # run_in FIXTURE PATHVALUE [NAME=value ...] -> OUT (colour codes removed) and RC (the runner's exit status)
    local fix="$1" p="$2" raw
    shift 2
    # VDE_TEST_JOBS=1 (serial): per-suite container counts exist only in serial mode; a later NAME=value argument overrides it. VDE_FLAKE_RERUN=0 keeps the row counts exact (the rerun has its own cases in runner-flaky.test.zsh).
    raw="$(cd "${fix}" && timeout 120 env -i HOME="${fix}/callerhome" PATH="${p}" VDE_TEST_JOBS=1 VDE_FLAKE_RERUN=0 \
        DOCKER_LOG="${fix}/docker.log" DOCKER_EVENTS="${fix}/docker.events" \
        "$@" zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RC=$?")"
    RC="${raw##*RC=}"
    OUT="$(print -r -- "${raw%RC=*}" | sed 's/\x1b\[[0-9;]*m//g')"
}

line_matching() {  # line_matching REGEX -> the first line of OUT matching REGEX (a zsh regex, unquoted); status 1 if none
    local line
    for line in "${(@f)OUT}"; do
        [[ "${line}" =~ $1 ]] && { print -r -- "${line}"; return 0; }
    done
    return 1
}

timing_section() {  # sets SECTION to OUT from the SUITE TIMING heading through the Total line, and TOTAL_LINE to that line
    local line
    local -i on=0
    SECTION=''
    TOTAL_LINE=''
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *'SUITE TIMING'* ]] && on=1
        (( on )) && SECTION+="${line}"$'\n'
        if (( on )) && [[ "${line}" == *'Total suite time:'* ]]; then TOTAL_LINE="${line}"; break; fi
    done
}

row_names() {  # sets ROW_NAMES to the name that starts each table row of SECTION (a row: "<name> <n>.<d>s <containers>"), in order
    local line
    local -a w
    ROW_NAMES=()
    for line in "${(@f)SECTION}"; do
        w=( ${(z)line} )
        [[ "${w[2]:-}" =~ '^[0-9]+\.[0-9]+s$' ]] && ROW_NAMES+=( "${w[1]}" )
    done
}

row_of() {  # row_of NAME -> the table row whose first word is NAME
    local line
    local -a w
    for line in "${(@f)SECTION}"; do
        w=( ${(z)line} )
        if [[ "${w[1]:-}" == "$1" ]]; then print -r -- "${line}"; return 0; fi
    done
    return 1
}

secs_of() {  # secs_of ROW -> the wall time in its field, which must have exactly one decimal (e.g. 1.0)
    [[ "$1" =~ '([0-9]+\.[0-9])s' ]] && print -r -- "${match[1]}"
    return 0
}

containers_of() {  # containers_of ROW -> its last field (the containers column)
    local -a w=( ${(z)1} )
    print -r -- "${w[-1]:-}"
}

typeset -a WANT=( a.test.zsh b.test.zsh c.test.zsh vm-lifecycle-integration.test.zsh )
typeset FIX_T="${SCRATCH}/timing" FIX_F="${SCRATCH}/docker-fails" FIX_N="${SCRATCH}/nodocker"
typeset NODOCKER="${SCRATCH}/path-without-docker"
new_fixture timing || exit 1
new_fixture docker-fails || exit 1
new_fixture nodocker || exit 1
build_nodocker_path "${NODOCKER}" || exit 1

# ---------------------------------------------------------------------------
# Case 1: a default run (no variable set), docker stub on PATH, c fails
# ---------------------------------------------------------------------------

test_start "1a: a default run prints a SUITE TIMING table and the runner still exits 1 (c fails)"
run_in "${FIX_T}" "${FIX_T}/stubs:${PATH}" VDE_TEST_TIMING_FILE="${FIX_T}/timing.txt"
timing_section
if [[ "${OUT}" == *'SUITE TIMING'* && "${RC}" == 1 ]]; then
    test_pass "1a the SUITE TIMING section is printed and the runner exits 1"
else
    test_fail "1a the SUITE TIMING section is printed and the runner exits 1" "rc=${RC} out: ${OUT[1,300]//$'\n'/ | }"
fi

test_start "1b one row for the Sovereign Audit and one for each of a, b, c and the integration suite (5 rows)"
row_names
typeset AUDIT_ROW='' w missing=''
for w in "${ROW_NAMES[@]}"; do
    [[ "${(L)w}" == *audit* || "${(L)w}" == *uap* ]] && AUDIT_ROW="${w}"
done
typeset -a ALL=()
[[ -n "${AUDIT_ROW}" ]] && ALL+=( "${AUDIT_ROW}" ) || missing+=" audit"
for w in "${WANT[@]}"; do
    (( ${ROW_NAMES[(Ie)${w}]} )) || missing+=" ${w}"
    ALL+=( "${w}" )
done
if [[ -z "${missing}" ]] && (( ${#ROW_NAMES} == 5 )); then
    test_pass "1b rows: ${ROW_NAMES[*]}"
else
    test_fail "1b one row for the audit and each of a, b, c, integration (5 rows)" "rows: ${ROW_NAMES[*]} missing:${missing}"
fi

test_start "1c rows are sorted slowest first: each row's seconds is at least the next row's; b.test.zsh takes at least 0.9s"
typeset sorted_bad='' prev_s='' cur_s='' bsecs_1c=''
typeset -i ri
for (( ri = 1; ri < ${#ROW_NAMES}; ri++ )); do
    prev_s="$(secs_of "$(row_of "${ROW_NAMES[ri]}")")"
    cur_s="$(secs_of "$(row_of "${ROW_NAMES[ri+1]}")")"
    [[ -n "${prev_s}" && -n "${cur_s}" ]] && (( prev_s >= cur_s )) || sorted_bad+=" ${ROW_NAMES[ri]}>${ROW_NAMES[ri+1]}"
done
bsecs_1c="$(secs_of "$(row_of b.test.zsh)")"
if [[ -z "${sorted_bad}" && -n "${bsecs_1c}" ]] && (( bsecs_1c >= 0.9 )); then
    test_pass "1c rows are in descending order of seconds; b=${bsecs_1c}s"
else
    test_fail "1c rows sorted by descending seconds, and b.test.zsh at least 0.9s" "out of order:${sorted_bad:- none} b=${bsecs_1c:-none} rows: ${ROW_NAMES[*]}"
fi

test_start "1d each row shows its wall time in seconds with one decimal; b took at least 0.9s"
typeset bad_rows='' s bsecs=''
for w in "${ALL[@]}"; do
    s="$(secs_of "$(row_of "${w}")")"
    [[ -n "${s}" ]] || bad_rows+=" ${w}"
done
bsecs="$(secs_of "$(row_of b.test.zsh)")"
if [[ -z "${bad_rows}" && -n "${bsecs}" ]] && (( bsecs >= 0.9 )); then
    test_pass "1d every row has a <n>.<d>s wall time; b=${bsecs}s"
else
    test_fail "1d every row has a <n>.<d>s wall time and b takes at least 0.9s" "rows without a time:${bad_rows} b=${bsecs:-none}"
fi

test_start "1e the total line reads 'Total suite time: <seconds>s (<n> suites)' and n equals the number of rows"
if [[ "${TOTAL_LINE}" =~ 'Total suite time: [0-9]+\.[0-9]s' && "${TOTAL_LINE}" =~ '\(([0-9]+) suites?\)' ]] \
    && (( ${match[1]} == ${#ROW_NAMES} )); then
    test_pass "1e total line: ${TOTAL_LINE}"
else
    test_fail "1e total line 'Total suite time: <seconds>s (<n> suites)' with n = rows" "line: ${TOTAL_LINE:-none}"
fi

test_start "1f the containers column: b created 2 containers; the audit, a, c and the integration suite 0"
typeset wrong='' got exp
for w in "${ALL[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${w}" == b.test.zsh ]] && exp=2 || exp=0
    [[ "${got}" == "${exp}" ]] || wrong+=" ${w}=${got:-none}"
done
if [[ -z "${wrong}" ]]; then
    test_pass "1f containers: b=2, the rest 0"
else
    test_fail "1f containers: b=2, the rest 0" "mismatch:${wrong}"
fi

test_start "1g the table comes before the final summary"
typeset -a L=( "${(@f)OUT}" )
typeset -i ti=${L[(i)*SUITE TIMING*]} si=${L[(i)*VDE TEST SUMMARY*]}
if (( ti <= ${#L} && ti < si )); then
    test_pass "1g SUITE TIMING (line ${ti}) precedes the VDE TEST SUMMARY (line ${si})"
else
    test_fail "1g SUITE TIMING before the final summary" "timing line ${ti}, summary line ${si}"
fi

test_start "1h each suite's announcement carries HH:MM:SS and its result line carries its duration"
typeset -a RUN_RE=( 'Running: a\.test\.zsh' 'Running: b\.test\.zsh' 'Running: c\.test\.zsh' 'Running: vm-lifecycle-integration\.test\.zsh' )
typeset -a RES_RE=(
    'a\.test\.zsh passed \([0-9]+\.[0-9]s\)'
    'b\.test\.zsh passed \([0-9]+\.[0-9]s\)'
    'c\.test\.zsh failed \(exit code: 1\) \([0-9]+\.[0-9]s\)'
    'vm-lifecycle-integration\.test\.zsh passed \([0-9]+\.[0-9]s\)'
)
typeset ann_bad='' res_bad='' ln
typeset -i n
for (( n = 1; n <= 4; n++ )); do
    ln="$(line_matching "${RUN_RE[n]}")"
    [[ -n "${ln}" && "${ln}" =~ '[0-9][0-9]:[0-9][0-9]:[0-9][0-9]' ]] || ann_bad+=" ${RUN_RE[n]}"
    [[ -n "$(line_matching "${RES_RE[n]}")" ]] || res_bad+=" ${RES_RE[n]}"
done
if [[ -z "${ann_bad}" && -z "${res_bad}" ]]; then
    test_pass "1h four announcements with HH:MM:SS and four result lines with durations"
else
    test_fail "1h announcements with HH:MM:SS and result lines with durations" "no timestamp:${ann_bad} no duration:${res_bad}"
fi

test_start "1i docker events was queried with type=container, event=create, --since and --until"
typeset LOG_T="${FIX_T}/docker.log" LOGTXT=''
[[ -f "${LOG_T}" ]] && LOGTXT="$(<"${LOG_T}")"
if [[ "${LOGTXT}" == *'events'* && "${LOGTXT}" == *'type=container'* && "${LOGTXT}" == *'event=create'* \
    && "${LOGTXT}" == *'--since'* && "${LOGTXT}" == *'--until'* ]]; then
    test_pass "1i docker events --filter type=container --filter event=create --since --until was called"
else
    test_fail "1i docker events query with type=container, event=create, --since and --until" "log: ${LOGTXT[1,300]//$'\n'/ | }"
fi

# The stub accepts any --format, but the real daemon rejects a field an events message does not have
# (`{{.ID}}` fails; the container id of an event is `{{.Actor.ID}}`), which would make every count n/a.
# Exactly ONE created container: a count taken as a string length (a container id is 64 characters, a stub
# line about 30) would report that length instead of 1.
test_start "1l exactly one container created in a window is counted as 1, not as the length of its id"
new_fixture one-create || exit 1
typeset FIX_1="${SCRATCH}/one-create"
grep -v 'b-two' "${FIX_1}/tests/unit/b.test.zsh" > "${FIX_1}/b.tmp" && mv "${FIX_1}/b.tmp" "${FIX_1}/tests/unit/b.test.zsh" && chmod +x "${FIX_1}/tests/unit/b.test.zsh"
run_in "${FIX_1}" "${FIX_1}/stubs:${PATH}"
timing_section
row_names
typeset got1="$(containers_of "$(row_of b.test.zsh)")"
if [[ "${got1}" == 1 ]]; then
    test_pass "1l one create in the window is counted as 1"
else
    test_fail "1l one create counted" "b containers=${got1:-none} (expected 1)"
fi

test_start "1k the docker events query reads the container id with the Actor.ID field the real daemon accepts"
if [[ "${LOGTXT}" == *'--format {{.Actor.ID}}'* ]]; then
    test_pass "1k docker events is called with --format {{.Actor.ID}}"
else
    test_fail "1k docker events format field" "log: ${LOGTXT[1,300]//$'\n'/ | }"
fi

test_start "1j VDE_TEST_TIMING_FILE gets one line per row: <seconds> <containers> <suite>, in table order"
typeset FILE_T="${FIX_T}/timing.txt"
typeset -a FL=() fields
typeset -i i
typeset fok=1
[[ -f "${FILE_T}" ]] && FL=( "${(@f)$(<"${FILE_T}")}" )
(( ${#FL} == ${#ROW_NAMES} && ${#ROW_NAMES} == 5 )) || fok=0
for (( i = 1; i <= ${#FL}; i++ )); do
    fields=( ${(z)FL[i]} )
    [[ "${fields[1]:-}" =~ '^[0-9]+(\.[0-9]+)?$' ]] || fok=0
    [[ "${fields[3]:-}" == "${ROW_NAMES[i]:-x}" ]] || fok=0
    if [[ "${fields[3]:-}" == b.test.zsh ]]; then
        [[ "${fields[2]:-}" == 2 ]] || fok=0
    else
        [[ "${fields[2]:-}" == 0 ]] || fok=0
    fi
done
if (( fok )); then
    test_pass "1j timing file: ${#FL} lines in table order, b first with 2 containers"
else
    test_fail "1j timing file: one '<seconds> <containers> <suite>' line per row, in table order" "lines: ${#FL} file: ${(j: | :)FL[1,5]}"
fi

test_start "1m the default run does not set LC_ALL for the suite: a.test.zsh sees LC_ALL unset"
typeset -a SEEN1=()
[[ -f "${FIX_T}/suite-a-locale-seen.txt" ]] && SEEN1=( "${(@f)$(<"${FIX_T}/suite-a-locale-seen.txt")}" )
if [[ "${SEEN1[1]:-}" == unset ]]; then
    test_pass "1m a.test.zsh saw LC_ALL unset in the default run"
else
    test_fail "1m a.test.zsh sees LC_ALL unset (the runner does not pin the suite's locale)" "first line: ${SEEN1[1]:-none}"
fi

# ---------------------------------------------------------------------------
# Case 2: docker events fails: n/a, the table still prints, the exit code is unchanged
# ---------------------------------------------------------------------------

test_start "2a: a failing docker events shows containers n/a, still prints the table, and leaves the exit code at 1"
run_in "${FIX_F}" "${FIX_F}/stubs:${PATH}" DOCKER_FAIL=1
timing_section
row_names
typeset na_bad=''
for w in "${ROW_NAMES[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${got}" == 'n/a' ]] || na_bad+=" ${w}=${got:-none}"
done
if [[ "${OUT}" == *'SUITE TIMING'* && "${RC}" == 1 && -z "${na_bad}" ]] && (( ${#ROW_NAMES} == 5 )); then
    test_pass "2a table printed, containers n/a for every row, rc=1 unchanged"
else
    test_fail "2a failing docker: n/a column, table printed, rc unchanged at 1" "rc=${RC} rows: ${ROW_NAMES[*]} not n/a:${na_bad}"
fi

# ---------------------------------------------------------------------------
# Case 3: no docker on PATH: the column shows n/a and the run still works
# ---------------------------------------------------------------------------

test_start "3a the PATH for this run has no docker"
if [[ ! -e "${NODOCKER}/docker" ]] && ! PATH="${NODOCKER}" command -v docker >/dev/null 2>&1; then
    test_pass "3a no docker on the run's PATH"
else
    test_fail "3a no docker on the run's PATH" "a docker is visible on ${NODOCKER}"
fi

test_start "3b without docker on PATH: the table still prints, every containers column is n/a, the suites run, rc=1 from c"
run_in "${FIX_N}" "${NODOCKER}"
timing_section
row_names
na_bad=''
for w in "${ROW_NAMES[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${got}" == 'n/a' ]] || na_bad+=" ${w}=${got:-none}"
done
if [[ "${OUT}" == *'SUITE TIMING'* && -z "${na_bad}" && "${OUT}" == *'Running: b.test.zsh'* && "${RC}" == 1 ]] \
    && (( ${#ROW_NAMES} == 5 )); then
    test_pass "3b table printed, containers n/a for all rows, the suites ran, rc=1"
else
    test_fail "3b without docker: table with n/a, suites run, rc=1" "rc=${RC} rows: ${ROW_NAMES[*]} not n/a:${na_bad} out: ${OUT[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case 4: docker events hangs: each row waits at most VDE_DOCKER_EVENTS_TIMEOUT, shows n/a, the exit code is unchanged
# ---------------------------------------------------------------------------

# The hang stub holds `docker events` for about 8 seconds (80 x 0.1s), so RED stays practical; create still works.
new_fixture events-hang || exit 1
typeset FIX_H="${SCRATCH}/events-hang"
print -l -- '#!/usr/bin/env zsh' \
    'zmodload zsh/datetime zsh/zselect' \
    'print -r -- "$*" >> "${DOCKER_LOG}"' \
    'case "$1" in' \
    '    create)' \
    '        print -r -- "${EPOCHREALTIME}" >> "${DOCKER_EVENTS}"' \
    '        exit 0 ;;' \
    '    events)' \
    '        typeset -i k' \
    '        for (( k = 0; k < 80; k++ )); do zselect -t 10; done' \
    '        exit 0 ;;' \
    'esac' \
    'exit 0' > "${FIX_H}/stubs/docker" || exit 1
chmod +x "${FIX_H}/stubs/docker"

zmodload zsh/datetime
test_start "4a: a hanging docker events is cut off at VDE_DOCKER_EVENTS_TIMEOUT=1: the run ends within 15s (unbounded it takes about 41s), containers n/a for every row, rc=1"
typeset -F T4_START="${EPOCHREALTIME}" T4_END=0 WALL=0
run_in "${FIX_H}" "${FIX_H}/stubs:${PATH}" VDE_DOCKER_EVENTS_TIMEOUT=1
T4_END="${EPOCHREALTIME}"
WALL=$(( T4_END - T4_START ))
timing_section
row_names
typeset na4=''
for w in "${ROW_NAMES[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${got}" == 'n/a' ]] || na4+=" ${w}=${got:-none}"
done
if (( WALL < 15 )) && [[ "${OUT}" == *'SUITE TIMING'* && "${RC}" == 1 && -z "${na4}" ]] && (( ${#ROW_NAMES} == 5 )); then
    test_pass "4a hung docker events: run took ${WALL}s, table printed, containers n/a for every row, rc=1"
else
    test_fail "4a hung docker events: run within 15s, table printed, n/a for every row, rc=1" "wall=${WALL}s rc=${RC} rows: ${ROW_NAMES[*]} not n/a:${na4} out: ${OUT[1,300]//$'\n'/ | }"
fi

# A PATH stub named timeout logs its arguments and execs the rest, so the duration the runner passes is visible.
test_start "4b the default run passes timeout the duration 10 before docker events"
new_fixture timeout-arg || exit 1
typeset FIX_TO="${SCRATCH}/timeout-arg" TDIR="${SCRATCH}/timeout-stub"
mkdir -p "${TDIR}" || exit 1
print -l -- '#!/usr/bin/env zsh' \
    'print -r -- "$*" >> "${TIMEOUT_LOG}"' \
    'shift' \
    'exec "$@"' > "${TDIR}/timeout" || exit 1
chmod +x "${TDIR}/timeout"
run_in "${FIX_TO}" "${TDIR}:${FIX_TO}/stubs:${PATH}" TIMEOUT_LOG="${FIX_TO}/timeout.log"
typeset TLOG=''
[[ -f "${FIX_TO}/timeout.log" ]] && TLOG="$(<"${FIX_TO}/timeout.log")"
if [[ "${TLOG}" =~ '(^|[[:space:]])10[[:space:]]' && "${TLOG}" == *'docker events'* ]]; then
    test_pass "4b timeout was called with 10 and docker events"
else
    test_fail "4b timeout called with duration 10 for docker events" "log: ${TLOG[1,300]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Case 5: a decimal-comma locale (LC_ALL=en_DK.utf8): the timing output keeps its dot and its sort stays numeric
# ---------------------------------------------------------------------------

typeset LOC_PROBE=''
LOC_PROBE="$(LC_ALL=en_DK.utf8 zsh -c 'printf "%.1f" 1.5' 2>/dev/null)"
if [[ "${LOC_PROBE}" != '1,5' ]]; then
    print -r -- "[SKIP] 5: no decimal-comma locale (en_DK.utf8) on this host; install the locales package and run locale-gen"
else
    new_fixture locale || exit 1
    typeset FIX_L="${SCRATCH}/locale"
    run_in "${FIX_L}" "${FIX_L}/stubs:${PATH}" LC_ALL=en_DK.utf8
    timing_section
    row_names

    test_start "5a under LC_ALL=en_DK.utf8 every SUITE TIMING row shows seconds with a dot and no comma appears in the section"
    if (( ${#ROW_NAMES} == 5 )) && [[ "${SECTION}" != *,* ]]; then
        test_pass "5a five rows with <n>.<d>s seconds and no comma in the table"
    else
        test_fail "5a every row has <n>.<d>s seconds (5 rows) and no comma in the table" "rows: ${ROW_NAMES[*]} section: ${SECTION[1,300]//$'\n'/ | }"
    fi

    test_start "5b under LC_ALL=en_DK.utf8 the first row is still b.test.zsh (the sort is numeric)"
    if [[ "${ROW_NAMES[1]:-}" == b.test.zsh ]]; then
        test_pass "5b the first row is b.test.zsh"
    else
        test_fail "5b the first row is b.test.zsh" "rows: ${ROW_NAMES[*]}"
    fi

    test_start "5c under LC_ALL=en_DK.utf8 the Total line shows a dot and a total of at least 0.9s"
    if [[ "${TOTAL_LINE}" =~ 'Total suite time: ([0-9]+\.[0-9])s' ]] && (( ${match[1]} >= 0.9 )); then
        test_pass "5c total line: ${TOTAL_LINE}"
    else
        test_fail "5c Total suite time with a dot and at least 0.9s" "line: ${TOTAL_LINE:-none}"
    fi

    test_start "5d under LC_ALL=en_DK.utf8 Running lines keep HH:MM:SS and result lines carry a dotted duration; no comma anywhere"
    typeset lbad='' ln5
    typeset -i nrun5=0
    for ln5 in "${(@f)OUT}"; do
        if [[ "${ln5}" == *'Running: '* ]]; then
            nrun5+=1
            [[ "${ln5}" =~ '[0-9][0-9]:[0-9][0-9]:[0-9][0-9]' && "${ln5}" != *,* ]] || lbad+=" ${ln5}"
        elif [[ "${ln5}" == *' passed ('* || "${ln5}" == *' failed ('* ]]; then
            [[ "${ln5}" =~ '\([0-9]+\.[0-9]s\)' && "${ln5}" != *,* ]] || lbad+=" ${ln5}"
        fi
    done
    if (( nrun5 == 4 )) && [[ -z "${lbad}" ]]; then
        test_pass "5d four Running lines with HH:MM:SS and dotted durations on every result line"
    else
        test_fail "5d Running lines with HH:MM:SS, result lines with (<n>.<d>s), no comma" "running lines: ${nrun5} bad:${lbad}"
    fi

    test_start "5e under LC_ALL=en_DK.utf8 the runner still exits 1 (suite c fails)"
    if [[ "${RC}" == 1 ]]; then
        test_pass "5e rc=1"
    else
        test_fail "5e the runner exits 1" "rc=${RC}"
    fi

    test_start "5f under LC_ALL=en_DK.utf8 a suite still sees the caller's LC_ALL (en_DK.utf8), never C"
    typeset -a SEEN5=()
    [[ -f "${FIX_L}/suite-a-locale-seen.txt" ]] && SEEN5=( "${(@f)$(<"${FIX_L}/suite-a-locale-seen.txt")}" )
    if [[ "${SEEN5[1]:-}" == en_DK.utf8 ]]; then
        test_pass "5f a.test.zsh saw LC_ALL=en_DK.utf8 (the caller's value)"
    else
        test_fail "5f a.test.zsh sees the caller's LC_ALL (en_DK.utf8)" "first line: ${SEEN5[1]:-none}"
    fi
fi

# ---------------------------------------------------------------------------
# Case 6: the containers query is one-shot, bounded, capped; failures and the timing file behave; static pins hold
# ---------------------------------------------------------------------------

typeset GATE_SRC="${ROOT}/githooks/gate-tree.zsh" LIB_SRC="${ROOT}/lib/vde-test-env"

test_start "6a with no timeout or gtimeout on PATH the runner never calls docker events, and every containers column is n/a"
new_fixture no-timeout || exit 1
typeset FIX_NT="${SCRATCH}/no-timeout" NOTO="${SCRATCH}/path-without-timeouts"
build_path_without_timeouts "${NOTO}" || exit 1
typeset nt_tools=''
PATH="${NOTO}" command -v timeout >/dev/null 2>&1 && nt_tools+=' timeout'
PATH="${NOTO}" command -v gtimeout >/dev/null 2>&1 && nt_tools+=' gtimeout'
run_in "${FIX_NT}" "${FIX_NT}/stubs:${NOTO}"
timing_section
row_names
typeset -a NT_LOG=()
typeset -i nt_events=0
typeset nt_line
[[ -f "${FIX_NT}/docker.log" ]] && NT_LOG=( "${(@f)$(<"${FIX_NT}/docker.log")}" )
for nt_line in "${NT_LOG[@]}"; do
    [[ "${nt_line}" == events* ]] && nt_events+=1
done
typeset na6=''
for w in "${ROW_NAMES[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${got}" == 'n/a' ]] || na6+=" ${w}=${got:-none}"
done
if [[ -z "${nt_tools}" ]] && (( nt_events == 0 )) && [[ -z "${na6}" ]] && (( ${#ROW_NAMES} == 5 )); then
    test_pass "6a no timeout on PATH: docker events never called, every row n/a"
else
    test_fail "6a no timeout on PATH: no docker events call, every row n/a" "timeout tools on PATH:${nt_tools:- none} events calls: ${nt_events} not n/a:${na6} rows: ${ROW_NAMES[*]}"
fi

test_start "6b VDE_DOCKER_EVENTS_TIMEOUT=0 falls back to 10: the runner calls timeout with 10 before docker events"
new_fixture timeout-zero || exit 1
typeset FIX_TZ="${SCRATCH}/timeout-zero"
run_in "${FIX_TZ}" "${TDIR}:${FIX_TZ}/stubs:${PATH}" VDE_DOCKER_EVENTS_TIMEOUT=0 TIMEOUT_LOG="${FIX_TZ}/timeout.log"
typeset TZLOG=''
[[ -f "${FIX_TZ}/timeout.log" ]] && TZLOG="$(<"${FIX_TZ}/timeout.log")"
if [[ "${TZLOG}" =~ '(^|[[:space:]])10[[:space:]]' && "${TZLOG}" == *'docker events'* ]]; then
    test_pass "6b timeout was called with 10 before docker events"
else
    test_fail "6b VDE_DOCKER_EVENTS_TIMEOUT=0 calls timeout with 10" "log: ${TZLOG[1,300]//$'\n'/ | }"
fi

test_start "6c a hanging docker events with VDE_DOCKER_EVENTS_TIMEOUT=1 is queried ONCE: exactly one events call, every row n/a, run well under 12s"
new_fixture events-once || exit 1
typeset FIX_EO="${SCRATCH}/events-once"
hang_docker_stub "${FIX_EO}" || exit 1
typeset -F EO_START="${EPOCHREALTIME}" EO_END=0 EO_WALL=0
run_in "${FIX_EO}" "${FIX_EO}/stubs:${PATH}" VDE_DOCKER_EVENTS_TIMEOUT=1
EO_END="${EPOCHREALTIME}"
EO_WALL=$(( EO_END - EO_START ))
timing_section
row_names
typeset -a EO_LOG=()
typeset -i eo_events=0
typeset eo_line
[[ -f "${FIX_EO}/docker.log" ]] && EO_LOG=( "${(@f)$(<"${FIX_EO}/docker.log")}" )
for eo_line in "${EO_LOG[@]}"; do
    [[ "${eo_line}" == events* ]] && eo_events+=1
done
na6=''
for w in "${ROW_NAMES[@]}"; do
    got="$(containers_of "$(row_of "${w}")")"
    [[ "${got}" == 'n/a' ]] || na6+=" ${w}=${got:-none}"
done
if (( eo_events == 1 )) && (( EO_WALL < 12 )) && [[ -z "${na6}" && "${RC}" == 1 ]] && (( ${#ROW_NAMES} == 5 )); then
    test_pass "6c one events call in the run, wall ${EO_WALL}s, every row n/a, rc=1"
else
    test_fail "6c one docker events call per run, every row n/a, run under 12s" "events calls: ${eo_events} wall=${EO_WALL}s rc=${RC} rows: ${ROW_NAMES[*]} not n/a:${na6}"
fi

test_start "6d a window with 256 creates shows 256+; a window with 255 shows 255"
new_fixture cap-256 || exit 1
typeset FIX_C2="${SCRATCH}/cap-256"
run_in "${FIX_C2}" "${FIX_C2}/stubs:${PATH}" B_EXTRA=254
timing_section
row_names
typeset got256="$(containers_of "$(row_of b.test.zsh)")"
new_fixture cap-255 || exit 1
typeset FIX_C3="${SCRATCH}/cap-255"
run_in "${FIX_C3}" "${FIX_C3}/stubs:${PATH}" B_EXTRA=253
timing_section
row_names
typeset got255="$(containers_of "$(row_of b.test.zsh)")"
if [[ "${got256}" == '256+' && "${got255}" == 255 ]]; then
    test_pass "6d 256 creates show 256+, 255 creates show 255"
else
    test_fail "6d cap: 256 creates show 256+ and 255 creates show 255" "256 window: ${got256:-none} 255 window: ${got255:-none}"
fi

test_start "6e a failing Sovereign Audit: the table prints with only a sovereign-audit row, the timing file gets that row, the runner exits non-zero"
new_fixture audit-fails || exit 1
typeset FIX_AF="${SCRATCH}/audit-fails"
print -l -- '#!/usr/bin/env zsh' 'exit 1' > "${FIX_AF}/bin/vde-enforce-uap.zsh" || exit 1
chmod +x "${FIX_AF}/bin/vde-enforce-uap.zsh"
run_in "${FIX_AF}" "${FIX_AF}/stubs:${PATH}" VDE_TEST_TIMING_FILE="${FIX_AF}/timing.txt"
timing_section
row_names
typeset af_file=''
[[ -f "${FIX_AF}/timing.txt" ]] && af_file="$(<"${FIX_AF}/timing.txt")"
if [[ "${RC}" != 0 && "${OUT}" == *'SUITE TIMING'* && "${OUT}" != *'Running: a.test.zsh'* ]] \
    && (( ${#ROW_NAMES} == 1 )) && [[ "${ROW_NAMES[1]:-}" == sovereign-audit && "${af_file}" == *sovereign-audit* ]]; then
    test_pass "6e audit failure: rc=${RC}, SUITE TIMING with a sovereign-audit row only, file has the row"
else
    test_fail "6e failing audit: non-zero rc, SUITE TIMING with only a sovereign-audit row, file has it" "rc=${RC} rows: ${ROW_NAMES[*]} file: ${af_file[1,200]//$'\n'/ | }"
fi

test_start "6f a VDE_TEST_TIMING_FILE in a directory that does not exist: exit 2 naming the path, and no suite runs"
new_fixture bad-path || exit 1
typeset FIX_BP="${SCRATCH}/bad-path" BADT="${SCRATCH}/no-such-dir/t.txt"
run_in "${FIX_BP}" "${FIX_BP}/stubs:${PATH}" VDE_TEST_TIMING_FILE="${BADT}"
if [[ "${RC}" == 2 && "${OUT}" == *"${BADT}"* && "${OUT}" != *'Running:'* && ! -e "${FIX_BP}/suite-a-locale-seen.txt" ]]; then
    test_pass "6f rc=2, error names the path, no suite ran"
else
    test_fail "6f unwritable timing path: rc 2, error naming the path, no suite run" "rc=${RC} suite a ran: $([[ -e "${FIX_BP}/suite-a-locale-seen.txt" ]] && echo yes || echo no) out: ${OUT[1,300]//$'\n'/ | }"
fi

test_start "6g two runners with the same VDE_TEST_TIMING_FILE, started together: the file holds exactly one run's rows, and no temp file is left"
CONC_DIR="${SCRATCH}/concurrent"
mkdir -p "${CONC_DIR}" || exit 1
typeset TF_CONC="${CONC_DIR}/timing.txt"
new_fixture conc-a || exit 1
typeset FIX_CA="${SCRATCH}/conc-a"
rm -f "${FIX_CA}/tests/unit/"*.test.zsh
slow_suite "${FIX_CA}/tests/unit/fa-one.test.zsh" && slow_suite "${FIX_CA}/tests/unit/fa-two.test.zsh" || exit 1
new_fixture conc-b || exit 1
typeset FIX_CB="${SCRATCH}/conc-b"
rm -f "${FIX_CB}/tests/unit/"*.test.zsh
slow_suite "${FIX_CB}/tests/unit/fb-one.test.zsh" && slow_suite "${FIX_CB}/tests/unit/fb-two.test.zsh" || exit 1
( run_in "${FIX_CA}" "${FIX_CA}/stubs:${PATH}" VDE_TEST_TIMING_FILE="${TF_CONC}" ) &
( run_in "${FIX_CB}" "${FIX_CB}/stubs:${PATH}" VDE_TEST_TIMING_FILE="${TF_CONC}" ) &
wait
typeset -a CONC_ROWS=() CONC_LEFT=()
typeset -i conc_a=0 conc_b=0
typeset conc_line
typeset -a cw
[[ -f "${TF_CONC}" ]] && CONC_ROWS=( "${(@f)$(<"${TF_CONC}")}" )
for conc_line in "${CONC_ROWS[@]}"; do
    cw=( ${(z)conc_line} )
    [[ "${cw[3]:-}" == fa-* ]] && conc_a+=1
    [[ "${cw[3]:-}" == fb-* ]] && conc_b+=1
done
CONC_LEFT=( "${CONC_DIR}"/*(DN) )
if (( ${#CONC_ROWS} == 4 )) && (( (conc_a == 2 && conc_b == 0) || (conc_a == 0 && conc_b == 2) )) \
    && (( ${#CONC_LEFT} == 1 )) && [[ "${CONC_LEFT[1]:-}" == "${TF_CONC}" ]]; then
    test_pass "6g one run's 4 rows (a=${conc_a} b=${conc_b}), no leftover files"
else
    test_fail "6g concurrent runners: exactly one run's rows and no temp files" "rows: ${#CONC_ROWS} fa-: ${conc_a} fb-: ${conc_b} dir: ${CONC_LEFT[*]:t}"
fi

test_start "6h durations come from vde_test_now (runner and gate-tree): no EPOCHREALTIME subtraction, no \$SECONDS for a duration, no comment calls \$SECONDS monotonic; lib defines vde_test_now"
typeset f7_bad='' static_f code_lines
for static_f in "${RUNNER_SRC}" "${GATE_SRC}"; do
    grep -qE 'EPOCHREALTIME *-|- *EPOCHREALTIME' "${static_f}" && f7_bad+=" ${static_f:t}:subtracts-EPOCHREALTIME"
    grep -qE 'vde_test_now' "${static_f}" || f7_bad+=" ${static_f:t}:no-vde_test_now-call"
    code_lines="$(grep -vE '^[[:space:]]*#' "${static_f}")"
    print -r -- "${code_lines}" | grep -qE '\$\{?SECONDS|typeset -F SECONDS' && f7_bad+=" ${static_f:t}:SECONDS-for-duration"
    grep -qiE '#.*SECONDS.*monoton|#.*monoton.*SECONDS' "${static_f}" && f7_bad+=" ${static_f:t}:comment-calls-SECONDS-monotonic"
done
grep -qE '^vde_test_now\(\)|^function vde_test_now' "${LIB_SRC}" || f7_bad+=" lib:no-vde_test_now-definition"
if [[ -z "${f7_bad}" ]]; then
    test_pass "6h durations use vde_test_now; no EPOCHREALTIME subtraction, no SECONDS for a duration"
else
    test_fail "6h durations from vde_test_now, never from EPOCHREALTIME subtraction or SECONDS" "${f7_bad}"
fi

test_start "6i no printf '%.1f' in the runner or gate-tree; lib/vde-test-env defines vde_test_fmt1, and both files call it"
typeset f12_bad=''
for static_f in "${RUNNER_SRC}" "${GATE_SRC}"; do
    grep -qF "printf '%.1f'" "${static_f}" && f12_bad+=" ${static_f:t}:has-printf-%.1f"
    grep -qE 'vde_test_fmt1 ' "${static_f}" || f12_bad+=" ${static_f:t}:no-vde_test_fmt1-call"
done
grep -qE '^vde_test_fmt1\(\)|^function vde_test_fmt1' "${LIB_SRC}" || f12_bad+=" lib:no-vde_test_fmt1-definition"
if [[ -z "${f12_bad}" ]]; then
    test_pass "6i one shared formatter: no printf '%.1f' in the two files, defined in lib, called by both"
else
    test_fail "6i one shared formatter (vde_test_fmt1) in lib/vde-test-env, no printf '%.1f' in the runner or gate-tree" "${f12_bad}"
fi

if ! command -v cc >/dev/null 2>&1; then
    print -r -- "[SKIP] 6j: no C compiler; cannot simulate a wall-clock jump"
else
    test_start "6j behavioural: with CLOCK_REALTIME and gettimeofday jumped +3600s mid-run (LD_PRELOAD shim), every row and the Total stay under 10s, b takes at least 0.9s, and the runner exits 0"
    typeset SHIM_DIR="${SCRATCH}/clk-shim" SHIM_SO cc_out=''
    mkdir -p "${SHIM_DIR}" || exit 1
    SHIM_SO="${SHIM_DIR}/jump.so"
    cat > "${SHIM_DIR}/jump.c" <<'EOF'
#define _GNU_SOURCE
#include <dlfcn.h>
#include <time.h>
#include <sys/time.h>
/* After the first call, every wall-clock read (CLOCK_REALTIME, gettimeofday, time) is shifted +3600 s. CLOCK_MONOTONIC is left alone. */
static int calls = 0;
int clock_gettime(clockid_t id, struct timespec *ts) {
    int (*real)(clockid_t, struct timespec *) = dlsym(RTLD_NEXT, "clock_gettime");
    int r = real(id, ts);
    if (id == CLOCK_REALTIME && ++calls > 3) ts->tv_sec += 3600;
    return r;
}
int gettimeofday(struct timeval *tv, void *tz) {
    int (*real)(struct timeval *, void *) = dlsym(RTLD_NEXT, "gettimeofday");
    int r = real(tv, tz);
    if (tv && ++calls > 3) tv->tv_sec += 3600;
    return r;
}
EOF
    if ! cc_out="$(cc -shared -fPIC -o "${SHIM_SO}" "${SHIM_DIR}/jump.c" -ldl 2>&1)"; then
        test_fail "6j compile the wall-clock shim" "cc: ${cc_out[1,300]//$'\n'/ | }"
    else
        # Canary: prove the shim really moves the wall clock in a process started the way the runner starts its
        # children (env -i, LD_PRELOAD). Without this the check below could pass vacuously if the shim stopped working.
        typeset canary_jump
        canary_jump="$(env -i HOME="${SCRATCH}" PATH="${PATH}" LD_PRELOAD="${SHIM_SO}" zsh -c 'zmodload zsh/datetime; typeset -F a=${EPOCHREALTIME}; typeset -F b=${EPOCHREALTIME}; typeset -F c=${EPOCHREALTIME}; typeset -F d=${EPOCHREALTIME}; print -r -- $(( d - a ))' 2>&1)"
        if [[ "${canary_jump}" =~ '^[0-9]+(\.[0-9]+)?$' ]] && (( canary_jump > 3000 )); then
            test_pass "6j canary: the shim jumps the wall clock (${canary_jump}s) in an env -i child"
        else
            test_fail "6j canary: the shim must jump the wall clock in an env -i child" "measured: [${canary_jump}]"
        fi
        new_fixture clk-jump || exit 1
        typeset FIX_J="${SCRATCH}/clk-jump"
        rm -f "${FIX_J}/tests/unit/"*.test.zsh
        print -l -- '#!/usr/bin/env zsh' 'zmodload zsh/zselect' 'zselect -t 100' 'exit 0' > "${FIX_J}/tests/unit/b.test.zsh" \
            && chmod +x "${FIX_J}/tests/unit/b.test.zsh" || exit 1
        run_in "${FIX_J}" "${FIX_J}/stubs:${PATH}" LD_PRELOAD="${SHIM_SO}"
        timing_section
        row_names
        typeset j_bad='' j_secs j_row j_total='' j_b=''
        for j_row in "${ROW_NAMES[@]}"; do
            j_secs="$(secs_of "$(row_of "${j_row}")")"
            [[ -n "${j_secs}" ]] && (( j_secs < 10 )) || j_bad+=" ${j_row}=${j_secs:-none}"
        done
        [[ "${TOTAL_LINE}" =~ 'Total suite time: ([0-9]+\.[0-9])s' ]] && j_total="${match[1]}"
        j_b="$(secs_of "$(row_of b.test.zsh)")"
        if [[ -z "${j_bad}" ]] && (( ${#ROW_NAMES} == 3 )) && [[ -n "${j_total}" ]] && (( j_total < 10 )) \
            && [[ -n "${j_b}" ]] && (( j_b >= 0.9 )) && [[ "${RC}" == 0 ]]; then
            test_pass "6j under the +3600s jump: rows under 10s (b=${j_b}s), total ${j_total}s, rc=0"
        else
            test_fail "6j under the +3600s jump: every row and the total under 10s, b at least 0.9s, rc=0" "rows: ${ROW_NAMES[*]} over-10s:${j_bad} total: ${j_total:-none} b: ${j_b:-none} rc=${RC} out: ${OUT[1,300]//$'\n'/ | }"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Case 7: the default is parallel-aware: with VDE_TEST_JOBS=2 a suite's containers cell is n/a and a "Unit phase:" line is printed
# ---------------------------------------------------------------------------

test_start "7a with VDE_TEST_JOBS=2 the containers cell of a fixture suite is n/a (not a number) and the output has a line starting 'Unit phase:'"
new_fixture parallel || exit 1
typeset FIX_P="${SCRATCH}/parallel"
run_in "${FIX_P}" "${FIX_P}/stubs:${PATH}" VDE_TEST_JOBS=2
timing_section
row_names
typeset p_cell="$(containers_of "$(row_of b.test.zsh)")"
typeset p_phase="$(line_matching '^Unit phase:')"
if [[ "${p_cell}" == 'n/a' && -n "${p_phase}" ]]; then
    test_pass "7a containers n/a for b.test.zsh and phase line: ${p_phase}"
else
    test_fail "7a VDE_TEST_JOBS=2: containers n/a for b.test.zsh and a 'Unit phase:' line" "containers=${p_cell:-none} phase line: ${p_phase:-none}"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
