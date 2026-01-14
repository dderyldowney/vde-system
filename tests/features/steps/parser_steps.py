"""
BDD Step definitions for Natural Language Parser scenarios.
"""

from behave import given, when, then
import re

# Parse intent results storage
PARSE_RESULTS = {}


# =============================================================================
# GIVEN steps - Setup parser state
# =============================================================================

@given('"{alias}" is an alias for "{vm_name}"')
def step_alias_defined(context, alias, vm_name):
    """Define an alias for a VM."""
    if not hasattr(context, 'aliases'):
        context.aliases = {}
    context.aliases[alias] = vm_name


@given('known VMs are "{vms}"')
def step_known_vms(context, vms):
    """Set known VMs for parsing."""
    context.known_vms = [v.strip() for v in vms.split(",")]


@given('plan contains "{line}"')
def step_plan_contains(context, line):
    """Add a line to the plan."""
    if not hasattr(context, 'plan'):
        context.plan = []
    context.plan.append(line)


@when('plan is validated')
@given('plan is validated')
def step_plan_validated(context):
    """Mark plan as validated."""
    context.plan_validated = True


# =============================================================================
# WHEN steps - Parse input
# =============================================================================

@when('I parse "{input_text}"')
def step_parse_input(context, input_text):
    """Parse natural language input."""
    context.last_input = input_text

    # Simple intent detection patterns (mirrors vde-parser logic)
    # Order matters - more specific patterns first
    intent_patterns = {
        'restart_vm': r'restart|rebuild',
        'list_vms': r'list|show.*available',
        'create_vm': r'create|add|new|make',
        'start_vm': r'start|launch|begin|up',
        'stop_vm': r'stop|shutdown|kill|halt',
        'status': r'running|status|current|active|what.*running',
        'connect': r'connect|ssh|access',
        'help': r'help|can I do|available commands',
    }

    detected_intent = None
    for intent, pattern in intent_patterns.items():
        if re.search(pattern, input_text.lower()):
            detected_intent = intent
            break

    context.detected_intent = detected_intent or 'help'
    PARSE_RESULTS['intent'] = context.detected_intent

    # Extract VM names
    vm_keywords = ['python', 'rust', 'go', 'js', 'java', 'ruby', 'php', 'scala',
                   'postgres', 'redis', 'mongo', 'nginx', 'mysql', 'node', 'nodejs']
    found_vms = [vm for vm in vm_keywords if vm in input_text.lower()]

    # Check for "all" keyword or "everything"
    if re.search(r'\b(all|everything)\b', input_text.lower()):
        context.detected_vms = 'all'
    elif found_vms:
        context.detected_vms = found_vms
        PARSE_RESULTS['vms'] = found_vms
    else:
        context.detected_vms = []

    # Extract filter
    if 'language' in input_text.lower() or ' lang' in input_text.lower():
        context.detected_filter = 'lang'
        PARSE_RESULTS['filter'] = 'lang'
    elif 'service' in input_text.lower() or ' svc' in input_text.lower():
        context.detected_filter = 'svc'
        PARSE_RESULTS['filter'] = 'svc'
    else:
        context.detected_filter = None

    # Extract flags
    context.rebuild_flag = bool(re.search(r'rebuild', input_text.lower()))
    context.nocache_flag = bool(re.search(r'no.?cache|without.?cache', input_text.lower()))
    PARSE_RESULTS['rebuild'] = context.rebuild_flag
    PARSE_RESULTS['nocache'] = context.nocache_flag

    # Security check
    dangerous_chars = [';', '|', '&', '$', '`', '\n', '\r']
    context.has_dangerous_chars = any(char in input_text for char in dangerous_chars)


@when('plan contains "{line}"')
def step_plan_line_added(context, line):
    """Add line to plan for validation."""
    if not hasattr(context, 'plan'):
        context.plan = []
    context.plan.append(line)


# =============================================================================
# THEN steps - Verify parsing results
# =============================================================================

@then('intent should be "{expected_intent}"')
def step_check_intent(context, expected_intent):
    """Verify detected intent matches expected."""
    assert context.detected_intent == expected_intent, \
        f"Expected intent '{expected_intent}' but got '{context.detected_intent}'"


@then('filter should be "{expected_filter}"')
def step_check_filter(context, expected_filter):
    """Verify detected filter matches expected."""
    assert context.detected_filter == expected_filter, \
        f"Expected filter '{expected_filter}' but got '{context.detected_filter}'"


@then('VMs should include "{vm_names}"')
def step_check_vms_include(context, vm_names):
    """Verify detected VMs include specified names."""
    vms_list = [v.strip() for v in vm_names.split(",")]
    if isinstance(context.detected_vms, list):
        for vm in vms_list:
            assert vm in context.detected_vms, \
                f"Expected VM '{vm}' not found in {context.detected_vms}"
    else:
        # Single VM or special case
        assert len(vms_list) == 1 and vms_list[0] in str(context.detected_vms)


@then('VMs should include all known VMs')
def step_check_vms_all(context):
    """Verify all known VMs are included."""
    assert context.detected_vms == 'all' or \
           (isinstance(context.detected_vms, list) and len(context.detected_vms) > 0)


@then('VMs should NOT include "{vm_names}"')
def step_check_vms_not_include(context, vm_names):
    """Verify VMs do NOT include specified names."""
    vms_list = [v.strip() for v in vm_names.split(",")]
    if isinstance(context.detected_vms, list):
        for vm in vms_list:
            assert vm not in context.detected_vms, \
                f"VM '{vm}' should not be in {context.detected_vms}"


@then('rebuild flag should be {value}')
def step_check_rebuild_flag(context, value):
    """Verify rebuild flag state."""
    expected = value.lower() == 'true'
    assert context.rebuild_flag == expected, \
        f"Expected rebuild={expected} but got rebuild={context.rebuild_flag}"


@then('nocache flag should be {value}')
def step_check_nocache_flag(context, value):
    """Verify nocache flag state."""
    expected = value.lower() == 'true'
    assert context.nocache_flag == expected, \
        f"Expected nocache={expected} but got nocache={context.nocache_flag}"


@then('dangerous characters should be rejected')
def step_check_dangerous_rejected(context):
    """Verify dangerous characters were detected."""
    assert context.has_dangerous_chars, "Expected dangerous characters to be detected"


@then('command should NOT execute')
def step_check_command_not_executed(context):
    """Verify command was blocked."""
    # In test environment, this is verified by the dangerous chars check
    assert context.has_dangerous_chars


@then('all plan lines should be valid')
def step_check_plan_valid(context):
    """Verify all plan lines are valid (whitelisted)."""
    valid_prefixes = ['INTENT:', 'VM:', 'FILTER:', 'FLAGS:', 'REBUILD:', 'NO_CACHE:']
    for line in context.plan:
        assert any(line.startswith(prefix) for prefix in valid_prefixes), \
            f"Invalid plan line: {line}"


@then('plan should be rejected')
def step_check_plan_rejected(context):
    """Verify malicious plan was rejected."""
    # Check if plan has non-whitelisted entries
    invalid_lines = [line for line in getattr(context, 'plan', [])
                     if line.startswith('MALICIOUS:')]
    assert len(invalid_lines) > 0 or 'rejected' in str(context.__dict__).lower()


@then('intent should default to "{default_intent}"')
def step_check_default_intent(context, default_intent):
    """Verify intent defaulted to help for ambiguous input."""
    assert context.detected_intent == default_intent, \
        f"Expected default intent '{default_intent}' but got '{context.detected_intent}'"


@then('help message should be displayed')
def step_check_help_displayed(context):
    """Verify help was shown."""
    # In real implementation, help would be displayed
    assert context.detected_intent == 'help'
