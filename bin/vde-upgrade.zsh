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
typeset -ri UP_NOT_UPDATABLE=3    # VDE_ERR_NOT_FOUND: this install cannot be updated (no git checkout, detached HEAD, no origin, no such branch on origin)
typeset -ri UP_DRIFT=13           # VDE_ERR_SYNC_DRIFT: your copy and origin disagree (diverged history, or edits the update would overwrite)

upgrade_usage() {
    print -r -- "Usage: vde upgrade [--dry-run]"
    print -r -- "  Brings this install up to date with the latest of the branch it is on."
    print -r -- "  It fetches that branch from origin and fast-forwards to it. It never merges,"
    print -r -- "  rebases or rewrites your history, and it refuses, changing nothing, if it cannot"
    print -r -- "  do that safely."
    print -r -- "  --dry-run   Fetch and report what would change; change nothing in your working tree."
    print -r -- "  Exit status: 0 done or already current; 2 bad option; 3 this install cannot be"
    print -r -- "  updated (not a git clone, detached HEAD, no origin, branch not on origin);"
    print -r -- "  13 your copy and origin disagree (diverged, or your edits clash with the update)."
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

# upgrade_copy_sources REV DOCKERFILE - the paths that Dockerfile COPYs in, one pattern per line
# (${VAR} becomes *). Read from the revision being installed, so the list can never go stale.
upgrade_copy_sources() {
    emulate -L zsh
    setopt extended_glob
    local line w
    local -a words
    git show "${1}:${2}" 2>/dev/null | while IFS= read -r line; do
        [[ "${line}" == COPY[[:space:]]* ]] || continue
        words=( ${(z)line} )
        shift words
        words=( ${words:#--*} )
        (( ${#words} >= 2 )) || continue
        for w in ${words[1,-2]}; do print -r -- "${w//\$\{[^\}]##\}/*}"; done
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

upgrade_main() {
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
        upgrade_refuse ${UP_NOT_UPDATABLE} "HEAD is detached, so there is no branch to follow. Switch to one first, e.g.: git switch stable"
        return $?
    fi

    git remote get-url origin >/dev/null 2>&1 || { upgrade_refuse ${UP_NOT_UPDATABLE} "this clone has no 'origin' remote to update from"; return $? }

    local rc
    git ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null 2>&1
    rc=$?
    if (( rc == 2 )); then
        upgrade_refuse ${UP_NOT_UPDATABLE} "origin has no branch '${branch}', so there is nothing to update this install to. Switch to one it has, e.g.: git switch stable"
        return $?
    elif (( rc != 0 )); then
        upgrade_refuse ${UP_NOT_UPDATABLE} "cannot reach origin (git exited ${rc}). Check your network connection and try again."
        return $?
    fi

    git fetch --quiet origin "refs/heads/${branch}" 2>/dev/null || { upgrade_refuse ${UP_NOT_UPDATABLE} "fetching '${branch}' from origin failed"; return $? }

    local old new
    old="$(git rev-parse HEAD)"
    new="$(git rev-parse 'FETCH_HEAD^{commit}')"
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

    # Your own work is kept unless the update also touches the same path. Three kinds of local
    # state stand in the way: edits to tracked files, untracked files the update adds, and
    # IGNORED files the update adds (git overwrites those without a word, so they are checked
    # here). A local file already identical to what the update brings loses nothing.
    local -a mine incoming clash stray
    local p
    mine=( ${(f)"$(git diff --no-renames --name-only HEAD 2>/dev/null)"} )
    incoming=( ${(f)"$(git diff --no-renames --name-only "${old}" "${new}" 2>/dev/null)"} )
    stray=( ${(f)"$(git ls-files --others 2>/dev/null)"} )
    mine=( ${mine:#} ); incoming=( ${incoming:#} ); stray=( ${stray:#} )
    clash=( ${mine:*incoming} )
    for p in ${stray:*incoming}; do
        [[ "$(git hash-object -- "${p}" 2>/dev/null)" == "$(git rev-parse "${new}:${p}" 2>/dev/null)" ]] && continue
        clash+=( "${p}" )
    done
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

    if ! git merge --ff-only --quiet "${new}" 2>&1; then
        upgrade_refuse ${UP_DRIFT} "git could not fast-forward '${branch}' (see its message above). Nothing was changed."
        return $?
    fi

    print -r -- "Upgraded '${branch}': ${oldver} (${old[1,7]}) -> ${newver} (${new[1,7]}); ${ncommits} commit(s), ${nfiles} file(s)."

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
upgrade_main "$@"; exit $?
