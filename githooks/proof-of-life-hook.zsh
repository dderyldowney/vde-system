#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# githooks/proof-of-life-hook.zsh - Enforces Mandate L (Proof of Life)
# Part of the Pre-Strike Sentinel
typeset _ZSH_PURE=${(%):-%x}
set -e

# Determine VDE root directory
typeset VDE_ROOT_DIR=$(git rev-parse --show-toplevel)
export VDE_ROOT_DIR

# The gate runs against its own scratch Projects base, never the caller's.
source "${VDE_ROOT_DIR}/lib/vde-test-env" || { echo "[ERROR] cannot load lib/vde-test-env"; exit 1; }
vde_test_env_enter || { echo "[ERROR] cannot create a scratch Projects base"; exit 1; }

# Source core libraries
[[ -f "${VDE_ROOT_DIR}/lib/vde-shell-compat" ]] && source "${VDE_ROOT_DIR}/lib/vde-shell-compat"
[[ -f "${VDE_ROOT_DIR}/lib/vde-log" ]] && source "${VDE_ROOT_DIR}/lib/vde-log"
source "${VDE_ROOT_DIR}/lib/vde-pol-stamp"

# Colors
typeset RED='\033[0;31m'
typeset GREEN='\033[0;32m'
typeset RESET='\033[0m'

typeset _SENTINEL=${(U):-"sentinel active"}
echo "[${_SENTINEL}] Running Sovereign Audit (Rule A)..."
# The push gate refreshes origin/develop (one best-effort, non-prompting fetch) so the shrink-only baseline check is judged against the real base, not a stale cached ref (Signet #646).
if ! VDE_SHIB_REFRESH_BASE=1 zsh "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" --quiet; then
    echo -e "${RED}[ERROR] Sovereign Audit Failed. Push blocked.${RESET}"
    vde_test_env_leave
    exit 1
fi

echo "[${_SENTINEL}] Running Proof of Life (Mandate L) Validation..."
# ZSH-native shibboleth (Rule 1)
typeset _SENTINEL=${(U):-"sentinel active"}
echo "[${_SENTINEL}] Feature: tests/features/core-infrastructure/proof-of-life-the-contract.feature"

# Reuse (Signet #602): skip only when this exact tree already passed Proof of Life
# and the tracked worktree is clean. Anything weaker runs the full contract.
# The hook receives "<local ref> <local sha> <remote ref> <remote sha>" lines on
# stdin when run by git; every outgoing tree must be the stamped one.
typeset -a _pushed_shas=()
typeset _lref _lsha _rref _rsha
if [[ ! -t 0 ]]; then
    while read -r _lref _lsha _rref _rsha; do
        [[ -z "${_lsha//0/}" ]] || _pushed_shas+=("${_lsha}")
    done
fi
if vde_pol_push_covered HEAD "${_pushed_shas[@]}"; then
    echo -e "${GREEN}✓ Proof of Life already certified for this exact tree (stamp matched, worktree clean). Skipping rerun.${RESET}"
    vde_test_env_leave
    exit 0
fi

# The gate's two proofs run under ONE stamp (Signet #769): the Sovereign suite certifies the
# patchset (the code's own tests), the Proof of Life certifies the VDE core lifecycle. A stamp
# therefore means both passed for this exact clean tree. The suite runs first (cheaper, fails fast);
# a failing suite blocks the push, names the failing suite (the runner prints it) and the Proof of
# Life never starts. Return 3 = the suite failed or is missing, 2 = the Proof of Life failed, anything else = the gate itself could not run.
_gate_proofs() {
    if [[ ! -f "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" ]]; then
        echo -e "${RED}[ERROR] tests/run-sovereign-tests.zsh is missing. Push blocked.${RESET}"
        return 3
    fi
    echo "[${_SENTINEL}] Running the Sovereign suite (tests/run-sovereign-tests.zsh)..."
    # Git exports GIT_DIR (in a linked worktree, the worktree's git directory) and other repository-selecting
    # variables into a hook. The suites build their own throwaway git repositories, so with those variables
    # set their git commands land in the REAL repository (Signet #656). Run the suite without them.
    if ! env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR -u GIT_PREFIX -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES -u GIT_NAMESPACE -u GIT_CONFIG_COUNT -u GIT_CONFIG_PARAMETERS -u GIT_TEMPLATE_DIR zsh "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh"; then
        echo -e "${RED}[ERROR] Sovereign suite failed. Push blocked.${RESET}"
        echo -e "  The failing suite is named above. Run 'zsh tests/run-sovereign-tests.zsh' for details."
        return 3
    fi
    echo "[${_SENTINEL}] Running Proof of Life (Mandate L) Validation..."
    # We use the full path to ensure it runs correctly from any directory
    python3 -m behave "${VDE_ROOT_DIR}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" --quiet --no-summary || return 2
}
typeset -i _gate_rc=0
if vde_pol_run_and_stamp _gate_proofs; then
    echo -e "${GREEN}✓ Proof of Life Certified.${RESET}"
    vde_test_env_leave
    exit 0
else
    _gate_rc=$?
    if (( _gate_rc == 2 )); then
        echo -e "${RED}[ERROR] Mandate L Violation: Proof of Life Contract Failed.${RESET}"
        echo -e "  The core VM lifecycle is broken. Push blocked."
        echo -e "  Run 'python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature' for details."
    elif (( _gate_rc != 3 )); then
        echo -e "${RED}[ERROR] The pre-push gate could not run (status ${_gate_rc}). Push blocked.${RESET}"
    fi
    vde_test_env_leave
    exit 1
fi
