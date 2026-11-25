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
# Spokes it started; a Spoke already running is left running (and is never
# written to through its host mount). Never prunes images.
# A Spoke that does not become ready is given about two minutes; every remote
# probe is also bounded by its own timeout.
# The login uses the student identity in ~/.ssh/vde (VDE_SSH_DIR overrides it).
# Service Spokes keep their data in the checkout's data/<name> directory, as
# `vde start` always does; run this from a disposable checkout if that matters.
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
test_pass() { print -n -P "${GREEN}[PASS]${RESET} "; print -r -- "$1"; ((TESTS_PASSED++)); return 0; }
test_fail() { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; ((TESTS_FAILED++)); return 0; }
test_skip() { print -r -- "[SKIP] $1"; return 0; }

# --- the matrix ---------------------------------------------------------------
# Per Spoke: its kind, the command that proves its own tool or service works,
# and a pattern its output must match.
typeset -A KIND=(
  python lang
  js lang
  postgres service
  redis service
  nginx service
)
typeset -A TOOL_CMD=(
  python 'python3 --version'
  js 'node --version && npm --version'
  postgres 'pg_isready -h localhost'
  redis 'redis-cli ping'
  nginx 'curl -s -m 10 -o /dev/null -w "%{http_code}" http://localhost/'
)
typeset -A TOOL_RE=(
  python '^Python 3'
  js '^v[0-9]+'
  postgres 'accepting connections'
  redis '^PONG$'
  nginx '^[234][0-9][0-9]$'
)
typeset -a BATCH1=(python postgres redis)
typeset -a BATCH2=(python nginx js)

typeset SSH_DIR="${VDE_SSH_DIR:-${HOME}/.ssh/vde}"
typeset -a SSH_OPTS=(
  -F /dev/null -i "${SSH_DIR}/vde_student" -o IdentityAgent=none -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10
)

load_vm_types >/dev/null 2>&1
ssh_port_of() { get_vm_info ssh_port "vde-${1}" 2>/dev/null; }
svc_port_of() { local p; p="$(get_vm_info svc_ports "vde-${1}" 2>/dev/null)"; print -r -- "${p%%,*}"; }

# in_spoke <name> <command...>: run on the Spoke over SSH (stdin closed, bounded by a
# timeout so a stalled probe cannot hang the run); prints its output, returns its status.
in_spoke() {
  local name="${1}"; shift
  timeout 45 ssh -n "${SSH_OPTS[@]}" -p "$(ssh_port_of "${name}")" devuser@127.0.0.1 "$@" 2>&1
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
typeset NODE_SRV_FILE=""

# cleanup_node: remove the Node server and its files (also in a Spoke this run did not start).
cleanup_node() {
  [[ -n "${NODE_SRV_FILE}" ]] || return 0
  in_spoke js "kill \$(cat ${NODE_SRV_FILE}.pid) 2>/dev/null; rm -f ${NODE_SRV_FILE} ${NODE_SRV_FILE}.pid; true" >/dev/null
  NODE_SRV_FILE=""
}

# cleanup: remove the Node server, then stop only the Spokes this run started. A Spoke
# that cannot be stopped is reported and stays tracked, never silently forgotten.
cleanup() {
  cleanup_node
  (( ${#STARTED} )) || return 0
  local s
  local -a failed=()
  for s in "${STARTED[@]}"; do
    "${PROJECT_ROOT}/bin/vde" stop "${s}" >/dev/null 2>&1 || failed+=("${s}")
  done
  STARTED=("${failed[@]}")
  (( ${#failed} == 0 )) && return 0
  test_fail "cleanup: stop the Spokes this run started" "could not stop: ${failed}"
  return 1
}
# An interrupt or termination stops what this run started and ends the run.
trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

# running_spokes: names (without the vde- prefix) of the running containers that VDE
# manages. Other containers that happen to be called vde-* do not count against Rule K.
running_spokes() {
  local -a names=("${(@f)$(docker ps --filter 'label=vde.managed=true' --format '{{.Names}}' 2>/dev/null)}")
  names=("${(@)names:#}")
  (( ${#names} )) && print -rl -- "${(@)names#vde-}"
  return 0
}

# wait_ready <name>: poll until SSH answers and the Spoke's own tool works (about two minutes).
wait_ready() {
  local name="${1}" out
  local -i deadline=$(( SECONDS + 120 ))
  while (( SECONDS < deadline )); do
    out="$(in_spoke "${name}" "${TOOL_CMD[$name]}")" && [[ "${out}" =~ ${TOOL_RE[$name]} ]] && return 0
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

# workspace_src <name>: print the host path behind the Spoke's workspace mount. Status 0 means
# it is safe to write through: this run started the Spoke AND the path is inside the scratch
# Projects base. 1 = not safe (a Spoke started elsewhere, no scratch base, a path outside the
# base or containing ..); 2 = the container has no workspace mount at all. It fails closed.
workspace_src() {
  local n="${1}" scratch src
  src="$(docker inspect "vde-${n}" --format '{{range .Mounts}}{{if eq .Destination "/home/devuser/workspace"}}{{.Source}}{{end}}{{end}}' 2>/dev/null)"
  [[ -n "${src}" ]] || return 2
  print -r -- "${src}"
  (( ${STARTED[(Ie)${n}]} )) || return 1
  scratch="$(vde_test_env_dir)" || return 1
  [[ -n "${scratch}" ]] || return 1
  [[ "${src}" == "${scratch}"/* && "${src}" != *..* ]] || return 1
  return 0
}

# check_workspace <name>: language Spokes only.
#  - started by this run: a file written in the workspace must appear at the mount's host
#    path, and only when that path is inside the scratch Projects base;
#  - already running: the workspace must be writable, checked without writing anything.
check_workspace() {
  local n="${1}" out rc host_src sr marker
  if (( ! ${STARTED[(Ie)${n}]} )); then
    out="$(in_spoke "${n}" 'test -d /home/devuser/workspace && test -w /home/devuser/workspace && print workspace-writable')"; rc=$?
    check "${n}: the workspace is writable (checked without writing; this Spoke was already running)" ${rc} "${out}" '^workspace-writable$'
    return 0
  fi
  host_src="$(workspace_src "${n}")"; sr=$?
  if (( sr == 1 )); then
    test_skip "${n}: a workspace write reaching the host mount (the mount source is outside the scratch Projects base; nothing is written there)"
    return 0
  elif (( sr == 2 )); then
    check "${n}: a workspace write reaches the host mount" 0 "no workspace mount on the container" '^on-host$'
    return 0
  fi
  marker=".smoke.${RUN_TAG}.${n}"
  rm -f -- "${host_src}/${marker}"
  in_spoke "${n}" "touch /home/devuser/workspace/${marker}" >/dev/null; rc=$?
  if (( rc != 0 )); then out="write failed"
  elif [[ -f "${host_src}/${marker}" ]]; then out="on-host"
  else out="written in the Spoke but absent at ${host_src}"; fi
  check "${n}: a workspace write reaches the host mount" 0 "${out}" '^on-host$'
  in_spoke "${n}" "rm -f /home/devuser/workspace/${marker}" >/dev/null
  rm -f -- "${host_src}/${marker}"
  return 0
}

# check_node: a real file round trip, a real server, and a client in another Spoke.
check_node() {
  local src="${1}" out rc node_dir node_js srv_js node_file srv_file srv_port srv_body
  # The workspace is only written when it is safe (this run started js and its mount is inside the
  # scratch Projects base; see workspace_src). Otherwise the round trip uses /tmp in the Spoke.
  node_dir=/tmp
  workspace_src js >/dev/null && node_dir=/home/devuser/workspace
  node_js='const fs=require("fs"),http=require("http");
const f="'"${node_dir}"'/.smoke-node."+process.pid;
fs.writeFileSync(f,"ok");const r=fs.readFileSync(f,"utf8");fs.unlinkSync(f);
const s=http.createServer((q,res)=>res.end("hello-from-node")).listen(0,()=>{
 http.get("http://127.0.0.1:"+s.address().port,x=>{let d="";x.on("data",c=>d+=c);
 x.on("end",()=>{console.log("fs-"+r+" http-"+d);s.close()})})})'
  node_file="/tmp/vde-smoke-node.${RUN_TAG}.js"
  out="$(print -r -- "${node_js}" | timeout 45 ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of js)" devuser@127.0.0.1 "cat > ${node_file} && node ${node_file}; r=\$?; rm -f ${node_file} ${node_dir}/.smoke-node.*(N); exit \$r" 2>&1)"; rc=$?
  check "js: Node fs round trip and HTTP server answer themselves" ${rc} "${out}" '^fs-ok http-hello-from-node$'

  # A per-run port and a per-run response, so a stale listener cannot satisfy the check,
  # and a check that the server process really started.
  srv_port=$(( 39000 + RUN_TAG % 900 ))
  srv_body="hello-from-node-${RUN_TAG}"
  srv_file="/tmp/vde-smoke-srv.${RUN_TAG}.js"
  srv_js='require("http").createServer((q,r)=>r.end("'"${srv_body}"'")).listen('"${srv_port}"')'
  NODE_SRV_FILE="${srv_file}"
  print -r -- "${srv_js}" | timeout 45 ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of js)" devuser@127.0.0.1 "cat > ${srv_file}; node ${srv_file} >/dev/null 2>&1 </dev/null & echo \$! > ${srv_file}.pid" >/dev/null 2>&1
  out="$(in_spoke js "kill -0 \$(cat ${srv_file}.pid)")"; rc=$?
  if (( rc != 0 )); then
    out="the Node server did not start (port ${srv_port} may be in use)"; rc=1
  elif wait_port "${src}" vde-js "${srv_port}"; then
    out="$(print -r -- 'import urllib.request as u; print("cross-" + u.urlopen("http://vde-js:'"${srv_port}"'", timeout=8).read().decode())' | timeout 45 ssh "${SSH_OPTS[@]}" -p "$(ssh_port_of "${src}")" devuser@127.0.0.1 'python3 -' 2>&1)"; rc=$?
  else
    out="port ${srv_port} on vde-js never answered"; rc=1
  fi
  check "${src} -> js:${srv_port}: a Node server in one Spoke answers a client in another" ${rc} "${out}" "^cross-${srv_body}\$"
  cleanup_node
  return 0
}

run_batch() {
  local label="${1}"; shift
  local -a spokes=("$@") to_start=() others running
  local n out rc t port
  # The snapshot is taken immediately before the start, so only a Spoke that was not
  # running at that moment is recorded as started by this run.
  running=("${(@f)$(running_spokes)}")
  running=("${(@)running:#}")
  for n in "${spokes[@]}"; do
    (( ${running[(Ie)${n}]} )) || to_start+=("${n}")
  done
  others=("${(@)running:|spokes}")
  if (( ${#others} + ${#spokes} > 3 )); then
    test_fail "${label}: free Spoke slots" "Rule K allows 3 running Spokes; others running: ${others}. Stop them and re-run."
    return 1
  fi
  test_start "${label}: start ${to_start:-nothing (already running)}"
  if (( ${#to_start} )); then
    STARTED+=("${to_start[@]}")
    if "${PROJECT_ROOT}/bin/vde" start "${to_start[@]}" >/dev/null 2>&1; then
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

  for n in "${spokes[@]}"; do
    out="$(in_spoke "${n}" 'print -r -- "host=$(hostname) user=$(whoami)"')"; rc=$?
    check "${n}: Hub to Spoke SSH login as devuser" ${rc} "${out}" "^host=vde-${n} user=devuser\$"

    if [[ "${KIND[$n]}" == "lang" ]]; then
      check_workspace "${n}"
    else
      test_skip "${n}: workspace write (a service Spoke has no workspace mount)"
    fi

    out="$(in_spoke "${n}" 'if test -S "$SSH_AUTH_SOCK"; then ssh-add -l >/dev/null 2>&1; r=$?; if test $r -ne 2; then print agent-ok; else print agent-unreachable; fi; else print no-agent-socket; fi')"; rc=$?
    check "${n}: SSH agent socket answers" ${rc} "${out}" '^agent-ok$'

    out="$(in_spoke "${n}" "${TOOL_CMD[$n]}")"; rc=$?
    check "${n}: its own tool or service works" ${rc} "${out}" "${TOOL_RE[$n]}"
  done

  # Spoke -> Spoke from python: DNS on the real SSH port, then TCP to each service port.
  for t in "${spokes[@]}"; do
    [[ "${t}" == "python" ]] && continue
    out="$(timeout 45 "${PROJECT_ROOT}/bin/vde" dns-check python "${t}" "$(ssh_port_of "${t}")" 2>&1)"; rc=$?
    check "python -> ${t}: DNS and bridge" ${rc} "${out}" 'Certification: PASS'
    port="$(svc_port_of "${t}")"
    if [[ -n "${port}" ]]; then
      out="$(in_spoke python "zmodload zsh/net/tcp && ztcp vde-${t} ${port} && print connected")"; rc=$?
      check "python -> ${t}:${port}: TCP on vde-net" ${rc} "${out}" '^connected$'
    else
      test_skip "python -> ${t}: TCP (${t} publishes no service port; its SSH port is covered by the DNS bridge check)"
    fi
  done

  (( ${spokes[(Ie)js]} )) && check_node python

  cleanup
  return 0
}

main() {
  # Preflight: refuse to pass on an environment that cannot run the matrix.
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
}

main "$@"
