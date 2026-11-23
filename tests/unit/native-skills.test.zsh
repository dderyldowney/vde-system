#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

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
        # A closed double-quoted string of 20+ characters: a bare length check also accepts
        # an unclosed quote, which is invalid YAML (Sourcery, PR #638).
        [[ "${desc}" =~ '^"[^"]{20,}"$' ]] || { (( ++bad )); msg+="${rel}: description is not a closed double-quoted string of 20+ characters | "; }
        [[ -n "${close}" ]] || { (( ++bad )); msg+="${rel}: frontmatter never closed | "; }
    done
    (( bad == 0 )) && test_pass "all ${#CANON} files have valid frontmatter" || test_fail "all files have valid frontmatter" "${bad} problems: ${msg[1,300]}"
}

# repo_ignores REL -> rc 0 when the REPOSITORY's own .gitignore ignores REL. It runs in a throwaway
# repo with global, system, env and info excludes all out of the picture: `git check-ignore` in the
# real repo also consults core.excludesFile and .git/info/exclude, so a developer's machine-wide
# rule could fail the suite for a valid link, or hide a missing rule (Sourcery, PR #644). The parent
# folder is created because a negated rule such as `!.claude/skills/` only applies to a directory
# that exists.
repo_ignores() {
    local rel="$1" t rc
    local -a clean=(env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR -u GIT_INDEX_FILE GIT_CONFIG_COUNT=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null)
    t="$(mktemp -d)" || return 2
    cp "${VDE_ROOT_DIR}/.gitignore" "${t}/.gitignore" || { rm -rf -- "${t:?}"; return 2; }
    mkdir -p "${t}/${rel:h}"
    : > "${t}/${rel}"
    # The git environment is scrubbed too: under a hook launched from a linked worktree git exports
    # GIT_DIR, and an unscrubbed `git init` would re-initialise THAT gitdir (see
    # tests/unit/spine-git-env-isolation.test.zsh; Sourcery/review, PR #644).
    "${clean[@]}" git -C "${t}" init -q 2>/dev/null || { rm -rf -- "${t:?}"; return 2; }
    "${clean[@]}" git -C "${t}" check-ignore -q -- "${rel}"
    rc=$?
    rm -rf -- "${t:?}"
    return ${rc}   # 0 ignored, 1 not ignored, anything else: the check itself failed
}

# The folders each agent discovers skills in. Antigravity reads .agents/skills (Signet #634);
# Claude Code reads .claude/skills (Signet #642). Both hold ONLY symlinks to the canonical files.
typeset -a SKILL_DIRS=(.agents/skills .claude/skills)

test_symlinks_resolve() {
    test_start "2: every canonical file has a <skill dir>/<name>/SKILL.md symlink that resolves to it (${SKILL_DIRS[*]})"
    local rel name link want got sdir rc bad=0 msg=""
    for sdir in "${SKILL_DIRS[@]}"; do
    for rel in "${CANON[@]}"; do
        name="${${rel:t}%.md}"
        link="${VDE_ROOT_DIR}/${sdir}/${name}/SKILL.md"
        if [[ ! -L "${link}" ]]; then (( ++bad )); msg+="${sdir}/${name}: no symlink | "; continue; fi
        want="${VDE_ROOT_DIR:A}/${rel}"
        got="${link:A}"
        [[ "${got}" == "${want}" ]] || { (( ++bad )); msg+="${sdir}/${name}: points at ${got#${VDE_ROOT_DIR:A}/} | "; }
        [[ "$(readlink "${link}")" != /* ]] || { (( ++bad )); msg+="${sdir}/${name}: absolute symlink | "; }
        # Found in review: .gitignore ignored the whole .agents/ folder, so the links
        # existed only on disk and a fresh clone had none. A link must be TRACKED by git
        # and must not be ignored, otherwise the "native skills" claim is false for
        # everyone who clones the repository. The same trap exists for .claude/ (Signet #642).
        git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- "${sdir}/${name}/SKILL.md" >/dev/null 2>&1 \
            || { (( ++bad )); msg+="${sdir}/${name}: link is not tracked by git | "; }
        # Judged on the repository's own rules in isolation (see repo_ignores): by default git skips
        # TRACKED paths, so a tracked link would look "not ignored" even when a rule matches it
        # (Sourcery, PR #635/#638), and global excludes must not change the verdict (PR #644).
        repo_ignores "${sdir}/${name}/SKILL.md"; rc=$?
        (( rc == 0 )) && { (( ++bad )); msg+="${sdir}/${name}: link is git-ignored | "; }
        (( rc > 1 )) && { (( ++bad )); msg+="${sdir}/${name}: the ignore check itself failed (rc ${rc}) | "; }
    done
    done
    (( bad == 0 )) && test_pass "all ${#CANON} symlinks resolve to their canonical file in ${#SKILL_DIRS} folders" || test_fail "all symlinks resolve" "${bad} problems: ${msg[1,300]}"
}

test_no_orphans_or_collisions() {
    test_start "3: no orphan skill folders and no duplicate skill names across skills and commands"
    local d name sdir bad=0 msg=""
    typeset -A seen
    for f in "${CANON[@]}"; do
        name="${${f:t}%.md}"
        [[ -n "${seen[${name}]:-}" ]] && { (( ++bad )); msg+="duplicate name ${name} | "; }
        seen[${name}]=1
    done
    for sdir in "${SKILL_DIRS[@]}"; do
    for d in "${VDE_ROOT_DIR}/${sdir}"/*(N/); do
        name="${d:t}"
        [[ -n "${seen[${name}]:-}" ]] || { (( ++bad )); msg+="orphan ${sdir}/${name} | "; }
    done
    done
    # The docs promise these folders hold ONLY symlinks. Git cannot see an untracked stray file here
    # (the .gitignore exception unignores the whole folder), so look at the filesystem: everything
    # that is not a directory must be a <name>/SKILL.md symlink.
    local stray
    for sdir in "${SKILL_DIRS[@]}"; do
        for stray in "${VDE_ROOT_DIR}/${sdir}"/**/*(ND^/); do
            [[ "${stray:t}" == SKILL.md && -L "${stray}" && "${stray:h:h}" == "${VDE_ROOT_DIR}/${sdir}" ]] \
                || { (( ++bad )); msg+="stray non-symlink entry ${stray#${VDE_ROOT_DIR}/} | "; }
        done
    done
    (( bad == 0 )) && test_pass "no orphans, no duplicate names, no stray files" || test_fail "no orphans, no duplicate names, no stray files" "${msg}"
}

test_claude_local_files_stay_ignored() {
    test_start "10: only .claude/skills is tracked; Claude's personal settings, backups and hooks stay git-ignored"
    local p rc bad=0 msg=""
    # Unignoring .claude/skills must not unignore the rest of .claude/ (settings.local.json
    # holds personal permissions). Judged on the repository's own rules in isolation (repo_ignores),
    # so a machine-wide ignore cannot make this pass when the repository rule is removed.
    for p in .claude/settings.local.json .claude/settings.json .claude/hooks/direnv-session-env.zsh .claude/settings.json.bak.1; do
        repo_ignores "${p}"; rc=$?
        (( rc == 0 )) || { (( ++bad )); msg+="${p} is NOT ignored (check rc ${rc}) | "; }
    done
    # Nothing but skill symlinks may be tracked under .claude/.
    local tracked
    tracked="$(git -C "${VDE_ROOT_DIR}" ls-files -- .claude | grep -v -E '^\.claude/skills/[^/]+/SKILL\.md$')"
    [[ -z "${tracked}" ]] || { (( ++bad )); msg+="unexpected tracked .claude files: ${tracked[1,120]} | "; }
    (( bad == 0 )) && test_pass ".claude/ personal files stay ignored; only skill links are tracked" || test_fail ".claude/ personal files stay ignored" "${bad} problems: ${msg[1,300]}"
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

test_tool_mandated_bullet_names_the_discovery_folders() {
    test_start "12: the 'Tool-mandated entry points' rule names .agents/skills and .claude/skills, so the root folders do not contradict 'nothing AI-specific at the root'"
    local f b
    for f in AGENTS.md .gemini/instructions.md; do
        b="$(grep -m1 -F 'Tool-mandated entry points' "${VDE_ROOT_DIR}/${f}")"
        [[ "${b}" == *'.agents/skills'* && "${b}" == *'.claude/skills'* ]] \
            && test_pass "${f}: the tool-mandated bullet names both discovery folders" \
            || test_fail "${f}: the tool-mandated bullet names both discovery folders" "the bullet says: ${b[1,200]} (Sourcery, PR #644)"
    done
}

test_root_tree_lists_claude() {
    test_start "13: the root structure tree in docs/reference/directory-structure.md lists .claude/"
    local tree
    tree="$(awk '/^## Root Structure/ { f = 1 } f && /^```/ { n++ ; next } f && n == 1 { print } n == 2 { exit }' "${VDE_ROOT_DIR}/docs/reference/directory-structure.md")"
    [[ "${tree}" == *'.claude/'* && "${tree}" == *'.agents/'* ]] \
        && test_pass "the root tree lists .agents/ and .claude/" \
        || test_fail "the root tree lists .agents/ and .claude/" "the 'complete directory layout' omits a discovery folder (Sourcery, PR #644)"
}

test_debug_procedure_cannot_inject_a_shell_command() {
    test_start "14: /vde-debug validates the feature, library and tag names and never passes them to a shell unquoted"
    local f="${VDE_ROOT_DIR}/.gemini/COMMANDS/vde-debug.md"
    # Sourcery (PR #644): the procedure builds `python3 -m behave tests/.../<feature>.feature` and
    # `zsh tests/unit/<libname>.test.zsh` from $ARGUMENTS or an error log, so a crafted value such as
    # $(cmd) would run. Same class as /vde-new-vm (PR #638): validate first, then pass quoted.
    grep -qF '^[A-Za-z0-9][A-Za-z0-9_-]*$' "${f}" \
        && test_pass "the procedure states the allowed name pattern" \
        || test_fail "the procedure states the allowed name pattern" "no validation rule before a name reaches a shell"
    # The rule must come BEFORE the first step that acts on the input: Step 1 classifies it and
    # Step 2 spawns agents that look the value up, so validating only at Step 3 is too late.
    local vline sline
    vline="$(grep -n -F '^[A-Za-z0-9][A-Za-z0-9_-]*$' "${f}" | head -1 | cut -d: -f1)"
    sline="$(grep -n -m1 -E '^\*\*Step 1' "${f}" | cut -d: -f1)"
    [[ -n "${vline}" && -n "${sline}" ]] && (( vline < sline )) \
        && test_pass "the validation rule comes before Step 1" \
        || test_fail "the validation rule comes before Step 1" "rule at line '${vline}', Step 1 at line '${sline}' (review, PR #644)"
    grep -qE "(behave|zsh) tests/" "${f}" \
        && test_fail "no unquoted test path built from a name remains" "an unquoted '(behave|zsh) tests/...' command is still in the procedure" \
        || test_pass "no unquoted test path built from a name remains"
    grep -qF "'tests/features/core-infrastructure/<feature>.feature'" "${f}" && grep -qF "'tests/unit/<libname>.test.zsh'" "${f}" \
        && test_pass "the commands pass the paths single-quoted" \
        || test_fail "the commands pass the paths single-quoted" "expected single-quoted test paths in the reproduce commands"
}

test_claude_row_does_not_present_skills_as_subagents() {
    test_start "15: section 5's Claude Code Sub-Agents cell calls the role skills single-agent procedures, not sub-agents"
    local row
    row="$(awk '/^## 5\. Agent-Platform Mapping/ { f = 1 } f && /^\| Sub-Agents/ { print; exit }' "${VDE_ROOT_DIR}/AGENTS.md")"
    [[ "${row}" == *'.claude/skills'* && "${row}" == *'single-agent'* ]] \
        && test_pass "the Claude cell says the role skills are single-agent procedures" \
        || test_fail "the Claude cell says the role skills are single-agent procedures" "row says: ${row[1,240]} (review, PR #644)"
}

test_new_vm_procedure_cannot_inject_a_shell_command() {
    test_start "7: /vde-new-vm validates the VM name and never interpolates it into a double-quoted shell argument"
    local f="${VDE_ROOT_DIR}/.gemini/COMMANDS/vde-new-vm.md"
    # Sourcery (PR #638, High): the procedure ran `grep -i "<name>" ...`; a name such as
    # $(cmd) satisfies "lowercase, no spaces" and would be executed by the shell. The
    # procedure is now a one-slash-command away in Antigravity, so it must validate the
    # name first and pass it as a fixed string in single quotes.
    grep -qF '^[a-z][a-z0-9-]*$' "${f}" \
        && test_pass "the procedure states the allowed name pattern ^[a-z][a-z0-9-]*\$" \
        || test_fail "the procedure states the allowed name pattern" "no validation rule before the name reaches a shell"
    grep -qE 'grep -iF -- '\''<name>'\''' "${f}" \
        && test_pass "the conflict check passes the name as a single-quoted fixed string" \
        || test_fail "the conflict check passes the name as a single-quoted fixed string" "expected: grep -iF -- '<name>' data/vm-types.json"
    grep -qE 'grep -i "<name>"' "${f}" \
        && test_fail "no double-quoted interpolation of the name remains" "grep -i \"<name>\" is still in the procedure" \
        || test_pass "no double-quoted interpolation of the name remains"
}

test_directory_guide_lists_the_native_skills_folder() {
    test_start "8: docs/reference/directory-structure.md lists .agents/skills and .claude/skills"
    local d
    for d in .agents/skills .claude/skills; do
        grep -qF "${d}" "${VDE_ROOT_DIR}/docs/reference/directory-structure.md" \
            && test_pass "the directory guide lists ${d}" \
            || test_fail "the directory guide lists ${d}" "the guide calls its tree complete but omits the folder (Sourcery, PR #638; Signet #642)"
    done
}

test_docs_name_the_claude_skills_folder() {
    test_start "11: AGENTS.md section 5 and the READING LOCATIONS blocks say Claude Code discovers the skills through .claude/skills"
    local f s b
    s="$(awk '/^## 5\. Agent-Platform Mapping/ { g = 1; print; next } g && /^## / { exit } g { print }' "${VDE_ROOT_DIR}/AGENTS.md")"
    [[ "${s}" == *'.claude/skills'* ]] \
        && test_pass "section 5 names .claude/skills" \
        || test_fail "section 5 names .claude/skills" "section 5 of AGENTS.md does not mention .claude/skills"
    for f in AGENTS.md .gemini/instructions.md; do
        b="$(sed -n '/^## READING LOCATIONS/,/^---/p' "${VDE_ROOT_DIR}/${f}")"
        [[ "${b}" == *'.claude/skills'* ]] \
            && test_pass "${f} READING LOCATIONS block names .claude/skills" \
            || test_fail "${f} READING LOCATIONS block names .claude/skills" "the block does not mention .claude/skills"
    done
}

test_subagents_row_names_the_native_role_skills() {
    test_start "9: section 5's Sub-Agents row tells Antigravity users the role skills exist natively"
    local row
    row="$(awk '/^## 5\. Agent-Platform Mapping/ { f = 1 } f && /^\| Sub-Agents/ { print; exit }' "${VDE_ROOT_DIR}/AGENTS.md")"
    [[ "${row}" == *scout* && "${row}" == *security-auditor* && "${row}" == *reviewer* && "${row}" == *coder* ]] \
        && test_pass "the Sub-Agents row names the scout, security-auditor, reviewer and coder skills" \
        || test_fail "the Sub-Agents row names the scout, security-auditor, reviewer and coder skills" "row says: ${row[1,200]}"
}

test_canonical_files_exist
test_frontmatter_valid
test_new_vm_procedure_cannot_inject_a_shell_command
test_directory_guide_lists_the_native_skills_folder
test_subagents_row_names_the_native_role_skills
test_symlinks_resolve
test_no_orphans_or_collisions
test_other_agents_unaffected
test_docs_state_the_new_truth
test_claude_local_files_stay_ignored
test_docs_name_the_claude_skills_folder
test_tool_mandated_bullet_names_the_discovery_folders
test_root_tree_lists_claude
test_debug_procedure_cannot_inject_a_shell_command
test_claude_row_does_not_present_skills_as_subagents

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
