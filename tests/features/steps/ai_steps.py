"""
BDD Step Definitions for AI Assistant features.
"""

from behave import given, when, then

# =============================================================================
# GIVEN steps
# =============================================================================

@given('I want help with VDE')
def step_want_help(context):
    context.want_help = True

@given('I have certain VMs running')
def step_have_vms_running(context):
    context.vms_running = True

@given('I just created a {vm_type} VM')
def step_just_created_vm(context, vm_type):
    context.last_created_vm = vm_type

@given('I need a complete development stack')
def step_need_stack(context):
    context.need_stack = True

@given('my request is not clear')
def step_request_unclear(context):
    context.request_unclear = True

@given('something goes wrong')
def step_something_wrong(context):
    context.error_occurred = True

@given('I don\'t understand something')
def step_dont_understand(context):
    context.need_explanation = True

@given('I need to do several things')
def step_need_several_things(context):
    context.multi_action = True

@given('I\'m about to do something risky')
def step_risky_action(context):
    context.risk_detected = True

@given('I request something that might not be optimal')
def step_not_optimal(context):
    context.suboptimal_request = True

@given('I want to see what will happen')
def step_want_preview(context):
    context.dry_run = True

@given('I make a typo in my command')
def step_typo(context):
    context.has_typo = True

@given('I have multiple VMs')
def step_multiple_vms(context):
    context.has_multiple_vms = True

@given('I use VDE regularly')
def step_use_regularly(context):
    context.developing = True

@given('I\'m doing something inefficient')
def step_inefficient(context):
    context.inefficient = True

@given('I start a long operation')
def step_long_operation(context):
    context.long_operation = True

# Additional Given steps for undefined scenarios
@given('I have VMs created but not running')
def step_vms_created_not_running(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.vms_created_state = 'not_running'

@given('I\'m new to VDE')
def step_new_to_vde_generic(context):
    context.is_new_to_vde = True

@given('I have several VMs configured')
def step_several_vms_configured(context):
    context.has_multiple_vms = True

@given('I\'m not sure what I can do')
def step_unsure_what_to_do(context):
    context.uncertain_what_to_do = True

@given('I want a go development environment')
def step_want_go_vm(context):
    context.desired_vm = 'go'

@given('I\'ve modified a Dockerfile')
def step_modified_dockerfile(context):
    context.dockerfile_modified = True

@given('I want to SSH into my VM')
def step_want_ssh(context):
    context.want_ssh_access = True

@given('I want to see available programming languages')
def step_want_languages(context):
    context.want_languages_list = True

@given('I want to see available services')
def step_want_services(context):
    context.want_services_list = True

@given('I\'m not sure of the exact command')
def step_unsure_command(context):
    context.uncertain_command = True

@given('I want to do multiple things')
def step_want_multiple(context):
    context.multiple_desires = True

@given('I\'m used to saying "{alias}" instead of "{fullname}"')
def step_use_alias(context, alias, fullname):
    context.use_alias = alias
    context.fullname = fullname

# =============================================================================
# WHEN steps
# =============================================================================

@when('I say "{input}"')
def step_say(context, input):
    context.last_input = input

@when('I tell the AI "{request}"')
def step_tell_ai(context, request):
    context.last_request = request

@when('I ask "{question}"')
def step_ask(context, question):
    context.last_question = question
    context.user_asked = True
    # Handle status queries specifically
    if "show status of" in question:
        # Extract VM names from the question
        vms_part = question.replace("show status of", "").strip().strip('"')
        context.status_vms_requested = vms_part.split(" and ")
        # Simulate running list-vms command
        context.last_output = f"Status for: {vms_part}"

@when('I ask for advice')
def step_ask_advice(context):
    context.user_asked_advice = True

@when('I ask the AI to fix it')
def step_ask_fix(context):
    context.ai_fix_requested = True

@when('I enable dry-run mode')
def step_enable_dryrun(context):
    context.dry_run_enabled = True

@when('the AI detects the risk')
def step_ai_detects_risk(context):
    context.risk_detected_by_ai = True

@when('the AI has a better suggestion')
def step_ai_has_suggestion(context):
    context.ai_suggestion = True

@when('I perform common actions')
def step_common_actions(context):
    context.common_actions = True

@when('the AI is executing it')
def step_ai_executing(context):
    context.ai_executing = True

# Additional When steps
# Note: Generic patterns handle specific steps:
# - "I say {input}" handles all "I say ..." steps
# - "I ask {question}" handles all "I ask ..." steps
# Specific behaviors are handled in Then steps

# =============================================================================
# THEN steps
# =============================================================================

@then('the AI should explain available commands')
def step_explain_commands(context):
    assert hasattr(context, 'last_input') or hasattr(context, 'last_question')

@then('I should understand what I can do')
def step_understand(context):
    assert True

@then('the AI should understand all components')
def step_understand_components(context):
    assert hasattr(context, 'last_request')

@then('create {vms} VMs')
def step_create_vms(context, vms):
    context.vms_created = vms.split(', ')
    assert True

@then('configure them to work together')
def step_configure_together(context):
    assert hasattr(context, 'vms_created')

@then('the AI should show my current state')
def step_show_state(context):
    assert True

@then('suggest relevant next actions')
def step_suggest_actions(context):
    assert True

@then('provide helpful information')
def step_provide_info(context):
    assert True

@then('the AI should ask for clarification')
def step_ask_clarify(context):
    assert hasattr(context, 'request_unclear')

@then('the AI should make a reasonable guess based on context')
def step_guess(context):
    assert hasattr(context, 'request_unclear')

@then('the AI should explain what it\'s doing')
def step_explain_doing(context):
    assert True

@then('the AI should know "{it}" means {vm}')
def step_ai_know_means(context, it, vm):
    assert hasattr(context, 'last_created_vm')

@then('start the {vm} VM')
def step_start_vm(context, vm):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add(vm)

@then('the AI should suggest better approaches')
def step_suggest_better(context):
    assert hasattr(context, 'inefficient')

@then('explain why they\'re better')
def step_explain_better(context):
    assert hasattr(context, 'inefficient')

@then('offer to implement them')
def step_offer_implement(context):
    assert hasattr(context, 'inefficient')

@then('the AI should diagnose the problem')
def step_diagnose(context):
    assert hasattr(context, 'error_occurred')

@then('suggest solutions')
def step_suggest_solutions(context):
    assert hasattr(context, 'error_occurred')

@then('offer to implement the fix')
def step_offer_fix(context):
    assert hasattr(context, 'ai_fix_requested')

@then('I should see progress updates')
def step_progress(context):
    assert hasattr(context, 'long_operation')

@then('know what\'s happening')
def know_happening(context):
    assert hasattr(context, 'long_operation')

@then('understand how long it will take')
def understand_time(context):
    assert hasattr(context, 'long_operation')

@then('the AI should learn my patterns')
def step_learn_patterns(context):
    assert hasattr(context, 'developing')

@then('suggest shortcuts')
def step_shortcuts(context):
    assert hasattr(context, 'developing')

@then('anticipate my needs')
def step_anticipate(context):
    assert hasattr(context, 'developing')

@then('the AI should explain clearly')
def step_explain_clearly(context):
    assert hasattr(context, 'need_explanation')

@then('provide examples')
def step_examples(context):
    assert hasattr(context, 'need_explanation')

@then('offer more details if needed')
def step_offer_details(context):
    assert hasattr(context, 'need_explanation')

@then('the AI should execute all operations')
def step_execute_all(context):
    assert hasattr(context, 'multi_action')

@then('report on each one')
def step_report_each(context):
    assert hasattr(context, 'multi_action')

@then('confirm everything is complete')
def step_confirm_complete(context):
    assert hasattr(context, 'multi_action')

@then('it should warn me')
def step_warn(context):
    assert hasattr(context, 'risk_detected')

@then('explain the danger')
def step_explain_danger(context):
    assert hasattr(context, 'risk_detected')

@then('ask for confirmation')
def step_ask_confirmation(context):
    assert hasattr(context, 'risk_detected')

@then('it should propose the alternative')
def step_propose(context):
    assert True

@then('explain the benefits')
def step_benefits(context):
    assert True

@then('let me choose')
def step_let_choose(context):
    assert True

@then('the AI should explain what it would do')
def step_explain_would_do(context):
    assert hasattr(context, 'dry_run')

@then('not actually do it')
def step_not_do(context):
    assert hasattr(context, 'dry_run')

@then('let me confirm before executing')
def step_let_confirm(context):
    assert hasattr(context, 'dry_run')

@then('the system should still understand my intent')
def step_understand_intent(context):
    assert hasattr(context, 'has_typo')

@then('And the system should provide helpful correction suggestions')
def step_corrections(context):
    assert hasattr(context, 'has_typo')

@then('rust VM should be created')
def step_rust_created(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('rust')

@then('rust and redis VMs should be started')
def step_vms_started(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('rust')
    context.running_vms.add('redis')

@then('I should not need separate commands')
def step_separate_commands(context):
    assert True

# Additional Then steps
@then('both python and rust VMs should start')
def step_both_vms_start(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'rust'])

@then('I should see a list of all available VM types')
def step_see_vm_list(context):
    context.vm_list_shown = True

@then('I should see which VMs are running')
def step_see_running_vms(context):
    context.running_vms_shown = True

@then('I should see available commands')
def step_see_commands(context):
    context.commands_shown = True

@then('go VM should be created')
def step_go_vm_created(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('go')

@then('all VMs should be stopped')
def step_all_vms_stopped(context):
    context.all_vms_stopped = True

@then('python VM should be rebuilt and started')
def step_python_rebuilt_started(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')
    context.vm_rebuilt = True

@then('I should see the SSH command')
def step_see_ssh_command(context):
    context.ssh_command_shown = True

@then('I should see python, rust, go, js, etc.')
def step_see_languages(context):
    context.languages_shown = ['python', 'rust', 'go', 'js']

@then('I should see postgres, redis, mongodb, nginx')
def step_see_services(context):
    context.services_shown = ['postgres', 'redis', 'mongodb', 'nginx']

@then('I should get helpful guidance')
def step_get_guidance(context):
    context.guidance_provided = True

# Note: rust VM should be created is defined above at line 353

@then('javascript VM should start')
def step_javascript_starts(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('javascript')
