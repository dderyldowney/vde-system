#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for Signet #633: the agent rules describe the agent platforms that
# actually exist (Claude Code and Antigravity's `agy`), not the retired Gemini
# CLI, and they say plainly that .gemini/COMMANDS and .gemini/SKILLS are
# procedures an agent is pointed at; Antigravity also discovers them natively
# through .agents/skills (Signet #634, verified 2026-11-18 with `agy`), while
# Claude Code and every other agent read the named file (Claude Code has no
# commands or skills folder here).
#
# Read-only: it inspects tracked files and never writes anywhere.

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

typeset -a HISTORICAL_PREFIXES=(
    docs/changelogs/ docs/releases/ docs/plans/plans/ docs/archive/
    bin/archive/ .gemini/PLANS/archive/
)

# Section 5 only: from its heading up to (not including) the next `## ` heading, so a
# claim that moves to another section cannot satisfy these tests.
section5() {
    awk '/^## 5\. Agent-Platform Mapping/ { f = 1; print; next } f && /^## / { exit } f { print }' "${VDE_ROOT_DIR}/AGENTS.md"
}
reading_block() { sed -n '/^## READING LOCATIONS/,/^---/p' "${VDE_ROOT_DIR}/$1"; }

test_retired_cli_not_named_as_a_platform() {
    test_start "1: no living file names the retired Gemini CLI as an agent platform"
    local hits line file skip p bad=0 msg=""
    hits="$(git -C "${VDE_ROOT_DIR}" grep -nIiE 'gemini[ -]cli' -- . 2>/dev/null)"
    while IFS= read -r line; do
        [[ -n "${line}" ]] || continue
        file="${line%%:*}"
        skip=0
        for p in "${HISTORICAL_PREFIXES[@]}"; do [[ "${file}" == "${p}"* ]] && skip=1; done
        (( skip )) && continue
        [[ "${file}" == "tests/unit/agent-platforms.test.zsh" ]] && continue
        (( ++bad )); (( bad <= 5 )) && msg+="${line[1,100]} | "
    done <<< "${hits}"
    (( bad == 0 )) && test_pass "no living file names the Gemini CLI" || test_fail "no living file names the Gemini CLI" "${bad} found: ${msg}"
}

test_section5_names_the_real_platforms() {
    test_start "2: AGENTS.md section 5 maps Claude Code and Antigravity, and none of the retired tool names"
    local s; s="$(section5)"
    [[ -n "${s}" ]] || { test_fail "section 5 exists" "heading '## 5. Agent-Platform Mapping' not found"; return; }
    [[ "${s}" == *"Claude Code"* ]] && test_pass "section 5 names Claude Code" || test_fail "section 5 names Claude Code" "missing"
    [[ "${s}" == *"Antigravity"* ]] && test_pass "section 5 names Antigravity" || test_fail "section 5 names Antigravity" "missing"
    local t
    for t in enter_plan_mode generalist codebase_investigator; do
        [[ "${s}" != *"${t}"* ]] && test_pass "section 5 no longer uses '${t}'" || test_fail "section 5 no longer uses '${t}'" "retired Gemini-CLI name still present"
    done
}

# cited_paths -> reads text on stdin and prints every path it cites: a backtick token that contains a slash, or
# a bare file name with a known extension (kilo.json, CLAUDE.md). Absolute paths and options are skipped.
cited_paths() {
    grep -oE '`[^`]+`' | tr -d '`' | tr ' ' '\n' | grep -E '/|\.(json|md|zsh)$' | grep -vE '^/|^-'
}

test_section5_paths_exist() {
    test_start "3: every path section 5 cites exists in the repository"
    local tok bad=0 n=0 msg=""
    while IFS= read -r tok; do
        [[ -n "${tok}" ]] || continue
        (( ++n ))
        [[ -e "${VDE_ROOT_DIR}/${tok}" ]] || { (( ++bad )); msg+="${tok} | "; }
    done < <(section5 | cited_paths)
    (( n > 0 )) || { test_fail "section 5 cites paths" "none extracted: either the table lost its paths or the extraction broke"; return; }
    (( bad == 0 )) && test_pass "all ${n} cited paths exist" || test_fail "all cited paths exist" "${bad} missing: ${msg}"
}

test_cited_paths_include_bare_file_names() {
    test_start "3b: the cited-path extraction also yields bare file names with a known extension (kilo.json), not only tokens that contain a slash"
    local got want
    got="$(print -r -- 'see `kilo.json`, `lib/x`, `zsh`, `CLAUDE.md`, `/abs`, `--flag` and `a.md b/c`' | cited_paths | tr '\n' ' ')"
    want="kilo.json lib/x CLAUDE.md a.md b/c "
    [[ "${got}" == "${want}" ]] \
        && test_pass "extraction yields: ${got}" \
        || test_fail "extraction yields the bare file names too" "got [${got}] want [${want}]"
}

test_section5_is_honest_about_discovery() {
    test_start "4: section 5 says the .gemini commands and skills are procedures, not auto-discovered"
    local s; s="$(section5)"
    [[ "${s}" == *"not auto-discovered"* ]] && test_pass "section 5 states 'not auto-discovered'" \
        || test_fail "section 5 states 'not auto-discovered'" "the claim is missing; agents would assume native /vde-* commands"
}

test_reading_block_points_at_procedures() {
    test_start "5: the READING LOCATIONS block points at the command and skill procedure folders"
    local f b
    for f in AGENTS.md .gemini/instructions.md; do
        b="$(reading_block "${f}")"
        if [[ "${b}" == *'.gemini/COMMANDS/'* && "${b}" == *'.gemini/SKILLS/'* ]]; then
            test_pass "${f} block names .gemini/COMMANDS/ and .gemini/SKILLS/"
        else
            test_fail "${f} block names .gemini/COMMANDS/ and .gemini/SKILLS/" "an agent is never told where the procedures live"
        fi
        # Same phrase as section 5 so the two statements cannot silently diverge.
        if [[ "${b}" == *'not auto-discovered'* ]]; then
            test_pass "${f} block uses the same 'not auto-discovered' wording as section 5"
        else
            test_fail "${f} block uses the same 'not auto-discovered' wording as section 5" "wording differs from section 5"
        fi
    done
}

test_section5_covers_kilo_and_platforms_without_subagents() {
    test_start "7: section 5 says how Kilo and a platform with no sub-agent facility follow the rules"
    local s; s="$(section5)"
    [[ "${s}" == *Kilo* && "${s}" == *kilo.json* ]] \
        && test_pass "section 5 names Kilo and kilo.json" \
        || test_fail "section 5 names Kilo and kilo.json" "Kilo loads these rules through kilo.json but gets no guidance (Sourcery, PR #637)"
    [[ "${s}" == *'no sub-agent facility'* ]] \
        && test_pass "section 5 gives the fallback when a platform has no sub-agent facility" \
        || test_fail "section 5 gives the fallback when a platform has no sub-agent facility" "the Phase 0/4 scout, security-auditor, reviewer and coder steps would have no way to run (Sourcery, PR #637)"
}

test_retired_cli_not_named_as_a_platform
test_section5_names_the_real_platforms
test_section5_paths_exist
test_cited_paths_include_bare_file_names
test_section5_is_honest_about_discovery
test_reading_block_points_at_procedures
test_section5_covers_kilo_and_platforms_without_subagents

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
