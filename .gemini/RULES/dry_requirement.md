# DRY Requirement (MANDATORY)
<!-- @forge (Governance Sentinel) -->

**Don't Repeat Yourself** - This is a hardcore requirement for ALL code in the VDE project.

## What is DRY?

DRY means: ONE generalized function with parameters, not multiple nearly-identical functions.

## Examples of VIOLATIONS

```python
# BAD - Duplicate logic
def verify_ssh_config_exists():
    """Verify SSH config file was created."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists()

def generate_ssh_config():
    """Generate SSH config."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    # ... different logic but same file path
```

```python
# BAD - Nearly identical functions
def get_vm_port_python(vm_name):
    return get_container_port(f"{vm_name}-dev", 22)

def get_vm_port_rust(vm_name):
    return get_container_port(f"{vm_name}-dev", 22)

# BAD - Copy-paste with minor changes
@then("SSH config should be generated")
def step_verify_config_1():
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists()

@then("SSH config should be regenerated")  
def step_verify_config_2():
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists()
```

## Examples of COMPLIANCE

```python
# GOOD - Single function with parameter
def execute_in_container(container, cmd, use_shell=True):
    """Execute command in container.
    
    Args:
        container: Container name
        cmd: Command to run
        use_shell: If True, run through shell; if False, run directly
    """
    if use_shell:
        return docker_exec(container, ["sh", "-c", cmd])
    else:
        return docker_exec(container, cmd.split())
```

```python
# GOOD - Reuse existing function
@when("SSH config is generated")
def step_generate_ssh_config(context):
    """Generate SSH config."""
    _generate_config_file()  # Shared helper

@then("SSH config should be generated")  
def step_verify_ssh_config(context):
    """Verify SSH config file was created."""
    _generate_config_file()  # Same helper for verification
    # OR just verify - different behavior, different step
```

## When Consolidating

When merging files (like SSH step files):
- **ELIMINATE duplicates** - don't preserve them
- **Merge similar logic** into one function with parameters
- **Create shared helpers** for common operations

## Detection

Watch for:
- Two functions doing the same thing with different names
- Copy-paste code with minor variations
- Functions that only differ by a parameter
- Multiple step definitions with identical logic

## Enforcement

Any code that violates DRY will be rejected in review.