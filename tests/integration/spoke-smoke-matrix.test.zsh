#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# Integration Test: Spoke smoke matrix (one Spoke per category), Signet #766
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# A change that quietly stops one kind of Spoke from working, or from being
# reachable, must fail a test. This starts a representative Spoke from each
# category, at most three at a time (Rule K), and checks the everyday workflow:
#   Hub -> Spoke   SSH login as devuser over loopback, a workspace write that
#                  reaches the host mount (language Spokes), a working SSH agent
#                  socket, and the Spoke's own tool or service.
#   Spoke -> Spoke (free mixing) DNS and TCP from python to each other Spoke on
#                  vde-net, plus a Node server in js answered to a client in python.
# Batch 1: python postgres redis.   Batch 2: python nginx js.
#
# Needs a Docker daemon and the Spoke images (a missing image is built by
# `vde start`, which takes a while the first time). Starts and stops only the
# Spokes it started; a Spoke already running is left running. Never prunes images.
# A Spoke that does not become ready is given about two minutes.
# Listed in tests/ci-coverage-exclusions.txt: run by hand before a release and
# whenever a change touches the templates, an image or the entrypoint.

typeset SCRIPT_DIR="${0:A:h}"
typeset PROJECT_ROOT="${SCRIPT_DIR:h:h}"
export VDE_ROOT_DIR="${PROJECT_ROOT}"
cd "${PROJECT_ROOT}" || exit 1
source "${PROJECT_ROOT}/lib/vde-constants" >/dev/null 2>&1
source "${PROJECT_ROOT}/lib/vm-common" >/dev/null 2>&1
zmodload zsh/zselect

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset RUN_TAG="$$"
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
# Messages carry command output, so they are printed raw (no prompt expansion).
test_start() { print -n -P "${YELLOW}[TEST]${RESET} "; print -r -- "$1"; }
test_pass()  { print -n -P "${GREEN}[PASS]${RESET} "; print -r -- "$1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; ((TESTS_FAILED++)); return 0; }
test_skip()  { print -r -- "[SKIP] $1"; return 0; }

# --- the matrix ---------------------------------------------------------------
# Per Spoke: its kind, the command that proves its own tool or service works,
# and a pattern its output must match.
typeset -A KIND=( python lang js lang postgres service redis service nginx service )
typeset -A TOOL_CMD=(
    python   'python3 --version'
    js       'node --version && npm --version'
    postgres 'pg_isready -h localhost'
    redis    'redis-cli ping'
    nginx    'curl -s -o /dev/null -w "%{http_code}" http://localhost/'
)
typeset -A TOOL_RE=(
    python   '^Python 3'
    js       '^v[0-9]+'
    postgres 'accepting connections'
    redis    '^PONG$'
    nginx    '^[234][0-9][0-9]$'
)
typeset -a BATCH1=(python postgres redis)
typeset -a BATCH2=(python nginx js)

typeset SSH_DIR="${VDE_SSH_DIR:-${HOME}/.ssh/vde}"
typeset -a SSH_OPTS=(-F /dev/null -i "${SSH_DIR}/vde_student" -o IdentityAgent=none -o IdentitiesOnly=yes
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10)

load_vm_types >/dev/null 2>&1
ssh_port_of() { get_vm_info ssh_port "vde-${1}" 2>/dev/null; }
svc_port_of() { local p; p="$(get_vm_info svc_ports "vde-${1}" 2>/dev/null)"; print -r -- "${p%%,*}"; }

# in_spoke <name> <command...>: run on the Spoke over SSH (stdin closed); prints
# its output, returns its status.
in_spoke() {
    local name="${1}"; shift
    ssh -n "${SSH_OPTS[@]}" -p "$(ssh_port_of ${name})" devuser@127.0.0.1 "$@" 2>&1
}

# check <label> <status> <output> <pattern>: pass only on status 0 AND a non-empty match.
check() {
    local label="${1}" rc="${2}" out="${3}" re="${4}"
    test_start "${label}"
    if (( rc != 0 )); then
        test_fail "${label}" "exit status ${rc}: ${out:0:160}"
    elif [[ -z "${out}" ]]; then
        test_fail "${label}" "empty output; refusing to pass on nothing"
    elif [[ ! "${out}" =~ ${re} ]]; then
        test_fail "${label}" "output did not match /${re}/: ${out:0:160}"
    else
        test_pass "${label}"
    fi
}

typeset -a STARTED=()
cleanup() {
    (( ${#STARTED} )) || return 0
    "${PROJECT_ROOT}/bin/vde" stop ${STARTED} >/dev/null 2>&1
    STARTED=()
}
# An interrupt or termination stops what this run started and ends the run.
trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

# running_spokes: names of VDE Spokes currently running (without the vde- prefix).
running_spokes() { docker ps --format '{{.Names}}' 2>/dev/null | sed -n 's/^vde-//p'; }

# wait_ready <name>: poll until SSH answers and the Spoke's own tool works (about two minutes).
wait_ready() {
    local name="${1}" out
    local -i deadline=$(( SECONDS + 120 ))
    while (( SECONDS < deadline )); do
        out="$(in_spoke ${name} "${TOOL_CMD[$name]}")" && [[ "${out}" =~ ${TOOL_RE[$name]} ]] && return 0
        zselect -t 200
    done
    return 1
}

# wait_port <from-spoke> <host> <port>: poll a TCP connect from a Spoke (about 10 s).
wait_port() {
    local from="${1}" host="${2}" port="${3}" i
    for (( i = 0; i < 40; i++ )); do
        in_spoke "${from}" "zmodload zsh/net/tcp && ztcp ${host} ${port}" >/dev/null && return 0
        zselect -t 25
    done
    return 1
}

run_batch() {
    local label="${1}"; shift
    local -a spokes=("$@") to_start=() others running
    local n
    running=(${(f)"$(running_spokes)"})
    for n in "${spokes[@]}"; do
        (( ${running[(Ie)${n}]} )) || to_start+=("${n}")
    done
    others=(${running:|spokes})
    if (( ${#others} + ${#spokes} > 3 )); then
        test_fail "${label}: free Spoke slots" "Rule K allows 3 running Spokes; others running: ${others}. Stop them and re-run."
        return 1
    fi
    test_start "${label}: start ${to_start:-nothing (already running)}"
    if (( ${#to_start} )); then
        STARTED+=("${to_start[@]}")
        if "${PROJECT_ROOT}/bin/vde" start ${to_start} >/dev/null 2>&1; then
            test_pass "${label}: start ${to_start}"
        else
            test_fail "${label}: start" "vde start ${to_start} failed"
            cleanup
            return 1
        fi
    else
        test_pass "${label}: all target Spokes already running"
    fi

    for n in "${spokes[@]}"; do
        test_start "${label}: ${n} becomes ready"
        if wait_ready "${n}"; then test_pass "${label}: ${n} becomes ready"; else test_fail "${label}: ${n} ready" "did not answer in time"; fi
    done

    local out rc host_src marker
    for n in "${spokes[@]}"; do
        out="$(in_spoke ${n} 'print -r -- "host=$(hostname) user=$(whoami)"')"; rc=$?
        check "${n}: Hub to Spoke SSH login as devuser" ${rc} "${out}" "^host=vde-${n} user=devuser$"

        if [[ "${KIND[$n]}" == lang ]] && (( ! ${STARTED[(Ie)${n}]} )); then
            # A Spoke started outside this run may mount the caller's real projects: never write there.
            test_skip "${n}: workspace write reaches the host mount (already running before this run; no host write outside the scratch Projects base)"
        elif [[ "${KIND[$n]}" == lang ]]; then
            # End to end: a file written in the Spoke's workspace must appear at the mount's host path.
            marker=".smoke.${RUN_TAG}.${n}"
            host_src="$(docker inspect "vde-${n}" --format '{{range .Mounts}}{{if eq .Destination "/home/devuser/workspace"}}{{.Source}}{{end}}{{end}}' 2>/dev/null)"
            [[ -n "${host_src}" ]] && rm -f -- "${host_src}/${marker}"
            in_spoke ${n} "touch /home/devuser/workspace/${marker}" >/dev/null; rc=$?
            if (( rc != 0 )); then out="write failed"
            elif [[ -z "${host_src}" ]]; then out="no workspace mount on the container"
            elif [[ -f "${host_src}/${marker}" ]]; then out="on-host"
            else out="written in the Spoke but absent at ${host_src}"; fi
            check "${n}: a workspace write reaches the host mount" 0 "${out}" '^on-host$'
            in_spoke ${n} "rm -f /home/devuser/workspace/${marker}" >/dev/null
            [[ -n "${host_src}" ]] && rm -f -- "${host_src}/${marker}"
        else
            test_skip "${n}: workspace write (a service Spoke has no workspace mount)"
        fi

        out="$(in_spoke ${n} 'if test -S "$SSH_AUTH_SOCK"; then ssh-add -l >/dev/null 2>&1; r=$?; if test $r -ne 2; then print agent-ok; else print agent-unreachable; fi; else print no-agent-socket; fi')"; rc=$?
        check "${n}: SSH agent socket answers" ${rc} "${out}" '^agent-ok$'

        out="$(in_spoke ${n} "${TOOL_CMD[$n]}")"; rc=$?
        check "${n}: its own tool or service works" ${rc} "${out}" "${TOOL_RE[$n]}"
    done

    # Spoke -> Spoke from python: DNS on the real SSH port, then TCP to each service port.
    local t port
    for t in "${spokes[@]}"; do
        [[ "${t}" == python ]] && continue
        out="$("${PROJECT_ROOT}/bin/vde" dns-check python ${t} "$(ssh_port_of ${t})" 2>&1)"; rc=$?
        check "python -> ${t}: DNS and bridge" ${rc} "${out}" 'Certification: PASS'
        port="$(svc_port_of ${t})"
        if [[ -n "${port}" ]]; then
            out="$(in_spoke python "zmodload zsh/net/tcp && ztcp vde-${t} ${port} && print connected")"; rc=$?
            check "python -> ${t}:${port}: TCP on vde-net" ${rc} "${out}" '^connected$'
        else
            test_skip "python -> ${t}: TCP (${t} publishes no service port; its SSH port is covered by the DNS bridge check)"
        fi
    done

    # Node (js Spoke): a real file round trip, a real server, and a client in python.
    if (( ${spokes[(Ie)js]} )); then
        # The workspace is only written when this run started js (see the workspace check above).
        local node_dir=/home/devuser/workspace
        (( ${STARTED[(Ie)js]} )) || node_dir=/tmp
        local node_js='const fs=require("fs"),http=require("http");
const f="'"${node_dir}"'/.smoke-node."+process.pid;
fs.writeFileSync(f,"ok");const r=fs.readFileSync(f,"utf8");fs.unlinkSync(f);
const s=http.createServer((q,res)=>res.end("hello-from-node")).listen(0,()=>{
 http.get("http://127.0.0.1:"+s.address().port,x=>{let d="";x.on("data",c=>d+=c);
 x.on("end",()=>{console.log("fs-"+r+" http-"+d);s.close()})})})'
        local node_file="/tmp/vde-smoke-node.${RUN_TAG}.js" srv_file="/tmp/vde-smoke-srv.${RUN_TAG}.js"
        out="$(print -r -- "${node_js}" | ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of js)" devuser@127.0.0.1 "cat > ${node_file} && node ${node_file}; r=\$?; rm -f ${node_file}; exit \$r" 2>&1)"; rc=$?
        check "js: Node fs round trip and HTTP server answer themselves" ${rc} "${out}" '^fs-ok http-hello-from-node$'

        local srv_js='require("http").createServer((q,r)=>r.end("hello-from-node")).listen(3998)'
        print -r -- "${srv_js}" | ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of js)" devuser@127.0.0.1 "cat > ${srv_file}; node ${srv_file} >/dev/null 2>&1 & echo \$! > ${srv_file}.pid" >/dev/null 2>&1
        if wait_port python vde-js 3998; then
            out="$(print -r -- 'import urllib.request as u; print("cross-" + u.urlopen("http://vde-js:3998", timeout=8).read().decode())' | ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of python)" devuser@127.0.0.1 'python3 -' 2>&1)"; rc=$?
        else
            out="port 3998 on vde-js never answered"; rc=1
        fi
        check "python -> js:3998: a Node server in one Spoke answers a client in another" ${rc} "${out}" '^cross-hello-from-node$'
        in_spoke js "kill \$(cat ${srv_file}.pid) 2>/dev/null; rm -f ${srv_file} ${srv_file}.pid; true" >/dev/null
    fi

    cleanup
}

# --- preflight: refuse to pass on an environment that cannot run the matrix ----
test_start "preflight: Docker daemon, VDE SSH identity and the vde CLI are available"
if ! docker info >/dev/null 2>&1; then
    test_fail "preflight" "no Docker daemon"
elif [[ ! -f "${SSH_DIR}/vde_student" ]]; then
    test_fail "preflight" "no VDE identity at ${SSH_DIR}/vde_student (run vde init)"
elif [[ ! -x "${PROJECT_ROOT}/bin/vde" ]]; then
    test_fail "preflight" "bin/vde is missing"
else
    test_pass "preflight"
    run_batch "batch 1" "${BATCH1[@]}"
    run_batch "batch 2" "${BATCH2[@]}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_PASSED > 0 && TESTS_FAILED == 0 ))
