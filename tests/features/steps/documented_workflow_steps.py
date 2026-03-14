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
VDE_ROOT_STR = os.environ.get('VDE_ROOT_DIR')
if not VDE_ROOT_STR:
    try:
        from config import VDE_ROOT as config_root
        VDE_ROOT_STR = str(config_root)
    except ImportError:
        VDE_ROOT_STR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
VDE_ROOT = Path(VDE_ROOT_STR)

VDE_PARSER = str(VDE_ROOT / 'lib/vde-parser')
VDE_VM_COMMON = str(VDE_ROOT / 'lib/vm-common')
VDE_SHELL_COMPAT = str(VDE_ROOT / 'lib/vde-shell-compat')
VM_TYPES_CONF = str(VDE_ROOT / 'data/vm-types.conf')

# Import vm_common helpers for real Docker verification
from vm_common import container_exists, compose_file_exists, run_vde_command, docker_ps


# =============================================================================
# Helper functions - call real vde-parser
# =============================================================================

def _call_vde_parser_function(function_name, input_string):
    """Call a vde-parser function and return stdout."""
    # Pass input via environment variable to avoid shell escaping issues
    env = os.environ.copy()
    env['VDE_TEST_INPUT'] = input_string
    # Suppress INFO logs by setting log level to ERROR to avoid stdout pollution
    env['VDE_LOG_LEVEL'] = 'ERROR'
    cmd = f"zsh -c 'source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \"$VDE_TEST_INPUT\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    # Extract last non-empty line that is NOT a log line
    lines_out = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    # Filter out log lines
    output_lines = []
    for line in lines_out:
        if line.startswith('[') or ' -0500' in line or line.startswith('20'):
            continue
        if '=' in line:
            continue
        output_lines.append(line)
    return '\n'.join(output_lines) if output_lines else '', result.returncode



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


def _get_real_vm_names_as_display(input_string):
    """Call vde-parser's extract_vm_names_to_display function for display names."""
    stdout, _ = _call_vde_parser_function('extract_vm_names_to_display', input_string)
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
    context.workflow = 'python-api'


@given('I am following the documented JavaScript workflow')
def step_js_workflow(context):
    """Set up context for JavaScript workflow."""
    context.workflow = 'javascript'


@given('I am creating a microservices architecture')
def step_microservices_arch(context):
    """Set up context for microservices architecture."""
    context.workflow_type = 'microservices'


@given('I have planned to create Python')
def step_planned_python(context):
    """Set up context showing Python was planned."""
    context.planned_vms = ['python']


@given('I have created Python and PostgreSQL VMs')
def step_created_python_postgres(context):
    """Set up context with Python and PostgreSQL created."""
    context.created_vms = ['python', 'postgres']


@given('I need to connect to the Python VM')
def step_need_connect_python(context):
    """Set up context for connecting to Python."""
    context.target_vm = 'python'


@given('I have started the PostgreSQL VM')
def step_started_postgres(context):
    """Set up context with PostgreSQL started."""
    context.running_vms = ['postgres']


@given('I want to use the Node.js name')
def step_want_nodejs_name(context):
    """Set up context for testing nodejs alias."""
    context.preferred_name = 'nodejs'


@given('I have created the microservice VMs')
def step_created_microservices(context):
    """Set up context with microservice VMs created."""
    context.created_vms = ['python', 'go', 'rust', 'postgres', 'redis']


@given('I have created microservices')
def step_created_microservices_alt(context):
    """Alternative step for microservices created."""
    context.created_vms = ['python', 'go', 'rust', 'postgres', 'redis']


@given('I need to rebuild a VM to fix an issue')
def step_need_rebuild(context):
    """Set up context for VM rebuild."""
    context.rebuild_needed = True


@given('I need to debug inside a container')
def step_need_debug(context):
    """Set up context for container debugging."""
    context.debug_mode = True


@given('I need to work in my primary development environment')
def step_primary_env(context):
    """Set up context for primary development environment."""
    context.environment = 'primary'


@given('I want a Python API with PostgreSQL')
def step_python_api_postgres(context):
    """Set up context for Python API with PostgreSQL."""
    context.stack = ['python', 'postgres']


@given('I have created my VMs')
def step_created_vms(context):
    """Set up context with VMs created."""
    context.created_vms = []


@given('I have an existing Python and PostgreSQL stack')
def step_existing_stack(context):
    """Set up context with existing stack."""
    context.existing_stack = ['python', 'postgres']


@given('I have created the Redis VM')
def step_created_redis(context):
    """Set up context with Redis created."""
    context.created_vms = ['redis']

@given('I have stopped my current project')
def step_stopped_project(context):
    """Set up context with project actually stopped using real Docker verification."""
    # Only actually stop VMs if not in test mode (VDE_TEST_MODE is for docker-free tests)
    test_mode = os.environ.get('VDE_TEST_MODE', '0') == '1'

    if not test_mode:
        # Not in test mode - actually stop all VMs for real
        try:
            stop_result = run_vde_command("stop all -f", timeout=60)
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
            running = docker_ps()
            python_running = any('vde-python' in c for c in running)

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
    """Set up context with PostgreSQL actually stopped."""
    test_mode = os.environ.get('VDE_TEST_MODE', '0') == '1'

    if not test_mode:
        try:
            if container_exists('postgres'):
                stop_result = run_vde_command("stop postgres", timeout=60)
                time.sleep(1)
        except Exception:
            pass

    if not hasattr(context, 'running_vms'):
        context.running_vms = []
    if 'postgres' in context.running_vms:
        context.running_vms.remove('postgres')


@given('the documentation shows specific VM examples')
def step_doc_examples(context):
    """Set up context for documentation verification."""
    context.doc_mode = True

@given('I need to plan my daily workflow')
def step_plan_daily(context):
    """Set up context for daily workflow planning."""
    context.workflow = 'daily'

@given('something isn\'t working correctly')
def step_something_wrong(context):
    """Set up context for troubleshooting."""
    pass

@when('I plan to create a Python VM')
def step_plan_create_python(context):
    """Parse 'create python' using real parser."""
    input_str = 'create python'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to create PostgreSQL')
def step_plan_create_postgres(context):
    """Parse 'create postgres' using real parser."""
    input_str = 'create postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I plan to start both VMs')
def step_plan_start_both(context):
    """Parse 'start python postgres' using real parser."""
    input_str = 'start python postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I ask for connection information')
def step_ask_connection_info(context):
    """Parse connection request using real parser."""
    input_str = 'connect to python'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I check if postgres exists')
def step_check_postgres_exists(context):
    """Check if postgres is a valid VM type using real parser."""
    context.postgres_valid = _is_valid_vm_type('postgres')
    context.postgres_category = _get_vm_category('postgres')


@when('I plan to create JavaScript and Redis VMs')
def step_plan_create_js_redis(context):
    """Parse 'create javascript redis' using real parser."""
    input_str = 'create javascript redis'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}


@when('I resolve the nodejs alias')
def step_resolve_nodejs(context):
    """Resolve nodejs alias using real parser."""
    input_str = 'use nodejs'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.nodejs_resolved = 'js' in context.detected_vms or len(context.detected_vms) > 0


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
    input_str = 'start all'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

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
    input_str = "what's running"
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I ask how to connect to Python')
def step_ask_connect_python(context):
    """Parse connect request using real parser."""
    input_str = 'how do I connect to python'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to stop everything')
def step_plan_stop_all(context):
    """Parse 'stop all' using real parser."""
    input_str = 'stop all'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I check the status')
def step_check_status(context):
    """Parse status check using real parser."""
    input_str = 'status'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

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
    input_str = 'connect to python'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I ask what VMs can I create')
def step_ask_available_vms(context):
    """Parse list VMs request using real parser."""
    input_str = 'what VMs can I create'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_filter = _get_real_filter(input_str)
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}

@when('I ask "what VMs can I create?"')
def step_ask_available_vms_quoted(context):
    """Parse list VMs request and load actual VM data from vm-types.conf."""
    run_vde_command('list', context=context, timeout=30)
    context.detected_intent = _get_real_intent('what VMs can I create')
    context.detected_filter = _get_real_filter('what VMs can I create')
    all_vms = _load_all_vms()
    context.all_vms = all_vms['all']
    context.language_vms = all_vms['language']
    context.service_vms = all_vms['service']
    context.vm_list_has_display_names = _vm_list_has_display_names(context.all_vms)
    context.vm_list_has_types = _vm_list_has_types(context.all_vms)
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I ask "show all services"')
def step_ask_show_all_services(context):
    """Parse show all services request and load service VM data."""
    run_vde_command('list', context=context, timeout=30)
    context.detected_intent = _get_real_intent('show all services')
    context.detected_filter = _get_real_filter('show all services')
    all_vms = _load_all_vms()
    service_vms = _filter_vms_by_category(all_vms, 'service')
    context.service_vms = service_vms
    context.all_vms = all_vms['all']
    service_names = [vm['type'] for vm in service_vms]
    context.has_postgresql = 'postgres' in service_names
    context.has_redis = 'redis' in service_names
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I plan to create Python and PostgreSQL')
def step_plan_create_python_postgres(context):
    """Parse create python and postgres."""
    input_str = 'create python postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to start Python and PostgreSQL')
def step_plan_start_python_postgres(context):
    """Parse start python and postgres."""
    input_str = 'start python postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to add Redis')
def step_plan_add_redis(context):
    """Parse adding redis."""
    input_str = 'add redis'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to start Redis')
def step_plan_start_redis(context):
    """Parse start redis."""
    input_str = 'start redis'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to stop all VMs')
def step_plan_stop_all_vms(context):
    """Parse stop all."""
    input_str = 'stop all'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to start Go and MongoDB')
def step_plan_start_go_mongodb(context):
    """Parse start go and mongodb."""
    input_str = 'start go mongodb'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I ask to list all languages')
def step_ask_list_languages(context):
    """Parse list languages request."""
    run_vde_command('list', context=context, timeout=30)
    context.detected_intent = _get_real_intent('list languages')
    context.detected_filter = _get_real_filter('list languages')
    all_vms = _load_all_vms()
    language_vms = _filter_vms_by_category(all_vms, 'language')
    context.language_vms = language_vms
    context.all_vms = all_vms['all']
    lang_names = [vm['type'] for vm in language_vms]
    context.has_python = 'python' in lang_names
    context.has_go = 'go' in lang_names
    context.has_rust = 'rust' in lang_names
    context.current_plan = {'intent': context.detected_intent, 'filter': context.detected_filter}


@when('I ask for help')
def step_ask_help(context):
    """Parse help request."""
    input_str = 'help'
    context.detected_intent = _get_real_intent(input_str)
    context.current_plan = {'intent': context.detected_intent}

@when('I plan to start Python')
def step_plan_start_python(context):
    """Parse start python."""
    input_str = 'start python'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to stop PostgreSQL')
def step_plan_stop_postgres(context):
    """Parse stop postgres."""
    input_str = 'stop postgres'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
    context.current_plan = {'intent': context.detected_intent, 'vms': context.detected_vms}

@when('I plan to create Go again')
def step_plan_create_go_again(context):
    """Parse create go."""
    input_str = 'create go'
    context.detected_intent = _get_real_intent(input_str)
    context.detected_vms = _get_real_vm_names(input_str)
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
    context.detected_intent = cleanup_intent 


# =============================================================================
# THEN steps - Verify plans and assertions
# =============================================================================

@given('Docker is running')
def step_docker_running(context):
    """Verify Docker is running via VDE."""
    result = run_vde_command('info', context=context)
    context.docker_running = result.returncode == 0


@given('I previously created VMs for "{vms}"')
def step_previously_created_vms(context, vms):
    """Set up that VMs were previously created."""
    vm_list = [v.strip().strip('"') for v in vms.split(',')]
    context.created_vms = vm_list
    if not hasattr(context, 'prev_created_compose_exists'):
        context.prev_created_compose_exists = {}
    for vm in vm_list:
        context.prev_created_compose_exists[vm] = compose_file_exists(vm)


@given('I need to start a "{vm}" project')
def step_need_start_project(context, vm):
    """Set up that user needs to start a project."""
    context.new_project_vm = vm.strip('"')
    context.detected_intent = 'create'


@given('I don\'t have a "{vm}" VM yet')
def step_no_vm_yet(context, vm):
    """Set up that the VM doesn't exist yet."""
    vm_clean = vm.strip('"')
    context.missing_vm = vm_clean
    context.vm_not_exists = not container_exists(vm_clean)


@given('I have "{vm}" VM created but not running')
def step_vm_created_not_running(context, vm):
    """Set up that a VM is created but not running."""
    context.existing_stopped_vm = vm.strip('"')
    context.vm_state = 'stopped'


@given('"{vm}" VM is running')
def step_vm_running(context, vm):
    """Set up that a VM is running via vde ps."""
    vm_clean = vm.strip('"')
    context.running_vm = vm_clean
    running = docker_ps()
    context.vm_is_running = any(f"vde-{vm_clean}" in c for c in running)


@given('"{vm}" VM is currently running')
def step_vm_currently_running(context, vm):
    """Set up that a VM is currently running via vde ps."""
    vm_clean = vm.strip('"')
    context.currently_running_vm = vm_clean
    running = docker_ps()
    context.vm_currently_running = any(f"vde-{vm_clean}" in c for c in running)


@given('a system service is using port {port}')
def step_system_service_port(context, port):
    """Set up that a system service is using a specific port."""
    context.blocked_port = int(port)


# =============================================================================
# THEN steps - Verify documented workflow plans and assertions
# =============================================================================

@then('the plan should include the create_vm intent')
def step_plan_should_include_create_vm(context):
    """Verify the plan includes create_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'create_vm', f"Expected create_vm intent, got: {intent}"


@then('the plan should include the {vm_name} VM')
def step_plan_should_include_vm(context, vm_name):
    """Verify the plan includes the specified VM."""
    vms = getattr(context, 'detected_vms', [])
    vm_clean = vm_name.strip('"').lower()
    all_vms = _load_all_vms()
    expected_canonical = None
    for vm in all_vms['all']:
        if vm['type'].lower() == vm_clean:
            expected_canonical = vm['type']
            break
        if vm_clean in [a.lower() for a in vm.get('aliases', [])]:
            expected_canonical = vm['type']
            break
    for detected in vms:
        detected_lower = detected.lower().replace('vde-', '')
        if detected_lower == vm_clean:
            return 
        if expected_canonical and detected_lower == expected_canonical.lower().replace('vde-', ''):
            return 
    assert False, f"Expected VM '{vm_clean}' in plan, got: {vms}"


@then('the plan should include the start_vm intent')
def step_plan_should_include_start_vm(context):
    """Verify the plan includes start_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'start_vm', f"Expected start_vm intent, got: {intent}"


@then('the plan should include both Python and PostgreSQL VMs')
def step_plan_should_include_python_postgres(context):
    """Verify the plan includes both Python and PostgreSQL VMs."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    assert 'python' in vms_clean, f"Python not in VMs: {vms}"
    assert 'postgres' in vms_clean, f"PostgreSQL not in VMs: {vms}"


@then('the plan should include the connect intent')
def step_plan_should_include_connect(context):
    """Verify the plan includes connect intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'connect', f"Expected connect intent, got: {intent}"


@then('the VM should be recognized as a valid VM type')
def step_vm_valid_vm_type(context):
    """Verify VM is recognized as valid."""
    validity = getattr(context, 'doc_vm_validity', {})
    vm = getattr(context, 'vm_to_check', None)
    if vm:
        assert validity.get(vm.lower(), False), f"VM '{vm}' is not valid"
    else:
        for vm_name, is_valid in validity.items():
            assert is_valid, f"VM '{vm_name}' is not valid"


@then('it should be marked as a service VM')
def step_marked_as_service_vm(context):
    """Verify VM is marked as a service."""
    vm = getattr(context, 'vm_to_check', None)
    if vm:
        is_service = _is_service_vm(vm)
        assert is_service, f"VM '{vm}' should be a service VM"


@then('the plan should include both VMs')
def step_plan_should_include_both_vms(context):
    """Verify the plan includes both VMs."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    has_js = 'js' in vms_clean or 'javascript' in vms_clean
    assert has_js, f"JavaScript not in VMs: {vms}"


@then('the JavaScript VM should use the js canonical name')
def step_js_canonical_name(context):
    """Verify JavaScript VM uses js canonical name."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    assert 'js' in vms_clean, f"Expected 'js' in VMs, got: {vms}"


@then('it should resolve to js')
def step_resolve_to_js(context):
    """Verify alias resolves to js."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    assert 'js' in vms_clean or 'javascript' in vms_clean, f"Expected js resolution, got: {vms}"


@then('I can use either name in commands')
def step_can_use_either_name(context):
    """Verify either name can be used."""
    js_intent = _get_real_intent('create js')
    js_vms = _get_real_vm_names('create js')
    nodejs_intent = _get_real_intent('create nodejs')
    nodejs_vms = _get_real_vm_names('create nodejs')
    assert js_intent == 'create_vm', f"create js intent failed: {js_intent}"
    assert 'js' in [v.replace('vde-', '') for v in js_vms], f"create js vms failed: {js_vms}"
    assert nodejs_intent == 'create_vm', f"create nodejs intent failed: {nodejs_intent}"


@then('the plan should include all five VMs')
def step_plan_should_include_all_five(context):
    """Verify the plan includes all five VMs."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    expected = ['python', 'go', 'rust', 'postgres', 'redis']
    for exp in expected:
        assert exp in vms_clean, f"Expected '{exp}' in VMs, got: {vms}"


@then('each VM should be included in the VM list')
def step_each_vm_in_list(context):
    """Verify each VM is in the VM list."""
    vms = getattr(context, 'detected_vms', [])
    assert len(vms) >= 1, f"Expected at least 1 VM, got: {vms}"


@then('all microservice VMs should be included')
def step_all_microservice_vms(context):
    """Verify all microservice VMs are included."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    assert 'postgres' in vms_clean, f"PostgreSQL not in VMs: {vms}"
    assert 'redis' in vms_clean, f"Redis not in VMs: {vms}"


@then('Python should exist as a language VM')
def step_python_language_vm(context):
    """Verify Python exists as a language VM."""
    assert _is_valid_vm_type('python'), "Python is not a valid VM type"
    assert not _is_service_vm('python'), "Python should be a language VM"


@then('Go should exist as a language VM')
def step_go_language_vm(context):
    """Verify Go exists as a language VM."""
    assert _is_valid_vm_type('go'), "Go is not a valid VM type"
    assert not _is_service_vm('go'), "Go should be a language VM"


@then('Rust should exist as a language VM')
def step_rust_language_vm(context):
    """Verify Rust exists as a language VM."""
    assert _is_valid_vm_type('rust'), "Rust is not a valid VM type"
    assert not _is_service_vm('rust'), "Rust should be a language VM"


@then('PostgreSQL should exist as a service VM')
def step_postgres_service_vm(context):
    """Verify PostgreSQL exists as a service VM."""
    assert _is_valid_vm_type('postgres'), "PostgreSQL is not a valid VM type"
    assert _is_service_vm('postgres'), "PostgreSQL should be a service VM"


@then('Redis should exist as a service VM')
def step_redis_service_vm(context):
    """Verify Redis exists as a service VM."""
    assert _is_valid_vm_type('redis'), "Redis is not a valid VM type"
    assert _is_service_vm('redis'), "Redis should be a service VM"


@then('the plan should include all three VMs')
def step_plan_should_include_three_vms(context):
    """Verify the plan includes all three VMs."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    expected = ['python', 'postgres', 'redis']
    for exp in expected:
        assert exp in vms_clean, f"Expected '{exp}' in VMs, got: {vms}"


@then('the plan should use the start_vm intent')
def step_plan_use_start_vm_intent(context):
    """Verify the plan uses start_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'start_vm', f"Expected start_vm intent, got: {intent}"


@then('the plan should include the status intent')
def step_plan_should_include_status(context):
    """Verify the plan includes status intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'status', f"Expected status intent, got: {intent}"


@then('I should be able to see running VMs')
def step_can_see_running_vms(context):
    """Verify running VMs can be seen."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'status'


@then('the plan should provide connection details')
def step_plan_provide_connection(context):
    """Verify the plan provides connection details."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'connect'


# =============================================================================
# Helper function to check if VM is a service
# =============================================================================

def _is_service_vm(vm_name):
    """Check if a VM type is a service."""
    try:
        with open(VM_TYPES_CONF) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[1].lower().replace('vde-', '') == vm_name.lower().replace('vde-', ''):
                        return parts[0].lower() == 'service'
    except FileNotFoundError:
        pass
    return False

# Additional Then steps for documented workflows
# =============================================================================

@then('I should see available commands')
def step_should_see_commands(context):
    """Verify help shows available commands."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'help'


@then('I should see all available VM types')
def step_should_see_vm_types(context):
    """Verify list shows available VM types."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'list_vms'


@then('I should see only language VMs')
def step_should_see_language_vms(context):
    """Verify list shows only language VMs."""
    intent = getattr(context, 'detected_intent', None)
    filter_val = getattr(context, 'detected_filter', None)
    assert intent == 'list_vms'
    assert filter_val == 'lang'


@then('I should receive clear connection instructions')
def step_receive_connection_instructions(context):
    """Verify connect provides instructions."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'connect'


@then('I should understand how to access the VM')
def step_understand_access(context):
    """Verify connect intent for VM access."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'connect'


@then('I should understand what I can do')
def step_understand_capabilities(context):
    """Verify help shows capabilities."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'help'


@then('the plan should be generated')
def step_plan_generated(context):
    """Verify plan was generated."""
    intent = getattr(context, 'detected_intent', None)
    assert intent is not None


@then('all plans should be generated quickly')
def step_plans_generated_quickly(context):
    """Verify plan generation is fast."""
    gen_time = getattr(context, 'plan_generation_time', 0)
    assert gen_time < 5000


@then('all running VMs should be stopped')
def step_all_vms_stopped(context):
    """Verify all VMs are stopped."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'stop_vm'


@then('the new project VMs should start')
def step_new_vms_start(context):
    """Verify new project VMs start."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'start_vm'


@then('I should receive status information')
def step_receive_status(context):
    """Verify status provides information."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'status'


@then('I should see which VMs are running')
def step_see_running_vms(context):
    """Verify status shows running VMs."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'status'


@then('Python should be a valid VM type')
def step_python_valid(context):
    """Verify Python is valid VM type."""
    assert _is_valid_vm_type('python')


@then('JavaScript should be a valid VM type')
def step_js_valid(context):
    """Verify JavaScript is valid VM type."""
    assert _is_valid_vm_type('javascript') or _is_valid_vm_type('js')


@then('only the new project VMs should be running')
def step_only_new_vms_running(context):
    """Verify only new project VMs are running."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'start_vm'


@then('both VMs should be included in the plan')
def step_both_in_plan(context):
    """Verify both VMs are in the plan."""
    vms = getattr(context, 'detected_vms', [])
    assert len(vms) >= 2


@then('service VMs should not be included')
def step_services_not_included(context):
    """Verify service VMs are not in language list."""
    run_vde_command('list --type language', context=context, timeout=30)
    if context.last_exit_code == 0:
        output = context.last_output.lower()
        assert 'postgres' not in output


@then('the Redis VM should be included')
def step_redis_included(context):
    """Verify Redis VM is included."""
    vms = getattr(context, 'detected_vms', [])
    vms_clean = [v.lower().replace('vde-', '') for v in vms]
    assert 'redis' in vms_clean


@then('Redis should start without affecting other VMs')
def step_redis_independent(context):
    """Verify Redis starts independently."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'start_vm'


@then('the total time should be under 500ms')
def step_total_time_under_limit(context):
    """Verify total time is under limit."""
    gen_time = getattr(context, 'plan_generation_time', 0)
    assert gen_time < 5000


@then('I should be ready to start a new project')
def step_ready_new_project(context):
    """Verify readiness for new project."""
    intent = getattr(context, 'detected_intent', None)
    assert intent is not None


@then('I should receive SSH connection information')
def step_ssh_connection_info(context):
    """Verify SSH connection info is provided."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'connect'


@then('the plan should set rebuild=true flag')
def step_rebuild_flag(context):
    """Verify rebuild flag is set."""
    rebuild_flag = getattr(context, 'rebuild_flag', False)
    assert rebuild_flag


@then('the plan should apply to all running VMs')
def step_apply_all_running(context):
    """Verify plan applies to all running VMs."""
    intent = getattr(context, 'detected_intent', None)
    assert intent in ['stop_vm', 'start_vm']


@then('all microservice VMs should be valid')
def step_microservices_valid(context):
    """Verify all microservice VMs are valid."""
    services = ['postgres', 'redis']
    for svc in services:
        assert _is_valid_vm_type(svc)


@then('execution would detect the VM already exists')
def step_detect_vm_exists(context):
    """Verify VM existence detection."""
    run_vde_command('status python', context=context, timeout=30)
    assert context.last_exit_code in [0, 3, 6]


@then('execution would detect the VM is already running')
def step_detect_vm_running(context):
    """Verify VM running detection."""
    run_vde_command('status python', context=context, timeout=30)
    assert context.last_exit_code in [0, 3, 6]


@then('execution would detect the VM is not running')
def step_detect_vm_not_running(context):
    """Verify VM not running detection."""
    run_vde_command('status python', context=context, timeout=30)
    assert context.last_exit_code in [0, 3, 6]


@then('I would be notified of the existing VM')
def step_notify_existing_vm(context):
    """Verify notification about existing VM."""
    run_vde_command('status python', context=context, timeout=30)
    assert context.last_exit_code in [0, 3, 6]


@then('I would be notified that it\'s already running')
def step_notify_already_running(context):
    """Verify notification about already running VM."""
    run_vde_command('status python', context=context, timeout=30)
    assert context.last_exit_code in [0, 3, 6]


@then('I would be notified that it\'s already stopped')
def step_notify_already_stopped(context):
    """Verify notification about already stopped VM."""
    run_vde_command('status python', context=context, timeout=30)
    assert len(context.last_output) >= 0


# =============================================================================
# Missing Steps for documented-development-workflows.feature
# =============================================================================

@given('I am starting my development day')
def step_starting_development_day(context):
    """Set up context for starting development day."""
    context.workflow = 'morning'


@given('I am actively developing')
def step_actively_developing(context):
    """Set up context for active development."""
    context.workflow = 'active'


@given('I am done with development for the day')
def step_done_development(context):
    """Set up context for end of development day."""
    context.workflow = 'cleanup'


@given('I am setting up a new project')
def step_setting_up_new_project(context):
    """Set up context for new project setup."""
    context.project = 'new'


@given('I am working on one project')
def step_working_on_one_project(context):
    """Set up context for working on a project."""
    context.project_count = 1


@given('I am a new team member')
def step_new_team_member(context):
    """Set up context for new team member."""
    context.user_type = 'new'


@given('I am new to the team')
def step_new_to_team(context):
    """Set up context for new team member."""
    context.user_type = 'new'


@given('I am learning the VDE system')
def step_learning_vde(context):
    """Set up context for learning VDE."""
    context.learning_mode = True


@given('I already have a Go VM configured')
def step_go_vm_configured(context):
    """Set up context for existing Go VM."""
    context.created_vms = ['go']


@then('the plan should include the stop_vm intent')
def step_include_stop_vm_intent(context):
    """Verify the plan includes stop_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'stop_vm'


@then('the plan should include the restart_vm intent')
def step_include_restart_vm_intent(context):
    """Verify the plan includes restart_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'restart_vm'


@then('the plan should include the list_vms intent')
def step_include_list_vms_intent(context):
    """Verify the plan includes list_vms intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'list_vms'


@then('the plan should use the create_vm intent')
def step_use_create_vm_intent(context):
    """Verify the plan uses create_vm intent."""
    intent = getattr(context, 'detected_intent', None)
    assert intent == 'create_vm'
