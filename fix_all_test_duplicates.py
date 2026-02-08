#!/usr/bin/env python3
"""Comprehensive script to fix ALL duplicate step definitions in test step files."""

import re

def fix_all_duplicates():
    """Find and fix all duplicate step definitions."""
    
    # Files to scan and their unique suffix
    files_to_fix = {
        "tests/features/steps/vm_to_host_steps.py": "VM-to-Host",
        "tests/features/steps/ssh_vm_steps.py": "SSH-VM",
        "tests/features/steps/daily_workflow_steps.py": "Daily-Workflow",
    }
    
    # Patterns to fix - these are the step definitions that need unique suffixes
    patterns_to_fix = [
        # GIVEN steps
        (r"@given\('I have Docker installed on my host'\)", "I have Docker installed on my host for"),
        (r"@given\('I have a Python VM running'\)", "I have a Python VM running for"),
        (r"@given\('I have a Go VM running'\)", "I have a Go VM running for"),
        (r"@given\('I have a Rust VM running'\)", "I have a Rust VM running for"),
        (r"@given\('I have projects on my host'\)", "I have projects on my host for"),
        (r"@given\('I have multiple VMs running'\)", "I have multiple VMs running for"),
        (r"@given\('I have custom scripts on my host'\)", "I have custom scripts on my host for"),
        # WHEN steps
        (r"@when\('I SSH into the Python VM'\)", "I SSH into the Python VM for"),
        (r"@when\('I SSH into the Go VM'\)", "I SSH into the Go VM for"),
        (r"@when\('I SSH into a VM'\)", "I SSH into a VM for"),
        (r"@when\('I SSH into the Rust VM'\)", "I SSH into the Rust VM for"),
    ]
    
    for filepath, suffix in files_to_fix.items():
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        
        for pattern, replacement in patterns_to_fix:
            # Find all matches
            matches = list(re.finditer(pattern, content))
            for i, match in enumerate(matches):
                if i > 0:  # First match keeps original, rest get suffix
                    old_text = match.group(0)
                    new_text = old_text.replace("')", f" for {suffix}')")
                    content = content.replace(old_text, new_text, 1)  # Replace first occurrence only
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed: {filepath}")

if __name__ == "__main__":
    fix_all_duplicates()
