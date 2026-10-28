#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: bash/sh in scripts/setup/*.zsh is allowlisted (Signet #594).
#
# Mandate C forbids foreign shells. The unavoidable vendor installers are listed
# in docs/governance/bash-exceptions.md. Any other bash/sh invocation fails, and
# so does any listed entry that no longer matches a line (stale). Static scan
# only; no Docker, no writes.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset DOC="docs/governance/bash-exceptions.md"

# Allowlist rows: | `script` | `match` | reason |
typeset -a al_script al_match
typeset line
while IFS= read -r line; do
    if [[ "${line}" =~ '^\| `([^`]+)` \| `(.+)` \| ' ]]; then
        al_script+=("${match[1]}"); al_match+=("${match[2]}")
    fi
done < "${DOC}"

test_start "allowlist parses from ${DOC}"
if (( ${#al_script} > 0 )); then test_pass "found ${#al_script} entries (${(j:, :)al_script})"
else test_fail "allowlist" "no entries parsed"; fi

# Collect real invocations: non-comment lines with a bare bash/sh word.
typeset -a hits
typeset f n
for f in scripts/setup/*.zsh; do
    n=0
    while IFS= read -r line; do
        (( n++ ))
        [[ "${line}" =~ '^[[:space:]]*#' ]] && continue
        if [[ "${line}" =~ '(^|[[:space:];|&(/"'"'"'])(ba)?sh([[:space:])"'"'"']|$)' ]]; then
            hits+=("${f:t}:${n}:${line}")
        fi
    done < "${f}"
done

test_start "every bash/sh invocation in scripts/setup is allowlisted"
typeset hit file text i ok bad=0
for hit in "${hits[@]}"; do
    file="${hit%%:*}"; text="${hit#*:*:}"; ok=0
    for (( i = 1; i <= ${#al_script}; i++ )); do
        [[ "${al_script[i]}" == "${file}" && "${text}" == *"${al_match[i]}"* ]] && ok=1
    done
    (( ok )) || { test_fail "non-allowlisted shell" "${hit}"; bad=1; }
done
(( bad )) || test_pass "${#hits} invocation(s), all allowlisted"

test_start "no stale allowlist entries"
typeset stale=0 found
for (( i = 1; i <= ${#al_script}; i++ )); do
    found=0
    for hit in "${hits[@]}"; do
        [[ "${hit%%:*}" == "${al_script[i]}" && "${hit}" == *"${al_match[i]}"* ]] && (( found++ ))
    done
    (( found == 1 )) || { test_fail "stale or ambiguous entry (matches ${found} lines)" "${al_script[i]} :: ${al_match[i]}"; stale=1; }
done
(( stale )) || test_pass "all entries match a live line"

test_start "every allowlisted call site references the governance doc"
typeset miss=0
for (( i = 1; i <= ${#al_script}; i++ )); do
    grep -q 'docs/governance/bash-exceptions.md' "scripts/setup/${al_script[i]}" \
        || { test_fail "missing call-site comment" "${al_script[i]}"; miss=1; }
done
(( miss )) || test_pass "call-site comments present"

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
