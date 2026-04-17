#!/usr/bin/env zsh
# Unit Test: ELK Cluster Registration
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

test_start "ELK Cluster Registration"

# Verify cluster existence
if vde_cluster_exists "elk"; then
    vms=$(vde_cluster_get_vms "elk")
    if echo "$vms" | grep -q "elasticsearch" && echo "$vms" | grep -q "logstash" && echo "$vms" | grep -q "kibana"; then
        test_pass "ELK cluster registered with correct Spokes"
    else
        test_fail "ELK cluster contents" "Found VMs: $vms"
    fi
else
    test_fail "ELK cluster existence" "Cluster 'elk' not found in state directory"
fi

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
