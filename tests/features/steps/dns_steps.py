#!/usr/bin/env python3
# VDE ARCHITECTURAL RECORD
# @forge (DNS Discovery Steps)
from behave import given, when, then
from shell_helpers import verify_container_running, normalize_vm_name, execute_in_container

# Global store for container results within a scenario
LAST_CONTAINER_RESULTS = {}

@given('"{vm_alias}" is running')
def step_vm_is_running(context, vm_alias):
    from vm_common import container_is_running, run_vde_command
    from shell_helpers import wait_for_container_healthy
    container_name = normalize_vm_name(vm_alias)
    
    if not container_is_running(container_name):
        run_vde_command(f"start {vm_alias}")
        wait_for_container_healthy(container_name)
        
    verify_container_running(container_name)
    context.vm_alias = vm_alias
    context.target_vm = container_name

@when('I execute "{command}" inside "{vm_alias}" to verify DNS')
def step_execute_dns_check(context, command, vm_alias):
    container_name = normalize_vm_name(vm_alias)
    context.vm_alias = vm_alias
    
    res = execute_in_container(container_name, command)
    # Persist globally for the next step
    LAST_CONTAINER_RESULTS['last'] = res
    context.last_container_result = res
    context.command_exit_code = res['returncode']
    context.command_output = res['stdout'] + res['stderr']

@then('the output should contain either "{text1}" or "{text2}"')
def step_output_contains_either(context, text1, text2):
    # Retrieve from the persistent store or context
    res = LAST_CONTAINER_RESULTS.get('last')
    if not res and hasattr(context, 'last_container_result'):
        res = context.last_container_result
        
    if not res:
        output = getattr(context, 'command_output', "")
    else:
        output = res['stdout'] + res['stderr']
    
    if not output:
        raise AssertionError("No physical output found for DNS verification.")
    
    assert text1 in output or text2 in output, \
        f"Neither '{text1}' nor '{text2}' found in output: {output}"
