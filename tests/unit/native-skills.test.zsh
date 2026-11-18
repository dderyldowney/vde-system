#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit tests for Signet #634: the 11 .gemini/SKILLS and 8 .gemini/COMMANDS are also
# native Antigravity skills (.agents/skills/<name>/SKILL.md symlinks), WITHOUT
# changing how any other agent reads them: the canonical files keep their paths
# and their bodies; they only gain a YAML frontmatter block whose line 2 is a YAML
# comment carrying the architectural tag (the audit requires the tag on line 2).
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

typeset -a CANON=()
typeset f
for f in "${VDE_ROOT_DIR}"/.gemini/SKILLS/*.md(N) "${VDE_ROOT_DIR}"/.gemini/COMMANDS/*.md(N); do
    CANON+=("${f#${VDE_ROOT_DIR}/}")
done

# frontmatter_field FILE KEY -> value of "KEY: value" inside the leading --- block
frontmatter_field() {
    awk -v k="$2" 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 && index($0, k ": ")==1 {print substr($0, length(k)+3); exit}' "${VDE_ROOT_DIR}/$1"
}

test_canonical_files_exist() {
    test_start "0: the canonical skill and command documents are present (19 expected today)"
    (( ${#CANON} >= 19 )) && test_pass "found ${#CANON} canonical files" || test_fail "found canonical files" "only ${#CANON} (expected the 11 skills and 8 commands)"
}

test_frontmatter_valid() {
    test_start "1: every canonical file starts with valid Antigravity frontmatter and keeps the audit's line-2 tag"
    local rel name desc line2 close bad=0 msg=""
    for rel in "${CANON[@]}"; do
        name="${${rel:t}%.md}"
        line2="$(sed -n 2p "${VDE_ROOT_DIR}/${rel}")"
        desc="$(frontmatter_field "${rel}" description)"
        close="$(sed -n '2,12{/^---$/{=;q}}' "${VDE_ROOT_DIR}/${rel}")"
        if [[ "$(sed -n 1p "${VDE_ROOT_DIR}/${rel}")" != "---" ]]; then
            (( ++bad )); msg+="${rel}: no frontmatter | "; continue
        fi
        [[ "${line2}" == "# @"(forge|armor|shared-law)* ]] || { (( ++bad )); msg+="${rel}: line 2 is not a YAML comment tag | "; }
        [[ "$(frontmatter_field "${rel}" name)" == "${name}" ]] || { (( ++bad )); msg+="${rel}: name != ${name} | "; }
        (( ${#desc} >= 20 )) || { (( ++bad )); msg+="${rel}: description missing/too short | "; }
        [[ -n "${close}" ]] || { (( ++bad )); msg+="${rel}: frontmatter never closed | "; }
    done
    (( bad == 0 )) && test_pass "all ${#CANON} files have valid frontmatter" || test_fail "all files have valid frontmatter" "${bad} problems: ${msg[1,300]}"
}

test_symlinks_resolve() {
    test_start "2: every canonical file has a .agents/skills/<name>/SKILL.md symlink that resolves to it"
    local rel name link want got bad=0 msg=""
    for rel in "${CANON[@]}"; do
        name="${${rel:t}%.md}"
        link="${VDE_ROOT_DIR}/.agents/skills/${name}/SKILL.md"
        if [[ ! -L "${link}" ]]; then (( ++bad )); msg+="${name}: no symlink | "; continue; fi
        want="${VDE_ROOT_DIR:A}/${rel}"
        got="${link:A}"
        [[ "${got}" == "${want}" ]] || { (( ++bad )); msg+="${name}: points at ${got#${VDE_ROOT_DIR:A}/} | "; }
        [[ "$(readlink "${link}")" != /* ]] || { (( ++bad )); msg+="${name}: absolute symlink | "; }
        # Found in review: .gitignore ignored the whole .agents/ folder, so the links
        # existed only on disk and a fresh clone had none. A link must be TRACKED by git
        # and must not be ignored, otherwise the "native skills" claim is false for
        # everyone who clones the repository.
        git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- ".agents/skills/${name}/SKILL.md" >/dev/null 2>&1 \
            || { (( ++bad )); msg+="${name}: link is not tracked by git | "; }
        git -C "${VDE_ROOT_DIR}" check-ignore -q -- ".agents/skills/${name}/SKILL.md" 2>/dev/null \
            && { (( ++bad )); msg+="${name}: link is git-ignored | "; }
    done
    (( bad == 0 )) && test_pass "all ${#CANON} symlinks resolve to their canonical file" || test_fail "all symlinks resolve" "${bad} problems: ${msg[1,300]}"
}

test_no_orphans_or_collisions() {
    test_start "3: no orphan skill folders and no duplicate skill names across skills and commands"
    local d name bad=0 msg=""
    typeset -A seen
    for f in "${CANON[@]}"; do
        name="${${f:t}%.md}"
        [[ -n "${seen[${name}]:-}" ]] && { (( ++bad )); msg+="duplicate name ${name} | "; }
        seen[${name}]=1
    done
    for d in "${VDE_ROOT_DIR}"/.agents/skills/*(N/); do
        name="${d:t}"
        [[ -n "${seen[${name}]:-}" ]] || { (( ++bad )); msg+="orphan .agents/skills/${name} | "; }
    done
    (( bad == 0 )) && test_pass "no orphans, no duplicate names" || test_fail "no orphans, no duplicate names" "${msg}"
}

test_other_agents_unaffected() {
    test_start "4: the canonical files keep their paths and still open with their original heading (other agents read them by path)"
    local rel h bad=0 msg=""
    for rel in "${CANON[@]}"; do
        [[ -f "${VDE_ROOT_DIR}/${rel}" && ! -L "${VDE_ROOT_DIR}/${rel}" ]] || { (( ++bad )); msg+="${rel}: not a regular file at its old path | "; continue; }
        h="$(awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{f=0;next} !f&&/^# /{print;exit}' "${VDE_ROOT_DIR}/${rel}")"
        [[ -n "${h}" ]] || { (( ++bad )); msg+="${rel}: no H1 heading after the frontmatter | "; }
    done
    (( bad == 0 )) && test_pass "every canonical file is still a regular file with its heading" || test_fail "canonical files intact" "${bad} problems: ${msg[1,300]}"
}

test_docs_state_the_new_truth() {
    test_start "5: AGENTS.md and the READING LOCATIONS blocks say Antigravity discovers them natively and others read the file"
    local f s
    s="$(awk '/^## 5\. Agent-Platform Mapping/ { g = 1; print; next } g && /^## / { exit } g { print }' "${VDE_ROOT_DIR}/AGENTS.md")"
    [[ "${s}" == *'discovers them natively'* && "${s}" == *'.agents/skills'* ]] \
        && test_pass "section 5 states native Antigravity discovery via .agents/skills/" \
        || test_fail "section 5 states native Antigravity discovery via .agents/skills" "section 5 of AGENTS.md must contain both 'discovers them natively' and '.agents/skills'"
    for f in AGENTS.md .gemini/instructions.md; do
        local b; b="$(sed -n '/^## READING LOCATIONS/,/^---/p' "${VDE_ROOT_DIR}/${f}")"
        [[ "${b}" == *'discovers them natively'* && "${b}" == *'.agents/skills'* ]] \
            && test_pass "${f} block states native Antigravity discovery" \
            || test_fail "${f} block states native Antigravity discovery" "the READING LOCATIONS block must contain both 'discovers them natively' and '.agents/skills'"
    done
}

test_suite_is_in_the_ci_runner() {
    test_start "6: this suite is listed in tests/run-sovereign-tests.zsh (otherwise CI never runs it)"
    grep -qF 'native-skills.test.zsh' "${VDE_ROOT_DIR}/tests/run-sovereign-tests.zsh" \
        && test_pass "suite is in the CI runner list" \
        || test_fail "suite is in the CI runner list" "tests/run-sovereign-tests.zsh uses an explicit list without it"
}

test_canonical_files_exist
test_frontmatter_valid
test_symlinks_resolve
test_no_orphans_or_collisions
test_other_agents_unaffected
test_docs_state_the_new_truth
test_suite_is_in_the_ci_runner

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
