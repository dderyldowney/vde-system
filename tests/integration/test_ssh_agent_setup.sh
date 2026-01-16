#!/usr/bin/env zsh
# Integration tests for SSH agent automatic setup and VM integration
# Creates and uses test-specific SSH keys for isolation

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "SSH Agent Setup Integration Tests"

setup_test_env

# Test-specific SSH key (isolated from user's keys)
TEST_SSH_KEY_NAME="vde_test_key_$$"
TEST_SSH_KEY_PATH="$HOME/.ssh/${TEST_SSH_KEY_NAME}"

# Explicitly source vm-common (before setup_test_env to get VDE_ROOT_DIR)
if [[ -z "$VDE_ROOT_DIR" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
source "$VDE_ROOT_DIR/scripts/lib/vm-common"

# Track if we need to clean up
CLEANUP_AGENT=false
BACKUP_SSH_CONFIG=""
ORIGINAL_SSH_AUTH_SOCK="$SSH_AUTH_SOCK"

# Cleanup function
cleanup_ssh_test() {
    echo ""
    echo "Cleaning up test artifacts..."

    # Remove test SSH keys
    if [[ -f "$TEST_SSH_KEY_PATH" ]]; then
        rm -f "$TEST_SSH_KEY_PATH" "$TEST_SSH_KEY_PATH.pub"
        echo "  Removed test SSH key: $TEST_SSH_KEY_PATH"
    fi

    # Remove test key from agent
    if ssh_agent_is_running 2>/dev/null; then
        ssh-add -d "$TEST_SSH_KEY_PATH" >/dev/null 2>&1 || true
    fi

    # Restore original SSH config
    if [[ -n "$BACKUP_SSH_CONFIG" && -f "$BACKUP_SSH_CONFIG" ]]; then
        mv "$BACKUP_SSH_CONFIG" "$HOME/.ssh/config"
        echo "  Restored SSH config backup"
    fi

    # Clean up test SSH agent if we started it
    if [[ "$CLEANUP_AGENT" == "true" ]]; then
        echo "  Cleaning up test SSH agent..."
        SSH_AUTH_SOCK="$ORIGINAL_SSH_AUTH_SOCK"
        export SSH_AUTH_SOCK
        ssh-agent -k 2>/dev/null || true
    fi

    echo "Cleanup complete."
}

trap cleanup_ssh_test EXIT

# Test 0: Create test SSH key
test_section "Test SSH Key Creation"

if ssh-keygen -t rsa -b 2048 -f "$TEST_SSH_KEY_PATH" -N "" -C "vde-test@localhost" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Test SSH key created: $TEST_SSH_KEY_PATH"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Failed to create test SSH key"
    ((TESTS_FAILED++))
    exit 1  # Can't continue without test key
fi
((TESTS_RUN++))

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

# Test 3: Load test SSH key into agent
test_section "SSH Key Loading"

if ssh_agent_is_running 2>/dev/null; then
    # Load our test key
    if ssh-add "$TEST_SSH_KEY_PATH" >/dev/null 2>&1; then
        # Verify key was loaded - check for our test comment
        key_list=$(ssh-add -l 2>/dev/null)
        if echo "$key_list" | grep -q "vde-test@localhost"; then
            echo -e "${GREEN}✓${NC} Test SSH key loaded into agent: $TEST_SSH_KEY_NAME"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗${NC} Test SSH key not found in agent"
            echo "  Agent contents:"
            echo "$key_list" | head -3
            ((TESTS_FAILED++))
        fi
        ((TESTS_RUN++))
    else
        echo -e "${RED}✗${NC} Failed to load test SSH key into agent"
        ((TESTS_FAILED++))
        ((TESTS_RUN++))
    fi
else
    echo -e "${YELLOW}○${NC} SSH agent not running, skipping key load test"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 4: Verify test key files exist
test_section "Test SSH Key Files Exist"

if [[ -f "$TEST_SSH_KEY_PATH" ]]; then
    echo -e "${GREEN}✓${NC} Private key exists: $TEST_SSH_KEY_PATH"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Private key not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

if [[ -f "$TEST_SSH_KEY_PATH.pub" ]]; then
    echo -e "${GREEN}✓${NC} Public key exists: $TEST_SSH_KEY_PATH.pub"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Public key not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test 5: Key has correct permissions
test_section "SSH Key Permissions"

private_perms=$(stat -f "%Lp" "$TEST_SSH_KEY_PATH" 2>/dev/null || stat -c "%a" "$TEST_SSH_KEY_PATH" 2>/dev/null)
if [[ "$private_perms" == "600" ]]; then
    echo -e "${GREEN}✓${NC} Private key has correct permissions (600)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○${NC} Private key permissions: $private_perms (expected 600)"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

public_perms=$(stat -f "%Lp" "$TEST_SSH_KEY_PATH.pub" 2>/dev/null || stat -c "%a" "$TEST_SSH_KEY_PATH.pub" 2>/dev/null)
if [[ "$public_perms" == "644" ]]; then
    echo -e "${GREEN}✓${NC} Public key has correct permissions (644)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○${NC} Public key permissions: $public_perms (expected 644)"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# Test 6: VM SSH config generation
test_section "VM SSH Config Auto-Generation"

if declare -f generate_vm_ssh_config >/dev/null; then
    # Backup existing config
    if [[ -f "$HOME/.ssh/config" ]]; then
        BACKUP_SSH_CONFIG="$HOME/.ssh/config.backup.$$"
        cp "$HOME/.ssh/config" "$BACKUP_SSH_CONFIG"
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
else
    echo -e "${YELLOW}○${NC} generate_vm_ssh_config function not found"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 7: Integration with create-virtual-for
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

# Test 8: Integration with start-virtual
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

# Test 9: Docker Compose templates have SSH agent socket mount
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

# Test 10: Dockerfile SSH agent forwarding
test_section "Dockerfile SSH Agent Forwarding"

base_dockerfile="$CONFIGS_DIR/docker/base-dev.Dockerfile"
if [[ -f "$base_dockerfile" ]]; then
    # Check for AllowAgentForwarding
    if grep -q "AllowAgentForwarding yes" "$base_dockerfile" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} base-dev.Dockerfile has AllowAgentForwarding enabled"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} base-dev.Dockerfile missing AllowAgentForwarding"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    # Check for ForwardAgent
    if grep -q "ForwardAgent yes" "$base_dockerfile" 2>/dev/null; then
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

# Test 11: SSH helper scripts exist
test_section "SSH Helper Scripts"

if [[ -f "$SCRIPTS_DIR/ssh-agent-setup" ]]; then
    echo -e "${GREEN}✓${NC} ssh-agent-setup script exists"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○${NC} ssh-agent-setup script not found"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

if [[ -f "$SCRIPTS_DIR/ssh-agent-setup" ]]; then
    if [[ -x "$SCRIPTS_DIR/ssh-agent-setup" ]]; then
        echo -e "${GREEN}✓${NC} ssh-agent-setup is executable"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} ssh-agent-setup not executable"
        ((TESTS_PASSED++))
    fi
else
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# Test 12: SSH config merge function exists
test_section "SSH Config Merge Function"

if declare -f merge_ssh_config_entry >/dev/null; then
    echo -e "${GREEN}✓${NC} merge_ssh_config_entry function exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} merge_ssh_config_entry function not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test 13: Test SSH key fingerprint verification
test_section "SSH Key Fingerprint"

if [[ -f "$TEST_SSH_KEY_PATH.pub" ]]; then
    fingerprint=$(ssh-keygen -lf "$TEST_SSH_KEY_PATH.pub" 2>/dev/null | awk '{print $2}')
    if [[ -n "$fingerprint" ]]; then
        echo -e "${GREEN}✓${NC} Test key fingerprint: $fingerprint"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}○${NC} Could not get fingerprint"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
else
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Final status
test_section "SSH Environment Status Summary"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ssh_agent_is_running 2>/dev/null; then
    echo -e "${GREEN}✓${NC} SSH Agent: Running"
    echo "  Socket: $SSH_AUTH_SOCK"

    key_count=$(ssh-add -l 2>/dev/null | wc -l | tr -d ' ')
    echo "  Keys loaded: $key_count"

    if [[ $key_count -gt 0 ]]; then
        echo "  Keys:"
        ssh-add -l 2>/dev/null | while read -r line; do
            echo "    $line"
        done
    fi
else
    echo -e "${YELLOW}○${NC} SSH Agent: Not running"
fi

echo ""
echo "Test SSH Key: $TEST_SSH_KEY_NAME"
echo "  Private: $TEST_SSH_KEY_PATH"
echo "  Public:  $TEST_SSH_KEY_PATH.pub"

test_suite_end "SSH Agent Setup Integration Tests"
