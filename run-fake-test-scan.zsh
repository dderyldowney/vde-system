#!/usr/bin/env zsh
# Fake test scanner - detects prohibited patterns in ALL test step files

cd /Users/dderyldowney/dev

echo "=== Fake Test Pattern Scan (All Step Files) ==="
echo ""
echo "Rules:"
echo "  - WHEN steps must call real functions"
echo "  - THEN steps must have real assertions"
echo "  - GIVEN steps can set context (allowed)"
echo ""

TOTAL_VIOLATIONS=0

# =============================================================================
# PHASE 1: Placeholder definitions
# =============================================================================
echo "--- Phase 1: Placeholder Definitions ---"

PLACEHOLDER=$(grep -rn "def step_impl(context):" tests/features/steps/*.py 2>/dev/null | grep -v "^#" | wc -l | tr -d ' ')
if [ "${PLACEHOLDER:-0}" -gt 0 ]; then
    echo "Found $PLACEHOLDER placeholder definitions:"
    grep -rn "def step_impl(context):" tests/features/steps/*.py 2>/dev/null | grep -v "^#" | head -5
    TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + PLACEHOLDER))
fi

REMOVED=$(grep -rn "REMOVED:" tests/features/steps/*.py 2>/dev/null | wc -l | tr -d ' ')
if [ "${REMOVED:-0}" -gt 0 ]; then
    echo "Found $REMOVED REMOVED comments:"
    grep -rn "REMOVED:" tests/features/steps/*.py 2>/dev/null | head -3
    TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + REMOVED))
fi

# =============================================================================
# PHASE 2 & 3: Use Python for reliable parsing
# =============================================================================
echo ""
echo "--- Phase 2 & 3: Checking WHEN/THEN Steps ---"

python3 << 'PYTHON_SCRIPT'
import re
import os
import glob

violations = {"when": 0, "then": 0, "obvious": 0}
step_files = glob.glob("tests/features/steps/*.py")

for filepath in step_files:
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('@when'):
            # Extract function
            func_body = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('@when', '@then', '@given')) and not lines[j].strip().startswith('def '):
                j += 1
            if j < len(lines) and lines[j].strip().startswith('def '):
                func_name = lines[j].strip()[4:].split('(')[0]
                # Check for pass-only without real calls
                func_content = '\n'.join(lines[i+1:j])
                has_pass = bool(re.search(r'^\s*pass\s*$', func_content, re.MULTILINE))
                has_real = bool(re.search(r'(subprocess|\.run\(|os\.system|Popen|check_output)', func_content))
                if has_pass and not has_real:
                    print(f"  FAKE WHEN: {func_name} in {os.path.basename(filepath)}")
                    violations["when"] += 1
            i = j
        elif line.strip().startswith('@then'):
            # Extract function
            func_body = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('@when', '@then', '@given')) and not lines[j].strip().startswith('def '):
                j += 1
            if j < len(lines) and lines[j].strip().startswith('def '):
                func_name = lines[j].strip()[4:].split('(')[0]
                func_content = '\n'.join(lines[i+1:j])
                has_assert = bool(re.search(r'^\s*assert\s+', func_content, re.MULTILINE))
                has_pass = bool(re.search(r'^\s*pass\s*$', func_content, re.MULTILINE))
                has_context_only = bool(re.search(r'^\s*context\.[a-zA-Z_]+\s*=\s*(True|False)', func_content, re.MULTILINE))
                has_real_check = bool(re.search(r'(subprocess|get_real|\.run\()', func_content))
                if (has_pass and not has_assert) or (has_context_only and not has_assert and not has_real_check):
                    if has_pass:
                        print(f"  FAKE THEN (pass-only): {func_name} in {os.path.basename(filepath)}")
                    else:
                        print(f"  FAKE THEN (context-only): {func_name} in {os.path.basename(filepath)}")
                    violations["then"] += 1
            i = j
        else:
            i += 1

print("")
print(f"WHEN violations: {violations['when']}")
print(f"THEN violations: {violations['then']}")
PYTHON_SCRIPT

# =============================================================================
# PHASE 4: Obvious fake patterns
# =============================================================================
echo ""
echo "--- Phase 4: Obvious Fake Patterns ---"

ASSERT_TRUE=$(grep -rn "assert True" tests/features/steps/*.py 2>/dev/null | grep -v "# " | grep -v "assert True," | wc -l | tr -d ' ')
if [ "${ASSERT_TRUE:-0}" -gt 0 ]; then
    echo "Found $ASSERT_TRUE 'assert True' patterns:"
    grep -rn "assert True" tests/features/steps/*.py 2>/dev/null | grep -v "# " | grep -v "assert True," | head -3
fi

SIMULATE=$(grep -rn "Simulate" tests/features/steps/*.py 2>/dev/null | grep -v "# " | wc -l | tr -d ' ')
if [ "${SIMULATE:-0}" -gt 0 ]; then
    echo "Found $SIMULATE 'Simulate' comments:"
    grep -rn "Simulate" tests/features/steps/*.py 2>/dev/null | grep -v "# " | head -3
fi

# =============================================================================
# Summary - get counts from Python
# =============================================================================
VIOLATION_COUNT=$(python3 << 'PYTHON_SCRIPT'
import re
import glob
count = 0
for filepath in glob.glob("tests/features/steps/*.py"):
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith(('@when', '@then')):
            is_when = line.strip().startswith('@when')
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('@when', '@then', '@given')) and not lines[j].strip().startswith('def '):
                j += 1
            func_content = '\n'.join(lines[i+1:j])
            has_assert = bool(re.search(r'^\s*assert\s+', func_content, re.MULTILINE))
            has_pass = bool(re.search(r'^\s*pass\s*$', func_content, re.MULTILINE))
            has_context_only = bool(re.search(r'^\s*context\.[a-zA-Z_]+\s*=\s*(True|False)', func_content, re.MULTILINE))
            has_real = bool(re.search(r'(subprocess|\.run\(|os\.system|Popen|check_output)', func_content))
            if is_when:
                if has_pass and not has_real:
                    count += 1
            else:
                if (has_pass and not has_assert) or (has_context_only and not has_assert and not has_real):
                    count += 1
        i += 1
print(count)
PYTHON_SCRIPT
)

TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + VIOLATION_COUNT))

echo ""
echo "========================================"
echo "SCAN SUMMARY"
echo "========================================"
echo "Total violations: $TOTAL_VIOLATIONS"
echo ""

if [ "$TOTAL_VIOLATIONS" -eq 0 ]; then
    echo "✓ CLEAN - No fake test patterns detected"
    exit 0
else
    echo "✗ VIOLATIONS FOUND - Fake tests detected"
    exit 1
fi
