#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit tests for the repository-prune safety contract (Signet #620).
# Every mutation case runs against a scratch Git clone; the real VDE tree is never touched.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

test_start() { print -r -- "[TEST] $1"; }
test_pass()  { print -r -- "[PASS] $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { print -r -- "[FAIL] $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset SCRATCH
SCRATCH=$(mktemp -d) || { print -u2 "mktemp failed"; exit 1; }
trap 'rm -rf -- "${SCRATCH}"' EXIT

mkdir -p "${SCRATCH}/logs" "${SCRATCH}/plans" "${SCRATCH}/plans/scripts" "${SCRATCH}/backup" "${SCRATCH}/docs/releases" "${SCRATCH}/docs/governance"
git -C "${SCRATCH}" init -q
git -C "${SCRATCH}" config user.email 'vde-test@example.invalid'
git -C "${SCRATCH}" config user.name 'VDE Test'
print -r -- 'tracked old log' > "${SCRATCH}/logs/old.log"
print -r -- 'tracked old plan' > "${SCRATCH}/plans/old.md"
print -r -- 'Version: 1.5.6' > "${SCRATCH}/docs/governance/vde-spec.md"
git -C "${SCRATCH}" add .
git -C "${SCRATCH}" commit -qm 'scratch fixture'
touch -d '10 days ago' "${SCRATCH}/logs/old.log" "${SCRATCH}/plans/old.md"

typeset SCRIPT="${VDE_ROOT_DIR}/bin/vde-prune.zsh"
typeset out rc

# Default mode must not mutate anything.
test_start "default vde prune prints a plan and leaves the scratch clone unchanged"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" 2>&1); rc=$?
if [[ ${rc} -eq 0 && "${out}" == *"dry run"* && -f "${SCRATCH}/logs/old.log" && -f "${SCRATCH}/plans/old.md" ]] && [[ -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "no default mutation"
else
    test_fail "default mutation" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Explicit dry-run must use the same plan and never git-rm/git-mv.
test_start "--dry-run uses the shared plan and never stages tracked removals"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --dry-run 2>&1); rc=$?
if [[ ${rc} -eq 0 && "${out}" == *"old.log"* && "${out}" == *"old.md"* && -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "dry-run safe"
else
    test_fail "dry-run" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Unknown options and extra arguments are refused before mutation.
test_start "unknown and extra arguments return 2 without mutation"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --dry-rnu 2>&1); rc=$?
if [[ ${rc} -eq 2 && -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "unknown option refused"
else
    test_fail "unknown option" "rc=${rc} out=${out}"
fi
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" extra 2>&1); rc=$?
if [[ ${rc} -eq 2 && -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "extra argument refused"
else
    test_fail "extra argument" "rc=${rc} out=${out}"
fi

# Locally modified tracked files must never be force-deleted.
test_start "--apply --yes refuses to force-delete a modified tracked file"
print -r -- 'local modification' > "${SCRATCH}/logs/old.log"
touch -d '10 days ago' "${SCRATCH}/logs/old.log"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes 2>&1); rc=$?
if [[ ${rc} -ne 0 && -f "${SCRATCH}/logs/old.log" && "${out}" == *"FAILED DELETE logs/old.log"* ]]; then
    test_pass "modified tracked file preserved"
else
    test_fail "modified tracked file" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Archive collisions must preserve both source and existing archive content.
test_start "--apply --yes refuses an archive collision"
mkdir -p "${SCRATCH}/plans/archive"
# Revert the prior delete state by restoring old.log and old.md before rebuilding fixture state.
git -C "${SCRATCH}" reset -q --hard
print -r -- 'source to move' > "${SCRATCH}/plans/movable.md"
print -r -- 'existing archive' > "${SCRATCH}/plans/archive/movable.md"
touch -d '2 days ago' "${SCRATCH}/plans/movable.md"
git -C "${SCRATCH}" add plans/movable.md
git -C "${SCRATCH}" commit -qm 'collision fixture'
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes --timeframe 7d 2>&1); rc=$?
if [[ ${rc} -ne 0 && -f "${SCRATCH}/plans/movable.md" && "$(<${SCRATCH}/plans/archive/movable.md)" == 'existing archive' ]]; then
    test_pass "archive collision preserved"
else
    test_fail "archive collision" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Explicit apply remains destructive and reports it performed work.
test_start "--apply --yes performs the planned delete on the scratch clone"
rm -rf -- "${SCRATCH}/logs/old.log" "${SCRATCH}/plans/old.md" "${SCRATCH}/plans/archive/movable.md" "${SCRATCH}/plans/movable.md"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes 2>&1); rc=$?
if [[ ${rc} -eq 0 && ! -e "${SCRATCH}/logs/old.log" && -n "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "explicit apply worked"
else
    test_fail "explicit apply" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
