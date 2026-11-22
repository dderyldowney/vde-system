#!/usr/bin/env zsh
# @armor (Engine Core)
# check-zsh-shebang - Verify all scripts use zsh shebang
# This script is used in CI to enforce zsh-only policy
typeset _ZSH_PURE=${(%):-%x}

print -r -- "Checking zsh shebang enforcement..."

typeset VDE_ROOT="${0:A:h:h}"
typeset failed=0
typeset file relpath shebang
typeset -a files=( "${VDE_ROOT}"/bin/**/*(.N) "${VDE_ROOT}"/lib/**/*(.N) )

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

  # Read only the first line, safely
  # (read returns non-zero for a last line with no trailing newline but still sets the variable)
  shebang=""
  IFS= read -r shebang < "${file}" 2>/dev/null || [[ -n "${shebang}" ]] || shebang=""

  if [[ "${shebang}" == \#!* ]]; then
    if [[ ! "${shebang}" =~ '^#!(/usr/bin/env zsh|/bin/zsh|/usr/bin/zsh|/usr/local/bin/zsh)([[:space:]]+-[-A-Za-z]+)*[[:space:]]*$' ]]; then
      print -r -- "FAIL: ${relpath} uses non-zsh shebang: ${shebang}"
      failed=1
    fi
  else
    # No shebang: warn under bin/, silently accept under lib/
    if [[ "${relpath}" == bin/* ]]; then
      print -r -- "WARN: ${relpath} has no shebang"
    fi
  fi
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
