#!/usr/bin/env zsh
# Setup SSH agent for VDE tests
# Usage:
#   source tests/setup-ssh-agent.zsh     # Setup and start agent
#   source tests/setup-ssh-agent.zsh --cleanup  # Cleanup (stop agent)

# VDE SSH directory
VDE_SSH_DIR="$HOME/.ssh/vde"
VDE_SSH_KEY="$VDE_SSH_DIR/id_ed25519"

# Check if agent is already running and usable
check_agent() {
    # If variables are already set, check if they are valid
    if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "$SSH_AUTH_SOCK" ]; then
        if ssh-add -l >/dev/null 2>&1 || [ $? -eq 1 ]; then
            echo "Using existing SSH agent (PID: ${SSH_AGENT_PID:-unknown})"
            return 0
        fi
    fi

    # Try to find an existing agent from this user (common patterns)
    local agent_sock
    
    # 1. Standard Linux /tmp/ssh-* pattern
    agent_sock=$(find /tmp/ssh-* -name "agent.*" -user $(whoami) 2>/dev/null | head -n 1)
    
    # 2. macOS com.apple.launchd pattern
    if [ -z "$agent_sock" ]; then
        agent_sock=$(find /private/tmp/com.apple.launchd.* -name "Listeners" -user $(whoami) 2>/dev/null | head -n 1)
    fi

    if [ -n "$agent_sock" ] && [ -S "$agent_sock" ]; then
        export SSH_AUTH_SOCK="$agent_sock"
        # Extract PID from socket path if possible (usually /tmp/ssh-XXXXXX/agent.PID)
        # If not possible (like on macOS), we can try to get it from pgreg
        local pid=$(echo "$agent_sock" | grep -oE '[0-9]+$' | head -n 1)
        if [ -z "$pid" ]; then
            pid=$(pgrep -u $(whoami) ssh-agent | head -n 1)
        fi
        export SSH_AGENT_PID="$pid"
        
        if ssh-add -l >/dev/null 2>&1 || [ $? -eq 1 ]; then
            echo "Discovered existing SSH agent at $SSH_AUTH_SOCK"
            return 0
        fi
    fi
    
    return 1
}

# Start a new SSH agent
start_agent() {
    echo "Starting SSH agent..."
    eval "$(ssh-agent -s)" >/dev/null
    echo "SSH agent started (PID: $SSH_AGENT_PID)"
}

# Generate test SSH key if needed
generate_key() {
    mkdir -p "$VDE_SSH_DIR"
    
    if [ -f "$VDE_SSH_KEY" ]; then
        echo "SSH key already exists at $VDE_SSH_KEY"
    else
        echo "Generating SSH key at $VDE_SSH_KEY..."
        ssh-keygen -t ed25519 -f "$VDE_SSH_KEY" -N "" -q
    fi
}

# Add key to agent
add_key() {
    if ssh-add -l 2>/dev/null | grep -q "$VDE_SSH_KEY"; then
        echo "Key already loaded in agent"
    else
        ssh-add "$VDE_SSH_KEY" 2>/dev/null
        echo "Key added to agent"
    fi
}

# Cleanup function (call this after tests)
cleanup_ssh_agent() {
    if [ -n "$SSH_AGENT_PID" ] && kill -0 "$SSH_AGENT_PID" 2>/dev/null; then
        echo "Stopping SSH agent (PID: $SSH_AGENT_PID)..."
        kill "$SSH_AGENT_PID" 2>/dev/null
        unset SSH_AUTH_SOCK SSH_AGENT_PID
        echo "SSH agent stopped"
    else
        echo "No running SSH agent to cleanup"
    fi
}

# Main setup
setup_ssh_agent() {
    echo "Setting up SSH agent for VDE tests..."
    
    # Check if agent is already running
    if check_agent; then
        echo "Agent already running, verifying key..."
    else
        start_agent
    fi
    
    # Generate key if needed
    generate_key
    
    # Add key to agent
    add_key
    
    # Export environment variables for child processes
    export SSH_AUTH_SOCK
    export SSH_AGENT_PID
    
    echo ""
    echo "SSH Agent Setup Complete:"
    echo "  SSH_AUTH_SOCK: $SSH_AUTH_SOCK"
    echo "  SSH_AGENT_PID: $SSH_AGENT_PID"
    echo "  SSH Key: $VDE_SSH_KEY"
    echo ""
    echo "Environment variables exported for this shell session."
}

# Handle cleanup flag
if [[ "${1:-}" == "--cleanup" ]]; then
    cleanup_ssh_agent
else
    setup_ssh_agent
fi
