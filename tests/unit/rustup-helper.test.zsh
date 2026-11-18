#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: shared rustup helper, bounded downloads and installer timeout
# (Signet #598, #600, #607, #611).
#
# vde_install_rustup lives once in lib/vde-core; rust-init and embed-init call
# it, and the rustup-init and probe-rs downloads carry VDE_CURL_BOUNDS. The
# rustup-init binary is verified against its published .sha256 and runs under
# timeout VDE_INSTALLER_TIMEOUT. Stubs stand in for sudo, curl and timeout;
# nothing touches the network or the host toolchain.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset stub
stub="$(mktemp -d)" || exit 1
trap 'rm -rf "${stub}"' EXIT
# sudo stub drops "-H -u USER" and runs the command as the current user.
printf '#!/usr/bin/env zsh\nshift 3\nexec "$@"\n' > "${stub}/sudo"
# curl stub appends each call to CURL_LOG as a ---CALL--- marker line followed by
# its arguments, one per line, so every fetch can be checked on its own. For a
# -o target ending in .sha256 it writes the real sha256 of the stub installer (or
# SHA_OVERRIDE when set); any other -o target gets the no-op installer.
cat > "${stub}/curl" <<'STUB'
#!/usr/bin/env zsh
printf '%s\n' '---CALL---' "$@" >> "${CURL_LOG}"
o=; while (( $# )); do [[ $1 == -o ]] && o=$2; shift; done
body='#!/usr/bin/env zsh
print -r -- "${0:t}" > "${CURL_LOG}.ran"'
if [[ "${o}" == *.sha256 ]]; then
    hash="$(print -r -- "${body}" | sha256sum)"; hash="${hash%% *}"
    print -r -- "${SHA_OVERRIDE:-${hash}}  rustup-init" > "${o}"
else
    print -r -- "${body}" > "${o}"
fi
STUB
chmod +x "${stub}/sudo" "${stub}/curl"
# Hermetic PATH: the stub dir plus links to the few tools the helper runs, so a
# host rustc in /usr/bin can never change what these tests exercise. timeout is
# linked for real here; the timeout test replaces the link with a recording stub.
typeset t
for t in zsh env uname mktemp chmod rm sha256sum timeout; do ln -s "$(command -v ${t})" "${stub}/${t}"; done
typeset -x CURL_LOG="${stub}/curl.log"

test_start "VDE_CURL_BOUNDS caps connect time, total time and retries"
source lib/vde-core
typeset b="${VDE_CURL_BOUNDS[*]}"
typeset -a want=(--connect-timeout 30 --max-time 600 --retry 3 --retry-delay 2)
# The curl stub logs one argument per line, so a bound passed as a single
# combined argument cannot match this newline-joined expectation.
typeset want_lines="${(F)want}"
if [[ "${VDE_CURL_BOUNDS[*]}" == "${want[*]}" ]]; then
    test_pass "${b}"
else test_fail "VDE_CURL_BOUNDS" "got '${b}', want '${want[*]}'"; fi

test_start "VDE_INSTALLER_TIMEOUT is a positive integer of seconds"
if [[ "${VDE_INSTALLER_TIMEOUT}" =~ '^[1-9][0-9]*$' ]]; then
    test_pass "VDE_INSTALLER_TIMEOUT=${VDE_INSTALLER_TIMEOUT}"
else test_fail "VDE_INSTALLER_TIMEOUT" "got '${VDE_INSTALLER_TIMEOUT}'"; fi

test_start "vde_install_rustup downloads the native binary and its .sha256 with the bounds"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
typeset rc=$?
# Split the log on the ---CALL--- marker: each part is one curl invocation. A
# part's arguments are "\n"-prefixed and "\n"-terminated, so a contiguous
# newline-delimited match of the bounds block proves every bound is an argument.
typeset -a calls=( ${(s:---CALL---:)"$(<"${CURL_LOG}")"} )
typeset call bin_ok=0 sha_ok=0 bounded_bin=0 bounded_sha=0
for call in "${calls[@]}"; do
    [[ "${call}" == *"/rustup/dist/"* ]] || continue
    if [[ "${call}" == *"/rustup-init.sha256"$'\n'* ]]; then
        sha_ok=1
        [[ "${call}" == *$'\n'"${want_lines}"$'\n'* ]] && bounded_sha=1
    elif [[ "${call}" == *"/rustup-init"$'\n'* ]]; then
        bin_ok=1
        [[ "${call}" == *$'\n'"${want_lines}"$'\n'* ]] && bounded_bin=1
    fi
done
if (( rc != 0 )); then test_fail "helper status" "vde_install_rustup returned ${rc}"
elif (( bin_ok && sha_ok && bounded_bin && bounded_sha )); then
    test_pass "binary and .sha256 curl calls each got ${want[*]} as separate arguments"
else test_fail "curl args" "want each of the binary and .sha256 calls to carry '${want[*]}' (bin ${bin_ok}/${bounded_bin}, sha ${sha_ok}/${bounded_sha}), log: '${(j: | :)${(f)$(<"${CURL_LOG}")}}'"; fi

test_start "installer keeps the name rustup-init (multi-call dispatch)"
typeset ran="$(<"${CURL_LOG}.ran" 2>/dev/null)"
if [[ "${ran}" == "rustup-init" ]]; then test_pass "installer ran as rustup-init"
else test_fail "installer name" "ran as '${ran}'"; fi

test_start "a sha256 mismatch fails the install and the installer never runs"
rm -f "${CURL_LOG}" "${CURL_LOG}.ran"
typeset -x SHA_OVERRIDE=0000000000000000000000000000000000000000000000000000000000000000
typeset err
err="$(PATH="${stub}" vde_install_rustup nobody VDE-T 2>&1 >/dev/null)"
rc=$?
unset SHA_OVERRIDE
if (( rc == 0 )); then test_fail "mismatch status" "vde_install_rustup returned 0"
elif [[ -e "${CURL_LOG}.ran" ]]; then test_fail "mismatch" "installer ran despite bad sha256"
elif [[ "${err}" != *"sha256 mismatch"* ]]; then test_fail "mismatch message" "got '${err}'"
else test_pass "returned ${rc}, reported the mismatch, installer not run"; fi

test_start "installer runs as the command timeout executes, under -k 30 VDE_INSTALLER_TIMEOUT"
rm -f "${stub}/timeout" "${CURL_LOG}.timeout" "${CURL_LOG}.ran"
# Replace the timeout link first: writing through it would clobber /usr/bin/timeout.
# The stub records every argument, one per line, then drops timeout's own
# "-k 30 LIMIT" and execs the remaining command, so the installer really runs.
printf '#!/usr/bin/env zsh\nprint -rl -- "$@" > "${CURL_LOG}.timeout"\nshift 3\nexec "$@"\n' > "${stub}/timeout"
chmod +x "${stub}/timeout"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
rc=$?
typeset targs_raw="$(<"${CURL_LOG}.timeout" 2>/dev/null)"
typeset -a targs=( ${(f)targs_raw} )
if (( rc != 0 )); then test_fail "timeout status" "vde_install_rustup returned ${rc}"
elif (( ${#targs} >= 4 )) && [[ "${targs[1]}" == -k && "${targs[2]}" == 30 \
     && "${targs[3]}" == "${VDE_INSTALLER_TIMEOUT}" && "${targs[4]:t}" == rustup-init && -e "${CURL_LOG}.ran" ]]; then
    test_pass "timeout got -k 30 ${targs[3]}, then ran ${targs[4]:t} (installer executed)"
else test_fail "installer timeout" "timeout got '${(j: :)targs}', want '-k 30 ${VDE_INSTALLER_TIMEOUT} .../rustup-init' and an executed installer"; fi

test_start "vde_install_rustup skips the download when rustc exists"
rm -f "${CURL_LOG}"
printf '#!/usr/bin/env zsh\nexit 0\n' > "${stub}/rustc"; chmod +x "${stub}/rustc"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
rc=$?
if (( rc != 0 )); then test_fail "skip status" "vde_install_rustup returned ${rc}"
elif [[ ! -e "${CURL_LOG}" ]]; then test_pass "no curl call, status 0"
else test_fail "idempotency" "curl ran"; fi

# Wiring pins read executable lines only: a comment that still spells out a
# safeguard must not satisfy a pin (Signet #611). Full-line comments and trailing
# " #..." comments are dropped (a "#" inside a word, as in "${#x}", is kept).
# code_n keeps the original line numbers for ordering checks.
code_of() { grep -vE '^[[:space:]]*#' "$1" | sed -E 's/[[:space:]]+#.*$//'; }
code_n()  { grep -nvE '^[[:space:]]*#' "$1" | sed -E 's/[[:space:]]+#.*$//'; }

typeset e=scripts/setup/embed-init.zsh
typeset k=scripts/setup/kotlin-init.zsh
typeset cs_file=scripts/setup/csharp-init.zsh
typeset re_probe='timeout -k 30 "[$][{][A-Za-z_]+[}]" sh "[$][{]_installer[}]"'
typeset re_sdkman='timeout -k 30 "[$][{][A-Za-z_]+[}]" (sudo -H -u [a-z]+ )?bash "[$][{]_sdkman_installer[}]"'
typeset re_cs_timeout='timeout -k 30 "[$][{]VDE_INSTALLER_TIMEOUT[}]" bash /tmp/dotnet-install[.]sh'

# Each pin prints one reason per broken safeguard on $1 and nothing when wired.
pin_probe_bounds() {
    local c; c="$(code_of "$1")"
    print -r -- "${c}" | grep -qF 'probe-rs-tools-installer.sh' \
      && print -r -- "${c}" | grep -B1 -F 'probe-rs-tools-installer.sh' | grep -qF -- '-sSfL "$@"' \
      && print -r -- "${c}" | grep -qF "' _ \"\${VDE_INSTALLER_TIMEOUT}\" \"\${VDE_CURL_BOUNDS[@]}\"" \
      || print -r -- "probe-rs bounds not wired end to end"
}
pin_timeout_embed() {
    [[ "$(code_of "$1")" =~ $re_probe ]] || print -r -- "probe-rs installer not wrapped by timeout -k 30"
}
pin_timeout_kotlin() {
    [[ "$(code_of "$1")" =~ $re_sdkman ]] || print -r -- "SDKMAN installer not wrapped by timeout -k 30"
}
pin_csharp() {
    local f="$1" c n_src n_use
    local -a curl_l
    c="$(code_of "${f}")"
    curl_l=( ${(M)${(f)c}:#*dot.net/v1/dotnet-install.sh*} )
    if (( ${#curl_l} != 1 )) || [[ "${curl_l[1]}" != *'"${VDE_CURL_BOUNDS[@]}"'* ]]; then
        print -r -- 'dotnet download line lacks "${VDE_CURL_BOUNDS[@]}"'
    fi
    [[ "${c}" =~ $re_cs_timeout ]] || print -r -- 'dotnet installer not run under timeout -k 30 "${VDE_INSTALLER_TIMEOUT}"'
    n_src="$(code_n "${f}" | grep -m1 -E '^[0-9]+:[[:space:]]*(source|[.]) .*lib/vde-core"?([[:space:]]|$)' | cut -d: -f1)"
    n_use="$(code_n "${f}" | grep -m1 'VDE_CURL_BOUNDS' | cut -d: -f1)"
    (( n_src && n_use && n_src < n_use )) \
      || print -r -- "lib/vde-core (line ${n_src:-none}) not sourced before first VDE_CURL_BOUNDS (line ${n_use:-none})"
}

test_start "rust and embed Spokes call the shared helper, not an inline copy"
typeset s ok=1
for s in scripts/setup/rust-init.zsh scripts/setup/embed-init.zsh; do
    code_of "${s}" | grep -q '^vde_install_rustup devuser ' || { ok=0; test_fail "${s}" "missing helper call"; }
    code_of "${s}" | grep -q 'rustup/dist' && { ok=0; test_fail "${s}" "inline rustup download remains"; }
done
(( ok )) && test_pass "both Spokes use vde_install_rustup"

test_start "probe-rs download is bounded"
typeset why
why="$(pin_probe_bounds "${e}")"
if [[ -z "${why}" ]]; then
    test_pass "curl takes \"\$@\" and the block passes the timeout and VDE_CURL_BOUNDS"
else test_fail "probe-rs curl" "${why}"; fi

test_start "probe-rs and SDKMAN installers are directly preceded by timeout -k 30 \"\${...}\""
why="$(pin_timeout_embed "${e}")$(pin_timeout_kotlin "${k}")"
if [[ -z "${why}" ]]; then
    test_pass "embed-init runs sh under timeout -k 30; kotlin-init runs SDKMAN under timeout -k 30"
else test_fail "installer timeout wiring" "${why}"; fi

test_start "csharp-init bounds the dotnet download and runs the installer under timeout -k 30, vde-core sourced first"
why="$(pin_csharp "${cs_file}")"
if [[ -z "${why}" ]]; then
    test_pass "csharp-init bounds the dotnet download and runs the installer under timeout -k 30, vde-core sourced first"
else test_fail "csharp-init wiring" "${why}"; fi

# A pin that passes on raw text would hide a disabled safeguard. Comment out the
# line that carries each safeguard (or demote it to a trailing comment on a no-op
# line), leaving its text behind, and require the pin to notice.
test_start "pins fail when a safeguard survives only in a comment (full-line or trailing)"
typeset mut="${stub}/mut" mok=1
mkdir -p "${mut}"
mutant_caught() {   # $1 pin function, $2 script, $3 BRE address (no "|") of the line to disable
    local out="${mut}/${2:t}" sub
    for sub in 's|^\([[:space:]]*\)|\1# |' 's|^\([[:space:]]*\)\(.*\)$|\1true  # \2|' 's|^\([[:space:]]*\)\(.*\)$|\1true #\2|'; do
        sed "\\|$3| ${sub}" "$2" > "${out}"
        cmp -s "$2" "${out}" && return 1
        [[ -n "$("$1" "${out}")" ]] || return 1
    done
}
mutant_caught pin_csharp         "${cs_file}" 'devuser timeout'                || { mok=0; test_fail "csharp timeout" "commented-out timeout still passes"; }
mutant_caught pin_csharp         "${cs_file}" 'dot[.]net/v1'                   || { mok=0; test_fail "csharp curl" "commented-out download still passes"; }
mutant_caught pin_csharp         "${cs_file}" '^source .*lib/vde-core'         || { mok=0; test_fail "csharp source" "commented-out source still passes"; }
mutant_caught pin_timeout_embed  "${e}"       '^[[:space:]]*timeout -k 30'     || { mok=0; test_fail "embed timeout" "commented-out timeout still passes"; }
mutant_caught pin_probe_bounds   "${e}"       "^' _ "                          || { mok=0; test_fail "embed bounds" "commented-out bounds still pass"; }
mutant_caught pin_timeout_kotlin "${k}"       'devuser timeout -k 30'          || { mok=0; test_fail "kotlin timeout" "commented-out timeout still passes"; }
(( mok )) && test_pass "6 safeguards rejected as full-line and as trailing comments"

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
