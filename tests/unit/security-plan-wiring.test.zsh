#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

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

tracked() { git -C "${VDE_ROOT_DIR}" ls-files --error-unmatch -- "$1" >/dev/null 2>&1; }
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
    local -a base=(AGENTS.md GEMINI.md .gemini/STATE/MEMORY.md "${POLICY}" "${RULE}" "${PROCESS}")
    for f in "${POLICY}" "${RULE}" "${PROCESS}"; do
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
}

test_agent_rule() {
    test_start "7: the agent rule states the non-negotiables"
    expect_has "never put weakness detail in public text" "${RULE}" 'NEVER put weakness detail in public text'
    expect_has "draft advisory first" "${RULE}" 'draft GitHub Security Advisory'
    expect_has "agents never publish" "${RULE}" 'Agents NEVER publish'
    expect_has "every Vulnerability is fixed privately" "${RULE}" 'Every Vulnerability (any severity) is fixed in the advisory'
    expect_has "CLAUDE.md routes Vulnerability fixes to the private fork" CLAUDE.md "advisory's temporary private fork"
    expect_has "follows the process document" "${RULE}" "${PROCESS}"
}

test_issue_chooser() {
    test_start "8: the issue chooser sends reporters to private reporting"
    expect_has "config.yml links private reporting" .github/ISSUE_TEMPLATE/config.yml \
        'https://github.com/dderyldowney/vde-system/security/advisories/new'
}

test_files_tracked
test_reading_locations
test_startup_binding
test_enforcer_requires_policy
test_public_policy
test_process_lifecycle
test_agent_rule
test_issue_chooser

echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
