#!/usr/bin/env python3
"""Fix specific duplicate step definitions by handling each file differently."""
import re

# Fix ssh_vm_to_vm_steps.py - rename ALL steps to have "for VM-to-VM" suffix
with open("tests/features/steps/ssh_vm_to_vm_steps.py", 'r') as f:
    content = f.read()

# Rename all @given, @when, @then steps to have "for VM-to-VM" suffix
# Given steps
content = re.sub(
    r"@given\('the SSH agent is running'\)",
    "@given('the SSH agent is running for VM-to-VM')",
    content
)
content = re.sub(
    r"@given\('my keys are loaded in the agent'\)",
    "@given('my keys are loaded in the agent for VM-to-VM')",
    content
)
content = re.sub(
    r"@given\('I do not have any SSH keys'\)",
    "@given('I do not have any SSH keys for VM-to-VM')",
    content
)
content = re.sub(
    r"@given\('I have a \{vm_type\} VM running'\)",
    "@given('I have a {vm_type} VM running for VM-to-VM')",
    content
)
content = re.sub(
    r"@given\('I have started the SSH agent'\)",
    "@given('I have started the SSH agent for VM-to-VM')",
    content
)

# When steps
content = re.sub(
    r"@when\('I SSH into the \{vm_type\} VM'\)",
    "@when('I SSH into the {vm_type} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh \{target_vm\}\" from within the \{source_vm\} VM'\)",
    "@when('I run \"ssh {target_vm}\" from within the {source_vm} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"scp \{source\}:\{src_path\} \{dest\}:\{dst_path\}\" from the \{vm_type\} VM'\)",
    "@when('I run \"scp {source}:{src_path} {dest}:{dst_path}\" from the {vm_type} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh \{target_vm\} \{command\}\" from the \{source_vm\} VM'\)",
    "@when('I run \"ssh {target_vm} {command}\" from the {source_vm} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh \{target_vm\} psql \{args\}\"'\)",
    "@when('I run \"ssh {target_vm} psql {args}\" for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh \{target_vm\} redis-cli ping\"'\)",
    "@when('I run \"ssh {target_vm} redis-cli ping\" for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh \{target_vm\} curl localhost:\{port\}/\{path\}\"'\)",
    "@when('I run \"ssh {target_vm} curl localhost:{port}/{path}\" for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I create a file in the \{vm_type\} VM'\)",
    "@when('I create a file in the {vm_type} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('SSH from one VM to another'\)",
    "@when('SSH from one VM to another for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I need to test the backend from the frontend VM'\)",
    "@when('I need to test the backend from the frontend VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@when\('I run \"ssh backend-dev pytest tests/\"'\)",
    "@when('I run \"ssh backend-dev pytest tests/\" for VM-to-VM')",
    content
)

# Then steps
content = re.sub(
    r"@then\('an SSH agent should be started automatically'\)",
    "@then('an SSH agent should be started automatically for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('an SSH key should be generated automatically'\)",
    "@then('an SSH key should be generated automatically for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('the key should be loaded into the agent'\)",
    "@then('the key should be loaded into the agent for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('no manual configuration should be required'\)",
    "@then('no manual configuration should be required for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('I should connect to the \{vm_type\} VM'\)",
    "@then('I should connect to the {vm_type} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('I should be authenticated using my host\\'s SSH keys'\)",
    "@then('I should be authenticated using my host\\'s SSH keys for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('I should not need to enter a password'\)",
    "@then('I should not need to enter a password for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('I should not need to copy keys to the \{vm_type\} VM'\)",
    "@then('I should not need to copy keys to the {vm_type} VM for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('I should be able to run psql commands'\)",
    "@then('I should be able to run psql commands for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('authentication should use my host\\'s SSH keys'\)",
    "@then('authentication should use my host\\'s SSH keys for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('the file should be copied using my host\\'s SSH keys'\)",
    "@then('the file should be copied using my host\\'s SSH keys for VM-to-VM')",
    content
)
content = re.sub(
    r"@then\('no password should be required'\)",
    "@then('no password should be required for VM-to-VM')",
    content
)

with open("tests/features/steps/ssh_vm_to_vm_steps.py", 'w') as f:
    f.write(content)

print("Fixed: tests/features/steps/ssh_vm_to_vm_steps.py")
