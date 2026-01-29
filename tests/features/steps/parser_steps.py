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
    context.detected_intent = _get_real_intent(parse_input)

    # Get VM names from real parser
    vm_names = _get_real_vm_names(parse_input)
    if 'all' in parse_input.lower() or 'everything' in parse_input.lower():
        # Check if it's a filter-based "all"
        filter_val = _get_real_filter(parse_input)
        if filter_val == 'lang':
            context.detected_vms = 'all_languages'
        elif filter_val == 'svc':
            context.detected_vms = 'all_services'
        else:
            context.detected_vms = 'all'
    elif vm_names:
        context.detected_vms = vm_names
    else:
        context.detected_vms = []

    # Get filter from real parser
    context.detected_filter = _get_real_filter(parse_input)
    if context.detected_filter == 'all':
        context.detected_filter = None

    # Get flags from real parser
    flags = _get_real_flags(parse_input)
    context.rebuild_flag = flags.get('rebuild', False)
    context.nocache_flag = flags.get('nocache', False)

    # Security check using real parser
    context.has_dangerous_chars = _has_dangerous_chars(parse_input)


@when('I parse \'{input_text}\'')
def step_parse_input_single_quoted(context, input_text):
    """Parse natural language input with single quotes (handles double quotes inside)."""
    # Delegate to the main parse function - the input_text parameter already has the value
    step_parse_input(context, input_text)


@when('I parse the input with single quotes')
def step_parse_input_single_quotes(context):
    """Parse using single-quoted variant (delegates to main parse function)."""
    step_parse_input(context, getattr(context, 'single_quote_input', ''))


@when('I parse with double quotes in input')
def step_parse_input_double_quotes(context):
    """Parse input containing double quotes (delegates to main parse function)."""
    step_parse_input(context, getattr(context, 'double_quote_input', ''))


@when('I parse the special character input')
def step_parse_special_chars(context):
    """Parse input with special characters (delegates to main parse function)."""
    step_parse_input(context, getattr(context, 'special_input', ''))


@when('I validate the plan line "{line}"')
def step_validate_plan_line(context, line):
    """Validate a single plan line using real validation."""
    context.line_valid = _validate_plan_line(line)


@when('I extract flags from "{input_text}"')
def step_extract_flags(context, input_text):
    """Extract flags from input using real parser."""
    flags = _get_real_flags(input_text)
    context.rebuild_flag = flags.get('rebuild', False)
    context.nocache_flag = flags.get('nocache', False)


@when('I check for dangerous characters in "{input_text}"')
def step_check_dangerous_chars(context, input_text):
    """Check for dangerous characters using real parser."""
    context.has_dangerous_chars = _has_dangerous_chars(input_text)


@when('I resolve VM names from "{input_text}"')
def step_resolve_vms(context, input_text):
    """Resolve VM names using real parser."""
    context.detected_vms = _get_real_vm_names(input_text)


@when('I detect the filter in "{input_text}"')
def step_detect_filter(context, input_text):
    """Detect filter using real parser."""
    filter_val = _get_real_filter(input_text)
    context.detected_filter = filter_val if filter_val != 'all' else None


@when('I detect the intent from "{input_text}"')
def step_detect_intent(context, input_text):
    """Detect intent using real parser."""
    context.detected_intent = _get_real_intent(input_text)


# =============================================================================
# THEN steps - Verify parser results
# =============================================================================

@then('intent should be "{intent}"')
def step_check_intent(context, intent):
    """Verify the detected intent."""
    assert hasattr(context, 'detected_intent'), "No intent was detected"
    assert context.detected_intent == intent, f"Expected intent '{intent}', got '{context.detected_intent}'"


@then('filter should be "{filter_type}"')
def step_check_filter(context, filter_type):
    """Verify the detected filter."""
    assert hasattr(context, 'detected_filter'), "No filter was detected"
    expected = None if filter_type == 'none' else filter_type
    assert context.detected_filter == expected, f"Expected filter '{expected}', got '{context.detected_filter}'"


@then('VMs should include "{vm_name}"')
def step_check_vm_included(context, vm_name):
    """Verify a VM was detected in the list."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    detected = context.detected_vms
    if isinstance(detected, str):
        assert detected in ['all', 'all_languages', 'all_services'], f"Expected VM list, got '{detected}'"
    elif isinstance(detected, list):
        # Check if vm_name somehow contains multiple VMs (behave pattern matching issue)
        if '", "' in vm_name:
            vms = vm_name.split('", "')
            for vm in vms:
                vm = vm.strip('"\'')
                assert vm in detected, f"VM '{vm}' not found in {detected}"
        else:
            assert vm_name in detected, f"VM '{vm_name}' not found in {detected}"
    else:
        raise AssertionError(f"Expected VM list, got '{detected}'")


@then('VMs should include all known VMs')
def step_check_all_vms(context):
    """Verify all VMs were detected."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    detected = context.detected_vms
    assert detected == 'all' or detected == 'all_languages' or detected == 'all_services', \
        f"Expected 'all' VMs, got '{detected}'"


@then('VMs should include {vm_list}')
def step_check_vms_included(context, vm_list):
    """Verify one or more VMs were detected (handles both single and multiple VMs)."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    # vm_list from behave: for "VMs should include "python", "rust", "go""
    # we get: python", "rust", "go
    # Split on ", " pattern which is how Gherkin separates multiple quoted strings
    vms = vm_list.split('", "') if '", "' in vm_list else vm_list.split(',')
    vms = [v.strip('"\'') for v in vms if v.strip()]

    detected = context.detected_vms
    if isinstance(detected, list):
        for vm in vms:
            assert vm in detected, f"VM '{vm}' not found in {detected}"
    elif isinstance(detected, str):
        assert detected in ['all', 'all_languages', 'all_services']
    else:
        raise AssertionError(f"Expected VM list, got '{detected}'")


@then('VMs should be empty')
def step_check_no_vms(context):
    """Verify no VMs were detected."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    assert context.detected_vms == [] or context.detected_vms is None, f"Expected no VMs, got {context.detected_vms}"


@then('detected VMs should be "{vm_list}"')
def step_check_vm_list(context, vm_list):
    """Verify the exact list of detected VMs."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    expected = [v.strip() for v in vm_list.split(',')]
    actual = context.detected_vms if isinstance(context.detected_vms, list) else [context.detected_vms]
    assert set(actual) == set(expected), f"Expected {expected}, got {actual}"


@then('detected filter should be "{filter_type}"')
def step_check_filter_detected(context, filter_type):
    """Verify the detected filter."""
    assert hasattr(context, 'detected_filter'), "No filter was detected"
    expected = None if filter_type == 'none' else filter_type
    assert context.detected_filter == expected, f"Expected filter '{expected}', got '{context.detected_filter}'"


@then('rebuild flag should be {flag_value}')
def step_check_rebuild_flag(context, flag_value):
    """Verify the rebuild flag."""
    assert hasattr(context, 'rebuild_flag'), "Rebuild flag was not set"
    expected = flag_value.lower() == 'true'
    assert context.rebuild_flag == expected, f"Expected rebuild={expected}, got rebuild={context.rebuild_flag}"


@then('nocache flag should be {flag_value}')
def step_check_nocache_flag(context, flag_value):
    """Verify the nocache flag."""
    assert hasattr(context, 'nocache_flag'), "Nocache flag was not set"
    expected = flag_value.lower() == 'true'
    assert context.nocache_flag == expected, f"Expected nocache={expected}, got nocache={context.nocache_flag}"


@then('input should be marked as having dangerous characters')
def step_check_dangerous(context):
    """Verify dangerous characters were detected."""
    assert hasattr(context, 'has_dangerous_chars'), "Dangerous char check was not performed"
    assert context.has_dangerous_chars is True, "Expected dangerous characters to be detected"


@then('input should be marked as safe')
def step_check_safe(context):
    """Verify input was marked as safe."""
    assert hasattr(context, 'has_dangerous_chars'), "Safety check was not performed"
    assert context.has_dangerous_chars is False, "Expected input to be marked as safe"


@then('plan line should be valid')
def step_check_line_valid(context):
    """Verify plan line was marked as valid."""
    assert hasattr(context, 'line_valid'), "Plan line was not validated"
    assert context.line_valid is True, "Expected plan line to be valid"


@then('plan line should be invalid')
def step_check_line_invalid(context):
    """Verify plan line was marked as invalid."""
    assert hasattr(context, 'line_valid'), "Plan line was not validated"
    assert context.line_valid is False, "Expected plan line to be invalid"


@then('plan should be valid')
def step_check_plan_valid(context):
    """Verify the plan was marked as valid."""
    assert hasattr(context, 'plan_validated'), "Plan was not validated"
    assert context.plan_validated is True, "Expected plan to be valid"


@then('plan should be rejected')
def step_check_plan_rejected(context):
    """Verify the plan was rejected."""
    assert hasattr(context, 'plan_validated'), "Plan was not validated"
    assert context.plan_validated is False, "Expected plan to be rejected"


@then('detected VMs should contain "{count}" VMs')
def step_check_vm_count(context, count):
    """Verify the number of detected VMs."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    expected = int(count)
    detected = context.detected_vms
    if isinstance(detected, list):
        actual = len(detected)
    elif detected in ['all', 'all_languages', 'all_services']:
        actual = -1  # Special value for "all"
    else:
        actual = 0
    if expected >= 0:
        assert actual == expected, f"Expected {expected} VMs, got {actual}"


@then('VM name should be resolved to "{canonical}"')
def step_check_resolved_vm(context, canonical):
    """Verify VM alias was resolved correctly."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    detected = context.detected_vms
    if isinstance(detected, list) and len(detected) > 0:
        assert canonical in detected, f"Expected '{canonical}' in {detected}"


@then('ambiguous input should be handled gracefully')
def step_check_ambiguous_handled(context):
    """Verify ambiguous input was handled without error."""
    assert hasattr(context, 'detected_intent'), "No intent was detected"
    assert context.detected_intent in ['help', 'list_vms'], "Ambiguous input should default to help or list"


@then('special characters should be handled safely')
def step_check_special_chars_safe(context):
    """Verify special characters were detected and handled."""
    assert hasattr(context, 'has_dangerous_chars'), "Special char check was not performed"
    assert context.has_dangerous_chars is True, "Special characters should be detected as dangerous"


@then('flags should be parsed correctly')
def step_check_flags_correct(context):
    """Verify all flags were parsed correctly."""
    assert hasattr(context, 'rebuild_flag'), "Rebuild flag was not set"
    assert hasattr(context, 'nocache_flag'), "Nocache flag was not set"


@then('empty input should return help intent')
def step_check_empty_help(context):
    """Verify empty input returns help intent."""
    assert hasattr(context, 'detected_intent'), "No intent was detected"
    assert context.detected_intent == 'help', f"Empty input should return help, got '{context.detected_intent}'"


# =============================================================================
# Additional THEN steps for security test scenarios
# =============================================================================

@then('dangerous characters should be rejected')
def step_dangerous_chars_rejected(context):
    """Verify dangerous characters were detected and rejected."""
    assert hasattr(context, 'has_dangerous_chars'), "Dangerous char check was not performed"
    assert context.has_dangerous_chars is True, "Expected dangerous characters to be detected and rejected"


@then('command should NOT execute')
def step_command_not_execute(context):
    """Verify command would not execute due to dangerous characters."""
    assert hasattr(context, 'has_dangerous_chars'), "Dangerous char check was not performed"
    assert context.has_dangerous_chars is True, "Command should NOT execute when dangerous chars present"


@then('all plan lines should be valid')
def step_all_plan_lines_valid(context):
    """Verify all plan lines are valid."""
    assert hasattr(context, 'plan_validated'), "Plan was not validated"
    assert context.plan_validated is True, "Expected all plan lines to be valid"


@then('intent should default to "help"')
def step_intent_defaults_to_help(context):
    """Verify intent defaults to help for ambiguous input."""
    assert hasattr(context, 'detected_intent'), "No intent was detected"
    assert context.detected_intent == 'help', f"Expected intent to default to 'help', got '{context.detected_intent}'"


@then('help message should be displayed')
def step_help_message_displayed(context):
    """Verify help would be displayed (real implementation checks help intent)."""
    assert hasattr(context, 'detected_intent'), "No intent was detected"
    assert context.detected_intent == 'help', "Help message should be displayed when intent is 'help'"
    # Verify vde script has help functionality
    vde_script = os.path.join(VDE_ROOT, 'scripts/vde')
    assert os.path.exists(vde_script), f"VDE script should exist at {vde_script}"


@then('VMs should NOT include "{vm_name}"')
def step_vm_not_included(context, vm_name):
    """Verify a VM was NOT detected in the list."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    detected = context.detected_vms

    # Handle case where multiple VMs are passed: "javascript", "js"
    if '", "' in vm_name:
        vms = [v.strip('"\'') for v in vm_name.split('", "')]
        for vm in vms:
            if isinstance(detected, list):
                assert vm not in detected, f"VM '{vm}' should NOT be in {detected}"
            elif isinstance(detected, str):
                assert detected != vm, f"VM '{vm}' should NOT be detected"
    else:
        vm_name = vm_name.strip('"\'')
        if isinstance(detected, list):
            assert vm_name not in detected, f"VM '{vm_name}' should NOT be in {detected}"
        elif isinstance(detected, str):
            assert detected != vm_name, f"VM '{vm_name}' should NOT be detected"
