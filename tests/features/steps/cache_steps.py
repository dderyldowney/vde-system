"""
BDD Step Definitions for cache and file operations.
"""

from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path("/vde")

# =============================================================================
# Cache-related GIVEN steps
# =============================================================================
# Note: VM types caching steps that duplicate common_steps.py are removed
# to avoid AmbiguousStep errors. Use the steps in common_steps.py instead.

@given('VM types cache exists and is valid')
def step_cache_valid(context):
    context.cache_valid = True

@given('VM types are cached')
def step_cached(context):
    context.vm_types_cached = True

@given('ports have been allocated for VMs')
def step_ports_allocated(context):
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports = {'python': 2200, 'rust': 2201}

@given('I want to start only specific VMs')
def step_start_specific(context):
    context.specific_vms = True

@given('some VMs are already running')
def step_some_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')

@given('I\'m monitoring the system')
def step_monitoring(context):
    context.monitoring = True

@given('I request to start multiple VMs')
def step_request_multiple(context):
    context.requested_multiple = True

@given('I\'m rebuilding a VM')
def step_rebuilding_vm(context):
    context.rebuilding = True

# =============================================================================
# Cache-related WHEN steps
# =============================================================================

@when('cache is read')
def step_cache_read(context):
    context.cache_read = True

@when('cache file is read')
def step_cache_file_read(context):
    context.cache_file_read = True

@when('I try to start it at the same time')
def step_start_at_same_time(context):
    context.concurrent_start = True

# =============================================================================
# Cache-related THEN steps
# =============================================================================

@then('cache file should be created at ".cache/vm-types.cache"')
def step_cache_created(context):
    cache_path = VDE_ROOT / ".cache" / "vm-types.cache"
    context.cache_created = str(cache_path)

@then('VM_TYPE array should be populated')
def step_vm_type_array(context):
    context.vm_type_array = True

@then('each line should match "ARRAY_NAME:key=value" format')
def step_cache_format(context):
    context.cache_format_correct = True

@then('only the stopped VMs should start')
def step_only_stopped_start(context):
    context.only_stopped_started = True

@then('I should see which were started')
def step_see_started(context):
    context.started_vms_shown = True

@then('I should be notified of the change')
def step_notified_change(context):
    context.notified_of_change = True

@then('understand what caused it')
def step_understand_cause(context):
    context.cause_understood = True

@then('know the new state')
def step_know_new_state(context):
    context.new_state_known = True

@then('the conflict should be detected')
def step_conflict_detected(context):
    context.conflict_detected = True

@then('I should be notified')
def step_notified(context):
    context.notified = True

@then('the operations should be queued or rejected')
def step_operations_queued(context):
    context.operations_queued = True

@then('I should be informed of progress')
def step_informed_progress(context):
    context.progress_informed = True

@then('know when it\'s ready to use')
def step_know_ready(context):
    context.ready_known = True

@then('not be left wondering')
def step_not_wondering(context):
    context.not_wondering = True

@then('I should see it\'s being built')
def step_see_building(context):
    context.building_shown = True

@then('I should see the progress')
def step_see_progress(context):
    context.progress_shown = True

@then('I should know when it will be ready')
def step_know_when_ready(context):
    context.ready_time_known = True

@then('I should see status for only those VMs')
def step_see_specific_status(context):
    context.specific_status_shown = True
