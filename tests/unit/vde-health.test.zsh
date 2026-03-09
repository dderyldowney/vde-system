#!/usr/bin/env zsh
# Test framework
TESTS_PASSED=0
TESTS_FAILED=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'
test_start() { echo -e "${YELLOW}Testing: $1${RESET}" }
test_pass() { echo -e "  ${GREEN}✓ PASS: $1${RESET}"; ((TESTS_PASSED++)) }
test_fail() { echo -e "  ${RED}✗ FAIL: $1 - $2${RESET}"; ((TESTS_FAILED++)) }

# Source required libraries
source "$(dirname "$0")/../../lib/vde-constants"
source "$(dirname "$0")/../../lib/vde-shell-compat"
source "$(dirname "$0")/../../lib/vm-common"
source "$(dirname "$0")/../../lib/vde-docker-state"
source "$(dirname "$0")/../../lib/vde-health"

# Mock dependencies
get_vm_info() {
    local prop="$1"
    local vm_name="$2"
    if [[ "$vm_name" == "vde-python" || "$vm_name" == "vde-go" ]]; then
        echo "lang"
    elif [[ "$vm_name" == "vde-postgres" ]]; then
        echo "service"
    else
        echo "unknown"
    fi
}

docker() {
    local cmd="$1"
    shift
    if [[ "$cmd" == "ps" ]]; then
        if [[ "$MOCK_DOCKER_RUNNING" == "1" ]]; then
            echo "vde-python"
            echo "vde-postgres"
        else
            echo ""
        fi
        return 0
    elif [[ "$cmd" == "port" ]]; then
        if [[ "$MOCK_PORT_MAPPING" == "1" ]]; then
            echo "0.0.0.0:32768"
        else
            echo ""
        fi
        return 0
    fi
    return 1
}

nc() { [[ "$MOCK_PORT_OPEN" == "1" ]]; }
ssh() { 
    if [[ "$MOCK_SSH_SUCCESS" == "1" ]]; then
        local last_arg="${@: -1}"
        if [[ "$last_arg" == "echo 'ssh_ok'" ]]; then echo "ssh_ok"; fi
        return 0
    fi
    return 1
}
timeout() { shift; "$@"; }

# Test 1: vde_check_container_running
test_start "vde_check_container_running"
MOCK_DOCKER_RUNNING=1
if vde_check_container_running "vde-python"; then
    test_pass "detects running language container"
else
    test_fail "detects running language container" "failed to detect vde-python"
fi

MOCK_DOCKER_RUNNING=0
if vde_check_container_running "vde-python"; then
    test_fail "detects stopped container" "expected failure for stopped container"
else
    test_pass "detects stopped language container"
fi

# Test 2: vde_check_ssh_port
test_start "vde_check_ssh_port"
MOCK_PORT_MAPPING=1
MOCK_PORT_OPEN=1
if vde_check_ssh_port "vde-python" 5; then
    test_pass "detects open SSH port"
else
    test_fail "detects open SSH port" "failed to detect open port"
fi

MOCK_PORT_OPEN=0
vde_check_ssh_port "vde-python" 1
if [[ $? -eq $VDE_ERR_TIMEOUT ]]; then
    test_pass "detects closed SSH port (timeout)"
else
    test_fail "detects closed SSH port" "expected VDE_ERR_TIMEOUT"
fi

# Test 3: vde_check_ssh_login
test_start "vde_check_ssh_login"
MOCK_PORT_MAPPING=1
MOCK_SSH_SUCCESS=1
if vde_check_ssh_login "vde-python" 5; then
    test_pass "detects successful SSH login"
else
    test_fail "detects successful SSH login" "failed to detect successful login"
fi

# Test 4: vde_health_check (aggregate)
test_start "vde_health_check"
MOCK_DOCKER_RUNNING=1
MOCK_PORT_MAPPING=1
MOCK_PORT_OPEN=1
MOCK_SSH_SUCCESS=1
if vde_health_check "vde-python" 0; then
    test_pass "aggregate health check passes when all ok"
else
    test_fail "aggregate health check" "expected pass"
fi

MOCK_SSH_SUCCESS=0
if ! vde_health_check "vde-python" 0; then
    test_pass "aggregate health check fails when SSH fails"
else
    test_fail "aggregate health check" "expected failure when SSH fails"
fi

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED
