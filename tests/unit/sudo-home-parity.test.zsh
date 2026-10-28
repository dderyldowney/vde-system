#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: setup scripts run devuser commands with sudo -H (Signet #555).
#
# `sudo -u devuser` alone does not guarantee HOME is devuser's home, so tools
# that install under ~ (pyenv, rustup, SDKMAN, PlatformIO, ...) can target the
# wrong directory. Every sudo that runs as devuser in scripts/setup/*.zsh must
# pass -H (elixir fix, defcb672). Static scan only; no Docker, no writes.

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

# sudo_lacks_home SEGMENT: succeeds when SEGMENT (one sudo command, no pipes)
# runs as devuser without -H / --set-home. Walks sudo's own options only, so
# -H is recognised in any position and bundled (-Hu), and -u/--user in any form.
sudo_lacks_home() {
    local -a words=(${(z)1})
    local w target=0 home=0 expect_arg=0 seen=0
    for w in "${words[@]}"; do
        w="${(Q)w}"
        if (( ! seen )); then [[ "${w}" == sudo ]] && seen=1; continue; fi
        if (( expect_arg )); then
            expect_arg=0
            [[ "${w}" == (devuser|\$\{DEVUSER\}) ]] && target=1
            continue
        fi
        case "${w}" in
            --set-home) home=1 ;;
            --user=*)   [[ "${w#--user=}" == (devuser|\$\{DEVUSER\}) ]] && target=1 ;;
            --user)     expect_arg=1 ;;
            --*)        ;;
            -u?*)       [[ "${w#-u}" == (devuser|\$\{DEVUSER\}) ]] && target=1 ;;
            -[a-zA-Z]*)
                [[ "${w}" == *H* ]] && home=1
                # an arg-taking option last in a bundle (-Hu devuser) consumes the next word
                [[ "${w}" == -*u ]] && expect_arg=1 ;;
            *) break ;;
        esac
    done
    (( target && ! home ))
}

test_start "matcher: option forms (fixtures)"
typeset -a must_flag=(
    'sudo -u devuser zsh -c x'
    'sudo --user devuser zsh -c x'
    'sudo --user=devuser zsh -c x'
    'sudo -u "${DEVUSER}" zsh -c x'
)
typeset -a must_pass=(
    'sudo -H -u devuser zsh -c x'
    'sudo -u devuser -H zsh -c x'
    'sudo -Hu devuser zsh -c x'
    'sudo --set-home --user=devuser zsh -c x'
    'sudo apt-get install -y x'
    'sudo service nginx start'
)
typeset fx fixture_bad=()
for fx in "${must_flag[@]}"; do sudo_lacks_home "${fx}" || fixture_bad+=("should flag: ${fx}"); done
for fx in "${must_pass[@]}"; do sudo_lacks_home "${fx}" && fixture_bad+=("should pass: ${fx}"); done
if (( ${#fixture_bad} == 0 )); then
    test_pass "matcher handles ${#must_flag} flagged + ${#must_pass} compliant forms"
else
    test_fail "matcher fixtures" "${(j:; :)fixture_bad}"
fi

test_start "every devuser sudo in scripts/setup/*.zsh passes -H"
typeset -a offenders
typeset f line logical seg n start
for f in scripts/setup/*.zsh; do
    n=0 start=0 logical=""
    while IFS= read -r line; do
        (( n++ ))
        [[ -z "${logical}" ]] && start=${n}
        [[ "${line}" =~ '^[[:space:]]*#' && -z "${logical}" ]] && continue
        # join backslash-continued physical lines into one logical line
        if [[ "${line}" == *\\ ]]; then logical+="${line%\\} "; continue; fi
        logical+="${line}"
        # split on pipes / separators so each sudo is judged on its own
        for seg in "${(@s:|:)${logical//&&/|}}"; do
            [[ "${seg}" == *sudo* ]] && sudo_lacks_home "${seg}" && offenders+=("${f}:${start}")
        done
        logical=""
    done < "${f}"
done
if (( ${#offenders} == 0 )); then
    test_pass "all devuser sudo calls use -H"
else
    test_fail "sudo -u without -H (${#offenders})" "${(j:, :)offenders}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
