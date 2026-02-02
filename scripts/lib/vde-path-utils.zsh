#!/bin/zsh
# VDE Path Utilities
# Path conversion functions for HOME-relative and absolute path handling
# Source this library with: source ./scripts/lib/vde-path-utils.zsh
#
# These utilities help with cross-platform path handling, making VDE scripts
# portable across Linux native, WSL2, and macOS.

# =============================================================================
# SOURCE GUARD
# =============================================================================

if [ "${_VDE_PATH_UTILS_LOADED:-}" = "1" ]; then
    return 0 2>/dev/null || exit 0
fi
_VDE_PATH_UTILS_LOADED=1

# =============================================================================
# DEPENDENCIES
# =============================================================================

# Ensure HOME is set
if [ -z "$HOME" ]; then
    export HOME="$(eval echo ~$(whoami))"
fi

# =============================================================================
# PATH CONVERSION FUNCTIONS
# =============================================================================

# Convert absolute path to HOME-relative path
# Usage: vde_path_to_home_rel "/home/user/.ssh/id_ed25519"
# Output: ~/.ssh/id_ed25519
vde_path_to_home_rel() {
    local abs_path="$1"
    
    if [[ -z "$abs_path" ]]; then
        echo ""
        return 1
    fi
    
    # Check if path starts with HOME
    if [[ "$abs_path" == "$HOME"* ]]; then
        local rel_path="${abs_path#$HOME}"
        if [[ "$rel_path" == /* ]]; then
            echo "~${rel_path}"
        else
            echo "~/${rel_path}"
        fi
    else
        # Path is not under HOME, return as-is
        echo "$abs_path"
    fi
}

# Convert HOME-relative path to absolute path
# Usage: vde_path_from_home_rel "~/.ssh/id_ed25519"
# Output: /home/user/.ssh/id_ed25519
vde_path_from_home_rel() {
    local rel_path="$1"
    
    if [[ -z "$rel_path" ]]; then
        echo ""
        return 1
    fi
    
    # Check if path starts with tilde
    if [[ "$rel_path" == "~"* ]]; then
        local without_tilde="${rel_path#~}"
        if [[ "$without_tilde" == /* ]]; then
            echo "${HOME}${without_tilde}"
        else
            echo "${HOME}/${without_tilde}"
        fi
    else
        # Path is already absolute, return as-is
        echo "$rel_path"
    fi
}

# Normalize path (remove double slashes, resolve . and ..)
# Usage: vde_path_normalize "/home//user/../user/./file"
# Output: /home/user/file
vde_path_normalize() {
    local path="$1"
    
    if [[ -z "$path" ]]; then
        echo ""
        return 1
    fi
    
    # Remove double slashes
    local normalized="${path//\/\//\/}"
    
    # Use cd to resolve . and .. (works in zsh and bash)
    if [[ -d "$normalized" ]] || [[ -f "$normalized" ]]; then
        cd "$normalized" 2>/dev/null && pwd
    else
        # For non-existent paths, do basic normalization
        echo "$normalized"
    fi
}

# Get project name from VDE_ROOT_DIR
# Usage: vde_get_project_name
# Output: vde (extracted from /path/to/vde)
vde_get_project_name() {
    local abs_project_root="${VDE_ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
    echo "${abs_project_root:t}"
}

# Check if a path is under HOME directory
# Usage: vde_is_home_path "/home/user/.ssh"
# Output: 0 (true) or 1 (false)
vde_is_home_path() {
    local path="$1"
    
    if [[ -z "$path" ]]; then
        return 1
    fi
    
    if [[ "$path" == "$HOME"* ]]; then
        return 0
    else
        return 1
    fi
}

# Make path portable by converting HOME-relative to absolute
# Usage: vde_make_portable "~/.ssh/id_ed25519"
# Output: /home/user/.ssh/id_ed25519 (if HOME=/home/user)
vde_make_portable() {
    local path="$1"
    
    if [[ -z "$path" ]]; then
        echo ""
        return 1
    fi
    
    # Convert to absolute if needed
    local abs_path
    abs_path=$(vde_path_from_home_rel "$path")
    
    # Normalize the path
    vde_path_normalize "$abs_path"
}

# Make path home-relative for display/storage
# Usage: vde_make_home_relative "/home/user/.ssh/id_ed25519"
# Output: ~/.ssh/id_ed25519
vde_make_home_relative() {
    local path="$1"
    
    if [[ -z "$path" ]]; then
        echo ""
        return 1
    fi
    
    vde_path_to_home_rel "$path"
}
