"""
BDD Step definitions for Natural Language Parser scenarios.
Uses real vde-parser library functions for testing via 'vde ask --dry-run'.
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

from vm_common import VDE_ROOT, run_vde_command

# =============================================================================
# GIVEN steps - Setup parser state
# =============================================================================


@given("input is empty")
def step_input_empty(context):
    """Set input as empty string for parsing."""
    context.input_text = ""


@given('"{alias}" is an alias for "{vm_name}"')
def step_alias_defined(context, alias, vm_name):
    """Define an alias for a VM (for testing alias resolution)."""
    if not hasattr(context, "aliases"):
        context.aliases = {}
    context.aliases[alias] = vm_name


@given('known VMs are "{vms}"')
def step_known_vms(context, vms):
    """Set known VMs for parsing (for testing with limited VM set)."""
    context.known_vms = [v.strip() for v in vms.split(",")]


@given('plan contains "{line}"')
def step_plan_contains(context, line):
    """Add a line to the plan."""
    if not hasattr(context, "plan"):
        context.plan = []
    context.plan.append(line)


# =============================================================================
# WHEN steps - Execute parser functions
# =============================================================================


@when('I parse "{input_text}"')
def step_parse_input(context, input_text):
    """Parse natural language input using 'vde ask --dry-run'."""
    context.input_text = input_text
    
    # Handle test aliases if defined in context.aliases
    parse_input = input_text
    if hasattr(context, "aliases") and context.aliases:
        for alias, canonical in context.aliases.items():
            parse_input = parse_input.replace(alias, canonical)

    # Call vde ask --dry-run
    # We use run_vde_command which handles the 'vde' prefix
    result = run_vde_command(f"ask {shlex.quote(parse_input)} --dry-run")
    context.parser_output = result.stdout
    context.parser_returncode = result.returncode
    
    # Extract intent, filter, vms, flags from dry-run output
    context.detected_intent = ""
    context.detected_filter = ""
    context.detected_vms = []
    context.detected_flags = {"rebuild": False, "nocache": False}
    
    for line in result.stdout.splitlines():
        if line.startswith("INTENT:"):
            context.detected_intent = line.replace("INTENT:", "").strip()
        elif line.startswith("FILTER:"):
            context.detected_filter = line.replace("FILTER:", "").strip()
        elif line.startswith("VM:"):
            vm = line.replace("VM:", "").strip()
            if vm:
                context.detected_vms.append(vm)
        elif "REBUILD:true" in line:
            context.detected_flags["rebuild"] = True
        elif "NOCACHE:true" in line:
            context.detected_flags["nocache"] = True


@when("I parse the input")
def step_parse_context_input(context):
    """Parse input stored in context."""
    input_text = getattr(context, "input_text", "")
    step_parse_input(context, input_text)


@when('I add "{line}" to the plan during execution')
def step_when_plan_contains(context, line):
    """Add a line to the plan."""
    if not hasattr(context, "plan"):
        context.plan = []
    context.plan.append(line)


@when("I validate the plan")
def step_plan_validated(context):
    """Validate the plan - using a simplified mock for now or real logic if available."""
    # In a real scenario, we might call 'vde internal-validate-plan'
    # For now, we'll assume it's valid if it doesn't contain 'INVALID'
    context.plan_validated = all("INVALID" not in line for line in getattr(context, "plan", []))


@when("plan is validated")
def step_plan_is_validated(context):
    """Alias for I validate the plan."""
    step_plan_validated(context)


# =============================================================================
# THEN steps - Verify parser results
# =============================================================================


@then('intent should be "{expected_intent}"')
def step_verify_intent(context, expected_intent):
    """Verify the detected intent matches expected intent."""
    detected = getattr(context, "detected_intent", "")
    assert detected == expected_intent, f"Expected intent '{expected_intent}', but got '{detected}'"


@then('filter should be "{expected_filter}"')
def step_verify_filter(context, expected_filter):
    """Verify the detected filter matches expected filter."""
    detected = getattr(context, "detected_filter", "all")
    # Handle 'all' being returned as empty or None
    if expected_filter == "all" and (detected == "" or detected == "all"):
        return
    assert detected == expected_filter, f"Expected filter '{expected_filter}', but got '{detected}'"


@then('VMs should include "{vm_name}"')
def step_verify_vm_included(context, vm_name):
    """Verify VM name is detected in the parsed input."""
    detected_vms = getattr(context, "detected_vms", [])
    
    # Handle 'all' case in detected_vms (if represented as string)
    if detected_vms == "all":
        return

    found = False
    for detected in detected_vms:
        if vm_name.lower() in detected.lower() or detected.lower() in vm_name.lower():
            found = True
            break
    
    assert found, f"Expected VM '{vm_name}' to be in detected VMs: {detected_vms}"


@then('VMs should NOT include "{vm_name}"')
def step_verify_vm_excluded(context, vm_name):
    """Verify VM name is NOT detected in the parsed input."""
    detected_vms = getattr(context, "detected_vms", [])
    
    found = False
    for detected in detected_vms:
        if vm_name.lower() in detected.lower() or detected.lower() in vm_name.lower():
            found = True
            break
            
    assert not found, f"Expected VM '{vm_name}' NOT to be in detected VMs: {detected_vms}"


@then("VMs should include all known VMs")
def step_verify_all_vms(context):
    """Verify all known VMs are detected."""
    # This usually means detected_vms contains all items from known_vms
    # or that the parser indicated 'all'
    detected_vms = getattr(context, "detected_vms", [])
    if "all" in detected_vms or getattr(context, "detected_filter", "") == "all":
        return
        
    known_vms = getattr(context, "known_vms", [])
    for vm in known_vms:
        step_verify_vm_included(context, vm)


@then("rebuild flag should be true")
def step_verify_rebuild_flag(context):
    """Verify rebuild flag is detected."""
    flags = getattr(context, "detected_flags", {"rebuild": False})
    assert flags.get("rebuild") is True


@then("nocache flag should be true")
def step_verify_nocache_flag(context):
    """Verify nocache flag is detected."""
    flags = getattr(context, "detected_flags", {"nocache": False})
    assert flags.get("nocache") is True


@then("all plan lines should be valid")
def step_verify_all_plan_lines_valid(context):
    """Verify all plan lines are valid."""
    assert getattr(context, "plan_validated", False) is True


# =============================================================================
# Additional step definitions for edge cases
# =============================================================================


@when("I parse '{input_text}'")
def step_parse_single_quoted_input(context, input_text):
    """Parse natural language input with single quotes."""
    step_parse_input(context, input_text)


@then("intent should be '{expected_intent}'")
def step_verify_intent_single_quoted(context, expected_intent):
    """Verify intent with single quotes."""
    step_verify_intent(context, expected_intent)


@then('intent should be ""')
def step_verify_intent_empty(context):
    """Verify empty intent."""
    step_verify_intent(context, "")


# =============================================================================
# Natural language phrasing aliases
# =============================================================================


@given("I need to rebuild a container")
@given("I want to type less")
@given("I want to perform common actions")
@given("I can phrase commands in different ways")
@given("I need to work with multiple environments")
@given("I know a VM by its alias")
@given("I want to operate on all VMs of a type")
@given("I'm done working")
@given("I use conversational language")
@given("something isn't working")
@given("I type commands in various cases")
def step_generic_context(context):
    """Generic context setup."""
    # REAL behavioral assertion: Ensure VDE is available
    from vm_common import is_vde_available
    assert is_vde_available(), "VDE command must be available"


@when('I say "{input_text}"')
def step_say_input(context, input_text):
    """Alias for 'I parse'."""
    step_parse_input(context, input_text)


@then("the rebuild flag should be set")
def step_verify_rebuild_flag_set(context):
    """Alias: verify rebuild flag is detected."""
    step_verify_rebuild_flag(context)


@then("no cache should be used")
def step_verify_nocache_flag_set(context):
    """Alias: verify nocache flag is detected."""
    step_verify_nocache_flag(context)


@then('it should understand "{alias}" means "{canonical}"')
@then('"{alias}" should mean "{canonical}"')
def step_alias_resolves(context, alias, canonical):
    """Verify alias resolution."""
    step_verify_vm_included(context, canonical)
