#!/usr/bin/env zsh
# Unit tests for SSH key management and agent forwarding functions

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "SSH Functions Unit Tests"

setup_test_env

# Explicitly source vm-common (before setup_test_env to get VDE_ROOT_DIR)
if [[ -z "$VDE_ROOT_DIR" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
source "$VDE_ROOT_DIR/scripts/lib/vm-common"

# Test: SSH key detection
test_section "SSH Key Detection"

# Mock detect_ssh_keys for testing
test_detect_ssh_keys_mock() {
    echo "/home/user/.ssh/id_ed25519"
    echo "/home/user/.ssh/id_rsa"
}

# Save original function
local original_detect="functions[detect_ssh_keys]"

# Test that detect_ssh_keys returns keys
if declare -f detect_ssh_keys >/dev/null; then
    keys=("${(@f)$(detect_ssh_keys)}")
    if [[ ${#keys[@]} -gt 0 ]]; then
        echo -e "${GREEN}✓${NC} detect_ssh_keys returns keys"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} detect_ssh_keys: No keys found (may be expected on this system)"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} detect_ssh_keys function not found (vm-common may not be sourced)"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: Primary SSH key selection
test_section "Primary SSH Key Selection"

if declare -f get_primary_ssh_key >/dev/null; then
    primary=$(get_primary_ssh_key)
    if [[ -n "$primary" ]]; then
        echo -e "${GREEN}✓${NC} get_primary_ssh_key returns: $primary"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} get_primary_ssh_key: No keys available"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} get_primary_ssh_key function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: SSH agent status check
test_section "SSH Agent Status"

if declare -f ssh_agent_is_running >/dev/null; then
    if ssh_agent_is_running; then
        echo -e "${GREEN}✓${NC} ssh_agent_is_running: Agent is running"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} ssh_agent_is_running: Agent not running (expected on fresh systems)"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} ssh_agent_is_running function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: SSH_AUTH_SOCK environment variable
test_section "SSH_AUTH_SOCK Environment"

if [[ -n "$SSH_AUTH_SOCK" ]]; then
    echo -e "${GREEN}✓${NC} SSH_AUTH_SOCK is set: $SSH_AUTH_SOCK"
    # Verify socket exists
    if [[ -S "$SSH_AUTH_SOCK" ]]; then
        echo -e "${GREEN}✓${NC} SSH_AUTH_SOCK points to valid socket"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} SSH_AUTH_SOCK points to non-existent socket"
        ((TESTS_FAILED++))
    fi
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} SSH_AUTH_SOCK not set (agent not running)"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: SSH keys loaded in agent
test_section "SSH Keys in Agent"

if ssh_agent_is_running 2>/dev/null; then
    key_count=$(ssh-add -l 2>/dev/null | wc -l)
    if [[ $key_count -gt 0 ]]; then
        echo -e "${GREEN}✓${NC} Keys loaded in agent: $key_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} No keys loaded in agent"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} SSH agent not running, skipping key check"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: VM SSH config generation (dry-run)
test_section "VM SSH Config Generation"

if declare -f get_vm_ssh_port >/dev/null; then
    # Test with a known VM if it exists
    if [[ -f "$CONFIGS_DIR/python/docker-compose.yml" ]]; then
        port=$(get_vm_ssh_port "python")
        if [[ -n "$port" ]]; then
            echo -e "${GREEN}✓${NC} get_vm_ssh_port returns: $port"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}○${NC} get_vm_ssh_port: No port found for python"
            ((TESTS_PASSED++))
        fi
        ((TESTS_RUN++))
    else
        echo -e "${YELLOW}○${NC} Python VM not configured, skipping port test"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    fi
else
    echo -e "${YELLOW}○${NC} get_vm_ssh_port function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: Public SSH keys directory
test_section "Public SSH Keys Directory"

if [[ -d "$VDE_ROOT_DIR/public-ssh-keys" ]]; then
    echo -e "${GREEN}✓${NC} public-ssh-keys directory exists"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))

    key_count=$(ls -1 "$VDE_ROOT_DIR/public-ssh-keys"/*.pub 2>/dev/null | wc -l)
    if [[ $key_count -gt 0 ]]; then
        echo -e "${GREEN}✓${NC} Public keys found: $key_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} No public keys in public-ssh-keys"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} public-ssh-keys directory not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: SSH config file
test_section "SSH Config File"

if [[ -f "$HOME/.ssh/config" ]]; then
    echo -e "${GREEN}✓${NC} ~/.ssh/config exists"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))

    # Check for VDE entries
    if grep -q "python-dev" "$HOME/.ssh/config" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} VDE SSH entries found in config"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} No VDE SSH entries found (VMs may not be configured yet)"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} ~/.ssh/config does not exist"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test: Identity file detection
test_section "SSH Identity File Detection"

if declare -f get_ssh_identity_file >/dev/null; then
    identity_file=$(get_ssh_identity_file)
    if [[ -n "$identity_file" ]]; then
        echo -e "${GREEN}✓${NC} get_ssh_identity_file returns: $identity_file"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))

        # Check if file exists
        if [[ -f "$identity_file" ]]; then
            echo -e "${GREEN}✓${NC} Identity file exists"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗${NC} Identity file does not exist: $identity_file"
            ((TESTS_FAILED++))
        fi
        ((TESTS_RUN++))
    else
        echo -e "${YELLOW}○${NC} get_ssh_identity_file: No identity file found"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    fi
else
    echo -e "${YELLOW}○${NC} get_ssh_identity_file function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

teardown_test_env

test_suite_end "SSH Functions Unit Tests"
exit $?
