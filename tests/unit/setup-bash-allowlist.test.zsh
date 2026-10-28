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

# Collect real invocations, one hit per bash/sh token (a line may hold several).
# A token is bash/sh at a command boundary: start, whitespace, ; | & ( / " ' \
# or a backslash; the hit text runs from the token to the end of the line.
typeset -a hits
typeset f n rest tok
typeset BOUND_RE='(^|[[:space:];|&(/"'"'"'\\])((ba)?sh)([[:space:];|&)"'"'"'\\]|$)'
for f in scripts/setup/*.zsh; do
    n=0
    while IFS= read -r line; do
        (( n++ ))
        [[ "${line}" =~ '^[[:space:]]*#' ]] && continue
        rest="${line}"
        while [[ "${rest}" =~ ${BOUND_RE} ]]; do
            tok=$(( MBEGIN + ${#match[1]} ))
            hits+=("${f:t}:${n}:${rest[tok,-1]}")
            rest="${rest[tok+${#match[2]},-1]}"
        done
    done < "${f}"
done

# Index of the first allowlist entry whose script and prefix match HIT (0 if none).
entry_for() {
    local h="$1" file="${1%%:*}" text="${1#*:*:}" k
    for (( k = 1; k <= ${#al_script}; k++ )); do
        [[ "${al_script[k]}" == "${file}" && "${text}" == "${al_match[k]}"* ]] && { echo ${k}; return; }
    done
    echo 0
}

test_start "every bash/sh invocation in scripts/setup is allowlisted"
typeset hit bad=0 i
typeset -a counts
for (( i = 1; i <= ${#al_script}; i++ )); do counts[i]=0; done
for hit in "${hits[@]}"; do
    i=$(entry_for "${hit}")
    if (( i )); then (( counts[i]++ )); else test_fail "non-allowlisted shell" "${hit}"; bad=1; fi
done
(( bad )) || test_pass "${#hits} invocation(s), all allowlisted"

test_start "no stale or ambiguous allowlist entries"
typeset stale=0
for (( i = 1; i <= ${#al_script}; i++ )); do
    (( counts[i] == 1 )) || { test_fail "stale or ambiguous entry (matches ${counts[i]} invocations)" "${al_script[i]} :: ${al_match[i]}"; stale=1; }
done
(( stale )) || test_pass "every entry matches exactly one live invocation"

test_start "every allowlisted call site references the governance doc"
typeset miss=0 ln lo k found
typeset -a src
for hit in "${hits[@]}"; do
    (( $(entry_for "${hit}") )) || continue
    f="scripts/setup/${hit%%:*}"; ln="${${hit#*:}%%:*}"
    src=("${(@f)$(<${f})}")
    found=0; lo=$(( ln > 12 ? ln - 12 : 1 ))
    for (( k = lo; k <= ln; k++ )); do
        [[ "${src[k]}" == *"docs/governance/bash-exceptions.md"* ]] && found=1
    done
    (( found )) || { test_fail "no governance reference within 12 lines above the call" "${hit%%:*}:${ln}"; miss=1; }
done
(( miss )) || test_pass "each call site references the governance doc"

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
