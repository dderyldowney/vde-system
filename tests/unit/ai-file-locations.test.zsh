#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for Signet #632: AI-only project-management files live under
# .gemini/STATE, the Strike lineage write-up lives under docs/architecture, and
# every reference (code, agent rules, project and user docs) points at the new
# locations. PROJECT_STATUS.md deliberately STAYS at the root: it is part of the
# version-sync / Gospel mechanism and a certified record people read.
#
# Read-only: it inspects tracked files with git and never writes anywhere.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset -i TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; (( ++TESTS_PASSED )); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; (( ++TESTS_FAILED )); }

typeset -r NEW_MEMORY='.gemini/STATE/MEMORY.md'
typeset -r NEW_HANDOVER='.gemini/STATE/session_handover.md'
typeset -r NEW_LINEAGE='docs/architecture/lineage-of-a-strike.md'

# Paths that describe the PAST and are never rewritten by a relocation.
typeset -a HISTORICAL_PREFIXES=(
    docs/changelogs/ docs/releases/ docs/plans/plans/ docs/archive/
    bin/archive/ .gemini/PLANS/archive/
)

tracked() { git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- "$1" >/dev/null 2>&1; }

test_files_moved() {
    test_start "1: the three files live at their new homes and are gone from the root"
    local f
    for f in "${NEW_MEMORY}" "${NEW_HANDOVER}" "${NEW_LINEAGE}"; do
        tracked "${f}" && test_pass "tracked at ${f}" || test_fail "tracked at ${f}" "not tracked there"
    done
    for f in MEMORY.md session_handover.md LINEAGE_OF_A_STRIKE.md; do
        tracked "${f}" && test_fail "${f} gone from root" "still tracked at the root" || test_pass "${f} gone from root"
    done
    tracked PROJECT_STATUS.md && test_pass "PROJECT_STATUS.md stays at the root" \
        || test_fail "PROJECT_STATUS.md stays at the root" "it moved, but it is part of the version-sync/Gospel mechanism"
}

# line_of FILE PATTERN -> first matching line (empty if none), comments included
line_of() { grep -m1 -E -- "$2" "${VDE_ROOT_DIR}/$1" 2>/dev/null; }

test_enforcer_mandatory_files() {
    test_start "2: bin/vde-enforce-uap.zsh requires MEMORY.md at its NEW path"
    local l; l="$(line_of bin/vde-enforce-uap.zsh '^MANDATORY_FILES=')"
    [[ "${l}" == *"${NEW_MEMORY}"* ]] && test_pass "mandatory list names ${NEW_MEMORY}" \
        || test_fail "mandatory list names ${NEW_MEMORY}" "line is: ${l}"
    [[ "${l}" != *'"MEMORY.md"'* ]] && test_pass "mandatory list no longer names root MEMORY.md" \
        || test_fail "mandatory list no longer names root MEMORY.md" "line is: ${l}"
}

test_sync_version_paths() {
    test_start "3: bin/vde-sync-version edits MEMORY.md at its NEW path"
    local f="${VDE_ROOT_DIR}/bin/vde-sync-version" bad targets reads
    bad="$(grep -cE '\./MEMORY\.md' "${f}")"
    # Count REAL targets only, each ending exactly at the path. A loose substring count
    # also matches comments, log lines and a nonexistent `...MEMORY.md.bak` path
    # (Sourcery, PR #636): four sed targets aimed at .bak still left six matching lines.
    targets="$(grep -cE 'vde_sed_inplace .*"\./\.gemini/STATE/MEMORY\.md"[[:space:]]*$' "${f}")"
    reads="$(grep -cE 'sed -n .*"\./\.gemini/STATE/MEMORY\.md"' "${f}")"
    (( bad == 0 )) && test_pass "no './MEMORY.md' left" || test_fail "no './MEMORY.md' left" "${bad} stale occurrence(s)"
    (( targets == 5 )) && test_pass "all 5 vde_sed_inplace targets end exactly at ./${NEW_MEMORY}" || test_fail "all 5 vde_sed_inplace targets end exactly at ./${NEW_MEMORY}" "only ${targets} of 5 do"
    (( reads == 1 )) && test_pass "the highlights read uses ./${NEW_MEMORY}" || test_fail "the highlights read uses ./${NEW_MEMORY}" "${reads} matching read(s), expected 1"
}

test_paired_update_enforcer_path() {
    test_start "4: bin/paired_update_enforcer reads the handover at its NEW path"
    local l; l="$(line_of bin/paired_update_enforcer '^HANDOVER=')"
    [[ "${l}" == "HANDOVER=\"${NEW_HANDOVER}\"" ]] && test_pass "HANDOVER points at ${NEW_HANDOVER}" \
        || test_fail "HANDOVER points at ${NEW_HANDOVER}" "line is: ${l}"
}

test_agents_startup_checklist() {
    test_start "5: the AGENTS.md startup checklist imports the NEW paths"
    local f="${VDE_ROOT_DIR}/AGENTS.md"
    grep -qF "@${NEW_MEMORY}" "${f}" && test_pass "checklist reads @${NEW_MEMORY}" || test_fail "checklist reads @${NEW_MEMORY}" "not found"
    grep -qF "@${NEW_HANDOVER}" "${f}" && test_pass "checklist reads @${NEW_HANDOVER}" || test_fail "checklist reads @${NEW_HANDOVER}" "not found"
}

test_no_stale_references() {
    test_start "6: no tracked file outside the historical set names the old root paths"
    local hits line file skip p bad=0 msg=""
    # A reference is stale unless the name is directly preceded by STATE/ .
    hits="$(git -C "${VDE_ROOT_DIR}" grep -nP '(?<!STATE/)\b(MEMORY|session_handover)\.md\b|LINEAGE_OF_A_STRIKE' -- . 2>/dev/null)"
    while IFS= read -r line; do
        [[ -n "${line}" ]] || continue
        file="${line%%:*}"
        skip=0
        for p in "${HISTORICAL_PREFIXES[@]}"; do [[ "${file}" == "${p}"* ]] && skip=1; done
        (( skip )) && continue
        # the files at their new homes may name themselves
        [[ "${file}" == "${NEW_MEMORY}" || "${file}" == "${NEW_HANDOVER}" ]] && continue
        # this test names the old paths on purpose
        [[ "${file}" == "tests/unit/ai-file-locations.test.zsh" ]] && continue
        # An ASCII tree lists a file POSITIONALLY under its parent node, so it
        # cannot carry the STATE/ prefix on the entry itself; test 7 proves the
        # entries really sit under the STATE node.
        [[ "${file}" == "docs/reference/directory-structure.md" && "${line}" == *[├└]──\ (MEMORY|session_handover).md* ]] && continue
        (( ++bad ))
        (( bad <= 6 )) && msg+="${line[1,110]} | "
    done <<< "${hits}"
    (( bad == 0 )) && test_pass "no stale references" || test_fail "no stale references" "${bad} stale: ${msg}"
}

test_lineage_discoverable() {
    test_start "7: the lineage doc is linked from the architecture docs and the layout doc shows the new homes"
    local o="${VDE_ROOT_DIR}/docs/architecture/overview.md" d="${VDE_ROOT_DIR}/docs/reference/directory-structure.md"
    grep -qF 'lineage-of-a-strike' "${o}" && test_pass "overview.md links the lineage doc" || test_fail "overview.md links the lineage doc" "no link"
    grep -qF '.gemini/STATE' "${d}" && test_pass "directory-structure.md shows .gemini/STATE" || test_fail "directory-structure.md shows .gemini/STATE" "not shown"
    grep -qE '^[├└]── (MEMORY|session_handover)\.md' "${d}" && test_fail "directory-structure.md no longer lists them at the root" "still listed at the root" \
        || test_pass "directory-structure.md no longer lists them at the root"
    # The two entries must sit UNDER a STATE/ node: after the 'STATE/' line, before the next
    # entry that is not deeper than it, both file names appear.
    local state_block
    state_block="$(awk '/STATE\//{f=1; match($0,/[│ ├└─]*/); ind=RLENGTH; next} f{match($0,/[│ ├└─]*/); if(RLENGTH<=ind) exit; print}' "${d}")"
    [[ "${state_block}" == *MEMORY.md* && "${state_block}" == *session_handover.md* ]] \
        && test_pass "MEMORY.md and session_handover.md are listed under the STATE/ node" \
        || test_fail "MEMORY.md and session_handover.md are listed under the STATE/ node" "block under STATE/ was: [${state_block}]"
}

test_agent_entry_points_tell_agents_where_to_read() {
    test_start "8: every agent entry point states the reading locations"
    local root="${VDE_ROOT_DIR}" f
    # .gemini/instructions.md is the single file that reaches Claude (CLAUDE.md
    # imports it), Gemini (GEMINI.md is a symlink to it) and Kilo (kilo.json).
    for f in .gemini/instructions.md AGENTS.md; do
        if grep -qF 'READING LOCATIONS' "${root}/${f}" \
            && grep -qF "${NEW_MEMORY}" "${root}/${f}" \
            && grep -qF "${NEW_HANDOVER}" "${root}/${f}" \
            && grep -qF '.gemini/RULES' "${root}/${f}"; then
            test_pass "${f} has a READING LOCATIONS block naming STATE and RULES"
        else
            test_fail "${f} has a READING LOCATIONS block naming STATE and RULES" "block or a path is missing"
        fi
    done
    if grep -qF '.gemini/STATE' "${root}/CLAUDE.md"; then
        test_pass "CLAUDE.md points Claude at .gemini/STATE"
    else
        test_fail "CLAUDE.md points Claude at .gemini/STATE" "no pointer"
    fi
}

test_agent_wiring_is_intact() {
    test_start "9: the routes that deliver instructions.md to each agent are intact"
    local root="${VDE_ROOT_DIR}" target
    target="$(readlink "${root}/GEMINI.md" 2>/dev/null)"
    [[ "${target}" == ".gemini/instructions.md" ]] && test_pass "GEMINI.md is a symlink to .gemini/instructions.md" \
        || test_fail "GEMINI.md is a symlink to .gemini/instructions.md" "readlink says: [${target}]"
    grep -qF '@.gemini/instructions.md' "${root}/CLAUDE.md" && test_pass "CLAUDE.md imports .gemini/instructions.md" \
        || test_fail "CLAUDE.md imports .gemini/instructions.md" "import line missing"
    grep -qF '".gemini/instructions.md"' "${root}/kilo.json" && test_pass "kilo.json lists .gemini/instructions.md" \
        || test_fail "kilo.json lists .gemini/instructions.md" "not listed"
}

test_no_dangling_agent_pointers() {
    test_start "10: every @path import and every path an agent entry file points at EXISTS"
    local root="${VDE_ROOT_DIR}" f token rel bad=0 msg="" n=0
    local -a files=(AGENTS.md CLAUDE.md .gemini/instructions.md)
    for f in "${files[@]}"; do
        # @imports: @something/with/slashes or @name.md  (tags like @armor/@forge have neither)
        while IFS= read -r token; do
            [[ -n "${token}" ]] || continue
            rel="${token#@}"
            (( ++n ))
            if [[ ! -e "${root}/${rel}" ]]; then
                (( ++bad )); msg+="${f}: ${token} | "
            fi
        done < <(grep -oE '(^|[[:space:]`(])@[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)*(\.md|/)' "${root}/${f}" | sed -E 's/^[[:space:]`(]+//')
    done
    # paths inside the READING LOCATIONS block (backticked, ending in .md, .json or /)
    for f in AGENTS.md .gemini/instructions.md; do
        while IFS= read -r token; do
            [[ -n "${token}" ]] || continue
            (( ++n ))
            if [[ ! -e "${root}/${token}" ]]; then
                (( ++bad )); msg+="${f}: ${token} | "
            fi
        done < <(sed -n '/^## READING LOCATIONS/,/^---/p' "${root}/${f}" | grep -oE '`[A-Za-z0-9_./-]+(\.md|\.json|/)`' | tr -d '`')
    done
    (( n > 0 )) || { test_fail "found pointers to check" "extracted none: the extraction itself is broken"; return; }
    (( bad == 0 )) && test_pass "all ${n} pointers resolve" || test_fail "all pointers resolve" "${bad} dangling: ${msg}"
}

reading_block() { sed -n '/^## READING LOCATIONS/,/^---/p' "${VDE_ROOT_DIR}/$1"; }

test_directory_pointers_hold_files() {
    test_start "12: every directory the READING LOCATIONS block names holds files directly (not only sub-folders)"
    # Found in review: the block called .gemini/PLANS/ the home of 'active' plans, but that
    # directory only contains archive/. A bare 'directory exists' test cannot see that.
    local f d bad=0 n=0 msg=""
    for f in AGENTS.md .gemini/instructions.md; do
        while IFS= read -r d; do
            [[ -n "${d}" ]] || continue
            (( ++n ))
            if ! git -C "${VDE_ROOT_DIR}" ls-files -- "${d}" | awk -v d="${d}" 'index($0,d)==1 { r=substr($0,length(d)+1); if (r !~ /\//) c++ } END { exit c ? 0 : 1 }'; then
                (( ++bad )); msg+="${f}: ${d} | "
            fi
        done < <(reading_block "${f}" | grep -oE '`[A-Za-z0-9_./-]+/`' | tr -d '`')
    done
    (( n > 0 )) || { test_fail "directory pointers found" "extracted none: the extraction is broken"; return; }
    (( bad == 0 )) && test_pass "all ${n} directory pointers hold files directly" \
        || test_fail "directory pointers hold files directly" "${bad} hold only sub-folders: ${msg}"
}

test_reading_blocks_are_identical() {
    test_start "13: the READING LOCATIONS block is byte-identical in AGENTS.md and .gemini/instructions.md"
    local a b
    a="$(reading_block AGENTS.md)"; b="$(reading_block .gemini/instructions.md)"
    [[ -n "${a}" && -n "${b}" ]] || { test_fail "blocks present" "a block is missing"; return; }
    if [[ "${a}" == "${b}" ]]; then
        test_pass "the two blocks are identical"
    else
        test_fail "the two blocks are identical" "they drifted: $(diff <(print -r -- "${a}") <(print -r -- "${b}") | head -4 | tr '\n' '|' | cut -c1-200)"
    fi
}

test_no_dead_paths_in_instruction_files() {
    test_start "14: every repository path an instruction file names is TRACKED (entry points, spec, state, rules, commands, skills)"
    # Instruction files must name only paths that exist. Only tokens that start with a real
    # top-level directory are checked, so patterns (<alias>, *), remote refs (origin/develop),
    # branch names and container paths (/vde/...) are never mistaken for repository files.
    local root="${VDE_ROOT_DIR}" f token rel bad=0 n=0 msg="" base
    # the entry points, the spec and every state, rule, command and skill file; globs are anchored
    # to the checkout so the result does not depend on the caller's working directory
    local -a files=("${root}"/{AGENTS.md,CLAUDE.md,.gemini/instructions.md,docs/governance/vde-spec.md} "${root}"/.gemini/{STATE,RULES,COMMANDS,SKILLS}/*.md(N))
    files=("${files[@]#${root}/}")
    local tops='bin|lib|tests|docs|plans|scripts|data|templates|configs|\.gemini|\.github'
    # build artifacts the rules name before they exist (each is in .gitignore)
    local -a generated=(tests/behave-results.json)
    for f in "${files[@]}"; do
        while IFS= read -r token; do
            [[ -n "${token}" ]] || continue
            rel="${token#./}"
            # a named build artifact is legitimately absent until it is generated; every other
            # path must exist, so a misspelled path that happens to match an ignore glob is still caught
            (( ${generated[(Ie)${rel}]} )) && continue
            (( ++n ))
            # the path must be TRACKED, not merely present in this working copy: a clean clone has no
            # untracked files
            if [[ -z "$(git -C "${root}" ls-files -- "${rel}")" ]]; then
                (( ++bad )); msg+="${f}: ${token} | "
            fi
        done < <(grep -oE "\`(\./)?(${tops})/[A-Za-z0-9_./-]*[A-Za-z0-9_]\`" "${root}/${f}" | tr -d '`')
        # a bare feature-file name (no directory) must name a tracked feature file
        while IFS= read -r token; do
            [[ -n "${token}" ]] || continue
            (( ++n ))
            if ! git -C "${root}" ls-files -- "tests/features/**/${token}" "tests/features/${token}" | grep -q .; then
                (( ++bad )); msg+="${f}: ${token} | "
            fi
        done < <(grep -oE '`[A-Za-z0-9_-]+\.feature`' "${root}/${f}" | tr -d '`')
    done
    (( n > 0 )) || { test_fail "found paths to check" "extracted none: the extraction itself is broken"; return; }
    (( bad == 0 )) && test_pass "all ${n} named paths resolve" || test_fail "named paths resolve" "${bad} dead: ${msg}"
}

test_files_moved
test_no_dead_paths_in_instruction_files
test_directory_pointers_hold_files
test_reading_blocks_are_identical
test_no_dangling_agent_pointers
test_enforcer_mandatory_files
test_sync_version_paths
test_paired_update_enforcer_path
test_agents_startup_checklist
test_no_stale_references
test_lineage_discoverable
test_agent_entry_points_tell_agents_where_to_read
test_agent_wiring_is_intact

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
