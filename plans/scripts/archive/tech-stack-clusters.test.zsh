#!/usr/bin/env zsh
# Unit Test: MEAN and LAMP Cluster Registration
# Part of Phase 29 Cluster Expansion

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/lib/vde-shell-compat"
source "$PROJECT_ROOT/lib/vde-constants"
source "$PROJECT_ROOT/lib/vde-naming"
source "$PROJECT_ROOT/lib/vde-core"
source "$PROJECT_ROOT/lib/vde-cluster-utils"

TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass() { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail() { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

test_cluster_contents() {
    local name="$1"
    local expected_vms="$2"
    test_start "Tech Stack Cluster: $name"
    
    if vde_cluster_exists "$name"; then
        vms=$(vde_cluster_get_vms "$name")
        local missing=0
        for vm in ${=expected_vms}; do
            if ! echo "$vms" | grep -q "$vm"; then
                test_fail "$name cluster contents" "Missing Spoke: $vm (Found: $vms)"
                missing=1
                break
            fi
        done
        if [[ $missing -eq 0 ]]; then
            test_pass "Cluster '$name' correctly registered with: $expected_vms"
        fi
    else
        test_fail "Cluster '$name' existence" "Cluster not found in state directory"
    fi
}

echo "=============================================="
echo "Tech Stack Cluster Unit Tests"
echo "=============================================="

test_cluster_contents "mean" "js mongodb"
test_cluster_contents "lamp" "php mysql nginx"

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
