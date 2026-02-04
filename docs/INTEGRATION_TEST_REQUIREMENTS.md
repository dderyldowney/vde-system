# Integration Test Requirements - Phase 1.3

## Overview
Integration tests require full Docker infrastructure to run. These tests verify actual VM lifecycle operations (create, start, stop, restart) with real containers.

## Test Categories

### 1. Docker-Required Tests (Can Run with Docker)
These tests require Docker daemon but not full VDE VM infrastructure:

| Feature | Scenarios | Requirements |
|---------|-----------|--------------|
| docker-operations | 14 | Docker daemon, compose files |
| daily-workflow | TBD | Docker + running VMs |
| ssh-agent-forwarding | TBD | Docker + SSH keys |

### 2. Full Integration Tests (Need Complete Infrastructure)
These tests require full VDE setup with all services running:

| Feature | Scenarios | Requirements |
|---------|-----------|--------------|
| collaboration-workflow | TBD | Multiple VMs running |
| multi-project-workflow | TBD | Multiple VMs, data persistence |
| team-collaboration | TBD | User management, config sharing |

## Infrastructure Requirements

### Minimum (Docker-Required)
- Docker daemon running
- Docker Compose v2+
- VDE scripts sourced

### Full Integration
- All above PLUS:
- All 27 VM configurations (20 languages + 7 services)
- Port ranges 2200-2299, 2400-2499 available
- Data directories (postgres, redis, mongodb, etc.)

## Tagged Tests

### @requires-docker-host (147 scenarios)
Tests marked with `@requires-docker-host` require:
- Running Docker daemon
- Network access to Docker
- Sufficient permissions (socket access)

### @integration (Pending Tagging)
Tests requiring full VDE infrastructure to be tagged.

## Test Execution

### Docker-Required Only
```bash
behave tests/features/docker-required/ --tags=@requires-docker-host
```

### All Integration Tests (when infrastructure ready)
```bash
behave tests/features/ --tags=@integration
```

## Current Status

| Category | Count | Notes |
|----------|-------|-------|
| docker-free (no infra) | 146 scenarios | ALL PASSING |
| docker-required | 14 scenarios | ALL PASSING |
| Undefined steps | 899 | Need step definitions |
| Integration tests | TBD | Need infrastructure |
