#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# Unit tests for the test-run scratch Projects base (lib/vde-test-env).
#
# Test and gate runs use their own scratch Projects base (VDE_PROJECTS_DIR), never the caller's value
# and never a value read from .env. Case A exercises the helper directly. Case B runs each entry point
# from a fixture tree that holds a copy of the real script. Case C loads a copy of the real behave
# environment module. Case D checks that every suite carries the prelude.
#
# External commands run under timeout 120. Scratch state lives under one mktemp directory that an EXIT
# trap removes, and HOME is a scratch directory too.

typeset REPO="${0:A:h:h:h}"
typeset HELPER="${REPO}/lib/vde-test-env"
typeset REAL_RUNNER="${REPO}/tests/run-sovereign-tests.zsh"
typeset REAL_COV="${REPO}/bin/coverage.zsh"
typeset REAL_HOOK="${REPO}/githooks/proof-of-life-hook.zsh"
typeset REAL_ENV_PY="${REPO}/tests/features/environment.py"

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
typeset -i TEST_NO=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$((TESTS_PASSED + 1)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; TESTS_FAILED=$((TESTS_FAILED + 1)); return 0; }

# check <description> <condition> [detail]
# Numbers each check, evaluates the condition string, and reports PASS or FAIL.
check() {
    typeset desc="$1" cond="$2" detail="${3:-}"
    TEST_NO+=1
    test_start "${TEST_NO}: ${desc}"
    if eval "${cond}"; then
        test_pass "${desc}"
    else
        test_fail "${desc}" "${detail}"
    fi
}

# tenv_nap: a 0.1 s zsh-native pause for the polling loops (zselect -t counts hundredths of a second).
zmodload zsh/zselect 2>/dev/null
tenv_nap() { zselect -t 10 2>/dev/null || true; }

typeset SCRATCH
SCRATCH=$(timeout 120 mktemp -d "${TMPDIR:-/tmp}/test-env-isolation.XXXXXX") || { echo "mktemp failed"; exit 1; }
SCRATCH="${SCRATCH:A}"
trap 'rm -rf -- "${SCRATCH}"' EXIT

export HOME="${SCRATCH}/home"
export TMPDIR="${SCRATCH}/tmp"
mkdir -p -- "${HOME}" "${TMPDIR}"

# Suite prelude: source the helper and enter the scratch Projects base.
typeset _ISO_HELPER="${REPO}/lib/vde-test-env"
[[ -f "${_ISO_HELPER}" ]] && source "${_ISO_HELPER}" && vde_test_env_enter

typeset SENT="${SCRATCH}/sentinel"
typeset DOTENV_VAL="${SCRATCH}/dotenv-value"
typeset STUBS="${SCRATCH}/stubs"
mkdir -p -- "${STUBS}"

# Stub kcov: logs each call to $STUB_LOG. A non-merge call takes the first non-option argument as the
# output directory, writes an index.html and a data file there, then runs the remaining arguments.
cat > "${STUBS}/kcov" <<'EOF'
#!/usr/bin/env zsh
print -r -- "$*" >> "${STUB_LOG}"
if [[ "${1}" == "--merge" ]]; then
    mkdir -p "${2}" || exit 1
    typeset src f
    for src in "${@[3,-1]}"; do
        for f in "${src}"/data-*(N); do
            cp -- "${f}" "${2}/" || exit 1
        done
    done
    print -r -- '<html>covered">50.0<</html>' > "${2}/index.html"
    exit 0
fi
typeset out="" arg
typeset -a cmd
for arg in "$@"; do
    if [[ -z "${out}" ]]; then
        [[ "${arg}" == --* ]] && continue
        out="${arg}"
    else
        cmd+=("${arg}")
    fi
done
mkdir -p "${out}" || exit 1
print -r -- "${out:t}" > "${out}/data-${out:t}"
print -r -- '<html>covered">50.0<</html>' > "${out}/index.html"
"${cmd[@]}"
exit $?
EOF
chmod +x "${STUBS}/kcov"

# has_line <text> <line>: the text contains that exact line
has_line() { print -r -- "$1" | timeout 120 grep -qxF -- "$2"; }

# kv <key>: the value after "<key>=" in the last helper run's output
kv() { print -r -- "${ZRUN_OUT}" | timeout 120 sed -n "s/^${1}=//p" | timeout 120 head -n 1; }

typeset ZRUN_OUT="" ZRUN_RC=0 ZRUN_OK=0 ZRUN_VALUE=""

# run_helper <zsh body> [VAR=value ...]
# Runs the body in a fresh zsh that sources the helper first. The environment starts without
# VDE_PROJECTS_DIR. ZRUN_OK is 1 only when the body reached its final "done=yes" line.
run_helper() {
    typeset body="$1"
    shift
    ZRUN_OUT=$(env -u VDE_PROJECTS_DIR HELPER_PATH="${HELPER}" HOME="${HOME}" TMPDIR="${TMPDIR}" "$@" timeout 120 zsh -c "source \"\${HELPER_PATH}\" || exit 90
${body}
print -r -- done=yes" </dev/null 2>&1)
    ZRUN_RC=$?
    ZRUN_OK=0
    if [[ ${ZRUN_RC} == 0 ]] && has_line "${ZRUN_OUT}" done=yes; then
        ZRUN_OK=1
    fi
}

#-------------------------------------------------------------------------------
# Case A: the helper contract

check "helper: lib/vde-test-env exists and is tracked by git" \
    '[[ -f "${HELPER}" ]] && timeout 120 env -u GIT_DIR -u GIT_INDEX_FILE -u GIT_WORK_TREE git -C "${REPO}" ls-files --error-unmatch -- lib/vde-test-env >/dev/null 2>&1' \
    "helper missing or not tracked"

run_helper 'vde_test_env_enter || print -r -- enter=failed
typeset _v="${VDE_PROJECTS_DIR-}"
print -r -- "value=${_v}"
[[ -d "${_v}" && ! -L "${_v}" ]] && print -r -- isdir=yes
[[ -w "${_v}" ]] && print -r -- writable=yes
[[ "${_v:t}" == vde-test-projects.* ]] && print -r -- prefix=yes' "VDE_PROJECTS_DIR=${SENT}"
ZRUN_VALUE=$(kv value)

check "enter: VDE_PROJECTS_DIR differs from the caller's sentinel" \
    '[[ ${ZRUN_OK} == 1 && -n "${ZRUN_VALUE}" && "${ZRUN_VALUE}" != "${SENT}" ]]' \
    "rc=${ZRUN_RC} out=${ZRUN_OUT}"
check "enter: VDE_PROJECTS_DIR names an existing real directory" \
    '[[ ${ZRUN_OK} == 1 && "$(kv isdir)" == yes ]]' "out=${ZRUN_OUT}"
check "enter: the directory basename starts with vde-test-projects." \
    '[[ ${ZRUN_OK} == 1 && "$(kv prefix)" == yes ]]' "out=${ZRUN_OUT}"
check "enter: the directory is writable" \
    '[[ ${ZRUN_OK} == 1 && "$(kv writable)" == yes ]]' "out=${ZRUN_OUT}"

run_helper 'vde_test_env_enter || print -r -- enter=failed
typeset _v="${VDE_PROJECTS_DIR-}"
vde_test_env_leave
print -r -- "rc=$?"
print -r -- "after=${VDE_PROJECTS_DIR-UNSET}"
[[ "${_v:t}" == vde-test-projects.* && ! -e "${_v}" ]] && print -r -- gone=yes' "VDE_PROJECTS_DIR=${SENT}"

check "leave: VDE_PROJECTS_DIR is restored to the sentinel exactly" \
    '[[ ${ZRUN_OK} == 1 && "$(kv after)" == "${SENT}" ]]' "out=${ZRUN_OUT}"
check "leave: the scratch directory it created is removed" \
    '[[ ${ZRUN_OK} == 1 && "$(kv gone)" == yes && "$(kv rc)" == 0 ]]' "out=${ZRUN_OUT}"

run_helper 'vde_test_env_enter || print -r -- enter=failed
vde_test_env_leave
print -r -- "after=${VDE_PROJECTS_DIR-UNSET}"'

check "leave: when the variable was unset before enter, it is unset after leave" \
    '[[ ${ZRUN_OK} == 1 && "$(kv after)" == UNSET ]]' "out=${ZRUN_OUT}"

# The child gets a private TMPDIR, so the count sees only what the child's two enters create.
typeset ENTER2_TMP
ENTER2_TMP=$(timeout 120 mktemp -d "${SCRATCH}/enter-twice.XXXXXX") || { echo "mktemp failed"; exit 1; }
run_helper 'vde_test_env_enter || print -r -- enter1=failed
typeset _a="${VDE_PROJECTS_DIR-}"
vde_test_env_enter || print -r -- enter2=failed
typeset _b="${VDE_PROJECTS_DIR-}"
print -r -- "first=${_a}"
print -r -- "second=${_b}"
typeset -a _dirs=( "${TMPDIR}"/vde-test-projects.*(N/) )
print -r -- "count=${#_dirs}"' "VDE_PROJECTS_DIR=${SENT}" "TMPDIR=${ENTER2_TMP}"

check "enter twice: the second enter leaves the value unchanged" \
    '[[ ${ZRUN_OK} == 1 && -n "$(kv first)" && "$(kv first)" == "$(kv second)" ]]' "out=${ZRUN_OUT}"
check "enter twice: only one scratch directory is created" \
    '[[ ${ZRUN_OK} == 1 && "$(kv count)" == 1 && -n "$(kv first)" && "$(kv first)" == "$(kv second)" ]]' "out=${ZRUN_OUT}"

run_helper 'vde_test_env_leave
print -r -- "rc=$?"
print -r -- "after=${VDE_PROJECTS_DIR-UNSET}"' "VDE_PROJECTS_DIR=${SENT}"

check "leave without enter: returns 0 and changes nothing" \
    '[[ ${ZRUN_OK} == 1 && "$(kv rc)" == 0 && "$(kv after)" == "${SENT}" ]]' "out=${ZRUN_OUT}"

# Repointing VDE_PROJECTS_DIR after enter must not make leave remove an unrelated directory.
run_helper 'vde_test_env_enter || print -r -- enter=failed
typeset _other="${TMPDIR}/other-dir"
mkdir -p -- "${_other}"
export VDE_PROJECTS_DIR="${_other}"
vde_test_env_leave
print -r -- "rc=$?"
[[ -d "${_other}" ]] && print -r -- other=kept' "VDE_PROJECTS_DIR=${SENT}"

check "leave after repointing VDE_PROJECTS_DIR: a directory without the prefix is left alone" \
    '[[ ${ZRUN_OK} == 1 && "$(kv other)" == kept ]]' "out=${ZRUN_OUT}"

# SIGTERM: the shell is terminated while the scratch directory is in use.
typeset SIG_FILE="${SCRATCH}/sigterm.out"
typeset SIG_PID="" SIG_ZPID="" SIG_VALUE="" SIG_EXISTED=no SIG_GONE=no SIG_NEEDED_KILL=no
typeset _i
env -u VDE_PROJECTS_DIR HELPER_PATH="${HELPER}" HOME="${HOME}" TMPDIR="${TMPDIR}" SIG_FILE="${SIG_FILE}" \
    timeout 120 zsh -c 'source "${HELPER_PATH}" || exit 90
vde_test_env_enter
print -r -- "$$ ${VDE_PROJECTS_DIR-}" > "${SIG_FILE}"
zmodload zsh/zselect && zselect -t 3000' </dev/null >/dev/null 2>&1 &
SIG_PID=$!
for _i in {1..100}; do
    [[ -s "${SIG_FILE}" ]] && break
    tenv_nap
done
read -r SIG_ZPID SIG_VALUE < "${SIG_FILE}" 2>/dev/null
if [[ -n "${SIG_VALUE}" && -d "${SIG_VALUE}" ]]; then
    SIG_EXISTED=yes
fi
if [[ -n "${SIG_ZPID}" ]]; then
    kill -TERM "${SIG_ZPID}" 2>/dev/null
    for _i in {1..30}; do
        kill -0 "${SIG_ZPID}" 2>/dev/null || break
        tenv_nap
    done
    kill -0 "${SIG_ZPID}" 2>/dev/null && SIG_NEEDED_KILL=yes
    kill -KILL "${SIG_ZPID}" 2>/dev/null
fi
wait "${SIG_PID}" 2>/dev/null
if [[ "${SIG_VALUE:t}" == vde-test-projects.* && ! -e "${SIG_VALUE}" ]]; then
    SIG_GONE=yes
fi

check "sigterm: a scratch directory existed while the shell ran" \
    '[[ "${SIG_EXISTED}" == yes ]]' "value=${SIG_VALUE}"
check "sigterm: the scratch directory is removed after TERM" \
    '[[ "${SIG_GONE}" == yes ]]' "value=${SIG_VALUE}"
check "sigterm: the shell exits on TERM and does not resume (no KILL needed)" \
    '[[ "${SIG_NEEDED_KILL}" == no ]]' "needed_kill=${SIG_NEEDED_KILL}"

# An inherited active flag must not skip creating a scratch base.
run_helper 'vde_test_env_enter; print -r -- "dir=${VDE_PROJECTS_DIR-}"
print -r -- done=yes' "_VDE_TENV_ACTIVE=1" "VDE_PROJECTS_DIR=${SENT}"
check "inherited active flag: enter still creates a scratch base" \
    '[[ ${ZRUN_OK} == 1 && "$(kv dir):t" != x && "$(kv dir)" != "${SENT}" && "$(kv dir):t" == *vde-test-projects.* ]]' "out=${ZRUN_OUT}"

# Suites that install their own INT/TERM trap must also run the helper's leave.
typeset _ts
for _ts in projects-dir-safety set-projects-dir-move-safety vde-projects-dir-env-fallback vde-projects-base-resolver; do
    check "own trap chains the helper: ${_ts}" \
        'timeout 120 grep -q vde_test_env_leave "${REPO}/tests/unit/${_ts}.test.zsh"' "suite=${_ts}"
done

# Behave helper: static checks for the hardened cleanup.
typeset _ENVPY="${REPO}/tests/features/environment.py"
check "behave: caller setting captured before the .env loader" \
    'timeout 120 grep -q "_CALLER_PROJECTS_WAS" "${_ENVPY}"' ""
check "behave: SIGTERM removes the scratch base" \
    'timeout 120 grep -q "signal.signal" "${_ENVPY}"' ""
check "behave: removal errors reach stderr" \
    'timeout 120 grep -q "file=sys.stderr" "${_ENVPY}"' ""
check "behave: scratch path cleared after cleanup" \
    'timeout 120 grep -q "_projects_scratch_path = None" "${_ENVPY}"' ""

#-------------------------------------------------------------------------------
# Case B: entry points, each run from a fixture tree that holds a copy of the real script

# make_fixture <name>: sets FX_ROOT to a fresh fixture root with a lib symlink and a .env
make_fixture() {
    FX_ROOT="${SCRATCH}/fx/$1"
    mkdir -p -- "${FX_ROOT}"
    ln -sfn -- "${REPO}/lib" "${FX_ROOT}/lib"
    print -r -- "VDE_PROJECTS_DIR=${DOTENV_VAL}" > "${FX_ROOT}/.env"
}

# write_probe <file>: a unit suite that records VDE_PROJECTS_DIR and whether it is a directory
write_probe() {
    cat > "$1" <<'PROBE'
#!/usr/bin/env zsh
typeset _p="${VDE_PROJECTS_DIR-UNSET}"
typeset _d=no
[[ -d "${_p}" ]] && _d=yes
print -r -- "${_p}" > "${PROBE_FILE}"
print -r -- "${_d}" >> "${PROBE_FILE}"
exit 0
PROBE
    chmod +x -- "$1"
}

# read_probe <file>: sets PROBE_VAL and PROBE_DIR from the probe output
read_probe() {
    PROBE_VAL=$(timeout 120 sed -n 1p "$1" 2>/dev/null)
    PROBE_DIR=$(timeout 120 sed -n 2p "$1" 2>/dev/null)
}

# entry_checks <label>: the six checks every runnable entry point must pass
entry_checks() {
    typeset label="$1"
    check "${label}: the probe ran and recorded a value" '[[ -n "${PROBE_VAL}" ]]' "probe value: ${PROBE_VAL}"
    check "${label}: during the run VDE_PROJECTS_DIR was an existing directory" '[[ "${PROBE_DIR}" == yes ]]' "dir flag: ${PROBE_DIR}"
    check "${label}: during the run VDE_PROJECTS_DIR was not the caller's sentinel" '[[ -n "${PROBE_VAL}" && "${PROBE_VAL}" != "${SENT}" ]]' "value: ${PROBE_VAL}"
    check "${label}: during the run VDE_PROJECTS_DIR was not the value from .env" '[[ -n "${PROBE_VAL}" && "${PROBE_VAL}" != "${DOTENV_VAL}" ]]' "value: ${PROBE_VAL}"
    check "${label}: during the run VDE_PROJECTS_DIR had the vde-test-projects. prefix" '[[ "${PROBE_VAL:t}" == vde-test-projects.* ]]' "value: ${PROBE_VAL}"
    check "${label}: the scratch directory was removed after the run" '[[ "${PROBE_VAL:t}" == vde-test-projects.* && ! -e "${PROBE_VAL}" ]]' "value: ${PROBE_VAL}"
}

# B9: the unit runner
make_fixture runner
R9="${FX_ROOT}"
mkdir -p -- "${R9}/bin" "${R9}/tests/unit"
cp -- "${REAL_RUNNER}" "${R9}/tests/run-sovereign-tests.zsh"
print -r -- '#!/usr/bin/env zsh' > "${R9}/bin/vde-enforce-uap.zsh"
print -r -- 'exit 0' >> "${R9}/bin/vde-enforce-uap.zsh"
chmod +x -- "${R9}/bin/vde-enforce-uap.zsh"
: > "${R9}/tests/ci-unit-exclusions.txt"
write_probe "${R9}/tests/unit/probe.test.zsh"
typeset R9_PFILE="${SCRATCH}/probe-runner.out"
( cd "${R9}" && timeout 120 env HOME="${HOME}" TMPDIR="${TMPDIR}" VDE_PROJECTS_DIR="${SENT}" PROBE_FILE="${R9_PFILE}" \
    zsh "${R9}/tests/run-sovereign-tests.zsh" </dev/null >/dev/null 2>&1 )
read_probe "${R9_PFILE}"
entry_checks "runner"

# B10: the coverage script, with a stub kcov and the probe as the only unit suite
make_fixture coverage
R10="${FX_ROOT}"
mkdir -p -- "${R10}/bin" "${R10}/tests/unit" "${R10}/tests/integration"
cp -- "${REAL_COV}" "${R10}/bin/coverage.zsh"
chmod +x -- "${R10}/bin/coverage.zsh"
write_probe "${R10}/tests/unit/probe.test.zsh"
typeset R10_PFILE="${SCRATCH}/probe-coverage.out"
( cd "${R10}" && timeout 120 env HOME="${HOME}" TMPDIR="${TMPDIR}" PATH="${STUBS}:${PATH}" \
    STUB_LOG="${SCRATCH}/kcov-coverage.log" VDE_PROJECTS_DIR="${SENT}" PROBE_FILE="${R10_PFILE}" \
    ./bin/coverage.zsh unit </dev/null >/dev/null 2>&1 )
read_probe "${R10_PFILE}"
entry_checks "coverage"

# B11: the proof-of-life pre-push hook, with a stub python3 that records the value and exits 0
make_fixture hook
R11="${FX_ROOT}"
mkdir -p -- "${R11}/githooks" "${R11}/bin" "${SCRATCH}/hook-stubs"
cp -- "${REAL_HOOK}" "${R11}/githooks/proof-of-life-hook.zsh"
print -r -- '#!/usr/bin/env zsh' > "${R11}/bin/vde-enforce-uap.zsh"
print -r -- 'exit 0' >> "${R11}/bin/vde-enforce-uap.zsh"
chmod +x -- "${R11}/bin/vde-enforce-uap.zsh"
cat > "${SCRATCH}/hook-stubs/python3" <<'PY3'
#!/usr/bin/env zsh
typeset _p="${VDE_PROJECTS_DIR-UNSET}"
typeset _d=no
[[ -d "${_p}" ]] && _d=yes
print -r -- "${_p}" > "${PROBE_FILE}"
print -r -- "${_d}" >> "${PROBE_FILE}"
exit 0
PY3
chmod +x -- "${SCRATCH}/hook-stubs/python3"
( cd "${R11}" && timeout 120 env -u GIT_DIR -u GIT_INDEX_FILE -u GIT_WORK_TREE git -C "${R11}" init -q >/dev/null 2>&1 )
typeset R11_PFILE="${SCRATCH}/probe-hook.out"
( cd "${R11}" && timeout 120 env HOME="${HOME}" TMPDIR="${TMPDIR}" PATH="${SCRATCH}/hook-stubs:${PATH}" \
    VDE_PROJECTS_DIR="${SENT}" PROBE_FILE="${R11_PFILE}" \
    zsh "${R11}/githooks/proof-of-life-hook.zsh" </dev/null >/dev/null 2>&1 )
read_probe "${R11_PFILE}"
entry_checks "hook"

#-------------------------------------------------------------------------------
# Case C: the behave hooks, loaded by path from a copy of the real environment module

typeset BROOT="${SCRATCH}/behave"
mkdir -p -- "${BROOT}/tests/features/steps" "${BROOT}/bin-stubs"
cp -- "${REAL_ENV_PY}" "${BROOT}/tests/features/environment.py"
print -r -- "VDE_ROOT = '${BROOT}'" > "${BROOT}/tests/features/steps/config.py"
print -r -- "VDE_SSH_DIR = '${BROOT}/ssh'" >> "${BROOT}/tests/features/steps/config.py"
print -r -- "VDE_PROJECTS_DIR=${DOTENV_VAL}" > "${BROOT}/.env"
print -r -- '#!/usr/bin/env zsh' > "${BROOT}/bin-stubs/docker"
print -r -- 'exit 0' >> "${BROOT}/bin-stubs/docker"
chmod +x -- "${BROOT}/bin-stubs/docker"

typeset PY_SNIP
PY_SNIP=$(cat <<'PY'
import importlib.util, os, sys, types
env_path, sentinel, dotenv = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ["VDE_PROJECTS_DIR"] = sentinel
spec = importlib.util.spec_from_file_location("environment_under_test", env_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
results = []
def run_case(label, before):
    if before is None:
        os.environ.pop("VDE_PROJECTS_DIR", None)
    else:
        os.environ["VDE_PROJECTS_DIR"] = before
    ctx = types.SimpleNamespace()
    mod.before_all(ctx)
    during = os.environ.get("VDE_PROJECTS_DIR", "")
    fresh = bool(during) and os.path.isdir(during) and os.path.basename(during).startswith("vde-test-projects.") and during not in (sentinel, dotenv)
    mod.after_all(ctx)
    if before is None:
        restored = "VDE_PROJECTS_DIR" not in os.environ
    else:
        restored = os.environ.get("VDE_PROJECTS_DIR") == before
    gone = bool(during) and not os.path.exists(during)
    print(label, "fresh=" + str(fresh), "restored=" + str(restored), "gone=" + str(gone))
    results.append(fresh and restored and gone)
run_case("sentinel", sentinel)
run_case("unset", None)
sys.exit(0 if results and all(results) else 1)
PY
)

typeset C12_OUT="" C12_RC=0
C12_OUT=$(env HOME="${HOME}" TMPDIR="${TMPDIR}" PATH="${BROOT}/bin-stubs:${PATH}" \
    timeout 120 python3 -I -c "${PY_SNIP}" "${BROOT}/tests/features/environment.py" "${SENT}" "${DOTENV_VAL}" </dev/null 2>&1)
C12_RC=$?

check "behave: before_all gives a fresh scratch directory, after_all restores the value and removes it (set and unset cases)" \
    '[[ ${C12_RC} == 0 ]]' "rc=${C12_RC} out=${C12_OUT}"

#-------------------------------------------------------------------------------
# Case D: static wiring of every suite

typeset -a UNIT_FILES=( "${REPO}"/tests/unit/*.test.zsh(N) )
typeset -a INT_FILES=( "${REPO}"/tests/integration/*.test.zsh(N) )

check "static: at least 59 unit suites are present" '(( ${#UNIT_FILES} >= 59 ))' "found ${#UNIT_FILES}"
for F in "${UNIT_FILES[@]}"; do
    check "static: ${F:t} references lib/vde-test-env within its first 30 lines" \
        '[[ -f "${F}" ]] && timeout 120 head -n 30 -- "${F}" | timeout 120 grep -q "lib/vde-test-env"' \
        "${F:t} has no lib/vde-test-env line in its first 30 lines"
done

check "static: at least 3 integration suites are present" '(( ${#INT_FILES} >= 3 ))' "found ${#INT_FILES}"
for F in "${INT_FILES[@]}"; do
    check "static: ${F:t} references lib/vde-test-env within its first 30 lines" \
        '[[ -f "${F}" ]] && timeout 120 head -n 30 -- "${F}" | timeout 120 grep -q "lib/vde-test-env"' \
        "${F:t} has no lib/vde-test-env line in its first 30 lines"
done

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
