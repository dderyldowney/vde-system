#!/usr/bin/env zsh
# Unit Test: 8-Field Translation Alignment
# Verifies that field 7 -> service_port and field 8 -> ssh_port

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/lib/vde-shell-compat"
source "$PROJECT_ROOT/lib/vde-constants"
source "$PROJECT_ROOT/lib/vde-naming"
source "$PROJECT_ROOT/lib/vde-core"

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

test_start "8-Field Mapping Audit"

# Create a sample .conf line
local tmp_conf="/tmp/test_mapping.conf"
local tmp_json="/tmp/test_mapping.json"
echo "service|vde-test|test|Test VM||zsh /vde/scripts/setup/test-init.zsh|8080|2222" > $tmp_conf

# Run translation
vde_translate_conf_to_json "$tmp_conf" "$tmp_json" >/dev/null 2>&1

# Verify JSON mapping
if grep -q "\"service_port\": \"8080\"" "$tmp_json" && grep -q "\"ssh_port\": 2222" "$tmp_json"; then
    test_pass "Fields 7 and 8 correctly mapped to service_port and ssh_port"
else
    test_fail "Field Mapping" "Mapping failed. JSON content:\n$(cat $tmp_json)"
fi

rm -f $tmp_conf $tmp_json

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
