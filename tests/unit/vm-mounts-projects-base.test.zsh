#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: get_vm_mounts honors the configured Projects base (Signet #566).
#
# get_vm_mounts used to hardcode "projects/<name>" and
# "projects/python/jupyterlabs", so anything consuming the string pointed at the
# repo-local folder while the Compose volume resolved to a custom base
# (split-brain). With no override the output stays relative and unchanged; with
# an override the source is "<base>/<name>".
#
# Hermetic: the base lives in a mktemp sandbox; the repo .env is neither read nor touched
# (its reader is replaced below; VDE_ROOT_DIR stays the real repo for the registry, and
# VDE_PROJECTS_DIR is set in the environment, which outranks .env).

# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
source "${VDE_ROOT_DIR}/lib/vde-constants" &>/dev/null
source "${VDE_ROOT_DIR}/lib/vm-common"     &>/dev/null
# The checkout's local .env is not part of these cases: replace its reader so the
# unset-variable defaults below do not depend on it.
vde_projects_dir_from_env_file() { return 0; }

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

# Second '|' field of get_vm_mounts is the workspace/data mount.
_mount_of() { local -a f; f=("${(@s:|:)$(get_vm_mounts "$1")}"); print -r -- "${f[2]}"; }
check() {  # <label> <expected> <actual>
    if [[ "$3" == "$2" ]]; then test_pass "$1"; else test_fail "$1" "expected '$2', got '$3'"; fi
}

unset VDE_PROJECTS_DIR
test_start "default (no override): language mount stays relative and unchanged"
check "python"     "projects/python:/home/devuser/workspace" "$(_mount_of python)"
test_start "default (no override): jupyterlab keeps its special path"
check "jupyterlab" "projects/python/jupyterlabs:/home/devuser/workspace" "$(_mount_of jupyterlab)"

typeset BASE="/tmp/vde-mounts-base-test/projects"
export VDE_PROJECTS_DIR="${BASE}"
test_start "override: language mount uses the configured base"
check "python"     "${BASE}/python:/home/devuser/workspace" "$(_mount_of python)"
test_start "override: jupyterlab uses the configured base"
check "jupyterlab" "${BASE}/python/jupyterlabs:/home/devuser/workspace" "$(_mount_of jupyterlab)"
test_start "override: service data mount is NOT affected (data/ is not the projects base)"
check "postgres"   "data/postgres:/var/lib/postgresql/data" "$(_mount_of postgres)"
unset VDE_PROJECTS_DIR

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
