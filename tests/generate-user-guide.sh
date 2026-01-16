#!/usr/bin/env zsh
# Generate Verified User Guide
# Runs BDD tests and generates user guide with ONLY passing scenarios

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Generate VERIFIED User Guide from PASSING Tests       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

# Parse arguments
SKIP_TAGS=""
RUN_ALL_FEATURES=true
SPECIFIC_FEATURE=""

for arg in "$@"; do
    case "$arg" in
        --skip-docker-host)
            SKIP_TAGS="--tags=~requires-docker-host"
            shift
            ;;
        --feature=*)
            SPECIFIC_FEATURE="${arg#--feature=}"
            RUN_ALL_FEATURES=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Generate a VERIFIED user guide from PASSING BDD tests."
            echo ""
            echo "This script:"
            echo "  1. Runs BDD tests with JSON output"
            echo "  2. Parses results to identify PASSING scenarios"
            echo "  3. Generates USER_GUIDE.md with ONLY verified scenarios"
            echo ""
            echo "Options:"
            echo "  --skip-docker-host    Skip scenarios that require Docker host access"
            echo "  --feature=NAME        Only test specific feature file"
            echo "  -h, --help            Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                              # Run all tests, generate verified guide"
            echo "  $0 --skip-docker-host           # Skip Docker host tests (for CI)"
            echo "  $0 --feature=vm-lifecycle       # Only test vm-lifecycle feature"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}Step 1: Running BDD tests...${RESET}"
echo "This will take a few minutes..."
echo ""

# Build the BDD tester image first
echo -e "${BLUE}Building BDD test container...${RESET}"
if docker build -t vde-bdd-tester -f tests/docker/bdd-test/Dockerfile . > /dev/null 2>&1; then
    echo -e "${GREEN}✓${RESET} Container built"
else
    echo -e "${RED}✗${RESET} Failed to build container"
    exit 1
fi

# Determine feature to test
if [[ "$RUN_ALL_FEATURES" == "true" ]]; then
    BEHAVE_PATH="tests/features/"
else
    BEHAVE_PATH="tests/features/${SPECIFIC_FEATURE}.feature"
fi

# Run Behave with JSON output
echo -e "${BLUE}Running Behave tests with JSON output...${RESET}"
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PROJECT_ROOT/tests/workspace:/vde/tests/workspace" \
    -v "$PROJECT_ROOT/tests:/vde/tests-output" \
    -e VDE_ROOT_DIR=/vde \
    -e PYTHONUNBUFFERED=1 \
    --network host \
    vde-bdd-tester \
    zsh -lc "
        cd /vde && \
        behave --format json --outfile /vde/tests-output/behave-results.json $SKIP_TAGS '$BEHAVE_PATH' 2>&1 | head -100
    " || {
    echo ""
    echo -e "${YELLOW}⚠ Some tests failed, but generating guide with PASSING scenarios only${RESET}"
}

# Check if JSON was generated
if [[ ! -f "$PROJECT_ROOT/tests/behave-results.json" ]]; then
    echo -e "${RED}✗${RESET} Failed to generate test results"
    exit 1
fi

echo ""
echo -e "${GREEN}✓${RESET} Test results saved to tests/behave-results.json"

# Count passing scenarios
PASSING_COUNT=$(python3 -c "
import json
with open('$PROJECT_ROOT/tests/behave-results.json') as f:
    data = json.load(f)
count = 0
for feature in data:
    for element in feature.get('elements', []):
        if element.get('type') == 'scenario' and element.get('status') == 'passed':
            count += 1
print(count)
" 2>/dev/null || echo "0")

FAILING_COUNT=$(python3 -c "
import json
with open('$PROJECT_ROOT/tests/behave-results.json') as f:
    data = json.load(f)
count = 0
for feature in data:
    for element in feature.get('elements', []):
        if element.get('type') == 'scenario' and element.get('status') == 'failed':
            count += 1
print(count)
" 2>/dev/null || echo "0")

echo ""
echo -e "${BLUE}Test Results Summary:${RESET}"
echo "  Passing:  ${GREEN}$PASSING_COUNT${RESET} scenarios"
echo "  Failing:  ${RED}$FAILING_COUNT${RESET} scenarios"
echo ""

echo -e "${BLUE}Step 2: Generating verified user guide...${RESET}"
echo ""

# Generate the user guide from passing scenarios
python3 "$PROJECT_ROOT/tests/scripts/generate_user_guide.py"

echo ""
echo -e "${GREEN}${BOLD}✓ VERIFIED User Guide Generated!${RESET}"
echo ""
echo "The USER_GUIDE.md now contains ONLY scenarios that have been"
echo "verified to PASS. Every example in the guide is proven to work."
