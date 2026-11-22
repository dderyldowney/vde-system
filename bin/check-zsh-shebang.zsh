#!/usr/bin/env zsh
# @armor (Engine Core)
# check-zsh-shebang - Verify all scripts use zsh shebang
# This script is used in CI to enforce zsh-only policy
typeset _ZSH_PURE=${(%):-%x}

print -r -- "Checking zsh shebang enforcement..."

typeset VDE_ROOT="${0:A:h:h}"

# Shared zsh-shebang predicate (vde_shib_is_zsh FILE) from the one shibboleth library
if [[ ! -r "${VDE_ROOT}/lib/vde-shibboleth" ]]; then
  print -r -- "FAIL: lib/vde-shibboleth is missing, cannot check shebangs"
  exit 1
fi
source "${VDE_ROOT}/lib/vde-shibboleth"

typeset failed=0
typeset file relpath shebang
typeset -a files=( "${VDE_ROOT}"/bin/**/*(.ND) "${VDE_ROOT}"/lib/**/*(.ND) )

for file in "${files[@]}"; do
  # Skip archived, cached, backup and non-script files
  [[ "${file}" == */bin/archive/* ]] && continue
  [[ "${file}" == */.cache/* ]] && continue
  [[ "${file}" == */backup/* ]] && continue
  [[ "${file}" == *.bak ]] && continue
  [[ "${file}" == *.py ]] && continue
  [[ "${file}" == *.md ]] && continue
  [[ "${file}" == *.json ]] && continue
  [[ "${file}" == *.txt ]] && continue

  relpath="${file#${VDE_ROOT}/}"

  # Shared predicate decides; a bin/ or lib/ file without a zsh shebang is a failure
  if vde_shib_is_zsh "${file}"; then
    continue
  fi

  # Read only the first line for the message
  # (read returns non-zero for a last line with no trailing newline but still sets the variable)
  shebang=""
  IFS= read -r shebang < "${file}" 2>/dev/null || [[ -n "${shebang}" ]]
  if [[ -n "${shebang}" ]]; then
    print -r -- "FAIL: ${relpath} uses non-zsh shebang: ${shebang}"
  else
    print -r -- "FAIL: ${relpath} has no readable zsh shebang (no shebang or unreadable)"
  fi
  failed=1
done

if (( failed == 0 )); then
  print -r -- "SUCCESS: All scripts use zsh shebang"
  exit 0
else
  print -r -- ""
  print -r -- "ERROR: Some scripts do not use zsh shebang"
  print -r -- "This project requires: #!/usr/bin/env zsh or #!/bin/zsh"
  exit 1
fi
