#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE repository pruning ritual (Forge housekeeping). Zsh only.
# Usage: vde prune [--timeframe <7d|3d|24h|12h>] [--dry-run|--apply] [--yes]

typeset _ZSH_PURE=${(%):-%x}

VDE_ROOT="${VDE_ROOT_DIR:-$HOME/VDE}"
TIMEFRAME="7d"
APPLY=0
YES=0
DRY_RUN=0

usage() {
    print -r -- "Usage: vde prune [--timeframe <7d|3d|24h|12h>] [--dry-run|--apply] [--yes]"
    print -r -- "  Default and --dry-run print a plan without changing files."
    print -r -- "  --apply deletes old repository housekeeping files and archives old plans/scripts."
    print -r -- "  --apply prompts unless --yes is supplied; use vde clean for Docker disk cleanup."
}

while (( $# > 0)); do
    case "$1" in
        --timeframe)
            (( $# >= 2 )) || { print -u2 -r -- "missing value for --timeframe"; usage; exit 2; }
            TIMEFRAME="$2"
            shift 2
            ;;
        --dry-run) DRY_RUN=1; shift ;;
        --apply) APPLY=1; shift ;;
        --yes) YES=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) print -u2 -r -- "unknown option or argument: $1"; usage; exit 2 ;;
    esac
done

if (( APPLY && DRY_RUN)); then
    print -u2 -r -- "--apply and --dry-run cannot be used together"; exit 2
fi
case "$TIMEFRAME" in
    7d|3d|24h|12h) ;;
    *) print -u2 -r -- "invalid --timeframe: $TIMEFRAME (allowed: 7d, 3d, 24h, 12h)"; exit 2 ;;
esac

typeset number=${TIMEFRAME[1,-2]}
typeset unit=${TIMEFRAME[-1]}
typeset minutes
case "$unit" in
    d) minutes=$(( number * 24 * 60 )) ;;
    h) minutes=$(( number * 60 )) ;;
    m) minutes=$number ;;
esac

CURRENT_BASELINE=""
if [[ -f "${VDE_ROOT}/docs/governance/vde-spec.md" ]]; then
    CURRENT_BASELINE=$(awk '/^Version:/ {print $2; exit}' "${VDE_ROOT}/docs/governance/vde-spec.md")
fi
if [[ -z "$CURRENT_BASELINE" ]]; then
    print -u2 -r -- "Refusing prune: cannot resolve the current baseline from docs/governance/vde-spec.md"
    exit 2
fi

is_tracked() {
    local relative="$1"
    git -C "${VDE_ROOT}" ls-files --error-unmatch "$relative" >/dev/null 2>&1
}

is_clean_tracked() {
    local relative="$1"
    git -C "${VDE_ROOT}" diff --quiet -- "$relative" && git -C "${VDE_ROOT}" diff --cached --quiet -- "$relative"
}

is_protected() {
    local dir="$1" file="$2"
    [[ "$dir" == "docs/releases" && "$file" == "${CURRENT_BASELINE}.md" ]] && return 0
    [[ "$file" == "2026-04-13-pruning-ritual-plan.md" ]] && return 0
    [[ "$file" == "2026-04-13-ingot-stash-plan.md" ]] && return 0
    [[ "$file" == *-init.zsh ]] && return 0
    return 1
}

# One selection routine is shared by dry-run and apply.
typeset -a DELETE_FILES MOVE_FILES
DELETE_FILES=()
MOVE_FILES=()

for dir in plans plans/scripts docs/releases; do
    [[ -d "${VDE_ROOT}/${dir}" ]] || continue
    while IFS= read -r file; do
        [[ -n "$file" ]] || continue
        typeset filename=${file:t}
        is_protected "$dir" "$filename" && continue
        DELETE_FILES+=("$file")
    done < <(find "${VDE_ROOT}/${dir}" -maxdepth 1 -type f -mmin +${minutes} -print)
done

for dir in plans plans/scripts docs/releases; do
    [[ -d "${VDE_ROOT}/${dir}" ]] || continue
    while IFS= read -r file; do
        [[ -n "$file" ]] || continue
        typeset filename=${file:t}
        is_protected "$dir" "$filename" && continue
        MOVE_FILES+=("$file")
    done < <(find "${VDE_ROOT}/${dir}" -maxdepth 1 -type f -mmin +1440 -mmin -${minutes} -print)
done

print -r -- "VDE prune plan (timeframe: ${TIMEFRAME}, ${minutes}m)"
print -r -- "DELETE (${#DELETE_FILES[@]}):"
for file in "${DELETE_FILES[@]}"; do print -r -- "  ${file#$VDE_ROOT/}"; done
print -r -- "MOVE (${#MOVE_FILES[@]}):"
for file in "${MOVE_FILES[@]}"; do print -r -- "  ${file#$VDE_ROOT/} -> ${file:h}/archive/${file:t}"; done

if (( ! APPLY && ! DRY_RUN )) || (( DRY_RUN)); then
    print -r -- "dry run: no files changed. Use --apply --yes to apply this exact plan."
    exit 0
fi

if (( ! YES)); then
    if [[ ! -t 0 ]]; then
        print -u2 -r -- "Refusing interactive confirmation without a terminal; use --yes"
        exit 2
    fi
    local reply
    read "reply?Apply this plan? [y/N] "
    [[ "$reply" == [yY]* ]] || { print -r -- "Cancelled: no files changed."; exit 0; }
fi

typeset deleted=0 moved=0 failures=0
for file in "${DELETE_FILES[@]}"; do
    typeset relative="${file[${#VDE_ROOT}+2,-1]}"
    [[ -f "$file" && ! -L "$file" ]] || { (( failures++)); print -u2 -r -- "FAILED DELETE ${relative}: target changed or became a symlink"; continue; }
    if [[ -z "$(find "$file" -maxdepth 0 -type f -mmin +${minutes} -print)" ]]; then
        (( failures++)); print -u2 -r -- "FAILED DELETE ${relative}: target is no longer old enough"; continue
    fi
    if is_tracked "$relative"; then
        if git -C "${VDE_ROOT}" rm -q "$relative"; then
            (( deleted++ ))
            print -r -- "DELETED ${file#$VDE_ROOT/}"
        else
            (( failures++ ))
            print -u2 -r -- "FAILED DELETE ${file#$VDE_ROOT/}"
        fi
    else
        if rm -rf -- "$file"; then
            (( deleted++ ))
            print -r -- "DELETED ${file#$VDE_ROOT/}"
        else
            (( failures++ ))
            print -u2 -r -- "FAILED DELETE ${file#$VDE_ROOT/}"
        fi
    fi
done

for file in "${MOVE_FILES[@]}"; do
    typeset relative="${file[${#VDE_ROOT}+2,-1]}"
    [[ -f "$file" && ! -L "$file" ]] || { (( failures++)); print -u2 -r -- "FAILED MOVE ${relative}: target changed or became a symlink"; continue; }
    if [[ -z "$(find "$file" -maxdepth 0 -type f -mmin +1440 -mmin -${minutes} -print)" ]]; then
        (( failures++)); print -u2 -r -- "FAILED MOVE ${relative}: target is outside the selected age window"; continue
    fi
    typeset dest="${file:h}/archive"
    typeset destination="${dest}/${file:t}"
    [[ ! -L "$dest" ]] || { (( failures++)); print -u2 -r -- "FAILED MOVE ${relative}: archive path is a symlink"; continue; }
    if [[ -e "$destination" || -L "$destination" ]]; then
        (( failures++))
        print -u2 -r -- "FAILED MOVE ${file#$VDE_ROOT/}: archive collision at ${destination#$VDE_ROOT/}"
        continue
    fi
    mkdir -p -- "$dest" || { (( failures++)); print -u2 -r -- "FAILED MOVE ${file#$VDE_ROOT/}: cannot create archive"; continue; }
    if is_tracked "$relative"; then
        if ! is_clean_tracked "$relative"; then
            (( failures++))
            print -u2 -r -- "FAILED MOVE ${relative}: tracked file has local modifications"
            continue
        fi
        if git -C "${VDE_ROOT}" mv "$relative" "$destination"; then
            (( moved++ ))
            print -r -- "MOVED ${file#$VDE_ROOT/} -> ${dest#$VDE_ROOT/}/${file:t}"
        else
            (( failures++ ))
            print -u2 -r -- "FAILED MOVE ${file#$VDE_ROOT/}"
        fi
    else
        if mv -n -- "$file" "$destination" && [[ -e "$destination" && ! -e "$file" ]]; then
            (( moved++ ))
            print -r -- "MOVED ${file#$VDE_ROOT/} -> ${dest#$VDE_ROOT/}/${file:t}"
        else
            (( failures++ ))
            print -u2 -r -- "FAILED MOVE ${file#$VDE_ROOT/}"
        fi
    fi
done

print -r -- "Applied: deleted=${deleted} moved=${moved} failed=${failures}"
(( failures == 0 ))
