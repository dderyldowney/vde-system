#!/usr/bin/env python3
"""Fix remaining duplicate step definitions."""
import re

# Fix ssh_vm_to_vm_steps.py - add remaining missing steps
with open("tests/features/steps/ssh_vm_to_vm_steps.py", 'r') as f:
    content = f.read()

# Fix the remaining duplicate
content = re.sub(
    r"@then\('only the SSH agent socket should be forwarded'\)",
    "@then('only the SSH agent socket should be forwarded for VM-to-VM')",
    content
)

with open("tests/features/steps/ssh_vm_to_vm_steps.py", 'w') as f:
    f.write(content)

print("Fixed: tests/features/steps/ssh_vm_to_vm_steps.py")

# Also fix ssh_git_steps.py - rename the conflicting step to keep it unique
with open("tests/features/steps/ssh_git_steps.py", 'r') as f:
    content = f.read()

content = re.sub(
    r"@then\('only the SSH agent socket should be forwarded'\)",
    "@then('only the SSH agent socket should be forwarded for SSH-Git')",
    content
)

with open("tests/features/steps/ssh_git_steps.py", 'w') as f:
    f.write(content)

print("Fixed: tests/features/steps/ssh_git_steps.py")
