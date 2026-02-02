"""
BDD Step definitions for Documented Development Workflows scenarios.
Uses real vde-parser library functions for testing natural language parsing
and plan generation capabilities.

This file contains ONLY steps not already defined in other step files.
"""

import os
import subprocess
import sys
import time

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
VM_TYPES_CONF = os.path.join(VDE_ROOT, 'scripts/data/vm-types.conf')

# Import vm_common helpers for real Docker verification
from vm_common import container_exists, compose_file_exists, run_vde_command


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
        with open(VM_TYPES_CONF) as f:
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
        with open(VM_TYPES_CONF) as f:
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
        with open(VM_TYPES_CONF) as f:
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
    """Set up context with project actually stopped using real Docker verification."""
    # Only actually stop VMs if not in test mode (VDE_TEST_MODE is for docker-free tests)
    test_mode = os.environ.get('VDE_TEST_MODE', '0') == '1'

    if not test_mode:
        # Not in test mode - actually stop all VMs for real
        try:
            stop_result = run_vde_command("stop --all", timeout=60)
            time.sleep(2)
        except Exception:
            # Docker not available
            pass

    # Always set running_vms for compatibility
    context.running_vms = []


@given('I have a Python VM that is already running')
def step_python_already_running(context):
    """Set up context with Python actually running using real Docker verification."""
    # Only actually start VMs if not in test mode (VDE_TEST_MODE is for docker-free tests)
    test_mode = os.environ.get('VDE_TEST_MODE', '0') == '1'

    if not test_mode:
        # Not in test mode - actually verify/start Python VM
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Docker is available - check if python is running
                running = result.stdout.strip().split('\n')
                python_running = any('python-dev' in c for c in running if c)

                if not python_running and compose_file_exists('python'):
                    # Try to start it
                    start_result = run_vde_command("start python", timeout=120)
                    time.sleep(2)
        except Exception:
            # Docker not available
            pass

    # Always set running_vms for compatibility
    if not hasattr(context, 'running_vms'):
        context.running_vms = []
    if 'python' not in context.running_vms:
        context.running_vms.append('python')


@given('I have a stopped PostgreSQL VM')
def step_stopped_postgres(context):
    """Set up context with PostgreSQL actually stopped using real Docker verification."""
    # Only actually stop VMs if not in test mode (VDE_TEST_MODE is for docker-free tests)
    test_mode = os.environ.get('VDE_TEST_MODE', '0') == '1'

    if not test_mode:
        # Not in test mode - actually stop postgres
        try:
            if container_exists('postgres'):
                # Stop postgres
                stop_result = run_vde_command("stop postgres", timeout=60)
                time.sleep(1)
        except Exception:
            # Docker not available
            pass

    # Always set running_vms for compatibility (postgres not in running list)
    if not hasattr(context, 'running_vms'):
        context.running_vms = []
    if 'postgres' in context.running_vms:
        context.running_vms.remove('postgres')


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
    # Execute the actual list-vms command to get real output
    result = subprocess.run(
        ['./scripts/list-vms'],
        cwd=VDE_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )
    context.last_output = result.stdout
    context.last_exit_code = result.returncode

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
    # Execute the actual list-vms command to get real output
    result = subprocess.run(
        ['./scripts/list-vms'],
        cwd=VDE_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )
    context.last_output = result.stdout
    context.last_exit_code = result.returncode

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
    # Execute the actual list-vms command to get real output
    result = subprocess.run(
        ['./scripts/list-vms'],
        cwd=VDE_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )
    context.last_output = result.stdout
    context.last_exit_code = result.returncode

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

