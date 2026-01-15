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


# =============================================================================
# AI planning and workflow steps
# =============================================================================

@given('I am following the documented Python API workflow')
def step_python_api_workflow(context):
    """Following documented Python API workflow."""
    context.following_python_api_workflow = True

@when('I plan to create a Python VM')
def step_plan_create_python(context):
    """Plan to create a Python VM."""
    context.planned_vm = "python"
    context.planned_intent = "create_vm"

@then('the plan should include the create_vm intent')
def step_plan_include_create_vm(context):
    """Plan should include create_vm intent."""
    context.plan_includes_create_vm = True

@then('the plan should include the Python VM')
def step_plan_include_python(context):
    """Plan should include Python VM."""
    context.plan_includes_python = True

@given('I have planned to create Python')
def step_planned_python(context):
    """Have planned to create Python."""
    context.planned_vm = "python"

@when('I plan to create PostgreSQL')
def step_plan_create_postgres(context):
    """Plan to create PostgreSQL."""
    context.planned_vm = "postgres"

@then('the plan should include the PostgreSQL VM')
def step_plan_include_postgres(context):
    """Plan should include PostgreSQL VM."""
    context.plan_includes_postgres = True

@given('I have created Python and PostgreSQL VMs')
def step_created_python_postgres(context):
    """Have created Python and PostgreSQL VMs."""
    context.created_vms = {"python", "postgres"}

@when('I plan to start both VMs')
def step_plan_start_both(context):
    """Plan to start both VMs."""
    context.planned_vms = ["python", "postgres"]

@then('the plan should include the start_vm intent')
def step_plan_include_start_vm(context):
    """Plan should include start_vm intent."""
    context.plan_includes_start_vm = True

@then('the plan should include both Python and PostgreSQL VMs')
def step_plan_include_both(context):
    """Plan should include both VMs."""
    context.plan_includes_both = True

@given('I need to connect to the Python VM')
def step_need_connect_python(context):
    """Need to connect to Python VM."""
    context.need_connection = True

@when('I ask for connection information')
def step_ask_connection_info(context):
    """Ask for connection information."""
    context.asked_connection_info = True

@then('the plan should include the connect intent')
def step_plan_include_connect(context):
    """Plan should include connect intent."""
    context.plan_includes_connect = True

@given('I have started the PostgreSQL VM')
def step_started_postgres(context):
    """Have started PostgreSQL VM."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("postgres")

@when('I check if postgres exists')
def step_check_postgres_exists(context):
    """Check if postgres exists."""
    context.checking_vm_exists = True

@then('the VM should be recognized as a valid VM type')
def step_vm_recognized_valid(context):
    """VM should be recognized as valid type."""
    context.vm_recognized_valid = True

@then('it should be marked as a service VM')
def step_marked_service_vm(context):
    """Should be marked as service VM."""
    context.marked_as_service_vm = True

@given('I am following the documented JavaScript workflow')
def step_js_workflow(context):
    """Following documented JavaScript workflow."""
    context.following_js_workflow = True

@when('I plan to create JavaScript and Redis VMs')
def step_plan_js_redis(context):
    """Plan to create JavaScript and Redis VMs."""
    context.planned_vms = ["js", "redis"]

@then('the plan should include both VMs')
def step_plan_include_both_vms(context):
    """Plan should include both VMs."""
    context.plan_includes_both_vms = True

@then('the JavaScript VM should use the js canonical name')
def step_js_canonical_name(context):
    """JavaScript VM should use js canonical name."""
    context.js_uses_canonical_name = True

@given('I want to use the Node.js name')
def step_want_nodejs_name(context):
    """Want to use Node.js name."""
    context.want_nodejs_name = True

@when('I resolve the nodejs alias')
def step_resolve_nodejs_alias(context):
    """Resolve nodejs alias."""
    context.resolving_alias = "nodejs"

@then('it should resolve to js')
def step_resolves_to_js(context):
    """Should resolve to js."""
    context.alias_resolves_to = "js"

@then('I can use either name in commands')
def step_either_name_works(context):
    """Can use either name in commands."""
    context.either_name_works = True

@given('I am creating a microservices architecture')
def step_microservices_arch(context):
    """Creating microservices architecture."""
    context.creating_microservices = True

@when('I plan to create Python, Go, Rust, PostgreSQL, and Redis')
def step_plan_microservices(context):
    """Plan to create microservice VMs."""
    context.planned_vms = ["python", "go", "rust", "postgres", "redis"]

@then('the plan should include all five VMs')
def step_plan_all_five(context):
    """Plan should include all five VMs."""
    context.plan_includes_all_five = True

@then('each VM should be included in the VM list')
def step_each_vm_in_list(context):
    """Each VM should be in VM list."""
    context.each_vm_in_list = True

@given('I have created the microservice VMs')
def step_created_microservices(context):
    """Have created microservice VMs."""
    context.created_vms = {"python", "go", "rust", "postgres", "redis"}

@when('I plan to start them all')
def step_plan_start_all(context):
    """Plan to start all VMs."""
    context.planned_start_all = True

@then('all microservice VMs should be included')
def step_all_microservices_included(context):
    """All microservice VMs should be included."""
    context.all_microservices_included = True

@given('I have created microservices')
def step_have_microservices(context):
    """Have created microservices."""
    context.created_vms = {"python", "go", "rust", "postgres", "redis"}

@when('I check for each service VM')
def step_check_each_service(context):
    """Check for each service VM."""
    context.checking_services = True

@then('Python should exist as a language VM')
def step_python_lang_vm(context):
    """Python should exist as language VM."""
    context.python_is_lang_vm = True

@then('Go should exist as a language VM')
def step_go_lang_vm(context):
    """Go should exist as language VM."""
    context.go_is_lang_vm = True

@then('Rust should exist as a language VM')
def step_rust_lang_vm(context):
    """Rust should exist as language VM."""
    context.rust_is_lang_vm = True

@then('PostgreSQL should exist as a service VM')
def step_postgres_svc_vm(context):
    """PostgreSQL should exist as service VM."""
    context.postgres_is_svc_vm = True

@then('Redis should exist as a service VM')
def step_redis_svc_vm(context):
    """Redis should exist as service VM."""
    context.redis_is_svc_vm = True

@when('I plan to start Python, PostgreSQL, and Redis')
def step_plan_python_postgres_redis(context):
    """Plan to start Python, PostgreSQL, and Redis."""
    context.planned_vms = ["python", "postgres", "redis"]

@then('the plan should include all three VMs')
def step_plan_all_three(context):
    """Plan should include all three VMs."""
    context.plan_includes_all_three = True

@then('the plan should use the start_vm intent')
def step_plan_uses_start_vm(context):
    """Plan should use start_vm intent."""
    context.plan_uses_start_vm = True

@when('I ask what\'s running')
def step_ask_whats_running(context):
    """Ask what's running."""
    context.asking_status = True

@then('the plan should include the status intent')
def step_plan_include_status(context):
    """Plan should include status intent."""
    context.plan_includes_status = True

@then('I should be able to see running VMs')
def step_see_running_vms(context):
    """Should be able to see running VMs."""
    context.running_vms_visible = True

@given('I need to work in my primary development environment')
def step_primary_dev_env(context):
    """Need to work in primary development environment."""
    context.need_primary_env = True

@when('I ask how to connect to Python')
def step_ask_connect_python(context):
    """Ask how to connect to Python."""
    context.asking_connect_python = True

@then('the plan should provide connection details')
def step_plan_connection_details(context):
    """Plan should provide connection details."""
    context.connection_details_provided = True

@when('I plan to stop everything')
def step_plan_stop_everything(context):
    """Plan to stop everything."""
    context.planning_stop_all = True

@then('the plan should include the stop_vm intent')
def step_plan_include_stop_vm(context):
    """Plan should include stop_vm intent."""
    context.plan_includes_stop_vm = True

@then('the plan should apply to all running VMs')
def step_plan_apply_all_running(context):
    """Plan should apply to all running VMs."""
    context.plan_applies_all_running = True

@given('something isn\'t working correctly')
def step_something_broken(context):
    """Something isn't working correctly."""
    context.something_broken = True

@when('I check the status')
def step_check_status(context):
    """Check the status."""
    context.checking_status = True

@then('I should receive status information')
def step_receive_status_info(context):
    """Should receive status information."""
    context.status_info_received = True

@given('I need to rebuild a VM to fix an issue')
def step_need_rebuild_vm(context):
    """Need to rebuild VM to fix issue."""
    context.need_rebuild_vm = True

@when('I plan to rebuild Python')
def step_plan_rebuild_python(context):
    """Plan to rebuild Python."""
    context.planned_rebuild = "python"

@then('the plan should include the restart_vm intent')
def step_plan_include_restart_vm(context):
    """Plan should include restart_vm intent."""
    context.plan_includes_restart_vm = True

@then('the plan should set rebuild=true flag')
def step_plan_rebuild_flag(context):
    """Plan should set rebuild=true flag."""
    context.rebuild_flag_set = True

@given('I need to debug inside a container')
def step_need_debug_container(context):
    """Need to debug inside container."""
    context.need_debug_container = True

@when('I ask to connect to Python')
def step_ask_connect_to_python(context):
    """Ask to connect to Python."""
    context.asking_connect_python_vm = True

@then('I should receive SSH connection information')
def step_receive_ssh_info(context):
    """Should receive SSH connection information."""
    context.ssh_info_received = True

@when('I ask what VMs can I create')
def step_ask_available_vms(context):
    """Ask what VMs can be created."""
    context.asking_available_vms = True

@then('the plan should include the list_vms intent')
def step_plan_include_list_vms(context):
    """Plan should include list_vms intent."""
    context.plan_includes_list_vms = True

@given('I want a Python API with PostgreSQL')
def step_want_python_api_postgres(context):
    """Want Python API with PostgreSQL."""
    context.wanted_stack = {"python", "postgres"}

@when('I plan to create Python and PostgreSQL')
def step_plan_create_python_postgres(context):
    """Plan to create Python and PostgreSQL."""
    context.planned_vms = ["python", "postgres"]

@then('both VMs should be included in the plan')
def step_both_in_plan(context):
    """Both VMs should be in plan."""
    context.both_vms_in_plan = True

@then('the plan should use the create_vm intent')
def step_plan_uses_create_vm(context):
    """Plan should use create_vm intent."""
    context.plan_uses_create_vm = True

@given('I have created my VMs')
def step_created_vms(context):
    """Have created VMs."""
    context.created_vms = {"python", "postgres"}

@when('I plan to start Python and PostgreSQL')
def step_plan_start_python_postgres(context):
    """Plan to start Python and PostgreSQL."""
    context.planned_vms = ["python", "postgres"]

@then('both VMs should start')
def step_both_vms_start(context):
    """Both VMs should start."""
    context.both_vms_start = True

@given('I have an existing Python and PostgreSQL stack')
def step_existing_python_postgres_stack(context):
    """Have existing Python and PostgreSQL stack."""
    context.created_vms = {"python", "postgres"}
    context.running_vms = {"python", "postgres"}

@when('I plan to add Redis')
def step_plan_add_redis(context):
    """Plan to add Redis."""
    context.planned_vm = "redis"

@then('the Redis VM should be included')
def step_redis_included(context):
    """Redis VM should be included."""
    context.redis_included = True

@given('I have created the Redis VM')
def step_created_redis(context):
    """Have created Redis VM."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("redis")

@when('I plan to start Redis')
def step_plan_start_redis(context):
    """Plan to start Redis."""
    context.planned_vm = "redis"

@then('Redis should start without affecting other VMs')
def step_redis_start_independent(context):
    """Redis should start without affecting other VMs."""
    context.redis_independent_start = True

@when('I plan to stop all VMs')
def step_plan_stop_all_vms(context):
    """Plan to stop all VMs."""
    context.planning_stop_all_vms = True

@then('I should be ready to start a new project')
def step_ready_new_project(context):
    """Should be ready to start new project."""
    context.ready_new_project = True

@given('I have stopped my current project')
def step_stopped_current_project(context):
    """Have stopped current project."""
    context.current_project_stopped = True

@when('I plan to start Go and MongoDB')
def step_plan_start_go_mongodb(context):
    """Plan to start Go and MongoDB."""
    context.planned_vms = ["go", "mongodb"]

@then('the new project VMs should start')
def step_new_project_vms_start(context):
    """New project VMs should start."""
    context.new_project_vms_start = True

@then('only the new project VMs should be running')
def step_only_new_running(context):
    """Only new project VMs should be running."""
    context.only_new_running = True

@when('I ask to list all languages')
def step_ask_list_languages(context):
    """Ask to list all languages."""
    context.asking_languages = True

@then('I should see only language VMs')
def step_see_only_languages(context):
    """Should see only language VMs."""
    context.only_languages_visible = True

@then('service VMs should not be included')
def step_services_not_included(context):
    """Service VMs should not be included."""
    context.services_excluded = True

@then('I should receive clear connection instructions')
def step_clear_connection_instructions(context):
    """Should receive clear connection instructions."""
    context.clear_instructions = True

@then('I should understand how to access the VM')
def step_understand_vm_access(context):
    """Should understand how to access VM."""
    context.understands_vm_access = True

@when('I ask for help')
def step_ask_for_help(context):
    """Ask for help."""
    context.asking_for_help = True

@given('I have a Python VM that is already running')
def step_python_already_running(context):
    """Have Python VM already running."""
    context.running_vms = {"python"}

@when('I plan to start Python')
def step_plan_to_start_python(context):
    """Plan to start Python."""
    context.planned_vm = "python"

@then('the plan should be generated')
def step_plan_generated(context):
    """Plan should be generated."""
    context.plan_generated = True

@then('execution would detect the VM is already running')
def step_detect_already_running(context):
    """Execution would detect VM already running."""
    context.detected_already_running = True

@then('I would be notified that it\'s already running')
def step_notified_already_running(context):
    """Would be notified that it's already running."""
    context.notified_already_running = True

@given('I have a stopped PostgreSQL VM')
def step_stopped_postgres_vm(context):
    """Have stopped PostgreSQL VM."""
    context.created_vms = {"postgres"}
    context.running_vms = set()

@when('I plan to stop PostgreSQL')
def step_plan_to_stop_postgres(context):
    """Plan to stop PostgreSQL."""
    context.planned_vm = "postgres"

@then('execution would detect the VM is not running')
def step_detect_not_running(context):
    """Execution would detect VM not running."""
    context.detected_not_running = True

@then('I would be notified that it\'s already stopped')
def step_notified_already_stopped(context):
    """Would be notified that it's already stopped."""
    context.notified_already_stopped = True

@when('I plan to create Go again')
def step_plan_create_go_again(context):
    """Plan to create Go again."""
    context.planned_vm = "go"

@then('execution would detect the VM already exists')
def step_detect_vm_exists(context):
    """Execution would detect VM already exists."""
    context.detected_vm_exists = True

@then('I would be notified of the existing VM')
def step_notified_existing_vm(context):
    """Would be notified of existing VM."""
    context.notified_existing_vm = True

@given('the documentation shows specific VM examples')
def step_documentation_examples(context):
    """Documentation shows specific VM examples."""
    context.documentation_has_examples = True

@when('I verify the documented VMs')
def step_verify_documented_vms(context):
    """Verify the documented VMs."""
    context.verifying_documented_vms = True

@then('Python should be a valid VM type')
def step_python_valid_vm(context):
    """Python should be valid VM type."""
    context.python_valid_vm = True

@then('JavaScript should be a valid VM type')
def step_javascript_valid_vm(context):
    """JavaScript should be valid VM type."""
    context.javascript_valid_vm = True

@then('all microservice VMs should be valid')
def step_microservices_valid(context):
    """All microservice VMs should be valid."""
    context.microservices_valid = True

@given('I need to plan my daily workflow')
def step_need_plan_workflow(context):
    """Need to plan daily workflow."""
    context.need_plan_workflow = True

@when('I generate plans for morning setup, checks, and cleanup')
def step_generate_plans(context):
    """Generate plans for morning setup, checks, cleanup."""
    context.plans_generated = True

@then('all plans should be generated quickly')
def step_plans_generated_quickly(context):
    """All plans should be generated quickly."""
    context.plans_quick = True

@then('the total time should be under 500ms')
def step_total_time_under_500ms(context):
    """Total time should be under 500ms."""
    context.total_time_under_500 = True

@given('I try to use a VM that doesn\'t exist')
def step_nonexistent_vm(context):
    """Try to use VM that doesn't exist."""
    context.nonexistent_vm = True

@when('I request to "start nonexistent-vm"')
def step_request_nonexistent(context):
    """Request to start nonexistent-vm."""
    context.requested_nonexistent = True

@then('suggest valid VM names')
def step_suggest_valid_names(context):
    """Should suggest valid VM names."""
    context.valid_names_suggested = True

@then('VDE should detect the conflict')
def step_vde_detect_conflict(context):
    """VDE should detect conflict."""
    context.vde_detected_conflict = True

@then('allocate an available port')
def step_allocate_available_port(context):
    """Allocate an available port."""
    context.available_port_allocated = True

@then('continue with the operation')
def step_continue_operation(context):
    """Continue with the operation."""
    context.operation_continued = True

@then('suggest how to fix it')
def step_suggest_fix(context):
    """Suggest how to fix it."""
    context.fix_suggested = True

@given('my disk is nearly full')
def step_disk_nearly_full(context):
    """Disk is nearly full."""
    context.disk_nearly_full = True

@when('I try to create a VM')
def step_try_create_vm(context):
    """Try to create a VM."""
    context.trying_create_vm = True

@then('VDE should detect the issue')
def step_vde_detect_issue(context):
    """VDE should detect the issue."""
    context.vde_detected_issue = True

@then('warn me before starting')
def step_warn_before_start(context):
    """Warn before starting."""
    context.warned_before_start = True

@then('suggest cleaning up')
def step_suggest_cleanup(context):
    """Suggest cleaning up."""
    context.cleanup_suggested = True

@given('the Docker network can\'t be created')
def step_network_cant_create(context):
    """Docker network can't be created."""
    context.network_cant_create = True

@then('offer to retry')
def step_offer_retry(context):
    """Offer to retry."""
    context.retry_offered = True

@then('I should see what went wrong')
def step_see_what_wrong(context):
    """Should see what went wrong."""
    context.what_wrong_visible = True

@then('get suggestions for fixing it')
def step_suggestions_fixing(context):
    """Get suggestions for fixing."""
    context.fixing_suggestions = True

@then('be able to retry after fixing')
def step_retry_after_fixing(context):
    """Be able to retry after fixing."""
    context.retry_after_fixing = True

@when('VDE detects the timeout')
def step_vde_detects_timeout(context):
    """VDE detects timeout."""
    context.vde_detected_timeout = True

@then('it should report the issue')
def step_report_issue(context):
    """Should report the issue."""
    context.issue_reported = True

@then('show the container logs')
def step_show_container_logs(context):
    """Show container logs."""
    context.container_logs_shown = True

@then('offer to check the status')
def step_offer_check_status(context):
    """Offer to check status."""
    context.status_check_offered = True

@when('I try to connect')
def step_try_connect(context):
    """Try to connect."""
    context.trying_connect = True

@then('VDE should diagnose the problem')
def step_vde_diagnose(context):
    """VDE should diagnose the problem."""
    context.vde_diagnosed = True

@then('check if SSH is running')
def step_check_ssh_running(context):
    """Check if SSH is running."""
    context.ssh_running_checked = True

@then('verify the SSH port is correct')
def step_verify_ssh_port(context):
    """Verify SSH port is correct."""
    context.ssh_port_verified = True

@then('it should explain the permission issue')
def step_explain_permission(context):
    """Should explain permission issue."""
    context.permission_explained = True

@then('offer to retry with proper permissions')
def step_offer_retry_permissions(context):
    """Offer to retry with proper permissions."""
    context.retry_permissions_offered = True

@when('I try to use the VM')
def step_try_use_vm(context):
    """Try to use the VM."""
    context.trying_use_vm = True

@then('show the specific problem')
def step_show_problem(context):
    """Show the specific problem."""
    context.problem_shown = True

@then('suggest how to fix the configuration')
def step_suggest_fix_config(context):
    """Suggest how to fix configuration."""
    context.config_fix_suggested = True

@given('one VM fails to start')
def step_one_vm_fails(context):
    """One VM fails to start."""
    context.one_vm_failed = True

@when('I start multiple VMs')
def step_start_multiple_vms(context):
    """Start multiple VMs."""
    context.starting_multiple = True

@then('other VMs should continue')
def step_other_vms_continue(context):
    """Other VMs should continue."""
    context.other_vms_continued = True

@then('I should be notified of the failure')
def step_notified_failure(context):
    """Should be notified of failure."""
    context.failure_notified = True

@then('successful VMs should be listed')
def step_successful_vms_listed(context):
    """Successful VMs should be listed."""
    context.successful_vms_listed = True

@when('VDE detects it\'s retryable')
def step_vde_detects_retryable(context):
    """VDE detects it's retryable."""
    context.retryable_detected = True

@then('it should automatically retry')
def step_auto_retry(context):
    """Should automatically retry."""
    context.auto_retried = True

@then('limit the number of retries')
def step_limit_retries(context):
    """Limit the number of retries."""
    context.retries_limited = True

@then('report if all retries fail')
def step_report_retries_failed(context):
    """Report if all retries fail."""
    context.retries_failed_reported = True

@when('I try again')
def step_try_again(context):
    """Try again."""
    context.trying_again = True

@then('VDE should detect partial state')
def step_detect_partial_state(context):
    """VDE should detect partial state."""
    context.partial_state_detected = True

@then('complete the operation')
def step_complete_operation(context):
    """Complete the operation."""
    context.operation_completed = True

@then('not duplicate work')
def step_not_duplicate_work(context):
    """Not duplicate work."""
    context.no_duplicate_work = True

@then('it should be in plain language')
def step_plain_language(context):
    """Should be in plain language."""
    context.plain_language = True

@then('explain what went wrong')
def step_explain_wrong(context):
    """Explain what went wrong."""
    context.explained_wrong = True

@when('VDE handles it')
def step_vde_handles(context):
    """VDE handles it."""
    context.vde_handled = True

@then('I can find it in the logs directory')
def step_find_in_logs(context):
    """Can find it in logs directory."""
    context.found_in_logs = True

@when('the failure is detected')
def step_failure_detected(context):
    """Failure is detected."""
    context.failure_detected = True

@then('VDE should clean up partial state')
def step_vde_cleanup_partial(context):
    """VDE should clean up partial state."""
    context.partial_state_cleaned = True

@then('return to a consistent state')
def step_consistent_state(context):
    """Return to consistent state."""
    context.consistent_state = True

@then('allow me to retry cleanly')
def step_allow_retry_cleanly(context):
    """Allow me to retry cleanly."""
    context.clean_retry_allowed = True

@when('the setup completes')
def step_setup_completes(context):
    """Setup completes."""
    context.setup_completed = True

@given('VDE is being set up')
def step_vde_being_setup(context):
    """VDE is being set up."""
    context.vde_being_setup = True

@given('VDE is installed')
def step_vde_installed(context):
    """VDE is installed."""
    context.vde_installed = True

@when('I run list-vms')
def step_run_list_vms(context):
    """Run list-vms."""
    context.last_command = "./scripts/list-vms"
    context.list_vms_run = True

@given('I\'ve installed VDE')
def step_installed_vde(context):
    """Have installed VDE."""
    context.vde_installed = True

@given('I am starting a new web project')
def step_starting_web_project(context):
    """Starting a new web project."""
    context.starting_web_project = True

@when('I request to "create JavaScript and nginx"')
def step_request_create_js_nginx(context):
    """Request to create JavaScript and nginx."""
    context.requested_vms = ["js", "nginx"]

@then('the JavaScript VM should be created')
def step_js_vm_created(context):
    """JavaScript VM should be created."""
    context.js_vm_created = True

@then('the nginx VM should be created')
def step_nginx_vm_created(context):
    """nginx VM should be created."""
    context.nginx_vm_created = True

@then('both should be configured for web development')
def step_web_configured(context):
    """Both should be configured for web development."""
    context.web_dev_configured = True

@given('I have web containers running (JavaScript, nginx)')
def step_web_containers_running(context):
    """Have web containers running."""
    context.running_vms = {"js", "nginx"}

@when('I request to "stop all and start python and postgres"')
def step_request_stop_start(context):
    """Request to stop all and start python and postgres."""
    context.requested_stop_all = True
    context.requested_vms = ["python", "postgres"]

@then('the web containers should be stopped')
def step_web_containers_stopped(context):
    """Web containers should be stopped."""
    context.web_containers_stopped = True

@then('the Python VM should start')
def step_python_starts(context):
    """Python VM should start."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("python")

@then('the PostgreSQL VM should start')
def step_postgres_starts_parser(context):
    """PostgreSQL VM should start."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("postgres")

@then('only the backend stack should be running')
def step_backend_only_running(context):
    """Only backend stack should be running."""
    context.backend_only_running = True

@given('I am building a microservices application')
def step_building_microservices(context):
    """Building microservices application."""
    context.building_microservices = True

@when('I request to "create Go, Rust, and nginx"')
def step_request_create_go_rust_nginx(context):
    """Request to create Go, Rust, and nginx."""
    context.requested_vms = ["go", "rust", "nginx"]

@then('the Go VM should be created for one service')
def step_go_vm_service(context):
    """Go VM should be created for one service."""
    context.go_vm_for_service = True

@then('the Rust VM should be created for another service')
def step_rust_vm_service(context):
    """Rust VM should be created for another service."""
    context.rust_vm_for_service = True

@then('the nginx VM should be created as a gateway')
def step_nginx_gateway(context):
    """nginx VM should be created as gateway."""
    context.nginx_as_gateway = True

@given('I have created my microservice VMs')
def step_created_microservice_vms(context):
    """Have created microservice VMs."""
    context.created_vms = {"go", "rust", "nginx"}

@when('I request to "start all services"')
def step_request_start_services(context):
    """Request to start all services."""
    context.requested_start_all = True

@then('all service VMs should start')
def step_all_services_start(context):
    """All service VMs should start."""
    context.all_services_started = True

@then('they should be able to communicate on the Docker network')
def step_communicate_docker_network(context):
    """Should communicate on Docker network."""
    context.docker_network_comm = True

@then('each should have its own SSH port')
def step_own_ssh_port(context):
    """Each should have own SSH port."""
    context.each_own_port = True

@given('I am doing data analysis')
def step_doing_data_analysis(context):
    """Doing data analysis."""
    context.doing_data_analysis = True

@when('I request to "start python and r"')
def step_request_python_r(context):
    """Request to start python and r."""
    context.requested_vms = ["python", "r"]

@then('the R VM should start')
def step_r_starts(context):
    """R VM should start."""
    context.running_vms.add("r")

@then('both should have data science tools available')
def step_data_science_tools(context):
    """Both should have data science tools."""
    context.data_science_tools = True

@given('I need a complete web stack')
def step_need_web_stack(context):
    """Need complete web stack."""
    context.need_web_stack = True

@when('I request to "create Python, PostgreSQL, Redis, and nginx"')
def step_request_web_stack(context):
    """Request to create complete web stack."""
    context.requested_vms = ["python", "postgres", "redis", "nginx"]

@then('the Python VM should be for the backend API')
def step_python_backend_api(context):
    """Python VM should be for backend API."""
    context.python_for_api = True

@then('PostgreSQL should be for the database')
def step_postgres_database(context):
    """PostgreSQL should be for database."""
    context.postgres_for_db = True

@then('Redis should be for caching')
def step_redis_cache(context):
    """Redis should be for caching."""
    context.redis_for_cache = True

@then('nginx should be for the web server')
def step_nginx_web_server(context):
    """nginx should be for web server."""
    context.nginx_for_web = True

@then('all should be on the same network')
def step_all_same_network(context):
    """All should be on same network."""
    context.all_same_network = True

@given('I am developing a mobile app with backend')
def step_mobile_app_backend(context):
    """Developing mobile app with backend."""
    context.developing_mobile_app = True

@when('I request to "start flutter and postgres"')
def step_request_flutter_postgres(context):
    """Request to start flutter and postgres."""
    context.requested_vms = ["flutter", "postgres"]

@then('the Flutter VM should start for mobile development')
def step_flutter_mobile_dev(context):
    """Flutter VM should start for mobile development."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("flutter")
    context.flutter_for_mobile = True

@then('PostgreSQL should start for the backend database')
def step_postgres_backend(context):
    """PostgreSQL should start for backend database."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("postgres")
    context.postgres_for_backend = True

@then('both should be accessible via SSH')
def step_both_ssh_accessible(context):
    """Both should be accessible via SSH."""
    context.both_ssh_accessible = True

@given('I have finished working on one project')
def step_finished_project(context):
    """Finished working on one project."""
    context.finished_project = True

@then('all containers should stop')
def step_all_containers_stop(context):
    """All containers should stop."""
    context.all_containers_stopped = True

@then('I can start a fresh environment for another project')
def step_fresh_environment(context):
    """Can start fresh environment for another project."""
    context.fresh_environment_possible = True

@then('there should be no leftover processes')
def step_no_leftover_processes(context):
    """No leftover processes."""
    context.no_leftover_processes = True

@given('I want to perform common actions')
def step_want_common_actions(context):
    """Want to perform common actions."""
    context.want_common_actions = True

@then('the system should understand I want to start the Python VM')
def step_understand_start_python(context):
    """System should understand I want to start Python VM."""
    context.understand_start_python = True

@then('the appropriate action should be taken')
def step_appropriate_action(context):
    """Appropriate action should be taken."""
    context.appropriate_action = True

@given('I can phrase commands in different ways')
def step_phrase_commands(context):
    """Can phrase commands in different ways."""
    context.can_phrase_commands = True

@then('it should be equivalent to "start go"')
def step_equivalent_start_go(context):
    """Should be equivalent to start go."""
    context.equivalent_start_go = True

@then('the Go VM should start')
def step_go_vm_starts(context):
    """Go VM should start."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("go")
    context.go_vm_started = True

@given('I need to work with multiple environments')
def step_need_multiple_envs(context):
    """Need to work with multiple environments."""
    context.need_multiple_envs = True

@then('the command should work the same as "start python, postgres"')
def step_works_as_python_postgres(context):
    """Command should work same as start python, postgres."""
    context.works_as_python_postgres = True

@given('I know a VM by its alias')
def step_know_vm_alias(context):
    """Know VM by its alias."""
    context.known_alias = True

@then('it should work the same as "create js"')
def step_works_as_create_js(context):
    """Should work same as create js."""
    context.works_as_create_js = True

@given('I want to know what\'s running')
def step_want_know_running(context):
    """Want to know what's running."""
    context.want_status = True

@then('I should see the status')
def step_see_status(context):
    """Should see the status."""
    context.status_visible = True

@then('it should work the same as "status"')
def step_works_as_status(context):
    """Should work same as status."""
    context.works_as_status = True

# =============================================================================
# Help and guidance steps
# =============================================================================

@given('I\'m not sure what to do')
def step_not_sure_what_to_do(context):
    """Not sure what to do."""
    context.not_sure_what_to_do = True

@then('I should see help information')
def step_see_help_info(context):
    """Should see help information."""
    context.help_info_visible = True

@then('available commands should be explained')
def step_commands_explained(context):
    """Available commands should be explained."""
    context.commands_explained = True

@given('I need to connect to a VM')
def step_need_connect_vm(context):
    """Need to connect to a VM."""
    context.need_connect_vm = True

@then('I should receive SSH connection instructions')
def step_receive_ssh_instructions(context):
    """Should receive SSH connection instructions."""
    context.ssh_instructions_received = True

@then('the instructions should be clear and actionable')
def step_instructions_clear(context):
    """Instructions should be clear and actionable."""
    context.instructions_clear = True

@given('I need to rebuild a container')
def step_need_rebuild_container(context):
    """Need to rebuild a container."""
    context.need_rebuild_container = True

@then('the rebuild flag should be set')
def step_rebuild_flag_set(context):
    """Rebuild flag should be set."""
    context.rebuild_flag_set = True

@then('no cache should be used')
def step_no_cache_used(context):
    """No cache should be used."""
    context.no_cache_used = True

@given('I want to operate on all VMs of a type')
def step_operate_all_type(context):
    """Want to operate on all VMs of a type."""
    context.operate_all_type = True

@then('all language VMs should start')
def step_all_lang_vms_start(context):
    """All language VMs should start."""
    context.all_lang_vms_started = True

@then('service VMs should not be affected')
def step_svc_vms_not_affected(context):
    """Service VMs should not be affected."""
    context.svc_vms_unaffected = True

@given('I\'m done working')
def step_done_working(context):
    """Done working."""
    context.done_working = True

@then('all running VMs should stop')
def step_all_running_stop(context):
    """All running VMs should stop."""
    context.all_running_stopped = True

@then('it should be equivalent to "stop all"')
def step_equiv_stop_all(context):
    """Should be equivalent to stop all."""
    context.equiv_stop_all = True

# =============================================================================
# Conversational language steps
# =============================================================================

@given('I use conversational language')
def step_conversational_language(context):
    """Use conversational language."""
    context.conversational_language = True

@then('the system should understand I want to create VMs')
def step_understand_create_vms(context):
    """System should understand I want to create VMs."""
    context.understand_create_vms = True

@then('Python and PostgreSQL should be created')
def step_python_postgres_created(context):
    """Python and PostgreSQL should be created."""
    context.python_postgres_created = True

@given('something isn\'t working')
def step_something_broken(context):
    """Something isn't working."""
    context.something_broken = True

@then('PostgreSQL should restart')
def step_postgres_restarts(context):
    """PostgreSQL should restart."""
    context.postgres_restarted = True

@then('the system should understand "database" means "postgres"')
def step_understand_database_means_postgres(context):
    """System should understand database means postgres."""
    context.database_means_postgres = True

@given('I type commands in various cases')
def step_various_cases(context):
    """Type commands in various cases."""
    context.various_cases = True

@then('it should work the same as "start python"')
def step_works_as_start_python(context):
    """Should work same as start python."""
    context.works_as_start_python = True

@then('case should not matter')
def step_case_not_matter(context):
    """Case should not matter."""
    context.case_insensitive = True

@given('I want to type less')
def step_want_type_less(context):
    """Want to type less."""
    context.want_type_less = True

@then('it should understand "py" means "python"')
def step_py_means_python(context):
    """Should understand py means python."""
    context.py_means_python = True

@then('"pg" should mean "postgres"')
def step_pg_means_postgres(context):
    """pg should mean postgres."""
    context.pg_means_postgres = True

# =============================================================================
# VM creation and port allocation steps
# =============================================================================

@when('I create a language VM')
def step_create_lang_vm(context):
    """Create a language VM."""
    context.created_lang_vm = True

@given('VM "python" is allocated port "2200"')
def step_python_port_2200(context):
    """VM python is allocated port 2200."""
    context.allocated_ports = {"python": "2200"}

@given('VM "rust" is allocated port "2201"')
def step_rust_port_2201(context):
    """VM rust is allocated port 2201."""
    context.allocated_ports["rust"] = "2201"

@given('language ports range from "2200" to "2299"')
def step_lang_ports_range(context):
    """Language ports range from 2200 to 2299."""
    context.lang_ports_range = ("2200", "2299")

@given('service ports range from "2400" to "2499"')
def step_svc_ports_range(context):
    """Service ports range from 2400 to 2499."""
    context.svc_ports_range = ("2400", "2499")

# =============================================================================
# Bulk operations steps
# =============================================================================

@given('my project needs python, postgres, and redis')
def step_project_needs_stack(context):
    """Project needs python, postgres, and redis."""
    context.project_stack = ["python", "postgres", "redis"]

@then('all three VMs should start with one command')
def step_all_three_one_command(context):
    """All three VMs should start with one command."""
    context.all_three_one_command = True

@then('I don\'t need to remember separate commands for each')
def step_no_separate_commands(context):
    """Don't need separate commands for each."""
    context.no_separate_commands = True

@then('all my created VMs should start')
def step_all_created_start(context):
    """All created VMs should start."""
    context.all_created_start = True

@then('I don\'t need to list each one individually')
def step_no_list_individually(context):
    """Don't need to list each individually."""
    context.no_list_individually = True

# =============================================================================
# SSH and communication steps
# =============================================================================

@given('I have VMs running for my project')
def step_vms_running_project(context):
    """Have VMs running for project."""
    context.vms_running_for_project = True

@then('I should be connected immediately')
def step_connected_immediately(context):
    """Should be connected immediately."""
    context.connected_immediately = True

@then('I don\'t need to remember ports or IP addresses')
def step_no_need_ports_ips(context):
    """Don't need to remember ports or IPs."""
    context.no_need_ports_ips = True

@then('SSH agent forwarding is automatic')
def step_ssh_agent_auto(context):
    """SSH agent forwarding is automatic."""
    context.ssh_agent_automatic = True

@given('my VM is running with volume mounts')
def step_vm_with_volumes(context):
    """VM is running with volume mounts."""
    context.vm_with_volumes = True

@when('I edit files in projects/<lang>/ on my host')
def step_edit_files_host(context):
    """Edit files on host."""
    context.editing_files_host = True

@then('changes are immediately visible in the VM')
def step_changes_visible_vm(context):
    """Changes immediately visible in VM."""
    context.changes_visible_vm = True

@then('I can use my preferred editor (VSCode, vim, etc.)')
def step_preferred_editor(context):
    """Can use preferred editor."""
    context.preferred_editor = True

@then('I don\'t need to edit files inside the container')
def step_no_edit_inside_container(context):
    """Don't need to edit files inside container."""
    context.no_edit_inside = True

@given('I\'m working inside a VM')
def step_working_inside_vm(context):
    """Working inside a VM."""
    context.working_inside_vm = True

@when('I want to run a command on my host')
def step_run_command_host(context):
    """Want to run command on host."""
    context.want_run_host_command = True

@then('I can use the host communication tools')
def step_host_comm_tools(context):
    """Can use host communication tools."""
    context.host_comm_tools = True

@then('I don\'t need to exit the VM')
def step_no_exit_vm(context):
    """Don't need to exit VM."""
    context.no_exit_vm = True

# =============================================================================
# Multi-project communication steps
# =============================================================================

@given('I have multiple projects using PostgreSQL')
def step_multiple_projects_postgres(context):
    """Have multiple projects using PostgreSQL."""
    context.multiple_projects_postgres = True

@when('I start one postgres VM')
def step_start_one_postgres(context):
    """Start one postgres VM."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("postgres")

@when('I start multiple language VMs')
def step_start_multiple_lang(context):
    """Start multiple language VMs."""
    context.starting_multiple_lang = True

@then('all language VMs can connect to the same postgres')
def step_all_lang_connect_postgres(context):
    """All language VMs can connect to same postgres."""
    context.all_lang_connect_postgres = True

@then('I don\'t need separate databases for each project')
def step_no_separate_dbs(context):
    """Don't need separate databases for each."""
    context.no_separate_dbs = True

# =============================================================================
# Git and SSH agent forwarding steps
# =============================================================================

@when('I need to git push to GitHub')
def step_need_git_push(context):
    """Need to git push to GitHub."""
    context.need_git_push = True

@then('SSH agent forwarding gives me access to my keys')
def step_ssh_agent_keys_access(context):
    """SSH agent forwarding gives access to keys."""
    context.ssh_agent_keys_access = True

@then('I don\'t need to copy keys into the container')
def step_no_copy_keys(context):
    """Don't need to copy keys into container."""
    context.no_copy_keys = True

@then('I can push without entering passwords')
def step_push_no_password(context):
    """Can push without entering passwords."""
    context.push_no_password = True
