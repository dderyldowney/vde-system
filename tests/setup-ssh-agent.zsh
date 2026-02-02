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
    if [ -n "$SSH_AUTH_SOCK" ] && ssh-add -l >/dev/null 2>&1; then
        echo "SSH agent already running (PID: $SSH_AGENT_PID)"
        return 0
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
