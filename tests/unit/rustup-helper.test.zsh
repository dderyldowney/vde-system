#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: shared rustup helper and bounded downloads (Signet #598).
#
# vde_install_rustup lives once in lib/vde-core; rust-init and embed-init call
# it, and the rustup-init and probe-rs downloads carry VDE_CURL_BOUNDS. Stubs stand in for
# sudo and curl; nothing touches the network or the host toolchain.

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
# curl stub records its arguments and writes a no-op installer to -o.
cat > "${stub}/curl" <<'STUB'
#!/usr/bin/env zsh
print -r -- "$*" > "${CURL_LOG}"
o=; while (( $# )); do [[ $1 == -o ]] && o=$2; shift; done
printf '#!/usr/bin/env zsh\nexit 0\n' > "${o}"
print -r -- "${o:t}" > "${CURL_LOG}.name"
STUB
chmod +x "${stub}/sudo" "${stub}/curl"
# Hermetic PATH: the stub dir plus links to the few tools the helper runs, so a
# host rustc in /usr/bin can never change what these tests exercise.
typeset t
for t in zsh env uname mktemp chmod rm; do ln -s "$(command -v ${t})" "${stub}/${t}"; done
typeset -x CURL_LOG="${stub}/curl.log"

test_start "VDE_CURL_BOUNDS caps connect time, total time and retries"
source lib/vde-core
typeset b="${VDE_CURL_BOUNDS[*]}"
typeset -a want=(--connect-timeout 30 --max-time 600 --retry 3 --retry-delay 2)
if [[ "${VDE_CURL_BOUNDS[*]}" == "${want[*]}" ]]; then
    test_pass "${b}"
else test_fail "VDE_CURL_BOUNDS" "got '${b}', want '${want[*]}'"; fi

test_start "vde_install_rustup downloads the native binary with the bounds"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
typeset got="$(<"${CURL_LOG}")"
if [[ "${got}" == *"--connect-timeout 30"* && "${got}" == *"static.rust-lang.org/rustup/dist/"*"/rustup-init"* ]]; then
    test_pass "curl ${got%% -o*}"
else test_fail "curl args" "got '${got}'"; fi

test_start "installer keeps the name rustup-init (multi-call dispatch)"
if [[ "$(<"${CURL_LOG}.name")" == "rustup-init" ]]; then test_pass "file name rustup-init"
else test_fail "installer name" "got '$(<"${CURL_LOG}.name")'"; fi

test_start "vde_install_rustup skips the download when rustc exists"
rm -f "${CURL_LOG}"
printf '#!/usr/bin/env zsh\nexit 0\n' > "${stub}/rustc"; chmod +x "${stub}/rustc"
PATH="${stub}" vde_install_rustup nobody VDE-T >/dev/null 2>&1
if [[ ! -e "${CURL_LOG}" ]]; then test_pass "no curl call"; else test_fail "idempotency" "curl ran"; fi

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
   && grep -qF "' _ \"\${VDE_CURL_BOUNDS[@]}\"" "${e}"; then
    test_pass "curl takes \"\$@\" and the block passes VDE_CURL_BOUNDS"
else test_fail "probe-rs curl" "bounds not wired end to end"; fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
