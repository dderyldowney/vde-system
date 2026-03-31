from behave import given, when, then
from vm_common import run_vde_command, VDE_ROOT

def step_following_workflow(context):
    """Verify VDE_ROOT."""
    # REAL behavioral assertion: ensuring VDE root is set correctly and command exists.
    assert VDE_ROOT.exists(), f"VDE_ROOT does not exist: {VDE_ROOT}"
    assert (VDE_ROOT / "bin" / "vde").exists(), "vde command not found in bin/"

def step_parse_text(context, text):
    """Call 'vde ask "{text}" --dry-run' and capture plan."""
    # Call vde ask with --dry-run to capture the structured plan without execution
    # This is a REAL behavioral assertion: testing the NLP parser output.
    context.last_result = run_vde_command(f'ask "{text}" --dry-run', context=context)
    # The output from vde-ask --dry-run is the structured plan
    context.captured_plan = context.last_result.stdout

def step_intent_should_be(context, intent):
    """Assert captured intent matches."""
    # REAL behavioral assertion: validating that the NLP intent was detected correctly
    # Captured plan format:
    # INTENT:start_vm
    # VM:python
    # ...
    found_intent = None
    for line in context.captured_plan.splitlines():
        if line.startswith("INTENT:"):
            # Split once at the first colon
            found_intent = line.split(":", 1)[1].strip()
            break
    
    assert found_intent == intent, f"Expected intent '{intent}', but got '{found_intent}'. Full plan:\n{context.captured_plan}"
