#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for Signet #719: the project's own check scripts must FAIL CLOSED.
# A gate that reports success when it cannot do its job, or when it finds a violation, is
# worse than no gate. Each case builds a throwaway repository root, copies the REAL script
# into it, runs it, and judges the exit status and the output of that real run.
#
#   Cases 1-4  bin/vde-security-audit.zsh  (CodeQL query, API failure, leak scan root)
#   Cases 5-8  bin/check-zsh-shebang.zsh   (violations in bin/ and lib/, interpreter match)
#   Case  9    bin/targeted-test.zsh       (--fail-fast must exit non-zero)
#   Case 10    bin/coverage.zsh            (unknown test type must exit non-zero)
#   Case 11    bin/vde-security-audit.zsh  (gh present but repository unknown must fail closed)
#   Case 12    bin/targeted-test.zsh       (a selector matching no test must exit non-zero)
#
# `gh` is replaced by a stub that behaves like the real one where it matters: it rejects the
# unsupported `--params` flag exactly as `gh api --params` does ("unknown flag"). No network,
# no docker, no real HOME.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
  export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
  typeset GREEN='%F{green}' RED='%F{red}' YELLOW='%F{yellow}' RESET='%f'
else
  typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { print -rP -- "${YELLOW}[TEST]${RESET} ${1//\%/%%}"; }
test_pass()  { print -rP -- "${GREEN}[PASS]${RESET} ${1//\%/%%}"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }
test_fail()  { print -rP -- "${RED}[FAIL]${RESET} ${1//\%/%%}: ${2//\%/%%}"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT

typeset SCRATCH_HOME="${TMP_ROOT}/home"
mkdir -p -- "${SCRATCH_HOME}"

# A stand-in for `gh` on PATH. FAKE_GH_MODE: clean | alert | fail.
typeset FAKEBIN="${TMP_ROOT}/fakebin"
typeset GH_LOG="${TMP_ROOT}/gh.log"
mkdir -p -- "${FAKEBIN}"
cat > "${FAKEBIN}/gh" <<'STUB'
#!/usr/bin/env zsh
typeset _ZSH_PURE=${(%):-%x}
print -r -- "$*" >> "${GH_LOG}"
if [[ "$1" == "repo" ]]; then
  if [[ "${FAKE_GH_MODE:-}" == "norepo" ]]; then print -u2 -r -- "not logged in"; exit 1; fi
  print -r -- "owner/repo"
  exit 0
fi
if [[ "$1" == "api" ]]; then
  # The real `gh api` has no --params flag.
  if (( ${@[(I)--params]} )); then
    print -u2 -r -- "unknown flag: --params"
    exit 1
  fi
  case "${FAKE_GH_MODE:-clean}" in
    alert) print -r -- "https://github.com/owner/repo/security/code-scanning/1"; exit 0 ;;
    fail)  print -u2 -r -- "HTTP 403: not accessible"; exit 1 ;;
    *)     exit 0 ;;
  esac
fi
exit 0
STUB
chmod +x "${FAKEBIN}/gh"

# make_root <name> <script...> : a throwaway repository root holding copies of the named scripts.
make_root() {
  local name="$1"; shift
  local root="${TMP_ROOT}/${name}"
  mkdir -p -- "${root}/bin" "${root}/lib" "${root}/templates" "${root}/configs/docker" "${root}/tests/unit"
  local s
  for s in "$@"; do cp -- "${VDE_ROOT_DIR}/bin/${s}" "${root}/bin/${s}"; done
  print -r -- "${root}"
}

# run_in <cwd> <mode> <command...> : run with the stub gh first on PATH and a scratch HOME;
# sets RC and OUT.
typeset RC OUT
run_in() {
  local cwd="$1" mode="$2"; shift 2
  : >| "${GH_LOG}"
  OUT="$(cd "${cwd}" && env HOME="${SCRATCH_HOME}" PATH="${FAKEBIN}:${PATH}" GH_LOG="${GH_LOG}" FAKE_GH_MODE="${mode}" "$@" 2>&1)"
  RC=$?
}

# ---------------------------------------------------------------- security audit

test_case1_codeql_query_uses_supported_flags() {
  test_start "1: the CodeQL query never passes --params, and a clean answer passes the audit"
  local root; root="$(make_root c1 vde-security-audit.zsh)"
  run_in "${root}" clean zsh "${root}/bin/vde-security-audit.zsh"
  if grep -q -- '--params' "${GH_LOG}"; then
    test_fail "case 1" "gh api was called with the unsupported --params flag: $(grep -- '--params' "${GH_LOG}" | head -1)"
  elif (( RC != 0 )); then
    test_fail "case 1" "clean run exited ${RC}: ${OUT}"
  elif ! grep -q -- '--paginate' "${GH_LOG}"; then
    test_fail "case 1" "gh api was called without --paginate, so alerts on later pages would be missed"
  else
    test_pass "case 1"
  fi
}

test_case2_api_failure_fails_closed() {
  test_start "2: when the code-scanning API cannot be read, the audit fails instead of reporting PASS"
  local root; root="$(make_root c2 vde-security-audit.zsh)"
  run_in "${root}" fail zsh "${root}/bin/vde-security-audit.zsh"
  if (( RC == 0 )); then
    test_fail "case 2" "exit 0 although the API call failed; output: ${OUT}"
  elif [[ "${OUT}" == *"CodeQL High/Critical Audit: PASS"* ]]; then
    test_fail "case 2" "reported CodeQL PASS although the API call failed"
  else
    test_pass "case 2"
  fi
}

test_case3_open_alert_fails() {
  test_start "3: an open high/critical alert fails the audit"
  local root; root="$(make_root c3 vde-security-audit.zsh)"
  run_in "${root}" alert zsh "${root}/bin/vde-security-audit.zsh"
  if (( RC == 0 )); then
    test_fail "case 3" "exit 0 with an open alert; output: ${OUT}"
  else
    test_pass "case 3"
  fi
}

test_case4_leak_scan_is_anchored_to_the_repo_root() {
  test_start "4: the absolute-path leak scan covers the repository root even when run from another directory"
  local root; root="$(make_root c4 vde-security-audit.zsh)"
  mkdir -p -- "${root}/docs" "${TMP_ROOT}/elsewhere"
  # The path is assembled here so this test file does not itself contain the leaked prefix
  # the audit scans the whole repository for.
  local _prefix="/Us""ers/"
  print -r -- "see ${_prefix}someone/project for the file" > "${root}/docs/leak.md"
  run_in "${TMP_ROOT}/elsewhere" clean zsh "${root}/bin/vde-security-audit.zsh"
  if (( RC == 0 )); then
    test_fail "case 4" "leak in the repo root was missed when run from another directory; output: ${OUT}"
  else
    test_pass "case 4"
  fi
}

# ---------------------------------------------------------------- shebang check

test_case5_bad_shebang_in_bin_fails() {
  test_start "5: a non-zsh shebang in bin/ makes the check exit non-zero"
  local root; root="$(make_root c5 check-zsh-shebang.zsh)"
  print -r -- $'#!/usr/bin/env zsh\necho ok' > "${root}/bin/good.zsh"
  print -r -- $'#!/bin/bash\necho bad' > "${root}/bin/bad.zsh"
  run_in "${TMP_ROOT}" clean zsh "${root}/bin/check-zsh-shebang.zsh"
  if (( RC == 0 )); then
    test_fail "case 5" "exit 0 with a bash script present; output: ${OUT}"
  else
    test_pass "case 5"
  fi
}

test_case6_bad_shebang_in_lib_fails() {
  test_start "6: a non-zsh shebang in lib/ is found (lib/ is scanned from the repo root, not from bin/)"
  local root; root="$(make_root c6 check-zsh-shebang.zsh)"
  print -r -- $'#!/usr/bin/env zsh\necho ok' > "${root}/bin/good.zsh"
  print -r -- $'#!/bin/bash\necho bad' > "${root}/lib/badlib"
  run_in "${TMP_ROOT}" clean zsh "${root}/bin/check-zsh-shebang.zsh"
  if (( RC == 0 )) || [[ "${OUT}" != *badlib* ]]; then
    test_fail "case 6" "lib/badlib was not reported (rc=${RC}); output: ${OUT}"
  else
    test_pass "case 6"
  fi
}

test_case7_interpreter_match_is_exact() {
  test_start "7: a shebang that only MENTIONS zsh in a comment is not accepted"
  local root; root="$(make_root c7 check-zsh-shebang.zsh)"
  print -r -- $'#!/bin/bash # zsh\necho sneaky' > "${root}/bin/sneaky.zsh"
  run_in "${TMP_ROOT}" clean zsh "${root}/bin/check-zsh-shebang.zsh"
  if (( RC == 0 )); then
    test_fail "case 7" "'#!/bin/bash # zsh' was accepted; output: ${OUT}"
  else
    test_pass "case 7"
  fi
}

test_case8_clean_tree_still_passes() {
  test_start "8: a tree of zsh scripts, plus a python helper in lib/, passes"
  local root; root="$(make_root c8 check-zsh-shebang.zsh)"
  print -r -- $'#!/usr/bin/env zsh\necho ok' > "${root}/bin/a.zsh"
  print -r -- $'#!/bin/zsh\necho ok' > "${root}/bin/b.zsh"
  print -r -- $'#!/bin/zsh -f\necho ok' > "${root}/bin/flagged.zsh"
  print -r -- $'#!/usr/bin/env zsh\necho ok' > "${root}/lib/vde-thing"
  print -r -- $'#!/usr/bin/env python3\nprint(1)' > "${root}/lib/helper.py"
  run_in "${TMP_ROOT}" clean zsh "${root}/bin/check-zsh-shebang.zsh"
  if (( RC != 0 )); then
    test_fail "case 8" "clean tree exited ${RC}; output: ${OUT}"
  else
    test_pass "case 8"
  fi
}

# ---------------------------------------------------------------- the two runners

test_case9_fail_fast_exits_non_zero() {
  test_start "9: targeted-test --fail-fast exits non-zero when a test fails"
  local root; root="$(make_root c9 targeted-test.zsh)"
  print -r -- $'#!/usr/bin/env zsh\nexit 1' > "${root}/tests/unit/boom.test.zsh"
  run_in "${root}" clean zsh "${root}/bin/targeted-test.zsh" --fail-fast --unit tests/unit/boom.test.zsh
  if (( RC == 0 )); then
    test_fail "case 9" "exit 0 although the test failed and --fail-fast was given; output: ${OUT}"
  else
    test_pass "case 9"
  fi
}

test_case10_coverage_unknown_type_exits_non_zero() {
  test_start "10: coverage.zsh with an unknown test type exits non-zero"
  local root; root="$(make_root c10 coverage.zsh)"
  run_in "${root}" clean zsh "${root}/bin/coverage.zsh" bogus-type
  if (( RC == 0 )); then
    test_fail "case 10" "exit 0 for an unknown test type; output: ${OUT}"
  else
    test_pass "case 10"
  fi
}

test_case11_unknown_repository_fails_closed() {
  test_start "11: gh is installed but the repository cannot be determined, so the audit fails closed"
  local root; root="$(make_root c11 vde-security-audit.zsh)"
  run_in "${root}" norepo zsh "${root}/bin/vde-security-audit.zsh"
  if (( RC == 0 )) || [[ "${OUT}" != *CRITICAL* ]]; then
    test_fail "case 11" "gh is installed but the repository could not be determined must fail, not skip (rc=${RC}); output: ${OUT}"
  else
    test_pass "case 11"
  fi
}

test_case12_targeted_test_with_no_matching_test_fails() {
  test_start "12: targeted-test with a selector that matches no test exits non-zero"
  local root; root="$(make_root c12 targeted-test.zsh)"
  run_in "${root}" clean zsh "${root}/bin/targeted-test.zsh" zzz-no-such-test-zzz
  if (( RC == 0 )); then
    test_fail "case 12" "exit 0 although no test matched the selector; output: ${OUT}"
  else
    test_pass "case 12"
  fi
}

test_case1_codeql_query_uses_supported_flags
test_case2_api_failure_fails_closed
test_case3_open_alert_fails
test_case4_leak_scan_is_anchored_to_the_repo_root
test_case5_bad_shebang_in_bin_fails
test_case6_bad_shebang_in_lib_fails
test_case7_interpreter_match_is_exact
test_case8_clean_tree_still_passes
test_case9_fail_fast_exits_non_zero
test_case10_coverage_unknown_type_exits_non_zero
test_case11_unknown_repository_fails_closed
test_case12_targeted_test_with_no_matching_test_fails

print -r -- ""
print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
