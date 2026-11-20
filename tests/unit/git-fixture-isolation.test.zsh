#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit tests: git fixtures must not read the caller's git environment (Signet #656).
#
# Four suites build throwaway git repositories as fixtures: shibboleth-check, pol-stamp,
# vde-prune-safety and ghost-zone-report-only. Git lets GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE beat both `cd` and `git -C`,
# and a git hook (or a linked-worktree shell) exports them. An unscrubbed fixture then runs its
# `git init`, `add` and `commit` against the ENCLOSING repository: the suite fails, and its
# fixture commits land in a repo that is not theirs.
#
# Each suite is run once in a clean environment (the reference counts) and once under each polluted
# environment, all in parallel, each polluted run pointing at its own canary repository:
#   A  GIT_DIR + GIT_WORK_TREE        (a hook, or a linked-worktree shell)
#   B  GIT_DIR + GIT_INDEX_FILE       (a hook that exports the index)
#   C  GIT_OBJECT_DIRECTORY           (fixture objects land in the canary's object store)
#   D  GIT_NAMESPACE                  (changes ref handling, so a suite's own results shift)
# A scrubbed suite passes and fails exactly as it does when clean, and its canary is untouched:
# same commits, files, HEAD, branch, status, local config and git-dir file listing (a stray
# stamp file or object would show there).
#
# The scrub is the eight variables bin/vde-spine-check.zsh unsets. GIT_PREFIX and
# GIT_ALTERNATE_OBJECT_DIRECTORIES are in the scrub for consistency with it, but they have no
# observable effect on these suites (measured), so no test here can fail on them.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

test_start() { print -r -- "[TEST] $1"; }
test_pass()  { print -r -- "[PASS] $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { print -r -- "[FAIL] $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }

typeset WORK
WORK="$(mktemp -d)" || { print -u2 "mktemp failed"; exit 1; }
trap 'rm -rf -- "${WORK}"' EXIT

# The suites under test, named the way the runner names them.
typeset -a SUITES=(pol-stamp vde-prune-safety shibboleth-check ghost-zone-report-only)

# The one definition of "the git environment this test removes" (this test's own bookkeeping and
# the clean/polluted runs both use it).
typeset -a GIT_UNSET=(-u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR
                      -u GIT_PREFIX -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES -u GIT_NAMESPACE)

# One git, always scrubbed: this test's own bookkeeping must not be fooled by the same variables.
cgit() {
    env "${GIT_UNSET[@]}" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git "$@"
}

# make_canary NAME -> a repository with one commit and one tracked file, in ${WORK}/NAME.
make_canary() {
    typeset c="${WORK}/$1"
    mkdir -p "${c}" || return 1
    cgit -C "${c}" init -q || return 1
    print -r -- canary > "${c}/canary.txt"
    cgit -C "${c}" add canary.txt || return 1
    cgit -C "${c}" -c user.email=c@c -c user.name=c -c commit.gpgsign=false commit -qm canary || return 1
}

# canary_state DIR -> a one-line fingerprint of everything a leaked fixture would change:
# commits on every ref, tracked files, HEAD, branch, working-tree status, the repo-local config,
# and the list of every file in the git dir (a stray stamp file, a new ref or an object shows there
# even when nothing else does; *.lock files are transient and skipped).
canary_state() {
    typeset c="$1"
    print -r -- "gitdir=$(cd "${c}/.git" && find . -type f ! -name '*.lock' | LC_ALL=C sort | md5sum | cut -c1-12)" \
        "commits=$(cgit -C "${c}" rev-list --count --all 2>&1)" \
        "files=$(cgit -C "${c}" ls-files 2>&1 | tr '\n' ',')" \
        "head=$(cgit -C "${c}" rev-parse HEAD 2>&1)" \
        "branch=$(cgit -C "${c}" symbolic-ref -q HEAD 2>&1)" \
        "status=$(cgit -C "${c}" status --porcelain 2>&1 | tr '\n' ',')" \
        "config=$(cgit -C "${c}" config --local --list 2>&1 | tr '\n' ',')"
}

# counts FILE -> "passed failed", read from whichever summary line the suite prints.
counts() {
    typeset line p f
    line="$(sed 's/\x1b\[[0-9;]*m//g' "$1" | grep -E '^(Passed: [0-9]+ +Failed: [0-9]+|Results: [0-9]+ passed, [0-9]+ failed)' | tail -1)"
    p="${${line##*(Passed:|Results:) }%% *}"
    f="${${line##*(Failed:|passed,) }%% *}"
    [[ "${p}" == <-> && "${f}" == <-> ]] && print -r -- "${p} ${f}" || print -r -- "none none"
}

# run_suite SUITE OUTFILE [VAR=value ...] -> runs the suite with a scratch HOME, the three git
# environment names removed first, then the given ones set. Never prints; the exit code is the suite's.
run_suite() {
    typeset suite="$1" out="$2"; shift 2
    typeset home="${WORK}/home-${out:t}"
    mkdir -p "${home}"
    env "${GIT_UNSET[@]}" \
        HOME="${home}" "$@" \
        zsh "${VDE_ROOT_DIR}/tests/unit/${suite}.test.zsh" > "${out}" 2>&1
}

# The polluted environments (see the header). variant_env VARIANT CANARY fills VENV with the
# NAME=value assignments for that variant, pointing at CANARY where a repository is involved.
typeset -a VARIANTS=(A B C D)
typeset -a VENV
variant_env() {
    case "$1" in
        A) VENV=(GIT_DIR="$2/.git" GIT_WORK_TREE="$2") ;;
        B) VENV=(GIT_DIR="$2/.git" GIT_INDEX_FILE="$2/.git/index") ;;
        C) VENV=(GIT_OBJECT_DIRECTORY="$2/.git/objects") ;;
        D) VENV=(GIT_NAMESPACE=leak) ;;
    esac
}

make_canary canary || { print -u2 "could not build the canary repository"; exit 1; }

# Reference state of the pristine canary (every copy below starts byte-identical to it).
typeset pristine
pristine="$(canary_state "${WORK}/canary")"

typeset suite variant
for variant in "${VARIANTS[@]}"; do
    for suite in "${SUITES[@]}"; do
        # Each run gets its OWN canary copy so one leak cannot hide behind another.
        cp -a "${WORK}/canary" "${WORK}/canary${variant}-${suite}"
    done
done

typeset -a PIDS=()
for suite in "${SUITES[@]}"; do
    run_suite "${suite}" "${WORK}/${suite}.clean" &
    PIDS+=($!)
    for variant in "${VARIANTS[@]}"; do
        variant_env "${variant}" "${WORK}/canary${variant}-${suite}"
        run_suite "${suite}" "${WORK}/${suite}.${variant}" "${VENV[@]}" &
        PIDS+=($!)
    done
done

typeset pid
for pid in "${PIDS[@]}"; do wait "${pid}"; done

typeset ref got state want
for suite in "${SUITES[@]}"; do
    ref="$(counts "${WORK}/${suite}.clean")"
    test_start "${suite}: the clean run is the reference (it must pass everything itself)"
    if [[ "${ref}" == [0-9]*" 0" ]]; then
        test_pass "${suite} clean reference ${ref}"
    else
        test_fail "${suite} clean reference" "got '${ref}' (passed failed); the suite is broken even when clean"
    fi

    for variant in "${VARIANTS[@]}"; do
        got="$(counts "${WORK}/${suite}.${variant}")"
        test_start "${suite}: counts under polluted env ${variant} equal the clean counts"
        if [[ "${got}" == "${ref}" ]]; then
            test_pass "${suite} env ${variant} counts ${got}"
        else
            test_fail "${suite} env ${variant} counts" "clean '${ref}' vs polluted '${got}' (passed failed); first failures: $(sed 's/\x1b\[[0-9;]*m//g' "${WORK}/${suite}.${variant}" | grep -E '^\[FAIL\]' | head -3 | tr '\n' '|')"
        fi

        test_start "${suite}: the canary is untouched under polluted env ${variant}"
        state="$(canary_state "${WORK}/canary${variant}-${suite}")"
        if [[ "${state}" == "${pristine}" ]]; then
            test_pass "${suite} env ${variant} canary unchanged"
        else
            test_fail "${suite} env ${variant} canary" "fixture git calls reached the enclosing repo; before: ${pristine} | after: ${state}"
        fi
    done
done

print -r -- "Passed: ${TESTS_PASSED} Failed: ${TESTS_FAILED}"
[[ ${TESTS_FAILED} -eq 0 ]]
