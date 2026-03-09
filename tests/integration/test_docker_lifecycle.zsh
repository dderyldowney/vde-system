#!/usr/bin/env zsh
# =============================================================================
# test_docker_lifecycle.zsh — Docker VM lifecycle integration test
#
# Tests the full: create → start → wait → assert → shutdown cycle.
# Requires Docker daemon to be running. Skips gracefully if it's not.
#
# Usage:
#   zsh tests/integration/test_docker_lifecycle.zsh [vm_name]
#   make test-docker
# =============================================================================

setopt ERR_EXIT PIPE_FAIL 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source shared utilities
source "$PROJECT_ROOT/tests/lib/docker-test-utils.zsh"

# The VM to test — prefer argument, then env var, then pick randomly
if [[ -n "${1:-}" ]]; then
    TEST_VM="$1"
elif [[ -n "${VDE_TEST_VM:-}" ]]; then
    TEST_VM="$VDE_TEST_VM"
else
    ALL_VMS=(c cpp asm python rust js csharp ruby go java kotlin swift php scala r lua flutter elixir haskell postgres redis mongodb nginx couchdb mysql rabbitmq)
    INDEX=$(( RANDOM % ${#ALL_VMS[@]} ))
    TEST_VM="${ALL_VMS[$INDEX]}"
fi

echo ""
echo "============================================================"
echo " VDE Docker Lifecycle Integration Test"
echo " VM: $TEST_VM"
echo " Timeout: /usr/local/bin/timeout (600s per phase)"
echo "============================================================"

# =============================================================================
# Setup: pre-clean, Docker check, SSH agent, EXIT trap
# =============================================================================
docker_test_setup "$TEST_VM"    # handles cleanup, Docker check, agent, trap

# =============================================================================
# Counters
# =============================================================================
TESTS_PASSED=0
TESTS_FAILED=0

pass() { echo "  ✓ $1"; (( TESTS_PASSED++ )) }
fail() { echo "  ✗ $1: $2" >&2; (( TESTS_FAILED++ )) }

# =============================================================================
# Phase 1: create-virtual-for
# =============================================================================
echo ""
echo "--- Phase 1: create-virtual-for $TEST_VM ---"

if /usr/local/bin/timeout 300 "$PROJECT_ROOT/bin/create-virtual-for" "$TEST_VM"; then
    pass "create-virtual-for $TEST_VM"
else
    fail "create-virtual-for $TEST_VM" "exit $?"
    echo "[ABORT] Cannot continue without VM creation — run 'make docker-clean' to retry"
    exit 1
fi

# =============================================================================
# Phase 2: start-virtual
# =============================================================================
echo ""
echo "--- Phase 2: start-virtual $TEST_VM ---"

if /usr/local/bin/timeout 300 "$PROJECT_ROOT/bin/start-virtual" "$TEST_VM"; then
    pass "start-virtual $TEST_VM"
else
    fail "start-virtual $TEST_VM" "exit $?"
    exit 1
fi

# =============================================================================
# Phase 3: wait for readiness
# =============================================================================
echo ""
echo "--- Phase 3: wait for container readiness ---"

if wait_for_container_ready "$TEST_VM" 120; then
    pass "Container $TEST_VM is ready"
else
    fail "Container $TEST_VM readiness" "timed out or unhealthy"
    exit 1
fi

# =============================================================================
# Phase 4: assertions
# =============================================================================
echo ""
echo "--- Phase 4: assertions ---"

# 4a: Container is running
CONTAINER_NAME="vde-${TEST_VM##vde-}"
STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null)
if [[ "$STATUS" == "running" ]]; then
    pass "Container status is 'running'"
else
    fail "Container status" "expected 'running', got '$STATUS'"
fi

# 4b: SSH port is allocated (registry file exists)
PORT_REGISTRY="${VDE_PORT_REGISTRY:-$PROJECT_ROOT/.cache/port-registry}"
RAW="${TEST_VM##vde-}"
if [[ -f "$PORT_REGISTRY/${RAW}.port" ]] || [[ -f "$PORT_REGISTRY/${CONTAINER_NAME}.port" ]]; then
    pass "SSH port registry entry exists"
else
    # Try querying live
    SSH_PORT=$(grep -oE '[0-9]+:22' "$PROJECT_ROOT/configs/docker/${RAW}/docker-compose.yml" 2>/dev/null | head -1 | cut -d: -f1)
    if [[ -n "$SSH_PORT" ]]; then
        pass "SSH port readable from compose file: $SSH_PORT"
    else
        fail "SSH port" "no registry entry and no compose port found"
    fi
fi

# 4c: Docker state JSON exists
STATE_FILE="$PROJECT_ROOT/.docker-state/${CONTAINER_NAME}.json"
if [[ -f "$STATE_FILE" ]]; then
    pass "Docker state file exists: ${STATE_FILE##*/}"
else
    fail "Docker state file" "not found: $STATE_FILE"
fi

# 4d: vde ask recognizes the VM
PLAN=$(VDE_LOG_LEVEL=ERROR "$PROJECT_ROOT/bin/vde" ask "status of ${RAW}" 2>/dev/null)
if echo "$PLAN" | grep -q "running\|started"; then
    pass "vde ask reports VM as running"
else
    # Not a hard failure — just informational
    echo "  ⚠ vde ask status output: ${PLAN:-<empty>}"
fi

# =============================================================================
# Phase 5: shutdown-virtual
# =============================================================================
echo ""
echo "--- Phase 5: shutdown-virtual $TEST_VM ---"

if /usr/local/bin/timeout 120 "$PROJECT_ROOT/bin/shutdown-virtual" "$TEST_VM"; then
    pass "shutdown-virtual $TEST_VM"
else
    fail "shutdown-virtual $TEST_VM" "exit $?"
fi

# Confirm stopped
sleep 3
STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "not_found")
if [[ "$STATUS" != "running" ]]; then
    pass "Container stopped (status: $STATUS)"
else
    fail "Container stop" "container still running after shutdown"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "============================================================"
echo " Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "============================================================"

[[ $TESTS_FAILED -eq 0 ]]
