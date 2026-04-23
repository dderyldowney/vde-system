#!/usr/bin/env python3
# VDE ARCHITECTURAL RECORD
# @forge (DNS Discovery Steps)
from behave import given, then
from shell_helpers import verify_container_running, normalize_vm_name

@given('"{vm_alias}" is running')
def step_vm_is_running(context, vm_alias):
    from vm_common import container_is_running, run_vde_command
    from shell_helpers import wait_for_container_healthy
    # Use normalize_vm_name to get vde- prefix correctly
    container_name = normalize_vm_name(vm_alias)
    
    if not container_is_running(container_name):
        run_vde_command(f"start {vm_alias}")
        wait_for_container_healthy(container_name)
        
    verify_container_running(container_name)

@then('the output should contain either "{text1}" or "{text2}"')
def step_output_contains_either(context, text1, text2):
    # Support both command_output (critical_steps) and last_result (system_spine_steps)
    # Be extremely robust to avoid loop-inducing AttributeErrors
    output = ""
    if hasattr(context, 'command_output'):
        output = context.command_output
    elif hasattr(context, 'last_result'):
        output = context.last_result.stdout + context.last_result.stderr
    
    assert text1 in output or text2 in output, \
        f"Neither '{text1}' nor '{text2}' found in output: {output}"
