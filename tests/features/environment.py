"""
BDD Hooks for VDE test scenarios - SIMPLIFIED + PARSER OPTIMIZATION

This environment runs minimal setup and lets tests define their own requirements.
Includes persistent zsh process for parser tests.
"""

import os
import select
import subprocess
import sys
from pathlib import Path

# Add tests directory to path
tests_dir_path = Path(__file__).parent.parent
if str(tests_dir_path) not in sys.path:
    sys.path.insert(0, str(tests_dir_path))

try:
    from test_config_loader import get_behave_config
except ImportError:
    def get_behave_config():
        return None


# Import shared configuration
features_dir = os.path.dirname(os.path.abspath(__file__))
steps_dir = os.path.join(features_dir, "steps")
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from config import VDE_ROOT

# Track state
_SSH_AGENT_PID = None

# Parser library paths
VDE_PARSER = os.path.join(VDE_ROOT, 'scripts/lib/vde-parser')
VDE_VM_COMMON = os.path.join(VDE_ROOT, 'scripts/lib/vm-common')
VDE_SHELL_COMPAT = os.path.join(VDE_ROOT, 'scripts/lib/vde-shell-compat')


def run_vde_command(command, timeout=60):
    """Run a VDE script and return the result."""
    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "0"
    vde_script = os.path.join(VDE_ROOT, "scripts", "vde")
    full_cmd = f"cd {VDE_ROOT} && {vde_script} {command}"
    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def run_vde_ps(args=None, timeout=30):
    """Run vde-ps and return the result."""
    vde_ps = os.path.join(VDE_ROOT, "scripts", "vde-ps")
    cmd = ["zsh", vde_ps]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=VDE_ROOT)
    return result


# =============================================================================
# PARSER TEST OPTIMIZATION: Persistent zsh process
# =============================================================================

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


def _call_parser_function(context, function_name, input_string):
    """Call a vde-parser function in the persistent process."""
    if not hasattr(context, '_parser_proc') or not context._parser_proc:
        raise RuntimeError("Parser process not initialized")
    
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
    
    return '\n'.join(output_lines), 0


# Expose to step modules via module-level function
def get_parser_helper():
    """Return parser helper functions for use in steps."""
    return {
        '_call_parser_function': _call_parser_function,
    }


# =============================================================================
# STANDARD HOOKS
# =============================================================================

def before_all(context):
    """Minimal setup."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["DOCKER_BUILDKIT"] = "0"
    os.environ["VDE_TEST_MODE"] = "1"

    cache_file = Path(VDE_ROOT) / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()


def before_feature(context, feature):
    """Tier-aware setup based on feature tags."""
    tags = feature.tags

    if "@unit" in tags:
        print("[SETUP] Unit test mode")
        return

    if "@integration" in tags:
        print("[SETUP] Integration test mode")
        os.environ["VDE_NETWORK"] = "vde-testing"
        run_vde_command("init --networks-only --testing", timeout=30)
        return

    if "@docker" in tags:
        # Skip Docker setup if Docker host is unavailable (all scenarios will be skipped too)
        if "requires-docker-host" in tags and not _docker_host_available():
            print("[SETUP] Docker host unavailable — skipping Docker feature setup")
            return
        print("[SETUP] Docker test mode")
        os.environ["VDE_NETWORK"] = "vde-testing"
        result = run_vde_ps(["-a", "-q"])
        if result.returncode == 0:
            containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
            for container in containers:
                vm_name = container.replace("vde-", "") if container.startswith("vde-") else container
                run_vde_command(f"remove {vm_name}", timeout=30)
        run_vde_command("init --networks-only --testing", timeout=30)
        return

    if "core-infrastructure" in feature.filename:
        print("[SETUP] Core infrastructure - minimal setup")
        os.environ["VDE_NETWORK"] = "vde-testing"


def _docker_host_available() -> bool:
    """Return True if a Docker daemon is reachable."""
    try:
        r = subprocess.run(
            ["docker", "info"],
            capture_output=True, timeout=5
        )
        return r.returncode == 0
    except Exception:
        return False


def before_scenario(context, scenario):
    """Reset context and start parser process for unit tests."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0

    # Skip @requires-docker-host scenarios when Docker is unavailable
    if "requires-docker-host" in scenario.effective_tags:
        if not _docker_host_available():
            scenario.skip("Docker host not available")
            return

    # Check if this is a parser test (unit test)
    if hasattr(scenario, 'feature') and hasattr(scenario.feature, 'tags'):
        if '@unit' in scenario.feature.tags:
            # Start persistent zsh for parser tests
            env = os.environ.copy()
            env['VDE_LOG_LEVEL'] = 'ERROR'
            
            init_cmd = f'''
source {VDE_SHELL_COMPAT}
source {VDE_VM_COMMON}
source {VDE_PARSER}
'''
            context._parser_proc = subprocess.Popen(
                ['zsh'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1
            )
            context._parser_proc.stdin.write(init_cmd)
            context._parser_proc.stdin.flush()
            _read_until_prompt(context._parser_proc)


def after_scenario(context, scenario):
    """Cleanup parser process and SSH config test state."""
    # Remove SSH files written by test scenarios to prevent state bleed
    vde_ssh = Path.home() / '.ssh' / 'vde'
    for filename in ('config', 'known_hosts', 'known_hosts.vde-backup'):
        p = vde_ssh / filename
        if p.exists():
            p.unlink()

    if hasattr(context, '_parser_proc') and context._parser_proc:
        try:
            context._parser_proc.stdin.write('exit\n')
            context._parser_proc.stdin.flush()
            context._parser_proc.terminate()
            context._parser_proc.wait(timeout=5)
        except:
            pass


def after_all(context):
    """No teardown."""
    pass
