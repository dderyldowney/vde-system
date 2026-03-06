"""
BDD Hooks for VDE test scenarios - SIMPLIFIED + PARSER OPTIMIZATION

This environment runs minimal setup and lets tests define their own requirements.
Includes persistent zsh process for parser tests.
"""

import os
import select
import shutil
import subprocess
import sys
import tempfile
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

def _backup_vde_ssh_dir():
    """Copy ~/.ssh/vde/ to a temp dir. Returns temp dir path or None."""
    vde_ssh = Path.home() / '.ssh' / 'vde'
    if vde_ssh.exists():
        tmpdir = tempfile.mkdtemp(prefix='vde_ssh_backup_')
        shutil.copytree(str(vde_ssh), os.path.join(tmpdir, 'vde'), symlinks=True)
        return tmpdir
    return None


def _restore_vde_ssh_dir(backup_tmpdir):
    """Restore ~/.ssh/vde/ from backup temp dir and remove temp dir."""
    if backup_tmpdir is None:
        return
    vde_ssh = Path.home() / '.ssh' / 'vde'
    backup = Path(backup_tmpdir) / 'vde'
    if vde_ssh.exists():
        shutil.rmtree(str(vde_ssh))
    if backup.exists():
        shutil.copytree(str(backup), str(vde_ssh), symlinks=True)
        vde_ssh.chmod(0o700)
    shutil.rmtree(backup_tmpdir, ignore_errors=True)


def _backup_configs_dir():
    """Copy configs/ and scripts/data/vm-types.json to a temp dir. Returns temp dir path or None."""
    configs_dir = Path(VDE_ROOT) / 'configs'
    if configs_dir.exists():
        tmpdir = tempfile.mkdtemp(prefix='vde_configs_backup_')
        shutil.copytree(str(configs_dir), os.path.join(tmpdir, 'configs'), symlinks=True)
        vm_types_json = Path(VDE_ROOT) / 'scripts' / 'data' / 'vm-types.json'
        if vm_types_json.exists():
            shutil.copy2(str(vm_types_json), os.path.join(tmpdir, 'vm-types.json'))
        return tmpdir
    return None


def _restore_configs_dir(backup_tmpdir):
    """Restore configs/ and scripts/data/vm-types.json from backup temp dir."""
    if backup_tmpdir is None:
        return
    configs_dir = Path(VDE_ROOT) / 'configs'
    backup = Path(backup_tmpdir) / 'configs'
    if configs_dir.exists():
        shutil.rmtree(str(configs_dir))
    if backup.exists():
        shutil.copytree(str(backup), str(configs_dir), symlinks=True)
    vm_types_backup = Path(backup_tmpdir) / 'vm-types.json'
    if vm_types_backup.exists():
        shutil.copy2(str(vm_types_backup), str(Path(VDE_ROOT) / 'scripts' / 'data' / 'vm-types.json'))
    shutil.rmtree(backup_tmpdir, ignore_errors=True)


def _restore_stale_compose_backups():
    """Restore any .yml.bak files left by killed test runs."""
    configs_dir = Path(VDE_ROOT) / "configs" / "docker"
    for bak in configs_dir.glob("**/*.yml.bak"):
        original = bak.with_suffix("")
        if original.exists():
            original.unlink()
        bak.rename(original)


def before_all(context):
    """Minimal setup."""
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["DOCKER_BUILDKIT"] = "0"
    os.environ["VDE_TEST_MODE"] = "1"

    # Restore any compose file backups left by previously killed test runs
    _restore_stale_compose_backups()

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

    if "user-guide-installation" in feature.tags or "user-guide-internal" in feature.tags:
        # Back up configs/ — these features mutate real config files
        context._configs_backup = _backup_configs_dir()
        print(f"[SETUP] {feature.name} — configs/ backed up")
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


def _get_running_vde_containers() -> list:
    """Return list of currently running vde-* container names."""
    try:
        r = subprocess.run(
            ["docker", "ps", "--filter", "name=vde-", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        return [c.strip() for c in r.stdout.splitlines() if c.strip()]
    except Exception:
        return []


def _stop_containers(container_names: list) -> None:
    """Stop and remove a list of containers."""
    for name in container_names:
        try:
            subprocess.run(["docker", "stop", name], capture_output=True, timeout=30)
            subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
        except Exception:
            pass


def before_scenario(context, scenario):
    """Reset context and start parser process for unit tests."""
    context.last_output = ""
    context.last_error = ""
    context.last_exit_code = 0
    context._unset_ssh_auth_sock = False

    # Skip @requires-docker-host scenarios when Docker is unavailable
    if "requires-docker-host" in scenario.effective_tags:
        if not _docker_host_available():
            scenario.skip("Docker host not available")
            return

    # Track containers before Docker scenarios for cleanup
    if "requires-docker-host" in scenario.effective_tags:
        context._containers_before_scenario = _get_running_vde_containers()

    # Backup ~/.ssh/vde/ before SSH scenarios so they can't bleed state
    if any(t in scenario.effective_tags for t in ('requires-docker-ssh', 'requires-ssh-agent')):
        context._vde_ssh_backup = _backup_vde_ssh_dir()
    else:
        context._vde_ssh_backup = None

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
    # Restore any compose file backup left by the invalid-YAML scenario
    compose_backup = getattr(context, '_compose_backup', None)
    compose_path = getattr(context, '_compose_path', None)
    if compose_backup and Path(compose_backup).exists():
        if compose_path and Path(compose_path).exists():
            Path(compose_path).unlink()
        Path(compose_backup).rename(compose_path)

    # Restore ~/.ssh/vde/ from backup (SSH scenario isolation)
    _restore_vde_ssh_dir(getattr(context, '_vde_ssh_backup', None))
    context._vde_ssh_backup = None

    # Remove test artifacts from public-ssh-keys/ to prevent cross-scenario pollution
    pub_keys_dir = Path(VDE_ROOT) / "public-ssh-keys"
    if pub_keys_dir.exists():
        for f in pub_keys_dir.iterdir():
            if f.is_file() and f.name not in ('.keep', '.gitignore') and not f.name.startswith('vde_'):
                f.unlink(missing_ok=True)

    # Stop containers created during @requires-docker-host scenarios
    if "requires-docker-host" in scenario.effective_tags and _docker_host_available():
        before = getattr(context, '_containers_before_scenario', [])
        after = _get_running_vde_containers()
        created_by_test = [c for c in after if c not in before]
        if created_by_test:
            _stop_containers(created_by_test)

    if hasattr(context, '_parser_proc') and context._parser_proc:
        try:
            context._parser_proc.stdin.write('exit\n')
            context._parser_proc.stdin.flush()
            context._parser_proc.terminate()
            context._parser_proc.wait(timeout=5)
        except:
            pass


def after_feature(context, feature):
    """Stop all VDE containers after any feature that required Docker."""
    if "user-guide-installation" in feature.tags or "user-guide-internal" in feature.tags:
        _restore_configs_dir(getattr(context, '_configs_backup', None))
        context._configs_backup = None
        print(f"[TEARDOWN] {feature.name} — configs/ restored")

    if "requires-docker-host" in feature.tags and _docker_host_available():
        running = _get_running_vde_containers()
        if running:
            print(f"[TEARDOWN] Stopping {len(running)} VDE container(s) after feature: {feature.name}")
            _stop_containers(running)


def after_all(context):
    """Stop any remaining VDE containers after the full test run."""
    if _docker_host_available():
        remaining = _get_running_vde_containers()
        if remaining:
            print(f"[TEARDOWN] Final cleanup: stopping {len(remaining)} VDE container(s)")
            _stop_containers(remaining)
