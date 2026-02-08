#!/usr/bin/env python3
"""Comprehensive fix for all duplicate step definitions in test files."""
import re
import os

STEPS_DIR = "tests/features/steps"

def fix_duplicates_in_file(filepath):
    """Fix duplicate steps in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Common duplicates to fix - patterns from test errors
    fixes = [
        # Given steps
        (r"@given\('I have Docker installed on my host'\)", 
         "@given('I have Docker installed on my host for VM-to-Host')"),
        (r"@given\('I have a Python VM running'\)",
         "@given('I have a Python VM running for VM-to-Host')"),
        (r"@given\('I have multiple VMs running'\)",
         "@given('I have multiple VMs running for VM-to-Host')"),
        (r"@given\('I have the SSH agent running'\)",
         "@given('I have the SSH agent running for VM-to-Host')"),
        (r"@given\('I have my SSH keys loaded'\)",
         "@given('I have my SSH keys loaded for VM-to-Host')"),
        
        # When steps - VM management in error_handling_steps.py
        (r"@when\('I start a VM'\)",
         "@when('I start a VM for Error-Handling')"),
        (r"@when\('I stop a VM'\)",
         "@when('I stop a VM for Error-Handling')"),
        (r"@when\('I restart a VM'\)",
         "@when('I restart a VM for Error-Handling')"),
        (r"@when\('I list all VMs'\)",
         "@when('I list all VMs for Error-Handling')"),
        (r"@when\('I check the VM status'\)",
         "@when('I check the VM status for Error-Handling')"),
        
        # When steps - VM management in ssh_agent_steps.py
        (r"@when\('I start a VM for SSH-Agent'\)",
         "@when('I start a VM for SSH-Agent-Steps')"),
        (r"@when\('I stop a VM for SSH-Agent'\)",
         "@when('I stop a VM for SSH-Agent-Steps')"),
        (r"@when\('I restart a VM for SSH-Agent'\)",
         "@when('I restart a VM for SSH-Agent-Steps')"),
        (r"@when\('I list all VMs for SSH-Agent'\)",
         "@when('I list all VMs for SSH-Agent-Steps')"),
        (r"@when\('I check the VM status for SSH-Agent'\)",
         "@when('I check the VM status for SSH-Agent-Steps')"),
        
        # When steps - to-host commands
        (r"@when\('I run \"to-host ([^\"]+)\"'\)",
         r"@when('I run \"to-host \1\" for VM-to-Host')"),
        (r"@when\('I run \"ssh-vm-vm ([^\"]+)\"'\)",
         r"@when('I run \"ssh-vm-vm \1\" for VM-to-VM')"),
        
        # Then steps
        (r"@then\('I should see the output'\)",
         "@then('I should see the output for VM-to-Host')"),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")

def main():
    """Fix all duplicate steps in all step files."""
    for filename in os.listdir(STEPS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(STEPS_DIR, filename)
            fix_duplicates_in_file(filepath)

if __name__ == "__main__":
    main()
