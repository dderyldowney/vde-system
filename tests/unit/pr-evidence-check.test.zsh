#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: bin/vde-check-pr-evidence.zsh, the pull request evidence check (Signet #778, second half).
#
# The script reads ONLY these environment variables: VDE_PR_BODY, VDE_PR_AUTHOR, VDE_PR_HEAD_REF, VDE_PR_HEAD_REPO and VDE_PR_BASE_REPO. The body is data.
#   exit 0  pass, or exempt (author dependabot[bot], or head ref exactly develop or stable from the SAME repository); it prints why
#   exit 1  a rule failed; the output names the rule as "rule (a)" to "rule (d)"
#   exit 2  a usage or internal error
# Until the script exists every case FAILS (RED): a missing script exits 127 and prints no rule. A 127 is never a pass.
#
# Each case runs the script through `env -i` (no inherited environment) with a scratch HOME, from the repository root.
# The injection cases run it from a scratch directory that would receive the sentinel file if the body were executed.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_POL_STAMP_TTL

typeset ROOT="${0:A:h:h:h}"
typeset CHECK="${ROOT}/bin/vde-check-pr-evidence.zsh"
typeset -g OUT='' RC='' HEAD_REPO=owner/repo BASE_REPO=owner/repo  # the head and base repository of the pull request; equal unless a case says otherwise
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
SCRATCH="$(mktemp -d "${SCRATCH}/pr-evidence-check.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT
typeset CHK_HOME="${SCRATCH}/home"
mkdir -p "${CHK_HOME}" || exit 1

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

run_check() {  # run_check CWD MODE AUTHOR HEAD BODY [EXTRA...] -> OUT (the script's output) and RC (its exit status)
    # MODE is set or unset: unset leaves VDE_PR_BODY out of the environment entirely.
    local cwd="$1" mode="$2" author="$3" head="$4" body="$5" raw
    local script="bin/vde-check-pr-evidence.zsh"
    local -a envs extra
    shift 5
    extra=( "$@" )
    envs=( HOME="${CHK_HOME}" PATH="${PATH}" VDE_PR_AUTHOR="${author}" VDE_PR_HEAD_REF="${head}" VDE_PR_HEAD_REPO="${HEAD_REPO}" VDE_PR_BASE_REPO="${BASE_REPO}" )
    if [[ "${mode}" == set ]]; then
        envs+=( VDE_PR_BODY="${body}" )
    fi
    [[ "${cwd}" == "${ROOT}" ]] || script="${CHECK}"
    raw="$(cd "${cwd}" && env -i "${envs[@]}" zsh "${script}" "${extra[@]}" 2>&1; print -r -- "RC=$?")"
    RC="${raw##*RC=}"
    OUT="${raw%RC=*}"
}

assert_pass() {  # assert_pass TITLE: the exit status is exactly 0
    if [[ "${RC}" == 0 ]]; then
        test_pass "$1"
    else
        test_fail "$1" "rc=${RC} (expected 0): ${OUT[1,200]//$'\n'/ | }"
    fi
}

assert_fail() {  # assert_fail TITLE RULE_RE: the exit status is exactly 1 and the output names the rule (RULE_RE is lower case)
    if [[ "${RC}" == 1 && "${(L)OUT}" =~ $2 ]]; then
        test_pass "$1"
    else
        test_fail "$1" "rc=${RC} (expected 1 and a message matching /$2/): ${OUT[1,200]//$'\n'/ | }"
    fi
}

assert_exempt() {  # assert_exempt TITLE: the exit status is exactly 0 and the output says the change is exempt
    if [[ "${RC}" == 0 && "${(L)OUT}" == *exempt* ]]; then
        test_pass "$1"
    else
        test_fail "$1" "rc=${RC} (expected 0 and a message saying exempt): ${OUT[1,200]//$'\n'/ | }"
    fi
}

pass_case() {  # pass_case TITLE MODE AUTHOR HEAD BODY
    test_start "$1"
    run_check "${ROOT}" "$2" "$3" "$4" "$5"
    assert_pass "$1"
}

rule_fail_case() {  # rule_fail_case TITLE RULE_RE MODE AUTHOR HEAD BODY
    test_start "$1"
    run_check "${ROOT}" "$3" "$4" "$5" "$6"
    assert_fail "$1" "$2"
}

exempt_case() {  # exempt_case TITLE AUTHOR HEAD: an empty body, so the exemption is the only reason for exit 0
    test_start "$1"
    run_check "${ROOT}" set "$2" "$3" ''
    assert_exempt "$1"
}

injection_case() {  # injection_case TITLE BODY: the body is text; it must not run, and the verdict is the rules' verdict
    local title="$1" body="$2" wd="${SCRATCH}/injection-wd"
    test_start "${title}"
    rm -rf -- "${wd}"
    mkdir -p "${wd}" || { test_fail "${title}" "could not create the scratch cwd ${wd}"; return 0; }
    run_check "${wd}" set deryl feature/x "${body}"
    if [[ -e "${wd}/SENTINEL" ]]; then
        test_fail "${title}" "SENTINEL was created in the cwd: the body was executed"
    elif [[ "${RC}" == 0 ]]; then
        test_pass "${title}"
    else
        test_fail "${title}" "rc=${RC} (expected 0: a fenced body with RED and GREEN passes the rules as text): ${OUT[1,200]//$'\n'/ | }"
    fi
}

# ---------------------------------------------------------------------------
# Pass cases: RED and GREEN words with a fenced block of literal output
# ---------------------------------------------------------------------------

typeset body

body="$(print -l -- 'RED: the check fails before the fix' 'GREEN: the check passes after it' '```' 'ok 1 - literal output' '```')"
pass_case "P1 RED and GREEN with a backtick-fenced literal output block: exit 0" set deryl feature/x "${body}"

body=$'RED\r\nGREEN\r\n```\r\nok 1 - literal output\r\n```\r\n'
pass_case "P2 a CRLF body with RED, GREEN and a fenced block: exit 0" set deryl feature/x "${body}"

body="$(print -l -- 'RED' 'GREEN' '~~~' 'ok 1 - literal output' '~~~')"
pass_case "P3 a tilde-fenced literal output block: exit 0" set deryl feature/x "${body}"

# ---------------------------------------------------------------------------
# Fail cases: each names the rule that failed, and exits 1
# ---------------------------------------------------------------------------

rule_fail_case "F1 an empty body fails rule (a): exit 1 naming rule (a)" 'rule \(a\)' set deryl feature/x ''

rule_fail_case "F2 an unset body fails rule (a): exit 1 naming rule (a)" 'rule \(a\)' unset deryl feature/x ''

body="$(print -l -- 'GREEN' '```' 'ok 1 - literal output' '```')"
rule_fail_case "F3 no RED word fails rule (a): exit 1 naming rule (a)" 'rule \(a\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED' '```' 'ok 1 - literal output' '```')"
rule_fail_case "F4 no GREEN word fails rule (a): exit 1 naming rule (a)" 'rule \(a\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED GREEN' 'ok 1 - no fence here')"
rule_fail_case "F5 no fenced code block fails rule (b): exit 1 naming rule (b)" 'rule \(b\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED GREEN' '```' '```')"
rule_fail_case "F6 an empty fenced block fails rule (b): exit 1 naming rule (b)" 'rule \(b\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED GREEN' '```' '' '   ' '```')"
rule_fail_case "F7 a fenced block of only blank lines fails rule (b) or (d): exit 1 naming the rule" 'rule \(b\)|rule \(d\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED GREEN' '```' '(Paste terminal output here)' '```')"
rule_fail_case "F8 a fenced block holding only the placeholder fails rule (b), (c) or (d): exit 1 naming the rule" 'rule \(b\)|rule \(c\)|rule \(d\)' set deryl feature/x "${body}"

body="$(print -l -- 'RED GREEN' '```' 'ok 1 - literal output' '```' '(Paste terminal output here)')"
rule_fail_case "F9 the placeholder text anywhere in the body fails rule (c): exit 1 naming rule (c)" 'rule \(c\)' set deryl feature/x "${body}"

# ---------------------------------------------------------------------------
# Exempt cases: dependabot[bot], and a head ref that is exactly develop or stable
# ---------------------------------------------------------------------------

exempt_case "E1 author dependabot[bot] is exempt: exit 0 and says so, with an empty body" 'dependabot[bot]' feature/x
exempt_case "E2 head ref exactly develop is exempt: exit 0 and says so, with an empty body" deryl develop
exempt_case "E3 head ref exactly stable is exempt: exit 0 and says so, with an empty body" deryl stable

rule_fail_case "N1 head ref develop-x is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl develop-x ''
rule_fail_case "N2 head ref my/develop is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl my/develop ''
rule_fail_case "N3 head ref feature/stable is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl feature/stable ''
HEAD_REPO=attacker/repo
rule_fail_case "N4 head ref develop from a FORK is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl develop ''
rule_fail_case "N5 head ref stable from a FORK is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl stable ''
HEAD_REPO='' BASE_REPO=''
rule_fail_case "N6 head ref develop with no repository named is NOT exempt: exit 1 naming rule (a)" 'rule \(a\)' set deryl develop ''
HEAD_REPO=owner/repo BASE_REPO=owner/repo

# ---------------------------------------------------------------------------
# Exit 2: a usage error (an argument the script does not take)
# ---------------------------------------------------------------------------

test_start "X1 an extra argument is a usage error: exit 2 with a message"
body="$(print -l -- 'RED GREEN' '```' 'ok 1 - literal output' '```')"
run_check "${ROOT}" set deryl feature/x "${body}" unexpected-argument
if [[ "${RC}" == 2 && -n "${OUT}" ]]; then
    test_pass "X1 exit 2 with a message for an extra argument"
else
    test_fail "X1 exit 2 with a message for an extra argument" "rc=${RC} (expected 2): ${OUT[1,200]//$'\n'/ | }"
fi

# ---------------------------------------------------------------------------
# Injection: the body is data. Each must NOT create the sentinel in the cwd, and the verdict is the rules' verdict.
# Each body is a fenced block with RED and GREEN, so the rules pass it as text.
# ---------------------------------------------------------------------------

body="$(print -l -- 'RED GREEN' '```' '$(touch SENTINEL)' '```')"
injection_case "I1 a body holding \$(touch SENTINEL) does not run it: no sentinel, verdict by the rules" "${body}"

body="$(print -l -- 'RED GREEN' '```' '`touch SENTINEL`' '```')"
injection_case "I2 a body holding backticks around touch SENTINEL does not run it: no sentinel, verdict by the rules" "${body}"

body="$(print -l -- 'RED GREEN' '```' '${IFS}' '```')"
injection_case "I3 a body holding \${IFS} is not expanded: no sentinel, verdict by the rules" "${body}"

body="$(print -l -- 'RED GREEN' '```' 'ok 1; touch SENTINEL' '```')"
injection_case "I4 a body holding '; touch SENTINEL' does not run it: no sentinel, verdict by the rules" "${body}"

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
