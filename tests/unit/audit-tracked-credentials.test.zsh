#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for 1.5.8 security hardening, item 22: the security audit fails when a
# git-tracked file carries a URL-embedded access token, and only for tracked files.
#
# Every run happens in a throwaway git repository with a stub `gh` (unauthenticated, so
# the CodeQL step is a loud skip) and a scratch HOME. No network, no docker.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
  export VDE_ROOT_DIR="${0:A:h:h:h}"
fi

typeset -i TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
  typeset GREEN='%F{green}' RED='%F{red}' YELLOW='%F{yellow}' RESET='%f'
else
  typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { print -P -- "${YELLOW}[TEST]${RESET} ${1//\%/%%}"; }
test_pass()  { print -P -- "${GREEN}[PASS]${RESET} ${1//\%/%%}"; (( ++TESTS_PASSED )); }
test_fail()  { print -P -- "${RED}[FAIL]${RESET} ${1//\%/%%}: ${2//\%/%%}"; (( ++TESTS_FAILED )); }

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT

typeset FAKEBIN="${TMP_ROOT}/fakebin" SCRATCH_HOME="${TMP_ROOT}/home"
mkdir -p -- "${FAKEBIN}" "${SCRATCH_HOME}"
cat > "${FAKEBIN}/gh" <<'STUB'
#!/usr/bin/env zsh
typeset _ZSH_PURE=${(%):-%x}
[[ "$1" == "auth" ]] && exit 1
[[ "$1" == "repo" ]] && { print -u2 -r -- "not logged in"; exit 1; }
exit 0
STUB
chmod +x "${FAKEBIN}/gh"

# A 48-character hex string built at run time (never written literally in this file).
typeset TOKEN_HEX
TOKEN_HEX="$(printf 'ab%.0s' {1..24})"

# make_root <name> : a git repository holding a copy of the audit and the dirs it requires.
make_root() {
  local root="${TMP_ROOT}/$1"
  mkdir -p -- "${root}/bin" "${root}/lib" "${root}/templates" "${root}/configs/docker"
  cp -- "${VDE_ROOT_DIR}/bin/vde-security-audit.zsh" "${root}/bin/"
  print -r -- "clean" > "${root}/templates/readme.txt"
  git -C "${root}" init -q . && git -C "${root}" add -A \
    && git -C "${root}" -c user.name=t -c user.email=t@t commit -q -m init
  print -r -- "${root}"
}

typeset RC OUT
run_audit() {
  OUT="$(cd "$1" && env -u GH_TOKEN -u GITHUB_TOKEN HOME="${SCRATCH_HOME}" PATH="${FAKEBIN}:${PATH}" zsh bin/vde-security-audit.zsh 2>&1)"
  RC=$?
}

check() { if eval "$3"; then test_pass "$1"; else test_fail "$1" "$2"; fi; }

test_clean_repo_passes() {
  test_start "a repository with no tracked token passes"
  local root; root="$(make_root clean)"
  run_audit "${root}"
  check "clean repo exits 0" "rc=${RC}" '(( RC == 0 ))'
}

test_tracked_token_fails() {
  test_start "a tracked file carrying a URL access token fails the audit"
  local root; root="$(make_root tracked)"
  print -r -- "http://127.0.0.1:8889/lab?token=${TOKEN_HEX}" > "${root}/server.txt"
  git -C "${root}" add server.txt
  run_audit "${root}"
  check "exits non-zero" "rc=${RC}" '(( RC != 0 ))'
  check "names the credential scan" "${OUT}" '[[ "${OUT}" == *"Access Token"* ]]'
  check "never prints the token" "token echoed" '[[ "${OUT}" != *"${TOKEN_HEX}"* ]]'
}

test_untracked_token_ignored() {
  test_start "an untracked file with a token is not the audit's business"
  local root; root="$(make_root untracked)"
  print -r -- "?token=${TOKEN_HEX}" > "${root}/server.txt"
  run_audit "${root}"
  check "untracked token exits 0" "rc=${RC}" '(( RC == 0 ))'
}

test_short_value_ignored() {
  test_start "a short token= value is not flagged"
  local root; root="$(make_root short)"
  print -r -- "x?token=abc123" > "${root}/notes.txt"
  git -C "${root}" add notes.txt
  run_audit "${root}"
  check "short value exits 0" "rc=${RC}" '(( RC == 0 ))'
}

test_clean_repo_passes
test_tracked_token_fails
test_untracked_token_ignored
test_short_value_ignored

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
