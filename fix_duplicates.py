#!/usr/bin/env python3
"""Fix duplicate step definitions in test files."""
import re

# Fix vm_to_host_steps.py
FILE_PATH = "tests/features/steps/vm_to_host_steps.py"

with open(FILE_PATH, 'r') as f:
    content = f.read()

# Pattern 1: @given('I have Docker installed on my host')
content = re.sub(
    r"@given\('I have Docker installed on my host'\)",
    "@given('I have Docker installed on my host for VM-to-Host')",
    content
)

# Pattern 2: @when('I run "to-host ...') steps
pattern = r"@when\('I run \"to-host ([^\"]+)\"'\)"
replacement = r"@when('I run \"to-host \1\" for VM-to-Host')"
content = re.sub(pattern, replacement, content)

# Pattern 3: @when('I have multiple VMs running')
content = re.sub(
    r"@when\('I have multiple VMs running'\)",
    "@when('I have multiple VMs running for VM-to-Host')",
    content
)

with open(FILE_PATH, 'w') as f:
    f.write(content)

print("Fixed duplicate step definitions in vm_to_host_steps.py")
