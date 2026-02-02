#!/usr/bin/env zsh
# Run fake test scan - checks for prohibited patterns in test steps

cd /Users/dderyldowney/dev

echo "=== Fake Test Pattern Scan ==="
echo ""

# Patterns that indicate fake tests (from .kilocode/rules/fake_tests.md)
FAKE_PATTERNS=(
    "assert True"
    "or True"
    "getattr(context,"
    "context.* = True"
    "context.* = False"
    "REMOVED:"
    "works the same as"
    "equivalent to"
    "def step_impl(context):"  # Placeholder
    "^\s*pass\s*$#"  # Pass statements in step definitions
)

TOTAL_VIOLATIONS=0

for pattern in "${FAKE_PATTERNS[@]}"; do
    echo "Checking for pattern: $pattern"
    COUNT=$(grep -r "$pattern" tests/features/steps/*.py 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        echo "  Found $COUNT occurrences"
        grep -r "$pattern" tests/features/steps/*.py 2>/dev/null | head -5
        TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + COUNT))
    fi
done

echo ""
echo "=== Scan Complete ==="
echo "Total potential violations: $TOTAL_VIOLATIONS"
if [ "$TOTAL_VIOLATIONS" -eq 0 ]; then
    echo "✓ No fake test patterns detected"
fi
