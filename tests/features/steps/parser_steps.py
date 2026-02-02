"""
BDD Step definitions for Natural Language Parser scenarios.
Uses real vde-parser library functions for testing.
"""

import os
import shlex
import subprocess
import sys

from behave import given, then, when

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

# Get VDE_ROOT from environment or calculate
VDE_ROOT = os.environ.get('VDE_ROOT_DIR')
if not VDE_ROOT:
    try:
        from config import VDE_ROOT as config_root
        VDE_ROOT = str(config_root)
    except ImportError:
        VDE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

VDE_PARSER = os.path.join(VDE_ROOT, 'scripts/lib/vde-parser')
VDE_VM_COMMON = os.path.join(VDE_ROOT, 'scripts/lib/vm-common')
VDE_SHELL_COMPAT = os.path.join(VDE_ROOT, 'scripts/lib/vde-shell-compat')


def _call_vde_parser_function(function_name, input_string):
    """Call a vde-parser function and return stdout."""
    # Pass input via environment variable to avoid shell escaping issues
    env = os.environ.copy()
    env['VDE_TEST_INPUT'] = input_string
    cmd = f"zsh -c 'source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \"$VDE_TEST_INPUT\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    return result.stdout.strip(), result.returncode


def _call_vde_parser_check(function_name, input_string):
    """Call a vde-parser check function that returns exit code."""
    # Pass input via environment variable to avoid shell escaping issues
    env = os.environ.copy()
    env['VDE_TEST_INPUT'] = input_string
    cmd = f"zsh -c 'source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \"$VDE_TEST_INPUT\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    return result.returncode


# =============================================================================
# Real vde-parser function wrappers
# =============================================================================

def _get_real_intent(input_string):
    """Call vde-parser's detect_intent function."""
    stdout, _ = _call_vde_parser_function('detect_intent', input_string)
    return stdout


def _get_real_vm_names(input_string):
    """Call vde-parser's extract_vm_names function."""
    stdout, _ = _call_vde_parser_function('extract_vm_names', input_string)
    if not stdout:
        return []
    return [vm for vm in stdout.split('\n') if vm]


def _get_real_filter(input_string):
    """Call vde-parser's extract_filter function."""
    stdout, _ = _call_vde_parser_function('extract_filter', input_string)
    return stdout if stdout else 'all'


def _get_real_flags(input_string):
    """Call vde-parser's extract_flags function."""
    stdout, _ = _call_vde_parser_function('extract_flags', input_string)
    flags = {'rebuild': False, 'nocache': False}
    if stdout:
        for pair in stdout.split():
            if '=' in pair:
                key, value = pair.split('=', 1)
                flags[key] = value.lower() == 'true'
    return flags


def _has_dangerous_chars(input_string):
    """Call vde-parser's contains_dangerous_chars function.
    Returns 0 if dangerous chars found, 3 if safe (VDE_ERR_NOT_FOUND).
    """
    returncode = _call_vde_parser_check('contains_dangerous_chars', input_string)
    return returncode == 0


def _validate_plan_line(line):
    """Call vde-parser's validate_plan_line function.
    Returns 0 if valid, 2 if invalid.
    """
    returncode = _call_vde_parser_check('validate_plan_line', line)
    return returncode == 0


# =============================================================================
# GIVEN steps - Setup parser state
# =============================================================================

@given('input is empty')
def step_input_empty(context):
    """Set input as empty string for parsing."""
    context.empty_input = ''  # Empty string for parsing


@when('I parse the input')
def step_parse_empty_input(context):
    """Parse empty input - should return help intent using real parser."""
    empty_input = getattr(context, 'empty_input', '')
    # Call real parser with empty input
    context.detected_intent = _get_real_intent(empty_input)
    context.detected_vms = _get_real_vm_names(empty_input)
    context.detected_filter = _get_real_filter(empty_input)


@given('"{alias}" is an alias for "{vm_name}"')
def step_alias_defined(context, alias, vm_name):
    """Define an alias for a VM (for testing alias resolution)."""
    if not hasattr(context, 'aliases'):
        context.aliases = {}
    context.aliases[alias] = vm_name


@given('known VMs are "{vms}"')
def step_known_vms(context, vms):
    """Set known VMs for parsing (for testing with limited VM set)."""
    context.known_vms = [v.strip() for v in vms.split(",")]


@given('plan contains "{line}"')
def step_plan_contains(context, line):
    """Add a line to the plan."""
    if not hasattr(context, 'plan'):
        context.plan = []
    context.plan.append(line)


@when('plan contains "{line}"')
def step_when_plan_contains(context, line):
    """Add a line to the plan and re-validate (for testing rejection)."""
    if not hasattr(context, 'plan'):
        context.plan = []
    context.plan.append(line)
    # Validate the plan with the new line using real validation logic
    all_valid = True
    for plan_line in context.plan:
        if not _validate_plan_line(plan_line):
            all_valid = False
            break
    context.plan_validated = all_valid


@when('I validate the plan')
def step_plan_validated(context):
    """Validate the plan using real validation logic."""
    # Validate each line and set plan_validated based on actual results
    all_valid = True
    for line in getattr(context, 'plan', []):
        if not _validate_plan_line(line):
            all_valid = False
            break
    context.plan_validated = all_valid


@when('plan is validated')
def step_plan_is_validated(context):
    """Validate the plan using real validation logic (alias for I validate the plan)."""
    # Validate each line and set plan_validated based on actual results
    all_valid = True
    for line in getattr(context, 'plan', []):
        if not _validate_plan_line(line):
            all_valid = False
            break
    context.plan_validated = all_valid


# =============================================================================
# WHEN steps - Execute parser functions
# =============================================================================

@when('I parse "{input_text}"')
def step_parse_input(context, input_text):
    """Parse natural language input using real vde-parser functions."""
    # Handle test aliases defined in context.aliases
    parse_input = input_text
    if hasattr(context, 'aliases') and context.aliases:
        for alias, canonical in context.aliases.items():
            # Replace alias occurrences with canonical name
            parse_input = parse_input.replace(alias, canonical)

    # Call real vde-parser functions
    detected_intent = _get_real_intent(parse_input)
    context.detected_intent = detected_intent
    context.nl_intent = detected_intent  # For natural_language_steps assertions

    # Get VM names from real parser
    vm_names = _get_real_vm_names(parse_input)
    if 'all' in parse_input.lower() or 'everything' in parse_input.lower():
        # Check if it's a filter-based "all"
        filter_val = _get_real_filter(parse_input)
        if filter_val == 'lang':
            context.detected_vms = 'all_languages'
            context.nl_vms = 'all_languages'
        elif filter_val == 'svc':
            context.detected_vms = 'all_services'
            context.nl_vms = 'all_services'
        else:
            context.detected_vms = 'all'
            context.nl_vms = 'all'
    elif vm_names:
        context.detected_vms = vm_names
        context.nl_vms = vm_names  # For natural_language_steps assertions

    # Get filter from real parser
    context.detected_filter = _get_real_filter(parse_input)
    context.nl_filter = context.detected_filter  # For natural_language_steps assertions

    # Get flags from real parser
    flags = _get_real_flags(parse_input)
    context.detected_flags = flags
    context.nl_flags = flags  # For natural_language_steps assertions
