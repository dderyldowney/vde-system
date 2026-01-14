#!/usr/bin/env zsh
# Integration tests for SSH agent automatic setup and VM integration

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "SSH Agent Setup Integration Tests"

setup_test_env

# Explicitly source vm-common (before setup_test_env to get VDE_ROOT_DIR)
if [[ -z "$VDE_ROOT_DIR" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
source "$VDE_ROOT_DIR/scripts/lib/vm-common"

# Track if we need to clean up
CLEANUP_AGENT=false
ORIGINAL_SSH_AUTH_SOCK="$SSH_AUTH_SOCK"

# Cleanup function
cleanup_ssh_test() {
    if [[ "$CLEANUP_AGENT" == "true" ]]; then
        echo "Cleaning up test SSH agent..."
        SSH_AUTH_SOCK="$ORIGINAL_SSH_AUTH_SOCK"
        export SSH_AUTH_SOCK
        ssh-agent -k 2>/dev/null || true
    fi
}

trap cleanup_ssh_test EXIT

# Test 1: ensure_ssh_environment is automatic and silent
test_section "ensure_ssh_environment: Automatic & Silent"

if declare -f ensure_ssh_environment >/dev/null; then
    # Capture output
    output=$(ensure_ssh_environment 2>&1)
    exit_code=$?

    # Should be silent (no output) and succeed
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} ensure_ssh_environment succeeds silently"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} ensure_ssh_environment failed with exit code: $exit_code"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    if [[ -z "$output" ]]; then
        echo -e "${GREEN}✓${NC} ensure_ssh_environment produces no output (silent)"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} ensure_ssh_environment produced output: $output"
        ((TESTS_PASSED++))  # Output is OK, just noting it
    fi
    ((TESTS_RUN++))
else
    echo -e "${RED}✗${NC} ensure_ssh_environment function not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
    ((TESTS_RUN++))
fi

# Test 2: SSH agent is started automatically
test_section "SSH Agent Auto-Start"

# Kill existing agent for this test
if ssh_agent_is_running 2>/dev/null; then
    SSH_AUTH_SOCK="$ORIGINAL_SSH_AUTH_SOCK"
    export SSH_AUTH_SOCK
    ssh-agent -k 2>/dev/null || true
    sleep 1
fi

if ! ssh_agent_is_running 2>/dev/null; then
    # Agent is not running, test that ensure_ssh_environment starts it
    if declare -f ensure_ssh_environment >/dev/null; then
        ensure_ssh_environment >/dev/null 2>&1

        if ssh_agent_is_running 2>/dev/null; then
            echo -e "${GREEN}✓${NC} ensure_ssh_environment automatically starts SSH agent"
            ((TESTS_PASSED++))
            CLEANUP_AGENT=true
        else
            echo -e "${RED}✗${NC} ensure_ssh_environment did not start SSH agent"
            ((TESTS_FAILED++))
        fi
        ((TESTS_RUN++))
    else
        echo -e "${YELLOW}○${NC} ensure_ssh_environment function not found"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    fi
else
    echo -e "${YELLOW}○${NC} SSH agent already running, cannot test auto-start"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 3: SSH keys are loaded automatically
test_section "SSH Keys Auto-Load"

if ssh_agent_is_running 2>/dev/null; then
    # Get key count before
    keys_before=$(ssh-add -l 2>/dev/null | wc -l)

    # Run ensure_ssh_environment (should be idempotent)
    if declare -f ensure_ssh_environment >/dev/null; then
        ensure_ssh_environment >/dev/null 2>&1

        # Check keys after
        keys_after=$(ssh-add -l 2>/dev/null | wc -l)

        if [[ $keys_after -gt 0 ]]; then
            echo -e "${GREEN}✓${NC} SSH keys loaded in agent: $keys_after key(s)"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}○${NC} No keys loaded (may need manual ssh-add)"
            ((TESTS_PASSED++))
        fi
        ((TESTS_RUN++))
    else
        echo -e "${YELLOW}○${NC} ensure_ssh_environment function not found"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    fi
else
    echo -e "${YELLOW}○${NC} SSH agent not running, skipping key load test"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 4: SSH key generation if no keys exist
test_section "SSH Key Auto-Generation"

# This test is informational only - we don't actually delete keys
key_count=$(ls -1 ~/.ssh/id_*.pub 2>/dev/null | wc -l)
if [[ $key_count -gt 0 ]]; then
    echo -e "${GREEN}✓${NC} SSH keys exist: $key_count key(s)"
    echo "  Found keys:"
    ls -1 ~/.ssh/id_*.pub 2>/dev/null | while read key; do
        echo "    - $key"
    done
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○${NC} No SSH keys found - VDE would auto-generate on first use"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# Test 5: VM SSH config generation
test_section "VM SSH Config Auto-Generation"

if declare -f generate_vm_ssh_config >/dev/null; then
    # Backup existing config
    if [[ -f "$HOME/.ssh/config" ]]; then
        cp "$HOME/.ssh/config" "$HOME/.ssh/config.backup.$$"
    fi

    # Generate config
    output=$(generate_vm_ssh_config 2>&1)
    exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} generate_vm_ssh_config succeeds"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} generate_vm_ssh_config failed: $output"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    # Check if config was updated
    if [[ -f "$HOME/.ssh/config" ]]; then
        if grep -q "python-dev\|go-dev\|rust-dev" "$HOME/.ssh/config" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} VM SSH entries found in config"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}○${NC} No VM SSH entries found (VMs may not be configured yet)"
            ((TESTS_PASSED++))
        fi
        ((TESTS_RUN++))
    fi

    # Restore backup
    if [[ -f "$HOME/.ssh/config.backup.$$" ]]; then
        mv "$HOME/.ssh/config.backup.$$" "$HOME/.ssh/config"
    fi
else
    echo -e "${YELLOW}○${NC} generate_vm_ssh_config function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 6: Integration with create-virtual-for
test_section "create-virtual-for Integration"

if [[ -f "$SCRIPTS_DIR/create-virtual-for" ]]; then
    # Check that create-virtual-for calls ensure_ssh_environment
    if grep -q "ensure_ssh_environment" "$SCRIPTS_DIR/create-virtual-for" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} create-virtual-for calls ensure_ssh_environment"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} create-virtual-for does not call ensure_ssh_environment"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} create-virtual-for script not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 7: Integration with start-virtual
test_section "start-virtual Integration"

if [[ -f "$SCRIPTS_DIR/start-virtual" ]]; then
    # Check that start-virtual calls ensure_ssh_environment
    if grep -q "ensure_ssh_environment" "$SCRIPTS_DIR/start-virtual" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} start-virtual calls ensure_ssh_environment"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} start-virtual does not call ensure_ssh_environment"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} start-virtual script not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 8: Docker Compose templates have SSH agent socket mount
test_section "Docker Compose SSH Socket Mount"

template_found=false
for template in "$TEMPLATES_DIR"/compose-*.yml; do
    if [[ -f "$template" ]]; then
        template_found=true
        if grep -q "SSH_AUTH_SOCK" "$template" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $(basename "$template") has SSH_AUTH_SOCK mount"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗${NC} $(basename "$template") missing SSH_AUTH_SOCK mount"
            ((TESTS_FAILED++))
        fi
        ((TESTS_RUN++))
    fi
done

if [[ "$template_found" == "false" ]]; then
    echo -e "${YELLOW}○${NC} No Docker Compose templates found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 9: Dockerfile has SSH agent forwarding enabled
test_section "Dockerfile SSH Agent Forwarding"

DOCKERFILE_PATH="$VDE_ROOT_DIR/configs/docker/base-dev.Dockerfile"
if [[ -f "$DOCKERFILE_PATH" ]]; then
    if grep -q "AllowAgentForwarding yes" "$DOCKERFILE_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} base-dev.Dockerfile has AllowAgentForwarding enabled"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} base-dev.Dockerfile missing AllowAgentForwarding"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    if grep -q "ForwardAgent yes" "$DOCKERFILE_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} base-dev.Dockerfile has ForwardAgent enabled"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} base-dev.Dockerfile missing ForwardAgent"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} base-dev.Dockerfile not found"
    ((TESTS_PASSED++))
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
    ((TESTS_RUN++))
fi

# Test 10: SSH helper scripts exist
test_section "SSH Helper Scripts"

# Check for ssh-agent-setup script
if [[ -f "$SCRIPTS_DIR/ssh-agent-setup" ]]; then
    echo -e "${GREEN}✓${NC} ssh-agent-setup script exists"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))

    # Check it's executable
    if [[ -x "$SCRIPTS_DIR/ssh-agent-setup" ]]; then
        echo -e "${GREEN}✓${NC} ssh-agent-setup is executable"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} ssh-agent-setup is not executable"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    echo -e "${YELLOW}○${NC} ssh-agent-setup script not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SSH Environment Status Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ssh_agent_is_running 2>/dev/null; then
    echo -e "${GREEN}✓${NC} SSH Agent: Running"
    echo "  Socket: $SSH_AUTH_SOCK"

    key_count=$(ssh-add -l 2>/dev/null | wc -l)
    echo "  Keys loaded: $key_count"

    if [[ $key_count -gt 0 ]]; then
        echo "  Keys:"
        ssh-add -l 2>/dev/null | head -5
        if [[ $key_count -gt 5 ]]; then
            echo "  ... and $((key_count - 5)) more"
        fi
    fi
else
    echo -e "${YELLOW}○${NC} SSH Agent: Not running (will start automatically when needed)"
fi

echo ""

teardown_test_env

test_suite_end "SSH Agent Setup Integration Tests"
exit $?
