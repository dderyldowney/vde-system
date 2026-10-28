#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: the script-documentation checks read the live doc and fail loudly
# when it is missing (Signet #530).
#
# bin/vde-gospel-audit.zsh and bin/vde-heal-docs.zsh pointed at the migrated-away
# docs/available-scripts.md behind an `[[ -f ]]` guard, so the cross-reference
# silently never ran. Both must target docs/reference/scripts.md, and a missing
# doc must be a hard failure (audit exits non-zero) rather than a silent pass.

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

typeset -a scripts=(bin/vde-gospel-audit.zsh bin/vde-heal-docs.zsh)
typeset s
for s in ${scripts}; do
    test_start "${s} targets docs/reference/scripts.md, not the stale path"
    typeset body="$(<${s})"
    if [[ "${body}" == *'AVAILABLE_SCRIPTS_DOC="./docs/reference/scripts.md"'* && "${body}" != *available-scripts.md* ]]; then
        test_pass "${s} path"
    else
        test_fail "${s} path" "still references docs/available-scripts.md"
    fi
done

# Build a sandbox mirroring the repo (symlinks) minus docs/reference/scripts.md.
typeset sandbox="$(mktemp -d)"
trap 'rm -rf "${sandbox}"' EXIT
typeset e
for e in ${VDE_ROOT_DIR}/*(N) ${VDE_ROOT_DIR}/.[^.]*(N); do
    [[ "${e:t}" == (docs|.git) ]] && continue
    ln -s "${e}" "${sandbox}/${e:t}"
done
mkdir -p "${sandbox}/docs/reference"
for e in ${VDE_ROOT_DIR}/docs/*(N); do
    [[ "${e:t}" == reference ]] && continue
    ln -s "${e}" "${sandbox}/docs/${e:t}"
done
for e in ${VDE_ROOT_DIR}/docs/reference/*(N); do
    [[ "${e:t}" == scripts.md ]] && continue
    ln -s "${e}" "${sandbox}/docs/reference/${e:t}"
done

test_start "gospel audit fails when the script documentation file is missing"
typeset out rc
out="$(cd "${sandbox}" && zsh bin/vde-gospel-audit.zsh 2>&1)"; rc=$?
if (( rc != 0 )) && [[ "${out}" == *"scripts.md"* ]]; then
    test_pass "missing doc is a hard failure"
else
    test_fail "missing doc" "rc=${rc}; output: ${out[-300,-1]}"
fi

test_start "self-healer fails before any write when the script documentation file is missing"
out="$(cd "${sandbox}" && zsh bin/vde-heal-docs.zsh 2>&1)"; rc=$?
if (( rc != 0 )) && [[ "${out}" == *"scripts.md"* && "${out}" != *"Synchronizing Version Baseline"* ]]; then
    test_pass "heal guard fires first"
else
    test_fail "heal missing doc" "rc=${rc}; output: ${out[-300,-1]}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
