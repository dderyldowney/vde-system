#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: the agent-socket bind mounts never auto-create their source (Signet #618).
#
# Docker creates a missing short-form bind source as a root-owned DIRECTORY. For
# the SSH agent socket that blocks the VDE agent for good (Signet #616 guards the
# `vde start` entry point; this guards the manifests themselves, for anything that
# runs `docker compose up` on them directly). The long form with
# `bind.create_host_path: false` makes Docker REFUSE to start instead.
#
# Checks, in order:
#   1. both templates use the long form for BOTH socket targets;
#   2. every tracked docker-compose.yml that mounts the socket does the same
#      (the templates are the source, the 34 manifests are what Docker reads);
#   3. `docker compose config` keeps create_host_path=false on both mounts
#      (skipped loudly when the docker CLI is absent);
#   4. behaviour: Compose refuses a missing source and creates nothing
#      (skipped loudly when no Docker daemon or no local image is available).
#
# Nothing here writes into the repo; fixtures live in a scratch directory.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset TESTS_SKIPPED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }
test_skip()  { echo -e "${YELLOW}[SKIP]${RESET} $1: $2"; TESTS_SKIPPED=$((TESTS_SKIPPED + 1)); return 0; }

typeset -a SOCKET_TARGETS=(/run/host-services/ssh-auth.sock /run/vde-ssh.sock)
typeset SOURCE_EXPR='${VDE_HOST_SSH_AUTH_SOCK:-/run/host-services/ssh-auth.sock}'

# socket_mount_problems FILE -> prints one line per defect, nothing when sound.
# A sound file has, for each target, NO short-form line `<src>:<target>` and
# exactly one long-form block: `type: bind`, the default source, the target and
# `create_host_path: false` inside the same `bind:` map.
socket_mount_problems() {
    local file="${1}" target short_re
    local -a lines=("${(@f)$(<"${file}")}")
    local i found
    for target in "${SOCKET_TARGETS[@]}"; do
        # short form: a list item whose scalar ends in ":<target>" (optionally ":ro")
        if print -rl -- "${lines[@]}" | grep -qE "^[[:space:]]*-[[:space:]]+[^[:space:]#].*:${target}(:[a-z]+)?[[:space:]]*\$"; then
            print -r -- "short-form mount of ${target} remains"
        fi
        found=0
        for (( i = 1; i <= ${#lines}; i++ )); do
            [[ "${lines[i]}" == *"target: ${target}" ]] || continue
            found=$((found + 1))
            # the block is: "- type: bind" / source / target / bind: / create_host_path
            [[ "${lines[i-2]}" == *"- type: bind" ]] || print -r -- "${target}: not a long-form bind (line $((i-2)))"
            [[ "${lines[i-1]}" == *"source: ${SOURCE_EXPR}" ]] || print -r -- "${target}: source is not ${SOURCE_EXPR}"
            [[ "${lines[i+1]}" == *"bind:" && "${lines[i+2]}" == *"create_host_path: false" ]] \
                || print -r -- "${target}: bind.create_host_path is not false"
        done
        (( found == 1 )) || print -r -- "${target}: expected exactly 1 long-form mount, found ${found}"
    done
}

# socket_manifests -> every tracked compose manifest that mounts the agent socket
# (one path per line). A helper, not an inline pipeline (Mandate D).
socket_manifests() {
    local f
    for f in ${(f)"$(git ls-files 'configs/docker/*docker-compose.yml')"}; do
        grep -qF 'ssh-auth.sock' "${f}" && print -r -- "${f}"
    done
    return 0
}

# --- 1. templates --------------------------------------------------------------
typeset tpl problems
for tpl in templates/compose-language.yml templates/compose-service.yml; do
    test_start "${tpl}: both agent-socket mounts are long-form with create_host_path: false"
    problems="$(socket_mount_problems "${tpl}")"
    if [[ -z "${problems}" ]]; then
        test_pass "${tpl} agent-socket mounts never auto-create"
    else
        test_fail "${tpl}" "${(j:; :)${(f)problems}}"
    fi
done

# --- 2. every tracked manifest that mounts the socket --------------------------
test_start "every tracked compose manifest that mounts the agent socket is long-form"
typeset -a manifests bad
typeset f
manifests=("${(@f)$(socket_manifests)}")
for f in "${manifests[@]}"; do
    [[ -z "${f}" ]] && continue
    problems="$(socket_mount_problems "${f}")"
    [[ -n "${problems}" ]] && bad+=("${f} (${(j:, :)${(f)problems}})")
done
if (( ${#manifests} >= 30 )) && (( ${#bad} == 0 )); then
    test_pass "${#manifests} tracked manifests mount the agent socket long-form"
elif (( ${#manifests} < 30 )); then
    test_fail "manifest census" "found only ${#manifests} manifests that mount the socket (expected >= 30)"
else
    test_fail "${#bad} manifest(s) still auto-create the socket source" "${(j:; :)bad[1,3]}"
fi

# --- 3. docker compose config keeps the flag -----------------------------------
test_start "docker compose config keeps create_host_path=false on both mounts"
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    test_skip "compose config" "docker compose CLI not available"
else
    # The manifest names untracked env files (../../../../.env, env-files/python.env),
    # absent in a fresh checkout: render a copy inside a scratch tree of the same
    # relative layout with empty ones, so the test never depends on the host's .env.
    typeset cfg_root; cfg_root="$(mktemp -d)"
    mkdir -p "${cfg_root}/configs/docker/languages/python" "${cfg_root}/env-files"
    : > "${cfg_root}/.env"; : > "${cfg_root}/env-files/python.env"
    cp configs/docker/languages/python/docker-compose.yml "${cfg_root}/configs/docker/languages/python/"
    typeset cfg
    cfg="$(VDE_HOST_SSH_AUTH_SOCK=/nonexistent/agent.sock VDE_DOCKER_SOCK_GID=1000 \
        docker compose -f "${cfg_root}/configs/docker/languages/python/docker-compose.yml" config --format json 2>&1)"
    rm -rf -- "${cfg_root}"
    typeset flags
    flags="$(print -r -- "${cfg}" | python3 -I -c '
import json, sys
try:
    cfg = json.load(sys.stdin)
except ValueError:
    print("unparseable"); sys.exit(0)
out = []
for svc in cfg.get("services", {}).values():
    for v in svc.get("volumes", []):
        if v.get("target") in ("/run/vde-ssh.sock", "/run/host-services/ssh-auth.sock"):
            out.append("%s=%s" % (v["target"], v.get("bind", {}).get("create_host_path")))
print(" ".join(sorted(out)))
' 2>&1)"
    if [[ "${flags}" == "/run/host-services/ssh-auth.sock=False /run/vde-ssh.sock=False" ]]; then
        test_pass "compose config reports create_host_path=false for both targets"
    else
        test_fail "compose config" "got [${flags}]"
    fi
fi

# --- 4. behaviour: Compose refuses a missing source and creates nothing --------
test_start "behaviour: compose refuses a missing agent socket and creates no directory"
typeset image=""
if ! docker info >/dev/null 2>&1; then
    test_skip "behaviour" "no Docker daemon"
else
    image="$(docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -vF '<none>' | head -n 1)"
    if [[ -z "${image}" ]]; then
        test_skip "behaviour" "no local image to build a throwaway container from"
    else
        typeset scratch; scratch="$(mktemp -d)"
        typeset missing="${scratch}/agent.sock"
        # The fixture lifts the REAL mount block out of the language template (so
        # it follows the template) and points it at an absent source. It only runs
        # when check 1 found the template sound: a short-form block would make
        # Docker create a root-owned directory in the scratch dir, which is the
        # very hazard under test and cannot be cleaned up without root.
        typeset -a tlines=("${(@f)$(<templates/compose-language.yml)}")
        typeset -i at=${tlines[(i)*target: /run/vde-ssh.sock]}
        if [[ -n "$(socket_mount_problems templates/compose-language.yml)" ]] || (( at < 3 || at > ${#tlines} )); then
            test_skip "behaviour" "template is not long-form (check 1 reports it); not risking a root-owned directory"
        else
            {
                print -r -- "name: vde-socket-fixture-$$"
                print -r -- "services:"
                print -r -- "  probe:"
                print -r -- "    image: ${image}"
                print -r -- "    volumes:"
                print -r -- "${(F)tlines[at-2,at+2]}"
            } > "${scratch}/compose.yml"
            typeset out rc=0
            out="$(VDE_HOST_SSH_AUTH_SOCK="${missing}" docker compose -f "${scratch}/compose.yml" create 2>&1)" || rc=$?
            docker compose -f "${scratch}/compose.yml" down --remove-orphans >/dev/null 2>&1
            if (( rc != 0 )) && [[ ! -e "${missing}" ]]; then
                test_pass "compose refused (rc=${rc}) and ${missing:t} was not created"
            else
                test_fail "behaviour" "rc=${rc}, source exists=$([[ -e ${missing} ]] && echo yes || echo no), output: ${out[1,160]}"
            fi
        fi
        rm -rf -- "${scratch}"
    fi
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}  Skipped: ${TESTS_SKIPPED}"
(( TESTS_FAILED == 0 ))
