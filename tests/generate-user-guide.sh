#!/bin/bash
# Generate USER_GUIDE.md from BDD test scenarios
# This regenerates the documentation from your working test scenarios

cd "$(dirname "$0")" || exit 1
python3 scripts/generate_user_guide.py "$@"

echo ""
echo "✓ USER_GUIDE.md has been regenerated from BDD test scenarios"
echo "  You can commit this updated documentation with your code changes."
