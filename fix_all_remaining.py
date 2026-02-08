#!/usr/bin/env python3
"""Fix ALL remaining duplicate step definitions comprehensively."""
import re

def fix_file_duplicates(filepath, file_specific_suffix):
    """Fix all duplicate steps in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix "all should use my host's SSH keys"
    content = re.sub(
        r"@then\('all should use my host\\'s SSH keys'\)",
        f"@then('all should use my host\\'s SSH keys for {file_specific_suffix}')",
        content
    )
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")

# Fix ssh_vm_to_vm_steps.py
fix_file_duplicates("tests/features/steps/ssh_vm_to_vm_steps.py", "VM-to-VM")

# Fix ssh_git_steps.py  
fix_file_duplicates("tests/features/steps/ssh_git_steps.py", "SSH-Git")

print("\nAll remaining duplicates fixed!")
