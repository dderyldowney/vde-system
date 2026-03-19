#!/usr/bin/env zsh
# Setup SSH agent for VDE tests
# This script is now a wrapper around lib/vde-ssh to ensure 
# consistent, isolated agent management.

# Usage:
#   source tests/setup-ssh-agent.zsh     # Setup and start agent
#   source tests/setup-ssh-agent.zsh --cleanup  # Cleanup (stop agent)

# Ensure VDE_ROOT_DIR is set (needed for sourcing libraries)
# Use script location for portability - two directories up from tests/
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h}}"

# Source VDE SSH library
if [[ -f "${VDE_ROOT_DIR}/lib/vde-ssh" ]]; then
    # We need to set VDE_ROOT_DIR before sourcing if not already set
    source "${VDE_ROOT_DIR}/lib/vde-ssh"
else
    echo "Error: lib/vde-ssh not found at ${VDE_ROOT_DIR}/lib/vde-ssh"
    return 1 2>/dev/null || exit 1
fi

# Cleanup function
cleanup_vde_ssh_agent() {
    # VDE_SSH_AGENT_ENV is defined in lib/vde-ssh
    if [[ -f "${VDE_SSH_AGENT_ENV}" ]]; then
        source "${VDE_SSH_AGENT_ENV}" >/dev/null 2>&1
        if [[ -n "${SSH_AGENT_PID}" ]] && ps -p "${SSH_AGENT_PID}" >/dev/null 2>&1; then
            echo "Stopping VDE SSH agent (PID: ${SSH_AGENT_PID})..."
            kill "${SSH_AGENT_PID}" 2>/dev/null
        fi
        rm -f "${VDE_SSH_AGENT_ENV}"
        echo "VDE SSH agent environment cleaned."
    else
        echo "No VDE SSH agent environment to cleanup."
    fi
    unset SSH_AUTH_SOCK SSH_AGENT_PID
}

# Main setup
setup_vde_ssh_agent() {
    echo "Setting up isolated SSH agent for VDE tests..."
    
    # ensure_ssh_agent is defined in lib/vde-ssh
    # It now uses ~/.ssh/vde/agent_env and ensures isolation
    if ensure_ssh_agent; then
        echo "VDE SSH agent is ready."
        echo "  PID: ${SSH_AGENT_PID}"
        echo "  SOCK: ${SSH_AUTH_SOCK}"
    else
        echo "Failed to set up VDE SSH agent."
        return 1
    fi
}

# Handle cleanup flag
if [[ "${1:-}" == "--cleanup" ]]; then
    cleanup_vde_ssh_agent
else
    setup_vde_ssh_agent
fi
