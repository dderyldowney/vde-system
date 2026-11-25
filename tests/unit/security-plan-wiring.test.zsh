#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit tests for Signet #736: the project security process exists, is the public
# policy, and every agent entry point is bound to it (reads it at startup, names it
# in READING LOCATIONS, and the Sovereign Audit refuses to run without it).
#
# Read-only: it inspects tracked files with git and grep and never writes anywhere.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="${0:A:h:h:h}"
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

typeset -r POLICY='SECURITY.md'
typeset -r PROCESS='docs/governance/security-process.md'
typeset -r INDEX='docs/security/advisories.md'
typeset -r RULE='.gemini/RULES/security.md'
typeset -r SKILL='.gemini/SKILLS/security-auditor.md'
typeset -r PREAMBLE='.gemini/RULES/security-preamble.md'

# tracked FILE: in git's index AND present, non-empty, in the working tree (a file
# deleted from the worktree is still "tracked" until it is committed away).
tracked() { git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- "$1" >/dev/null 2>&1 && [[ -f "${VDE_ROOT_DIR}/$1" && -s "${VDE_ROOT_DIR}/$1" ]]; }
# has FILE FIXED-STRING
has() { grep -qF -- "$2" "${VDE_ROOT_DIR}/$1" 2>/dev/null; }
# expect_has LABEL FILE FIXED-STRING
expect_has() {
    if has "$2" "$3"; then test_pass "$1"; else test_fail "$1" "$2 does not contain [$3]"; fi
}
reading_block() { sed -n '/^## READING LOCATIONS/,/^---/p' "${VDE_ROOT_DIR}/$1"; }

test_files_tracked() {
    test_start "1: the four security documents are tracked"
    local f
    for f in "${POLICY}" "${PROCESS}" "${INDEX}" "${RULE}"; do
        tracked "${f}" && test_pass "${f} is tracked" || test_fail "${f} is tracked" "not tracked"
    done
}

test_reading_locations() {
    test_start "2: both READING LOCATIONS blocks name the agent rule and the process"
    local f blk
    for f in AGENTS.md .gemini/instructions.md; do
        blk="$(reading_block "${f}")"
        [[ "${blk}" == *"\`${RULE}\`"* ]] && test_pass "${f} names ${RULE}" \
            || test_fail "${f} names ${RULE}" "missing from READING LOCATIONS"
        [[ "${blk}" == *"\`${PROCESS}\`"* ]] && test_pass "${f} names ${PROCESS}" \
            || test_fail "${f} names ${PROCESS}" "missing from READING LOCATIONS"
    done
}

test_startup_binding() {
    test_start "3: every agent entry point binds the agent to the security rule"
    # The startup checklist (main agent) must import the rule with an @path.
    local checklist
    checklist="$(sed -n '/^## 1\. STOP/,/^---/p' "${VDE_ROOT_DIR}/AGENTS.md")"
    [[ "${checklist}" == *"@${RULE}"* ]] && test_pass "AGENTS.md startup checklist reads @${RULE}" \
        || test_fail "AGENTS.md startup checklist reads @${RULE}" "not in the checklist"
    expect_has "AGENTS.md core mandates carry the Security Mandate" AGENTS.md '**Security Mandate'
    expect_has ".gemini/instructions.md carries THE SECURITY MANDATE" .gemini/instructions.md '**THE SECURITY MANDATE**'
    expect_has ".gemini/instructions.md points at ${RULE} from the mandate" .gemini/instructions.md "${RULE}"
    expect_has "CLAUDE.md points Claude at ${RULE}" CLAUDE.md "${RULE}"
    expect_has "the security-auditor skill follows ${RULE}" "${SKILL}" "${RULE}"
}

# run_enforcer_in FIXTURE -> runs a copy of the real enforcer whose root is FIXTURE;
# prints its output followed by a final line RC=<exit status>.
run_enforcer_in() {
    local fx="$1" out rc
    mkdir -p "${fx}/bin"
    cp "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" "${fx}/bin/"
    out="$(cd "${fx}" && HOME="${fx}/home" zsh bin/vde-enforce-uap.zsh 2>&1)"; rc=$?
    print -r -- "${out}"
    print -r -- "RC=${rc}"
}

test_enforcer_requires_policy() {
    test_start "4: the Sovereign Audit refuses to run when a policy file is missing or empty"
    # Behavioural: run the REAL enforcer against a scratch root (its root is the
    # directory above its own bin/), so the existence loop itself is exercised.
    local tmp fx out f
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/vde-secplan.XXXXXX")" || { test_fail "scratch dir" "mktemp failed"; return; }
    local -a base=(AGENTS.md GEMINI.md .gemini/STATE/MEMORY.md "${POLICY}" "${RULE}" "${PROCESS}" "${INDEX}" "${PREAMBLE}")
    for f in "${POLICY}" "${RULE}" "${PROCESS}" "${INDEX}" "${PREAMBLE}"; do
        # Fixture A: every mandatory file present and non-empty except F, which is deleted.
        fx="${tmp}/missing-${f:t:r}"
        mkdir -p "${fx}"
        local g; for g in "${base[@]}"; do mkdir -p "${fx}/${g:h}"; print -r -- "x" > "${fx}/${g}"; done
        rm -f -- "${fx}/${f}"
        out="$(run_enforcer_in "${fx}")"
        [[ "${out}" == *"Mandatory file missing or empty: ${f}"* && "${out}" != *"RC=0" ]] \
            && test_pass "a deleted ${f} fails the audit" \
            || test_fail "a deleted ${f} fails the audit" "output: ${${out//$'\n'/ | }[1,240]}"
        # Fixture B: F present but EMPTY (a bad merge or truncation).
        fx="${tmp}/empty-${f:t:r}"
        mkdir -p "${fx}"
        for g in "${base[@]}"; do mkdir -p "${fx}/${g:h}"; print -r -- "x" > "${fx}/${g}"; done
        : > "${fx}/${f}"
        out="$(run_enforcer_in "${fx}")"
        [[ "${out}" == *"Mandatory file missing or empty: ${f}"* && "${out}" != *"RC=0" ]] \
            && test_pass "an empty ${f} fails the audit" \
            || test_fail "an empty ${f} fails the audit" "output: ${${out//$'\n'/ | }[1,240]}"
        # Fixture C: F replaced by a NON-EMPTY DIRECTORY (-s alone accepts one).
        fx="${tmp}/dir-${f:t:r}"
        mkdir -p "${fx}"
        for g in "${base[@]}"; do mkdir -p "${fx}/${g:h}"; print -r -- "x" > "${fx}/${g}"; done
        rm -f -- "${fx}/${f}"; mkdir -p "${fx}/${f}"; print -r -- "x" > "${fx}/${f}/inner"
        out="$(run_enforcer_in "${fx}")"
        [[ "${out}" == *"Mandatory file missing or empty: ${f}"* && "${out}" != *"RC=0" ]] \
            && test_pass "a directory in place of ${f} fails the audit" \
            || test_fail "a directory in place of ${f} fails the audit" "output: ${${out//$'\n'/ | }[1,240]}"
    done
    # Control: with every file present and non-empty, the mandatory check reports nothing
    # (other checks may still fail in a bare fixture; only this check is judged).
    fx="${tmp}/complete"
    mkdir -p "${fx}"
    for f in "${base[@]}"; do mkdir -p "${fx}/${f:h}"; print -r -- "x" > "${fx}/${f}"; done
    out="$(run_enforcer_in "${fx}")"
    [[ "${out}" != *"Mandatory file missing"* ]] \
        && test_pass "a complete fixture raises no mandatory-file error (the check can pass)" \
        || test_fail "a complete fixture raises no mandatory-file error" "output: ${${out//$'\n'/ | }[1,240]}"
    [[ "${tmp}" == "${TMPDIR:-/tmp}"/vde-secplan.* ]] && rm -rf -- "${tmp}"
}

test_public_policy() {
    test_start "5: SECURITY.md is the public policy and links the process"
    expect_has "links private reporting" "${POLICY}" 'https://github.com/dderyldowney/vde-system/security/advisories/new'
    expect_has "links the process document" "${POLICY}" "${PROCESS}"
    expect_has "links the advisory index" "${POLICY}" "${INDEX}"
    expect_has "states the 90-day disclosure limit" "${POLICY}" 'no later than 90 days after the report'
    expect_has "states the acknowledgement target" "${POLICY}" '3 business days'
    expect_has "has a safe-harbor section" "${POLICY}" '## Safe Harbor'
    expect_has "states the threat model" "${POLICY}" '## Scope and Threat Model'
    # The old targets promised a patch in 48 hours, which one maintainer cannot keep.
    has "${POLICY}" '| 48 hours |' && test_fail "drops the unkeepable 48-hour patch target" "still present" \
        || test_pass "drops the unkeepable 48-hour patch target"
}

test_process_lifecycle() {
    test_start "6: the process covers the whole lifecycle in order"
    local -a sections=('## 1. Intake' '## 2. Triage' '## 3. Tracking' '## 4. Fix'
        '## 5. Patch Release' '## 6. Disclosure' '## 7. Alerts' '## 8. Prevention')
    local s prev=0 ln
    for s in "${sections[@]}"; do
        ln="$(grep -nF -m1 -- "${s}" "${VDE_ROOT_DIR}/${PROCESS}" 2>/dev/null)"; ln="${ln%%:*}"
        if [[ -n "${ln}" ]] && (( ln > prev )); then
            test_pass "has [${s}] in order"; prev=${ln}
        else
            test_fail "has [${s}] in order" "missing or out of order (line [${ln}], previous ${prev})"
        fi
    done
    expect_has "scores with CVSS v4.0" "${PROCESS}" 'CVSS v4.0'
    expect_has "classifies with CWE" "${PROCESS}" 'CWE'
    expect_has "uses the advisory's temporary private fork" "${PROCESS}" 'temporary private fork'
    expect_has "says how the Strike Protocol runs in a private fork" "${PROCESS}" '**The Strike Protocol in a private fork.**'
    expect_has "fixes merge to public branches only in the release-day sequence" "${PROCESS}" '**Release-day sequence for a private fork.**'
    expect_has "a combined gate precedes the release chain" "${PROCESS}" '**Combined gate before the release chain.**'
    expect_has "the combined gate names the full Sovereign suite" "${PROCESS}" 'tests/run-sovereign-tests.zsh'
    expect_has "the combined gate names the Spoke smoke matrix" "${PROCESS}" 'tests/integration/spoke-smoke-matrix.test.zsh'
    expect_has "the combined gate stops the sequence on a failure" "${PROCESS}" 'nothing is rolled to `stable` until the gate is green'
    expect_has "the combined gate runs on a local candidate tree that is never pushed" "${PROCESS}" 'which is never pushed'
    expect_has "the merge order comes from a release plan the User approves before release day" "${PROCESS}" 'a list of the fork pull requests in merge order, with any shared commits noted, that the User approves before release day'
    expect_has "a Vulnerability failure is fixed in the private fork, not on public develop" "${PROCESS}" 'is fixed in that advisory'"'"'s temporary private fork'
    expect_has "each fork merge is approved after the gate, naming the tested head sha" "${PROCESS}" 'names the head sha the gate tested'
    expect_has "each promotion pull request needs its own written approval" "${PROCESS}" 'needs its own written approval, as does the roll from `stable` to `main`'
    # The gate's two named tests must exist, or the gate cannot run as written.
    local gate_file
    for gate_file in tests/run-sovereign-tests.zsh tests/integration/spoke-smoke-matrix.test.zsh; do
        if tracked "${gate_file}"; then test_pass "the combined gate's ${gate_file} is tracked"; else test_fail "the combined gate's ${gate_file}" "is not tracked or is empty"; fi
    done
    expect_has "reserves each item number in the private ledger first" "${PROCESS}" '**Reserve the item number first.**'
    expect_has "checks for a duplicate before drafting an advisory" "${PROCESS}" '**Check for a duplicate first.**'
    expect_has "closes the draft advisory on Hardening or Not an issue" "${PROCESS}" '**Close the draft on Hardening or Not an issue.**'
    expect_has "records a finding in the private ledger without being asked" "${PROCESS}" 'without waiting to be asked'
    expect_has "names the one early-disclosure exception" "${PROCESS}" '**Early disclosure.**'
}

test_agent_rule() {
    test_start "7: the agent rule states the non-negotiables"
    expect_has "never put weakness detail in public text" "${RULE}" 'NEVER put weakness detail in public text'
    expect_has "draft advisory first" "${RULE}" 'draft GitHub Security Advisory'
    expect_has "agents never publish" "${RULE}" 'Agents NEVER publish'
    expect_has "every Vulnerability is fixed privately" "${RULE}" 'Every Vulnerability (any severity) is fixed in the advisory'
    expect_has "CLAUDE.md routes Vulnerability fixes to the private fork" CLAUDE.md "advisory's temporary private fork"
    expect_has "follows the process document" "${RULE}" "${PROCESS}"
    expect_has "early disclosure is the User's decision" "${RULE}" "**Early disclosure is the User's decision.**"
    expect_has "findings are recorded in the ledger without being asked" "${RULE}" 'without waiting to be asked'
    expect_has "the fork merges only in the release-day sequence" "${RULE}" 'release-day sequence'
    # Standing order (the User, 2026-11-22): public disclosure by any bot or person is preserved privately, then deleted.
    expect_has "standing order: remove public text that discloses a weakness" "${RULE}" '**Remove any public text that discloses a weakness we are fixing.**'
    expect_has "the process document carries the same standing order" "${PROCESS}" '**Remove any public text that discloses a weakness we are fixing.**'
    expect_has "the public policy says fixes reach public branches only with the release" "${POLICY}" 'only as part of that patch release'
}

test_issue_chooser() {
    test_start "8: the issue chooser sends reporters to private reporting"
    expect_has "config.yml links private reporting" .github/ISSUE_TEMPLATE/config.yml \
        'https://github.com/dderyldowney/vde-system/security/advisories/new'
    # A public blank issue is the wrong place for a security report: templates only.
    expect_has "config.yml disables blank issues" .github/ISSUE_TEMPLATE/config.yml 'blank_issues_enabled: false'
}

test_agent_reach() {
    test_start "9: every agent, however it is activated, is bound by the stance and the preamble"
    local preamble='.gemini/RULES/security-preamble.md' s f
    tracked "${preamble}" && test_pass "${preamble} is tracked" || test_fail "${preamble} is tracked" "not tracked"
    expect_has "preamble acts only when the User approves" "${preamble}" 'only when the User approves'
    expect_has "preamble tells the User what it finds" "${preamble}" 'tell the User'
    has "${preamble}" 'then file a neutral issue' && test_fail "the preamble no longer tells an agent to file an issue on its own" "still present" \
        || test_pass "the preamble no longer tells an agent to file an issue on its own"
    for s in 'NO AID TO THE ENEMY' 'fix/sec-item-NN' 'keep it private' 'outside the repository' "${RULE}"; do
        expect_has "preamble contains [${s}]" "${preamble}" "${s}"
    done
    for s in 'NO AID TO THE ENEMY' 'When unsure whether something is safe to publish, keep it private.' \
        'Every security-item branch is named' 'fix/sec-item-NN' 'Every sub-agent prompt begins with the security preamble'; do
        expect_has "${RULE} contains [${s}]" "${RULE}" "${s}"
    done
    for f in CLAUDE.md AGENTS.md .gemini/instructions.md; do
        expect_has "${f} contains security-preamble.md" "${f}" 'security-preamble.md'
        expect_has "${f} contains NO AID TO THE ENEMY" "${f}" 'NO AID TO THE ENEMY'
    done
    local -a skills commands
    skills=("${VDE_ROOT_DIR}"/.gemini/SKILLS/*.md(N))
    commands=("${VDE_ROOT_DIR}"/.gemini/COMMANDS/*.md(N))
    (( ${#skills[@]} >= 11 )) && test_pass "at least 11 skill files were found (${#skills[@]})" \
        || test_fail "at least 11 skill files were found" "found ${#skills[@]}"
    (( ${#commands[@]} >= 8 )) && test_pass "at least 8 command files were found (${#commands[@]})" \
        || test_fail "at least 8 command files were found" "found ${#commands[@]}"
    for f in "${skills[@]}"; do
        expect_has "skill ${f:t} binds the security preamble" ".gemini/SKILLS/${f:t}" '.gemini/RULES/security-preamble.md'
    done
    for f in "${commands[@]}"; do
        expect_has "command ${f:t} binds the security preamble" ".gemini/COMMANDS/${f:t}" '.gemini/RULES/security-preamble.md'
    done
    expect_has "the security process names the fix/sec-item-NN branch for every security item" "${PROCESS}" \
        'Every security item, Hardening or Vulnerability, uses the branch name'
    expect_has "the security process names the fix/sec-item-NN branch pattern" "${PROCESS}" 'fix/sec-item-NN'
}

test_files_tracked
test_reading_locations
test_startup_binding
test_enforcer_requires_policy
test_public_policy
test_process_lifecycle
test_agent_rule
test_issue_chooser
test_agent_reach

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
