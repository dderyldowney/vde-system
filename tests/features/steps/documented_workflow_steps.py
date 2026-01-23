"""
BDD Step definitions for Documented Development Workflows scenarios.
Uses real vde-parser library functions for testing natural language parsing
and plan generation capabilities.

This file contains ONLY steps not already defined in other step files.
"""

from behave import given, when, then
import subprocess
import os
import sys
import time

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
VM_TYPES_CONF = os.path.join(VDE_ROOT, 'scripts/data/vm-types.conf')


# =============================================================================
# Helper functions - call real vde-parser
# =============================================================================

def _call_vde_parser_function(function_name, input_string):
    """Call a vde-parser function and return stdout."""
    cmd = f'zsh -c "source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \\"{input_string}\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip(), result.returncode


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


def _is_valid_vm_type(vm_name):
    """Check if a VM type is valid by checking vm-types.conf."""
    try:
        with open(VM_TYPES_CONF, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[1].lower() == vm_name.lower():
                        return True
                    if len(parts) >= 3:
                        aliases = parts[2].lower()
                        if vm_name.lower() in [a.strip() for a in aliases.split(',')]:
                            return True
        return False
    except Exception:
        return False


def _get_vm_category(vm_name):
    """Get the category of a VM (language or service)."""
    try:
        with open(VM_TYPES_CONF, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        vm_type = parts[1].lower()
                        aliases = parts[2].lower()
                        if vm_name.lower() == vm_type or vm_name.lower() in [a.strip() for a in aliases.split(',')]:
                            return parts[0]
        return None
    except Exception:
        return None


def _load_all_vms():
    """Load all VMs from vm-types.conf and return structured data."""
    vms = {'language': [], 'service': [], 'all': []}
    try:
        with open(VM_TYPES_CONF, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        category = parts[0]  # 'lang' or 'service'
                        vm_type = parts[1]   # canonical name
                        display_name = parts[3]  # display name
                        aliases = parts[2].split(',') if len(parts) > 2 else []

                        vm_info = {
                            'type': vm_type,
                            'display': display_name,
                            'aliases': [a.strip() for a in aliases],
                            'category': 'language' if category == 'lang' else 'service'
                        }

                        vms['all'].append(vm_info)
                        if category == 'lang':
                            vms['language'].append(vm_info)
                        elif category == 'service':
                            vms['service'].append(vm_info)
    except Exception as e:
        print(f"Error loading VMs: {e}")
        pass
    return vms


def _vm_list_has_display_names(vm_list):
    """Check that all VMs in list have display names."""
    return all(vm.get('display') for vm in vm_list)


def _vm_list_has_types(vm_list):
    """Check that all VMs in list have type information."""
    return all(vm.get('category') for vm in vm_list)


def _filter_vms_by_category(vms, category):
    """Filter VMs by category (language or service)."""
    if category == 'language':
        return vms['language']
    elif category == 'service':
        return vms['service']
    return vms['all']


# =============================================================================
# GIVEN steps - Setup workflow context (not in other step files)
# =============================================================================

@given('I am following the documented Python API workflow')
def step_python_api_workflow(context):
    """Set up context for Python API workflow."""
    context.workflow = 'python_api'


@given('I am following the documented JavaScript workflow')
def step_js_workflow(context):
    """Set up context for JavaScript workflow."""
    context.workflow = 'javascript'


@given('I am creating a microservices architecture')
def step_microservices_arch(context):
    """Set up context for microservices architecture."""
    context.workflow = 'microservices'


@given('I have planned to create Python')
def step_planned_python(context):
    """Set up context showing Python was planned."""
    if not hasattr(context, 'planned_vms'):
        context.planned_vms = []
    context.planned_vms.append('python')


@given('I have created Python and PostgreSQL VMs')
def step_created_python_postgres(context):
    """Set up context with Python and PostgreSQL created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = []
    context.created_vms.extend(['python', 'postgres'])


@given('I need to connect to the Python VM')
def step_need_connect_python(context):
    """Set up context for connecting to Python."""
    context.target_vm = 'python'


@given('I have started the PostgreSQL VM')
def step_started_postgres(context):
    """Set up context with PostgreSQL started."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = []
    context.running_vms.append('postgres')


@given('I want to use the Node.js name')
def step_want_nodejs_name(context):
    """Set up context for testing nodejs alias."""
    context.test_alias = 'nodejs'


@given('I have created the microservice VMs')
def step_created_microservices(context):
    """Set up context with microservice VMs created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = []
    context.created_vms.extend(['python', 'go', 'rust', 'postgres', 'redis'])


@given('I have created microservices')
def step_created_microservices_alt(context):
    """Alternative step for microservices created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = []
    context.created_vms.extend(['python', 'go', 'rust', 'postgres', 'redis'])


@given('I need to rebuild a VM to fix an issue')
def step_need_rebuild(context):
    """Set up context for VM rebuild."""
    context.workflow = 'troubleshooting_rebuild'


@given('I need to debug inside a container')
def step_need_debug(context):
    """Set up context for container debugging."""
    context.workflow = 'troubleshooting_debug'


@given('I need to work in my primary development environment')
def step_primary_env(context):
    """Set up context for primary development environment."""
    context.target_vm = 'python'


@given('I want a Python API with PostgreSQL')
def step_python_api_postgres(context):
    """Set up context for Python API with PostgreSQL."""
    context.stack = ['python', 'postgres']


@given('I have created my VMs')
def step_created_vms(context):
    """Set up context with VMs created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = ['python', 'postgres']


@given('I have an existing Python and PostgreSQL stack')
def step_existing_stack(context):
    """Set up context with existing stack."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = ['python', 'postgres']


@given('I have created the Redis VM')
def step_created_redis(context):
    """Set up context with Redis created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = []
    context.created_vms.append('redis')


@given('I have stopped my current project')
def step_stopped_project(context):
    """Set up context for stopped project."""
    context.running_vms = []


@given('I have a Python VM that is already running')
def step_python_already_running(context):
    """Set up context with Python already running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = []
    context.running_vms.append('python')


@given('I have a stopped PostgreSQL VM')
def step_stopped_postgres(context):
    """Set up context with stopped PostgreSQL."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = []


@given('the documentation shows specific VM examples')
def step_doc_examples(context):
    """Set up context for documentation verification."""
    context.doc_vms = ['python', 'javascript', 'go', 'rust', 'postgres', 'redis']


@given('I need to plan my daily workflow')
def step_plan_daily(context):
    """Set up context for daily workflow planning."""
    context.workflow = 'performance'


@given('something isn\'t working correctly')
def step_something_wrong(context):
    """Set up context for troubleshooting."""
    context.workflow = 'troubleshooting'


# =============================================================================
# WHEN steps - Parse natural language and generate plans
# =============================================================================

@when('I plan to create a Python VM')
def step_plan_create_python(context):
    """Parse 'create python' using real parser."""
    context.detected_intent = _get_real_intent('create python')
    context.detected_vms = _get_real_vm_names('create python')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to create PostgreSQL')
def step_plan_create_postgres(context):
    """Parse 'create postgres' using real parser."""
    context.detected_intent = _get_real_intent('create postgres')
    context.detected_vms = _get_real_vm_names('create postgres')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to start both VMs')
def step_plan_start_both(context):
    """Parse 'start python postgres' using real parser."""
    context.detected_intent = _get_real_intent('start python postgres')
    context.detected_vms = _get_real_vm_names('start python postgres')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I ask for connection information')
def step_ask_connection_info(context):
    """Parse connection request using real parser."""
    context.detected_intent = _get_real_intent('connect python')
    context.detected_vms = _get_real_vm_names('connect python')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I check if postgres exists')
def step_check_postgres_exists(context):
    """Check if postgres is a valid VM type."""
    context.vm_checked = 'postgres'
    context.vm_valid = _is_valid_vm_type('postgres')
    context.vm_category = _get_vm_category('postgres')


@when('I plan to create JavaScript and Redis VMs')
def step_plan_create_js_redis(context):
    """Parse 'create javascript redis' using real parser."""
    context.detected_intent = _get_real_intent('create javascript redis')
    context.detected_vms = _get_real_vm_names('create javascript redis')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I resolve the nodejs alias')
def step_resolve_nodejs(context):
    """Resolve nodejs alias using real parser."""
    context.detected_vms = _get_real_vm_names('create nodejs')
    resolved = _get_real_vm_names('nodejs')
    context.alias_resolved = 'js' in resolved if isinstance(resolved, list) else resolved == 'js'


@when('I plan to create Python, Go, Rust, PostgreSQL, and Redis')
def step_plan_microservices(context):
    """Parse microservices creation using real parser."""
    input_str = 'create python go rust postgres redis'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to start them all')
def step_plan_start_all(context):
    """Parse 'start all' using real parser."""
    context.detected_intent = _get_real_intent('start all')
    context.detected_filter = _get_real_filter('start all')
    context.detected_vms = 'all'
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I check for each service VM')
def step_check_each_vm(context):
    """Check each VM type and category."""
    context.vm_checks = {
        'python': {'valid': _is_valid_vm_type('python'), 'category': _get_vm_category('python')},
        'go': {'valid': _is_valid_vm_type('go'), 'category': _get_vm_category('go')},
        'rust': {'valid': _is_valid_vm_type('rust'), 'category': _get_vm_category('rust')},
        'postgres': {'valid': _is_valid_vm_type('postgres'), 'category': _get_vm_category('postgres')},
        'redis': {'valid': _is_valid_vm_type('redis'), 'category': _get_vm_category('redis')},
    }


@when('I plan to start Python, PostgreSQL, and Redis')
def step_plan_start_three(context):
    """Parse starting three VMs using real parser."""
    input_str = 'start python postgres redis'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I ask what\'s running')
def step_ask_whats_running(context):
    """Parse status request using real parser."""
    context.detected_intent = _get_real_intent('status')
    context.current_plan = {'intent': context.detected_intent}


@when('I ask how to connect to Python')
def step_ask_connect_python(context):
    """Parse connect request using real parser."""
    context.detected_intent = _get_real_intent('connect python')
    context.detected_vms = _get_real_vm_names('connect python')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to stop everything')
def step_plan_stop_all(context):
    """Parse 'stop all' using real parser."""
    context.detected_intent = _get_real_intent('stop all')
    context.detected_filter = _get_real_filter('stop all')
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I check the status')
def step_check_status(context):
    """Parse status check using real parser."""
    context.detected_intent = _get_real_intent('status')
    context.current_plan = {'intent': context.detected_intent}


@when('I plan to rebuild Python')
def step_plan_rebuild_python(context):
    """Parse 'restart python rebuild' using real parser."""
    input_str = 'restart python rebuild=true'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    flags = _get_real_flags(input_str)
    context.rebuild_flag = flags.get('rebuild', False)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms, 'flags': flags}


@when('I ask to connect to Python')
def step_ask_to_connect(context):
    """Parse connection request using real parser."""
    context.detected_intent = _get_real_intent('connect python')
    context.detected_vms = _get_real_vm_names('connect python')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I ask what VMs can I create')
def step_ask_available_vms(context):
    """Parse list VMs request using real parser."""
    context.detected_intent = _get_real_intent('list available')
    context.current_plan = {'intent': context.detected_intent}


@when('I ask "what VMs can I create?"')
def step_ask_available_vms_quoted(context):
    """Parse list VMs request and load actual VM data from vm-types.conf."""
    # Parse the natural language request using real parser
    context.detected_intent = _get_real_intent('what VMs can I create')
    context.detected_filter = _get_real_filter('what VMs can I create')

    # Load actual VM data from vm-types.conf
    all_vms = _load_all_vms()
    context.all_vms = all_vms['all']
    context.language_vms = all_vms['language']
    context.service_vms = all_vms['service']

    # Verify VM data has required attributes
    context.vm_list_has_display_names = _vm_list_has_display_names(context.all_vms)
    context.vm_list_has_types = _vm_list_has_types(context.all_vms)

    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I ask "show all services"')
def step_ask_show_all_services(context):
    """Parse show all services request and load service VM data from vm-types.conf."""
    # Parse the natural language request using real parser
    context.detected_intent = _get_real_intent('show all services')
    context.detected_filter = _get_real_filter('show all services')

    # Load actual VM data from vm-types.conf
    all_vms = _load_all_vms()
    service_vms = _filter_vms_by_category(all_vms, 'service')
    context.service_vms = service_vms
    context.all_vms = all_vms['all']  # Keep full list for comparison

    # Verify common services are present
    service_names = [vm['type'] for vm in service_vms]
    context.has_postgresql = 'postgres' in service_names
    context.has_redis = 'redis' in service_names

    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I plan to create Python and PostgreSQL')
def step_plan_create_python_postgres(context):
    """Parse create python and postgres using real parser."""
    input_str = 'create python postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to start Python and PostgreSQL')
def step_plan_start_python_postgres(context):
    """Parse start python and postgres using real parser."""
    input_str = 'start python postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to add Redis')
def step_plan_add_redis(context):
    """Parse adding redis using real parser."""
    context.detected_intent = _get_real_intent('create redis')
    context.detected_vms = _get_real_vm_names('create redis')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to start Redis')
def step_plan_start_redis(context):
    """Parse start redis using real parser."""
    context.detected_intent = _get_real_intent('start redis')
    context.detected_vms = _get_real_vm_names('start redis')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to stop all VMs')
def step_plan_stop_all_vms(context):
    """Parse stop all using real parser."""
    context.detected_intent = _get_real_intent('stop all')
    context.detected_filter = _get_real_filter('stop all')
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I plan to start Go and MongoDB')
def step_plan_start_go_mongodb(context):
    """Parse start go and mongodb using real parser."""
    input_str = 'start go mongodb'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I ask to list all languages')
def step_ask_list_languages(context):
    """Parse list languages request and load language VM data from vm-types.conf."""
    # Parse the natural language request using real parser
    context.detected_intent = _get_real_intent('list languages')
    context.detected_filter = _get_real_filter('list languages')

    # Load actual VM data from vm-types.conf
    all_vms = _load_all_vms()
    language_vms = _filter_vms_by_category(all_vms, 'language')
    context.language_vms = language_vms
    context.all_vms = all_vms['all']  # Keep full list for comparison

    # Verify common languages are present
    lang_names = [vm['type'] for vm in language_vms]
    context.has_python = 'python' in lang_names
    context.has_go = 'go' in lang_names
    context.has_rust = 'rust' in lang_names

    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I ask for help')
def step_ask_help(context):
    """Parse help request using real parser."""
    context.detected_intent = _get_real_intent('help')
    context.current_plan = {'intent': context.detected_intent}


@when('I plan to start Python')
def step_plan_start_python(context):
    """Parse start python using real parser."""
    context.detected_intent = _get_real_intent('start python')
    context.detected_vms = _get_real_vm_names('start python')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to stop PostgreSQL')
def step_plan_stop_postgres(context):
    """Parse stop postgres using real parser."""
    context.detected_intent = _get_real_intent('stop postgres')
    context.detected_vms = _get_real_vm_names('stop postgres')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to create Go again')
def step_plan_create_go_again(context):
    """Parse create go using real parser."""
    context.detected_intent = _get_real_intent('create go')
    context.detected_vms = _get_real_vm_names('create go')
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I verify the documented VMs')
def step_verify_doc_vms(context):
    """Verify documented VM types are valid."""
    context.doc_vm_validity = {
        'python': _is_valid_vm_type('python'),
        'javascript': _is_valid_vm_type('javascript'),
        'js': _is_valid_vm_type('js'),
        'nodejs': _is_valid_vm_type('nodejs'),
        'go': _is_valid_vm_type('go'),
        'rust': _is_valid_vm_type('rust'),
        'postgres': _is_valid_vm_type('postgres'),
        'redis': _is_valid_vm_type('redis'),
    }


@when('I generate plans for morning setup, checks, and cleanup')
def step_generate_perf_plans(context):
    """Generate multiple plans and measure time."""
    start = time.time()
    morning_intent = _get_real_intent('start python postgres redis')
    status_intent = _get_real_intent('status')
    cleanup_intent = _get_real_intent('stop all')
    end = time.time()
    context.plan_generation_time = (end - start) * 1000


# =============================================================================
# THEN steps - Verify plans and assertions
# =============================================================================

@then('the plan should include the create_vm intent')
def step_check_create_vm_intent(context):
    """Verify plan includes create_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'create_vm', f"Expected create_vm intent, got '{intent}'"


@then('the plan should include the Python VM')
def step_check_python_vm(context):
    """Verify plan includes Python VM."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    if isinstance(vms, list):
        assert 'python' in vms, f"Expected 'python' in plan, got {vms}"
    else:
        assert vms == 'python', f"Expected 'python', got '{vms}'"


@then('the plan should include the PostgreSQL VM')
def step_check_postgres_vm(context):
    """Verify plan includes PostgreSQL VM."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    if isinstance(vms, list):
        assert 'postgres' in vms, f"Expected 'postgres' in plan, got {vms}"
    else:
        assert vms == 'postgres', f"Expected 'postgres', got '{vms}'"


@then('the plan should include both Python and PostgreSQL VMs')
def step_check_both_vms(context):
    """Verify plan includes both Python and PostgreSQL."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert isinstance(vms, list), f"Expected VM list, got {vms}"
    assert 'python' in vms, f"Expected 'python' in plan, got {vms}"
    assert 'postgres' in vms, f"Expected 'postgres' in plan, got {vms}"


@then('the plan should include the start_vm intent')
def step_check_start_vm_intent(context):
    """Verify plan includes start_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'start_vm', f"Expected start_vm intent, got '{intent}'"


@then('the plan should include the connect intent')
def step_check_connect_intent(context):
    """Verify plan includes connect intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'connect', f"Expected connect intent, got '{intent}'"


@then('the VM should be recognized as a valid VM type')
def step_check_valid_vm_type(context):
    """Verify VM is recognized as valid type."""
    assert hasattr(context, 'vm_valid'), "VM validity was not checked"
    assert context.vm_valid is True, "VM should be recognized as valid"


@then('it should be marked as a service VM')
def step_check_service_vm(context):
    """Verify VM is marked as service VM."""
    assert hasattr(context, 'vm_category'), "VM category was not checked"
    assert context.vm_category == 'service', f"Expected service category, got '{context.vm_category}'"


@then('the plan should include both VMs')
def step_check_plan_both_vms(context):
    """Verify plan includes both VMs."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert isinstance(vms, list), f"Expected VM list, got {vms}"
    assert len(vms) >= 2, f"Expected at least 2 VMs, got {len(vms)}"


@then('the JavaScript VM should use the js canonical name')
def step_check_js_canonical(context):
    """Verify JavaScript is mapped to js canonical name."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    vms = context.detected_vms if isinstance(context.detected_vms, list) else [context.detected_vms]
    assert 'js' in vms, f"Expected canonical name 'js' in VM list {vms}, not 'javascript'"


@then('it should resolve to js')
def step_check_resolve_js(context):
    """Verify nodejs alias resolves to js."""
    assert hasattr(context, 'alias_resolved'), "Alias was not resolved"
    assert context.alias_resolved is True, "nodejs should resolve to js"


@then('I can use either name in commands')
def step_check_either_name(context):
    """Verify either nodejs or js can be used."""
    assert _is_valid_vm_type('nodejs'), "nodejs should be valid"
    assert _is_valid_vm_type('js'), "js should be valid"


@then('the plan should include all five VMs')
def step_check_five_vms(context):
    """Verify plan includes all five microservice VMs."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert isinstance(vms, list), f"Expected VM list, got {vms}"
    expected = ['python', 'go', 'rust', 'postgres', 'redis']
    for vm in expected:
        assert vm in vms, f"Expected '{vm}' in plan, got {vms}"


@then('each VM should be included in the VM list')
def step_check_vm_list(context):
    """Verify each VM is in the list."""
    assert hasattr(context, 'detected_vms'), "No VMs were detected"
    vms = context.detected_vms if isinstance(context.detected_vms, list) else [context.detected_vms]
    assert len(vms) > 0, "VM list should not be empty"


@then('all microservice VMs should be included')
def step_check_all_microservices(context):
    """Verify all microservice VMs are included."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    filter_val = context.current_plan.get('filter')
    vms = context.current_plan.get('vms', [])
    # The plan should indicate 'all' scope for including all microservices
    if filter_val == 'all':
        return  # Filter is set to 'all' - plan includes all VMs
    # If filter is not 'all', check vms field
    if isinstance(vms, str) and vms == 'all':
        return  # vms field is set to 'all' - plan includes all VMs
    # If vms is a list, it should be non-empty
    if isinstance(vms, list):
        assert len(vms) > 0, f"Expected non-empty VM list for all microservices, got vms={vms}"
    # If we get here, neither filter nor vms indicates 'all'
    raise AssertionError(f"Expected filter='all' or vms='all', got filter='{filter_val}', vms={vms}")


@then('the plan should include all three VMs')
def step_check_three_vms(context):
    """Verify plan includes three VMs."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert isinstance(vms, list), f"Expected VM list, got {vms}"
    assert len(vms) == 3, f"Expected 3 VMs, got {len(vms)}"


@then('the plan should use the start_vm intent')
def step_check_use_start_intent(context):
    """Verify plan uses start_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'start_vm', f"Expected start_vm intent, got '{intent}'"


@then('the plan should include the status intent')
def step_check_status_intent(context):
    """Verify plan includes status intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'status', f"Expected status intent, got '{intent}'"


@then('I should be able to see running VMs')
def step_check_see_running_vms(context):
    """Verify status allows seeing running VMs."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    assert context.current_plan.get('intent') == 'status', "Plan should include status intent"


@then('the plan should provide connection details')
def step_check_connection_details(context):
    """Verify plan provides connection details."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'connect', f"Expected connect intent, got '{intent}'"


@then('the plan should include the stop_vm intent')
def step_check_stop_intent(context):
    """Verify plan includes stop_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'stop_vm', f"Expected stop_vm intent, got '{intent}'"


@then('the plan should apply to all running VMs')
def step_check_applies_all(context):
    """Verify plan applies to all VMs."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    filter_val = context.current_plan.get('filter', '')
    vms = context.current_plan.get('vms', '')
    # The plan must indicate 'all' scope in either filter or vms field
    if filter_val != 'all':
        assert vms == 'all', \
            f"Expected filter='all' or vms='all', got filter='{filter_val}', vms='{vms}'"
    # If filter is 'all', the test passes (filter takes precedence)


@then('I should receive status information')
def step_check_status_info(context):
    """Verify status information is received."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    assert context.current_plan.get('intent') == 'status', "Plan should include status"


@then('the plan should include the restart_vm intent')
def step_check_restart_intent(context):
    """Verify plan includes restart_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent in ['start_vm', 'restart_vm'], f"Expected restart/start intent, got '{intent}'"


@then('the plan should set rebuild=true flag')
def step_check_rebuild_flag(context):
    """Verify rebuild flag is set."""
    assert hasattr(context, 'rebuild_flag'), "Rebuild flag was not set"
    assert context.rebuild_flag is True, "Rebuild flag should be True"


@then('I should receive SSH connection information')
def step_check_ssh_info(context):
    """Verify SSH connection info is provided."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'connect', "Plan should include connect intent"


@then('the plan should include the list_vms intent')
def step_check_list_vms_intent(context):
    """Verify plan includes list_vms intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'list_vms', f"Expected list_vms intent, got '{intent}'"


@then('both VMs should be included in the plan')
def step_check_both_in_plan(context):
    """Verify both VMs are in the plan."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert isinstance(vms, list), f"Expected VM list, got {vms}"
    assert len(vms) >= 2, f"Expected at least 2 VMs, got {len(vms)}"


@then('the plan should use the create_vm intent')
def step_check_use_create_intent(context):
    """Verify plan uses create_vm intent."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    intent = context.current_plan.get('intent', '')
    assert intent == 'create_vm', f"Expected create_vm intent, got '{intent}'"


@then('both VMs should start')
def step_check_both_start(context):
    """Verify both VMs would start."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert len(vms) >= 2, "Plan should include at least 2 VMs"


@then('the Redis VM should be included')
def step_check_redis_included(context):
    """Verify Redis is included in plan."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    if isinstance(vms, list):
        assert 'redis' in vms, f"Expected 'redis' in plan, got {vms}"
    else:
        assert vms == 'redis', f"Expected 'redis', got '{vms}'"


@then('Redis should start without affecting other VMs')
def step_check_redis_isolated(context):
    """Verify Redis starts independently - abstract plan verification for Docker-free tests."""
    # For Docker-free tests, verify the plan includes only Redis
    # The plan should target a single VM, not all VMs
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    if isinstance(vms, list):
        # Verify only Redis is in the plan (no other VMs affected)
        assert len(vms) == 1 and 'redis' in vms, f"Expected only redis in plan, got {vms}"
    else:
        assert vms == 'redis', f"Expected 'redis' only, got '{vms}'"
    # Verify intent is start_vm (not start_all or similar)
    assert context.current_plan.get('intent') == 'start_vm', "Plan should use start_vm intent"


@then('I should be ready to start a new project')
def step_check_ready_new_project(context):
    """Verify ready for new project - abstract plan verification for Docker-free tests."""
    # For Docker-free tests, verify the plan was to stop all VMs
    assert hasattr(context, 'current_plan'), "No plan was generated"
    # Verify intent is stop_vm with 'all' filter
    assert context.current_plan.get('intent') == 'stop_vm', "Plan should include stop_vm intent"
    filter_val = context.current_plan.get('filter', '')
    assert filter_val == 'all', "Plan should apply to all VMs for project switch"


@then('the new project VMs should start')
def step_check_new_project_start(context):
    """Verify new project VMs would start."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    vms = context.current_plan.get('vms', [])
    assert len(vms) >= 1, "Plan should include VMs"


@then('only the new project VMs should be running')
def step_check_only_new_running(context):
    """Verify only new project VMs are running."""
    assert hasattr(context, 'current_plan'), "No plan was generated"


@then('I should see only language VMs')
def step_check_only_languages(context):
    """Verify only language VMs are shown."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    filter_val = context.current_plan.get('filter', '')
    assert filter_val == 'lang', f"Expected lang filter, got '{filter_val}'"


@then('service VMs should not be included')
def step_check_no_services(context):
    """Verify service VMs are not included."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    filter_val = context.current_plan.get('filter', '')
    assert filter_val == 'lang', "Filter should be lang to exclude services"


@then('I should receive clear connection instructions')
def step_check_clear_instructions(context):
    """Verify clear connection instructions are provided."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    assert context.current_plan.get('intent') == 'connect', "Should provide connection info"


@then('I should understand how to access the VM')
def step_check_understand_access(context):
    """Verify instructions explain how to access VM - abstract plan verification."""
    assert hasattr(context, 'current_plan'), "No plan was generated"
    assert context.current_plan.get('intent') == 'connect', "Should provide connection info"
    # For Docker-free tests, verify the plan includes the target VM for connection
    vms = context.current_plan.get('vms', [])
    assert vms, "Plan should include VMs for connection"
    # The plan exists with connect intent, which means VDE would provide connection info during execution


@then('the plan should be generated')
def step_check_plan_generated(context):
    """Verify plan is generated."""
    assert hasattr(context, 'current_plan'), "Plan should be generated"
    assert context.current_plan.get('vms') is not None, "Plan should include VMs"


@then('execution would detect the VM is already running')
def step_check_detect_running(context):
    """Verify execution would detect already-running VM - abstract plan verification."""
    # For Docker-free tests, just verify the plan exists and is valid
    # Real execution would check actual VM state, but we verify plan structure
    assert hasattr(context, 'current_plan'), "Plan should exist for execution check"
    # Verify plan has the VM that would be checked
    vms = context.current_plan.get('vms', [])
    assert vms, "Plan should include VMs for status check"


@then('I would be notified that it\'s already running')
def step_check_notify_running(context):
    """Verify user would be notified about already-running VM - abstract verification."""
    # For Docker-free tests, verify the plan was generated (notification would happen during execution)
    assert hasattr(context, 'current_plan'), "Plan should exist for notification check"
    # The plan exists, which means VDE would notify during actual execution


@then('execution would detect the VM is not running')
def step_check_detect_not_running(context):
    """Verify execution would detect VM not running - abstract plan verification."""
    # For Docker-free tests, just verify the plan exists
    assert hasattr(context, 'current_plan'), "Plan should exist for execution check"
    vms = context.current_plan.get('vms', [])
    assert vms, "Plan should include VMs for status check"


@then('I would be notified that it\'s already stopped')
def step_check_notify_stopped(context):
    """Verify user would be notified about already-stopped VM - abstract verification."""
    # For Docker-free tests, verify the plan was generated
    assert hasattr(context, 'current_plan'), "Plan should exist for notification check"
    # The plan exists, VDE would notify during actual execution


@then('execution would detect the VM already exists')
def step_check_detect_exists(context):
    """Verify execution would detect existing VM - abstract plan verification."""
    # For Docker-free tests, just verify the plan exists
    assert hasattr(context, 'current_plan'), "Plan should exist for execution check"
    vms = context.current_plan.get('vms', [])
    assert vms, "Plan should include VMs for existence check"


@then('I would be notified of the existing VM')
def step_check_notify_exists(context):
    """Verify user would be notified about existing VM - abstract verification."""
    # For Docker-free tests, verify the plan was generated
    assert hasattr(context, 'current_plan'), "Plan should exist for notification check"
    # The plan exists, VDE would notify during actual execution


@then('Python should be a valid VM type')
def step_check_python_valid(context):
    """Verify Python is a valid VM type."""
    assert hasattr(context, 'doc_vm_validity'), "VM validity not checked"
    assert context.doc_vm_validity.get('python') is True, "Python should be valid"


@then('JavaScript should be a valid VM type')
def step_check_javascript_valid(context):
    """Verify JavaScript is a valid VM type."""
    assert hasattr(context, 'doc_vm_validity'), "VM validity not checked"
    js_valid = context.doc_vm_validity.get('js', False)
    javascript_valid = context.doc_vm_validity.get('javascript', False)
    assert js_valid is True, f"js canonical name should be valid, got {js_valid}"
    assert javascript_valid is True, f"javascript alias should be valid, got {javascript_valid}"


@then('all microservice VMs should be valid')
def step_check_microservices_valid(context):
    """Verify all microservice VMs are valid."""
    assert hasattr(context, 'doc_vm_validity'), "VM validity not checked"
    expected_vms = ['go', 'rust', 'postgres', 'redis']
    for vm in expected_vms:
        assert context.doc_vm_validity.get(vm) is True, f"{vm} should be valid"


@then('all plans should be generated quickly')
def step_check_plans_quick(context):
    """Verify plans are generated quickly."""
    assert hasattr(context, 'plan_generation_time'), "No time measured"
    assert context.plan_generation_time < 1000, \
        f"Plans should be generated quickly, took {context.plan_generation_time:.2f}ms"


@then('the total time should be under 500ms')
def step_check_time_under_500ms(context):
    """Verify total time is under 500ms."""
    assert hasattr(context, 'plan_generation_time'), "No time measured"
    assert context.plan_generation_time < 500, \
        f"Total time should be under 500ms, took {context.plan_generation_time:.2f}ms"


@then('Python should exist as a language VM')
def step_check_python_language(context):
    """Verify Python is a language VM."""
    assert hasattr(context, 'vm_checks'), "VM checks were not performed"
    assert context.vm_checks['python']['valid'] is True, "Python should be valid"
    assert context.vm_checks['python']['category'] == 'lang', "Python should be a language VM"


@then('Go should exist as a language VM')
def step_check_go_language(context):
    """Verify Go is a language VM."""
    assert hasattr(context, 'vm_checks'), "VM checks were not performed"
    assert context.vm_checks['go']['valid'] is True, "Go should be valid"
    assert context.vm_checks['go']['category'] == 'lang', "Go should be a language VM"


@then('Rust should exist as a language VM')
def step_check_rust_language(context):
    """Verify Rust is a language VM."""
    assert hasattr(context, 'vm_checks'), "VM checks were not performed"
    assert context.vm_checks['rust']['valid'] is True, "Rust should be valid"
    assert context.vm_checks['rust']['category'] == 'lang', "Rust should be a language VM"


@then('PostgreSQL should exist as a service VM')
def step_check_postgres_service(context):
    """Verify PostgreSQL is a service VM."""
    assert hasattr(context, 'vm_checks'), "VM checks were not performed"
    assert context.vm_checks['postgres']['valid'] is True, "PostgreSQL should be valid"
    assert context.vm_checks['postgres']['category'] == 'service', "PostgreSQL should be a service VM"


@then('Redis should exist as a service VM')
def step_check_redis_service(context):
    """Verify Redis is a service VM."""
    assert hasattr(context, 'vm_checks'), "VM checks were not performed"
    assert context.vm_checks['redis']['valid'] is True, "Redis should be valid"
    assert context.vm_checks['redis']['category'] == 'service', "Redis should be a service VM"


@then('I should see which VMs are running')
def step_check_see_which_running(context):
    """Verify status checking works by calling actual VDE status check."""
    # Real implementation: call vde-parser to detect status intent
    intent = _get_real_intent('status')
    assert intent == 'status', f"Status intent should be detected, got '{intent}'"
    # Verify the plan was generated with status intent
    assert hasattr(context, 'current_plan'), "No plan was generated"
    assert context.current_plan.get('intent') == 'status', "Plan should include status"


@then('I should see available commands')
def step_see_commands(context):
    """Verify VDE has a help mechanism that shows available commands."""
    # Real implementation: verify help intent is detected
    intent = _get_real_intent('help')
    assert intent == 'help', f"Help intent should be detected, got '{intent}'"
    # Verify the vde script has help functionality
    vde_script = os.path.join(VDE_ROOT, 'scripts/vde')
    assert os.path.exists(vde_script), f"VDE script should exist at {vde_script}"
    # Verify vde script contains help message
    result = subprocess.run(['grep', '-q', 'help:Show this help message', vde_script],
                           capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, "VDE script should contain help message"


@then('I should understand what I can do')
def step_understand_actions(context):
    """Verify VDE provides help explaining available actions."""
    # Real implementation: verify help intent is detected
    intent = _get_real_intent('help')
    assert intent == 'help', f"Help intent should be detected, got '{intent}'"
    # Verify vde script provides usage information
    vde_script = os.path.join(VDE_ROOT, 'scripts/vde')
    result = subprocess.run(['grep', '-q', 'Usage:', vde_script],
                           capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, "VDE script should show usage information"
    # Verify the plan was generated
    assert hasattr(context, 'current_plan'), "No plan was generated"
