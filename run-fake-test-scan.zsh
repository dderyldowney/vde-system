#!/usr/bin/env zsh
# Fake test scanner - detects prohibited patterns in ALL test step files

cd /Users/dderyldowney/dev

echo "=== Fake Test Pattern Scan (All Step Files) ==="
echo ""
echo "Rules:"
echo "  - WHEN steps must call real functions (no pass-only)"
echo "  - THEN steps MUST have assertions (context-only is fake)"
echo "  - GIVEN steps can set context (allowed)"
echo ""

# =============================================================================
# Use Python for accurate parsing
# =============================================================================

python3 << 'PYTHON_SCRIPT'
import re
import os
import glob

violations = []
step_files = glob.glob("tests/features/steps/*.py")

for filepath in step_files:
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Only process @when and @then decorated functions
        if line.startswith('@when') or line.startswith('@then'):
            step_type = line.split('(')[0].replace('@', '')
            
            # Find the function definition
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('@when', '@then', '@given')) and not lines[j].strip().startswith('def '):
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('def '):
                func_name = lines[j].strip()[4:].split('(')[0]
                
                # Get the function body - from after @decorator to next @decorator or def or end
                # IMPORTANT: Include lines AFTER the def line too (the function implementation)
                k = j + 1
                while k < len(lines) and not lines[k].strip().startswith(('@when', '@then', '@given')) and not lines[k].strip().startswith('def '):
                    k += 1
                
                # Function content is from after @then to before next @decorator/def
                func_content = '\n'.join(lines[i+1:k])
                
                # Check for assertions - properly indented assert counts
                has_assert = bool(re.search(r'^\s+assert\s+', func_content, re.MULTILINE))
                
                # Check for pass-only (WHEN violation)
                has_pass = bool(re.search(r'^\s+pass\s*$', func_content, re.MULTILINE))
                
                # Check for real function calls
                has_real = bool(re.search(r'(subprocess\.run\(|subprocess\.Popen|subprocess\.check_output|\.exists\(|\.read_text\(|\.write_text\(|\.check\()', func_content))
                
                if step_type == 'when':
                    # WHEN steps: must have real calls, pass-only is fake
                    if has_pass and not has_real:
                        violations.append(('WHEN', func_name, os.path.basename(filepath)))
                        
                elif step_type == 'then':
                    # THEN steps: MUST have assertions
                    if not has_assert:
                        violations.append(('THEN', func_name, os.path.basename(filepath)))
            
            # Move past this @decorator to the next
            i = k if 'k' in dir() else j
        else:
            i += 1

# Print results
for vtype, fname, fpath in violations:
    print(f"{vtype}: {fname} in {fpath}")

print("")
print(f"Total violations: {len(violations)}")

# Exit with appropriate code
import sys
sys.exit(0 if len(violations) == 0 else 1)
PYTHON_SCRIPT

exit_code=$?

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "========================================"

if [ $exit_code -eq 0 ]; then
    echo "✓ CLEAN - No fake test patterns detected"
    exit 0
else
    echo "✗ VIOLATIONS FOUND - Fake tests detected"
    echo ""
    echo "Files with violations:"
    echo "  - Fix THEN steps to add assert statements"
    echo "  - Fix WHEN steps to use real subprocess/file calls"
    exit 1
fi
