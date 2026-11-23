#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

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
# TEST: _safe_move_tree maintains a global move counter (honesty for the summary)
# =============================================================================
# _SAFE_MOVE_COUNT is reset to 0 at the start of every call and incremented once
# per successful move, so the caller can gate "relocated" messages on real moves.
test_safe_move_tree_counts_moves() {
    test_start "_safe_move_tree: _SAFE_MOVE_COUNT counts real moves and resets per call"

    local tmp
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-count.XXXXXX")"
    local src="${tmp}/src" dst="${tmp}/dst"
    local ok=1 why=""

    # (a) two registered VMs movable, one unrelated dir -> exactly 2 moves.
    mkdir -p "${src}/python" "${src}/rust" "${src}/mywork"
    print -r -- "py"   > "${src}/python/main.py"
    print -r -- "rs"   > "${src}/rust/main.rs"
    print -r -- "MINE" > "${src}/mywork/notes.md"

    _safe_move_tree "${src}" "${dst}" "true"
    [[ "${_SAFE_MOVE_COUNT:-}" == 2 ]] \
        || { ok=0; why="(a) expected count 2, got ${_SAFE_MOVE_COUNT:-unset}"; }

    # (b) second call with nothing movable left in src -> counter reset to 0.
    _safe_move_tree "${src}" "${dst}" "true"
    [[ "${_SAFE_MOVE_COUNT:-}" == 0 ]] \
        || { ok=0; why="${why:+${why}; }(b) expected reset to 0, got ${_SAFE_MOVE_COUNT:-unset}"; }

    # (c) HONESTY CASE: dst already holds python/, src has only unrelated 'mywork'
    #     with known_only=true -> nothing moves, so the count must be 0.
    local tmp2="${tmp}/case-c"
    local src2="${tmp2}/src" dst2="${tmp2}/dst"
    mkdir -p "${src2}/mywork" "${dst2}/python"
    print -r -- "MINE" > "${src2}/mywork/notes.md"
    print -r -- "x"    > "${dst2}/python/x"

    _safe_move_tree "${src2}" "${dst2}" "true"
    [[ "${_SAFE_MOVE_COUNT:-}" == 0 ]] \
        || { ok=0; why="${why:+${why}; }(c) nothing movable but count is ${_SAFE_MOVE_COUNT:-unset}"; }

    rm -rf "${tmp}"

    if (( ok )); then
        test_pass "_safe_move_tree move counter"
    else
        test_fail "_safe_move_tree move counter" "${why}"
    fi
}

# =============================================================================
# TEST: a dangling symlink at the destination is an existing collision
# =============================================================================
# A broken symlink fails a plain -e test, so a naive collision check would let
# the move replace it. It must be treated as occupied: left alone, src kept.
test_safe_move_tree_never_replaces_dangling_symlink() {
    test_start "_safe_move_tree: dangling symlink at destination is a collision, never replaced"

    local tmp
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-dangle.XXXXXX")"
    local src="${tmp}/src" dst="${tmp}/dst"

    mkdir -p "${src}" "${dst}"
    print -r -- "MINE" > "${src}/report.txt"
    ln -s "${tmp}/does-not-exist" "${dst}/report.txt"

    unset _SAFE_MOVE_COUNT
    _safe_move_tree "${src}" "${dst}"

    local ok=1 why=""

    # Destination symlink still present and still dangling (not replaced).
    [[ -L "${dst}/report.txt" && ! -e "${dst}/report.txt" ]] \
        || { ok=0; why="dangling destination symlink replaced or removed"; }

    # Source file left in place with its content intact.
    [[ -f "${src}/report.txt" && "$(<"${src}/report.txt")" == "MINE" ]] \
        || { ok=0; why="${why:+${why}; }source report.txt moved or altered"; }

    # Nothing moved, so nothing may be counted (exactly 0, not merely "not 1").
    [[ "${_SAFE_MOVE_COUNT:-unset}" == 0 ]] \
        || { ok=0; why="${why:+${why}; }expected count 0, got ${_SAFE_MOVE_COUNT:-unset}"; }

    rm -rf "${tmp}"

    if (( ok )); then
        test_pass "_safe_move_tree dangling symlink collision"
    else
        test_fail "_safe_move_tree dangling symlink collision" "${why}"
    fi
}

# =============================================================================
# TEST: relocate flags in bin/nuke-vde are gated on the move counter
# =============================================================================
# Static wiring pin: PROJECTS_RELOCATED=true and DATA_RELOCATED=true may only be
# set on a line that carries `_SAFE_MOVE_COUNT > 0` as its own condition. Also forbids combining those flags with an
# `ls -A "${dest}/` listing check (that would again report on a non-empty dest
# rather than on real moves).
test_relocate_flags_gated_on_move_count() {
    test_start "bin/nuke-vde: PROJECTS_RELOCATED / DATA_RELOCATED gated on _SAFE_MOVE_COUNT"

    local -a exec_lines=()
    local line stripped
    setopt localoptions extendedglob
    while IFS= read -r line || [[ -n "${line}" ]]; do
        stripped="${line##[[:space:]]#}"
        [[ -z "${stripped}" || "${stripped}" == \#* ]] && continue
        exec_lines+=("${stripped}")
    done < "${NUKE_SRC}"

    local flag ok=1 why=""
    local -i i n=${#exec_lines}
    for flag in PROJECTS_RELOCATED=true DATA_RELOCATED=true; do
        local -i found=0
        for (( i = 1; i <= n; i++ )); do
            [[ "${exec_lines[i]}" == *"${flag}"* ]] || continue
            (( ++found ))
            # The whole statement must be exactly `(( _SAFE_MOVE_COUNT > 0 )) && FLAG`:
            # same line, `&&` (an `||` would invert the guard), nothing else wrapped
            # around it.
            if [[ "${exec_lines[i]}" != '(( _SAFE_MOVE_COUNT > 0 )) && '"${flag}" ]]; then
                ok=0
                why="${why:+${why}; }${flag} is not exactly '(( _SAFE_MOVE_COUNT > 0 )) && ${flag}': ${exec_lines[i]}"
            fi
        done
        # An assignment that vanished must fail the pin, not silently pass it.
        if (( found == 0 )); then
            ok=0
            why="${why:+${why}; }${flag} assignment not found in bin/nuke-vde"
        fi
    done

    for (( i = 1; i <= n; i++ )); do
        line="${exec_lines[i]}"
        if [[ "${line}" == *'ls -A "${dest}/'* ]] \
            && [[ "${line}" == *PROJECTS_RELOCATED=true* || "${line}" == *DATA_RELOCATED=true* ]]; then
            ok=0
            why="${why:+${why}; }relocate flag combined with ls -A dest check: ${line}"
        fi
    done

    if (( ok )); then
        test_pass "relocate flags gated on _SAFE_MOVE_COUNT"
    else
        test_fail "relocate flags gated on _SAFE_MOVE_COUNT" "${why}"
    fi
}

# =============================================================================
# TEST: offer_relocate_before_nuke itself reports only what really moved
# =============================================================================
# The counter and the wiring pin prove the pieces; this runs the REAL function
# end to end. offer_relocate_before_nuke returns at once without a terminal
# (`[[ -t 0 ]] || return 0`), so the harness runs it under `script`, which gives
# it a pty, and answers its two prompts (relocate? / where to?) from stdin.
# The function bodies are extracted from bin/nuke-vde, never copied, so the test
# cannot drift from the code. The forge is a mktemp dir, never the real VDE root.
# Sets OFFER_OUT (pty output, CRs stripped) and OFFER_RESULT ("projects=.. data=.. dest=..").
_run_offer_relocate() {  # $1=forge root  $2=destination to type at the prompt
    local forge="${1}" dest="${2}" harness="${1}.harness.zsh" fn
    {
        print -r -- "typeset -g VDE_ROOT_DIR='${forge}'"
        print -r -- "source '${VDE_ROOT_DIR}/lib/vde-shell-compat'"
        print -r -- "source '${VDE_ROOT_DIR}/lib/vde-constants'"
        print -r -- "source '${VDE_ROOT_DIR}/lib/vde-errors'"
        print -r -- "source '${VDE_ROOT_DIR}/lib/vde-path-utils'"
        print -r -- "typeset -g DRY_RUN=false SKIP_CONFIRM=false PROJECTS_RELOCATED=false DATA_RELOCATED=false RELOCATE_DEST=''"
        # Same stub as the rest of this file: only python/rust are VDE-owned.
        print -r -- 'is_known_vm() { [[ "${1}" == python || "${1}" == rust ]] }'
        for fn in print_warning print_success print_info ask_yes_no _safe_move_tree offer_relocate_before_nuke; do
            awk "/^${fn}\\(\\) \\{/,/^\\}/" "${NUKE_SRC}"
        done
        print -r -- 'offer_relocate_before_nuke'
        print -r -- 'print -r -- "RESULT projects=${PROJECTS_RELOCATED} data=${DATA_RELOCATED} dest=${RELOCATE_DEST}"'
    } > "${harness}"
    OFFER_OUT="$(printf 'y\n%s\n' "${dest}" | env -u VDE_PROJECTS_DIR script -qec "zsh '${harness}'" /dev/null 2>&1 | tr -d '\r')"
    OFFER_RESULT="$(print -r -- "${OFFER_OUT}" | awk '/^RESULT /{sub(/^RESULT /,""); print}')"
}

test_offer_relocate_nothing_moved_reports_nothing() {
    test_start "offer_relocate_before_nuke: pre-populated destination + nothing movable => 'Nothing needed moving'"
    if ! command -v script >/dev/null 2>&1; then
        echo "[SKIP] 'script' (util-linux) not installed; cannot give the function a pty"
        return 0
    fi
    local tmp; tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-offer.XXXXXX")"
    local forge="${tmp}/forge" dest="${tmp}/safe"
    # Inside the forge: only the student's unrelated dir (not a VDE alias) and an
    # EMPTY data tree, so there is genuinely nothing for nuke to move.
    mkdir -p "${forge}/projects/mywork" "${forge}/data"
    print -r -- "MINE" > "${forge}/projects/mywork/notes.md"
    # The trap: the destination is already non-empty, which the old code mistook
    # for "something moved".
    mkdir -p "${dest}/projects/x"
    print -r -- "pre-existing" > "${dest}/projects/x/f"

    _run_offer_relocate "${forge}" "${dest}"

    local ok=1 why=""
    [[ "${OFFER_RESULT}" == "projects=false data=false dest=" ]] \
        || { ok=0; why="flags/dest wrong: '${OFFER_RESULT:-<no RESULT line; harness did not run>}'"; }
    [[ "${OFFER_OUT}" == *"Nothing needed moving"* ]] \
        || { ok=0; why="${why:+${why}; }missing 'Nothing needed moving'"; }
    [[ "${OFFER_OUT}" != *"Your work was moved under"* ]] \
        || { ok=0; why="${why:+${why}; }claimed 'Your work was moved under' though nothing moved"; }
    # Nothing of the student's was disturbed.
    [[ "$(<"${forge}/projects/mywork/notes.md")" == "MINE" && -f "${dest}/projects/x/f" ]] \
        || { ok=0; why="${why:+${why}; }a student file was disturbed"; }

    rm -rf "${tmp}"
    if (( ok )); then
        test_pass "offer_relocate nothing-moved honesty"
    else
        test_fail "offer_relocate nothing-moved honesty" "${why}"
    fi
}

# Positive control: the same harness must SEE a real relocate, otherwise the test
# above could be passing only because the harness never reaches the move.
test_offer_relocate_real_move_is_reported() {
    test_start "offer_relocate_before_nuke: a registered alias really moves => reported with its destination"
    if ! command -v script >/dev/null 2>&1; then
        echo "[SKIP] 'script' (util-linux) not installed; cannot give the function a pty"
        return 0
    fi
    local tmp; tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-nuke-offer.XXXXXX")"
    local forge="${tmp}/forge" dest="${tmp}/safe"
    mkdir -p "${forge}/projects/python" "${forge}/projects/mywork" "${forge}/data" "${dest}"
    print -r -- "py"   > "${forge}/projects/python/main.py"
    print -r -- "MINE" > "${forge}/projects/mywork/notes.md"

    _run_offer_relocate "${forge}" "${dest}"

    local ok=1 why=""
    [[ "${OFFER_RESULT}" == "projects=true data=false dest=${dest}" ]] \
        || { ok=0; why="flags/dest wrong: '${OFFER_RESULT:-<no RESULT line; harness did not run>}'"; }
    [[ "${OFFER_OUT}" == *"Your work was moved under: ${dest}"* ]] \
        || { ok=0; why="${why:+${why}; }missing 'Your work was moved under'"; }
    [[ -f "${dest}/projects/python/main.py" && ! -e "${forge}/projects/python" ]] \
        || { ok=0; why="${why:+${why}; }python not actually moved"; }
    [[ "$(<"${forge}/projects/mywork/notes.md")" == "MINE" && ! -e "${dest}/projects/mywork" ]] \
        || { ok=0; why="${why:+${why}; }unrelated student dir was moved or altered"; }

    rm -rf "${tmp}"
    if (( ok )); then
        test_pass "offer_relocate real-move reporting"
    else
        test_fail "offer_relocate real-move reporting" "${why}"
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
test_safe_move_tree_counts_moves
test_safe_move_tree_never_replaces_dangling_symlink
test_relocate_flags_gated_on_move_count
test_offer_relocate_nothing_moved_reports_nothing
test_offer_relocate_real_move_is_reported
test_dirs_to_remove_excludes_student_data
test_dirs_guard_detects_all_forms
test_dirs_extraction_shapes

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
