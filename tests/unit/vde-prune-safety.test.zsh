#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit tests for the repository-prune safety contract (Signet #620).
# Every mutation case runs against a scratch Git clone; the real VDE tree is never touched.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Fixture isolation (Signet #656): git lets the GIT_* variables that select a repository, its index,
# its objects or its namespace (the eight bin/vde-spine-check.zsh unsets)
# beat `cd` and `git -C`, and a git hook or a linked-worktree shell exports them. Without this scrub the
# fixture repository below (and the scripts this suite runs) would write into the ENCLOSING repository.
# It also drops the variables that inject git config or install hooks: GIT_CONFIG_COUNT (with its
# GIT_CONFIG_KEY_n/GIT_CONFIG_VALUE_n), GIT_CONFIG_PARAMETERS (what a parent `git -c` exports) and GIT_TEMPLATE_DIR.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

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
print -r -- 'student backup' > "${SCRATCH}/backup/old-backup"
print -r -- 'tracked old plan' > "${SCRATCH}/plans/old.md"
print -r -- 'historical release' > "${SCRATCH}/docs/releases/1.5.5.md"
print -r -- 'Version: 1.5.6' > "${SCRATCH}/docs/governance/vde-spec.md"
git -C "${SCRATCH}" add .
git -C "${SCRATCH}" commit -qm 'scratch fixture'
touch -d '10 days ago' "${SCRATCH}/logs/old.log" "${SCRATCH}/backup/old-backup" "${SCRATCH}/plans/old.md" "${SCRATCH}/docs/releases/1.5.5.md"

typeset SCRIPT="${VDE_ROOT_DIR}/bin/vde-prune.zsh"
typeset out rc

# Default mode must not mutate anything.
test_start "default vde prune prints a plan and leaves the scratch clone unchanged"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" 2>&1); rc=$?
if [[ ${rc} -eq 0 && "${out}" == *"dry run"* && "${out}" == *"plans/old.md"* && -f "${SCRATCH}/logs/old.log" && -f "${SCRATCH}/plans/old.md" ]] && [[ -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "no default mutation"
else
    test_fail "default mutation" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Explicit dry-run must use the same plan and never git-rm/git-mv.
test_start "--dry-run uses the shared plan and never stages tracked removals"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --dry-run 2>&1); rc=$?
if [[ ${rc} -eq 0 && "${out}" == *"old.md"* && -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "dry-run safe"
else
    test_fail "dry-run" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Unknown options, extra arguments, and unsupported timeframes are refused before mutation.
test_start "unknown options, extra arguments, and unsupported timeframes return 2 without mutation"
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
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --timeframe 6d 2>&1); rc=$?
if [[ ${rc} -eq 2 && -z "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "unsupported timeframe refused"
else
    test_fail "unsupported timeframe" "rc=${rc} out=${out}"
fi

# Locally modified tracked files must never be force-deleted.
test_start "--apply --yes refuses to force-delete a modified tracked file"
print -r -- 'local modification' > "${SCRATCH}/plans/old.md"
touch -d '10 days ago' "${SCRATCH}/plans/old.md"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes 2>&1); rc=$?
if [[ ${rc} -ne 0 && -f "${SCRATCH}/plans/old.md" && "${out}" == *"FAILED DELETE plans/old.md"* ]]; then
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

# Student data and historical releases are excluded from the destructive plan.
test_start "dry run excludes logs and backup but plans historical release housekeeping"
mkdir -p "${SCRATCH}/docs/releases"
print -r -- 'historical release' > "${SCRATCH}/docs/releases/1.5.5.md"
touch -d '10 days ago' "${SCRATCH}/docs/releases/1.5.5.md"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --dry-run 2>&1); rc=$?
if [[ ${rc} -eq 0 && "${out}" != *"logs/old.log"* && "${out}" != *"backup/old-backup"* && "${out}" == *"docs/releases/1.5.5.md"* ]]; then
    test_pass "protected student and release data excluded"
else
    test_fail "protected data exclusion" "rc=${rc} out=${out}"
fi

# Modified tracked files must not be moved either.
test_start "--apply --yes refuses to move a modified tracked plan"
rm -rf -- "${SCRATCH}/plans/movable.md" "${SCRATCH}/plans/archive/movable.md"
print -r -- 'clean tracked move' > "${SCRATCH}/plans/modified-move.md"
git -C "${SCRATCH}" add plans/modified-move.md
git -C "${SCRATCH}" commit -qm 'modified move fixture'
print -r -- 'local modification after commit' >> "${SCRATCH}/plans/modified-move.md"
touch -d '2 days ago' "${SCRATCH}/plans/modified-move.md"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes 2>&1); rc=$?
if [[ ${rc} -ne 0 && -f "${SCRATCH}/plans/modified-move.md" && "${out}" == *"FAILED MOVE plans/modified-move.md"* ]]; then
    test_pass "modified tracked move preserved"
else
    test_fail "modified tracked move" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

# Explicit apply remains destructive and reports it performed work.
test_start "--apply --yes performs the planned delete on the scratch clone"
rm -rf -- "${SCRATCH}/plans/archive/movable.md" "${SCRATCH}/plans/movable.md" "${SCRATCH}/plans/modified-move.md"
mkdir -p "${SCRATCH}/docs/releases"
print -r -- 'historical release' > "${SCRATCH}/docs/releases/1.5.5.md"
touch -d '10 days ago' "${SCRATCH}/plans/old.md" "${SCRATCH}/docs/releases/1.5.5.md"
out=$(VDE_ROOT_DIR="${SCRATCH}" zsh "${SCRIPT}" --apply --yes 2>&1); rc=$?
if [[ ${rc} -eq 0 && ! -e "${SCRATCH}/plans/old.md" && ! -e "${SCRATCH}/docs/releases/1.5.5.md" && -f "${SCRATCH}/logs/old.log" && -f "${SCRATCH}/backup/old-backup" && -n "$(git -C "${SCRATCH}" status --porcelain)" ]]; then
    test_pass "explicit apply worked"
else
    test_fail "explicit apply" "rc=${rc} out=${out} status=$(git -C "${SCRATCH}" status --porcelain)"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
