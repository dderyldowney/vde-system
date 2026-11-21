#!/usr/bin/env zsh
# @armor (Engine Core)
# vde upgrade - bring this install up to date with the latest of the branch it is on. Zsh only.
# Usage: vde upgrade [--dry-run]

typeset _ZSH_PURE=${(%):-%x}

# Where this script really lives. Captured at the top level: inside a function $0 is the
# function's name. The install is the directory above bin/, wherever the caller happens to be.
typeset -r _UP_SELF="${0:A}"

# Exit statuses (the numbering of lib/vde-constants).
typeset -ri UP_OK=0
typeset -ri UP_USAGE=2            # VDE_ERR_INVALID_INPUT: bad option
typeset -ri UP_NOT_UPDATABLE=3    # VDE_ERR_NOT_FOUND: this install cannot be updated (no git checkout, detached HEAD, no origin, no such branch on origin, origin unreachable)
typeset -ri UP_LOCKED=9           # VDE_ERR_LOCK: a rebuild or a start is running
typeset -ri UP_DRIFT=13           # VDE_ERR_SYNC_DRIFT: your copy and origin disagree (diverged history, or local files the update would overwrite)

upgrade_usage() {
  print -r -- "Usage: vde upgrade [--dry-run]"
  print -r -- "  Brings this install up to date with the latest of the branch it is on."
  print -r -- "  It fetches that branch from origin and fast-forwards to it. It never merges,"
  print -r -- "  rebases or rewrites your history, and it refuses, changing nothing, if it cannot"
  print -r -- "  do that safely."
  print -r -- "  --dry-run   Fetch and report what would change; change nothing in your working tree."
  print -r -- "  Exit status: 0 done or already current; 2 bad option; 3 this install cannot be"
  print -r -- "  updated (not a git clone, detached HEAD, no origin, branch not on origin, origin"
  print -r -- "  unreachable); 9 a rebuild or start is running; 13 your copy and origin disagree"
  print -r -- "  (diverged, or your files would be overwritten by the update)."
}

# upgrade_version REV - the Gospel version recorded at a git revision, or "unknown".
upgrade_version() {
  local line v
  line="$(git show "${1}:docs/governance/vde-spec.md" 2>/dev/null | grep -m1 '^# VDE-SPEC ')"
  v="${${(s: :)line}[3]}"
  print -r -- "${${v#v}:-unknown}"
}

upgrade_refuse() {  # upgrade_refuse CODE MESSAGE... -> message on stderr, returns CODE ("status" is a read-only zsh variable)
  local code="$1"; shift
  print -u2 -r -- "vde upgrade: $*"
  return ${code}
}

# upgrade_array NAME COMMAND... - fill the array NAME from the NUL-separated output of COMMAND,
# so a path with a newline, quote or space in it survives intact.
upgrade_array() {
  local name="$1" item
  local -a out
  shift
  while IFS= read -r -d '' item; do
    out+=( "${item}" )
  done < <("$@" 2>/dev/null)
  set -A "${name}" "${out[@]}"
}

# upgrade_copy_sources REV DOCKERFILE - the repository paths that Dockerfile copies in, one
# pattern per line. Reads COPY and ADD, shell and JSON-array forms, and lines continued with a
# backslash; skips copies from another build stage (--from=) and URLs; ${VAR} becomes *. Read
# from the revision being installed, so the list can never go stale.
upgrade_copy_sources() {
  emulate -L zsh
  setopt extended_glob
  local text line w verb
  local -a words
  text="$(git show "${1}:${2}" 2>/dev/null)" || return 0
  text="${text//\\$'\n'/ }"
  for line in "${(@f)text}"; do
    words=( ${(z)line} )
    verb="${(L)words[1]}"
    [[ "${verb}" == (copy|add) ]] || continue
    shift words
    (( ${words[(I)--from=*]} )) && continue
    words=( ${words//[\[\]\",]/} )
    words=( ${words:#} )
    words=( ${words:#--*} )
    (( ${#words} >= 2 )) || continue
    for w in ${words[1,-2]}; do
      [[ "${w}" == *://* ]] && continue
      print -r -- "${w//\$\{[^\}]##\}/*}"
    done
  done
}

# upgrade_hits - prints each file in the caller's array "incoming" that matches a pattern in the
# caller's array "pats" (a pattern ending in / names a whole directory).
upgrade_hits() {
  emulate -L zsh
  setopt extended_glob
  local f p
  for f in ${incoming}; do
    for p in ${pats}; do
      if [[ "${f}" == ${~p} || ( "${p}" == */ && "${f}" == "${p}"* ) ]]; then
        print -r -- "${f}"
        break
      fi
    done
  done
}

# upgrade_same_as_incoming PATH REV - 0 when the local file PATH is a regular file whose content
# AND executable bit equal the entry REV holds, so overwriting it loses nothing. A symlink, a
# different mode or different bytes is a difference.
upgrade_same_as_incoming() {
  local p="$1" rev="$2" line mode rest sha lmode localsha
  local -a entries
  entries=( ${(f)"$(git ls-tree "${rev}" -- "${p}" 2>/dev/null)"} )
  line="${entries[1]}"
  [[ -n "${line}" ]] || return 1
  read -r mode _ rest <<< "${line}"
  sha="${rest%%$'\t'*}"
  [[ "${mode}" == (100644|100755) && ! -L "${p}" && -f "${p}" ]] || return 1
  [[ -x "${p}" ]] && lmode=100755 || lmode=100644
  [[ "${lmode}" == "${mode}" ]] || return 1
  localsha="$(git hash-object -- "${p}" 2>/dev/null)"
  [[ -n "${localsha}" && "${localsha}" == "${sha}" ]]
}

# upgrade_preflight OLD NEW - fills the caller's arrays "incoming", "clash" and "identical":
# files the update changes; local files it would overwrite; local files already identical to
# what it brings (nothing to lose, but git will not overwrite them itself). Your work is kept
# unless the update touches the same path. Three kinds of local state stand in the way: edits
# to tracked files, and untracked or ignored files the update adds.
upgrade_preflight() {
  local old="$1" new="$2" p
  local -a mine stray
  upgrade_array mine git diff -z --no-renames --name-only HEAD
  upgrade_array incoming git diff -z --no-renames --name-only "${old}" "${new}"
  upgrade_array stray git ls-files -z --others
  clash=( ${mine:*incoming} )
  identical=()
  for p in ${stray:*incoming}; do
    if upgrade_same_as_incoming "${p}" "${new}"; then
      identical+=( "${p}" )
    else
      clash+=( "${p}" )
    fi
  done
}

# upgrade_busy ROOT - prints the name of a running rebuild or start (a live per-Spoke lock) and
# returns 0; returns 1 when nothing is running.
upgrade_busy() {
  local lock pid
  for lock in "${1}"/.locks/vms/*.lock(N/); do
    [[ -r "${lock}/pid" ]] || continue
    pid="$(< "${lock}/pid")"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      print -r -- "${lock:t:r}"
      return 0
    fi
  done
  return 1
}

main() {
  emulate -L zsh
  local dry_run=0
  while (( $# > 0 )); do
    case "$1" in
      --dry-run) dry_run=1 ;;
      -h|--help) upgrade_usage; return ${UP_OK} ;;
      *) print -u2 -r -- "unknown option or argument: $1"; upgrade_usage >&2; return ${UP_USAGE} ;;
    esac
    shift
  done

  local root="${_UP_SELF:h:h}"
  cd "${root}" 2>/dev/null || { upgrade_refuse ${UP_NOT_UPDATABLE} "cannot enter the install directory ${root}"; return $? }
  command -v git >/dev/null 2>&1 || { upgrade_refuse ${UP_NOT_UPDATABLE} "git is required (it is one of the four prerequisites)"; return $? }

  local top
  top="$(git rev-parse --show-toplevel 2>/dev/null)"
  if [[ -z "${top}" || "${top:A}" != "${root:A}" ]]; then
    upgrade_refuse ${UP_NOT_UPDATABLE} "${root} is not a git checkout, so it cannot be updated in place. Reinstall with: git clone -b stable https://github.com/dderyldowney/vde-system.git VDE"
    return $?
  fi

  local branch
  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)"
  if [[ -z "${branch}" ]]; then
    upgrade_refuse ${UP_NOT_UPDATABLE} "HEAD is detached, so there is no branch to follow. Switch to one first (most installs follow stable), e.g.: git switch stable"
    return $?
  fi

  git remote get-url origin >/dev/null 2>&1 || { upgrade_refuse ${UP_NOT_UPDATABLE} "this clone has no 'origin' remote to update from"; return $? }

  # A stalled network or a credential prompt must not hang the upgrade.
  export GIT_TERMINAL_PROMPT=0 GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=30
  local -a bound=()
  command -v timeout >/dev/null 2>&1 && bound=( timeout 120 )

  local rc
  "${bound[@]}" git ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null 2>&1
  rc=$?
  if (( rc == 2 )); then
    upgrade_refuse ${UP_NOT_UPDATABLE} "origin has no branch '${branch}', so there is nothing to update this install to. Switch to one it has (most installs follow stable), e.g.: git switch stable"
    return $?
  elif (( rc == 124 )); then
    upgrade_refuse ${UP_NOT_UPDATABLE} "origin did not answer within 120 seconds. Check your network connection and try again."
    return $?
  elif (( rc != 0 )); then
    upgrade_refuse ${UP_NOT_UPDATABLE} "cannot reach origin (git exited ${rc}). Check your network connection and try again."
    return $?
  fi

  # Fetch into a private ref so this run uses exactly the commit it fetched, whatever else
  # fetches into this clone meanwhile.
  local ref="refs/vde-upgrade/incoming-$$" old new
  "${bound[@]}" git fetch --quiet origin "+refs/heads/${branch}:${ref}" 2>/dev/null \
    || { upgrade_refuse ${UP_NOT_UPDATABLE} "fetching '${branch}' from origin failed or timed out"; return $? }
  new="$(git rev-parse "${ref}^{commit}" 2>/dev/null)"
  git update-ref -d "${ref}" 2>/dev/null
  [[ -n "${new}" ]] || { upgrade_refuse ${UP_NOT_UPDATABLE} "could not read what was fetched from origin"; return $? }
  old="$(git rev-parse HEAD)"

  local oldver newver
  oldver="$(upgrade_version "${old}")"
  newver="$(upgrade_version "${new}")"

  if [[ "${old}" == "${new}" ]]; then
    print -r -- "VDE is up to date: ${oldver} on '${branch}' (${old[1,7]})."
    return ${UP_OK}
  fi
  if git merge-base --is-ancestor "${new}" "${old}"; then
    print -r -- "VDE is up to date: your '${branch}' is ahead of origin by $(git rev-list --count "${new}..${old}") commit(s); there is nothing newer to bring in."
    return ${UP_OK}
  fi
  if ! git merge-base --is-ancestor "${old}" "${new}"; then
    upgrade_refuse ${UP_DRIFT} "your '${branch}' and origin/${branch} have diverged (you have $(git rev-list --count "${new}..${old}") commit(s) origin lacks; origin has $(git rev-list --count "${old}..${new}") you lack). vde upgrade never merges or rewrites your history. Nothing was changed."
    return $?
  fi

  local -a incoming clash identical
  upgrade_preflight "${old}" "${new}"
  if (( ${#clash} > 0 )); then
    upgrade_refuse ${UP_DRIFT} "this update changes files you have edited or added, and would overwrite them:
  ${(pj:\n  :)clash}
Keep them aside first (git stash, or commit them, or move them), then run vde upgrade again. Nothing was changed."
    return $?
  fi

  local ncommits nfiles
  ncommits="$(git rev-list --count "${old}..${new}")"
  nfiles=${#incoming}

  if (( dry_run )); then
    print -r -- "Upgrade available on '${branch}': ${oldver} (${old[1,7]}) -> ${newver} (${new[1,7]}); ${ncommits} commit(s), ${nfiles} file(s)."
    print -r -- "Dry run: nothing in your working tree was changed."
    return ${UP_OK}
  fi

  local busy
  if busy="$(upgrade_busy "${root}")"; then
    upgrade_refuse ${UP_LOCKED} "a rebuild or start is running (${busy}); upgrading now could hand it a mixture of two versions. Wait for it to finish, then run vde upgrade again. Nothing was changed."
    return $?
  fi

  # Look once more immediately before the merge: something may have appeared since the first look.
  upgrade_preflight "${old}" "${new}"
  if (( ${#clash} > 0 )); then
    upgrade_refuse ${UP_DRIFT} "files appeared that this update would overwrite:
  ${(pj:\n  :)clash}
Nothing was changed. Move them aside and run vde upgrade again."
    return $?
  fi

  # Files already identical to the incoming ones lose nothing, but git will not overwrite an
  # untracked or ignored file itself. Set them aside; put them back if the merge fails.
  local p
  for p in ${identical}; do rm -f -- "${p}"; done
  # Hooks off: an update must not be able to run code through a hook it brings.
  if ! git -c core.hooksPath=/dev/null merge --ff-only --quiet "${new}" 2>&1; then
    for p in ${identical}; do
      git show "${new}:${p}" > "${p}" 2>/dev/null
      [[ "$(git ls-tree "${new}" -- "${p}" | cut -c1-6)" == 100755 ]] && chmod +x "${p}"
    done
    upgrade_refuse ${UP_DRIFT} "git could not fast-forward '${branch}' (see its message above). Nothing was changed."
    return $?
  fi

  print -r -- "Upgraded '${branch}': ${oldver} (${old[1,7]}) -> ${newver} (${new[1,7]}); ${ncommits} commit(s), ${nfiles} file(s)."
  if [[ -x "${root}/bin/vde-rebuild-cache" ]]; then
    if "${root}/bin/vde-rebuild-cache" >/dev/null 2>&1; then
      print -r -- "Registry cache refreshed."
    else
      print -r -- "The registry cache did not refresh; it refreshes itself on your next vde command."
    fi
  fi

  # What the update changes inside images. The base image (vde-base) and the Spoke images are
  # built from different inputs, read from the Dockerfiles at the revision just installed. A
  # Spoke is built FROM vde-base, so it keeps the base it was built on until it is rebuilt.
  local basedf="configs/docker/vde-base.Dockerfile" d
  local -a pats base_hits spoke_hits
  if git cat-file -e "${new}:${basedf}" 2>/dev/null; then
    pats=( "${basedf}" ${(f)"$(upgrade_copy_sources "${new}" "${basedf}")"} )
    base_hits=( ${(f)"$(upgrade_hits)"} )
    pats=( "configs/docker/*" "templates/*" "data/vm-types*" )
    for d in ${(f)"$(git ls-tree --name-only "${new}" configs/docker/ 2>/dev/null)"}; do
      [[ "${d}" == *.Dockerfile && "${d}" != "${basedf}" ]] && pats+=( ${(f)"$(upgrade_copy_sources "${new}" "${d}")"} )
    done
    spoke_hits=( ${(f)"$(upgrade_hits)"} )
    spoke_hits=( ${spoke_hits:|base_hits} )
  else
    # Cannot tell what the base is made of: assume anything but documentation matters.
    base_hits=( ${incoming:#(docs|tests|plans)/*} )
    base_hits=( ${base_hits:#*.md} )
  fi
  if (( ${#base_hits} > 0 )); then
    print -r -- ""
    print -r -- "REBUILD YOUR BASE IMAGE. This update changes what goes into vde-base:"
    print -r -- "  ${(pj:\n  :)base_hits[1,5]}"
    (( ${#base_hits} > 5 )) && print -r -- "  ... and $(( ${#base_hits} - 5 )) more"
    print -r -- "A Spoke keeps running on the base it was built from, so rebuild the base first and then"
    print -r -- "every Spoke you use. Name 'base' before the Spokes and VDE does both, in that order:"
    print -r -- "  vde rebuild base <spoke> [<spoke> ...]"
    print -r -- "  vde rebuild --no-cache base <spoke> [<spoke> ...]   (from scratch; add --pull to refresh Debian too)"
    print -r -- "Running Spokes keep their old image until you rebuild and restart them."
  elif (( ${#spoke_hits} > 0 )); then
    print -r -- ""
    print -r -- "REBUILD YOUR SPOKES. This update changes how Spokes are built, not the base image."
    print -r -- "  vde rebuild <spoke> [<spoke> ...]"
    print -r -- "A plain 'vde rebuild <spoke>' reuses your existing base image, which is right here."
    print -r -- "Running Spokes keep their old image until you rebuild and restart them."
  else
    print -r -- "This update changes no image inputs; there is nothing to rebuild."
  fi
  return ${UP_OK}
}

# Everything above is parsed before anything runs, and the script ends in this one line, so
# an update that replaces this very file cannot disturb the run in progress.
main "$@"; exit $?
