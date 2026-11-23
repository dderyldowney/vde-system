#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit tests for the agent merge-method policy (Signet #744).
#
# Agents merge pull requests with a MERGE COMMIT only. Squash and rebase are
# disabled in the repository settings, so every agent-facing file must say so:
# each `gh pr merge` it shows carries --merge, and --squash or --rebase appears
# only inside a prohibition.
#
# Checks 1 and 2 scan every agent-facing *.md file, one check per file. Checks
# 3-6 pin the wording the merge rule relies on in CLAUDE.md and the other entry
# points.

typeset REPO="${0:A:h:h:h}"

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

# The agent-facing files: entry points, then every *.md under the four agent folders.
typeset -a AGENT_FILES
AGENT_FILES=(
    "${REPO}/CLAUDE.md"
    "${REPO}/AGENTS.md"
    "${REPO}/.gemini/instructions.md"
    "${REPO}"/.gemini/STATE/**/*.md(N)
    "${REPO}"/.gemini/RULES/**/*.md(N)
    "${REPO}"/.gemini/SKILLS/**/*.md(N)
    "${REPO}"/.gemini/COMMANDS/**/*.md(N)
)

typeset -i SCANNED=0
typeset f line rel
typeset -i n
typeset -a file_lines
for f in "${AGENT_FILES[@]}"; do
    [[ -f "${f}" ]] && SCANNED+=1
done

check "the scan read at least 20 agent-facing files" "[[ \${SCANNED} -ge 20 ]]" "scanned=${SCANNED}"

# Checks 1 and 2, one check per file.
typeset BAD_MERGE BAD_SQUASH
for f in "${AGENT_FILES[@]}"; do
    [[ -f "${f}" ]] || continue
    rel="${f#${REPO}/}"
    file_lines=("${(@f)$(<"${f}")}")
    BAD_MERGE=""
    BAD_SQUASH=""
    n=0
    for line in "${file_lines[@]}"; do
        n+=1
        if [[ "${line}" == *'gh pr merge'* && "${line}" != *'--merge'* ]]; then
            BAD_MERGE+=" ${rel}:${n}"
        fi
        if [[ "${line}" == *'--squash'* || "${line}" == *'--rebase'* ]]; then
            if [[ "${line}" != *never* && "${line}" != *NEVER* && "${line}" != *disabled* ]]; then
                BAD_SQUASH+=" ${rel}:${n}"
            fi
        fi
    done
    check "${rel}: every gh pr merge line carries --merge" "[[ -z \"\${BAD_MERGE}\" ]]" "lines without --merge:${BAD_MERGE}"
    check "${rel}: --squash and --rebase appear only in a prohibition" "[[ -z \"\${BAD_SQUASH}\" ]]" "lines without never/disabled:${BAD_SQUASH}"
done

# Checks 3-6: the wording the merge rule relies on.
typeset CLAUDE_MD="${REPO}/CLAUDE.md"

check "CLAUDE.md gives the exact merge command" "grep -qF -- 'gh pr merge N --merge --delete-branch' '${CLAUDE_MD}'" "string missing from CLAUDE.md"

for f in CLAUDE.md AGENTS.md .gemini/instructions.md .gemini/STATE/handoff.md; do
    check "${f} names the merge commit" "[[ -f '${REPO}/${f}' ]] && grep -qF -- 'merge commit' '${REPO}/${f}'" "'merge commit' missing or file absent"
done

check "CLAUDE.md states that merge approval is per PR" "grep -qF -- 'explicit written approval for that PR' '${CLAUDE_MD}'" "string missing from CLAUDE.md"
check "CLAUDE.md states that squash and rebase are disabled" "grep -qF -- 'squash and rebase are disabled' '${CLAUDE_MD}'" "string missing from CLAUDE.md"

#-------------------------------------------------------------------------------
echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
