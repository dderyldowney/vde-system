#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: the parallel unit phase of the Sovereign runner (Signet #774, step 2).
#
# The runner runs unit suites VDE_TEST_JOBS at a time (the tested maximum is 4), keeps the suites named in
# tests/serial-unit-suites.txt out of the pool, and gives every parallel suite its own HOME.
#
# This file runs a copy of the real runner in a stub fixture (stub audit, stub integration suite, stub docker on
# PATH, no containers, no network). Fixture suites share a state directory (RP_STATE) through the environment.
# Concurrency is observed with marker files: each suite writes a running marker while it runs and records, in
# max.<suite>, how many markers it saw. Every wait is a bounded poll (zselect, 50 ms apart, at most 200 polls, so
# a 10 s cap); no check depends on a clock, and a missing feature makes a poll expire, so the run never hangs.
#
# Until the parallel runner lands, the checks for the parallel contract FAIL (RED); see each case for what the
# serial runner already satisfies.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_TEST_JOBS VDE_TEST_TIMING_FILE VDE_DOCKER_EVENTS_TIMEOUT VDE_POL_STAMP_TTL

zmodload zsh/zselect

typeset ROOT="${0:A:h:h:h}"
typeset RUNNER_SRC="${ROOT}/tests/run-sovereign-tests.zsh"
typeset LIBENV_SRC="${ROOT}/lib/vde-test-env"
typeset -g OUT='' RC=0 BLOCK='' INDEX=0 OBSMAX=0 MAXFILES=0
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
SCRATCH="$(mktemp -d "${SCRATCH}/runner-parallel.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

poll_for() {  # poll_for POLLS COMMAND...: runs the command at most POLLS times, 50 ms apart; status 0 once it succeeds, 1 at the cap
    typeset -i n polls="$1"
    shift
    for (( n = 0; n < polls; n++ )); do
        "$@" && return 0
        zselect -t 5
    done
    return 1
}

poll_until() {  # poll_until COMMAND...: poll_for with the 10 s cap (200 polls)
    poll_for 200 "$@"
}

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

barrier_suite() {  # barrier_suite FILE: prints 40 lines tagged with its own name, then waits for RP_NEED suites to run at once.
    # A suite keeps its running marker until RP_NEED suites have ARRIVED (seen RP_NEED markers at once), so an early
    # finisher can never hide the overlap from a late one. At most RP_POLLS polls per wait. Records the most markers it
    # saw in max.<suite>. With RP_NEED unset it needs no company and passes at once.
    write_suite "$1" <<'EOF'
#!/usr/bin/env zsh
# runner-parallel fixture: barrier suite
zmodload zsh/zselect
typeset me="${0:t}" st="${RP_STATE}" n k
typeset -i need="${RP_NEED:-0}" polls="${RP_POLLS:-200}" maxseen=0 arrived_n=0
typeset -a live arrived
for (( k = 1; k <= 40; k++ )); do print -r -- "${me} line ${k}"; done
: > "${st}/running.${me}"
for (( n = 0; n <= polls; n++ )); do
    live=( "${st}"/running.*(N) )
    (( ${#live} > maxseen )) && maxseen=${#live}
    (( maxseen >= need )) && break
    (( n < polls )) && zselect -t 5
done
if (( maxseen >= need && need > 0 )); then
    : > "${st}/arrived.${me}"
    for (( n = 0; n <= polls; n++ )); do
        arrived=( "${st}"/arrived.*(N) )
        arrived_n=${#arrived}
        (( arrived_n >= need )) && break
        (( n < polls )) && zselect -t 5
    done
fi
print -r -- "${maxseen}" > "${st}/max.${me}"
rm -f -- "${st}/running.${me}"
(( maxseen >= need && arrived_n >= need )) && exit 0
(( need == 0 )) && exit 0
exit 1
EOF
}

rendezvous_suite() {  # rendezvous_suite FILE PEER: announces itself with a ready file, passes only once PEER has announced too (10 s cap)
    {
        print -r -- '#!/usr/bin/env zsh'
        print -r -- "typeset -g peer=${(q)2}"
        cat <<'EOF'
zmodload zsh/zselect
typeset -i n
: > "${RP_STATE}/ready.${0:t}"
for (( n = 0; n < 200; n++ )); do
    [[ -e "${RP_STATE}/ready.${peer}" ]] && exit 0
    zselect -t 5
done
exit 1
EOF
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

index_of() {  # index_of TEXT -> INDEX: the number of the first line of OUT containing TEXT literally (0 if none)
    local line
    local -i k=0
    INDEX=0
    for line in "${(@f)OUT}"; do
        k+=1
        if [[ "${line}" == *"$1"* ]]; then INDEX=${k}; return 0; fi
    done
}

block_of() {  # block_of NAME -> BLOCK: the lines of OUT from the "Running: NAME" header through the NAME result line
    local line
    local -i on=0
    BLOCK=''
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *"Running: $1"* ]] && on=1
        (( on )) && BLOCK+="${line}"$'\n'
        if (( on )) && [[ "${line}" == *"$1 passed ("* || "${line}" == *"$1 failed ("* ]]; then break; fi
    done
}

count_in_block() {  # count_in_block TEXT -> the number of lines of BLOCK containing TEXT literally
    local line
    local -i c=0
    for line in "${(@f)BLOCK}"; do
        [[ "${line}" == *"$1"* ]] && c+=1
    done
    print -r -- "${c}"
}

table_cell() {  # table_cell NAME -> the containers cell (last field) of NAME's SUITE TIMING row, or "none"
    local line
    local -a w
    local -i on=0
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *'SUITE TIMING'* ]] && on=1
        (( on )) || continue
        w=( ${(z)line} )
        if [[ "${w[1]:-}" == "$1" ]]; then print -r -- "${w[-1]}"; return 0; fi
    done
    print -r -- none
}

observed_max() {  # observed_max STATEDIR -> OBSMAX: the largest value in any max.<suite> file there (0 if none); MAXFILES: how many such files
    local f
    local -a files=( "$1"/max.*(N) )
    local -i m=0 v
    for f in "${files[@]}"; do
        v="$(<"${f}")"
        (( v > m )) && m=${v}
    done
    OBSMAX=${m}
    MAXFILES=${#files}
}

# ---------------------------------------------------------------------------
# P1: two rendezvous suites with VDE_TEST_JOBS=2 both pass (they overlapped)
# ---------------------------------------------------------------------------

test_start "P1 two rendezvous suites with VDE_TEST_JOBS=2 both pass (they overlapped)"
new_fixture p1 || exit 1
typeset FIX1="${SCRATCH}/p1"
rendezvous_suite "${FIX1}/tests/unit/r-a.test.zsh" r-b.test.zsh || exit 1
rendezvous_suite "${FIX1}/tests/unit/r-b.test.zsh" r-a.test.zsh || exit 1
run_par "${FIX1}" VDE_TEST_JOBS=2
if [[ "${RC}" == 0 ]] && has_line 'r-a.test.zsh passed (' && has_line 'r-b.test.zsh passed ('; then
    test_pass "P1 both rendezvous suites passed, rc=0"
else
    test_fail "P1 rendezvous suites overlap and both pass" "rc=${RC} (a rendezvous that never overlaps waits out its 10 s cap and fails)"
fi

# ---------------------------------------------------------------------------
# P2: VDE_TEST_JOBS=1 is the serial behaviour: the observed maximum concurrency is 1
# ---------------------------------------------------------------------------

test_start "P2 with VDE_TEST_JOBS=1 the observed maximum concurrency is 1 (two marker suites)"
new_fixture p2 || exit 1
typeset FIX2="${SCRATCH}/p2"
barrier_suite "${FIX2}/tests/unit/m-a.test.zsh" || exit 1
barrier_suite "${FIX2}/tests/unit/m-b.test.zsh" || exit 1
run_par "${FIX2}" VDE_TEST_JOBS=1
observed_max "${FIX2}/state"
if [[ "${RC}" == 0 ]] && (( MAXFILES == 2 && OBSMAX == 1 )); then
    test_pass "P2 two suites ran, observed maximum concurrency 1"
else
    test_fail "P2 VDE_TEST_JOBS=1: observed maximum 1" "rc=${RC} files=${MAXFILES} max=${OBSMAX}"
fi

# ---------------------------------------------------------------------------
# P3: VDE_TEST_JOBS=9 prints the clamp line and never runs more than 4 at once (six barrier suites: 4 is reached)
# ---------------------------------------------------------------------------

test_start "P3 VDE_TEST_JOBS=9 prints the clamp line and the observed maximum is 4 (never above 4)"
new_fixture p3 || exit 1
typeset FIX3="${SCRATCH}/p3"
typeset p3n
for p3n in 1 2 3 4 5 6; do
    barrier_suite "${FIX3}/tests/unit/s-${p3n}.test.zsh" || exit 1
done
# The suites' exit status is not checked here: the two that start after the first four have drained never see four.
run_par "${FIX3}" VDE_TEST_JOBS=9 RP_NEED=4 RP_POLLS=100
observed_max "${FIX3}/state"
if has_line 'VDE_TEST_JOBS=9 exceeds the tested maximum 4; using 4' && (( OBSMAX == 4 && MAXFILES == 6 )); then
    test_pass "P3 clamp line printed, observed maximum 4 across 6 suites"
else
    test_fail "P3 clamp line and observed maximum 4" "clamp line: $(has_line 'exceeds the tested maximum' && print yes || print no) max=${OBSMAX} files=${MAXFILES} rc=${RC}"
fi

# ---------------------------------------------------------------------------
# P4: VDE_TEST_JOBS values that are not a whole number from 1 to 4 exit 2 before any suite runs
# ---------------------------------------------------------------------------

test_start "P4 VDE_TEST_JOBS=0, abc, -1, 2.5 and the empty string each exit 2 with the error line, and no suite ran"
typeset -a BAD_JOBS=( 0 abc -1 2.5 '' )
typeset -i i4=0
typeset bad4='' jv FIX4
for jv in "${BAD_JOBS[@]}"; do
    i4+=1
    new_fixture "p4-${i4}" || exit 1
    FIX4="${SCRATCH}/p4-${i4}"
    barrier_suite "${FIX4}/tests/unit/m-a.test.zsh" || exit 1
    run_par "${FIX4}" "VDE_TEST_JOBS=${jv}"
    observed_max "${FIX4}/state"
    if [[ "${RC}" != 2 ]] || ! has_line 'ERROR: VDE_TEST_JOBS must be a whole number from 1 to 4' || (( MAXFILES > 0 )); then
        bad4+=" [${jv:-empty}] rc=${RC} suites-ran=${MAXFILES}"
    fi
done
if [[ -z "${bad4}" ]]; then
    test_pass "P4 all five bad values exit 2 with the error line; no suite ran"
else
    test_fail "P4 bad VDE_TEST_JOBS exits 2 with the error line before any suite runs" "failing values:${bad4}"
fi

# ---------------------------------------------------------------------------
# P5: a suite listed in tests/serial-unit-suites.txt never overlaps another suite and runs after the pool drains
# ---------------------------------------------------------------------------

test_start "P5 a suite listed in tests/serial-unit-suites.txt never overlaps another suite (max 1) and runs after the others"
new_fixture p5 || exit 1
typeset FIX5="${SCRATCH}/p5"
barrier_suite "${FIX5}/tests/unit/a-serial.test.zsh" || exit 1
barrier_suite "${FIX5}/tests/unit/p1.test.zsh" || exit 1
barrier_suite "${FIX5}/tests/unit/p2.test.zsh" || exit 1
print -l -- '# Serial unit suites (fixture)' 'a-serial.test.zsh shares a resource with the others in this fixture' \
    > "${FIX5}/tests/serial-unit-suites.txt" || exit 1
run_par "${FIX5}" VDE_TEST_JOBS=3
typeset -i serial_max=0 serial_at=0 p1_done=0 p2_done=0
[[ -f "${FIX5}/state/max.a-serial.test.zsh" ]] && serial_max="$(<"${FIX5}/state/max.a-serial.test.zsh")"
index_of 'Running: a-serial.test.zsh'; serial_at=${INDEX}
index_of 'p1.test.zsh passed ('; p1_done=${INDEX}
index_of 'p2.test.zsh passed ('; p2_done=${INDEX}
if [[ "${RC}" == 0 ]] && (( serial_max == 1 && serial_at > 0 && serial_at > p1_done && serial_at > p2_done )); then
    test_pass "P5 serial suite saw max 1 and ran after the pool drained"
else
    test_fail "P5 serial suite: max 1, runs after the pool drained" "rc=${RC} serial max=${serial_max} header line=${serial_at} p1 line=${p1_done} p2 line=${p2_done}"
fi

# ---------------------------------------------------------------------------
# P6: serial list validation: each bad line exits 1 naming the problem; nothing runs
# ---------------------------------------------------------------------------

test_start "P6 serial list validation: no reason, stale name, duplicate, path, wrong extension, also-excluded each exit 1 naming the problem, nothing ran"
typeset -a S6_LINE=(
    'p1.test.zsh'
    'nope.test.zsh has a reason'
    $'p1.test.zsh first\np1.test.zsh second'
    'unit/p1.test.zsh a reason'
    'p1.sh a reason'
    'p1.test.zsh a reason'
)
typeset -a S6_TOKEN=( p1.test.zsh nope.test.zsh p1.test.zsh p1.test.zsh p1.sh p1.test.zsh )
typeset -a S6_EXCL=( '' '' '' '' '' 'p1.test.zsh already excluded in tests/ci-unit-exclusions.txt' )
typeset -i i6
typeset bad6=''
typeset F6
for (( i6 = 1; i6 <= ${#S6_LINE}; i6++ )); do
    new_fixture "s6-${i6}" || exit 1
    F6="${SCRATCH}/s6-${i6}"
    barrier_suite "${F6}/tests/unit/p1.test.zsh" || exit 1
    barrier_suite "${F6}/tests/unit/p2.test.zsh" || exit 1
    print -l -- '# Serial unit suites (fixture)' "${S6_LINE[i6]}" > "${F6}/tests/serial-unit-suites.txt" || exit 1
    if [[ -n "${S6_EXCL[i6]}" ]]; then
        print -r -- "${S6_EXCL[i6]}" > "${F6}/tests/ci-unit-exclusions.txt" || exit 1
    fi
    run_par "${F6}" VDE_TEST_JOBS=2
    observed_max "${F6}/state"
    if [[ "${RC}" != 1 ]] || ! has_line "${S6_TOKEN[i6]}" || (( MAXFILES > 0 )); then
        bad6+=" [${S6_TOKEN[i6]}] rc=${RC} suites-ran=${MAXFILES}"
    fi
done
if [[ -z "${bad6}" ]]; then
    test_pass "P6 all six bad serial lists exit 1 naming the problem; nothing ran"
else
    test_fail "P6 bad serial list exits 1 naming the problem, before anything runs" "failing cases:${bad6}"
fi

# ---------------------------------------------------------------------------
# P7: a failing parallel suite: exit 1, its text inside its block, named in the FAIL summary, passing suites counted
# ---------------------------------------------------------------------------

test_start "P7 a failing parallel suite: exit 1, its output inside its block, named in the FAIL summary, passing suites still counted"
new_fixture p7 || exit 1
typeset FIX7="${SCRATCH}/p7"
write_suite "${FIX7}/tests/unit/f-ok.test.zsh" <<'EOF'
#!/usr/bin/env zsh
print -r -- 'OK-TEXT f-ok'
exit 0
EOF
write_suite "${FIX7}/tests/unit/f-bad.test.zsh" <<'EOF'
#!/usr/bin/env zsh
print -r -- 'BAD-TEXT f-bad'
exit 1
EOF
run_par "${FIX7}" VDE_TEST_JOBS=2
block_of f-bad.test.zsh
# Passing suites counted: f-ok, the stub integration suite and the BDD metadata check make Passed: 3.
if [[ "${RC}" == 1 ]] && [[ "${BLOCK}" == *'BAD-TEXT f-bad'* ]] && [[ "${OUT}" == *'Failed Suites:'*'f-bad.test.zsh'* ]] \
    && has_line 'FAIL: 1 test suites failed' && has_line 'Passed: 3'; then
    test_pass "P7 rc=1, f-bad output in its block, named in the FAIL summary, Passed: 3"
else
    test_fail "P7 failing suite: rc 1, output in its block, FAIL summary names it, Passed: 3" "rc=${RC} block: ${BLOCK[1,160]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# P8: blocks are not interleaved: each suite's block carries only its own 40 lines (three barrier suites overlap)
# ---------------------------------------------------------------------------

test_start "P8 blocks are not interleaved: each suite's block has its own 40 lines and no other suite's line (three suites overlap)"
new_fixture p8 || exit 1
typeset FIX8="${SCRATCH}/p8"
barrier_suite "${FIX8}/tests/unit/h-alpha.test.zsh" || exit 1
barrier_suite "${FIX8}/tests/unit/h-bravo.test.zsh" || exit 1
barrier_suite "${FIX8}/tests/unit/h-charlie.test.zsh" || exit 1
run_par "${FIX8}" VDE_TEST_JOBS=3 RP_NEED=3
typeset p8bad='' p8n p8o
typeset -i p8own=0 p8other=0
typeset -a P8_NAMES=( h-alpha h-bravo h-charlie )
for p8n in "${P8_NAMES[@]}"; do
    block_of "${p8n}.test.zsh"
    p8own="$(count_in_block "${p8n}.test.zsh line ")"
    p8other=0
    for p8o in "${P8_NAMES[@]}"; do
        [[ "${p8o}" == "${p8n}" ]] && continue
        p8other+=$(count_in_block "${p8o}.test.zsh")
    done
    if (( p8own != 40 || p8other != 0 )) || [[ "${BLOCK}" != *'passed ('* ]]; then
        p8bad+=" ${p8n}(own=${p8own} foreign=${p8other})"
    fi
done
if [[ "${RC}" == 0 && -z "${p8bad}" ]]; then
    test_pass "P8 three blocks, each with its own 40 lines, no foreign lines, all passed"
else
    test_fail "P8 blocks not interleaved: 40 own lines, no foreign line, each passed" "rc=${RC} problems:${p8bad}"
fi

# ---------------------------------------------------------------------------
# P9: each parallel suite has its own HOME: all differ, none is the caller's HOME
# ---------------------------------------------------------------------------

test_start "P9 each parallel suite has its own HOME: three distinct values, none equal to the caller's HOME"
new_fixture p9 || exit 1
typeset FIX9="${SCRATCH}/p9"
typeset p9n
for p9n in h9-a h9-b h9-c; do
    write_suite "${FIX9}/tests/unit/${p9n}.test.zsh" <<'EOF'
#!/usr/bin/env zsh
print -r -- "HOME-OF ${0:t} ${HOME}"
exit 0
EOF
done
run_par "${FIX9}" VDE_TEST_JOBS=3
typeset -A HOMES=()
typeset ln9
for ln9 in "${(@f)OUT}"; do
    if [[ "${ln9}" =~ 'HOME-OF (h9-[abc]\.test\.zsh) (.+)$' ]]; then
        HOMES[${match[1]}]="${match[2]}"
    fi
done
typeset -a p9vals=( ${(u)HOMES[@]} )
if [[ "${RC}" == 0 ]] && (( ${#HOMES[@]} == 3 && ${#p9vals} == 3 )) \
    && [[ "${p9vals[*]}" != *"${FIX9}/callerhome"* ]]; then
    test_pass "P9 three suites, three distinct HOME values, none the caller's"
else
    test_fail "P9 own HOME per parallel suite" "rc=${RC} suites reporting: ${#HOMES[@]} distinct: ${#p9vals} values: ${(j: :)HOMES[@]}"
fi

# ---------------------------------------------------------------------------
# P10: the Unit phase line carries the job count, and the containers cell of parallel suites is n/a
# ---------------------------------------------------------------------------

test_start "P10 the Unit phase line reads 3 suites, 3 at a time, and the containers cell of each parallel suite is n/a"
new_fixture p10 || exit 1
typeset FIX10="${SCRATCH}/p10"
typeset p10n
for p10n in h10-a h10-b h10-c; do
    write_suite "${FIX10}/tests/unit/${p10n}.test.zsh" <<'EOF'
#!/usr/bin/env zsh
exit 0
EOF
done
run_par "${FIX10}" VDE_TEST_JOBS=3
typeset p10phase='' p10line ph_re
ph_re='Unit phase: 3 suites, 3 at a time, [0-9]+\.[0-9]+s wall \([0-9]+\.[0-9]+s of suite time\), containers created during the phase: (n/a|[0-9]+|256\+)$'
for p10line in "${(@f)OUT}"; do
    [[ "${p10line}" =~ ${ph_re} ]] && p10phase="${p10line}"
done
typeset p10cells='' p10c
for p10n in h10-a.test.zsh h10-b.test.zsh h10-c.test.zsh; do
    p10c="$(table_cell "${p10n}")"
    [[ "${p10c}" == n/a ]] || p10cells+=" ${p10n}=${p10c}"
done
if [[ "${RC}" == 0 && -n "${p10phase}" && -z "${p10cells}" ]]; then
    test_pass "P10 Unit phase line present (3 suites, 3 at a time); containers n/a for the three suites"
else
    test_fail "P10 Unit phase line with 3 suites at 3 a time, containers n/a for parallel suites" "rc=${RC} phase line: ${p10phase:-none} containers not n/a:${p10cells:- none}"
fi

# ---------------------------------------------------------------------------
# P11: a worker killed mid-run counts as a failed suite and the run exits 1
# ---------------------------------------------------------------------------

test_start "P11 a worker that kills itself (kill -9) counts as a failed suite, the run exits 1, and the other suite still passes"
new_fixture p11 || exit 1
typeset FIX11="${SCRATCH}/p11"
write_suite "${FIX11}/tests/unit/k-die.test.zsh" <<'EOF'
#!/usr/bin/env zsh
kill -9 $$
exit 0
EOF
write_suite "${FIX11}/tests/unit/k-ok.test.zsh" <<'EOF'
#!/usr/bin/env zsh
print -r -- 'K-OK'
exit 0
EOF
run_par "${FIX11}" VDE_TEST_JOBS=2
if [[ "${RC}" == 1 ]] && has_line 'k-die.test.zsh failed (' && has_line 'k-ok.test.zsh passed (' \
    && [[ "${OUT}" == *'Failed Suites:'*'k-die.test.zsh'* ]]; then
    test_pass "P11 killed worker counted failed, rc=1, the other suite passed"
else
    test_fail "P11 killed worker is a failed suite, rc=1" "rc=${RC} k-die line: $(has_line 'k-die.test.zsh failed (' && print yes || print no)"
fi

# ---------------------------------------------------------------------------
# P12: interrupt: TERM to the runner while two suites wait; afterwards no worker survives and the runner scratch is gone
# ---------------------------------------------------------------------------

test_start "P12 TERM to the runner while two suites wait: no worker process survives and the runner scratch is removed"
new_fixture p12 || exit 1
typeset FIX12="${SCRATCH}/p12"
typeset w12
for w12 in w-one w-two; do
    write_suite "${FIX12}/tests/unit/${w12}.test.zsh" <<'EOF'
#!/usr/bin/env zsh
# runner-parallel fixture: a suite that records its pid and waits for a release file that never comes (10 s cap)
zmodload zsh/zselect
typeset -i n
print -r -- "$$" > "${RP_STATE}/pid.${0:t}"
for (( n = 0; n < 200; n++ )); do
    [[ -e "${RP_STATE}/release" ]] && exit 0
    zselect -t 5
done
exit 0
EOF
done
typeset -i RUNNER_PID=0
env -i HOME="${FIX12}/callerhome" PATH="${FIX12}/stubs:${PATH}" TMPDIR="${FIX12}/tmproot" \
    RP_STATE="${FIX12}/state" FIXTURE_CALLER_HOME="${FIX12}/callerhome" VDE_TEST_JOBS=2 \
    zsh "${FIX12}/tests/run-sovereign-tests.zsh" > "${FIX12}/p12.log" 2>&1 &
RUNNER_PID=$!
both_started() { [[ -s "${FIX12}/state/pid.w-one.test.zsh" && -s "${FIX12}/state/pid.w-two.test.zsh" ]] }
runner_gone() { ! kill -0 "${RUNNER_PID}" 2>/dev/null }
# Both workers start within milliseconds on a parallel runner. The wait is 5 s (100 polls), shorter than the workers'
# own 10 s cap, so a runner that starts them one after another is decided here, while both are still waiting.
poll_for 100 both_started
typeset p12started=0
both_started && p12started=1
kill -TERM "${RUNNER_PID}" 2>/dev/null
poll_until runner_gone
typeset p12gone=0
runner_gone && p12gone=1
if (( ! p12gone )); then
    kill -9 "${RUNNER_PID}" 2>/dev/null
fi
wait "${RUNNER_PID}" 2>/dev/null
typeset -a p12alive=()
typeset p12f p12pid
for p12f in "${FIX12}/state"/pid.*(N); do
    p12pid="$(<"${p12f}")"
    if kill -0 "${p12pid}" 2>/dev/null; then
        p12alive+=( "${p12f:t}" )
        kill -9 "${p12pid}" 2>/dev/null
    fi
done
typeset -a p12left=( "${FIX12}/tmproot"/*(DN) )
if (( p12started && p12gone && ${#p12alive} == 0 && ${#p12left} == 0 )); then
    test_pass "P12 both workers started, the runner exited on TERM, no worker alive, runner scratch removed"
else
    test_fail "P12 TERM: both workers started, runner exits, no worker alive, scratch removed" \
        "both started=${p12started} runner gone=${p12gone} workers alive: ${(j: :)p12alive} scratch entries left: ${#p12left}"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
