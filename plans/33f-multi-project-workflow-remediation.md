# Plan 33f: Multi-Project Workflow Remediation

**Feature**: `tests/features/docker-required/multi-project-workflow.feature`  
**Created**: 2026-02-06  
**Updated**: 2026-02-07  
**Status**: ⚠️ PARTIAL - See Plan 34 for remaining work

---

## Summary

This plan addresses the implementation of multi-project workflow tests for VDE. Users should be able to set up, manage, and switch between multiple development projects using VDE VMs.

---

## Current Status (2026-02-07)

### Test Results
- **Total Scenarios**: 9
- **Passing**: 3
- **Failing**: 6
- **Steps**: 23 unique implemented

### Failing Scenarios
1. "Web development project setup" - Missing pre-created VMs
2. "Switching between projects" - Path verification issues
3. "Microservices architecture setup" - VM requirements not met
4. "Data science project setup" - VM creation fails
5. "Full stack web applications" - Dependencies not configured
6. "Mobile development with backend" - Flutter VM issues

### Root Causes
1. **VM Pre-creation**: Scenarios require VMs to exist before execution, but `_SCENARIO_REQUIREMENTS` is not properly populated
2. **Path Verification**: Uses wrong directories (configs/docker vs data/)
3. **Environment Hooks**: `_setup_scenario_environment()` not creating VMs defined in requirements

---

## Original Plan Content

### Overview

This plan implements step definitions for testing VDE's multi-project workflow capabilities. These tests verify that users can:
- Set up web development projects (JavaScript, nginx)
- Switch between different projects
- Configure microservices architectures
- Set up data science environments (Python, R, Redis)
- Deploy full-stack web applications
- Develop mobile apps with backend services

### Scope

#### Project Type Tests
- **Web Development**: JavaScript + nginx
- **Microservices**: Go + Rust + nginx
- **Data Science**: Python + R + Redis
- **Full Stack**: Python + PostgreSQL + nginx + Redis
- **Mobile Development**: Flutter + Go

#### Workflow Tests
- Project setup and configuration
- Switching between projects
- Cleaning up between projects

### Phase 1: Discovery & Analysis

1. **Analyze Feature File**
   - Document all scenarios and their Gherkin steps
   - Identify VM requirements for each scenario
   - Map dependencies between scenarios

2. **Survey Existing Libraries**
   - `tests/features/steps/docker_lifecycle_steps.py` - VM lifecycle
   - `tests/features/steps/multi_project_workflow_steps.py` - Project workflows
   - `tests/features/environment.py` - Scenario hooks

3. **Identify Patterns**
   - Common VM requirements across scenarios
   - Shared setup/teardown patterns
   - Project-specific configuration needs

### Phase 2: Step Definition Planning

#### Pattern 1: Project Setup
```python
@when('I set up a "{project_type}" project')
def setup_project(context, project_type):
    vms = _get_project_vms(project_type)
    for vm in vms:
        vde_commands.create_vm(vm)
    context.current_project = project_type
```

#### Pattern 2: Project Switching
```python
@when('I switch to "{project_type}" project')
def switch_project(context, project_type):
    # Stop current VMs
    # Start new project VMs
    context.current_project = project_type
```

#### Pattern 3: Verification
```python
@then('the project should be ready')
def verify_project(context):
    # Check all VMs are running
    # Verify services are accessible
    # Check workspace directories
```

### Phase 3: Implementation

#### Iteration 1: Web Development Setup
1. Create JavaScript VM
2. Configure nginx service
3. Verify project setup

#### Iteration 2: Project Switching
1. Save current project state
2. Stop current VMs
3. Start new project VMs

#### Iteration 3: Advanced Workflows
1. Microservices setup (Go, Rust, nginx)
2. Data science setup (Python, R, Redis)
3. Full stack setup (Python, PostgreSQL, nginx, Redis)

### Phase 4: Validation

1. Run behave tests for multi-project-workflow feature
2. Verify each scenario passes
3. Document any edge cases that need special handling

### Phase 5: Integration Testing

1. Test complete project lifecycle
2. Verify VM isolation between projects
3. Test service connectivity

---

## Remaining Work (Plan 34)

### Task 3.1: Fix VM Pre-creation in environment.py
**Issue**: VMs not created before scenario execution  
**Action**: Update `_SCENARIO_REQUIREMENTS` and `_setup_scenario_environment()`

### Task 3.2: Fix Path Verification
**Issue**: Uses wrong directories (configs/docker vs data/)  
**Action**: Update path references in `multi_project_workflow_steps.py`

### Task 3.3: Implement Missing Project Setups
**Issue**: Web, microservices, data science, full stack, mobile not fully configured  
**Action**: Complete implementation for all project types

---

## References

- [Feature File](tests/features/docker-required/multi-project-workflow.feature)
- [Step Definitions](tests/features/steps/multi_project_workflow_steps.py)
- [Environment Hooks](tests/features/environment.py)
- [Plan 34: Full Remediation](34-test-remediation-plan.md)
