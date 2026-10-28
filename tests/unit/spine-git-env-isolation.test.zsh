#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit Tests for the spine check's Pillar II git probe (Signet #493).
#
# Pillar II runs a throwaway `git init` in a temp directory. Under a git hook
# launched from a linked worktree git exports GIT_DIR=<repo>/.git/worktrees/<name>;
# an unscrubbed `git init` then re-initialises that gitdir instead of the temp
# directory and writes core.bare=true into the shared config. These tests rebuild
# that situation with a scratch repository and prove the probe leaves it alone,
# and that the probe still fails closed when git itself is broken.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

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

typeset SPINE="${VDE_ROOT_DIR}/bin/vde-spine-check.zsh"
typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }
trap 'rm -rf -- "${SCRATCH}"' EXIT

# git with the developer's repository-selecting variables removed.
clean_git() { env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR -u GIT_INDEX_FILE git "$@" }

# A scratch repository with one commit and one linked worktree. Environment is
# scrubbed so the developer's own GIT_* variables cannot leak into the fixture.
typeset REPO="${SCRATCH}/repo" WT="${SCRATCH}/wt"
clean_git init -q "${REPO}"
clean_git -C "${REPO}" \
    -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
clean_git -C "${REPO}" worktree add -q "${WT}" -b wt

typeset WT_GITDIR="${REPO}/.git/worktrees/wt"

core_bare() {
    clean_git -C "${REPO}" config --get core.bare
}

#-------------------------------------------------------------------------------
test_start "Pillar II probe under a linked worktree's GIT_DIR leaves core.bare unchanged"
typeset before=$(core_bare)
typeset spine_out
spine_out=$(env GIT_DIR="${WT_GITDIR}" zsh "${SPINE}" 2>&1)
typeset after=$(core_bare)
if [[ "${spine_out}" != *"Pillar II: Git is operational"* ]]; then
    test_fail "Pillar II probe did not run" "output: ${spine_out}"
elif [[ "${before}" == "false" && "${after}" == "false" ]]; then
    test_pass "core.bare stayed '${after}'"
else
    test_fail "core.bare changed" "before='${before}' after='${after}'"
    clean_git -C "${REPO}" config core.bare false
fi

#-------------------------------------------------------------------------------
test_start "Pillar II probe still fails closed when git init fails"
typeset SHIM="${SCRATCH}/shim"
mkdir -p "${SHIM}"
typeset REAL_GIT=$(command -v git)
print -r -- "#!/usr/bin/env zsh
[[ \"\$1\" == init ]] && exit 1
exec ${(q)REAL_GIT} \"\$@\"" > "${SHIM}/git"
chmod +x "${SHIM}/git"
typeset out rc=0
out=$(env PATH="${SHIM}:${PATH}" zsh "${SPINE}" --quiet 2>&1) || rc=$?
if (( rc != 0 )) && [[ "${out}" == *"Pillar II (Git) failed"* ]]; then
    test_pass "broken git init reported as Pillar II failure (rc=${rc})"
else
    test_fail "did not fail closed" "rc=${rc} out='${out}'"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
