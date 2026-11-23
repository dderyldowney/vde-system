#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit tests for the agent merge-method policy (Signet #744).
#
# Agents merge pull requests with a MERGE COMMIT only. Squash and rebase are
# disabled in the repository settings, so every merge-facing file must say so:
# each `gh pr merge` it shows carries --merge, and --squash or --rebase appears
# only inside a prohibition.
#
# The scan covers the agent-facing files plus the workflow guides. Checks 1 and 2
# run on every scanned file, one check per file.
# Check 3 (one per agent-facing file) requires every `gh pr merge` line in an
# agent file to carry --match-head-commit, --subject and --body. Checks 4-N pin
# the wording the merge rule relies on in the entry points and the skills.

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
# Conditions must not contain repository paths: use file_has for file contents.
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

# file_has <relpath> <string>
# True when the repository file exists and contains the fixed string. It reads
# the repository path itself, so no path is ever interpolated into eval text.
file_has() {
    [[ -f "${REPO}/$1" ]] && grep -qF -- "$2" "${REPO}/$1"
}

# prohibits_flags <line>
# True when every --squash and --rebase on the line has the word never (or Never,
# NEVER) within 45 characters before or after that occurrence. A line without
# either flag passes. The window is per occurrence, so a prohibition on one part
# of a line does not excuse a flag elsewhere on the same line.
prohibits_flags() {
    typeset line="$1"
    typeset flag before after
    typeset -i i len=${#1} fend start aft_from aft_to
    typeset -r window=45
    typeset -r never_re='(^|[^[:alpha:]])(never|Never|NEVER)([^[:alpha:]]|$)'
    for (( i = 1; i + 7 <= len; i++ )); do
        fend=i+7
        flag="${line[i,fend]}"
        [[ "${flag}" == '--squash' || "${flag}" == '--rebase' ]] || continue
        start=i-window
        (( start < 1 )) && start=1
        before=""
        (( i > 1 )) && before="${line[start,i-1]}"
        aft_from=i+8
        aft_to=i+7+window
        after="${line[aft_from,aft_to]}"
        # Only the same sentence counts: cut the window at the nearest sentence break.
        before="${before##*(. |; |\! |\? )}"
        after="${after%%(. |; |\! |\? )*}"
        [[ "${before}" =~ ${never_re} || "${after}" =~ ${never_re} ]] || return 1
    done
    return 0
}

# Self-check of the matcher. The loose wording passed the old rule only because
# it contains "disabled"; the matcher must reject it and accept a real Never.
typeset SELF_LOOSE='Use `--squash` when the setting is disabled'
typeset SELF_STRICT='Never `--squash` or `--rebase` here'
check "the prohibition matcher rejects a loose prohibition (no never nearby)" '! prohibits_flags "${SELF_LOOSE}"' "loose wording was accepted"
typeset SELF_CROSS='Use `--squash` now. Never mind the rest of this line'
check "the prohibition matcher rejects a never in the next sentence" '! prohibits_flags "${SELF_CROSS}"' "cross-sentence never was accepted"
check "the prohibition matcher accepts a Never prohibition" 'prohibits_flags "${SELF_STRICT}"' "Never prohibition was rejected"

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

# The other merge-facing files: the workflow guides.
typeset -a OTHER_FILES
OTHER_FILES=(
    "${REPO}"/docs/context/workflows/*.md(N)
)

typeset -a SCAN_FILES
SCAN_FILES=("${AGENT_FILES[@]}" "${OTHER_FILES[@]}")

typeset -i SCANNED=0
typeset f line rel
typeset -i n is_agent
typeset -a file_lines
for f in "${AGENT_FILES[@]}"; do
    [[ -f "${f}" ]] && SCANNED+=1
done

check "the scan read at least 20 agent-facing files" "[[ \${SCANNED} -ge 20 ]]" "scanned=${SCANNED}"

# Checks 1, 2 and 3, one check per file.
typeset BAD_MERGE BAD_SQUASH BAD_FULL
for f in "${SCAN_FILES[@]}"; do
    [[ -f "${f}" ]] || continue
    rel="${f#${REPO}/}"
    is_agent=0
    (( ${AGENT_FILES[(Ie)${f}]} )) && is_agent=1
    # Join backslash-continued lines so a wrapped command is checked as one command.
    file_lines=("${(@f)$(<"${f}")}")
    typeset -a joined=()
    typeset acc=""
    for line in "${file_lines[@]}"; do
        if [[ "${line}" == *'\' ]]; then
            acc+="${line%\\}"
        else
            joined+=("${acc}${line}")
            acc=""
        fi
    done
    [[ -n "${acc}" ]] && joined+=("${acc}")
    file_lines=("${joined[@]}")
    BAD_MERGE=""
    BAD_SQUASH=""
    BAD_FULL=""
    n=0
    for line in "${file_lines[@]}"; do
        n+=1
        if [[ "${line}" == *'gh pr merge'* && "${line}" != *'--merge'* ]]; then
            BAD_MERGE+=" ${rel}:${n}"
        fi
        if ! prohibits_flags "${line}"; then
            BAD_SQUASH+=" ${rel}:${n}"
        fi
        # Every documented command carries the full flag set, in every scanned file.
        if true; then
            if [[ "${line}" == *'gh pr merge'* ]] && [[ "${line}" != *'--match-head-commit'* || "${line}" != *'--subject'* || "${line}" != *'--body'* ]]; then
                BAD_FULL+=" ${rel}:${n}"
            fi
        fi
    done
    check "${rel}: every gh pr merge line carries --merge" "[[ -z \"\${BAD_MERGE}\" ]]" "lines without --merge:${BAD_MERGE}"
    check "${rel}: --squash and --rebase appear only in a prohibition" "[[ -z \"\${BAD_SQUASH}\" ]]" "lines without never/disabled:${BAD_SQUASH}"
    if true; then
        check "${rel}: every gh pr merge line carries --match-head-commit, --subject and --body" "[[ -z \"\${BAD_FULL}\" ]]" "lines missing a required flag:${BAD_FULL}"
    fi
done

# Checks 4-N: the wording the merge rule relies on.
check "CLAUDE.md gives the exact merge command" "file_has CLAUDE.md 'gh pr merge N --merge --delete-branch'" "string missing from CLAUDE.md"

for f in CLAUDE.md AGENTS.md .gemini/instructions.md .gemini/STATE/handoff.md; do
    check "${f} names the merge commit" "file_has ${f} 'merge commit'" "'merge commit' missing or file absent"
done

check "CLAUDE.md states that merge approval is per PR" "file_has CLAUDE.md 'explicit written approval for that PR'" "string missing from CLAUDE.md"
check "CLAUDE.md states that squash and rebase are disabled" "file_has CLAUDE.md 'squash and rebase are disabled'" "string missing from CLAUDE.md"

check "CLAUDE.md pins --match-head-commit" "file_has CLAUDE.md '--match-head-commit'" "string missing from CLAUDE.md"
check "CLAUDE.md names untrusted input" "file_has CLAUDE.md 'untrusted input'" "string missing from CLAUDE.md"
check "CLAUDE.md names the permanent branch" "file_has CLAUDE.md 'permanent branch'" "string missing from CLAUDE.md"
check "CLAUDE.md names promotion" "file_has CLAUDE.md 'promotion'" "string missing from CLAUDE.md"

check "git-manager.md pins --match-head-commit" "file_has .gemini/SKILLS/git-manager.md '--match-head-commit'" "string missing or file absent"
check "git-manager.md names item NN" "file_has .gemini/SKILLS/git-manager.md 'item NN'" "string missing or file absent"

check "AGENTS.md pins --match-head-commit" "file_has AGENTS.md '--match-head-commit'" "string missing from AGENTS.md"
check "AGENTS.md names the permanent branch" "file_has AGENTS.md 'permanent branch'" "string missing from AGENTS.md"

check "handoff.md pins --match-head-commit" "file_has .gemini/STATE/handoff.md '--match-head-commit'" "string missing or file absent"
check "handoff.md names the permanent branch" "file_has .gemini/STATE/handoff.md 'permanent branch'" "string missing or file absent"

#-------------------------------------------------------------------------------
echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
