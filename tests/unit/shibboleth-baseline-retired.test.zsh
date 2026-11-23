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

typeset BASE="${REPO}/docs/governance/shibboleth-baseline.txt"
check "the baseline file is readable" '[[ -r "${BASE}" ]]'
typeset -a ENTRIES
typeset ENTRIES_TEXT
ENTRIES_TEXT="$(grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' "${BASE}")"
ENTRIES=(${(f)ENTRIES_TEXT})
check "the baseline holds no entries" '[[ -r "${BASE}" ]] && (( ${#ENTRIES} == 0 ))'

# Controls: the matcher must accept a file that has the line and reject one that lacks it,
# so a broken helper cannot pass the sweep below.
typeset CTL="$(mktemp -d "${TMPDIR:-/tmp}/shib-retired.XXXXXX")"
print -r -- '#!/usr/bin/env zsh' > "${CTL}/with"; print -r -- 'typeset _ZSH_PURE=${(%):-%x}' >> "${CTL}/with"
print -r -- '#!/usr/bin/env zsh' > "${CTL}/without"; print -r -- 'print hi' >> "${CTL}/without"
check "control: a file with the line is accepted" 'vde_shib_has_literal "${CTL}/with"'
check "control: a file without the line is rejected" '! vde_shib_has_literal "${CTL}/without"'
check "control: a zsh shebang file is recognised as zsh" '_vde_shib_is_zsh_file "${CTL}/without"'
rm -rf -- "${CTL}"

typeset LS_OUT
LS_OUT="$(git -C "${REPO}" ls-files -z; print -r -- "RC=$?")"
check "git ls-files succeeds" '[[ "${LS_OUT##*RC=}" == 0 ]]'
typeset -a MISSING FILES
typeset -i SCANNED=0
typeset f
FILES=(${(0)"$(git -C "${REPO}" ls-files -z)"})
for f in "${FILES[@]}"; do
  [[ -n "${f}" ]] || continue
  vde_shib_excluded "${f}" && continue
  _vde_shib_is_zsh_file "${REPO}/${f}" || continue
  SCANNED+=1
  vde_shib_has_literal "${REPO}/${f}" || MISSING+=("${f}")
done
check "the sweep scanned at least 100 tracked zsh files (scanned: ${SCANNED})" '(( SCANNED >= 100 ))'
check "every tracked zsh file carries the shibboleth line (missing: ${#MISSING})" '(( ${#MISSING} == 0 ))'

print -r -- "Passed: ${PASS}  Failed: ${FAIL}"
(( FAIL == 0 ))
