#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for the retired shibboleth baseline (Mandate C).
# The baseline must hold no entries, and every tracked zsh file must carry the
# shibboleth line within the window, with no exception.

typeset REPO="${0:A:h:h:h}"
source "${REPO}/lib/vde-shibboleth" || exit 1
typeset -i PASS=0 FAIL=0
check() {
  typeset desc="$1" cond="$2"
  if eval "${cond}"; then
    print -r -- "[PASS] ${desc}"; PASS+=1
  else
    print -r -- "[FAIL] ${desc}"; FAIL+=1
  fi
}

typeset -a ENTRIES
ENTRIES=(${(f)"$(grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' "${REPO}/docs/governance/shibboleth-baseline.txt")"})
check "the baseline holds no entries" '(( ${#ENTRIES} == 0 ))'

typeset -a MISSING
typeset f
for f in ${(f)"$(git -C "${REPO}" ls-files)"}; do
  vde_shib_excluded "${f}" && continue
  _vde_shib_is_zsh_file "${REPO}/${f}" || continue
  vde_shib_has_literal "${REPO}/${f}" || MISSING+=("${f}")
done
check "every tracked zsh file carries the shibboleth line (missing: ${#MISSING})" '(( ${#MISSING} == 0 ))'

print -r -- "Passed: ${PASS}  Failed: ${FAIL}"
(( FAIL == 0 ))
