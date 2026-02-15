# Specification by Tests: VDE Project Specification Model

## Overview

The VDE project uses **Behavior-Driven Development (BDD)** as the single source of truth for project specifications. The feature tests are not merely verification tools—they are **the authoritative specification document** that defines what the project should do.

---

## Test Suite Statistics

| Metric | Value |
|--------|-------|
| **Total Scenarios** | 324 |
| **Passed** | 258 (79.6%) |
| **Failed** | 65 |
| **Errored** | 1 |
| **Undefined Steps** | 366 (Documentation-only scenarios) |

---

## Implementation Status Dashboard

| Component | Reliability | Pass Rate | Status |
|-----------|-------------|-----------|--------|
| **Core CLI & Parsing** | 🟢 High | 95% | Foundational success; natural language intent detection is stable. |
| **Language/Service Support** | 🟡 Medium | 80% | 19+ languages supported; service VMs (databases) require more depth. |
| **SSH Configuration** | 🟡 Medium | 70% | Agent forwarding works; automated config merging is currently brittle. |
| **Project/Team Workflow** | 🔴 Low | 50% | Shared configs work architecturally but fail in edge-case syncing. |
| **Error Recovery** | 🔴 Low | 40% | Deep recovery scenarios (disk space, network failures) need hardening. |

## The Core Principle

```
Tests → Specification → Code
```

The feature tests come **first**. They define the expected behavior. The implementation code is written to satisfy these tests. This is "Specification by Tests" (also known as Specification-Driven Development).

## How It Works

### 1. Feature Files Define Requirements

Feature files (`.feature`) in Gherkin syntax describe user stories and scenarios:

```gherkin
Feature: Natural Language Parser
  As a developer
  I want to control VDE using natural language commands
  So that I don't need to remember specific command syntax

  Scenario: Detect list VMs intent
    When I parse "list all vms"
    Then intent should be "list_vms"
```

Each scenario is a **concrete requirement** that must be satisfied.

### 2. Step Definitions Implement the Verification

Step definitions (Python) connect scenarios to actual verification:

```python
@when('I parse "{text}"')
def step_parse_command(context, text):
    context.result = parse_natural_language(text)

@then('intent should be "{expected}"')
def step_verify_intent(context, expected):
    assert context.result['intent'] == expected
```

### 3. Passing Tests Generate Documentation

The [`generate_user_guide.py`](tests/scripts/generate_user_guide.py:1) script reads Behave JSON output and generates [`USER_GUIDE.md`](USER_GUIDE.md:1) from **only passing scenarios**:

```python
"""
Generate USER_GUIDE.md from PASSING BDD test scenarios only.

This script:
1. Reads Behave JSON output to identify which scenarios passed
2. Generates user guide with ONLY passing scenarios
3. Ensures all examples in the guide are actually verified to work
"""
```

This creates a powerful feedback loop:
- **What works** → Appears in user guide
- **What doesn't work** → Not documented until fixed

## Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Docker-Free | [`features/docker-free/`](tests/features/docker-free/) | Parser logic, shell compatibility, workflows without Docker |
| Docker-Required | [`features/docker-required/`](tests/features/docker-required/) | VM lifecycle, SSH, Docker operations |

## Key Feature Files as Specification

### Core Features (Docker-Free)

| Feature File | Purpose | Test Count | Status |
|--------------|---------|------------|--------|
| [`natural-language-parser.feature`](tests/features/docker-free/natural-language-parser.feature) | Intent detection, entity extraction, alias resolution | 50+ | 🟢 Implemented |
| [`cache-system.feature`](tests/features/docker-free/cache-system.feature) | VM type metadata caching and port registry persistence | 20+ | 🟢 Implemented |
| [`shell-compatibility.feature`](tests/features/docker-free/shell-compatibility.feature) | Native zsh support with associative arrays | 30+ | 🟢 Implemented |
| [`vm-information-and-discovery.feature`](tests/features/docker-free/vm-information-and-discovery.feature) | Listing available VMs, filtering by type | 10+ | 🟢 Implemented |
| [`vde-ssh-commands.feature`](tests/features/docker-free/vde-ssh-commands.feature) | SSH setup and management commands | 10+ | 🟡 Partial |
| [`error-path-testing.feature`](tests/features/docker-free/error-path-testing.feature) | Error handling for invalid inputs | 10+ | 🟡 Partial |
| [`documented-development-workflows.feature`](tests/features/docker-free/documented-development-workflows.feature) | Daily workflow scenarios from documentation | 40+ | 🟡 Partial |
| [`vm-metadata-verification.feature`](tests/features/docker-free/vm-metadata-verification.feature) | VM type metadata validation | 15+ | 🟢 Implemented |

### Docker-Required Features

| Feature File | Purpose | Test Count | Status |
|--------------|---------|------------|--------|
| [`vm-lifecycle.feature`](tests/features/docker-required/vm-lifecycle.feature) | VM creation, start, stop, restart, removal | 25+ | 🟡 Partial |
| [`port-management.feature`](tests/features/docker-required/port-management.feature) | Port allocation, collision detection, registry | 15+ | 🟡 Partial |
| [`ssh-configuration.feature`](tests/features/docker-required/ssh-configuration.feature) | SSH agent setup, key generation, config merging | 45+ | 🟡 Partial |
| [`docker-operations.feature`](tests/features/docker-required/docker-operations.feature) | Docker Compose operations, build, up, down | 20+ | 🟡 Partial |
| [`error-handling-and-recovery.feature`](tests/features/docker-required/error-handling-and-recovery.feature) | Error handling, recovery, graceful degradation | 20+ | 🔴 Needs Work |
| [`daily-development-workflow.feature`](tests/features/docker-required/daily-development-workflow.feature) | Morning setup, status check, cleanup | 10+ | 🟡 Partial |
| [`template-system.feature`](tests/features/docker-required/template-system.feature) | VM configuration generation from templates | 15+ | 🟡 Partial |
| [`productivity-features.feature`](tests/features/docker-required/productivity-features.feature) | Data persistence, backups, service management | 5+ | 🟡 Partial |
| [`team-collaboration-and-maintenance.feature`](tests/features/docker-required/team-collaboration-and-maintenance.feature) | Team workflows, shared configs, maintenance | 15+ | 🔴 Needs Work |
| [`debugging-troubleshooting.feature`](tests/features/docker-required/debugging-troubleshooting.feature) | Diagnostics, logs, recovery | 20+ | 🔴 Needs Work |
| [`ssh-agent-automatic-setup.feature`](tests/features/docker-required/ssh-agent-automatic-setup.feature) | SSH agent auto-start, key management | 10+ | 🟡 Partial |
| [`ssh-agent-forwarding-vm-to-vm.feature`](tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature) | VM-to-VM SSH with agent forwarding | 10+ | 🟡 Partial |
| [`ssh-agent-vm-to-host-communication.feature`](tests/features/docker-required/ssh-agent-vm-to-host-communication.feature) | VM-to-Host communication | 5+ | 🟡 Partial |
| [`ssh-agent-external-git-operations.feature`](tests/features/docker-required/ssh-agent-external-git-operations.feature) | Git operations from VMs | 5+ | 🔴 Needs Work |

---

## Detailed Feature Specifications

### 1. Natural Language Parser

**Feature:** [`natural-language-parser.feature`](tests/features/docker-free/natural-language-parser.feature)

**The Need:** Users should be able to control VDE using natural language commands like "start the python VM" instead of memorizing specific command syntax.

**Implemented Capabilities:**
- Intent detection for: list_vms, create_vm, start_vm, stop_vm, restart_vm, status, connect, help
- Entity extraction: VM names, filters (lang/svc), flags (rebuild, nocache)
- Alias resolution: "nodejs" → "js", "python3" → "python", etc.
- Security: Injection attempt handling for shell metacharacters

**Status:** 🟢 HIGH RELIABILITY (95% pass rate)

**Top Verified Scenarios:**
- Detect create multiple VMs intent: Parser correctly identifies "create python and rust"
- Resolve VM aliases: Successfully maps "nodejs" to canonical "js"
- Use native associative arrays in zsh: Confirmed zero-dependency shell state management

---

### 2. Cache System

**Feature:** [`cache-system.feature`](tests/features/docker-free/cache-system.feature)

**The Need:** VM type data should be cached for performance so scripts don't reparse configuration on every invocation.

**Implemented Capabilities:**
- VM type metadata caching (.cache/vm-types.cache)
- Port registry persistence (.cache/port-registry)
- Cache invalidation on config modification
- Lazy loading on first access

**Status:** 🟢 HIGH RELIABILITY (100% pass rate)

**Top Verified Scenarios:**
- Cache file should be created at ".cache/vm-types.cache": Verified high-speed metadata access
- Cache invalidates when config is modified: Ensures data freshness

---

### 3. Shell Compatibility

**Feature:** [`shell-compatibility.feature`](tests/features/docker-free/shell-compatibility.feature)

**The Need:** VDE should work natively in zsh with consistent shell behavior using associative arrays.

**Implemented Capabilities:**
- Native zsh associative array support (typeset -gA)
- Script path detection
- Storage cleanup on exit
- Special character handling in keys

**Status:** 🟢 HIGH RELIABILITY (100% pass rate)

---

### 4. VM Lifecycle Management

**Feature:** [`vm-lifecycle.feature`](tests/features/docker-required/vm-lifecycle.feature)

**The Need:** Users should be able to create, start, stop, restart, and manage development VMs.

**Implemented Capabilities:**
- Create language VMs (docker-compose.yml generation)
- Create service VMs with custom ports
- Start/stop individual and multiple VMs
- Start all VMs with "start-virtual all"
- Rebuild with --rebuild flag
- Remove VM instances
- Add new VM types dynamically

**Status:** 🟡 MEDIUM RELIABILITY (80% pass rate)

**Issue Examples:**
- Configure VM with multiple service ports: Assertion failure on docker-compose.yml location/parsing
- Service port configuration: Failed connectivity to PostgreSQL on external port 2400
- Data persistence for services: Verification logic inconsistent

---

### 5. SSH Configuration

**Feature:** [`ssh-configuration.feature`](tests/features/docker-required/ssh-configuration.feature)

**The Need:** VDE should provide automatic SSH agent forwarding and key management for seamless VM access.

**Implemented Capabilities:**
- SSH agent auto-start if not running
- SSH key generation (ed25519 preferred)
- SSH config entry generation for new VMs
- VM-to-VM SSH config entries
- Backup before modification
- Known hosts cleanup

**Status:** 🟡 MEDIUM RELIABILITY (70% pass rate)

**Issue Examples:**
- SSH config merging is currently brittle
- Multi-developer synchronization fails in edge cases
- Atomic merge prevents corruption if interrupted: Implementation needs hardening

---

### 6. Port Management

**Feature:** [`port-management.feature`](tests/features/docker-required/port-management.feature)

**The Need:** VDE should automatically allocate and manage SSH ports to avoid conflicts.

**Implemented Capabilities:**
- Sequential port allocation (2200-2299 for languages, 2400-2499 for services)
- Port registry persistence
- Host port collision detection
- Atomic port reservation

**Status:** 🟡 MEDIUM RELIABILITY

**Issue Examples:**
- VDE handles port conflicts gracefully: Failed to re-allocate from 2200 to 2201 when host port occupied

---

### 7. Error Handling and Recovery

**Feature:** [`error-handling-and-recovery.feature`](tests/features/docker-required/error-handling-and-recovery.feature)

**The Need:** The system should handle errors gracefully with clear messages and recovery options.

**Implemented Capabilities:**
- Invalid VM name handling with suggestions
- Port conflict resolution
- Docker daemon availability check
- Configuration file error detection

**Status:** 🔴 LOW RELIABILITY (40% pass rate)

**Issue Examples:**
- Invalid VM name handling: Error messages lack documented "Solution" and "Suggestions" content
- Insufficient disk space: Warning mechanism failed to trigger
- SSH connection failure: SSH port accessibility check times out on valid running containers

---

### 8. Docker Operations

**Feature:** [`docker-operations.feature`](tests/features/docker-required/docker-operations.feature)

**The Need:** Reliable Docker Compose operations with proper error handling.

**Implemented Capabilities:**
- docker-compose build
- docker-compose up -d
- docker-compose down
- --build flag for rebuild
- --no-cache flag for clean rebuild
- Container status detection
- Volume mounts
- Environment variable passing

**Status:** 🟡 MEDIUM RELIABILITY

---

### 9. Daily Development Workflow

**Feature:** [`daily-development-workflow.feature`](tests/features/docker-required/daily-development-workflow.feature)

**The Need:** Users should be able to efficiently manage development containers for daily work.

**Implemented Scenarios:**
- Starting development environment
- Checking what's running
- Getting connection information
- Stopping work for the day
- Restarting with rebuild
- Starting multiple VMs (full stack)
- Creating a new VM for the first time

**Status:** 🟡 MEDIUM RELIABILITY

**Issue Examples:**
- Connect to PostgreSQL from Python VM: Inter-container network resolution ("vde-net") is unreliable
- Mobile development with backend: Failure to coordinate multi-container startup (Flutter + Postgres)

---

### 10. Template System

**Feature:** [`template-system.feature`](tests/features/docker-required/template-system.feature)

**The Need:** VM configurations should be generated from templates for consistency.

**Implemented Capabilities:**
- Language VM template rendering
- Service VM template rendering
- Multiple service ports handling
- SSH agent forwarding configuration
- Network configuration (vde-net)
- Restart policy (unless-stopped)
- User configuration (devuser:1000)

**Status:** 🟡 MEDIUM RELIABILITY

---

### 11. Team Collaboration

**Feature:** [`team-collaboration-and-maintenance.feature`](tests/features/docker-required/team-collaboration-and-maintenance.feature)

**The Need:** Teams should be able to maintain and share development environments.

**Implemented Scenarios:**
- Rebuilding after system updates
- Troubleshooting problematic VMs
- Checking system status
- Adding new languages to team
- Sharing SSH configurations
- Batch operations for efficiency

**Status:** 🔴 LOW RELIABILITY (50% pass rate)

**Issue Examples:**
- Shared configs work architecturally but fail in edge-case syncing
- Switch from Python to Rust project: Simultaneous SSH access to multiple VMs fails

---

### 12. Debugging and Troubleshooting

**Feature:** [`debugging-troubleshooting.feature`](tests/features/docker-required/debugging-troubleshooting.feature)

**The Need:** Users should have tools to diagnose and fix VM issues.

**Implemented Scenarios:**
- View VM logs for debugging
- Access VM shell for debugging
- Rebuild VM from scratch
- Check port usage
- Verify SSH connection
- Test database connectivity
- Inspect docker-compose configuration
- Verify volumes
- Clear Docker cache
- Reset to initial state
- Verify network connectivity
- Check resource usage
- Validate configuration
- Recover from Docker daemon issues
- Fix permission issues

**Status:** 🔴 LOW RELIABILITY (Deferred - needs implementation updates)

## Workflow: Adding New Features

1. **Write the feature file first** (the specification)
2. **Run tests** - they will fail (no implementation)
3. **Implement the code** to make tests pass
4. **Update documentation** - the passing tests auto-generate user docs

## Verification Chain

```
Feature File (Specification)
        ↓
Step Definitions (Verification)
        ↓
Code Implementation (Satisfies Tests)
        ↓
Passing Tests → User Guide (Documentation)
```

## Running the Tests

```bash
# Run all feature tests
cd tests && behave

# Run specific category
behave tests/features/docker-free/
behave tests/features/docker-required/

# Generate user guide from passing tests
python3 tests/scripts/generate_user_guide.py
```

## Tags and Organization

Feature scenarios use tags for organization:

| Tag | Meaning |
|-----|---------|
| `@wip` | Work in progress (excluded from default runs) |
| `@user-guide-*` | Include in user guide generation |
| `@requires-docker-host` | Requires Docker running |
| `@docker-free` | Runs without Docker |

---

## Supported Intents

The parser recognizes 9 distinct intents:

| Intent | Purpose | Example Commands |
|--------|---------|------------------|
| `list_vms` | List available VMs | "what VMs can I create?", "show languages" |
| `create_vm` | Create new VMs | "create a Go VM", "make Python and PostgreSQL" |
| `start_vm` | Start VMs | "start Go", "launch everything" |
| `stop_vm` | Stop VMs | "stop Go", "shutdown everything" |
| `restart_vm` | Restart VMs | "restart Python", "rebuild and start Go" |
| `status` | Show running status | "what's running?", "show status" |
| `connect` | Get SSH connection info | "how do I connect to Python?", "SSH into Go" |
| `add_vm_type` | Add new VM types | "add a new language called Zig" |
| `help` | Show help | "help", "what can I do?" |

---

## Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Docker-Free | [`features/docker-free/`](tests/features/docker-free/) | Parser logic, shell compatibility, workflows without Docker |
| Docker-Required | [`features/docker-required/`](tests/features/docker-required/) | VM lifecycle, SSH, Docker operations |

### Tags and Organization

Feature scenarios use tags for organization:

| Tag | Meaning |
|-----|---------|
| `@wip` | Work in progress (excluded from default runs) |
| `@user-guide-*` | Include in user guide generation |
| `@requires-docker-host` | Requires Docker running |
| `@docker-free` | Runs without Docker |
| `@requires-ssh-agent` | Requires SSH agent |
| `@requires-docker-ssh` | Requires Docker and SSH |

---

## Roadmap: Next Steps

Based on the current test results, the following areas need attention:

### Priority 1: Error Path Hardening
- Implement proper error messages with "Solution" and "Suggestions" content
- Add disk space detection and warning mechanism
- Fix SSH port accessibility check timeouts
- Implement graceful degradation for partial failures

### Priority 2: SSH Configuration Stability
- Refactor SSH config merging to handle multi-developer synchronization
- Implement atomic merge with proper file locking
- Add comprehensive backup/restore for SSH configs

### Priority 3: Multi-VM Integration
- Fix inter-container network resolution ("vde-net")
- Coordinate multi-container startup (Flutter + Postgres)
- Implement simultaneous SSH access to multiple VMs

### Priority 4: Team Collaboration
- Implement shared configuration patterns
- Add team sync functionality
- Complete debugging/troubleshooting tools

---

## Summary

In the VDE project:

1. **Feature tests ARE the specification** - they define what the system must do
2. **Passing tests become documentation** - the user guide is generated from passing scenarios
3. **Code satisfies tests** - implementation is driven by test requirements
4. **No passing test means no feature** - if it's not tested, it's not in the spec

This approach ensures:
- **Accuracy**: Documentation matches actual behavior (only passing tests are documented)
- **Completeness**: Every documented feature has test coverage
- **Maintainability**: Tests and specs are always in sync

---

## Appendix: Implementation Libraries

The following libraries implement the specification:

| Library | Purpose | Status |
|---------|---------|--------|
| [`vde-parser`](../scripts/lib/vde-parser) | Natural language command parsing | 🟢 Implemented |
| [`vm-common`](../scripts/lib/vm-common) | Core VM operations | 🟢 Implemented |
| [`vde-commands`](../scripts/lib/vde-commands) | Command wrappers | 🟢 Implemented |
| [`vde-ssh`](../scripts/lib/vde-ssh) | SSH management | 🟡 Partial |
| [`vde-docker`](../scripts/lib/vde-docker) | Docker operations | 🟡 Partial |
| [`vde-templates`](../scripts/lib/vde-templates) | Template rendering | 🟡 Partial |
| [`vde-errors`](../scripts/lib/vde-errors) | Error handling | 🟡 Partial |
| [`vde-log`](../scripts/lib/vde-log) | Logging utilities | 🟢 Implemented |
| [`vde-health`](../scripts/lib/vde-health) | Health checks | 🟡 Partial |
| [`vde-audit`](../scripts/lib/vde-audit) | Audit trails | 🔴 Needs Work |
| [`vde-metrics`](../scripts/lib/vde-metrics) | Performance monitoring | 🔴 Needs Work |
