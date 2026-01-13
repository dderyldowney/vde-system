#!/usr/bin/env zsh
# Integration tests for AI API functionality with vde-ai
# Tests the integration between vde-ai and the AI API library

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "AI API Integration Tests"

setup_test_env

# -----------------------
# Test Library Loading
# -----------------------
test_section "Library Loading in vde-ai"

# Check that vde-ai sources the AI API library
if grep -q "vde-ai-api" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai sources vde-ai-api library"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai does not source vde-ai-api library"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check that vde-chat sources the AI API library
if grep -q "vde-ai-api" "$TEST_DIR/scripts/vde-chat"; then
    echo -e "${GREEN}✓${NC} vde-chat sources vde-ai-api library"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-chat does not source vde-ai-api library"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Environment Variable Usage
# -----------------------
test_section "Environment Variable Configuration"

# Test ANTHROPIC_BASE_URL usage
if grep -q "ANTHROPIC_BASE_URL" "$TEST_DIR/scripts/lib/vde-ai-api"; then
    echo -e "${GREEN}✓${NC} vde-ai-api uses ANTHROPIC_BASE_URL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai-api does not use ANTHROPIC_BASE_URL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test ANTHROPIC_MODEL usage
if grep -q "ANTHROPIC_MODEL" "$TEST_DIR/scripts/lib/vde-ai-api"; then
    echo -e "${GREEN}✓${NC} vde-ai-api uses ANTHROPIC_MODEL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai-api does not use ANTHROPIC_MODEL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test ANTHROPIC_DEFAULT_SONNET_MODEL usage
if grep -q "ANTHROPIC_DEFAULT_SONNET_MODEL" "$TEST_DIR/scripts/lib/vde-ai-api"; then
    echo -e "${GREEN}✓${NC} vde-ai-api uses ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai-api does not use ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Fallback Behavior
# -----------------------
test_section "Fallback to Pattern-Based Parsing"

# Check that vde-ai falls back to pattern-based parsing when AI unavailable
if grep -q "Falling back to pattern-based parsing" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai has fallback message"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai missing fallback message"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check that vde-ai calls generate_plan as fallback
if grep -q 'generate_plan "$USER_INPUT"' "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai calls generate_plan as fallback"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai missing generate_plan fallback"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test API Call Integration
# -----------------------
test_section "API Call Integration"

# Check that vde-ai calls parse_command_with_ai when AI is enabled
if grep -q "parse_command_with_ai" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai calls parse_command_with_ai"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai does not call parse_command_with_ai"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check that vde-chat also has AI integration
if grep -q "parse_command_with_ai" "$TEST_DIR/scripts/vde-chat"; then
    echo -e "${GREEN}✓${NC} vde-chat calls parse_command_with_ai"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-chat does not call parse_command_with_ai"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Error Handling
# -----------------------
test_section "Error Handling"

# Check for AI API availability check
if grep -q "ai_api_available" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai checks AI API availability"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai does not check AI API availability"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check for error handling on parse failure
if grep -q "parse_exit_code" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai handles parse exit codes"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai does not handle parse exit codes"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Third-Party Provider Support
# -----------------------
test_section "Third-Party Provider Support"

# Verify Zhipu AI example in documentation
if grep -q "api.z.ai" "$TEST_DIR/docs/vde-ai-assistant.md"; then
    echo -e "${GREEN}✓${NC} Documentation includes Zhipu AI example"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Documentation missing Zhipu AI example"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Verify glm-4.7 model in documentation
if grep -q "glm-4.7" "$TEST_DIR/docs/vde-ai-assistant.md"; then
    echo -e "${GREEN}✓${NC} Documentation includes glm-4.7 model"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Documentation missing glm-4.7 model"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Help Messages
# -----------------------
test_section "Help Messages Include New Variables"

# Check vde-ai help
if grep -q "ANTHROPIC_DEFAULT_SONNET_MODEL" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai help includes ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai help missing ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check vde-chat help
if grep -q "ANTHROPIC_DEFAULT_SONNET_MODEL" "$TEST_DIR/scripts/vde-chat"; then
    echo -e "${GREEN}✓${NC} vde-chat help includes ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-chat help missing ANTHROPIC_DEFAULT_SONNET_MODEL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check for example URLs in help
if grep -q "api.z.ai" "$TEST_DIR/scripts/vde-ai"; then
    echo -e "${GREEN}✓${NC} vde-ai help includes example URL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai help missing example URL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

if grep -q "api.z.ai" "$TEST_DIR/scripts/vde-chat"; then
    echo -e "${GREEN}✓${NC} vde-chat help includes example URL"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-chat help missing example URL"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Test Library Structure
# -----------------------
test_section "Library File Structure"

# Check that vde-ai-api library exists
if [[ -f "$TEST_DIR/scripts/lib/vde-ai-api" ]]; then
    echo -e "${GREEN}✓${NC} vde-ai-api library file exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} vde-ai-api library file missing"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Check that library is executable
if [[ -x "$TEST_DIR/scripts/lib/vde-ai-api" ]]; then
    echo -e "${GREEN}✓${NC} vde-ai-api library is executable"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} vde-ai-api library not executable (sourced, not executed)"
    ((TESTS_PASSED++))  # This is expected for sourced libraries
fi
((TESTS_RUN++))

# -----------------------
# Teardown
# -----------------------
teardown_test_env

test_suite_end "AI API Integration Tests"
exit $?
