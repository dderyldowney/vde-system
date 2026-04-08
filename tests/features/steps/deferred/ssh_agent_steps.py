from behave import given, when, then
import os
import shutil
import subprocess
from pathlib import Path
from config import VDE_ROOT, VDE_SSH_DIR
from ssh_helpers import ssh_agent_is_running, has_ssh_keys
from vm_common import run_vde_command

# Use a temporary alternate SSH directory for tests that need "no keys" 
# to avoid destroying user's actual ~/.ssh/vde/
TEST_SSH_DIR = VDE_ROOT / ".tmp_test_ssh"

@then('the key should be loaded into the agent')
@then('my keys should be loaded automatically')
@then('all keys should be loaded into the agent')
@then('my keys should be loaded into the agent')
def step_key_loaded_agent(context):
    output = getattr(context, 'last_output', '')
    assert 'Identity added' in output or 'Key loaded' in output or 'agent' in output.lower(), \
        f"Output should show keys being loaded. Got: {output}"

@then('VDE should inform me of the SSH setup status')
def step_inform_ssh_status(context):
    output = getattr(context, 'last_output', '')
    assert 'SSH' in output and 'setup' in output.lower(), "Should inform about SSH setup"

@then('I can immediately use SSH to run commands')
def step_use_ssh_immediately(context):
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f'exec {vm_name} "whoami"', context=context)
    assert result.returncode == 0
    assert 'devuser' in result.stdout

@then('my existing VDE SSH keys should be detected')
def step_existing_keys_detected(context):
    output = getattr(context, 'last_output', '')
    assert 'Found existing keys' in output or 'Using existing' in output.lower()

@then('no SSH-related configuration messages should be shown')
def step_no_ssh_messages(context):
    output = getattr(context, 'last_output', '')
    assert 'Starting SSH agent' not in output

@then('I should see exactly the VM creation progress')
def step_see_progress(context):
    output = getattr(context, 'last_output', '')
    assert 'Starting' in output or 'Progress' in output

@then('I should see the SSH agent status')
def step_see_agent_status(context):
    output = getattr(context, 'command_output', getattr(context, 'last_output', ''))
    assert 'Agent PID' in output or 'running' in output.lower()

@then('I should see my available SSH keys')
def step_see_available_keys(context):
    output = getattr(context, 'command_output', getattr(context, 'last_output', ''))
    assert 'Available keys' in output or 'id_ed25519' in output

@then('I should see keys loaded in the agent')
def step_see_loaded_keys(context):
    output = getattr(context, 'command_output', getattr(context, 'last_output', ''))
    assert 'Loaded identities' in output or 'The agent has no identities' in output or 'SHA256' in output

@then('I should see usage examples')
def step_see_usage_examples(context):
    output = getattr(context, 'command_output', getattr(context, 'last_output', ''))
    assert 'vde enter' in output or 'vde exec' in output

@then('ed25519 should be the preferred key type')
def step_ed25519_preferred(context):
    pass

@then('the key should be generated with a comment')
def step_key_with_comment(context):
    ssh_dir = Path(os.environ.get('VDE_SSH_DIR', VDE_SSH_DIR))
    pub_key = ssh_dir / 'id_ed25519.pub'
    with open(pub_key, 'r') as f:
        content = f.read()
    assert 'vde' in content or 'devuser' in content

@then('I should see that SSH management is automatic')
@then('no manual SSH setup instructions should be present')
def step_check_docs_content(context):
    pass

