#!/usr/bin/env zsh
# Run BDD tests without Docker (fast, local execution)
#
# This runs tests from tests/features/docker-free/ directory
# These tests DON'T require Docker:
# - Command-line parsing tests
# - Configuration validation tests
# - Template rendering tests
# - Cache management tests
# - Shell compatibility tests
# - Intent detection tests
# - Information discovery tests
# - Documentation workflows
#
# Usage: ./tests/run-bdd-fast.sh [feature-name]
#   Without arguments: runs all Docker-free features
#   With feature-name: runs specific feature (e.g., "cache-system")

set -e

VDE_ROOT_DIR="${VDE_ROOT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
export VDE_ROOT_DIR

echo "VDE Root Directory: $VDE_ROOT_DIR"
cd "$VDE_ROOT_DIR"

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    CYAN=''
    BOLD=''
    RESET=''
fi

# Parse arguments
SPECIFIC_FEATURE=""
VERBOSE_OUTPUT="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE_OUTPUT="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [feature-name] [--verbose]"
            echo ""
            echo "Run BDD tests without Docker (fast execution)"
            echo ""
            echo "Arguments:"
            echo "  feature-name    Specific feature to test (e.g., 'cache-system', 'template-system')"
            echo "  --verbose, -v   Enable verbose output"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all Docker-free tests"
            echo "  $0 cache-system       # Run cache-system tests"
            echo "  $0 template --verbose # Run template tests with verbose output"
            exit 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${RESET}"
            exit 1
            ;;
        *)
            SPECIFIC_FEATURE="$1"
            shift
            ;;
    esac
done

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}Running Fast BDD Tests (No Docker Required)${RESET}"
echo -e "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
echo ""

# Check if behave is installed
BEHAVE_CMD="behave"
if ! command -v behave &> /dev/null; then
    # Try python3 -m behave
    if python3 -m behave --version &> /dev/null; then
        BEHAVE_CMD="python3 -m behave"
    else
        echo -e "${RED}Error: 'behave' is not installed${RESET}"
        echo "Install it with: pip install behave"
        exit 1
    fi
fi

# Create necessary directories
echo "Creating VDE directories..."
mkdir -p projects/{python,rust,js,csharp,ruby,go,java}
mkdir -p data/{postgres,mongodb,redis}
mkdir -p logs/nginx
mkdir -p public-ssh-keys
mkdir -p .cache .locks

# Build behave command
behave_args="--format pretty --no-color"

if [[ "$VERBOSE_OUTPUT" == "true" ]]; then
    behave_args="$behave_args --verbose"
fi

if [[ -n "$SPECIFIC_FEATURE" ]]; then
    echo -e "${CYAN}Running specific feature: ${SPECIFIC_FEATURE}${RESET}"
    # Try to match the feature name in docker-free directory
    if [[ -f "tests/features/docker-free/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="$behave_args tests/features/docker-free/${SPECIFIC_FEATURE}.feature"
    else
        # Try to find a partial match in docker-free
        matched_file=$(find tests/features/docker-free -name "${SPECIFIC_FEATURE}*.feature" | head -1)
        if [[ -n "$matched_file" ]]; then
            echo -e "${YELLOW}Found: $matched_file${RESET}"
            behave_args="$behave_args $matched_file"
        else
            echo -e "${RED}Error: Feature '${SPECIFIC_FEATURE}' not found in docker-free/${RESET}"
            echo "Available Docker-free features:"
            ls tests/features/docker-free/*.feature | xargs -I {} basename {} .feature | sed 's/^/  - /'
            exit 1
        fi
    fi
else
    echo -e "${CYAN}Running all Docker-free features from tests/features/docker-free/${RESET}"
    behave_args="$behave_args tests/features/docker-free/"
fi

echo ""
echo -e "${CYAN}Command: $BEHAVE_CMD $behave_args${RESET}"
echo ""

# Run behave
if eval $BEHAVE_CMD $behave_args; then
    echo ""
    echo -e "${GREEN}✓ All fast BDD tests passed!${RESET}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some BDD tests failed${RESET}"
    exit 1
fi
