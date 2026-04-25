#!/usr/bin/env python3
# @forge (Governance Steps)
from behave import given, when, then
import os
import shutil
import json

@given('I have an intentional version mismatch in "{file_path}"')
def step_impl(context, file_path):
    root = "."
    full_path = os.path.join(root, file_path)
    context.backup_path = full_path + '.bak'
    shutil.copy2(full_path, context.backup_path)
    
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    # Intentional drift
    data['version'] = "9.9.9-drift"
    
    with open(full_path, 'w') as f:
        json.dump(data, f, indent=2)

@then('I restore "{file_path}" to its original state')
@when('I restore "{file_path}" to its original state')
def step_impl(context, file_path):
    root = "."
    full_path = os.path.join(root, file_path)
    if hasattr(context, 'backup_path') and os.path.exists(context.backup_path):
        shutil.move(context.backup_path, full_path)

@given('I create a temporary script "{file_path}"')
def step_impl(context, file_path):
    root = "."
    full_path = os.path.join(root, file_path)
    with open(full_path, 'w') as f:
        f.write("#!/usr/bin/env zsh\n# @forge (Ghost)\necho 'Boo'\n")
    os.chmod(full_path, 0o755)

@then('I remove "{file_path}"')
def step_impl(context, file_path):
    root = "."
    full_path = os.path.join(root, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
