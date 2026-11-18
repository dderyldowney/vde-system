#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: bin/vde action handlers and lib/vde-actions (Signet #588).
#
# Characterization of start/stop/restart/remove/exec/enter/port/help, pinned
# BEFORE they were extracted from bin/vde into lib/vde-actions, so the extraction
# is provably behavior-neutral. Runs the real router and lib in a sandbox with a
# stub `docker` (argv logged) and stub exec/ssh delegates; no daemon needed.
#
# Exit status of stop/restart/remove (Signet #590): 0 when every target was handled
# or was already in the desired state; 1 if any target is unknown or its docker
# operation failed. (It used to be the accident of a trailing `[[ ]] &&` list.)

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

typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Sandbox: real bin/vde and lib/data/templates/configs, stub docker + delegates.
typeset _root="$(mktemp -d)"
trap 'rm -rf "${_root}"' EXIT
mkdir -p "${_root}/bin" "${_root}/stubs"
cp "${VDE_ROOT_DIR}/bin/vde" "${_root}/bin/vde"
for _d in lib data scripts templates docs configs; do
    [[ -e "${VDE_ROOT_DIR}/${_d}" ]] && ln -s "${VDE_ROOT_DIR}/${_d}" "${_root}/${_d}"
done
cat > "${_root}/stubs/docker" <<'STUB'
#!/usr/bin/env zsh
print -r -- "docker $*" >> "${STUB_LOG}"
[[ "$1" == ps ]] && print -rl -- ${=STUB_PS:-}
[[ -n "${STUB_FAIL:-}" && "$1" == "${STUB_FAIL}" ]] && exit 1
exit 0
STUB
chmod +x "${_root}/stubs/docker"
for _s in vde-exec ssh-vm; do
    printf '#!/usr/bin/env zsh\nprint -r -- "%s ARGS=[$*]"\n' "${_s}" > "${_root}/bin/${_s}"
    chmod +x "${_root}/bin/${_s}"
done

typeset rc so_text se_text dk_log
typeset -x STUB_LOG="${_root}/docker.log" VDE_QUIET=1
# run_vde "<names of running containers>" ARGS...  -> rc, so_text, se_text, dk_log
run_vde() {
    local ps="$1"; shift
    : > "${STUB_LOG}"
    so_text="$(PATH="${_root}/stubs:${PATH}" STUB_PS="${ps}" zsh "${_root}/bin/vde" "$@" 2>"${_root}/err")"
    rc=$?
    se_text="$(<"${_root}/err")"
    dk_log="$(<"${STUB_LOG}")"
}
# expect LABEL WANT_RC [stdout-substr] [stderr-substr] [log-substr]  ("" = skip)
expect() {
    local label="$1" want="$2" so="$3" se="$4" lg="$5"
    test_start "${label}"
    if (( rc != want )); then test_fail "${label}" "rc=${rc} want ${want} out=[${so_text[1,100]}] err=[${se_text[1,100]}]"; return; fi
    [[ -n "${so}" && "${so_text}" != *"${so}"* ]] && { test_fail "${label}" "stdout lacks [${so}]: [${so_text[1,100]}]"; return; }
    [[ -n "${se}" && "${se_text}" != *"${se}"* ]] && { test_fail "${label}" "stderr lacks [${se}]: [${se_text[1,100]}]"; return; }
    [[ -n "${lg}" && "${dk_log}" != *"${lg}"* ]] && { test_fail "${label}" "docker log lacks [${lg}]: [${dk_log}]"; return; }
    test_pass "${label}"
}
expect_no_log() {
    test_start "$1"
    if [[ "${dk_log}" != *"$2"* ]]; then test_pass "$1"; else test_fail "$1" "docker log has [$2]: [${dk_log}]"; fi
}

# ── stop ─────────────────────────────────────────────────────────────────────
run_vde "" stop;                       expect "stop: no target -> usage, exit 1" 1 "" "Usage: vde stop"
run_vde "" stop nosuchvm;              expect "stop: unknown alias warns, exit 1" 1 "" "Unknown VM: nosuchvm"
run_vde "vde-python" stop python;      expect "stop: present container is stopped, exit 0" 0 "vde-python stopped" "" "docker stop vde-python"
run_vde "" stop python;                expect "stop: absent container is already stopped, exit 0" 0 "" "" "docker ps -a"
expect_no_log "stop: absent container -> no docker stop" "docker stop"
run_vde "vde-python" stop python nosuch; expect "stop: mixed known+unknown, exit 1" 1 "vde-python stopped" "Unknown VM: nosuch" "docker stop vde-python"
STUB_FAIL=stop run_vde "vde-python" stop python; expect "stop: docker stop fails, exit 1" 1 "" "" "docker stop vde-python"

# ── remove ───────────────────────────────────────────────────────────────────
run_vde "" remove;                     expect "remove: no target -> usage, exit 1" 1 "" "Usage: vde remove"
run_vde "vde-python" rm python;        expect "remove: present container removed, exit 0" 0 "vde-python removed" "" "docker rm -f vde-python"
run_vde "" rm python;                  expect "remove: absent container, nothing to remove, exit 0" 0 "" "" "docker ps -a"
expect_no_log "remove: absent container -> no docker rm" "docker rm"
STUB_FAIL=rm run_vde "vde-python" rm python; expect "remove: docker rm fails, exit 1" 1 "" "" "docker rm -f vde-python"
run_vde "" delete nosuch;              expect "remove: unknown alias warns, exit 1" 1 "" "Unknown VM: nosuch"

# ── restart ──────────────────────────────────────────────────────────────────
run_vde "" restart;                    expect "restart: no target -> usage, exit 1" 1 "" "Usage: vde restart"
run_vde "vde-python" restart python;   expect "restart: stops then starts, exit 0" 0 "vde-python restarted" "" "docker stop vde-python"
run_vde "" restart nosuch;             expect "restart: unknown alias warns, exit 1" 1 "" "Unknown VM: nosuch"

# ── start (paths that need no compose) ───────────────────────────────────────
run_vde "" start;                      expect "start: no target -> usage, exit 1" 1 "" "Usage: vde start"
run_vde "" start nosuchvm;             expect "start: unknown alias reported, exit 0" 0 "Unknown VM type or alias: 'nosuchvm'" "" "docker ps"
run_vde "vde-python" start python;     expect "start: already running is skipped, exit 0" 0 "vde enter python" ""

# ── exec / enter ─────────────────────────────────────────────────────────────
run_vde "" exec;                       expect "exec: no target -> usage, exit 1" 1 "" "Usage: vde exec"
run_vde "" exec python ls -la;         expect "exec: forwards VM and command" 0 "vde-exec ARGS=[python ls -la]"
run_vde "" exec -f python ls;          expect "exec: -f stripped before the target" 0 "vde-exec ARGS=[python ls]"
run_vde "" enter;                      expect "enter: no target -> usage, exit 1" 1 "" "Usage: vde enter"
run_vde "" enter python;               expect "enter: forwards VM" 0 "ssh-vm ARGS=[python]"
run_vde "" ssh python ls -la;          expect "ssh alias: forwards VM and command" 0 "ssh-vm ARGS=[python ls -la]"

# ── port ─────────────────────────────────────────────────────────────────────
run_vde "" port python;                expect "port: prints the SSH port, exit 0" 0 "2217"
run_vde "" port nosuch;                expect "port: unknown alias prints nothing, exit 0" 0

# ── help ─────────────────────────────────────────────────────────────────────
run_vde "" help;                       expect "help: usage, exit 0" 0 "Usage: vde <command>"
run_vde "" -h;                         expect "-h: usage, exit 0" 0 "Usage: vde <command>"
run_vde "" --help;                     expect "--help: usage, exit 0" 0 "The Sovereign Orchestrator"

# ── function-trace must not show the extracted frames ────────────────────────
run_vde "vde-python" function-trace stop python
test_start "function-trace: vde_action_* frames hidden"
if [[ "${so_text}" == *"FUNCTION TRACE"* && "${so_text}" != *"vde_action_"* ]]; then
    test_pass "no vde_action_ frame in trace"
else
    test_fail "trace" "trace missing or leaks a vde_action_ frame: [${so_text[1,160]}]"
fi

# ── lib/vde-actions contract (red until the extraction lands) ────────────────
test_start "lib/vde-actions defines every vde_action_* handler"
typeset _missing=""
if [[ -f "${VDE_ROOT_DIR}/lib/vde-actions" ]]; then
    for _fn in start stop restart remove exec enter port help; do
        zsh -c "source '${VDE_ROOT_DIR}/lib/vde-actions'; typeset -f vde_action_${_fn} >/dev/null" 2>/dev/null || _missing+=" ${_fn}"
    done
else
    _missing=" (lib/vde-actions absent)"
fi
if [[ -z "${_missing}" ]]; then test_pass "all 8 handlers defined"; else test_fail "handlers" "missing:${_missing}"; fi

test_start "handler status is explicit: no _VDE_ACTION_RC handover remains"
if ! grep -rq '_VDE_ACTION_RC' "${VDE_ROOT_DIR}/bin/vde" "${VDE_ROOT_DIR}/lib/vde-actions"; then
    test_pass "no accidental-status handover"
else
    test_fail "rc handover" "_VDE_ACTION_RC still referenced"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
