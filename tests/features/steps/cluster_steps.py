import os
import shlex
import re
from behave import given, when, then
from vm_common import VDE_ROOT, run_vde_command

@given('I have "{vm1}" and "{vm2}" VMs created')
def step_vms_created(context, vm1, vm2):
    # Ensure they exist
    run_vde_command(f"create {vm1}")
    run_vde_command(f"create {vm2}")

@then('the cluster "{name}" should be saved')
def step_cluster_saved(context, name):
    cluster_file = VDE_ROOT / ".docker-state" / "clusters" / f"{name}.json"
    assert cluster_file.exists(), f"Cluster file {cluster_file} not found"

@then('VDE command "{cmd}" should contain "{text}"')
def step_command_contains(context, cmd, text):
    result = run_vde_command(cmd)
    assert text in result.stdout, f"Output of '{cmd}' does not contain '{text}': {result.stdout}"

@given('I have a saved cluster "{name}" with "{vm1}" and "{vm2}"')
def step_cluster_exists(context, name, vm1, vm2):
    run_vde_command(f"cluster save {name} {vm1} {vm2}")

@given('"{vm1}" and "{vm2}" VMs are stopped')
def step_vms_stopped(context, vm1, vm2):
    run_vde_command(f"stop {vm1}")
    run_vde_command(f"stop {vm2}")

@given('"{vm1}" and "{vm2}" VMs are running')
def step_vms_running(context, vm1, vm2):
    run_vde_command(f"start {vm1}")
    run_vde_command(f"start {vm2}")

@then('"{vm1}" and "{vm2}" VMs should be running')
def step_vms_should_be_running(context, vm1, vm2):
    # Use real-time status from vde-docker library functions if possible, 
    # but here we use the CLI 'ps' output which is the user-facing view.
    result = run_vde_command("ps")
    # Containers might be named vde-python or vde-python-1
    # Status might be [RUNNING] or show 'Up X seconds'
    out_upper = result.stdout.upper()
    assert re.search(f"vde-{vm1}(-1)?", result.stdout) and ("RUNNING" in out_upper or "UP" in out_upper), f"{vm1} not running in {result.stdout}"
    assert re.search(f"vde-{vm2}(-1)?", result.stdout) and ("RUNNING" in out_upper or "UP" in out_upper), f"{vm2} not running in {result.stdout}"

@then('"{vm1}" and "{vm2}" VMs should be stopped')
def step_vms_should_be_stopped(context, vm1, vm2):
    result = run_vde_command("ps")
    # Check if they are STOPPED or not in the list (if not created)
    # vde ps shows created/exited as [STOPPED]
    res1 = re.search(f"vde-{vm1}(-1)?", result.stdout)
    res2 = re.search(f"vde-{vm2}(-1)?", result.stdout)
    
    if res1:
        assert "[STOPPED]" in result.stdout or "[EXITED]" in result.stdout, f"{vm1} exists but not stopped: {result.stdout}"
    if res2:
        assert "[STOPPED]" in result.stdout or "[EXITED]" in result.stdout, f"{vm2} exists but not stopped: {result.stdout}"

@then('the cluster "{name}" should NOT exist')
def step_cluster_not_exists(context, name):
    cluster_file = VDE_ROOT / ".docker-state" / "clusters" / f"{name}.json"
    assert not cluster_file.exists(), f"Cluster file {cluster_file} still exists"

@then('the "{vm1}" and "{vm2}" VMs should still exist')
def step_vms_still_exist(context, vm1, vm2):
    # VMs exist if their configs exist
    assert (VDE_ROOT / "configs" / "docker" / "languages" / vm1).exists() or \
           (VDE_ROOT / "configs" / "docker" / "services" / vm1).exists()
    assert (VDE_ROOT / "configs" / "docker" / "languages" / vm2).exists() or \
           (VDE_ROOT / "configs" / "docker" / "services" / vm2).exists()

# NLP Steps (reuse parser_steps where possible, adding specific cluster checks)

@then('CLUSTER_ACTION should be "{expected_action}"')
def step_verify_cluster_action(context, expected_action):
    # Search for CLUSTER_ACTION in parser output
    actual = ""
    for line in context.parser_output.splitlines():
        if line.startswith("CLUSTER_ACTION:"):
            actual = line.replace("CLUSTER_ACTION:", "").strip()
            break
    assert actual == expected_action, f"Expected cluster action '{expected_action}', but got '{actual}'"

@then('CLUSTER_NAME should be "{expected_name}"')
def step_verify_cluster_name(context, expected_name):
    # Search for CLUSTER_NAME in parser output
    actual = ""
    for line in context.parser_output.splitlines():
        if line.startswith("CLUSTER_NAME:"):
            actual = line.replace("CLUSTER_NAME:", "").strip()
            break
    assert actual == expected_name, f"Expected cluster name '{expected_name}', but got '{actual}'"
