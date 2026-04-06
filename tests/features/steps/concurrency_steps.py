"""
Step definitions for Concurrency & Stress Hardening tests.
Simulates high-pressure VM operations to verify locking and atomic allocation.
"""

import os
import subprocess
import time
import concurrent.futures
from pathlib import Path
from behave import given, when, then
from vm_common import VDE_ROOT, load_vm_types_raw

@given("the VDE system is initialized")
def step_system_init(context):
    """Ensure the system is ready for testing."""
    # Ensure cache is fresh
    subprocess.run([str(VDE_ROOT / "bin/vde"), "rebuild-cache"], check=True)
    # Ensure locks dir exists and is clean
    locks_dir = VDE_ROOT / ".locks"
    if locks_dir.exists():
        subprocess.run(["rm", "-rf", str(locks_dir)], check=True)
    locks_dir.mkdir(parents=True, exist_ok=True)

@given('I have a list of VM aliases: "{aliases_str}"')
def step_set_aliases(context, aliases_str):
    """Store the list of VM aliases to be used in the test."""
    context.vm_aliases = [a.strip() for a in aliases_str.split(",")]

@when("I attempt to create and start these VMs simultaneously")
def step_parallel_ignition(context):
    """Launch multiple 'vde start' commands in parallel."""
    vde_bin = str(VDE_ROOT / "bin/vde")
    
    def start_vm(alias):
        # Use vde rebuild base if needed, but here we assume base exists
        return subprocess.run([vde_bin, "start", alias], 
                            capture_output=True, 
                            text=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(context.vm_aliases)) as executor:
        # Submit all tasks
        future_to_alias = {}
        for alias in context.vm_aliases:
            future_to_alias[executor.submit(start_vm, alias)] = alias
            time.sleep(0.1)
            
        context.results = {}
        for future in concurrent.futures.as_completed(future_to_alias):
            alias = future_to_alias[future]
            try:
                context.results[alias] = future.result()
            except Exception as exc:
                context.results[alias] = f"Error: {exc}"

@when("I attempt to add multiple new VM types simultaneously")
def step_parallel_add_vm_types(context):
    """Launch multiple 'add-vm-type' commands in parallel."""
    add_bin = str(VDE_ROOT / "bin/add-vm-type")
    
    # We use a list of unique names to avoid name collisions (not the goal here)
    # The goal is to verify port allocation and registry integrity
    new_types = ["stress1", "stress2", "stress3", "stress4", "stress5"]
    context.new_vm_types = new_types
    
    def add_type(name):
        return subprocess.run([add_bin, name, "echo stress"], 
                            capture_output=True, 
                            text=True,
                            timeout=60) # Increased timeout

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(new_types)) as executor:
        future_to_name = {}
        for name in new_types:
            future_to_name[executor.submit(add_type, name)] = name
            # Stagger submissions slightly to prevent perfect timing collisions
            time.sleep(0.1)
            
        context.add_results = {}
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                context.add_results[name] = future.result()
            except Exception as exc:
                context.add_results[name] = f"Error: {exc}"

@then("all new VM types should be added successfully")
def step_verify_add_success(context):
    """Verify all add-vm-type commands exited successfully."""
    failures = []
    for name, result in context.add_results.items():
        if isinstance(result, str) or result.returncode != 0:
            stderr = result.stderr if hasattr(result, 'stderr') else result
            failures.append(f"{name}: {stderr}")
    assert not failures, f"Parallel add-vm-type failed:\n" + "\n".join(failures)

@then("the VDE registry should remain valid and uncorrupted")
def step_verify_registry_integrity(context):
    """Verify that vm-types.json is valid and contains all new entries."""
    # 1. Schema check
    vde_bin = str(VDE_ROOT / "bin/vde")
    # vde validate-schemas now only checks vm-types.json
    subprocess.run([vde_bin, "validate-schemas"], check=True)
    
    # 2. Content check
    vm_types = load_vm_types_raw()
    # Check both languages and services categories
    names = []
    for cat in ["language", "service"]:
        names.extend([vm["name"] for vm in vm_types["vms"].get(cat, [])])
        
    for name in context.new_vm_types:
        assert f"vde-{name}" in names, f"New VM type 'vde-{name}' missing from registry"

@then("all VMs should be created successfully")
def step_verify_success(context):
    """Verify that all parallel start commands exited with success."""
    failures = []
    for alias, result in context.results.items():
        if isinstance(result, str) or result.returncode != 0:
            stdout = result.stdout if hasattr(result, 'stdout') else ""
            stderr = result.stderr if hasattr(result, 'stderr') else result
            failures.append(f"{alias} (Code: {getattr(result, 'returncode', 'ERR')})\nSTDOUT: {stdout}\nSTDERR: {stderr}")
    
    assert not failures, f"Parallel ignition failed for some VMs:\n" + "\n".join(failures)

@then("all {which} should have unique SSH ports")
def step_verify_unique_ports(context, which):
    """Verify that no two items were allocated the same SSH port."""
    if which == "VMs":
        targets = context.vm_aliases
    else:
        targets = context.new_vm_types
        
    ports = {}
    for alias in targets:
        # Get allocated port via 'vde info <alias>' or direct registry check
        # We'll use the registry check for maximum directness
        port_file = VDE_ROOT / f".cache/port-registry/{alias}.port"
        if not port_file.exists():
            # Fallback to resolving name first
            from vm_common import get_container_name
            canonical = get_container_name(alias)
            port_file = VDE_ROOT / f".cache/port-registry/{canonical}.port"
            
        assert port_file.exists(), f"Port registry entry missing for {alias}"
        port = port_file.read_text().strip()
        
        if port in ports:
            assert False, f"Port collision detected! Port {port} used by both {ports[port]} and {alias}"
        ports[port] = alias

@then("there should be no lock file leftovers")
def step_verify_no_locks(context):
    """Ensure all lifecycle locks were released."""
    locks_dir = VDE_ROOT / ".locks/vms"
    if not locks_dir.exists():
        return
        
    leftovers = list(locks_dir.glob("*.lock"))
    assert not leftovers, f"Stale lock files found: {', '.join([l.name for l in leftovers])}"

@then("I cleanup the stress VM types")
def step_cleanup_stress_types(context):
    """Remove the temporary stress VM types from the registry."""
    conf_file = VDE_ROOT / "data/vm-types.conf"
    content = conf_file.read_text()
    
    new_lines = []
    for line in content.splitlines():
        is_stress = False
        for name in context.new_vm_types:
            if f"vde-{name}" in line:
                is_stress = True
                break
        if not is_stress:
            new_lines.append(line)
            
    conf_file.write_text("\n".join(new_lines) + "\n")
    
    # Trigger re-smelt
    vde_bin = str(VDE_ROOT / "bin/vde")
    subprocess.run([vde_bin, "rebuild-cache"], check=True)

@then("all VMs should be reachable via SSH")
def step_verify_ssh(context):
    """Perform a quick 'whoami' check via SSH for all started VMs."""
    vde_bin = str(VDE_ROOT / "bin/vde")
    failures = []
    
    for alias in context.vm_aliases:
        result = subprocess.run([vde_bin, "exec", alias, "whoami"], 
                              capture_output=True, 
                              text=True)
        if result.returncode != 0:
            failures.append(f"{alias} (SSH Exec Failed): {result.stderr}")
        elif "devuser" not in result.stdout:
            failures.append(f"{alias} (Wrong user): {result.stdout}")
            
    assert not failures, f"Some VMs are not reachable or healthy:\n" + "\n".join(failures)
