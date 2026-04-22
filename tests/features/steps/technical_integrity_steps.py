#!/usr/bin/env python3
from behave import given, when, then
# @armor (BDD Integration Logic)
# @armor (BDD Step Definition)
# @armor (BDD Step Definition)
import subprocess
import os

@given('the environment is being initialized')
def step_impl(context):
    pass

@given('the Unyielding Tetrad is installed')
def step_impl(context):
    for tool in ['git', 'docker', 'ssh']:
        res = subprocess.run(['command', '-v', tool], shell=True, capture_output=True)
        assert res.returncode == 0, f"Missing Tetrad tool: {tool}"

@when('I check for command "{command}"')
def step_impl(context, command):
    context.last_result = subprocess.run(['command', '-v', command], shell=True, capture_output=True)

@given('the VDE root directory is active')
def step_impl(context):
    # Already established in environment
    pass
