#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: shared rustup helper, bounded downloads and installer timeout
# (Signet #598, #600).
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
# curl stub appends its arguments to CURL_LOG on every call. For a -o target
# ending in .sha256 it writes the real sha256 of the stub installer (or
# SHA_OVERRIDE when set); any other -o target gets the no-op installer.
cat > "${stub}/curl" <<'STUB'
#!/usr/bin/env zsh
printf '%s\n' "$@" >> "${CURL_LOG}"
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

test_start "vde_install_rustup downloads the native binary with the bounds"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
typeset rc=$?
typeset got="$(<"${CURL_LOG}")"
if (( rc != 0 )); then test_fail "helper status" "vde_install_rustup returned ${rc}"
elif [[ "${got}" == *"${want_lines}"* && "${got}" == *"static.rust-lang.org/rustup/dist/"*"/rustup-init"* \
     && "${got}" == *"rustup-init.sha256"* ]]; then
    test_pass "curl got each bound as its own argument: ${want[*]}, plus the .sha256 fetch"
else test_fail "curl args" "want separate '${want[*]}', the rustup-init URL and its .sha256, got '${(j: :)${(f)got}}'"; fi

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

test_start "installer runs under timeout with VDE_INSTALLER_TIMEOUT as its limit"
rm -f "${stub}/timeout" "${CURL_LOG}.timeout" "${CURL_LOG}.ran"
# Replace the timeout link first: writing through it would clobber /usr/bin/timeout.
printf '#!/usr/bin/env zsh\nprint -r -- "$1" > "${CURL_LOG}.timeout"\nshift\nexec "$@"\n' > "${stub}/timeout"
chmod +x "${stub}/timeout"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
rc=$?
typeset limit="$(<"${CURL_LOG}.timeout" 2>/dev/null)"
if (( rc != 0 )); then test_fail "timeout status" "vde_install_rustup returned ${rc}"
elif [[ "${limit}" == "${VDE_INSTALLER_TIMEOUT}" && -e "${CURL_LOG}.ran" ]]; then
    test_pass "timeout received ${limit}, installer ran under it"
else test_fail "installer timeout" "timeout got '${limit}', want '${VDE_INSTALLER_TIMEOUT}'"; fi

test_start "vde_install_rustup skips the download when rustc exists"
rm -f "${CURL_LOG}"
printf '#!/usr/bin/env zsh\nexit 0\n' > "${stub}/rustc"; chmod +x "${stub}/rustc"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
rc=$?
if (( rc != 0 )); then test_fail "skip status" "vde_install_rustup returned ${rc}"
elif [[ ! -e "${CURL_LOG}" ]]; then test_pass "no curl call, status 0"
else test_fail "idempotency" "curl ran"; fi

test_start "rust and embed Spokes call the shared helper, not an inline copy"
typeset s ok=1
for s in scripts/setup/rust-init.zsh scripts/setup/embed-init.zsh; do
    grep -q '^vde_install_rustup devuser ' "${s}" || { ok=0; test_fail "${s}" "missing helper call"; }
    grep -q 'rustup/dist' "${s}" && { ok=0; test_fail "${s}" "inline rustup download remains"; }
done
(( ok )) && test_pass "both Spokes use vde_install_rustup"

test_start "probe-rs download is bounded"
typeset e=scripts/setup/embed-init.zsh
if grep -F 'probe-rs-tools-installer.sh' "${e}" >/dev/null \
   && grep -B1 -F 'probe-rs-tools-installer.sh' "${e}" | grep -qF -- '-sSfL "$@"' \
   && grep -qF "' _ \"\${VDE_INSTALLER_TIMEOUT}\" \"\${VDE_CURL_BOUNDS[@]}\"" "${e}"; then
    test_pass "curl takes \"\$@\" and the block passes the timeout and VDE_CURL_BOUNDS"
else test_fail "probe-rs curl" "bounds not wired end to end"; fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
