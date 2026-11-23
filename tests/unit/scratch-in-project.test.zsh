#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for the scratch-in-project policy (Signet #760).
#
# Scratch work (a scratch HOME, a scratch projects directory, logs and test
# evidence) lives under <project root>/.scratch/, not in /tmp or a tool's own
# scratch area. The rule file .gemini/RULES/scratch.md states it; the entry
# .gitignore keeps the directory out of git. This suite pins both.

typeset REPO="${0:A:h:h:h}"
typeset RULE=".gemini/RULES/scratch.md"

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

# --- the rule file ---------------------------------------------------------------------
check "the rule file exists" '[[ -f "${REPO}/${RULE}" ]]' "missing ${RULE}"
check "the rule carries the Forge header comment" 'file_has "${RULE}" "<!-- @forge (Governance Sentinel) -->"' "no @forge header"
check "the rule names the scratch root" 'file_has "${RULE}" ".scratch/"' "no .scratch/"
check "the rule names the scratch HOME location" 'file_has "${RULE}" ".scratch/h"' "no .scratch/h"
check "the rule names the scratch projects location" 'file_has "${RULE}" ".scratch/p"' "no .scratch/p"
check "the rule forbids /tmp and tool scratch areas" 'file_has "${RULE}" "/tmp"' "/tmp not named"
check "the rule states the unix socket path limit" 'file_has "${RULE}" "104"' "limit 104 not stated"
check "the rule protects the real HOME, ssh and projects" 'file_has "${RULE}" "~/.ssh" && file_has "${RULE}" "~/.zshrc"' "real-user paths not named"
check "the rule says to delete scratch when done" 'file_has "${RULE}" "deleted"' "no deletion duty"
check "the rule says it is never the user's data" 'file_has "${RULE}" "never"' "no never-clause"

check "the rule keeps the private security directory out of the project" 'file_has "${RULE}" "VDE_SECURITY_DIR"' "VDE_SECURITY_DIR exception not stated"
check "the rule says the private directory is permanent, not scratch" 'file_has "${RULE}" "is a separate, permanent location and is not scratch"' "split not explicit"
check "the rule routes ledger and weakness evidence to the private directory" 'file_has "${RULE}" "evidence that names an unfixed weakness"' "evidence routing not stated"
check "the rule routes private security items away from .scratch/ in the layout" 'file_has "${RULE}" "Anything private to a security item goes in the private security directory"' "layout bullet missing"

# --- the ignore entry --------------------------------------------------------------------
check ".gitignore has the exact /.scratch/ entry" 'grep -qxF "/.scratch/" "${REPO}/.gitignore"' "no /.scratch/ line"
check "git really ignores a file under .scratch/" 'git -C "${REPO}" check-ignore -q .scratch/h/.ssh/probe' "check-ignore says not ignored"
check "git does not ignore a look-alike outside it" '! git -C "${REPO}" check-ignore -q lib/.scratch-notes' "over-broad ignore"

print -P "\nTests passed: ${TESTS_PASSED}  failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
