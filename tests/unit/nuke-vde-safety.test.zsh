#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for nuke-vde data-integrity safety (Signet #543 follow-up).
#
# These tests prove, WITHOUT ever running a real `vde nuke`, that:
#   1. _safe_move_tree never overwrites or deletes a student's existing work on
#      a name collision (it skips the colliding child and leaves it in place).
#   2. The dirs_to_remove purge list in bin/nuke-vde contains neither
#      "projects" nor "data" -- a static guard against a regression that would
#      make nuke delete the student's source or database volumes.
#
# _safe_move_tree and main() share one file, and `main "$@"` runs on source, so
# the function under test is EXTRACTED verbatim from bin/nuke-vde at runtime
# (awk range) and eval'd in this harness. Extracting the live definition keeps
# the test from drifting out of sync with the real implementation.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset NUKE_SRC="${VDE_ROOT_DIR}/bin/nuke-vde"

# Test configuration
typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

# Stubs for the print helpers the function calls (harmless echoes).
print_success() { : ; }
print_warning() { : ; }
print_info()    { : ; }

# is_known_vm stub: only python/rust count as VDE-owned here. Keeps the known_only
# test focused on _safe_move_tree's FILTER, not the real registry (covered by the
# vm-types / vm-common suites).
is_known_vm() { [[ "${1}" == python || "${1}" == rust ]] }

# Extract and load the real _safe_move_tree from bin/nuke-vde.
typeset _fn_text
_fn_text="$(awk '/^_safe_move_tree\(\) \{/,/^\}/' "${NUKE_SRC}")"
if [[ -z "${_fn_text}" ]]; then
    echo "FATAL: could not extract _safe_move_tree from ${NUKE_SRC}"
    exit 1
fi
eval "${_fn_text}"

# =============================================================================
# TEST: _safe_move_tree adopts, never clobbers
# =============================================================================
test_safe_move_tree_non_destructive() {
    test_start "_safe_move_tree: moves non-colliding children, skips collisions, never deletes"

    local tmp
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-safe.XXXXXX")"
    local src="${tmp}/src" dst="${tmp}/dst"

    # SRC: a loose file, a nested folder, a hidden file, and a collider.
    mkdir -p "${src}/dirB" "${src}/collide"
    print -r -- "A"       > "${src}/fileA.txt"
    print -r -- "B"       > "${src}/dirB/inner.txt"
    print -r -- "H"       > "${src}/.hidden"
    print -r -- "STUDENT" > "${src}/collide/student.txt"

    # DST already holds the student's own 'collide' folder with their work.
    mkdir -p "${dst}/collide"
    print -r -- "KEEP" > "${dst}/collide/existing.txt"

    _safe_move_tree "${src}" "${dst}"

    local ok=1 why=""

    # Non-colliding children moved in.
    [[ -f "${dst}/fileA.txt"      && "$(<"${dst}/fileA.txt")"      == "A" ]] || { ok=0; why="fileA not moved"; }
    [[ -f "${dst}/dirB/inner.txt" && "$(<"${dst}/dirB/inner.txt")" == "B" ]] || { ok=0; why="dirB not moved"; }
    [[ -f "${dst}/.hidden"        && "$(<"${dst}/.hidden")"        == "H" ]] || { ok=0; why="hidden entry not moved"; }

    # Moved children are gone from SRC.
    [[ ! -e "${src}/fileA.txt" ]] || { ok=0; why="fileA left in src"; }
    [[ ! -e "${src}/dirB"      ]] || { ok=0; why="dirB left in src"; }

    # Collision: student's existing file is UNTOUCHED, not overwritten/merged.
    [[ -f "${dst}/collide/existing.txt" && "$(<"${dst}/collide/existing.txt")" == "KEEP" ]] \
        || { ok=0; why="collision destination overwritten/altered"; }
    [[ ! -e "${dst}/collide/student.txt" ]] || { ok=0; why="colliding src merged into dst"; }

    # Collision source is LEFT IN PLACE, never deleted.
    [[ -f "${src}/collide/student.txt" && "$(<"${src}/collide/student.txt")" == "STUDENT" ]] \
        || { ok=0; why="colliding src content deleted/altered"; }

    rm -rf "${tmp}"

    if (( ok )); then
        test_pass "_safe_move_tree non-destructive"
    else
        test_fail "_safe_move_tree non-destructive" "${why}"
    fi
}

# Helper: succeed (printing the offending lines) when an array body lists a
# student dir ('projects' or 'data') in any quoting/prefix form. Comment lines
# and trailing '# ...' comments are ignored; quotes, an optional
# "${VDE_ROOT_DIR}/", "$VDE_ROOT_DIR/" or "./" prefix and an optional trailing "/" are stripped
# before the exact-name match, so 'projects-old' and 'database' do not match.
_dirs_block_lists_student_dir() {
    local line entry hit=1
    local re='^([$]([{]VDE_ROOT_DIR[}]|VDE_ROOT_DIR)/|[.]/)?(projects|data)/?$'
    for line in "${(@f)1}"; do
        line="${line%%\#*}"
        for entry in "${(@z)line}"; do
            entry="${entry//[\"\']/}"
            if [[ "${entry}" =~ ${re} ]]; then
                print -r -- "${line}"
                hit=0
                break
            fi
        done
    done
    return ${hit}
}

# Helper: print the body of the 'local dirs_to_remove=( ... )' array in FILE
# (between the opening paren and the first ')'). Entries on the opening line
# (single-line array) and a ')' that shares a line with the last entry are both
# included, and extraction stops at that ')' so later code is never scanned.
_extract_dirs_block() {
    awk '/local dirs_to_remove=\(/{sub(/.*dirs_to_remove=\(/,"");f=1} f{if(/\)/){sub(/\).*/,"");print;f=0}else print}' "${1}"
}

# =============================================================================
# TEST: static guard -- dirs_to_remove never lists projects/ or data/
# =============================================================================
test_dirs_to_remove_excludes_student_data() {
    test_start "nuke-vde dirs_to_remove excludes 'projects' and 'data'"

    local block
    block="$(_extract_dirs_block "${NUKE_SRC}")"

    if [[ -z "${block}" ]]; then
        test_fail "dirs_to_remove guard" "could not locate dirs_to_remove array in ${NUKE_SRC}"
        return
    fi

    local bad=""
    if bad="$(_dirs_block_lists_student_dir "${block}")"; then
        test_fail "dirs_to_remove guard" "student dir listed for removal: ${bad}"
    else
        test_pass "dirs_to_remove guard"
    fi
}

# =============================================================================
# TEST: the dirs_to_remove guard flags every projects/data form, and only those
# =============================================================================
test_dirs_guard_detects_all_forms() {
    test_start "dirs_to_remove guard detects all quoting/prefix forms of projects/data"

    local -a flag_cases=(
        '    "projects"'
        "    'data'"
        '    projects'
        '    "${VDE_ROOT_DIR}/projects"'
        '    "$VDE_ROOT_DIR/data"'
        '    ./data'
        '    "data/"'
        $'    "logs"\n    "projects"\n    "env-files"'
    )
    local -a clean_cases=(
        $'    "logs"\n    "env-files"\n    ".cache"\n    ".locks"'
        '    "database"'
        '    "projects-old"'
        '    "logs" # projects'
        '    # the word projects lives only in this comment'
    )

    local c why="" ok=1
    for c in "${flag_cases[@]}"; do
        _dirs_block_lists_student_dir "${c}" >/dev/null || { ok=0; why="not flagged: ${c}"; }
    done
    for c in "${clean_cases[@]}"; do
        _dirs_block_lists_student_dir "${c}" >/dev/null && { ok=0; why="wrongly flagged: ${c}"; }
    done

    if (( ok )); then
        test_pass "dirs_to_remove guard detects all forms"
    else
        test_fail "dirs_to_remove guard detects all forms" "${why}"
    fi
}

# =============================================================================
# TEST: the extraction reads the whole array however it is laid out
# =============================================================================
test_dirs_extraction_shapes() {
    test_start "dirs_to_remove extraction handles single-line, trailing-paren and multi-line arrays"

    local tmp f why="" ok=1
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-extract.XXXXXX")"

    # name|source text|expected: flag (guard must report) or clean
    local -a names=(multiline single-line-bad single-line-ok trailing-paren-ok trailing-paren-bad multiline-unquoted)
    local -a flags=(clean flag clean clean flag flag)
    local -a srcs=(
        $'x() {\n    local dirs_to_remove=(\n        "logs"\n        ".cache"\n    )\n}'
        $'x() {\n    local dirs_to_remove=("logs" "projects")\n}'
        $'x() {\n    local dirs_to_remove=("logs" ".cache")\n}'
        $'x() {\n    local dirs_to_remove=(\n        "logs"\n        ".cache")\n    local other=("projects" "data")\n}'
        $'x() {\n    local dirs_to_remove=(\n        "logs"\n        "data")\n}'
        $'x() {\n    local dirs_to_remove=(\n        "logs"\n        projects\n    )\n}'
    )

    local -i i
    for (( i = 1; i <= ${#names}; i++ )); do
        f="${tmp}/${names[$i]}.zsh"
        print -r -- "${srcs[$i]}" > "${f}"
        local blk; blk="$(_extract_dirs_block "${f}")"
        if _dirs_block_lists_student_dir "${blk}" >/dev/null; then
            [[ "${flags[$i]}" == flag ]] || { ok=0; why="${names[$i]}: wrongly flagged"; }
        else
            [[ "${flags[$i]}" == clean ]] || { ok=0; why="${names[$i]}: not flagged"; }
        fi
    done
    rm -rf "${tmp}"

    if (( ok )); then
        test_pass "dirs_to_remove extraction shapes"
    else
        test_fail "dirs_to_remove extraction shapes" "${why}"
    fi
}

# =============================================================================
# TEST: known_only relocate moves ONLY registered VMs (code-review fix #2)
# =============================================================================
# When nuke offers to relocate a Projects base that may ALSO hold the student's
# own unrelated repos (e.g. ~/Projects, ~/GitHub), it must move only VDE-owned
# <base>/<alias> folders and leave everything else exactly in place.
test_safe_move_tree_known_only_filters() {
    test_start "_safe_move_tree(known_only): moves only registered VMs, leaves the student's other dirs"

    local tmp
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-known.XXXXXX")"
    local src="${tmp}/src" dst="${tmp}/dst"

    # Two registered VMs plus two unrelated student dirs (one hidden).
    mkdir -p "${src}/python" "${src}/rust" "${src}/mywork" "${src}/.dotrepo"
    print -r -- "py"   > "${src}/python/main.py"
    print -r -- "rs"   > "${src}/rust/main.rs"
    print -r -- "MINE" > "${src}/mywork/notes.md"
    print -r -- "DOT"  > "${src}/.dotrepo/cfg"

    _safe_move_tree "${src}" "${dst}" "true"

    local ok=1 why=""

    # Registered VMs moved whole (with contents).
    [[ -f "${dst}/python/main.py" ]] || { ok=0; why="python not moved"; }
    [[ -f "${dst}/rust/main.rs"   ]] || { ok=0; why="rust not moved"; }
    [[ ! -e "${src}/python" ]]       || { ok=0; why="python left in src"; }
    [[ ! -e "${src}/rust"   ]]       || { ok=0; why="rust left in src"; }

    # Unrelated student dirs untouched in src, never moved to dst.
    [[ -f "${src}/mywork/notes.md" && "$(<"${src}/mywork/notes.md")" == "MINE" ]] || { ok=0; why="student dir 'mywork' disturbed"; }
    [[ -f "${src}/.dotrepo/cfg"    && "$(<"${src}/.dotrepo/cfg")"    == "DOT"  ]] || { ok=0; why="hidden student dir '.dotrepo' disturbed"; }
    [[ ! -e "${dst}/mywork"   ]] || { ok=0; why="mywork wrongly moved to dst"; }
    [[ ! -e "${dst}/.dotrepo" ]] || { ok=0; why=".dotrepo wrongly moved to dst"; }

    rm -rf "${tmp}"

    if (( ok )); then
        test_pass "_safe_move_tree known_only filter"
    else
        test_fail "_safe_move_tree known_only filter" "${why}"
    fi
}

# =============================================================================
# Run All Tests
# =============================================================================
echo "=============================================="
echo "VDE nuke-vde Safety Unit Tests"
echo "=============================================="

test_safe_move_tree_non_destructive
test_safe_move_tree_known_only_filters
test_dirs_to_remove_excludes_student_data
test_dirs_guard_detects_all_forms
test_dirs_extraction_shapes

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
