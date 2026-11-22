#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit tests for Signet #737: the Forge creates the private security directory.
#
# lib/vde-security-dir resolves ${VDE_SECURITY_DIR:-$HOME/.vde-security} and, when it is
# missing, creates it with mode 0700; it tightens a looser mode and refuses a relative
# path, a path inside the repository, a symlink, a non-directory and a directory owned
# by someone else. It NEVER deletes or overwrites anything. Only the Sovereign Audit
# calls it (the Forge); the student (@armor) install and upgrade paths never do.
#
# Every run happens in a scratch tree with its own HOME; the real HOME is never touched.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="${0:A:h:h:h}"
fi

zmodload -F zsh/stat b:zstat

typeset -i TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; (( ++TESTS_PASSED )); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; (( ++TESTS_FAILED )); }
# check LABEL DETAIL 'ZSH-EXPRESSION': passes when the expression succeeds. The expression
# is evaluated here, so it sees the calling test's locals and the R_* result variables.
check() {
    if eval "$3"; then test_pass "$1"; else test_fail "$1" "$2"; fi
}

typeset -r PROCESS='docs/governance/security-process.md'
typeset -r RULE='.gemini/RULES/security.md'

typeset SCRATCH
SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/vde-secdir.XXXXXX")" || { echo "mktemp failed"; exit 1; }
mkdir -p "${SCRATCH}/cwd" "${SCRATCH}/home"

# run_ensure ROOT [VAR=value ...]: runs vde_security_dir_ensure ROOT in a fresh zsh whose
# environment holds only PATH and the given variables, and whose working directory is the
# scratch cwd. (zsh restores an UNSET HOME from the password database, so "no HOME" is
# tested with HOME= set empty.) Sets R_OUT (stdout), R_ERR (stderr) and R_RC.
typeset R_OUT R_ERR; typeset -i R_RC
run_ensure() {
    local root="$1"; shift
    local errf="${SCRATCH}/err.$$"
    R_OUT="$(env -i PATH="${PATH}" "$@" zsh -f -c 'cd "$3" && source "$1/lib/vde-security-dir" && vde_security_dir_ensure "$2"' _ "${VDE_ROOT_DIR}" "${root}" "${SCRATCH}/cwd" 2>"${errf}")"; R_RC=$?
    R_ERR="$(<"${errf}")"; rm -f -- "${errf}"
}
# mode_is PATH OCTAL: the permission bits of PATH are exactly OCTAL (for example 700).
mode_is() { local -A st; zstat -H st -- "$1" 2>/dev/null || return 1; (( (st[mode] & 8#777) == 8#$2 )); }
contains() { [[ "$1" == *"$2"* ]]; }
has_fixed() { grep -qF -- "$2" "${VDE_ROOT_DIR}/$1" 2>/dev/null; }
expect_has() { if has_fixed "$2" "$3"; then test_pass "$1"; else test_fail "$1" "$2 does not contain [$3]"; fi; }

typeset REPO="${SCRATCH}/repo"
mkdir -p "${REPO}/sub"

test_creates_missing() {
    test_start "1: a missing directory is created with mode 0700, parents included"
    local d="${SCRATCH}/new/nested/priv"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${d}"
    check "succeeds" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC == 0 ))'
    check "prints the resolved path" "out=[${R_OUT}]" '[[ "$R_OUT" == "$d" ]]'
    check "the directory exists" "missing" '[[ -d "$d" ]]'
    check "mode is exactly 0700" "wrong mode" 'mode_is "$d" 700'
}

test_default_path() {
    test_start "2: with no variable the default is \$HOME/.vde-security"
    local h="${SCRATCH}/home-default"; mkdir -p "${h}"
    run_ensure "${REPO}" HOME="${h}"
    check "succeeds" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC == 0 ))'
    check "prints \$HOME/.vde-security" "out=[${R_OUT}]" '[[ "$R_OUT" == "$h/.vde-security" ]]'
    check "created with mode 0700" "wrong mode" 'mode_is "$h/.vde-security" 700'
}

test_tightens_and_keeps() {
    test_start "3: a looser mode is tightened and the contents are never touched"
    local d="${SCRATCH}/loose"; mkdir -p "${d}/inner"; chmod 755 "${d}"
    print -r -- "ledger line" > "${d}/ledger.md"; print -r -- "hidden" > "${d}/.dot"; print -r -- "deep" > "${d}/inner/f"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${d}"
    check "succeeds" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC == 0 ))'
    check "mode tightened to 0700" "still loose" 'mode_is "$d" 700'
    check "ledger.md kept intact" "changed" '[[ "$(<"$d/ledger.md")" == "ledger line" ]]'
    check "the dotfile is kept" "changed" '[[ "$(<"$d/.dot")" == "hidden" ]]'
    check "the nested file is kept" "changed" '[[ "$(<"$d/inner/f")" == "deep" ]]'
    local before; before="$(print -l -- "${d}"/**/*(DN) | sort)"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${d}"
    check "a second run is a no-op" "listing changed" '[[ "$(print -l -- "$d"/**/*(DN) | sort)" == "$before" ]]'
}

test_refuses_relative() {
    test_start "4: a relative path is refused and nothing is created"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="relative/priv"
    check "fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says it must be absolute" "err=[${R_ERR}]" 'contains "$R_ERR" "must be an absolute path"'
    check "created nothing" "relative/priv appeared" '[[ ! -e "$SCRATCH/cwd/relative" ]]'
}

test_refuses_inside_repo() {
    test_start "5: a path inside the repository is refused and nothing is created"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${REPO}/sec"
    check "a new directory under the repository fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says it is inside the repository" "err=[${R_ERR}]" 'contains "$R_ERR" "is inside the repository"'
    check "it was not created" "created" '[[ ! -e "$REPO/sec" ]]'
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${REPO}"
    check "the repository root itself is refused" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC != 0 )) && contains "$R_ERR" "is inside the repository"'
    mkdir -p "${REPO}/existing"; chmod 755 "${REPO}/existing"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${REPO}/existing"
    check "an existing directory under the repository is refused" "rc=${R_RC}" '(( R_RC != 0 )) && contains "$R_ERR" "is inside the repository"'
    check "and is not chmod'ed" "mode changed" 'mode_is "$REPO/existing" 755'
    ln -s "${REPO}" "${SCRATCH}/lnk-to-repo"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${SCRATCH}/lnk-to-repo/via-link"
    check "a symlinked parent that resolves into the repository is refused" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC != 0 )) && contains "$R_ERR" "is inside the repository"'
    check "and nothing appears behind the link" "created" '[[ ! -e "$REPO/via-link" ]]'
}

test_refuses_symlink() {
    test_start "6: a symlink at the path is refused, even a dangling one"
    local real="${SCRATCH}/real-dir"; mkdir -p "${real}"; chmod 755 "${real}"
    ln -s "${real}" "${SCRATCH}/sym"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${SCRATCH}/sym"
    check "a symlink to a directory fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says it is a symlink" "err=[${R_ERR}]" 'contains "$R_ERR" "is a symlink"'
    check "the target is not chmod'ed" "mode changed" 'mode_is "$real" 755'
    ln -s "${SCRATCH}/nowhere" "${SCRATCH}/dangling"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${SCRATCH}/dangling"
    check "a dangling symlink fails" "rc=${R_RC} err=[${R_ERR}]" '(( R_RC != 0 )) && contains "$R_ERR" "is a symlink"'
    check "its target is not created" "created" '[[ ! -e "$SCRATCH/nowhere" ]]'
}

test_refuses_non_directory() {
    test_start "7: a regular file at the path is refused and left alone"
    print -r -- "precious" > "${SCRATCH}/afile"
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="${SCRATCH}/afile"
    check "fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says it is not a directory" "err=[${R_ERR}]" 'contains "$R_ERR" "exists and is not a directory"'
    check "the file is untouched" "changed" '[[ "$(<"$SCRATCH/afile")" == "precious" ]]'
}

test_refuses_foreign_owner() {
    test_start "8: a directory owned by someone else is refused"
    if [[ -O /usr ]]; then
        test_pass "skipped: this user owns /usr (running as root)"; return
    fi
    run_ensure "${REPO}" HOME="${SCRATCH}/home" VDE_SECURITY_DIR="/usr"
    check "fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says it is not owned by you" "err=[${R_ERR}]" 'contains "$R_ERR" "is not owned by you"'
}

test_refuses_without_home() {
    test_start "9: no variable and an empty HOME is refused"
    run_ensure "${REPO}" HOME=
    check "fails" "rc=${R_RC}" '(( R_RC != 0 ))'
    check "says HOME is not set" "err=[${R_ERR}]" 'contains "$R_ERR" "HOME is not set"'
}

# The Sovereign Audit calls the helper: run a copy of the REAL enforcer whose root is a
# scratch tree that holds the library too. Other checks may fail in a bare fixture; only
# the private-directory check is judged.
run_enforcer_in() {
    local fx="$1"; shift
    mkdir -p "${fx}/bin" "${fx}/lib"
    cp "${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" "${fx}/bin/"
    cp "${VDE_ROOT_DIR}/lib/vde-security-dir" "${VDE_ROOT_DIR}/lib/vde-shibboleth" "${fx}/lib/" 2>/dev/null
    (cd "${fx}" && env -i PATH="${PATH}" HOME="${fx}/home" "$@" zsh bin/vde-enforce-uap.zsh 2>&1)
}

test_audit_calls_helper() {
    test_start "10: the Sovereign Audit creates the directory and fails closed on a refusal"
    local fx="${SCRATCH}/fx-ok" d out
    mkdir -p "${fx}/home"; d="${SCRATCH}/priv-from-audit"
    out="$(run_enforcer_in "${fx}" VDE_SECURITY_DIR="${d}")"
    check "the audit created the directory" "missing" '[[ -d "$d" ]]'
    check "with mode 0700" "wrong mode" 'mode_is "$d" 700'
    check "and raised no private-directory error" "out: ${${out//$'\n'/ | }[1,200]}" '[[ "$out" != *"SECURITY-DIR"* ]]'
    local fx2="${SCRATCH}/fx-bad"
    mkdir -p "${fx2}/home"
    out="$(run_enforcer_in "${fx2}" VDE_SECURITY_DIR="${fx2}/inside")"
    check "a path inside the repository is an audit error" "out: ${${out//$'\n'/ | }[1,200]}" 'contains "$out" "[UAP-ERROR]" && contains "$out" "private security directory"'
    check "and was not created" "created" '[[ ! -e "$fx2/inside" ]]'
}

test_only_the_forge_calls_it() {
    test_start "11: only the Sovereign Audit calls the helper; no student path does"
    local found
    found="$(cd "${VDE_ROOT_DIR}" && grep -rlE 'vde[-_]security[-_]dir' bin scripts lib 2>/dev/null | grep -v '^bin/archive/' | sort | tr '\n' ' ')"
    check "bin, scripts and lib reference it only from the audit and the library itself" "found: ${found}" '[[ "$found" == "bin/vde-enforce-uap.zsh lib/vde-security-dir " ]]'
    expect_has "the audit sources the library" bin/vde-enforce-uap.zsh 'lib/vde-security-dir'
    expect_has "the audit calls vde_security_dir_ensure" bin/vde-enforce-uap.zsh 'vde_security_dir_ensure'
}

test_docs_name_path_and_variable() {
    test_start "12: the process document and the agent rule name the default path and the variable"
    expect_has "process names the variable" "${PROCESS}" 'VDE_SECURITY_DIR'
    expect_has "process names the default path" "${PROCESS}" '~/.vde-security'
    expect_has "process says the Forge creates it" "${PROCESS}" 'created by the Forge'
    expect_has "rule names the variable" "${RULE}" 'VDE_SECURITY_DIR'
    expect_has "rule names the default path" "${RULE}" '~/.vde-security'
}

test_removal_default() {
    test_start "13: removing a public disclosure is preserve-then-delete (standing order)"
    expect_has "rule 10 says remove, not only hide" "${RULE}" '**Remove any public text that discloses a weakness we are fixing.**'
    expect_has "rule 10 saves a private copy first" "${RULE}" 'save a private copy first'
    expect_has "rule 10 then deletes" "${RULE}" 'then delete'
    expect_has "the process document carries the same standing order" "${PROCESS}" '**Remove any public text that discloses a weakness we are fixing.**'
    expect_has "the process document names the private copy" "${PROCESS}" 'private copy'
}

test_creates_missing
test_default_path
test_tightens_and_keeps
test_refuses_relative
test_refuses_inside_repo
test_refuses_symlink
test_refuses_non_directory
test_refuses_foreign_owner
test_refuses_without_home
test_audit_calls_helper
test_only_the_forge_calls_it
test_docs_name_path_and_variable
test_removal_default

[[ "${SCRATCH}" == "${TMPDIR:-/tmp}"/vde-secdir.* ]] && rm -rf -- "${SCRATCH}"
echo ""
echo "Results: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
exit $(( TESTS_FAILED > 0 ? 1 : 0 ))
