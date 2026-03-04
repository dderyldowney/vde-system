"""
BDD Step definitions for Natural Language Parser scenarios.
OPTIMIZED: Uses persistent zsh process from context when available.
"""

import os
import select
import shlex
import subprocess
import sys

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


def _read_until_prompt(proc, timeout=10):
    """Read output from persistent process until prompt."""
    output = []
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 0.1)
        if ready:
            char = proc.stdout.read(1)
            if not char:
                break
            output.append(char)
            if char == '\n' and output:
                if len(output) > 2 and output[-3] in ('$', '#'):
                    break
        else:
            if proc.poll() is not None:
                break
        if len(output) > 10000:
            break
    return ''.join(output)


def _call_vde_parser_function(function_name, input_string, context=None):
    """Call a vde-parser function - uses persistent process if available."""
    
    # Try to use persistent process from context
    if context and hasattr(context, '_parser_proc') and context._parser_proc:
        proc = context._parser_proc
        cmd = f'''
export VDE_TEST_INPUT="{input_string}"
output=$({function_name} "$VDE_TEST_INPUT" 2>/dev/null)
echo "$output"
'''
        proc.stdin.write(cmd)
        proc.stdin.flush()
        output = _read_until_prompt(proc)
        
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        output_lines = []
        for line in lines:
            if line.startswith('[') or ' -0500' in line or line.startswith('20'):
                continue
            if '=' in line and "'" in line:
                continue
            output_lines.append(line)
        return '\n'.join(output_lines) if output_lines else '', 0
    
    # Fallback: spawn new zsh process
    env = os.environ.copy()
    env['VDE_TEST_INPUT'] = input_string
    env['VDE_LOG_LEVEL'] = 'ERROR'
    cmd = f"zsh -c 'source {VDE_SHELL_COMPAT} && source {VDE_VM_COMMON} && source {VDE_PARSER} && {function_name} \"$VDE_TEST_INPUT\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    output_lines = []
    for line in lines:
        if line.startswith('[') or ' -0500' in line or line.startswith('20'):
            continue
        if '=' in line and "'" in line:
            continue
        output_lines.append(line)
    return '\n'.join(output_lines) if output_lines else '', result.returncode


# =============================================================================
# Real vde-parser function wrappers
# =============================================================================

def _get_real_intent(input_string, context=None):
    """Call vde-parser's detect_intent function."""
    stdout, _ = _call_vde_parser_function('detect_intent', input_string, context)
    return stdout


def _get_real_vm_names(input_string, context=None):
    """Call vde-parser's extract_vm_names function."""
    stdout, _ = _call_vde_parser_function('extract_vm_names', input_string, context)
    if not stdout:
        return []
    return [vm for vm in stdout.split('\n') if vm]


def _get_real_filter(input_string, context=None):
    """Call vde-parser's extract_filter function."""
    stdout, _ = _call_vde_parser_function('extract_filter', input_string, context)
    return stdout if stdout else 'all'


def _get_real_flags(input_string, context=None):
    """Call vde-parser's extract_flags function."""
    stdout, _ = _call_vde_parser_function('extract_flags', input_string, context)
    flags = {'rebuild': False, 'nocache': False}
    if stdout:
        for pair in stdout.split():
            if '=' in pair:
                key, val = pair.split('=', 1)
                if val.lower() in ('true', '1', 'yes'):
                    flags[key] = True
    return flags
