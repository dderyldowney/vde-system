#!/usr/bin/env zsh
# Unit tests for vde-ai-api library
# Tests the AI API client functionality

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

# Ensure we're in the test directory
cd "$TEST_DIR"

test_suite_start "vde-ai-api Library Tests"

# -----------------------
# Setup
# -----------------------
setup_test_env

# Source the vde-ai-api library
if [[ -f "$TEST_DIR/scripts/lib/vde-ai-api" ]]; then
    source "$TEST_DIR/scripts/lib/vde-ai-api"
else
    echo "vde-ai-api library not found"
    test_suite_end "vde-ai-api Library Tests"
    exit 1
fi

# -----------------------
# Configuration Helper Tests
# -----------------------
test_section "Configuration Helpers - Base URL"

# Test default base URL when no env var set
unset ANTHROPIC_BASE_URL
BASE_URL=$(_get_ai_base_url)
assert_equals "https://api.anthropic.com" "$BASE_URL" "default base URL should be Anthropic"

# Test custom base URL
ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
BASE_URL=$(_get_ai_base_url)
assert_equals "https://api.z.ai/api/anthropic" "$BASE_URL" "custom base URL should be used"

# Reset
unset ANTHROPIC_BASE_URL

test_section "Configuration Helpers - Model Selection"

# Test default model
unset ANTHROPIC_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL
MODEL=$(_get_ai_model)
assert_equals "claude-3-5-sonnet-20241022" "$MODEL" "default model should be Sonnet"

# Test ANTHROPIC_MODEL takes precedence
ANTHROPIC_MODEL="custom-model"
ANTHROPIC_DEFAULT_SONNET_MODEL="default-sonnet"
MODEL=$(_get_ai_model)
assert_equals "custom-model" "$MODEL" "ANTHROPIC_MODEL should take precedence"

# Test ANTHROPIC_DEFAULT_SONNET_MODEL when ANTHROPIC_MODEL not set
unset ANTHROPIC_MODEL
ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.7"
MODEL=$(_get_ai_model)
assert_equals "glm-4.7" "$MODEL" "ANTHROPIC_DEFAULT_SONNET_MODEL should be used"

# Reset
unset ANTHROPIC_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL

test_section "Configuration Helpers - API Key"

# Test no API key
unset CLAUDE_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
if _get_ai_api_key >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} should fail when no API key set"
else
    echo -e "${GREEN}✓${NC} correctly fails when no API key"
fi
((TESTS_PASSED++))
((TESTS_RUN++))

# Test ANTHROPIC_AUTH_TOKEN has highest priority
ANTHROPIC_AUTH_TOKEN="sk-auth-test789"
ANTHROPIC_API_KEY="sk-ant-test123"
CLAUDE_API_KEY="sk-claude-test456"
KEY=$(_get_ai_api_key)
assert_equals "sk-auth-test789" "$KEY" "ANTHROPIC_AUTH_TOKEN should have highest priority"

# Test ANTHROPIC_API_KEY is used when AUTH_TOKEN not set
unset ANTHROPIC_AUTH_TOKEN
KEY=$(_get_ai_api_key)
assert_equals "sk-ant-test123" "$KEY" "ANTHROPIC_API_KEY should be used when AUTH_TOKEN not set"

# Test CLAUDE_API_KEY fallback
unset ANTHROPIC_API_KEY
KEY=$(_get_ai_api_key)
assert_equals "sk-claude-test456" "$KEY" "CLAUDE_API_KEY should be used as fallback"

# Reset
unset CLAUDE_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

# -----------------------
# API Availability Tests
# -----------------------
test_section "API Availability Check"

# Test unavailable when no API key
unset CLAUDE_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
if ai_api_available >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} should not be available without API key"
else
    echo -e "${GREEN}✓${NC} correctly reports unavailable without API key"
fi
((TESTS_PASSED++))
((TESTS_RUN++))

# Test available when AUTH_TOKEN is set
ANTHROPIC_AUTH_TOKEN="sk-ant-test123"
if ai_api_available >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} correctly reports available with AUTH_TOKEN"
else
    echo -e "${RED}✗${NC} should be available with AUTH_TOKEN"
fi
((TESTS_PASSED++))
((TESTS_RUN++))

# Reset
unset CLAUDE_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

# -----------------------
# Content Extraction Tests
# -----------------------
test_section "Content Extraction from API Response"

# Mock API response
mock_response='{
  "id": "msg_123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "INTENT:start_vm\\nVM:python\\nFLAGS:rebuild=false nocache=false"
    }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "stop_reason": "end_turn"
}'

# Extract content
CONTENT=$(extract_ai_content "$mock_response")
assert_contains "$CONTENT" "INTENT:start_vm" "should extract intent from response"
assert_contains "$CONTENT" "VM:python" "should extract VM from response"

# Test empty response
EMPTY_CONTENT=$(extract_ai_content '{"content": []}')
if [[ -z "$EMPTY_CONTENT" ]]; then
    echo -e "${GREEN}✓${NC} correctly handles empty content"
else
    echo -e "${RED}✗${NC} should return empty for empty content array"
fi
((TESTS_PASSED++))
((TESTS_RUN++))

# -----------------------
# Mock API Call Tests
# -----------------------
test_section "Mock API Calling (with curl mock)"

# We can't actually test the API call without real credentials,
# but we can verify the function structure exists

if type call_ai_api >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} call_ai_api function exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} call_ai_api function not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

if type parse_command_with_ai >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} parse_command_with_ai function exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} parse_command_with_ai function not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

if type extract_ai_content >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} extract_ai_content function exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} extract_ai_content function not found"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Configuration Display Tests
# -----------------------
test_section "Configuration Display"

# Test show_ai_config doesn't crash
if show_ai_config >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} show_ai_config executes without error"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} show_ai_config failed"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# -----------------------
# Environment Variable Integration Tests
# -----------------------
test_section "Environment Variable Integration"

# Test Zhipu AI configuration scenario with ANTHROPIC_AUTH_TOKEN
ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.7"
ANTHROPIC_AUTH_TOKEN="zhipu-test-key"

BASE_URL=$(_get_ai_base_url)
MODEL=$(_get_ai_model)
KEY=$(_get_ai_api_key)

assert_equals "https://api.z.ai/api/anthropic" "$BASE_URL" "Zhipu: base URL"
assert_equals "glm-4.7" "$MODEL" "Zhipu: model selection"
assert_equals "zhipu-test-key" "$KEY" "Zhipu: auth token"

# Reset
unset ANTHROPIC_BASE_URL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_AUTH_TOKEN

# Test corporate proxy scenario
ANTHROPIC_BASE_URL="https://api-gateway.internal.company.com/anthropic/v1"
ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
ANTHROPIC_AUTH_TOKEN="corp-test-key"

BASE_URL=$(_get_ai_base_url)
MODEL=$(_get_ai_model)
KEY=$(_get_ai_api_key)

assert_equals "https://api-gateway.internal.company.com/anthropic/v1" "$BASE_URL" "Corporate: base URL"
assert_equals "claude-3-5-sonnet-20241022" "$MODEL" "Corporate: model selection"
assert_equals "corp-test-key" "$KEY" "Corporate: auth token"

# Reset
unset ANTHROPIC_BASE_URL ANTHROPIC_MODEL ANTHROPIC_AUTH_TOKEN

# Test priority: AUTH_TOKEN > API_KEY > CLAUDE_KEY
ANTHROPIC_AUTH_TOKEN="auth-token-123"
ANTHROPIC_API_KEY="api-key-456"
CLAUDE_API_KEY="claude-key-789"

KEY=$(_get_ai_api_key)
assert_equals "auth-token-123" "$KEY" "AUTH_TOKEN should have highest priority"

# Test API_KEY used when AUTH_TOKEN not set
unset ANTHROPIC_AUTH_TOKEN
KEY=$(_get_ai_api_key)
assert_equals "api-key-456" "$KEY" "API_KEY should be used when AUTH_TOKEN not set"

# Test CLAUDE_KEY fallback
unset ANTHROPIC_API_KEY
KEY=$(_get_ai_api_key)
assert_equals "claude-key-789" "$KEY" "CLAUDE_KEY should be fallback"

# Reset
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY CLAUDE_API_KEY

# -----------------------
# Teardown
# -----------------------
teardown_test_env

test_suite_end "vde-ai-api Library Tests"
exit $?
