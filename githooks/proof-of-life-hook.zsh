#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# githooks/proof-of-life-hook.zsh - Enforces Mandate L (Proof of Life), commit by commit (Signet #770)
# Part of the Pre-Strike Sentinel
#
# The orchestrator. It works out which commits a push carries (oldest first), certifies each one
# through lib/vde-gate-commits (the commit's tree is checked in a throwaway worktree and stamped per
# tree), and the checks themselves run inside githooks/gate-tree.zsh. Every pushed ref's tip (the
# commit each ref points to after the push, peeled through annotated tags) gets the full tier, and so
# does the newest commit of the list; every other commit gets the fast tier. A manual run (no ref
# lines on stdin) certifies HEAD in full and refuses a dirty tracked worktree. An interrupt (INT or
# TERM) removes the throwaway worktrees and blocks the push.
typeset _ZSH_PURE=${(%):-%x}

# Determine VDE root directory
typeset VDE_ROOT_DIR
VDE_ROOT_DIR="$(git rev-parse --show-toplevel)" || { echo "[ERROR] not inside a git repository"; exit 1; }
export VDE_ROOT_DIR

# lib/vde-gate-commits defines _VDE_GATE_SCRUB: the variables that select a repository for git. Every
# git call that targets the gate's own repository with -C runs with these unset, so a caller's
# environment cannot redirect it. It is sourced first because the prune below already uses it.
source "${VDE_ROOT_DIR}/lib/vde-gate-commits" || { echo "[ERROR] cannot load lib/vde-gate-commits"; exit 1; }

# Clear any worktree registration left behind by an earlier run that was killed.
env "${_VDE_GATE_SCRUB[@]}" git -C "${VDE_ROOT_DIR}" worktree prune >/dev/null 2>&1

# The gate runs against its own scratch Projects base, never the caller's.
source "${VDE_ROOT_DIR}/lib/vde-test-env" || { echo "[ERROR] cannot load lib/vde-test-env"; exit 1; }
vde_test_env_enter || { echo "[ERROR] cannot create a scratch Projects base"; exit 1; }

# Source core libraries
[[ -f "${VDE_ROOT_DIR}/lib/vde-shell-compat" ]] && source "${VDE_ROOT_DIR}/lib/vde-shell-compat"
[[ -f "${VDE_ROOT_DIR}/lib/vde-log" ]] && source "${VDE_ROOT_DIR}/lib/vde-log"
source "${VDE_ROOT_DIR}/lib/vde-pol-stamp" || { echo "[ERROR] cannot load lib/vde-pol-stamp"; vde_test_env_leave; exit 1; }

# Colors
typeset RED='\033[0;31m'
typeset GREEN='\033[0;32m'
typeset RESET='\033[0m'

# An interrupt removes the scratch area (and with it the throwaway worktrees), prunes their
# registrations, and blocks the push. These replace the defaults that vde_test_env_enter sets.
_vde_hook_interrupted() {
    vde_test_env_leave
    env "${_VDE_GATE_SCRUB[@]}" git -C "${VDE_ROOT_DIR}" worktree prune >/dev/null 2>&1
    echo -e "${RED}[ERROR] The gate was interrupted. Push blocked.${RESET}"
    exit "$1"
}
TRAPINT() { emulate -L zsh; _vde_hook_interrupted 130; }
TRAPTERM() { emulate -L zsh; _vde_hook_interrupted 143; }

echo "[SENTINEL ACTIVE] Gate: per-commit Proof of Life (Mandate L)"

# The hook receives "<local ref> <local sha> <remote ref> <remote sha>" lines on stdin when git runs it.
# Read them once: an interactive run (terminal stdin) or a run with no ref lines at all is a manual run.
typeset _ref_lines=""
if [[ ! -t 0 ]]; then
    _ref_lines="$(cat)"
fi
typeset -i _manual=0
[[ -z "${_ref_lines//[[:space:]]/}" ]] && _manual=1

typeset -a _commits=()
typeset -A _tips=()
typeset _range_out="" _peeled _lref _lsha _rref _rsha
if (( _manual )); then
    # Certifying HEAD says nothing about uncommitted edits, so the tracked worktree must be clean.
    vde_pol_clean_tree >/dev/null || {
        echo -e "${RED}[ERROR] The tracked worktree has uncommitted changes. A manual run certifies HEAD only; commit or stash them first. Push blocked.${RESET}"
        vde_test_env_leave
        exit 1
    }
    _commits=("$(git rev-parse --verify HEAD)")
    _tips[${_commits[1]}]=1
else
    # Every pushed ref's tip, peeled to its commit. A line that does not peel to a commit (a tree or
    # blob ref, or a deletion) names no tip.
    while read -r _lref _lsha _rref _rsha || [[ -n "${_lref}" ]]; do
        [[ -n "${_lsha}" && -n "${_lsha//0/}" ]] || continue
        _peeled="$(git rev-parse --verify --quiet "${_lsha}^{commit}")" || continue
        [[ -n "${_peeled}" ]] && _tips[${_peeled}]=1
    done <<< "${_ref_lines}"

    _range_out="$(print -r -- "${_ref_lines}" | vde_gate_range_commits "${1:-}")" || {
        echo -e "${RED}[ERROR] Could not list the commits being pushed. Push blocked.${RESET}"
        vde_test_env_leave
        exit 1
    }
    [[ -n "${_range_out}" ]] && _commits=("${(@f)_range_out}")
    if (( ${#_commits} == 0 )); then
        echo "nothing to certify (the push carries no new commits)"
        vde_test_env_leave
        exit 0
    fi
fi

typeset -i _total=${#_commits}
typeset -a _tiers=()
typeset -i _full_count=0 _i
typeset _c
for (( _i = 1; _i <= _total; _i++ )); do
    _c="${_commits[_i]}"
    # The newest commit is always a tip (belt and braces); any other commit that is a pushed tip too.
    if (( _i == _total )) || (( ${+_tips[${_c}]} )); then
        _tiers[_i]=full
        (( _full_count += 1 ))
    else
        _tiers[_i]=fast
    fi
done

typeset -i _earlier=$(( _total - _full_count ))
typeset _tip="${_commits[_total]}"
if (( _full_count == 1 )); then
    echo "${_earlier} earlier commit(s): fast check; tip ${_tip[1,7]}: full certification"
else
    echo "${_earlier} earlier commit(s): fast check; ${_full_count} tip(s) full certification"
fi

# Oldest first. Each commit is certified on its own tree; the first failure stops the push.
typeset -i _reused=0
typeset _tier
for (( _i = 1; _i <= _total; _i++ )); do
    _c="${_commits[_i]}"
    _tier="${_tiers[_i]}"
    if ! vde_gate_certify_commit "${VDE_ROOT_DIR}" "${_c}" "${_tier}"; then
        vde_test_env_leave
        exit 1
    fi
    # A reuse is a commit that vde_gate_certify_commit found already certified (it sets VDE_GATE_LAST_REUSED to 1).
    if (( ${VDE_GATE_LAST_REUSED:-0} == 1 )); then
        (( _reused += 1 ))
    fi
done

echo -e "${GREEN}✓ Proof of Life Certified.${RESET}"
if (( _full_count == 1 )); then
    echo "${_total} commit(s) checked (${_reused} reused), tip fully certified"
else
    echo "${_total} commit(s) checked (${_reused} reused), all tips fully certified"
fi
vde_test_env_leave
exit 0
