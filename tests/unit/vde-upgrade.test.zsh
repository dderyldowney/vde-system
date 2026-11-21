#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for `vde upgrade` (Signet #676): bin/vde-upgrade.zsh brings an install up to
# date with the latest of the branch it is on, and refuses, changing nothing, whenever it
# cannot do that safely.
#
# The REAL script is copied into a throwaway install, a real clone of a real bare "origin"
# on disk, and run there. Every assertion looks at the repository or at the script's own
# output AFTER a real run. No docker, no real HOME. Case 18 clones THIS repository; on a shallow
# checkout (CI) it first deepens that checkout, which needs the network.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
  export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# Fixture isolation (Signet #656): drop every GIT_* variable that selects a repository, its
# index, its objects or its namespace, and the ones that inject config or hooks.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

typeset SCRIPT_SRC="${VDE_ROOT_DIR}/bin/vde-upgrade.zsh"

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

# Colours are prompt escapes for print -P (STYLE_GUIDE.md); only on a terminal. Messages are
# escaped first, because print -P would otherwise read a % inside them as an escape.
if [[ -t 1 ]]; then
  typeset GREEN='%F{green}' RED='%F{red}' YELLOW='%F{yellow}' RESET='%f'
else
  typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { print -rP -- "${YELLOW}[TEST]${RESET} ${1//\%/%%}"; }
test_pass()  { print -rP -- "${GREEN}[PASS]${RESET} ${1//\%/%%}"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }
test_fail()  { print -rP -- "${RED}[FAIL]${RESET} ${1//\%/%%}: ${2//\%/%%}"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset TMP_ROOT
TMP_ROOT="$(mktemp -d)" || exit 1
trap 'rm -rf -- "${TMP_ROOT}"' EXIT
export HOME="${TMP_ROOT}/home"; mkdir -p "${HOME}"

typeset -g UP_OUT='' UP_RC=0

# ---------------------------------------------------------------------------
# Harness helpers
# ---------------------------------------------------------------------------

# make_fixture NAME -> builds ${TMP_ROOT}/NAME/{origin.git,seed,install}; origin has
# branches stable and develop; install is a clone of stable. Prints the fixture root.
make_fixture() {
  local f="${TMP_ROOT}/$1"
  mkdir -p "${f}"
  git init -q --bare -b stable "${f}/origin.git"
  git clone -q "${f}/origin.git" "${f}/seed" 2>/dev/null
  git -C "${f}/seed" checkout -q -b stable
  mkdir -p "${f}/seed/bin" "${f}/seed/docs/governance" "${f}/seed/configs/docker" "${f}/seed/configs/ssh"
  [[ -f "${SCRIPT_SRC}" ]] && cp "${SCRIPT_SRC}" "${f}/seed/bin/vde-upgrade.zsh"
  chmod +x "${f}/seed/bin/vde-upgrade.zsh" 2>/dev/null
  print -r -- "# VDE-SPEC 1.5.6 (The Sovereign Evolution)" > "${f}/seed/docs/governance/vde-spec.md"
  if [[ -z "${NO_DOCKERFILES:-}" ]]; then
    mkdir -p "${f}/seed/scripts/setup" "${f}/seed/lib"
    print -r -- 'FROM debian:bookworm-slim
COPY --chown=devuser:devuser configs/ssh/config.spoke /home/devuser/.ssh/config
COPY scripts/vde-entrypoint.zsh /usr/local/bin/vde-entrypoint.zsh' > "${f}/seed/configs/docker/vde-base.Dockerfile"
    print -r -- 'FROM vde-base:latest
COPY lib/ /vde/lib/
COPY scripts/setup/${VM_NAME}-init.zsh /vde/scripts/setup/' > "${f}/seed/configs/docker/vde-lang.Dockerfile"
    print -r -- "a" > "${f}/seed/scripts/vde-entrypoint.zsh"; print -r -- "a" > "${f}/seed/lib/common"
    print -r -- "a" > "${f}/seed/scripts/setup/python-init.zsh"; print -r -- "a" > "${f}/seed/configs/ssh/config.spoke" 2>/dev/null
  fi
  print -r -- '#!/usr/bin/env zsh
touch "${0:A:h:h}/.git/vde-cache-refreshed"' > "${f}/seed/bin/vde-rebuild-cache"
  chmod +x "${f}/seed/bin/vde-rebuild-cache"
  print -r -- "base" > "${f}/seed/file-a"
  print -r -- "base" > "${f}/seed/file-b"
  git -C "${f}/seed" add -A
  git -C "${f}/seed" commit -qm "1.5.6"
  git -C "${f}/seed" push -q origin stable 2>/dev/null
  git -C "${f}/seed" checkout -q -b develop
  git -C "${f}/seed" push -q origin develop 2>/dev/null
  git -C "${f}/seed" checkout -q stable
  git clone -q -b stable "${f}/origin.git" "${f}/install" 2>/dev/null
  print -r -- "${f}"
}

# publish FIXTURE BRANCH FILE CONTENT [VERSION] -> a new commit on origin/BRANCH
publish() {
  local f="$1" b="$2" file="$3" content="$4" ver="${5:-}"
  git -C "${f}/seed" checkout -q "${b}"
  mkdir -p "${f}/seed/${file:h}"
  print -r -- "${content}" > "${f}/seed/${file}"
  [[ -n "${ver}" ]] && print -r -- "# VDE-SPEC ${ver} (The Sovereign Evolution)" > "${f}/seed/docs/governance/vde-spec.md"
  git -C "${f}/seed" add -A
  git -C "${f}/seed" commit -qm "change ${file}"
  git -C "${f}/seed" push -q origin "${b}" 2>/dev/null
  git -C "${f}/seed" checkout -q stable
}

# run_up FIXTURE [CWD [ARGS...]] -> runs the install's own copy of the script; sets UP_OUT and UP_RC
run_up() {
  local f="$1" cwd="${2:-$1/install}" raw
  shift; (( $# > 0 )) && shift
  raw="$(cd "${cwd}" && zsh "${f}/install/bin/vde-upgrade.zsh" "$@" 2>&1; print -r -- "UPRC=$?")"
  UP_RC="${raw##*UPRC=}"
  UP_OUT="$(print -r -- "${raw%UPRC=*}")"
}

head_of() { git -C "$1/install" rev-parse HEAD; }
origin_head() { git -C "$1/origin.git" rev-parse "$2"; }

# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

test_case1_the_script_exists_and_is_executable() {
  test_start "1: bin/vde-upgrade.zsh exists, is executable and carries the shibboleth"
  [[ -x "${SCRIPT_SRC}" ]] && test_pass "case1a executable" || test_fail "case1a executable" "${SCRIPT_SRC} missing or not executable"
  grep -qE '^typeset _ZSH_PURE=\$\{\(%\):-%x\}$' "${SCRIPT_SRC}" 2>/dev/null \
    && test_pass "case1b shibboleth line present" || test_fail "case1b shibboleth line present" "not found"
  grep -qE '\bjq\b' "${SCRIPT_SRC}" 2>/dev/null \
    && test_fail "case1c Mandate G: no direct jq" "script mentions jq" || test_pass "case1c Mandate G: no direct jq"
}

test_case2_happy_path_fast_forwards_and_reports_versions() {
  test_start "2: a newer origin is fast-forwarded and the old and new versions are reported"
  local f; f="$(make_fixture c2)"
  publish "${f}" stable file-a "new" "1.5.7"
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 0 ]] && test_pass "case2a exits 0" || test_fail "case2a exits 0" "rc=${UP_RC} out=${UP_OUT}"
  [[ "$(head_of "${f}")" == "$(origin_head "${f}" stable)" ]] \
    && test_pass "case2b install HEAD is now origin/stable" || test_fail "case2b install HEAD is now origin/stable" "head=$(head_of "${f}")"
  [[ "$(cat "${f}/install/file-a")" == "new" ]] \
    && test_pass "case2c the working tree has the new content" || test_fail "case2c the working tree has the new content" "$(cat "${f}/install/file-a")"
  [[ "${UP_OUT}" == *"1.5.6"* && "${UP_OUT}" == *"1.5.7"* ]] \
    && test_pass "case2d output names the old and the new version" || test_fail "case2d output names the old and the new version" "out: ${UP_OUT}"
  [[ "$(git -C "${f}/install" log --format=%P -1 | wc -w)" == 1 ]] \
    && test_pass "case2e history stayed linear (no merge commit)" || test_fail "case2e history stayed linear (no merge commit)" "HEAD has several parents"
}

test_case3_already_up_to_date_is_a_no_op() {
  test_start "3: an install that is already current says so and changes nothing"
  local f; f="$(make_fixture c3)"
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case3a exits 0 and HEAD is unchanged" || test_fail "case3a exits 0 and HEAD is unchanged" "rc=${UP_RC}"
  [[ "${UP_OUT}" == *"up to date"* ]] \
    && test_pass "case3b says it is up to date" || test_fail "case3b says it is up to date" "out: ${UP_OUT}"
}

test_case4_dry_run_changes_nothing() {
  test_start "4: --dry-run reports what would change and leaves the install untouched"
  local f; f="$(make_fixture c4)"
  publish "${f}" stable file-a "new" "1.5.7"
  local before; before="$(head_of "${f}")"
  run_up "${f}" "${f}/install" --dry-run
  [[ "${UP_RC}" == 0 && "$(head_of "${f}")" == "${before}" && "$(cat "${f}/install/file-a")" == "base" ]] \
    && test_pass "case4a HEAD and files unchanged, exit 0" || test_fail "case4a HEAD and files unchanged, exit 0" "rc=${UP_RC} head moved or file changed"
  [[ "${UP_OUT}" == *"1.5.7"* && "${UP_OUT}" == *[Dd]"ry run"* ]] \
    && test_pass "case4b names the version it would install and says it is a dry run" || test_fail "case4b names the version it would install and says it is a dry run" "out: ${UP_OUT}"
}

test_case5_it_follows_the_branch_you_are_on() {
  test_start "5: an install on develop pulls develop, not stable"
  local f; f="$(make_fixture c5)"
  git -C "${f}/install" checkout -q develop
  publish "${f}" develop file-b "dev-change"
  publish "${f}" stable file-a "stable-change"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(cat "${f}/install/file-b")" == "dev-change" && "$(cat "${f}/install/file-a")" == "base" ]] \
    && test_pass "case5a develop's change arrived, stable's did not" || test_fail "case5a develop's change arrived, stable's did not" "rc=${UP_RC} b=$(cat "${f}/install/file-b") a=$(cat "${f}/install/file-a")"
  [[ "$(git -C "${f}/install" branch --show-current)" == develop ]] \
    && test_pass "case5b still on develop" || test_fail "case5b still on develop" "branch=$(git -C "${f}/install" branch --show-current)"
}

test_case6_detached_head_is_refused() {
  test_start "6: a detached HEAD is refused and nothing changes"
  local f; f="$(make_fixture c6)"
  publish "${f}" stable file-a "new" "1.5.7"
  git -C "${f}/install" checkout -q --detach
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 3 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case6a exits 3 (cannot be updated) and HEAD is unchanged" || test_fail "case6a exits 3 (cannot be updated) and HEAD is unchanged" "rc=${UP_RC}"
  [[ "${UP_OUT}" == *"detached"* ]] \
    && test_pass "case6b the message says why" || test_fail "case6b the message says why" "out: ${UP_OUT}"
}

test_case7_a_diverged_branch_is_refused() {
  test_start "7: local commits plus new upstream commits (diverged) are refused; history is never rewritten"
  local f; f="$(make_fixture c7)"
  print -r -- "mine" > "${f}/install/local-file"
  git -C "${f}/install" add -A; git -C "${f}/install" commit -qm "local work"
  publish "${f}" stable file-a "new" "1.5.7"
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(head_of "${f}")" == "${before}" && -f "${f}/install/local-file" ]] \
    && test_pass "case7a exits 13 (drift), HEAD and local commit intact" || test_fail "case7a exits 13 (drift), HEAD and local commit intact" "rc=${UP_RC}"
  [[ "${UP_OUT}" == *"diverged"* ]] \
    && test_pass "case7b the message says diverged" || test_fail "case7b the message says diverged" "out: ${UP_OUT}"
}

test_case8_local_commits_ahead_of_origin_are_not_an_error() {
  test_start "8: being AHEAD of origin (nothing new upstream) is not an upgrade and not a failure"
  local f; f="$(make_fixture c8)"
  print -r -- "mine" > "${f}/install/local-file"
  git -C "${f}/install" add -A; git -C "${f}/install" commit -qm "local work"
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case8a exits 0, HEAD unchanged" || test_fail "case8a exits 0, HEAD unchanged" "rc=${UP_RC} out=${UP_OUT}"
}

test_case9_local_edits_that_the_update_would_overwrite_are_refused() {
  test_start "9: a local edit to a file the update also changes is refused, and the edit survives"
  local f; f="$(make_fixture c9)"
  publish "${f}" stable file-a "new" "1.5.7"
  print -r -- "my precious edit" > "${f}/install/file-a"
  local before; before="$(head_of "${f}")"
  run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(head_of "${f}")" == "${before}" && "$(cat "${f}/install/file-a")" == "my precious edit" ]] \
    && test_pass "case9a exits 13, HEAD unchanged, the edit survives" || test_fail "case9a exits 13, HEAD unchanged, the edit survives" "rc=${UP_RC}"
  [[ "${UP_OUT}" == *"file-a"* ]] \
    && test_pass "case9b the conflicting file is named" || test_fail "case9b the conflicting file is named" "out: ${UP_OUT}"
}

test_case10_unrelated_local_edits_are_kept() {
  test_start "10: a local edit to a file the update does NOT touch is preserved and the upgrade proceeds"
  local f; f="$(make_fixture c10)"
  publish "${f}" stable file-a "new" "1.5.7"
  print -r -- "my edit to b" > "${f}/install/file-b"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(cat "${f}/install/file-a")" == "new" && "$(cat "${f}/install/file-b")" == "my edit to b" ]] \
    && test_pass "case10a upgraded, and the unrelated edit survives" || test_fail "case10a upgraded, and the unrelated edit survives" "rc=${UP_RC} a=$(cat "${f}/install/file-a") b=$(cat "${f}/install/file-b")"
}

test_case11_no_origin_and_no_remote_branch_are_refused() {
  test_start "11: no origin remote, and a branch origin does not have, are refused with a reason"
  local f; f="$(make_fixture c11)"
  git -C "${f}/install" checkout -q -b mine-only
  run_up "${f}"
  [[ "${UP_RC}" == 3 && "${UP_OUT}" == *"mine-only"* ]] \
    && test_pass "case11a a branch origin lacks is refused and named" || test_fail "case11a a branch origin lacks is refused and named" "rc=${UP_RC} out=${UP_OUT}"
  git -C "${f}/install" checkout -q stable
  git -C "${f}/install" remote remove origin
  run_up "${f}"
  [[ "${UP_RC}" == 3 && "${UP_OUT}" == *"origin"* ]] \
    && test_pass "case11b no origin remote is refused and the message names origin" || test_fail "case11b no origin remote is refused and the message names origin" "rc=${UP_RC} out=${UP_OUT}"
}

test_case12_an_install_that_is_not_a_git_checkout_is_refused() {
  test_start "12: a copy of the tree with no .git (a tarball) is refused with advice"
  local f="${TMP_ROOT}/c12"
  mkdir -p "${f}/install/bin"
  [[ -z "$(git -C "${f}" rev-parse --show-toplevel 2>/dev/null)" ]] || { test_fail "case12 fixture" "the scratch directory is inside a git repository"; return }
  [[ -f "${SCRIPT_SRC}" ]] && cp "${SCRIPT_SRC}" "${f}/install/bin/vde-upgrade.zsh"
  run_up "${f}"
  [[ "${UP_RC}" == 3 && "${UP_OUT}" == *"not a git checkout"* ]] \
    && test_pass "case12a exits 3 and says it is not a git checkout" || test_fail "case12a exits 3 and says it is not a git checkout" "rc=${UP_RC} out=${UP_OUT}"
}

test_case13_it_works_from_any_directory() {
  test_start "13: run from an unrelated directory, it still upgrades the install the script lives in"
  local f; f="$(make_fixture c13)"
  publish "${f}" stable file-a "new" "1.5.7"
  local elsewhere="${TMP_ROOT}/elsewhere"; mkdir -p "${elsewhere}"
  run_up "${f}" "${elsewhere}"
  [[ "${UP_RC}" == 0 && "$(cat "${f}/install/file-a")" == "new" ]] \
    && test_pass "case13a upgraded from another cwd" || test_fail "case13a upgraded from another cwd" "rc=${UP_RC} out=${UP_OUT}"
}

test_case14_the_script_can_upgrade_itself() {
  test_start "14: an update that rewrites bin/vde-upgrade.zsh itself still finishes cleanly"
  local f; f="$(make_fixture c14)"
  publish "${f}" stable bin/vde-upgrade.zsh "$(cat "${f}/seed/bin/vde-upgrade.zsh")
# a changed line, so this commit rewrites the very script that is running" "1.5.7"
  [[ "$(head_of "${f}")" != "$(origin_head "${f}" stable)" ]] \
    && test_pass "case14pre origin really is ahead before the run (the update changes the script)" || test_fail "case14pre origin really is ahead before the run" "origin did not advance"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(head_of "${f}")" == "$(origin_head "${f}" stable)" ]] \
    && test_pass "case14a exit 0 and fast-forwarded although the script was replaced mid-run" || test_fail "case14a exit 0 and fast-forwarded although the script was replaced mid-run" "rc=${UP_RC} out=${UP_OUT}"
}

test_case15_rebuild_guidance_separates_base_from_spokes() {
  test_start "15: after an upgrade the advice says WHICH image to rebuild: base first, only Spokes, or nothing"
  local f
  f="$(make_fixture c15a)"; publish "${f}" stable scripts/vde-entrypoint.zsh "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR BASE IMAGE"* && "${UP_OUT}" == *"vde rebuild base <spoke>"* && "${UP_OUT}" == *"scripts/vde-entrypoint.zsh"* ]] \
    && test_pass "case15a a file baked into vde-base: base-first advice, naming the file" || test_fail "case15a a file baked into vde-base: base-first advice, naming the file" "out: ${UP_OUT}"
  f="$(make_fixture c15b)"; publish "${f}" stable configs/docker/vde-base.Dockerfile "FROM scratch" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR BASE IMAGE"* ]] \
    && test_pass "case15b the base Dockerfile itself: base-first advice" || test_fail "case15b the base Dockerfile itself: base-first advice" "out: ${UP_OUT}"
  f="$(make_fixture c15c)"; publish "${f}" stable lib/common "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR SPOKES"* && "${UP_OUT}" != *"vde rebuild base"* ]] \
    && test_pass "case15c a file only Spokes bake in (lib/): Spoke advice and NO base advice" || test_fail "case15c a file only Spokes bake in (lib/): Spoke advice and NO base advice" "out: ${UP_OUT}"
  f="$(make_fixture c15d)"; publish "${f}" stable scripts/setup/python-init.zsh "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR SPOKES"* ]] \
    && test_pass "case15d a Spoke hydration script: Spoke advice" || test_fail "case15d a Spoke hydration script: Spoke advice" "out: ${UP_OUT}"
  f="$(make_fixture c15e)"; publish "${f}" stable notes.txt "docs only" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"nothing to rebuild"* && "${UP_OUT}" != *"REBUILD"* ]] \
    && test_pass "case15e nothing image-related changed: nothing to rebuild" || test_fail "case15e nothing image-related changed: nothing to rebuild" "out: ${UP_OUT}"
  f="$(NO_DOCKERFILES=1 make_fixture c15f)"; publish "${f}" stable lib/common "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR BASE IMAGE"* ]] \
    && test_pass "case15f when the Dockerfiles cannot be read, it errs toward rebuilding the base" || test_fail "case15f when the Dockerfiles cannot be read, it errs toward rebuilding the base" "out: ${UP_OUT}"
}

test_case19_local_files_in_the_way_are_refused_not_overwritten() {
  test_start "19: ignored, untracked and staged local files the update would overwrite are refused, and kept"
  local f before
  f="$(make_fixture c19a)"; publish "${f}" stable keep.conf "upstream" "1.5.7"
  print -r -- "keep.conf" > "${f}/install/.git/info/exclude"; print -r -- "MY LOCAL SECRET" > "${f}/install/keep.conf"
  before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(cat "${f}/install/keep.conf")" == "MY LOCAL SECRET" && "$(head_of "${f}")" == "${before}" && "${UP_OUT}" == *"keep.conf"* ]] \
    && test_pass "case19a an IGNORED local file the update adds: exit 13, kept, named" || test_fail "case19a an IGNORED local file the update adds: exit 13, kept, named" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c19b)"; publish "${f}" stable notes.txt "upstream" "1.5.7"
  print -r -- "mine" > "${f}/install/notes.txt"; before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(cat "${f}/install/notes.txt")" == "mine" && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case19b an UNTRACKED local file the update adds: exit 13 and kept" || test_fail "case19b an UNTRACKED local file the update adds: exit 13 and kept" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c19c)"; publish "${f}" stable file-a "new" "1.5.7"
  print -r -- "staged edit" > "${f}/install/file-a"; git -C "${f}/install" add file-a; before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(git -C "${f}/install" show :file-a)" == "staged edit" && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case19c a STAGED edit the update touches: exit 13 and kept" || test_fail "case19c a STAGED edit the update touches: exit 13 and kept" "rc=${UP_RC}"
  f="$(make_fixture c19d)"; publish "${f}" stable file-a "new" "1.5.7"
  print -r -- "my edit" > "${f}/install/file-a"; run_up "${f}" "${f}/install" --dry-run
  [[ "${UP_RC}" == 13 && "$(cat "${f}/install/file-a")" == "my edit" ]] \
    && test_pass "case19d --dry-run reports the same clash instead of promising an upgrade" || test_fail "case19d --dry-run reports the same clash instead of promising an upgrade" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c19e)"; publish "${f}" stable keep.conf "upstream" "1.5.7"
  print -r -- "keep.conf" > "${f}/install/.git/info/exclude"; print -r -- "upstream" > "${f}/install/keep.conf"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(head_of "${f}")" == "$(origin_head "${f}" stable)" ]] \
    && test_pass "case19e an ignored file IDENTICAL to what the update brings loses nothing: upgrades" || test_fail "case19e an ignored file IDENTICAL to what the update brings loses nothing: upgrades" "rc=${UP_RC} out=${UP_OUT}"
}

test_case20_a_rename_upstream_still_names_your_edited_file() {
  test_start "20: upstream renames a file you edited: the refusal names it (rename detection must not hide it)"
  local f; f="$(make_fixture c20)"
  git -C "${f}/seed" mv file-b file-b-renamed; git -C "${f}/seed" commit -qm rename; git -C "${f}/seed" push -q origin stable 2>/dev/null
  print -r -- "my edit" > "${f}/install/file-b"
  run_up "${f}"
  [[ "${UP_RC}" == 13 && "${UP_OUT}" == *"changes files you have edited"* && "${UP_OUT}" == *"file-b"* && "$(cat "${f}/install/file-b")" == "my edit" ]] \
    && test_pass "case20a exit 13 from the script's OWN check (not git's fallback), the old path is named, the edit is kept" || test_fail "case20a exit 13 from the script's OWN check (not git's fallback), the old path is named, the edit is kept" "rc=${UP_RC} out=${UP_OUT}"
}

test_case16_usage_errors_exit_2() {
  test_start "16: --help exits 0; an unknown option exits 2 and changes nothing"
  local f; f="$(make_fixture c16)"
  local before; before="$(head_of "${f}")"
  run_up "${f}" "${f}/install" --help
  [[ "${UP_RC}" == 0 && "${UP_OUT}" == *"Usage: vde upgrade"* ]] \
    && test_pass "case16a --help exits 0 with usage" || test_fail "case16a --help exits 0 with usage" "rc=${UP_RC}"
  run_up "${f}" "${f}/install" --bogus
  [[ "${UP_RC}" == 2 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case16b unknown option exits 2" || test_fail "case16b unknown option exits 2" "rc=${UP_RC}"
}

test_case17_the_router_dispatches_upgrade() {
  test_start "17: bin/vde knows the command: a dispatch case, a help line and a documented script"
  grep -qE '^\s+upgrade\)' "${VDE_ROOT_DIR}/bin/vde" \
    && test_pass "case17a bin/vde has an upgrade) case" || test_fail "case17a bin/vde has an upgrade) case" "no upgrade) case in bin/vde"
  grep -q 'vde-upgrade.zsh' "${VDE_ROOT_DIR}/bin/vde" \
    && test_pass "case17b it dispatches bin/vde-upgrade.zsh" || test_fail "case17b it dispatches bin/vde-upgrade.zsh" "not referenced"
  grep -qE '^\s+upgrade\s' "${VDE_ROOT_DIR}/lib/vde-actions" \
    && test_pass "case17c vde help lists upgrade" || test_fail "case17c vde help lists upgrade" "no help line"
  grep -q 'vde-upgrade.zsh' "${VDE_ROOT_DIR}/docs/reference/scripts.md" \
    && test_pass "case17d docs/reference/scripts.md documents the script" || test_fail "case17d docs/reference/scripts.md documents the script" "not documented"
  grep -q 'vde upgrade' "${VDE_ROOT_DIR}/docs/reference/commands.md" \
    && test_pass "case17e docs/reference/commands.md documents the command" || test_fail "case17e docs/reference/commands.md documents the command" "not documented"
}

test_case18_real_history_five_commits_back_lands_on_the_tip() {
  test_start "18: this repository's real history: set an install 5 commits back, run the script, land exactly on the tip"
  local src="${VDE_ROOT_DIR}" f="${TMP_ROOT}/c18" tip old depth=5
  # CI checks out shallow. Deepen best-effort so there is history to step back through.
  if [[ "$(git -C "${src}" rev-parse --is-shallow-repository 2>/dev/null)" == true ]]; then
    git -C "${src}" fetch -q --deepen=20 origin 2>/dev/null
  fi
  tip="$(git -C "${src}" rev-parse HEAD)"
  old="$(git -C "${src}" rev-list --first-parent -n1 --skip=${depth} HEAD 2>/dev/null)"
  if [[ -z "${old}" ]]; then   # a very short history: step back as far as it goes
    depth=1
    old="$(git -C "${src}" rev-list --first-parent -n1 --skip=1 HEAD 2>/dev/null)"
  fi
  if [[ -z "${old}" ]]; then
    test_fail "case18a history to step back through" "this checkout has only one commit; cannot build the scenario"
    return
  fi
  mkdir -p "${f}"
  git clone -q --bare "${src}" "${f}/origin.git" 2>/dev/null
  git --git-dir="${f}/origin.git" branch -f under-test "${tip}"
  git clone -q --no-checkout "${f}/origin.git" "${f}/install" 2>/dev/null
  git -C "${f}/install" checkout -q -B under-test "${old}" 2>/dev/null
  git -C "${f}/install" branch -q --set-upstream-to=origin/under-test under-test 2>/dev/null
  # The branch that FIRST adds this script has no copy of it in older history. Put the script
  # under test there as an IGNORED file: a fast-forward may overwrite an ignored file, and the
  # script's own clash check ignores it. Once the script is in history this branch is skipped.
  if ! git -C "${f}/install" cat-file -e "HEAD:bin/vde-upgrade.zsh" 2>/dev/null; then
    mkdir -p "${f}/install/bin"
    print -r -- "bin/vde-upgrade.zsh" >> "${f}/install/.git/info/exclude"
    cp "${SCRIPT_SRC}" "${f}/install/bin/vde-upgrade.zsh"
  fi
  local behind; behind="$(git -C "${f}/install" rev-list --count "HEAD..${tip}")"
  (( behind >= 1 )) \
    && test_pass "case18a the install starts ${behind} commit(s) behind the tip (asked for ${depth} first-parent steps)" \
    || test_fail "case18a the install starts behind the tip" "behind=${behind}"
  run_up "${f}"
  [[ "${UP_RC}" == 0 ]] && test_pass "case18b the upgrade exits 0" || test_fail "case18b the upgrade exits 0" "rc=${UP_RC} out=${UP_OUT}"
  [[ "$(head_of "${f}")" == "${tip}" ]] \
    && test_pass "case18c HEAD is exactly the tip of the branch under test (${tip[1,8]})" || test_fail "case18c HEAD is exactly the tip of the branch under test" "head=$(head_of "${f}") tip=${tip}"
  [[ -z "$(git -C "${f}/install" diff --stat "${tip}")" ]] \
    && test_pass "case18d the working tree equals the tip, file for file" || test_fail "case18d the working tree equals the tip, file for file" "$(git -C "${f}/install" diff --stat "${tip}" | tail -3)"
  [[ -z "$(git -C "${f}/install" status --porcelain --untracked-files=no)" ]] \
    && test_pass "case18e no stray changes were left behind" || test_fail "case18e no stray changes were left behind" "$(git -C "${f}/install" status --short | head -3)"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "${UP_OUT}" == *"up to date"* ]] \
    && test_pass "case18f running it again is a clean no-op" || test_fail "case18f running it again is a clean no-op" "rc=${UP_RC} out=${UP_OUT}"
}

test_case21_a_running_rebuild_blocks_the_upgrade() {
  test_start "21: a live per-Spoke lock (a rebuild or start is running) blocks the upgrade; a dead one does not"
  local f before
  f="$(make_fixture c21a)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${f}/install/.locks/vms/vde-base.lock"; print -r -- "$$" > "${f}/install/.locks/vms/vde-base.lock/pid"
  before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 9 && "$(head_of "${f}")" == "${before}" && "${UP_OUT}" == *"vde-base"* ]] \
    && test_pass "case21a a live lock: exit 9, nothing changed, the lock is named" || test_fail "case21a a live lock: exit 9, nothing changed, the lock is named" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c21b)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${f}/install/.locks/vms/vde-base.lock"; print -r -- "999999" > "${f}/install/.locks/vms/vde-base.lock/pid"
  run_up "${f}"
  [[ "${UP_RC}" == 0 && "$(cat "${f}/install/file-a")" == "new" ]] \
    && test_pass "case21b a stale lock (dead pid) does not block" || test_fail "case21b a stale lock (dead pid) does not block" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c21c)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${f}/install/.locks/vms/vde-base.lock"; print -r -- "$$" > "${f}/install/.locks/vms/vde-base.lock/pid"
  run_up "${f}" "${f}/install" --dry-run
  [[ "${UP_RC}" == 0 ]] \
    && test_pass "case21c --dry-run is not blocked by a lock (it changes nothing)" || test_fail "case21c --dry-run is not blocked by a lock" "rc=${UP_RC}"
}

test_case22_the_registry_cache_is_refreshed_after_a_real_upgrade_only() {
  test_start "22: the registry cache refresh runs after an upgrade, not on a dry run or a refusal"
  local f
  f="$(make_fixture c22a)"; publish "${f}" stable file-a "new" "1.5.7"; run_up "${f}"
  [[ "${UP_RC}" == 0 && -f "${f}/install/.git/vde-cache-refreshed" && "${UP_OUT}" == *"cache refreshed"* ]] \
    && test_pass "case22a refreshed after a real upgrade, and it says so" || test_fail "case22a refreshed after a real upgrade, and it says so" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c22b)"; publish "${f}" stable file-a "new" "1.5.7"; run_up "${f}" "${f}/install" --dry-run
  [[ ! -f "${f}/install/.git/vde-cache-refreshed" ]] \
    && test_pass "case22b not on a dry run" || test_fail "case22b not on a dry run" "the cache script ran"
  f="$(make_fixture c22c)"; publish "${f}" stable file-a "new" "1.5.7"; print -r -- "mine" > "${f}/install/file-a"; run_up "${f}"
  [[ ! -f "${f}/install/.git/vde-cache-refreshed" ]] \
    && test_pass "case22c not on a refusal" || test_fail "case22c not on a refusal" "the cache script ran"
}

test_case23_dockerfile_forms_are_all_understood() {
  test_start "23: COPY and ADD, JSON-array and backslash-continued forms count; a copy from another build stage does not"
  local f form src
  for form in 'COPY scripts/vde-motd.zsh /x' 'COPY \
  scripts/vde-motd.zsh \
  /x' 'COPY ["scripts/vde-motd.zsh", "/x"]' 'ADD scripts/vde-motd.zsh /x'; do
    f="$(NO_DOCKERFILES=1 make_fixture c23)"; rm -rf "${f}"
    f="$(NO_DOCKERFILES=1 make_fixture c23-${#form}-${RANDOM})"
    mkdir -p "${f}/seed/scripts"; print -r -- "a" > "${f}/seed/scripts/vde-motd.zsh"
    print -r -- "FROM debian
${form}" > "${f}/seed/configs/docker/vde-base.Dockerfile"
    git -C "${f}/seed" add -A; git -C "${f}/seed" commit -qm dockerfile; git -C "${f}/seed" push -q origin stable 2>/dev/null
    git -C "${f}/install" pull -q --ff-only origin stable 2>/dev/null
    publish "${f}" stable scripts/vde-motd.zsh "changed" "1.5.7"; run_up "${f}"
    [[ "${UP_OUT}" == *"REBUILD YOUR BASE IMAGE"* ]] \
      && test_pass "case23 a base input given as: ${${form//$'\n'/ }[1,40]}" || test_fail "case23 a base input given as: ${form}" "out: ${UP_OUT}"
  done
  f="$(NO_DOCKERFILES=1 make_fixture c23stage)"
  mkdir -p "${f}/seed/src"; print -r -- "a" > "${f}/seed/src/foo"
  print -r -- "FROM debian
COPY --from=build src/foo /x" > "${f}/seed/configs/docker/vde-base.Dockerfile"
  git -C "${f}/seed" add -A; git -C "${f}/seed" commit -qm dockerfile; git -C "${f}/seed" push -q origin stable 2>/dev/null
  git -C "${f}/install" pull -q --ff-only origin stable 2>/dev/null
  publish "${f}" stable src/foo "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" != *"REBUILD YOUR BASE IMAGE"* ]] \
    && test_pass "case23f a copy FROM another build stage is not a base input" || test_fail "case23f a copy FROM another build stage is not a base input" "out: ${UP_OUT}"
}

test_case24_nested_compose_files_count_as_spoke_inputs() {
  test_start "24: a changed compose file nested under configs/docker/ asks for a Spoke rebuild"
  local f; f="$(make_fixture c24)"
  publish "${f}" stable configs/docker/languages/python/docker-compose.yml "changed" "1.5.7"; run_up "${f}"
  [[ "${UP_OUT}" == *"REBUILD YOUR SPOKES"* && "${UP_OUT}" != *"REBUILD YOUR BASE IMAGE"* ]] \
    && test_pass "case24 nested compose: Spoke advice, no base advice" || test_fail "case24 nested compose: Spoke advice, no base advice" "out: ${UP_OUT}"
}

test_case25_same_bytes_is_not_always_the_same_file() {
  test_start "25: an ignored file with the same bytes but another mode, a newline in its name, or a symlink in its place is refused and kept"
  local f before
  f="$(make_fixture c25a)"; publish "${f}" stable keep.sh "same" "1.5.7"
  print -r -- "keep.sh" > "${f}/install/.git/info/exclude"; print -r -- "same" > "${f}/install/keep.sh"; chmod +x "${f}/install/keep.sh"
  before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 13 && -x "${f}/install/keep.sh" && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case25a same bytes, different executable bit: refused, mode kept" || test_fail "case25a same bytes, different executable bit: refused, mode kept" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c25b)"; publish "${f}" stable $'odd\nname' "upstream" "1.5.7"
  print -r -- $'odd\nname' > "${f}/install/.git/info/exclude"; print -r -- "MINE" > "${f}/install/"$'odd\nname'
  run_up "${f}"
  [[ "${UP_RC}" == 13 && "$(cat "${f}/install/"$'odd\nname')" == "MINE" ]] \
    && test_pass "case25b an ignored file whose NAME contains a newline: refused and kept" || test_fail "case25b an ignored file whose NAME contains a newline: refused and kept" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c25c)"
  git -C "${f}/seed" checkout -q stable; ln -s "target-text" "${f}/seed/lnk"; git -C "${f}/seed" add -A; git -C "${f}/seed" commit -qm symlink; git -C "${f}/seed" push -q origin stable 2>/dev/null
  print -r -- "target-text" > "${f}/install/lnk"; run_up "${f}"
  [[ "${UP_RC}" == 13 && -f "${f}/install/lnk" && ! -L "${f}/install/lnk" ]] \
    && test_pass "case25c a regular file whose bytes equal an incoming symlink's target: refused and kept" || test_fail "case25c a regular file whose bytes equal an incoming symlink's target: refused and kept" "rc=${UP_RC} out=${UP_OUT}"
}

test_case26_a_hook_the_update_brings_does_not_run() {
  test_start "26: a post-merge hook delivered by the update (core.hooksPath inside the worktree) is not executed"
  local f; f="$(make_fixture c26)"
  git -C "${f}/install" config core.hooksPath .githooks
  mkdir -p "${f}/seed/.githooks"; print -r -- '#!/bin/sh
touch "$(git rev-parse --git-dir)/hook-ran"' > "${f}/seed/.githooks/post-merge"; chmod +x "${f}/seed/.githooks/post-merge"
  git -C "${f}/seed" add -A; git -C "${f}/seed" commit -qm hook; git -C "${f}/seed" push -q origin stable 2>/dev/null
  run_up "${f}"
  [[ "${UP_RC}" == 0 && -x "${f}/install/.githooks/post-merge" && ! -f "${f}/install/.git/hook-ran" ]] \
    && test_pass "case26 upgraded, the hook file arrived, and it did not run" || test_fail "case26 upgraded, the hook file arrived, and it did not run" "rc=${UP_RC} ran=$([[ -f "${f}/install/.git/hook-ran" ]] && echo yes || echo no) out=${UP_OUT}"
}

test_case27_the_busy_check_reads_the_real_lock_record() {
  test_start "27: a live lock in the REAL claim_lock format (PID:PGID:TIMESTAMP), in the default or a configured locks directory, blocks the upgrade"
  local f before
  f="$(make_fixture c27a)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${f}/install/.locks/vms/vde-base.lock"; print -r -- "$$:$$:$(date +%s)" > "${f}/install/.locks/vms/vde-base.lock/pid"
  before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 9 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case27a PID:PGID:TIMESTAMP with a live pid: exit 9, nothing changed" || test_fail "case27a PID:PGID:TIMESTAMP with a live pid: exit 9, nothing changed" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c27b)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${TMP_ROOT}/elsewhere-locks/vms/vde-python.lock"; print -r -- "$$:$$:$(date +%s)" > "${TMP_ROOT}/elsewhere-locks/vms/vde-python.lock/pid"
  before="$(head_of "${f}")"; VDE_LOCKS_DIR="${TMP_ROOT}/elsewhere-locks" run_up "${f}"
  [[ "${UP_RC}" == 9 && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case27b a lock under a configured VDE_LOCKS_DIR is honoured" || test_fail "case27b a lock under a configured VDE_LOCKS_DIR is honoured" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c27c)"; publish "${f}" stable file-a "new" "1.5.7"
  mkdir -p "${f}/install/.locks/vms/vde-base.lock"; print -r -- "999999:999999:$(date +%s)" > "${f}/install/.locks/vms/vde-base.lock/pid"
  run_up "${f}"
  [[ "${UP_RC}" == 0 ]] \
    && test_pass "case27c a stale record (dead pid) in the real format does not block" || test_fail "case27c a stale record (dead pid) in the real format does not block" "rc=${UP_RC} out=${UP_OUT}"
}

test_case28_hidden_local_edits_are_still_edits() {
  test_start "28: a file marked assume-unchanged or skip-worktree that the update changes is a conflict, not an invisible edit"
  local f before
  f="$(make_fixture c28a)"; publish "${f}" stable file-a "new" "1.5.7"
  git -C "${f}/install" update-index --assume-unchanged file-a; print -r -- "my hidden edit" > "${f}/install/file-a"
  before="$(head_of "${f}")"; run_up "${f}"
  [[ "${UP_RC}" == 13 && "${UP_OUT}" == *"changes files you have edited"* && "$(cat "${f}/install/file-a")" == "my hidden edit" && "$(head_of "${f}")" == "${before}" ]] \
    && test_pass "case28a assume-unchanged: exit 13 from the script's OWN check, the edit kept" || test_fail "case28a assume-unchanged: exit 13 from the script's OWN check, the edit kept" "rc=${UP_RC} out=${UP_OUT}"
  f="$(make_fixture c28b)"; publish "${f}" stable file-a "new" "1.5.7"
  git -C "${f}/install" update-index --skip-worktree file-a; print -r -- "my hidden edit" > "${f}/install/file-a"
  run_up "${f}"
  [[ "${UP_RC}" == 13 && "${UP_OUT}" == *"changes files you have edited"* && "$(cat "${f}/install/file-a")" == "my hidden edit" ]] \
    && test_pass "case28b skip-worktree: exit 13 from the script's OWN check, the edit kept" || test_fail "case28b skip-worktree: exit 13 from the script's OWN check, the edit kept" "rc=${UP_RC} out=${UP_OUT}"
}

test_case29_ssh_is_bounded_and_never_prompts() {
  test_start "29: git reaches origin over SSH with a connect timeout and no prompts, even when the timeout command does not exist"
  local f fakebin="${TMP_ROOT}/fakebin29" log="${TMP_ROOT}/ssh29.log"
  f="$(make_fixture c29)"
  mkdir -p "${fakebin}"
  print -r -- '#!/bin/sh
echo "$@" >> "'"${log}"'"
exit 255' > "${fakebin}/ssh"; chmod +x "${fakebin}/ssh"
  git -C "${f}/install" remote set-url origin "ssh://git@example.invalid/none.git"
  : > "${log}"
  PATH="${fakebin}:${PATH}" run_up "${f}"
  [[ "${UP_RC}" == 3 && "$(< "${log}")" == *"ConnectTimeout="* && "$(< "${log}")" == *"BatchMode=yes"* ]] \
    && test_pass "case29 exit 3, and ssh was given ConnectTimeout and BatchMode=yes" || test_fail "case29 exit 3, and ssh was given ConnectTimeout and BatchMode=yes" "rc=${UP_RC} ssh-args=$(< "${log}") out=${UP_OUT}"
}

test_case30_the_router_keeps_the_scripts_own_message_and_status() {
  test_start "30: bin/vde runs vde-upgrade.zsh directly, so its status and message are not rewritten by the error mapper (3 would read 'Unknown VM')"
  local block
  block="$(sed -n '/^    upgrade)/,/^        ;;/p' "${VDE_ROOT_DIR}/bin/vde")"
  [[ "${block}" == *"vde-upgrade.zsh"* && "${block}" != *"vde_run"* ]] \
    && test_pass "case30a the upgrade) case calls the script without vde_run" || test_fail "case30a the upgrade) case calls the script without vde_run" "block: ${block}"
  grep -q 'a rebuild or start is running' "${VDE_ROOT_DIR}/docs/reference/commands.md" \
    && test_pass "case30b commands.md documents exit status 9" || test_fail "case30b commands.md documents exit status 9" "not documented"
  grep -q 'git pull --ff-only' "${VDE_ROOT_DIR}/docs/releases/1.5.7.md" \
    && test_pass "case30c the 1.5.7 record tells existing installs to pull fast-forward only" || test_fail "case30c the 1.5.7 record tells existing installs to pull fast-forward only" "still a plain git pull"
}

test_case1_the_script_exists_and_is_executable
test_case2_happy_path_fast_forwards_and_reports_versions
test_case3_already_up_to_date_is_a_no_op
test_case4_dry_run_changes_nothing
test_case5_it_follows_the_branch_you_are_on
test_case6_detached_head_is_refused
test_case7_a_diverged_branch_is_refused
test_case8_local_commits_ahead_of_origin_are_not_an_error
test_case9_local_edits_that_the_update_would_overwrite_are_refused
test_case10_unrelated_local_edits_are_kept
test_case11_no_origin_and_no_remote_branch_are_refused
test_case12_an_install_that_is_not_a_git_checkout_is_refused
test_case13_it_works_from_any_directory
test_case14_the_script_can_upgrade_itself
test_case15_rebuild_guidance_separates_base_from_spokes
test_case16_usage_errors_exit_2
test_case17_the_router_dispatches_upgrade
test_case18_real_history_five_commits_back_lands_on_the_tip
test_case19_local_files_in_the_way_are_refused_not_overwritten
test_case20_a_rename_upstream_still_names_your_edited_file
test_case21_a_running_rebuild_blocks_the_upgrade
test_case22_the_registry_cache_is_refreshed_after_a_real_upgrade_only
test_case23_dockerfile_forms_are_all_understood
test_case24_nested_compose_files_count_as_spoke_inputs
test_case25_same_bytes_is_not_always_the_same_file
test_case26_a_hook_the_update_brings_does_not_run
test_case27_the_busy_check_reads_the_real_lock_record
test_case28_hidden_local_edits_are_still_edits
test_case29_ssh_is_bounded_and_never_prompts
test_case30_the_router_keeps_the_scripts_own_message_and_status

echo
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
