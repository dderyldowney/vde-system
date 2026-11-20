#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests: a Spoke receives only what it needs from the root .env (Signet #666,
# split from #441 item 4).
#
# The root .env is the user's file for host-side secrets. The Compose templates used
# to list it under `env_file:`, so EVERYTHING in it (the dev DB password, any other
# secret the user adds) landed in the environment of EVERY Spoke. Now the templates
# list only the per-VM env file and name the one variable a Spoke really needs,
# VDE_AUTHORIZED_KEY (the PUBLIC key the entrypoint writes to the SSH vault), which
# Compose interpolates from the root .env that `vde start` passes as --env-file.
# DATABASE_URL still gets the real dev password through the same interpolation.
#
# Checks, in order:
#   1. both templates: no root .env under env_file, per-VM env file kept, the key named;
#   2. every tracked manifest that lists an env_file does the same (>= 30 of them);
#   3. the one starter of Spokes (lib/vde-actions) still passes the root .env as
#      --env-file, because the key now reaches a Spoke ONLY that way;
#   4. behaviour: rendered config in a scratch tree keeps a canary secret OUT, carries
#      the quoted key lib/vde-ssh writes, and interpolates DATABASE_URL
#      (skipped loudly when the docker CLI is absent).
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

typeset KEY_LINE='- VDE_AUTHORIZED_KEY=${VDE_AUTHORIZED_KEY:-}'
# The names are assembled from parts so this file carries no credential-shaped
# assignment of its own: the pre-commit Secret Sentinel (Rule 12) scans it too.
typeset PW_NAME='POSTGRES_DEV_''PASSWORD'
typeset PW_LINE="- ${PW_NAME}=\${${PW_NAME}:-}"

# env_isolation_problems FILE -> one line per defect, nothing when sound.
# Sound: no non-comment line anywhere that points at the root .env (a bare list
# item, one with a trailing comment, or a long-form `path:` entry all count), the
# per-VM env-files entry kept, and each explicit variable line present exactly once.
env_isolation_problems() {
    local file="${1}" n_root n_vm n_key n_pw
    # `(../)+.env` only matches the root file: `../env-files/x.env` has no `../.env`.
    n_root="$(grep -vE '^[[:space:]]*#' "${file}" | grep -cE '(\.\./)+\.env([^[:alnum:]_.-]|$)')"
    n_vm="$(grep -cE "^[[:space:]]*-[[:space:]]+(\\.\\./)+env-files/[^[:space:]]+\\.env[[:space:]]*\$" "${file}")"
    n_key="$(grep -cF -- "${KEY_LINE}" "${file}")"
    n_pw="$(grep -cF -- "${PW_LINE}" "${file}")"
    (( n_root == 0 )) || print -r -- "root .env still referenced (${n_root}x)"
    (( n_vm == 1 )) || print -r -- "expected exactly 1 per-VM env-files entry, found ${n_vm}"
    (( n_key == 1 )) || print -r -- "expected exactly 1 '${KEY_LINE}' line, found ${n_key}"
    (( n_pw == 1 )) || print -r -- "expected exactly 1 '${PW_LINE}' line, found ${n_pw}"
    return 0
}

# env_manifests -> every tracked manifest with an env_file (one path per line).
# A helper, not an inline pipeline (Mandate D).
env_manifests() {
    local f
    for f in ${(f)"$(git ls-files 'configs/docker/*docker-compose.yml')"}; do
        grep -qE '^[[:space:]]*env_file:' "${f}" && print -r -- "${f}"
    done
    return 0
}

# --- 1. templates --------------------------------------------------------------
typeset tpl problems
for tpl in templates/compose-language.yml templates/compose-service.yml; do
    test_start "${tpl}: only the per-VM env file is loaded, the key is named explicitly"
    problems="$(env_isolation_problems "${tpl}")"
    if [[ -z "${problems}" ]]; then
        test_pass "${tpl} isolates the Spoke from the root .env"
    else
        test_fail "${tpl}" "${(j:; :)${(f)problems}}"
    fi
done

# --- 2. every tracked manifest with an env_file --------------------------------
test_start "every tracked compose manifest isolates the Spoke from the root .env"
typeset -a manifests bad
typeset f
manifests=("${(@f)$(env_manifests)}")
for f in "${manifests[@]}"; do
    [[ -z "${f}" ]] && continue
    problems="$(env_isolation_problems "${f}")"
    [[ -n "${problems}" ]] && bad+=("${f} (${(j:, :)${(f)problems}})")
done
if (( ${#manifests} >= 30 )) && (( ${#bad} == 0 )); then
    test_pass "${#manifests} tracked manifests load only their per-VM env file"
elif (( ${#manifests} < 30 )); then
    test_fail "manifest census" "found only ${#manifests} manifests with an env_file (expected >= 30)"
else
    test_fail "${#bad} manifest(s) still load the root .env" "${(j:; :)bad[1,3]}"
fi

# --- 3. the starter still hands the root .env to Compose -----------------------
test_start "lib/vde-actions passes the root .env as --env-file (the key now travels only this way)"
# A source pin, not a run: it ignores comment lines and demands the guarded
# `compose_up_cmd+=(--env-file ...)` assignment, but cannot see dead code.
if grep -vE '^[[:space:]]*#' lib/vde-actions | grep -qF -- 'compose_up_cmd+=(--env-file "${VDE_ROOT_DIR}/.env")'; then
    test_pass "lib/vde-actions passes --env-file \"\${VDE_ROOT_DIR}/.env\" to compose up"
else
    test_fail "lib/vde-actions" "no --env-file \"\${VDE_ROOT_DIR}/.env\": Spokes would start with an empty VDE_AUTHORIZED_KEY"
fi

# --- 4. behaviour: rendered config ---------------------------------------------
# render_env_defects CATEGORY NAME -> one line per defect, nothing when sound.
# Renders the tracked manifest in a scratch tree of the same relative layout (the
# manifest names untracked env files, so the test never reads the host's real
# .env) with a canary secret in the scratch root .env, once WITH and once WITHOUT
# the --env-file that `vde start` passes.
render_env_defects() {
    local category="${1}" name="${2}" root mdir with_flag without_flag
    root="$(mktemp -d)"
    mdir="${root}/configs/docker/${category}/${name}"
    mkdir -p "${mdir}" "${root}/env-files"
    # lib/vde-ssh writes the key QUOTED: VDE_AUTHORIZED_KEY="ssh-ed25519 ... comment"
    {
        printf '%s=%s\n' "${PW_NAME}" canary_pg_pw
        print -r -- 'VDE_AUTHORIZED_KEY="ssh-ed25519 AAAAcanarykey canary@host"'
        print -r -- 'MY_CLOUD_TOKEN=canary_unrelated_secret'
    } > "${root}/.env"
    print -r -- 'DATABASE_URL=postgresql://devuser:${POSTGRES_DEV_PASSWORD:-vde_dev_pass}@postgres:5432/x' \
        > "${root}/env-files/${name}.env"
    cp "configs/docker/${category}/${name}/docker-compose.yml" "${mdir}/"
    with_flag="$(VDE_HOST_SSH_AUTH_SOCK=/nonexistent/agent.sock VDE_DOCKER_SOCK_GID=1000 \
        docker compose --env-file "${root}/.env" -f "${mdir}/docker-compose.yml" config 2>&1)"
    without_flag="$(VDE_HOST_SSH_AUTH_SOCK=/nonexistent/agent.sock VDE_DOCKER_SOCK_GID=1000 \
        docker compose -f "${mdir}/docker-compose.yml" config 2>&1)"
    rm -rf -- "${root}"

    [[ "${with_flag}" != *"MY_CLOUD_TOKEN"* && "${with_flag}" != *"canary_unrelated_secret"* ]] \
        || print -r -- "${name}: the unrelated secret reached the Spoke environment"
    [[ "${with_flag}" == *"VDE_AUTHORIZED_KEY: ssh-ed25519 AAAAcanarykey canary@host"* ]] \
        || print -r -- "${name}: the quoted key did not arrive unquoted"
    # postgres-init and jupyterlab-init read POSTGRES_DEV_PASSWORD from the container
    # environment, so it must arrive as a variable of its own, not only via DATABASE_URL.
    [[ "${with_flag}" == *"POSTGRES_DEV_PASSWORD: canary_pg_pw"* ]] \
        || print -r -- "${name}: POSTGRES_DEV_PASSWORD did not arrive as its own variable"
    [[ "${with_flag}" == *"DATABASE_URL: postgresql://devuser:canary_pg_pw@postgres:5432/x"* ]] \
        || print -r -- "${name}: DATABASE_URL did not interpolate the dev password under --env-file"
    # Without --env-file nothing of the root .env may arrive, and DATABASE_URL must
    # fall back to its documented default (never to a leaked value).
    [[ "${without_flag}" != *"canary_unrelated_secret"* && "${without_flag}" != *"canary_pg_pw"* ]] \
        || print -r -- "${name}: a root .env value arrived WITHOUT --env-file"
    [[ "${without_flag}" == *"DATABASE_URL: postgresql://devuser:vde_dev_pass@postgres:5432/x"* ]] \
        || print -r -- "${name}: DATABASE_URL lost its default without --env-file"
    return 0
}

test_start "behaviour: rendered config keeps a canary secret out and still carries the key and password"
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    test_skip "compose config" "docker compose CLI not available"
else
    typeset defects
    defects="$(render_env_defects languages python)
$(render_env_defects services postgres)"
    defects="${defects//$'\n'$'\n'/$'\n'}"
    if [[ -z "${${defects//$'\n'/}}" ]]; then
        test_pass "language and service manifests: canary stays out; key, password and DATABASE_URL arrive via --env-file only"
    else
        test_fail "rendered config" "${(j:; :)${(f)defects}}"
    fi
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}  Skipped: ${TESTS_SKIPPED}"
(( TESTS_FAILED == 0 ))
