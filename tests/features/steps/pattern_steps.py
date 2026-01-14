"""
Comprehensive catch-all step definitions for VDE BDD tests.
Uses parameterized patterns to handle many similar steps.

NOTE: To avoid AmbiguousStep errors in behave, we use:
1. Specific patterns (not overly-broad parameterized patterns)
2. Patterns with specific parameter types (like {num} for numbers)
3. Avoid patterns that could match specific implementations in other files
"""

from behave import given, when, then
import re

# =============================================================================
# SSH CONFIG STATE PATTERNS (specific ones only)
# =============================================================================

@given('~/.ssh/config exists with blank lines')
def step_ssh_blank_lines(context):
    context.ssh_has_blank_lines = True

@given('~/.ssh/config exists with content')
def step_ssh_has_content(context):
    context.ssh_has_content = True

@given('~/.ssh/config exists with existing host entries')
def step_ssh_existing_entries(context):
    context.ssh_existing_entries = True

@given('~/.ssh/config has comments and custom formatting')
def step_ssh_formatting(context):
    context.ssh_custom_formatting = True

# =============================================================================
# VM STATE PATTERNS (using specific patterns or number-based parameters)
# =============================================================================

@given('"{vm}" VM is created but not running')
def step_vm_created_not_running(context, vm):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add(vm)

@given('I have "{vm}" VM running')
def step_i_have_vm_running(context, vm):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add(vm)

# These use {num} which only matches numbers - less likely to conflict
@given('I have {num} VMs running')
def step_have_n_vms_running(context, num):
    context.num_vms_running = int(num)

@given('I have {num} VMs configured for my project')
def step_n_vms_configured(context, num):
    context.num_vms_configured = int(num)

@given('I have {num} SSH keys loaded in the agent')
def step_n_keys_loaded(context, num):
    context.num_keys_loaded = int(num)

# NOTE: "I have a {vm_type} VM running" conflicts with specific VM implementations
# Specific VM patterns (python, postgres, rust, etc.) are in ssh_docker_steps.py
# For dynamic VM types, we'll need specific implementations

@given('I don\'t have a "{vm}" VM yet')
def step_dont_have_vm(context, vm):
    context.dont_have_vm = vm

# =============================================================================
# CREATION PATTERNS
# =============================================================================

@given('I create multiple VMs')
def step_create_multiple(context):
    context.creating_multiple = True

@when('I create a new VM')
def step_create_new(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('new-vm')

@when('I connect via SSH')
def step_connect_ssh(context):
    context.connected_ssh = True

# NOTE: restart VM and rebuild VM are in ssh_docker_steps.py

# =============================================================================
# STATE PATTERNS
# =============================================================================

@given('Docker is running')
def step_docker_running(context):
    context.docker_running = True

@given('cache file is newer than config file')
def step_cache_newer(context):
    context.cache_newer = True

@given('cache file was created before config file')
def step_cache_older(context):
    context.cache_older = True

@given('an operation fails partway through')
def step_op_fails_partway(context):
    context.op_failed_partway = True

@given('an operation is interrupted')
def step_op_interrupted(context):
    context.op_interrupted = True

@given('any error occurs')
def step_any_error(context):
    context.any_error = True

@given('any VM template is rendered')
def step_template_rendered(context):
    context.template_rendered = True

@given('associative array with key "{key}"')
def step_assoc_key(context, key):
    context.assoc_key = key

@given('associative array with keys "{keys}"')
def step_assoc_keys(context, keys):
    context.assoc_keys = keys.split(', ')

@given('associative array with multiple entries')
def step_assoc_multiple(context):
    context.assoc_multiple = True

@given('file-based associative arrays are in use')
def step_file_assoc(context):
    context.file_based_assoc = True

@given('both "{key1}" and "{key2}" keys exist')
def step_both_keys(context, key1, key2):
    context.keys_exist = [key1, key2]

# =============================================================================
# USER STATE PATTERNS
# =============================================================================

@given('I am a new VDE user')
def step_new_user(context):
    context.is_new_user = True

@given('I am a new team member')
def step_new_team_member(context):
    context.is_new_team_member = True

@given('I am new to the team')
def step_new_to_team(context):
    context.is_new_to_team = True

@given('I am new to VDE')
def step_new_to_vde(context):
    context.is_new_to_vde = True

@given('I am actively developing')
def step_actively_developing(context):
    context.developing = True

@given('I am learning the VDE system')
def step_learning_vde(context):
    context.learning_vde = True

@given('I am connected to a VM')
def step_connected_vm(context):
    context.connected_to_vm = True

@given('I am connected via SSH')
def step_connected_ssh(context):
    context.ssh_connected = True

# NOTE: Pattern-based project creation can conflict - using specific patterns
@given('I am starting my development day')
def step_starting_day(context):
    context.starting_day = True

@given('I am done with development for the day')
def step_done_for_day(context):
    context.done_for_day = True

@given('I am experiencing issues')
def step_experiencing_issues(context):
    context.having_issues = True

# =============================================================================
# ERROR PATTERNS
# =============================================================================

@given('I do not have an SSH agent running')
def step_no_ssh_agent(context):
    context.ssh_agent_running = False

@given('I do not have any SSH keys')
def step_no_ssh_keys(context):
    context.ssh_keys_exist = False

@given('I cannot SSH into a VM')
def step_cannot_ssh(context):
    context.cannot_ssh = True

@given('I don\'t have permission for an operation')
def step_no_permission(context):
    context.no_permission = True

@given('I get a "{error}" error')
def step_get_error(context, error):
    context.last_error = error

@given('I get permission denied errors in VM')
def step_permission_denied(context):
    context.permission_denied = True

# =============================================================================
# PROJECT PATTERNS
# =============================================================================

@given('I am working on one project')
def step_one_project(context):
    context.single_project = True

# NOTE: Parameterized project/workflow patterns removed to avoid conflicts
# Specific implementations should be added as needed

@given('I am setting up a new project')
def step_setting_up_project(context):
    context.setting_up_project = True

@given('documentation explains how to create each VM')
def step_documentation_exists(context):
    context.has_documentation = True

@given('each service has its own repository')
def step_separate_repos(context):
    context.separate_repos = True

@given('env-files/project-name.env is committed to git')
def step_env_committed(context):
    context.env_committed = True

# NOTE: a project requires specific services - in ssh_docker_steps.py

@given('docker-compose operation fails with transient error')
def step_transient_compose_error(context):
    context.transient_compose_error = True

# NOTE: a system service is using port - in ssh_docker_steps.py

@given('I already have a Go VM configured')
def step_go_vm_configured(context):
    context.has_go_vm = True

# =============================================================================
# THEN PATTERNS (specific ones only to avoid conflicts)
# =============================================================================

# NOTE: Broad parameterized patterns removed to avoid AmbiguousStep errors
# Specific Then steps should be added as needed
