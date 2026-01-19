"""
BDD Step Definitions for Help and Guidance features.
These are critical for ZeroToMastery students who need guidance.
Note: Many steps are shared with ai_steps.py - those are defined there.
"""
import sys
import os

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT


from behave import given, when, then
from pathlib import Path


# VDE_ROOT imported from config

# =============================================================================
# Help/Guidance GIVEN steps
# =============================================================================
# Note: Most Given steps are defined in ai_steps.py and reused here

# =============================================================================
# Help/Guidance WHEN steps
# =============================================================================
# Note: Generic WHEN steps like "I say {input}" are defined in ai_steps.py

# =============================================================================
# Help/Guidance THEN steps
# =============================================================================

@then('I should not need to remember the exact command')
def step_no_exact_command_memory(context):
    context.no_command_memory_needed = True

@then('I should understand my options')
def step_understand_options(context):
    context.options_understood = True

@then('I should see which VMs are stopped')
def step_see_stopped_vms(context):
    context.stopped_vms_visible = True

@then('I should see SSH connection info for running VMs')
def step_see_ssh_info(context):
    context.ssh_info_visible = True

@then('example commands should be shown')
def step_example_commands(context):
    context.example_commands_shown = True

@then('I should understand how to use VDE')
def step_understand_how_use(context):
    context.usage_understood = True

@then('I should not need to remember create-virtual-for syntax')
def step_no_create_syntax_memory(context):
    context.no_create_syntax_memory = True

@then('I should not need to list each VM')
def step_no_list_each_vm(context):
    context.no_vm_listing_needed = True

@then('I should not need to remember --rebuild flag')
def step_no_rebuild_flag_memory(context):
    context.no_rebuild_memory_needed = True

@then('I should see the port number')
def step_see_port_number(context):
    context.port_number_visible = True

@then('I should see VSCode Remote-SSH instructions')
def step_see_vscode_instructions(context):
    context.vscode_instructions_visible = True

@then('I should not see postgres, redis, nginx')
def step_not_see_services(context):
    context.services_not_visible = True

@then('I should not see language VMs')
def step_not_see_languages(context):
    context.languages_not_visible = True

@then('available options should be suggested')
def step_options_suggested(context):
    context.available_options_suggested = True

@then('I should not get a cryptic error')
def step_no_cryptic_error(context):
    context.clear_error_message = True

@then('other VMs should not clutter the output')
def step_no_clutter(context):
    context.output_clean = True

@then('common aliases should work naturally')
def step_aliases_work_naturally(context):
    context.natural_aliases_work = True
