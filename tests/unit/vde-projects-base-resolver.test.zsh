#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests for the shared Projects-base resolver (Signet #564, hardening of #545).
#
# vde_resolve_projects_base (lib/vde-path-utils) is the ONE place a student-typed
# or configured Projects base is validated and absolutized. It must:
#   - expand a leading ~ and $NAME / ${NAME} -- and nothing else (no ${(e)}, so a
#     variable whose VALUE contains $(...) can never execute),
#   - refuse empty values, ':' (corrupts the short-form Compose mount
#     "<base>/<vm>:/home/devuser/workspace") and any command/process/arithmetic
#     substitution syntax,
#   - absolutize relative values.
# vde_projects_dir() returns the resolved value so mkdir and Compose agree.
#
# Hermetic: sandboxes under mktemp; the repo's own .env is never read or written.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
typeset -r REPO_ROOT="${VDE_ROOT_DIR}"

source "${REPO_ROOT}/lib/vde-shell-compat" &>/dev/null
source "${REPO_ROOT}/lib/vde-constants"    &>/dev/null
source "${REPO_ROOT}/lib/vde-path-utils"   &>/dev/null

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
assert_eq() {  # <label> <expected> <actual>
    if [[ "$3" == "$2" ]]; then test_pass "$1"; else test_fail "$1" "expected '$2', got '$3'"; fi
}

typeset SANDBOX
SANDBOX="$(mktemp -d /tmp/vde-base-resolver.XXXXXX)"
trap '[[ "${SANDBOX}" == /tmp/vde-base-resolver.* ]] && rm -rf -- "${SANDBOX}"' EXIT INT TERM

# resolve <raw> [reldir]  -> sets RES_RC, RES (result or error text)
resolve() {
    vde_resolve_projects_base "$@"
    RES_RC=$?
    RES="${VDE_PB_RESULT}"
    [[ ${RES_RC} -ne 0 ]] && RES="${VDE_PB_ERROR}"
}

# ---------------------------------------------------------------------------
# Accepted forms
# ---------------------------------------------------------------------------
test_accepts_absolute() {
    test_start "absolute path resolves to itself"
    resolve "${SANDBOX}/base"
    assert_eq "rc 0"    "0"                "${RES_RC}"
    assert_eq "result"  "${SANDBOX}/base"  "${RES}"
}

test_expands_tilde() {
    test_start "leading ~ expands to HOME"
    local h="${SANDBOX}/home"; mkdir -p "${h}"
    HOME="${h}" resolve '~/Projects'
    assert_eq "rc 0"   "0"                  "${RES_RC}"
    assert_eq "result" "${h}/Projects"      "${RES}"
}

test_expands_plain_and_braced_vars() {
    test_start "\$NAME and \${NAME} expand"
    typeset -x VDE_T_BASE="${SANDBOX}/viavar"
    resolve '$VDE_T_BASE/a'
    assert_eq "plain var"  "${SANDBOX}/viavar/a" "${RES}"
    resolve '${VDE_T_BASE}/b'
    assert_eq "braced var" "${SANDBOX}/viavar/b" "${RES}"
    unset VDE_T_BASE
}

test_relative_is_absolutized() {
    test_start "relative path is absolutized (against reldir, default PWD)"
    resolve "rel/base" "${SANDBOX}/anchor"
    assert_eq "against reldir" "${SANDBOX}/anchor/rel/base" "${RES}"
    ( cd "${SANDBOX}" && vde_resolve_projects_base "here/x" && print -r -- "${VDE_PB_RESULT}" ) > "${SANDBOX}/pwdout"
    assert_eq "default is PWD" "${SANDBOX:A}/here/x" "$(<"${SANDBOX}/pwdout")"
}

test_normalizes() {
    test_start "dots and double slashes are normalized"
    resolve "${SANDBOX}//a/./b/../c/"
    assert_eq "normalized" "${SANDBOX}/a/c" "${RES}"
}

# ---------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------
test_refuses_empty() {
    test_start "empty value is refused"
    resolve ""
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
}

test_refuses_colon() {
    test_start "':' in the base is refused (breaks short-form Compose mount)"
    resolve "${SANDBOX}/a:b"
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
    [[ "${RES}" == *':'* ]] && test_pass "error mentions the colon" || test_fail "error mentions the colon" "got '${RES}'"
}

test_refuses_substitution_forms() {
    test_start "command/process/arithmetic substitution forms are refused and never run"
    local marker="${SANDBOX}/INJECTED" raw
    local -a payloads=(
        '$(touch '"${marker}"')'
        '`touch '"${marker}"'`'
        '$[1+1]'
        '<(touch '"${marker}"')'
        '>(touch '"${marker}"')'
        '=(touch '"${marker}"')'
        '${(e)x}'
        '${(e):-$(touch '"${marker}"')}'
    )
    for raw in "${payloads[@]}"; do
        resolve "${raw}"
        assert_eq "refused: ${raw}" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
    done
    [[ ! -e "${marker}" ]] && test_pass "no payload executed" || test_fail "no payload executed" "marker exists"
}

test_variable_value_never_executes() {
    test_start "a variable whose VALUE contains \$(...) is refused, not executed (#545 item 2)"
    local marker="${SANDBOX}/INJECTED_VIA_VAR"
    typeset -x VDE_T_EVIL='$(touch '"${marker}"')'
    resolve '$VDE_T_EVIL/x'
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
    [[ ! -e "${marker}" ]] && test_pass "payload not executed" || test_fail "payload not executed" "marker exists"
    unset VDE_T_EVIL
}

test_value_is_not_reexpanded() {
    test_start "expanded values are not re-scanned (\$A -> '\$B' stays literal and is refused)"
    typeset -x VDE_T_A='$VDE_T_B' VDE_T_B="${SANDBOX}/nope"
    resolve '$VDE_T_A'
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
    unset VDE_T_A VDE_T_B
}

test_refuses_tilde_user() {
    test_start "~user is refused (not silently treated as a relative path)"
    resolve '~bob/Projects'
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
}

test_refuses_unset_variable() {
    test_start "reference to an unset variable is refused"
    unset VDE_T_UNSET
    resolve '$VDE_T_UNSET/x'
    assert_eq "rc is VDE_ERR_INVALID_INPUT" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
}

test_refuses_unsupported_expansion() {
    test_start "unsupported \$-forms (\${X:-d}, \$\$, \$1) are refused"
    local raw
    for raw in '${HOME:-/x}' '$$' '$1'; do
        resolve "${raw}"
        assert_eq "refused: ${raw}" "${VDE_ERR_INVALID_INPUT}" "${RES_RC}"
    done
}

# ---------------------------------------------------------------------------
# vde_projects_dir returns the RESOLVED value (#545 comment, finding 2)
# ---------------------------------------------------------------------------
_forge() {  # $1 = .env content line (optional) ; echoes forge root
    local f; f="$(mktemp -d "${SANDBOX}/forge.XXXXXX")"
    [[ -n "$1" ]] && print -r -- "$1" > "${f}/.env"
    print -r -- "${f}"
}
_projects_dir_in() {  # $1=forge ; env var VAL (optional) -> stdout/stderr of vde_projects_dir
    ( unset VDE_PROJECTS_DIR; [[ -n "${VAL:-}" ]] && VDE_PROJECTS_DIR="${VAL}"
      VDE_ROOT_DIR="$1"; vde_projects_dir )
}

test_projects_dir_expands_tilde_from_env() {
    test_start "vde_projects_dir expands a ~ in VDE_PROJECTS_DIR"
    local f; f="$(_forge)"; local h="${SANDBOX}/home2"; mkdir -p "${h}"
    local got; got="$(HOME="${h}" VAL='~/Projects' _projects_dir_in "${f}")"
    assert_eq "tilde resolved" "${h}/Projects" "${got}"
}

test_projects_dir_expands_tilde_from_dotenv() {
    test_start "vde_projects_dir expands a hand-edited ~ in .env"
    local f; f="$(_forge 'VDE_PROJECTS_DIR=~/FromEnv')"; local h="${SANDBOX}/home3"; mkdir -p "${h}"
    local got; got="$(HOME="${h}" _projects_dir_in "${f}")"
    assert_eq "tilde resolved" "${h}/FromEnv" "${got}"
}

test_projects_dir_relative_is_rooted_at_vde() {
    test_start "vde_projects_dir anchors a relative .env value at VDE_ROOT_DIR"
    local f; f="$(_forge 'VDE_PROJECTS_DIR=rel/base')"
    local got; got="$(_projects_dir_in "${f}")"
    assert_eq "rooted at forge" "${f:A}/rel/base" "${got}"
}

test_projects_dir_invalid_falls_back_loudly() {
    test_start "vde_projects_dir falls back to the in-tree default, with a warning, on an invalid stored value"
    local f; f="$(_forge 'VDE_PROJECTS_DIR=/mnt/a:b')"
    local out err
    out="$(_projects_dir_in "${f}" 2>"${SANDBOX}/err")"; err="$(<"${SANDBOX}/err")"
    assert_eq "default returned" "${f}/projects" "${out}"
    [[ -n "${err}" ]] && test_pass "warning emitted on stderr" || test_fail "warning emitted on stderr" "stderr empty"
}

test_path_is_within() {
    test_start "vde_path_is_within: equal or nested => true; sibling/prefix-lookalike/outside => false (#565)"
    local r="${SANDBOX}/vde"; mkdir -p "${r}/projects" "${SANDBOX}/vde-other"
    vde_path_is_within "${r}" "${r}";                   assert_eq "equal"              "0" "$?"
    vde_path_is_within "${r}/projects/x" "${r}";        assert_eq "nested"             "0" "$?"
    vde_path_is_within "${r}/../vde/./y" "${r}";        assert_eq "dot-dot normalized" "0" "$?"
    vde_path_is_within "${SANDBOX}/vde-other" "${r}";   assert_eq "prefix lookalike"   "1" "$?"
    vde_path_is_within "${SANDBOX}/elsewhere" "${r}";   assert_eq "outside"            "1" "$?"
    ln -s "${r}" "${SANDBOX}/link"
    vde_path_is_within "${SANDBOX}/link/z" "${r}";      assert_eq "symlink into root"  "0" "$?"
}

test_accepts_absolute
test_path_is_within
test_expands_tilde
test_expands_plain_and_braced_vars
test_relative_is_absolutized
test_normalizes
test_refuses_empty
test_refuses_colon
test_refuses_substitution_forms
test_variable_value_never_executes
test_value_is_not_reexpanded
test_refuses_tilde_user
test_refuses_unset_variable
test_refuses_unsupported_expansion
test_projects_dir_expands_tilde_from_env
test_projects_dir_expands_tilde_from_dotenv
test_projects_dir_relative_is_rooted_at_vde
test_projects_dir_invalid_falls_back_loudly

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
