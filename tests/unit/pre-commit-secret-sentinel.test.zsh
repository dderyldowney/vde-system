#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: the pre-commit Secret Sentinel (Rule 12) blocks hardcoded credentials
# and lets a pure pass-through of a variable through (Signet #666).
#
# Rule 12 rejects any ADDED line matching (API_KEY|SECRET|PASSWORD)\s*= . That also
# caught the Compose line that forwards POSTGRES_DEV_PASSWORD as NAME=${NAME:-}: it
# forwards a variable and carries no value. The rule now exempts exactly that
# shape: `=${NAME:-}` (EMPTY default) at the end of the line. Anything that can carry
# a literal stays blocked. Rule 12 had no test before this suite.
#
# Every case runs the REAL githooks/pre-commit in a scratch git repo.
#
# Cases:
#   1. a literal credential is blocked (names the rule and the file);
#   2. a pure `=${NAME:-}` pass-through is allowed;
#   3. a default that carries a literal (`=${NAME:-hunter2}`) is blocked;
#   4. a bare `=${NAME}` reference stays blocked (the exemption is not wider);
#   5. a pass-through next to a literal in the same file is blocked;
#   6. API_KEY and SECRET with spaces around `=` are blocked;
#   7. files under env-files/ keep their existing exemption.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

# Fixture isolation (Signet #656): drop the GIT_* variables that select a repository,
# index, objects or namespace, and the ones that inject config or hooks.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

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

typeset SCRATCH; SCRATCH="$(mktemp -d)"
trap 'rm -rf -- "${SCRATCH}"' EXIT

typeset HOOK="${VDE_ROOT_DIR}/githooks/pre-commit"
typeset HOOK_OUT HOOK_RC

# stage_and_run NAME RELPATH CONTENT -> fresh repo, stages RELPATH with CONTENT, runs the hook.
# Sets HOOK_OUT (ANSI stripped) and HOOK_RC.
stage_and_run() {
    local name="${1}" rel="${2}" content="${3}" r="${SCRATCH}/${1}"
    mkdir -p "${r}/lib" && git -C "${r}" init -q 2>/dev/null
    git -C "${r}" config user.email t@example.invalid
    git -C "${r}" config user.name t
    cp "${VDE_ROOT_DIR}/lib/vde-shibboleth" "${r}/lib/vde-shibboleth"
    print -r -- base > "${r}/README"
    git -C "${r}" add -A && git -C "${r}" commit -q -m base
    mkdir -p "${r}/${rel:h}"
    print -r -- "${content}" > "${r}/${rel}"
    git -C "${r}" add -A
    HOOK_OUT="$(cd "${r}" && zsh "${HOOK}" 2>&1)"
    HOOK_RC=$?
    HOOK_OUT="${HOOK_OUT//$'\033'\[[0-9;]#m/}"
}

# expect_blocked LABEL -> the last run must have exited 1 with the Rule 12 message
expect_blocked() {
    if (( HOOK_RC == 1 )) && [[ "${HOOK_OUT}" == *"Rule 12 Violation"* ]]; then
        test_pass "${1}"
    else
        test_fail "${1}" "rc=${HOOK_RC}, hook said: [${HOOK_OUT[1,200]}]"
    fi
}
# expect_allowed LABEL -> the last run must have passed
expect_allowed() {
    if (( HOOK_RC == 0 )); then
        test_pass "${1}"
    else
        test_fail "${1}" "rc=${HOOK_RC}, hook said: [${HOOK_OUT[1,200]}]"
    fi
}

# The lines are assembled from parts so that THIS file never carries a literal
# credential assignment itself (the same hook scans it when it is committed).
typeset PW='POSTGRES_DEV_''PASSWORD' AK='API_''KEY' SC='SE''CRET' PL='PASS''WORD'

test_start "1: a literal credential is blocked and the rule and file are named"
stage_and_run c1 deploy/compose.yml "      - ${PW}=hunter2"
expect_blocked "case1 literal value blocked"
[[ "${HOOK_OUT}" == *"deploy/compose.yml"* ]] \
    && test_pass "case1 the message names the file" \
    || test_fail "case1 the message names the file" "hook said: [${HOOK_OUT[1,200]}]"

test_start "2: a pure =\${NAME:-} pass-through is allowed"
stage_and_run c2 deploy/compose.yml "      - ${PW}=\${${PW}:-}"
expect_allowed "case2 pass-through with an empty default allowed"

test_start "3: a default that carries a literal is blocked"
stage_and_run c3 deploy/compose.yml "      - ${PW}=\${${PW}:-hunter2}"
expect_blocked "case3 \${NAME:-hunter2} blocked"

test_start "4: a bare \${NAME} reference is blocked (the exemption is exactly the :-} shape)"
stage_and_run c4 deploy/compose.yml "      - ${PW}=\${${PW}}"
expect_blocked "case4 \${NAME} without the empty default blocked"

test_start "5: a pass-through next to a literal in the same file is blocked"
stage_and_run c5 deploy/compose.yml "      - ${PW}=\${${PW}:-}
      - DB_${PL}=hunter2"
expect_blocked "case5 the literal is still found beside an exempt line"

test_start "6: API_KEY and SECRET with spaces around = are blocked"
stage_and_run c6a deploy/app.conf "${AK} = abc123"
expect_blocked "case6a an API_KEY assignment with spaces blocked"
stage_and_run c6b deploy/app.conf "client_${SC} = abc123"
expect_blocked "case6b a SECRET assignment with spaces blocked"

test_start "7: files under env-files/ keep their existing exemption"
stage_and_run c7 env-files/app.env "${PW}=hunter2"
expect_allowed "case7 env-files/ stays exempt"

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
