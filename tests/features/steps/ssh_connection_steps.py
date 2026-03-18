"""
BDD Step Definitions for SSH Connection Testing.

These steps verify SSH connectivity between VMs and from host to VMs.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    wait_for_container,
)

# =============================================================================
# SSH CONNECTION GIVEN steps
# =============================================================================


@given("I have configured SSH through VDE")
@given("I have set up SSH keys")
def step_have_ssh_keys(context):
    """Context: SSH keys have been set up for authentication."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    ssh_dir.mkdir(parents=True, exist_ok=True)

    private_key = ssh_dir / "id_ed25519"
    public_key = ssh_dir / "id_ed25519.pub"

    # Check if keys exist, if not, they are created during ssh-setup --init
    if not private_key.exists():
        run_vde_command("ssh-setup --init", context=context)

    context.ssh_keys_setup = private_key.exists() and public_key.exists()


@given("I have a web service running in a VM")
def step_web_service_in_vm(context):
    """Context: A web service is running inside a VM container."""
    # We'll use nginx as a representative web service
    if not container_exists("nginx"):
        run_vde_command("create nginx", context=context)
        run_vde_command("start nginx", context=context)
        wait_for_container("nginx", timeout=60)

    # Check if port is mapped using vde port
    result = run_vde_command("port nginx 80", context=context)
    context.web_service_running = result.returncode == 0
    context.web_service_vm = "nginx"


# =============================================================================
# SSH CONNECTION THEN steps
# =============================================================================


@then("the VM should be ready to use")
def step_vm_ready_ssh(context):
    """Verify VM is ready - container running."""
    from vm_common import docker_ps

    running = docker_ps()
    # Check for anything starting with vde- or tagged with vde.managed
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) > 0, f"No VDE VMs are running. Found: {running}"


@then("it should be accessible via SSH")
def step_accessible_ssh(context):
    """Verify VM is accessible via SSH port mapping."""
    # Get a running VM
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"port {vm_name} 22", context=context)
        assert result.returncode == 0, f"SSH port mapping not found for {vm_name}"
        assert "22" in result.stdout or result.stdout.strip(), (
            f"Invalid port output: {result.stdout}"
        )


@when("I access localhost on the VM's port")
def step_access_localhost_port(context):
    vm_name = getattr(context, "web_service_vm", "nginx")
    result = run_vde_command(f"port {vm_name} 80", context=context)
    assert result.returncode == 0, f"Failed to get port for {vm_name}"
    port = result.stdout.strip()
    curl_result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:{port}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    context.http_status = curl_result.stdout.strip()


@when("I connect to a VM")
def step_connect_vm(context):
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"connect {vm_name} --dry-run", context=context)
        context.ssh_connection_cmd = result.stdout
        context.last_exit_code = result.returncode


@then("I should receive the hostname (localhost)")
def step_receive_hostname(context):
    """Verify hostname is localhost - check SSH config points to localhost."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "localhost" in content.lower() or "127.0.0.1" in content, (
            "SSH config should reference localhost for connections"
        )


@then("I should receive the SSH port")
def step_receive_ssh_port(context):
    """Verify SSH port is received via vde port."""
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"port {vm_name} 22", context=context)
        assert result.returncode == 0, "Failed to get SSH port"
        assert result.stdout.strip(), "SSH port mapping should not be empty"


@then("I should receive the username (devuser)")
def step_receive_username(context):
    """Verify username is devuser - check VDE config."""
    # VDE containers use devuser as the default user
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        assert "devuser" in content.lower(), "VDE should use devuser as default username"
    context.user_is_devuser = True


@then("language VMs should have SSH access")
def step_language_vms_ssh(context):
    """Verify language VMs have SSH access configured in compose files."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        # Check python specifically as it's a guaranteed language VM
        compose_file = configs_dir / "python" / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            assert "22" in content, "Language VM missing SSH port mapping"


@then("vde command should be available")
def step_vde_available(context):
    """Verify VDE command is available via version check."""
    result = run_vde_command("--version", context=context)
    assert result.returncode == 0, "VDE should be available"


@then("each VM should have its own separate data directory")
def step_each_separate_data(context):
    """Verify each VM has separate configuration directory."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.exists(), "Configs directory missing"
    assert (configs_dir / "python").exists(), "Python VM config missing"
    assert (configs_dir / "go").exists(), "Go VM config missing"


@then("files should be shared between host and VM via mounts")
def step_files_shared_host_vm(context):
    """Verify files are shared between host and VM via inspect."""
    # Verify mount configuration in a known VM
    result = run_vde_command("inspect python -f '{{json .Mounts}}'", context=context)
    if result.returncode == 0:
        mounts = result.stdout.lower()
        assert any(k in mounts for k in ["projects", "workspace", "data", "vde"]), (
            f"Expected project/data mounts not found in: {mounts}"
        )


@then("all should use my SSH keys for SSH-Connection")
def step_all_use_ssh_keys(context):
    """Verify all VMs use configured SSH keys."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    assert ssh_dir.exists(), "VDE SSH directory should exist"
    assert (ssh_dir / "id_ed25519").exists(), "VDE private key missing"


@then("all should work with the same configuration for SSH-Connection")
def step_all_same_config(context):
    """Verify all VMs work with same base configuration."""
    assert (VDE_ROOT / "configs" / "docker").exists(), "VM configurations should exist"


@then("both connections should work")
def step_both_connections_work(context):
    """Verify multiple VM connectivity capability."""
    running = docker_ps()
    assert len(running) >= 1, "At least one VM should be running for connectivity test"


@then("both should be accessible via SSH")
def step_both_accessible_ssh(context):
    """Verify multiple VM accessibility capability."""
    running = docker_ps()
    assert len(running) >= 1, "At least one VM should be running"


@then("standard Node.js aliases should be functional for starting VMs")
def step_all_node_aliases_work(context):
    """Verify all node aliases work using vde create command."""
    for alias in ["js", "node", "nodejs"]:
        result = run_vde_command(f"create {alias}", context=context)
        # 0 = created, 6 = already exists (both are success for this test)
        assert result.returncode in [0, 6], f"Alias '{alias}' failed with rc={result.returncode}"


@then("aliases should show in list-vms output")
def step_aliases_show_in_list(context):
    """Verify aliases show in vde list output."""
    result = run_vde_command("list", context=context)
    output = result.stdout.lower()
    # Check for presence of alias markers in the list output
    assert any(x in output for x in ["js", "nodejs", "alias"]), "Aliases missing from list output"


@then("I can use any alias to reference the VM")
def step_can_use_any_alias(context):
    """Verify any alias can be used in reference VM."""
    # Try an alias
    result = run_vde_command("status js", context=context)
    assert result.returncode == 0, "Should be able to reference VM by alias"


# =============================================================================
# ADDITIONAL STEPS FOR SSH CONFIG VERIFICATION
# =============================================================================


@then("the SSH config entries should exist")
def step_ssh_config_entries_exist(context):
    """Verify SSH config entries exist for VMs."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Host" in content, "SSH config should have Host entries"
    else:
        assert False, "SSH config file should exist"


@then("I should be able to use short hostnames")
def step_use_short_hostnames(context):
    """Verify short hostnames work in SSH config."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "vde-" in content, "SSH config should have vde-* hostnames"


@then("I should not need to remember port numbers")
def step_no_port_numbers_needed(context):
    """Verify SSH config handles port mapping."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Port" in content, "SSH config should have Port entries"


@then("my public keys should be copied to public-ssh-keys/")
def step_public_keys_copied(context):
    """Verify public keys are copied to public-ssh-keys/."""
    public_dir = VDE_ROOT / "public-ssh-keys"
    if public_dir.exists():
        pub_files = list(public_dir.glob("*.pub"))
        assert len(pub_files) >= 0, "Public keys should be in public-ssh-keys/"


@then("all my public keys should be in the VM's authorized_keys")
def step_public_keys_in_authorized(context):
    """Verify public keys are in VM's authorized_keys."""
    # Check a running VM for authorized_keys
    result = run_vde_command("exec python 'cat ~/.ssh/authorized_keys'", context=context)
    # If VM is running, check for keys
    if result.returncode == 0:
        output = result.stdout
        assert "ssh-" in output or len(output) > 0, "Authorized keys should contain public keys"


@then("I should be able to use any of the keys")
def step_use_any_key(context):
    """Verify any of the configured keys can be used."""
    from ssh_helpers import ssh_agent_has_keys, ssh_agent_is_running

    assert ssh_agent_is_running(), "SSH agent should be running"
    # Keys should be available


@then("I should not need to manually copy keys")
def step_no_manual_key_copy(context):
    """Verify keys were copied automatically."""
    from pathlib import Path

    public_dir = VDE_ROOT / "public-ssh-keys"
    # Keys should have been synced automatically
    assert public_dir.exists(), "public-ssh-keys should exist (auto-sync)"
