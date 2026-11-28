#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Wiring test for Signet #778: the testing policy is ONE source of truth. The policy
# section in docs/development/testing.md, its numbers in tests/test-policy.conf, the agent
# rule, the sub-agent preamble and every pointer to them must exist, must agree with each
# other, and must match the tooling defaults.
#
# Read-only: it inspects tracked files with git and grep and never writes anywhere.
# A missing file is a FAIL with a message, never a crash.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="${0:A:h:h:h}"
fi

typeset -i TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; (( ++TESTS_PASSED )); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; (( ++TESTS_FAILED )); }

typeset -r DOC='docs/development/testing.md'
typeset -r CONF_FILE='tests/test-policy.conf'
typeset -r RULE='.gemini/RULES/testing.md'
typeset -r PREAMBLE='.gemini/RULES/testing-preamble.md'
typeset -r POLICY_HEADING='## Testing Policy (binding)'
typeset -r GATE_HEADING='## 1. THE SUPREME GATE'
typeset -r NUMBERS_HEADING='### Policy numbers'
typeset -r LAYERS_HEADING='### Which layer enforces which rule'
typeset -r SCOPE_HEADING='### Scope and authority'
typeset -r SIZES_HEADING='### Test sizes'
typeset -r DET_HEADING='### Determinism rules'
typeset -r COVERAGE_HEADING='### Coverage'
typeset -r LEGACY_EXEC='## 4. EXECUTION PROTOCOLS'
typeset -r LEGACY_MANDATES='## 5. HARDENED MANDATES'
typeset -r STAMP_FILE='lib/vde-pol-stamp'
typeset -r SOVEREIGN_FILE='tests/run-sovereign-tests.zsh'
typeset -r SERIAL_FILE='tests/serial-unit-suites.txt'
typeset -r INSTRUCTIONS='.gemini/instructions.md'
typeset -r RULE_K_LINE='K. The 3-VM Concurrent Limit'
typeset -r AGENTS_FILE='AGENTS.md'
typeset -r CLAUDE_FILE='CLAUDE.md'
# Every file that names a sub-agent preamble (check 11).
typeset -a PREAMBLE_FILES=("${RULE}" "${PREAMBLE}" "${AGENTS_FILE}" "${CLAUDE_FILE}" "${INSTRUCTIONS}")

# The exact key set of tests/test-policy.conf (check 2).
typeset -a POLICY_KEYS=(UNIT_SUITE_BUDGET_SECONDS FULL_TIER_BUDGET_SECONDS STAMP_TTL_SECONDS
    DOCKER_EVENTS_TIMEOUT_SECONDS MAX_RUNNING_SPOKES TEST_PARALLEL_JOBS FLAKE_RERUN_ON_FAIL
    FLAKE_WINDOW_RUNS FLAKE_FAIL_THRESHOLD)
# Parsed conf: CONF[KEY]=value. Filled once by load_conf before the checks run.
typeset -A CONF=()
typeset -a CONF_MALFORMED=() CONF_DUPLICATE=()

# tracked FILE: in git's index AND present, non-empty, in the working tree (a file
# deleted from the worktree is still "tracked" until it is committed away).
tracked() { git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- "$1" >/dev/null 2>&1 && [[ -f "${VDE_ROOT_DIR}/$1" && -s "${VDE_ROOT_DIR}/$1" ]]; }
# has FILE FIXED-STRING
has() { grep -qF -- "$2" "${VDE_ROOT_DIR}/$1" 2>/dev/null; }
# expect_has LABEL FILE FIXED-STRING
expect_has() {
    if has "$2" "$3"; then test_pass "$1"; else test_fail "$1" "$2 does not contain [$3]"; fi
}
# cell_trim TEXT: strips the spaces and backticks around one table cell.
cell_trim() {
    setopt localoptions extendedglob
    local t="$1"
    t="${t##[[:space:]]#}"
    t="${t%%[[:space:]]#}"
    t="${t//\`/}"
    print -r -- "${t}"
}
# block HEADING FILE: the lines under HEADING, up to the next heading of the same or a
# higher level (an H2 block ends at the next "## "; an H3 block at the next "## " or "### ").
block() {
    local want="$1" file="${VDE_ROOT_DIR}/$2" line lvl="${1%% *}"
    local -i on=0
    [[ -f "${file}" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        if (( ! on )); then
            [[ "${line}" == "${want}" ]] && on=1
            continue
        fi
        if [[ "${line}" == '## '* ]] || { [[ "${lvl}" == '###' ]] && [[ "${line}" == '### '* ]]; }; then
            break
        fi
        print -r -- "${line}"
    done < "${file}"
}
# line_of EXACT FILE: line number of the first line equal to EXACT (empty if none).
line_of() {
    local m
    m="$(grep -nxF -m1 -- "$1" "${VDE_ROOT_DIR}/$2" 2>/dev/null)"
    print -r -- "${m%%:*}"
}
# line_of_prefix TEXT FILE: line number of the first line containing TEXT (empty if none).
line_of_prefix() {
    local m
    m="$(grep -nF -m1 -- "$1" "${VDE_ROOT_DIR}/$2" 2>/dev/null)"
    print -r -- "${m%%:*}"
}
# tooling_defaults FILE VAR: the N of EVERY `${VAR:-N}` in FILE, one per line (none if absent).
tooling_defaults() {
    local m
    [[ -f "${VDE_ROOT_DIR}/$1" ]] || return 0
    grep -oE -- "${2}:-[0-9]+" "${VDE_ROOT_DIR}/$1" 2>/dev/null | while IFS= read -r m; do
        print -r -- "${m##*:-}"
    done
}
# line_has_all BLOCK NEEDLE...: 0 if one line of BLOCK contains every NEEDLE (fixed strings,
# case-insensitive). A needle may hold spaces; each needle is one argument.
line_has_all() {
    local blk="$1" line n ok
    shift
    while IFS= read -r line; do
        ok=1
        for n in "$@"; do
            [[ "${(L)line}" == *"${(L)n}"* ]] || { ok=0; break; }
        done
        (( ok )) && return 0
    done <<< "${blk}"
    return 1
}
# first_pos TEXT NEEDLE...: the offset of the earliest NEEDLE in TEXT (empty if none).
first_pos() {
    local text="$1" n pre
    local -i best=-1 p
    shift
    for n in "$@"; do
        [[ "${text}" == *"${n}"* ]] || continue
        pre="${text%%"${n}"*}"
        p=${#pre}
        (( best < 0 || p < best )) && best=$p
    done
    (( best < 0 )) && return 0
    print -r -- "${best}"
}
# layer_rows: one "Rule<TAB>Status" line per row of the layers table (cells[2] and cells[4]).
layer_rows() {
    local line name st
    local -a cells
    while IFS= read -r line; do
        [[ "${line}" == '|'* ]] || continue
        [[ "${line}" == *'---'* ]] && continue
        cells=("${(@s:|:)line}")
        name="$(cell_trim "${cells[2]:-}")"
        st="$(cell_trim "${cells[4]:-}")"
        print -r -- "${name}"$'\t'"${st}"
    done <<< "$(block "${LAYERS_HEADING}" "${DOC}")"
}
# preamble_sentence_problem SENTENCE: a message (empty if none) when a lowercase sentence says a
# prompt begins or starts with a preamble and the first preamble named after that phrase is
# not the security one. Only the text after the phrase is inspected, so a later mention in the
# same sentence cannot hide a wrong order.
preamble_sentence_problem() {
    local s="$1" phrase tail sp2 tp2
    for phrase in 'begins with' 'starts with'; do
        [[ "${s}" == *"${phrase}"* ]] || continue
        tail="${s#*"${phrase}"}"
        sp2="$(first_pos "${tail}" 'security-preamble' 'security preamble')"
        tp2="$(first_pos "${tail}" 'testing-preamble' 'testing preamble' 'this preamble')"
        [[ -n "${sp2}" || -n "${tp2}" ]] || continue
        if [[ -z "${sp2}" ]]; then
            print -rn -- "says a prompt ${phrase} the testing preamble without naming the security preamble first; "
        elif [[ -n "${tp2}" ]] && (( tp2 < sp2 )); then
            print -rn -- "says a prompt ${phrase} the testing preamble before the security preamble; "
        fi
    done
}
# preamble_problems FILE: one message per sentence that breaks the preamble order (empty if
# none). Each line is split into sentences at ". " and "; " (a leading markdown bullet marker
# is dropped first). A sentence naming both preambles must name the security one first. A
# sentence that says a prompt begins or starts with a preamble must name the security one first.
preamble_problems() {
    local line lc s sp tp msg out=""
    local -i ln=0
    local -a sents
    [[ -f "${VDE_ROOT_DIR}/$1" ]] || { print -r -- "file missing"; return 0; }
    setopt localoptions extendedglob
    while IFS= read -r line || [[ -n "${line}" ]]; do
        (( ++ln ))
        line="${line##[[:space:]]#([-*]|[0-9]##.)[[:space:]]##}"
        line="${line//'. '/$'.\n'}"
        line="${line//'; '/$';\n'}"
        sents=("${(@f)line}")
        for s in "${sents[@]}"; do
            lc="${(L)s}"
            sp="$(first_pos "${lc}" 'security-preamble' 'security preamble')"
            tp="$(first_pos "${lc}" 'testing-preamble' 'testing preamble' 'this preamble')"
            if [[ -n "${sp}" && -n "${tp}" ]] && (( tp < sp )); then
                out+="line ${ln} names the testing preamble before the security preamble; "
            fi
            msg="$(preamble_sentence_problem "${lc}")"
            [[ -n "${msg}" ]] && out+="line ${ln} ${msg}"
        done
    done < "${VDE_ROOT_DIR}/$1"
    print -r -- "${out}"
}

# load_conf: fills CONF from tests/test-policy.conf (KEY=value; comments and blank lines
# are ignored; a trailing "# comment" is stripped from the value).
load_conf() {
    local line key
    [[ -f "${VDE_ROOT_DIR}/${CONF_FILE}" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        line="${line%%\#*}"
        line="${line//[[:space:]]/}"
        [[ -n "${line}" ]] || continue
        if [[ "${line}" != *=* ]]; then
            CONF_MALFORMED+=("${line}")
            continue
        fi
        key="${line%%=*}"
        if (( ${+CONF[$key]} )); then
            CONF_DUPLICATE+=("${key}")
        fi
        CONF[$key]="${line#*=}"
    done < "${VDE_ROOT_DIR}/${CONF_FILE}"
}

test_policy_section() {
    test_start "1: testing.md has the Testing Policy section, its headings in order, before the supreme gate section"
    local -a h3=('### Scope and authority' '### Standards followed' '### Test sizes'
        '### Determinism rules' '### Flake policy' '### Timing and budgets' '### Coverage'
        '### Test quality and evidence' "${LAYERS_HEADING}" "${NUMBERS_HEADING}")
    local h2_ln gate_ln ln h
    local -i prev=0
    tracked "${DOC}" && test_pass "${DOC} is tracked and non-empty" \
        || test_fail "${DOC} is tracked and non-empty" "not tracked, missing or empty"
    h2_ln="$(line_of "${POLICY_HEADING}" "${DOC}")"
    gate_ln="$(line_of_prefix "${GATE_HEADING}" "${DOC}")"
    if [[ -n "${h2_ln}" ]]; then
        test_pass "has the H2 [${POLICY_HEADING}]"
        prev=${h2_ln}
    else
        test_fail "has the H2 [${POLICY_HEADING}]" "no such line in ${DOC}"
    fi
    if [[ -z "${gate_ln}" ]]; then
        test_fail "has the anchor [${GATE_HEADING}] after the policy section" "no such line in ${DOC}"
    elif [[ -n "${h2_ln}" ]] && (( h2_ln < gate_ln )); then
        test_pass "the policy section sits before [${GATE_HEADING}]"
    else
        test_fail "the policy section sits before [${GATE_HEADING}]" "H2 at line [${h2_ln}], gate at line [${gate_ln}]"
    fi
    for h in "${h3[@]}"; do
        ln="$(line_of "${h}" "${DOC}")"
        if [[ -n "${ln}" ]] && (( ln > prev )) && { [[ -z "${gate_ln}" ]] || (( ln < gate_ln )); }; then
            test_pass "has [${h}] in order"
            prev=${ln}
        else
            test_fail "has [${h}] in order" "missing, or out of order after line [${prev}] (found at [${ln:-none}])"
        fi
    done
}

test_conf_keys() {
    test_start "2: tests/test-policy.conf is tracked, has exactly the policy keys, every value numeric"
    local k v
    if tracked "${CONF_FILE}"; then
        test_pass "${CONF_FILE} is tracked and non-empty"
    else
        test_fail "${CONF_FILE} is tracked and non-empty" "not tracked, missing or empty"
        return
    fi
    for k in "${CONF_MALFORMED[@]}"; do
        test_fail "${CONF_FILE} lines are KEY=value" "malformed line [${k}]"
    done
    for k in "${CONF_DUPLICATE[@]}"; do
        test_fail "${CONF_FILE} keys are unique" "duplicate key [${k}]"
    done
    for k in "${POLICY_KEYS[@]}"; do
        if (( ${+CONF[$k]} )); then
            test_pass "${CONF_FILE} has ${k}"
        else
            test_fail "${CONF_FILE} has ${k}" "key missing"
        fi
    done
    for k in "${(@k)CONF}"; do
        if (( ${POLICY_KEYS[(Ie)${k}]} )); then
            v="${CONF[$k]}"
            [[ "${v}" == <-> ]] && test_pass "${k} value [${v}] is numeric" \
                || test_fail "${k} value is numeric" "value [${v}]"
        else
            test_fail "${CONF_FILE} has no extra keys" "unexpected key [${k}]"
        fi
    done
}

test_numbers_table() {
    test_start "3: the Policy numbers table in the doc matches tests/test-policy.conf, key for key and value for value, and names each key once"
    local -A DOCV=()
    local -a rows cells all dups=()
    local line k key val
    rows=("${(@f)$(block "${NUMBERS_HEADING}" "${DOC}")}")
    for line in "${rows[@]}"; do
        [[ "${line}" == '| `'*'` | `'*'` |'* ]] || continue
        cells=("${(@s:|:)line}")
        key="$(cell_trim "${cells[2]}")"
        val="$(cell_trim "${cells[3]}")"
        if (( ${+DOCV[$key]} )); then
            dups+=("${key}")
        fi
        DOCV[$key]="${val}"
    done
    if (( ${#dups[@]} == 0 )); then
        test_pass "the Policy numbers table names each key once"
    else
        for k in "${dups[@]}"; do
            test_fail "the Policy numbers table names each key once" "duplicate row for [${k}]"
        done
    fi
    if (( ${#DOCV[@]} == 0 )); then
        test_fail "the Policy numbers table has rows" "no \`KEY\` | \`value\` rows under [${NUMBERS_HEADING}] in ${DOC}"
        return
    fi
    all=("${(@k)CONF}" "${(@k)DOCV}")
    all=("${(@u)all}")
    for k in "${all[@]}"; do
        if ! (( ${+CONF[$k]} )); then
            test_fail "table key ${k} is a conf key" "${CONF_FILE} has no ${k}"
        elif ! (( ${+DOCV[$k]} )); then
            test_fail "conf key ${k} has a table row" "the Policy numbers table has no ${k} row"
        elif [[ "${DOCV[$k]}" == "${CONF[$k]}" ]]; then
            test_pass "${k} is ${CONF[$k]} in both the doc and the conf"
        else
            test_fail "${k} matches the conf" "doc says [${DOCV[$k]}], conf says [${CONF[$k]}]"
        fi
    done
}

test_tooling_defaults() {
    test_start "4: the conf matches every tooling default (stamp TTL, all occurrences; Spoke events timeout) and Rule K"
    local -a dflts=()
    local d kline n
    dflts=("${(@f)$(tooling_defaults "${STAMP_FILE}" VDE_POL_STAMP_TTL)}")
    dflts=("${(@)dflts:#}")
    if (( ${#dflts[@]} == 0 )); then
        test_fail "${STAMP_FILE} declares the VDE_POL_STAMP_TTL default (:-<seconds>)" "no such default"
    else
        for d in "${dflts[@]}"; do
            if [[ "${CONF[STAMP_TTL_SECONDS]:-}" == "${d}" ]]; then
                test_pass "STAMP_TTL_SECONDS equals the ${STAMP_FILE} default (${d})"
            else
                test_fail "STAMP_TTL_SECONDS equals every ${STAMP_FILE} default" \
                    "conf [${CONF[STAMP_TTL_SECONDS]:-<absent>}], tooling [${d}]"
            fi
        done
    fi
    dflts=("${(@f)$(tooling_defaults "${SOVEREIGN_FILE}" VDE_DOCKER_EVENTS_TIMEOUT)}")
    dflts=("${(@)dflts:#}")
    if (( ${#dflts[@]} == 0 )); then
        test_fail "${SOVEREIGN_FILE} declares the VDE_DOCKER_EVENTS_TIMEOUT default (:-<seconds>)" "no such default"
    else
        for d in "${dflts[@]}"; do
            if [[ "${CONF[DOCKER_EVENTS_TIMEOUT_SECONDS]:-}" == "${d}" ]]; then
                test_pass "DOCKER_EVENTS_TIMEOUT_SECONDS equals the ${SOVEREIGN_FILE} default (${d})"
            else
                test_fail "DOCKER_EVENTS_TIMEOUT_SECONDS equals every ${SOVEREIGN_FILE} default" \
                    "conf [${CONF[DOCKER_EVENTS_TIMEOUT_SECONDS]:-<absent>}], tooling [${d}]"
            fi
        done
    fi
    [[ "${CONF[MAX_RUNNING_SPOKES]:-}" == 3 ]] && test_pass "MAX_RUNNING_SPOKES is 3" \
        || test_fail "MAX_RUNNING_SPOKES is 3" "conf [${CONF[MAX_RUNNING_SPOKES]:-<absent>}]"
    expect_has "${INSTRUCTIONS} states Rule K (3-VM Concurrent Limit)" "${INSTRUCTIONS}" "${RULE_K_LINE}"
    # Rule K body: the concurrency limit in the Rule K line itself must be the conf number.
    n="${CONF[MAX_RUNNING_SPOKES]:-}"
    kline="$(grep -F -- "${RULE_K_LINE}" "${VDE_ROOT_DIR}/${INSTRUCTIONS}" 2>/dev/null | head -1)"
    if [[ -n "${n}" && "${kline}" == *"maximum ${n} concurrent Spokes"* ]]; then
        test_pass "the Rule K body states the concurrency limit as maximum ${n} concurrent Spokes"
    else
        test_fail "the Rule K body states the concurrency limit (MAX_RUNNING_SPOKES)" \
            "no [maximum ${n:-<absent>} concurrent Spokes] in the Rule K line of ${INSTRUCTIONS}"
    fi
    # Entry points must not state another number next to the words concurrent Spokes.
    local f c
    local -a claims
    for f in "${AGENTS_FILE}" "${CLAUDE_FILE}"; do
        claims=("${(@f)$(grep -oE -- '[0-9]+ concurrent Spokes' "${VDE_ROOT_DIR}/${f}" 2>/dev/null)}")
        claims=("${(@)claims:#}")
        local -i wrong=0
        for c in "${claims[@]}"; do
            [[ "${c%% *}" == "${n}" ]] || wrong+=1
        done
        if (( wrong == 0 )); then
            test_pass "${f} states no other concurrency number next to concurrent Spokes"
        else
            test_fail "${f} states no other concurrency number next to concurrent Spokes" \
                "${wrong} line(s) state a different number than the conf"
        fi
    done
}

test_parallel_jobs() {
    test_start "4b: the runner's VDE_MAX_TEST_JOBS equals TEST_PARALLEL_JOBS in the conf and in the Policy numbers table; the serial suite list is tracked and non-empty"
    local -a occ=() rows cells=()
    local line rn="" dv=""
    occ=("${(@f)$(grep -oE -- 'VDE_MAX_TEST_JOBS=[0-9]+' "${VDE_ROOT_DIR}/${SOVEREIGN_FILE}" 2>/dev/null)}")
    occ=("${(@)occ:#}")
    if (( ${#occ[@]} == 1 )); then
        rn="${occ[1]##*=}"
        test_pass "${SOVEREIGN_FILE} declares VDE_MAX_TEST_JOBS once (${rn})"
    else
        test_fail "${SOVEREIGN_FILE} declares VDE_MAX_TEST_JOBS once" "found ${#occ[@]} declaration(s) of VDE_MAX_TEST_JOBS=<n>"
    fi
    if [[ -n "${rn}" && "${rn}" == "${CONF[TEST_PARALLEL_JOBS]:-}" ]]; then
        test_pass "VDE_MAX_TEST_JOBS equals TEST_PARALLEL_JOBS in ${CONF_FILE} (${rn})"
    else
        test_fail "VDE_MAX_TEST_JOBS equals TEST_PARALLEL_JOBS in ${CONF_FILE}" \
            "runner [${rn:-<absent>}], conf [${CONF[TEST_PARALLEL_JOBS]:-<absent>}]"
    fi
    rows=("${(@f)$(block "${NUMBERS_HEADING}" "${DOC}")}")
    for line in "${rows[@]}"; do
        [[ "${line}" == '| `TEST_PARALLEL_JOBS`'* ]] || continue
        cells=("${(@s:|:)line}")
        dv="$(cell_trim "${cells[3]}")"
    done
    if [[ -n "${rn}" && "${rn}" == "${dv}" ]]; then
        test_pass "VDE_MAX_TEST_JOBS equals the TEST_PARALLEL_JOBS row in ${DOC} (${rn})"
    else
        test_fail "VDE_MAX_TEST_JOBS equals the TEST_PARALLEL_JOBS row in ${DOC}" \
            "runner [${rn:-<absent>}], doc [${dv:-<no row>}]"
    fi
    if tracked "${SERIAL_FILE}"; then
        test_pass "${SERIAL_FILE} is tracked and non-empty"
    else
        test_fail "${SERIAL_FILE} is tracked and non-empty" "not tracked, missing or empty"
    fi
}

test_pointers() {
    test_start "5: the agent rule and the preamble are tracked; every entry point names the policy, the rule and the preamble"
    local f
    for f in "${RULE}" "${PREAMBLE}"; do
        tracked "${f}" && test_pass "${f} is tracked and non-empty" \
            || test_fail "${f} is tracked and non-empty" "not tracked, missing or empty"
    done
    for f in AGENTS.md CLAUDE.md "${INSTRUCTIONS}"; do
        expect_has "${f} names ${DOC}" "${f}" "${DOC}"
        expect_has "${f} names ${RULE}" "${f}" "${RULE}"
        expect_has "${f} names ${PREAMBLE}" "${f}" "${PREAMBLE}"
    done
}

test_links() {
    test_start "6: the security process and the GitHub lifecycle link the testing policy"
    # Each link is relative to its own directory, so the target text differs: from docs/governance/ it is
    # ../development/testing.md, from docs/development/ it is testing.md.
    expect_has "security-process.md links ${DOC}" docs/governance/security-process.md "](../development/testing.md)"
    expect_has "github-lifecycle.md links ${DOC}" docs/development/github-lifecycle.md "](testing.md)"
}

test_layers_table() {
    test_start "7: every row of the 'Which layer enforces which rule' table has a Status of Implemented or Planned (#N)"
    local line st name
    local -i si=0 rows=0 bad=0 i
    local -a lines cells
    local re='^(Implemented|Planned \(#[0-9]+\))$'
    lines=("${(@f)$(block "${LAYERS_HEADING}" "${DOC}")}")
    for line in "${lines[@]}"; do
        [[ "${line}" == '|'* ]] || continue
        [[ "${line}" == *'---'* ]] && continue
        cells=("${(@s:|:)line}")
        if (( si == 0 )); then
            for (( i = 1; i <= ${#cells[@]}; i++ )); do
                [[ "$(cell_trim "${cells[i]}")" == Status ]] && si=$i
            done
            if (( si == 0 )); then
                test_fail "the layers table has a Status column" "no Status header under [${LAYERS_HEADING}] in ${DOC}"
                return
            fi
            continue
        fi
        rows+=1
        name="$(cell_trim "${cells[2]}")"
        st="$(cell_trim "${cells[si]}")"
        if [[ ! "${st}" =~ ${re} ]]; then
            bad+=1
            test_fail "row [${name:-?}] has Status Implemented or Planned (#N)" "status is [${st}]"
        fi
    done
    if (( rows == 0 )); then
        test_fail "the layers table has rows" "no rows under [${LAYERS_HEADING}] in ${DOC}"
    elif (( bad == 0 )); then
        test_pass "all ${rows} layer rows have an Implemented or Planned (#N) status"
    fi
}

test_rule_restates_no_number() {
    test_start "8: the agent rule restates no policy number"
    local k v
    local -i hits=0
    if ! tracked "${RULE}"; then
        test_fail "${RULE} restates no policy number" "not tracked, missing or empty"
        return
    fi
    if (( ${#CONF[@]} == 0 )); then
        test_fail "${RULE} restates no policy number" "no conf values to check against"
        return
    fi
    for k in "${(@k)CONF}"; do
        v="${CONF[$k]}"
        if grep -qw -- "${v}" "${VDE_ROOT_DIR}/${RULE}" 2>/dev/null; then
            hits+=1
            test_fail "${RULE} does not restate ${k}" "the number [${v}] appears in the rule"
        fi
    done
    (( hits == 0 )) && test_pass "${RULE} restates no policy number from ${CONF_FILE}"
}

test_new_section_prose() {
    test_start "9: the new policy section is plain developer prose (no mythos words, no sleep example)"
    setopt localoptions extendedglob
    local sec prose mythos l k
    sec="$(block "${POLICY_HEADING}" "${DOC}")"
    if [[ -z "${sec}" ]]; then
        test_fail "the policy section exists to be checked" "no [${POLICY_HEADING}] block in ${DOC}"
        return
    fi
    # Backtick spans are literal names of existing commands, files or tests: allowed. Removed per line.
    prose=""
    for l in "${(@f)sec}"; do
        prose+="${l//\`[^\`]#\`/}"$'\n'
    done
    mythos="$(print -r -- "${prose}" | grep -oiwE 'strike|signet|beskar|mandalorian|gospel|sovereign baseline' | sort -u | tr '\n' ' ')"
    if [[ -z "${mythos}" ]]; then
        test_pass "the policy section's prose uses no mythos words"
    else
        test_fail "the policy section's prose uses no mythos words" "found [${mythos}]"
    fi
    if print -r -- "${sec}" | grep -qE '(^|[^[:alnum:]_])sleep[[:space:]]+[0-9]'; then
        test_fail "the policy section has no sleep-using example" "a line sleeps for a number of seconds"
    else
        test_pass "the policy section has no sleep-using example"
    fi
    for k in 'test' 'pull request' 'issue'; do
        print -r -- "${sec}" | grep -qi -- "${k}" && test_pass "the policy section uses the word [${k}]" \
            || test_fail "the policy section uses the word [${k}]" "absent"
    done
}

test_timing_pins() {
    test_start "10: the timing rules match their implementation (vde_test_now and vde_test_fmt1 exist, are named and explained, and the timing row is Implemented)"
    local sec budgets line st
    local -a cells
    if grep -qF -- 'vde_test_now() {' "${VDE_ROOT_DIR}/lib/vde-test-env" 2>/dev/null; then
        test_pass "lib/vde-test-env defines vde_test_now"
    else
        test_fail "lib/vde-test-env defines vde_test_now" "no such definition"
    fi
    if grep -qF -- 'vde_test_fmt1() {' "${VDE_ROOT_DIR}/lib/vde-test-env" 2>/dev/null; then
        test_pass "lib/vde-test-env defines vde_test_fmt1"
    else
        test_fail "lib/vde-test-env defines vde_test_fmt1" "no such definition"
    fi
    sec="$(block "${DET_HEADING}" "${DOC}")"
    for k in 'vde_test_now' 'vde_test_fmt1'; do
        print -r -- "${sec}" | grep -qF -- "${k}" && test_pass "the Determinism rules name [${k}]" \
            || test_fail "the Determinism rules name [${k}]" "absent from the subsection"
    done
    for k in 'SECONDS' 'monotonic'; do
        print -r -- "${sec}" | grep -qF -- "${k}" && test_pass "the Determinism rules say [${k}] (SECONDS is not a monotonic clock)" \
            || test_fail "the Determinism rules say [${k}] (SECONDS is not a monotonic clock)" "absent from the subsection"
    done
    budgets="$(block '### Timing and budgets' "${DOC}")"
    for k in 'once PR #783' 'once the'; do
        if print -r -- "${budgets}" | grep -qF -- "${k}"; then
            test_fail "Timing and budgets has no conditional [${k}]" "found [${k}]"
        else
            test_pass "Timing and budgets has no conditional [${k}]"
        fi
    done
    # Columns of the layers table: Rule | Enforced by | Status (cells[4] after the leading empty cell).
    line="$(block "${LAYERS_HEADING}" "${DOC}" | grep -F -- '| Timing printed every run' | head -1)"
    cells=("${(@s:|:)line}")
    st="$(cell_trim "${cells[4]:-}")"
    if [[ "${st}" == 'Implemented' ]]; then
        test_pass "the timing row Status is exactly Implemented"
    else
        test_fail "the timing row Status is exactly Implemented" "status is [${st:-<no row>}]"
    fi
}

test_preamble_order() {
    test_start "11: (E) every file that names a sub-agent preamble names the security preamble first, then the testing preamble"
    local f probs
    for f in "${PREAMBLE_FILES[@]}"; do
        probs="$(preamble_problems "${f}")"
        if [[ -z "${probs}" ]]; then
            test_pass "${f} names the security preamble before the testing preamble"
        else
            test_fail "${f} names the security preamble before the testing preamble" "${probs}"
        fi
    done
}

test_layers_rows_policy() {
    test_start "12: (F) the layers table has a suite discovery row Implemented, a test-size and determinism row Planned (#778), and no Implemented claim for test sizes or determinism"
    local line name st lname
    local -i discovery_ok=0 planned_ok=0
    local bad_rows=""
    for line in "${(@f)$(layer_rows)}"; do
        name="${line%%$'\t'*}"
        st="${line#*$'\t'}"
        lname="${(L)name}"
        if [[ "${lname}" == *'suite discovery'* && "${lname}" == *exclusions* && "${st}" == Implemented ]]; then
            discovery_ok=1
        fi
        if [[ "${lname}" == *size* && "${lname}" == *determinism* && "${st}" == 'Planned (#778)' ]]; then
            planned_ok=1
        fi
        if [[ "${st}" == Implemented && ( "${lname}" == *size* || "${lname}" == *determinism* ) ]]; then
            bad_rows+="[${name}] "
        fi
    done
    if (( discovery_ok )); then
        test_pass "a layers row names suite discovery and exclusions, Implemented"
    else
        test_fail "a layers row names suite discovery and exclusions, Implemented" "no such row"
    fi
    if (( planned_ok )); then
        test_pass "a layers row names the test-size and determinism checks, Planned (#778)"
    else
        test_fail "a layers row names the test-size and determinism checks, Planned (#778)" "no such row"
    fi
    if [[ -z "${bad_rows}" ]]; then
        test_pass "no layers row claims Implemented for test sizes or determinism"
    else
        test_fail "no layers row claims Implemented for test sizes or determinism" "rows ${bad_rows}"
    fi
}

test_coverage_exclusions() {
    test_start "13: (G) the Coverage subsection mentions tests/ci-coverage-exclusions.txt"
    local cov
    cov="$(block "${COVERAGE_HEADING}" "${DOC}")"
    if [[ "${cov}" == *'tests/ci-coverage-exclusions.txt'* ]]; then
        test_pass "the Coverage subsection names tests/ci-coverage-exclusions.txt"
    else
        test_fail "the Coverage subsection names tests/ci-coverage-exclusions.txt" "absent from the subsection"
    fi
}

test_legacy_deferral() {
    test_start "14: (H) the legacy sections 4 and 5 each defer to the Testing Policy (binding)"
    local h b
    for h in "${LEGACY_EXEC}" "${LEGACY_MANDATES}"; do
        b="$(block "${h}" "${DOC}")"
        if line_has_all "${b}" 'Testing Policy (binding)' 'defer'; then
            test_pass "[${h}] defers to the Testing Policy (binding)"
        else
            test_fail "[${h}] defers to the Testing Policy (binding)" "no sentence in the section defers to it"
        fi
    done
}

test_size_exceptions() {
    test_start "15: (I) the Test sizes subsection names vde-agent-sock.test.zsh and spine-git-env-isolation.test.zsh as small-tier exceptions with Status Planned for moving them"
    local sz s
    sz="$(block "${SIZES_HEADING}" "${DOC}")"
    for s in vde-agent-sock.test.zsh spine-git-env-isolation.test.zsh; do
        if line_has_all "${sz}" "${s}" 'exception' 'Planned'; then
            test_pass "the Test sizes subsection names ${s} as an exception, Planned"
        else
            test_fail "the Test sizes subsection names ${s} as an exception, Planned" "no line names it with exception and Planned"
        fi
    done
}

test_config_scope() {
    test_start "16: (J) the Scope paragraph does not say the tooling reads tests/test-policy.conf, and says the numbers mirror the tooling defaults and this test fails on drift"
    local scope
    scope="$(block "${SCOPE_HEADING}" "${DOC}")"
    if line_has_all "${scope}" 'tooling reads' 'test-policy.conf'; then
        test_fail "the Scope paragraph does not say the tooling reads ${CONF_FILE}" "it says so"
    else
        test_pass "the Scope paragraph does not say the tooling reads ${CONF_FILE}"
    fi
    if line_has_all "${scope}" 'mirror' 'default'; then
        test_pass "the Scope paragraph says the numbers mirror the tooling defaults"
    else
        test_fail "the Scope paragraph says the numbers mirror the tooling defaults" "no such statement"
    fi
    if line_has_all "${scope}" 'drift'; then
        test_pass "the Scope paragraph says this test fails if they drift"
    else
        test_fail "the Scope paragraph says this test fails if they drift" "no such statement"
    fi
}

test_determinism_home() {
    test_start "17: (K) the Determinism rules do not say lib/vde-test-env provides the scratch HOME, and say the gate runs the suites under a scratch HOME"
    local sec plain
    sec="$(block "${DET_HEADING}" "${DOC}")"
    plain="${sec//\`/}"
    if line_has_all "${plain}" 'provided by lib/vde-test-env' 'home'; then
        test_fail "the Determinism rules do not claim lib/vde-test-env provides the scratch HOME" "a line says so"
    else
        test_pass "the Determinism rules do not claim lib/vde-test-env provides the scratch HOME"
    fi
    if line_has_all "${plain}" 'gate' 'scratch home'; then
        test_pass "the Determinism rules say the gate runs the suites under a scratch HOME"
    else
        test_fail "the Determinism rules say the gate runs the suites under a scratch HOME" "no such statement"
    fi
}

# det_check LABEL BLOCK PHRASE...: pass when ONE bullet (one markdown list line) of BLOCK
# contains every PHRASE. Each phrase is a fixed string of the obligation's own wording, so a
# stray line that merely shares a keyword cannot satisfy the check.
det_check() {
    local label="$1" blk="$2"
    shift 2
    if line_has_all "${blk}" "$@"; then
        test_pass "the Determinism rules state ${label}"
    else
        test_fail "the Determinism rules state ${label}" "missing phrase in one bullet: no bullet of the subsection contains all of [$*]"
    fi
}

test_determinism_obligations() {
    test_start "18: (D) the Determinism rules state each obligation (one check per obligation)"
    local sec
    sec="$(block "${DET_HEADING}" "${DOC}")"
    det_check "a wait through zselect in place of sleep" "${sec}" 'Do not use `sleep`' zselect
    det_check "a timing margin" "${sec}" 'Assert with a margin'
    det_check "output that does not change under LC_ALL" "${sec}" 'under `LC_ALL`'
    det_check "no network use" "${sec}" 'Small tests use no network'
    det_check "no dependence on test order" "${sec}" 'depends on the order in which'
    det_check "a fixed seed for any randomness" "${sec}" 'uses a fixed seed'
    det_check "a cleanup that leaves no process, container or file" "${sec}" 'leaves no process, container or file behind'
    det_check "a scratch HOME and scratch directories" "${sec}" 'Small tests use their own scratch'
}

# step_lines FILE N: the lines of FILE whose numbered list item is N (after any indentation).
step_lines() {
    local f="${VDE_ROOT_DIR}/$1"
    [[ -f "${f}" ]] || return 0
    grep -E -- "^[[:space:]]*$2\\." "${f}" 2>/dev/null
}
# top_block KEY FILE: the lines of the top-level KEY: block of a workflow file (from the KEY:
# line up to the next line that starts a top-level key).
top_block() {
    local line re_top='^[A-Za-z_][A-Za-z0-9_-]*:'
    local -i on=0
    [[ -f "${VDE_ROOT_DIR}/$2" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        if [[ "${line}" == "$1:" ]]; then
            on=1
            continue
        fi
        if [[ "${line}" =~ ${re_top} ]]; then
            on=0
        fi
        if (( on )); then
            print -r -- "${line}"
        fi
    done < "${VDE_ROOT_DIR}/$2"
}
# wf_env FILE: one KEY<TAB>VALUE line per entry of every env: block of a workflow file. The
# entries of an env: block are the lines indented deeper than the env: key.
wf_env() {
    setopt localoptions extendedglob
    local line t ws key val
    local -i ci env_ind=-1
    [[ -f "${VDE_ROOT_DIR}/$1" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        [[ -n "${line//[[:space:]]/}" ]] || continue
        ws="${line%%[^[:space:]]*}"
        ci=${#ws}
        t="${line##[[:space:]]#}"
        if (( env_ind >= 0 && ci <= env_ind )); then
            env_ind=-1
        fi
        if (( env_ind >= 0 )); then
            key="${t%%:*}"
            val="${t#*:}"
            val="${val##[[:space:]]#}"
            print -r -- "${key}"$'\t'"${val}"
        elif [[ "${t}" == 'env:' ]]; then
            env_ind=$ci
        fi
    done < "${VDE_ROOT_DIR}/$1"
}
# wf_runs FILE: one BLOCK<TAB>LINE line per line of every run script of a workflow file. A
# single-line run: value is one line; a run: | or run: > block ends at the next non-blank line
# indented no deeper than its run: key.
wf_runs() {
    setopt localoptions extendedglob
    local line t ws kt rest
    local -i ci kc rk=-1 n=0 inrun=0
    [[ -f "${VDE_ROOT_DIR}/$1" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        ws="${line%%[^[:space:]]*}"
        ci=${#ws}
        t="${line##[[:space:]]#}"
        if (( inrun )); then
            if [[ -n "${line//[[:space:]]/}" ]] && (( ci <= rk )); then
                inrun=0
            else
                print -r -- "${n}"$'\t'"${line}"
                continue
            fi
        fi
        kt="${t}"
        kc=$ci
        if [[ "${kt}" == '- '* ]]; then
            kt="${kt#- }"
            kt="${kt##[[:space:]]#}"
            kc=$(( ci + 2 ))
        fi
        if [[ "${kt}" == run:* ]]; then
            n+=1
            rest="${kt#run:}"
            rest="${rest##[[:space:]]#}"
            rk=$kc
            if [[ "${rest}" == '|'* || "${rest}" == '>'* ]]; then
                inrun=1
            else
                print -r -- "${n}"$'\t'"${rest}"
            fi
        fi
    done < "${VDE_ROOT_DIR}/$1"
}
# wf_jobs FILE: the job ids under the top-level jobs: key of a workflow file, one per line.
wf_jobs() {
    local line re_top='^[A-Za-z_][A-Za-z0-9_-]*:' re_job='^  ([A-Za-z0-9_-]+):[[:space:]]*$'
    local -i injobs=0
    [[ -f "${VDE_ROOT_DIR}/$1" ]] || return 0
    while IFS= read -r line || [[ -n "${line}" ]]; do
        if [[ "${line}" == 'jobs:' ]]; then
            injobs=1
            continue
        fi
        if [[ "${line}" =~ ${re_top} ]]; then
            injobs=0
        fi
        if (( injobs )) && [[ "${line}" =~ ${re_job} ]]; then
            print -r -- "${match[1]}"
        fi
    done < "${VDE_ROOT_DIR}/$1"
}

typeset -r REVIEWER='.gemini/SKILLS/reviewer.md'
typeset -r PR_SCRIPT='bin/vde-check-pr-evidence.zsh'
typeset -r PR_WF='.github/workflows/pr-evidence.yml'
typeset -r PR_VERDICT='DRY: CLEAN | FAKE TESTS: NONE | SPEC: COMPLIANT | ZSH: COMPLIANT | TESTING: COMPLIANT'

test_reviewer_step() {
    test_start "19: (R1) the reviewer skill has a numbered step 6 for the Testing Policy, says Run all 6 review steps, and has the APPROVED verdict line with TESTING: COMPLIANT"
    local s6 appr_ln ver_ln
    s6="$(step_lines "${REVIEWER}" 6)"
    if [[ -n "${s6}" ]] && line_has_all "${s6}" 'Testing Policy' 'docs/development/testing.md'; then
        test_pass "${REVIEWER} has step 6 naming the Testing Policy and docs/development/testing.md"
    else
        test_fail "${REVIEWER} has step 6 naming the Testing Policy and docs/development/testing.md" "no numbered step 6 with both"
    fi
    expect_has "${REVIEWER} says Run all 6 review steps" "${REVIEWER}" 'Run all 6 review steps'
    if has "${REVIEWER}" 'Run all 5 review steps'; then
        test_fail "${REVIEWER} has no Run all 5 review steps" "the old count remains"
    else
        test_pass "${REVIEWER} has no Run all 5 review steps"
    fi
    appr_ln="$(line_of '**APPROVED:**' "${REVIEWER}")"
    ver_ln="$(line_of "${PR_VERDICT}" "${REVIEWER}")"
    if [[ -n "${appr_ln}" && -n "${ver_ln}" ]] && (( ver_ln > appr_ln )); then
        test_pass "the APPROVED verdict line is [${PR_VERDICT}]"
    else
        test_fail "the APPROVED verdict line is [${PR_VERDICT}]" "no such line after the APPROVED heading in ${REVIEWER}"
    fi
}

test_pr_workflow_exists() {
    test_start "20: (W1) the pr-evidence workflow is tracked, its single job and its name are pr-evidence, and no other workflow uses that name"
    local -a wjobs=()
    local f base
    local -i clash=0
    if tracked "${PR_WF}"; then
        test_pass "${PR_WF} is tracked and non-empty"
    else
        test_fail "${PR_WF} is tracked and non-empty" "not tracked, missing or empty"
    fi
    wjobs=("${(@f)$(wf_jobs "${PR_WF}")}")
    wjobs=("${(@)wjobs:#}")
    if (( ${#wjobs[@]} == 1 )) && [[ "${wjobs[1]}" == pr-evidence ]]; then
        test_pass "${PR_WF} has exactly one job, pr-evidence"
    else
        test_fail "${PR_WF} has exactly one job, pr-evidence" "jobs [${wjobs[*]:-<none>}]"
    fi
    if grep -qxF -- '    name: pr-evidence' "${VDE_ROOT_DIR}/${PR_WF}" 2>/dev/null; then
        test_pass "the pr-evidence job has name: pr-evidence"
    else
        test_fail "the pr-evidence job has name: pr-evidence" "no such line in ${PR_WF}"
    fi
    for f in "${VDE_ROOT_DIR}"/.github/workflows/*.(yml|yaml)(N); do
        base="${f:t}"
        [[ "${base}" == pr-evidence.yml ]] && continue
        if grep -qE -- '^  pr-evidence:[[:space:]]*$|name:[[:space:]]*pr-evidence[[:space:]]*$' "${f}"; then
            clash+=1
            test_fail "no other workflow uses the job or step name pr-evidence" "${base} does"
        fi
    done
    (( clash == 0 )) && test_pass "no other workflow uses the job or step name pr-evidence"
}

test_pr_workflow_triggers() {
    test_start "21: (W2) the pr-evidence workflow runs on pull_request types opened, edited, synchronize and reopened"
    local tl w
    local -a words=()
    tl="$(top_block on "${PR_WF}" | grep -F -- 'types:' | head -n 1)"
    tl="${tl#*types:}"
    tl="${tl//\[/ }"
    tl="${tl//\]/ }"
    tl="${tl//,/ }"
    words=(${=tl})
    local -i miss=0
    for w in opened edited synchronize reopened; do
        (( ${words[(Ie)${w}]} )) || miss+=1
    done
    if (( miss == 0 )) && top_block on "${PR_WF}" | grep -qE -- '^  pull_request:'; then
        test_pass "${PR_WF} runs on pull_request types opened, edited, synchronize, reopened"
    else
        test_fail "${PR_WF} runs on pull_request types opened, edited, synchronize, reopened" "missing [${miss}] type(s) under pull_request"
    fi
}

test_pr_workflow_env() {
    test_start "22: (W3) an env block of the pr-evidence workflow feeds VDE_PR_BODY, VDE_PR_AUTHOR and VDE_PR_HEAD_REF from the pull request event"
    local envs pair key want
    envs="$(wf_env "${PR_WF}")"
    for pair in 'VDE_PR_BODY|${{ github.event.pull_request.body }}' \
        'VDE_PR_AUTHOR|${{ github.event.pull_request.user.login }}' \
        'VDE_PR_HEAD_REF|${{ github.event.pull_request.head.ref }}'; do
        key="${pair%%|*}"
        want="${pair#*|}"
        if print -r -- "${envs}" | grep -qxF -- "${key}"$'\t'"${want}"; then
            test_pass "${PR_WF} env feeds ${key} from the pull request event"
        else
            test_fail "${PR_WF} env feeds ${key} from the pull request event" "no env entry [${key}] with value [${want}]"
        fi
    done
}

test_pr_workflow_no_expression_in_run() {
    test_start "23: (W4) no run: block of the pr-evidence workflow contains an expression (injection safety)"
    local runs
    runs="$(wf_runs "${PR_WF}")"
    if [[ -z "${runs}" ]]; then
        test_fail "${PR_WF} has run blocks to check" "none parsed"
    elif print -r -- "${runs}" | grep -qF -- '${{'; then
        test_fail "no run: block of ${PR_WF} contains an expression" "a run script holds an expression marker"
    else
        test_pass "no run: block of ${PR_WF} contains an expression"
    fi
}

test_pr_workflow_last_command() {
    test_start "24: (W5) the last command of the pr-evidence run step is ./bin/vde-check-pr-evidence.zsh"
    setopt localoptions extendedglob
    local -A lastcmd=()
    local row bn body t
    local -i found=0
    while IFS= read -r row; do
        bn="${row%%$'\t'*}"
        body="${row#*$'\t'}"
        t="${body##[[:space:]]#}"
        t="${t%%[[:space:]]#}"
        [[ -n "${t}" ]] && lastcmd[$bn]="${t}"
    done <<< "$(wf_runs "${PR_WF}")"
    for bn in "${(@k)lastcmd}"; do
        [[ "${lastcmd[$bn]}" == './bin/vde-check-pr-evidence.zsh' ]] && found=1
    done
    if (( found )); then
        test_pass "the last command of a run step in ${PR_WF} is ./bin/vde-check-pr-evidence.zsh"
    else
        test_fail "the last command of a run step in ${PR_WF} is ./bin/vde-check-pr-evidence.zsh" "no run step ends with it"
    fi
}

test_pr_script() {
    test_start "25: (S1) bin/vde-check-pr-evidence.zsh is tracked and executable, has the @forge tag on line 2 and the shibboleth within 20 lines"
    local tagline
    if tracked "${PR_SCRIPT}"; then
        test_pass "${PR_SCRIPT} is tracked and non-empty"
    else
        test_fail "${PR_SCRIPT} is tracked and non-empty" "not tracked, missing or empty"
    fi
    if [[ -x "${VDE_ROOT_DIR}/${PR_SCRIPT}" ]]; then
        test_pass "${PR_SCRIPT} is executable"
    else
        test_fail "${PR_SCRIPT} is executable" "not executable or missing"
    fi
    tagline="$(head -n 2 -- "${VDE_ROOT_DIR}/${PR_SCRIPT}" 2>/dev/null | tail -n 1)"
    if [[ "${tagline}" == *'@forge'* ]]; then
        test_pass "${PR_SCRIPT} has the @forge tag on line 2"
    else
        test_fail "${PR_SCRIPT} has the @forge tag on line 2" "line 2 is [${tagline}]"
    fi
    if head -n 20 -- "${VDE_ROOT_DIR}/${PR_SCRIPT}" 2>/dev/null | grep -qxF -- 'typeset _ZSH_PURE=${(%):-%x}'; then
        test_pass "${PR_SCRIPT} has the shibboleth within 20 lines"
    else
        test_fail "${PR_SCRIPT} has the shibboleth within 20 lines" "no such line in the first 20"
    fi
}

test_layers_reviewer_pr_evidence() {
    test_start "26: (L1) the layers table has a Reviewer checklist row and a Pull request evidence check row, both Implemented, and no text says either is Planned"
    local line name st l lc
    local -i rev_row=0 rev_impl=0 pr_row=0 pr_impl=0 hits=0 ln=0
    for line in "${(@f)$(layer_rows)}"; do
        name="${line%%$'\t'*}"
        st="${line#*$'\t'}"
        if [[ "${name}" == 'Reviewer checklist'* ]]; then
            rev_row=1
            [[ "${st}" == Implemented ]] && rev_impl=1
        fi
        if [[ "${name}" == 'Pull request evidence check'* ]]; then
            pr_row=1
            [[ "${st}" == Implemented ]] && pr_impl=1
        fi
    done
    if (( rev_impl )); then
        test_pass "the layers row Reviewer checklist has Status exactly Implemented"
    else
        test_fail "the layers row Reviewer checklist has Status exactly Implemented" "row present: ${rev_row}"
    fi
    if (( pr_impl )); then
        test_pass "the layers row Pull request evidence check has Status exactly Implemented"
    else
        test_fail "the layers row Pull request evidence check has Status exactly Implemented" "row present: ${pr_row}"
    fi
    while IFS= read -r l || [[ -n "${l}" ]]; do
        ln+=1
        lc="${(L)l}"
        if [[ "${lc}" == *planned* ]] && { [[ "${lc}" == *'reviewer checklist'* ]] || [[ "${lc}" == *'review checklist'* ]] || [[ "${lc}" == *'pull request evidence'* ]]; }; then
            hits+=1
            test_fail "no text in ${DOC} says the reviewer checklist or the pull request evidence check is Planned" "line ${ln}"
        fi
    done < "${VDE_ROOT_DIR}/${DOC}"
    (( hits == 0 )) && test_pass "no text in ${DOC} says the reviewer checklist or the pull request evidence check is Planned"
}

load_conf
test_policy_section
test_conf_keys
test_numbers_table
test_tooling_defaults
test_parallel_jobs
test_pointers
test_links
test_layers_table
test_rule_restates_no_number
test_new_section_prose
test_timing_pins
test_preamble_order
test_layers_rows_policy
test_coverage_exclusions
test_legacy_deferral
test_size_exceptions
test_config_scope
test_determinism_home
test_determinism_obligations
test_reviewer_step
test_pr_workflow_exists
test_pr_workflow_triggers
test_pr_workflow_env
test_pr_workflow_no_expression_in_run
test_pr_workflow_last_command
test_pr_script
test_layers_reviewer_pr_evidence

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
