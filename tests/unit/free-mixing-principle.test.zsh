#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for the free-mixing design principle (Signet #761).
#
# Every Spoke on vde-net may use every other language and service Spoke freely, with no
# setup. vde-net is the trust boundary; security work hardens the boundary and each
# service's own privileges and never adds a gate between Spokes. The spec states it
# (docs/governance/vde-spec.md, section 6.1); the agent entry points carry a pointer in
# the READING LOCATIONS block so every session reads it; the philosophy document links
# back. This suite pins the wording each of them relies on.

typeset REPO="${0:A:h:h:h}"
typeset SPEC="docs/governance/vde-spec.md"

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset -i TEST_NO=0

if [[ -t 1 ]]; then
  typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
  typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { print -P "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { print -P "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { print -P "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }

# check <description> <condition> [detail]
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

# file_has <relpath> <string>: the repository file exists and contains the fixed string.
file_has() {
  [[ -f "${REPO}/$1" ]] && grep -qF -- "$2" "${REPO}/$1"
}

# --- the spec (the authority) -------------------------------------------------------------
check "the spec has the 6.1 free-mixing subsection" 'file_has "${SPEC}" "### 6.1 Design principle: free mixing"' "no 6.1 heading"
check "the spec sits after section 6 and before section 7" '[[ -f "${REPO}/${SPEC}" ]] && { typeset -i a b c; a=$(grep -n "^## 6\\. " "${REPO}/${SPEC}" | head -1 | cut -d: -f1); b=$(grep -n "^### 6\\.1 " "${REPO}/${SPEC}" | head -1 | cut -d: -f1); c=$(grep -n "^## 7\\. " "${REPO}/${SPEC}" | head -1 | cut -d: -f1); (( a > 0 && b > a && c > b )); }' "6.1 is not between section 6 and section 7"
check "the spec says every Spoke on vde-net uses every other freely" 'file_has "${SPEC}" "Every Spoke on \`vde-net\` may use every other language and service Spoke freely, with no setup"' "principle sentence missing"
check "the spec names vde-net as the trust boundary" 'file_has "${SPEC}" "The trust boundary is \`vde-net\`"' "trust boundary not stated"
check "the spec says security never adds a gate between Spokes" 'file_has "${SPEC}" "never adds a gate between Spokes"' "no-gate clause missing"
check "the spec names what security work does harden" 'file_has "${SPEC}" "published ports bind to loopback"' "hardening examples missing"
check "the spec carries the one-line test question" 'file_has "${SPEC}" "can student code in any Spoke still reach any service with no setup"' "test question missing"

# --- the agent entry points (read at the start of every session) -----------------------------
for _f in AGENTS.md .gemini/instructions.md; do
  check "${_f} READING LOCATIONS names the design principle" 'file_has "${_f}" "**Design principle:**"' "no Design principle bullet in ${_f}"
  check "${_f} points at the spec section" 'file_has "${_f}" "section 6.1"' "no pointer to spec section 6.1 in ${_f}"
  check "${_f} states free mixing" 'file_has "${_f}" "free mixing"' "no free-mixing wording in ${_f}"
done

# --- the philosophy document links back ----------------------------------------------------------
check "project-philosophy points at the spec principle" 'file_has "docs/governance/project-philosophy.md" "vde-spec.md" && file_has "docs/governance/project-philosophy.md" "free mixing"' "no pointer in project-philosophy.md"

print -P "\nTests passed: ${TESTS_PASSED}  failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
