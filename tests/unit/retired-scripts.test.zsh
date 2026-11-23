#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for retired scripts (1.5.8 hardening, item 20).
# A retired script must be gone from the tree, from the script reference and from
# the shibboleth baseline, and nothing tracked may refer to it.

typeset REPO="${0:A:h:h:h}"
typeset -i PASS=0 FAIL=0
check() {
  typeset desc="$1" cond="$2"
  if eval "${cond}"; then
    print -r -- "[PASS] ${desc}"; PASS+=1
  else
    print -r -- "[FAIL] ${desc}"; FAIL+=1
  fi
}

typeset -a RETIRED=(bin/vde-release.zsh)
typeset r
for r in "${RETIRED[@]}"; do
  check "${r}: the file is gone" '[[ ! -e "${REPO}/${r}" ]]'
  check "${r}: not in the script reference" '! grep -qF -- "${r:t}" "${REPO}/docs/reference/scripts.md"'
  check "${r}: not in the shibboleth baseline" '! grep -qF -- "${r}" "${REPO}/docs/governance/shibboleth-baseline.txt"'
  check "${r}: no tracked file other than this test refers to it" \
    '[[ -z "$(git -C "${REPO}" grep -lF -- "${r:t}" -- . ":(exclude)tests/unit/retired-scripts.test.zsh")" ]]'
done

print -r -- "Passed: ${PASS}  Failed: ${FAIL}"
(( FAIL == 0 ))
