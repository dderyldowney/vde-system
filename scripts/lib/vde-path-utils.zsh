#!/bin/zsh
# VDE Path Utilities
# Cross-platform path handling utilities for the Virtual Development Environment
#
# This library provides functions for converting between absolute and relative
# paths, with special handling for HOME-relative paths for portability across
# Linux, WSL2, and macOS.
#
# Source this library with: source ./scripts/lib/vde-path-utils.zsh
# Note: This library requires vde-constants to be sourced first

# =============================================================================
# SOURCE GUARD
# =============================================================================

if [ "${_VDE_PATH_UTILS_LOADED:-}" = "1" ]; then
    return 0 2>/dev/null || exit 0
fi
_VDE_PATH_UTILS_LOADED=1

# =============================================================================
# PATH CONVERSION FUNCTIONS
# =============================================================================

# Convert absolute path to HOME-relative path
# Usage: vde_path_to_home_rel "/home/user/.ssh/vde/id_ed25519"
# Output: "~/.ssh/vde/id_ed25519"
vde_path_to_home_rel() {
    local abs_path="$1"
    
    # Check if path starts with HOME
    if [[ "$abs_path" == "$HOME/"* ]] || [[ "$abs_path" == "$HOME" ]]; then
        local rel_path="${abs_path#$HOME}"
        if [[ -z "$rel_path" ]]; then
            echo "~"
        else
            echo "~${rel_path}"
        fi
    else
        echo "$abs_path"
    fi
}

# Convert HOME-relative path to absolute path
# Usage: vde_path_from_home_rel "~/.ssh/vde/id_ed25519"
# Output: "/home/user/.ssh/vde/id_ed25519"
vde_path_from_home_rel() {
    local rel_path="$1"
    
    # Check if path starts with tilde
    if [[ "$rel_path" == "~"* ]]; then
        local abs_path="${rel_path#~}"
        echo "${HOME}${abs_path}"
    else
        echo "$rel_path"
    fi
}

# Convert absolute path to VDE root-relative path
# Usage: vde_path_to_vde_rel "/home/user/dev/data/postgres"
# Output: "data/postgres" (if VDE_ROOT_DIR is /home/user/dev)
vde_path_to_vde_rel() {
    local abs_path="$1"
    
    # Check if path starts with VDE_ROOT_DIR
    if [[ "$abs_path" == "$VDE_ROOT_DIR/"* ]] || [[ "$abs_path" == "$VDE_ROOT_DIR" ]]; then
        local rel_path="${abs_path#$VDE_ROOT_DIR}"
        if [[ -z "$rel_path" ]]; then
            echo "."
        else
            echo "${rel_path#/}"
        fi
    else
        echo "$abs_path"
    fi
}

# Convert VDE root-relative path to absolute path
# Usage: vde_path_from_vde_rel "data/postgres"
# Output: "/home/user/dev/data/postgres" (if VDE_ROOT_DIR is /home/user/dev)
vde_path_from_vde_rel() {
    local rel_path="$1"
    
    # Check if path is already absolute
    if [[ "$rel_path" == "/"* ]]; then
        echo "$rel_path"
    else
        echo "${VDE_ROOT_DIR}/${rel_path}"
    fi
}

# Extract just the directory name from an absolute path
# Usage: vde_dir_name "/home/user/projects/vde"
# Output: "vde"
vde_dir_name() {
    local abs_path="$1"
    echo "${abs_path:t}"
}

# Extract just the basename from a path
# Usage: vde_basename "/home/user/projects/vde/data"
# Output: "data"
vde_basename() {
    local path="$1"
    echo "${path:t}"
}

# Normalize a path (resolve . and .., remove trailing slashes)
# Usage: vde_normalize_path "/home/user/../user/./projects/vde/"
# Output: "/home/user/projects/vde"
vde_normalize_path() {
    local path="$1"
    
    # Use zsh's :A modifier to resolve to absolute path
    if [[ -e "$path" ]] || [[ -d "$path" ]]; then
        echo "${path:A}"
    else
        # For non-existent paths, do basic normalization
        echo "$path"
    fi
}

# Check if a path is inside another path
# Usage: vde_is_subpath "/home/user/projects/vde/data" "/home/user/projects/vde"
# Output: "yes" or "no"
vde_is_subpath() {
    local child_path="$1"
    local parent_path="$2"
    
    # Normalize both paths
    local normalized_child="${child_path:A}"
    local normalized_parent="${parent_path:A}"
    
    if [[ "$normalized_child" == "$normalized_parent/"* ]]; then
        echo "yes"
    else
        echo "no"
    fi
}

# Get the relative path from parent to child
# Usage: vde_relative_path "/home/user/projects" "/home/user/projects/vde/data"
# Output: "vde/data"
vde_relative_path() {
    local from_path="$1"
    local to_path="$2"
    
    local normalized_from="${from_path:A}"
    local normalized_to="${to_path:A}"
    
    if [[ "$normalized_to" == "$normalized_from/"* ]]; then
        echo "${normalized_to#$normalized_from/}"
    else
        echo "$normalized_to"
    fi
}

# =============================================================================
# PORTABLE PATH EXPANSION
# =============================================================================

# Expand tilde paths in a string (for cases where zsh doesn't auto-expand)
# Usage: vde_expand_tilde "~/.ssh/config"
# Output: "/home/user/.ssh/config"
vde_expand_tilde() {
    local path="$1"
    echo "${path//\~/$HOME}"
}

# Create a portable path representation for use in configs
# - For HOME-relative paths: use ~ notation
# - For VDE-relative paths: use relative notation
# - For other paths: use absolute path
# Usage: vde_portable_path "/home/user/.ssh/vde/id_ed25519"
# Output: "~/.ssh/vde/id_ed25519"
vde_portable_path() {
    local abs_path="$1"
    
    # Check if path is HOME-relative
    if [[ "$abs_path" == "$HOME/"* ]]; then
        vde_path_to_home_rel "$abs_path"
    # Check if path is VDE_ROOT_DIR-relative
    elif [[ "$abs_path" == "$VDE_ROOT_DIR/"* ]]; then
        vde_path_to_vde_rel "$abs_path"
    else
        echo "$abs_path"
    fi
}

# =============================================================================
# DOCKER PATH HANDLING
# =============================================================================

# Convert a local path to a Docker-compatible path for volume mounts
# Usage: vde_docker_volume_path "/home/user/.ssh/vde" "linux"
# Output: "/home/user/.ssh/vde"
vde_docker_volume_path() {
    local local_path="$1"
    local container_os="${2:-linux}"
    
    # For Linux containers, use host paths as-is (they're compatible)
    # For Windows/macOS, would need special handling (future enhancement)
    echo "$local_path"
}

# Get the appropriate HOME path for a container based on OS
# Usage: vde_container_home_path "linux"
# Output: "/home/dev"
vde_container_home_path() {
    local container_os="$1"
    
    case "$container_os" in
        linux|alpine|debian|ubuntu|fedora|centos)
            echo "/home/dev"
            ;;
        macos|osx)
            echo "/Users/dev"
            ;;
        windows)
            echo "C:\\Users\\dev"
            ;;
        *)
            echo "/home/dev"
            ;;
    esac
}

# =============================================================================
# END OF VDE PATH UTILS
# =============================================================================
