#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: two unit suites must not depend on the checkout's local
# configuration file (.env at the repository root).
#
# Each suite runs against a sandbox root: a directory of symlinks to every
# top-level entry of the real repository except the local configuration file
# and .git, plus a regular local configuration file that sets a non-default
# VDE_PROJECTS_DIR. With that file present both suites must still pass, because
# they must not depend on the checkout's local configuration. A control run with
# the file removed shows the sandbox itself is sound, so a failure with the file
# present is about the file.

typeset REPO="${0:A:h:h:h}"

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

# check <label> <condition> <detail>: evals the condition string.
check() {
    if eval "$2"; then
        test_pass "$1"
    else
        test_fail "$1" "$3"
    fi
}

typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "setup error: mktemp failed"; exit 1; }
SCRATCH="${SCRATCH:A}"
trap 'rm -rf -- "${SCRATCH}"' EXIT

typeset SANDBOX="${SCRATCH}/root"
typeset PROJECTS_DIR="${SCRATCH}/projects-base"
typeset SCRATCH_HOME="${SCRATCH}/home"
mkdir -p "${SANDBOX}" "${PROJECTS_DIR}" "${SCRATCH_HOME}" || { echo "setup error: mkdir failed"; exit 1; }

# Symlink farm: every top-level entry of the real repo (dotfiles included)
# except the local configuration file and .git.
typeset _entry
for _entry in "${REPO}"/*(DN); do
    [[ "${_entry:t}" == ".env" || "${_entry:t}" == ".git" ]] && continue
    ln -s "${_entry}" "${SANDBOX}/${_entry:t}" || { echo "setup error: symlink failed for ${_entry:t}"; exit 1; }
done

# The local configuration file under test: a regular file persisting a
# non-default projects base that really exists.
typeset SANDBOX_ENV="${SANDBOX}/.env"
print -r -- "VDE_PROJECTS_DIR=${PROJECTS_DIR}" > "${SANDBOX_ENV}"

# run_suite <suite-name> <output-file>: prints the suite's exit status.
run_suite() {
    local rc
    env -u VDE_PROJECTS_DIR HOME="${SCRATCH_HOME}" VDE_ROOT_DIR="${SANDBOX}" VDE_CI_MODE=1 \
        timeout 200 zsh "${REPO}/tests/unit/$1.test.zsh" </dev/null >"$2" 2>&1
    rc=$?
    print -r -- "${rc}"
}

typeset REAL_ENV="${REPO}/.env"
typeset ENV_BEFORE="absent"
[[ -e "${REAL_ENV}" ]] && ENV_BEFORE=$(stat -c '%Y:%s' "${REAL_ENV}")

typeset OUT_PATH="${SCRATCH}/path-with-env.out"
typeset OUT_MOUNTS="${SCRATCH}/mounts-with-env.out"
typeset RC_PATH RC_MOUNTS
RC_PATH=$(run_suite vde-path-utils "${OUT_PATH}")
RC_MOUNTS=$(run_suite vm-mounts-projects-base "${OUT_MOUNTS}")

test_start "vde-path-utils passes against a root whose local configuration file sets VDE_PROJECTS_DIR"
check "vde-path-utils with local file" \
    '[[ "${RC_PATH}" == 0 ]]' \
    "exit ${RC_PATH}; last line: $(tail -n 1 "${OUT_PATH}" 2>/dev/null)"

test_start "vm-mounts-projects-base passes against a root whose local configuration file sets VDE_PROJECTS_DIR"
check "vm-mounts-projects-base with local file" \
    '[[ "${RC_MOUNTS}" == 0 ]]' \
    "exit ${RC_MOUNTS}; last line: $(tail -n 1 "${OUT_MOUNTS}" 2>/dev/null)"

# Control: remove the local configuration file and run both suites again.
rm -f -- "${SANDBOX_ENV}"
typeset OUT_CTRL_PATH="${SCRATCH}/path-control.out"
typeset OUT_CTRL_MOUNTS="${SCRATCH}/mounts-control.out"
typeset RC_CTRL_PATH RC_CTRL_MOUNTS
RC_CTRL_PATH=$(run_suite vde-path-utils "${OUT_CTRL_PATH}")
RC_CTRL_MOUNTS=$(run_suite vm-mounts-projects-base "${OUT_CTRL_MOUNTS}")

test_start "control: both suites pass with the local configuration file removed (sandbox is sound)"
check "control vde-path-utils without local file" \
    '[[ "${RC_CTRL_PATH}" == 0 ]]' \
    "exit ${RC_CTRL_PATH}; last line: $(tail -n 1 "${OUT_CTRL_PATH}" 2>/dev/null)"
check "control vm-mounts-projects-base without local file" \
    '[[ "${RC_CTRL_MOUNTS}" == 0 ]]' \
    "exit ${RC_CTRL_MOUNTS}; last line: $(tail -n 1 "${OUT_CTRL_MOUNTS}" 2>/dev/null)"

# The real repository's local configuration file must be untouched.
test_start "the real repository's local configuration file was not read or modified"
typeset ENV_AFTER="absent"
[[ -e "${REAL_ENV}" ]] && ENV_AFTER=$(stat -c '%Y:%s' "${REAL_ENV}")
if [[ "${ENV_BEFORE}" == "absent" ]]; then
    test_pass "real repository local configuration file is absent (nothing to compare; skipped)"
else
    check "real repository local configuration file unchanged" \
        '[[ "${ENV_BEFORE}" == "${ENV_AFTER}" ]]' \
        "stat before ${ENV_BEFORE}, after ${ENV_AFTER}"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
