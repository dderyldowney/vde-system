# VDE (Virtual Development Environment)

VDE is a Docker-based container orchestration system for managing 20+ language VMs and 7+ service VMs. It provides a unified interface for creating, starting, stopping, and managing development environments with features like SSH agent forwarding, natural language command parsing, and template-based configuration generation.

## Code Style

- **All shell scripts must use zsh** (`#!/usr/bin/env zsh` or `#!/bin/zsh`)
  - Zsh version: 5.0 or later required
  - `/bin/sh` and `/usr/bin/env sh` are strictly forbidden
- **Indentation**: 2 spaces (no tabs)
- **Line length**: Maximum 120 characters (soft limit)
- **Trailing whitespace**: Never include trailing whitespace
- **Final newline**: Every file must end in a newline

### Naming Conventions
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`
- **Local variables**: `lower_case_with_underscores`
- **Environment variables**: `UPPER_CASE_WITH_UNDERSCORES`
- **Private variables/functions**: Prefix with `_` (e.g., `_private_var`, `_helper_function`)
- **Public functions**: `lower_case_with_underscores`

### Key Patterns
- **Always quote variables**: `"$VAR"` not `$VAR`
- **Use `[[`** for string comparisons (not `[` or `((`)
- **Always use `local`** for function-scoped variables
- **Return exit codes**: 0 for success, non-zero for failure
- **Print to stdout for data, stderr for errors

## Architecture

VDE uses a modular library architecture that separates concerns and enables code reuse:

### Libraries (scripts/lib/)

| Library | Purpose |
|---------|---------|
| **vde-constants** | Centralized constants (return codes, port ranges, timeouts) |
| **vde-shell-compat** | Portable shell operations (zsh/bash compatibility) |
| **vde-errors** | Error messages with remediation steps |
| **vde-log** | Structured logging with rotation (JSON/text/syslog) |
| **vde-core** | Essential VDE functions (VM types, queries, caching) |
| **vm-common** | Full VDE functionality (VM types, ports, Docker, SSH, templates) |
| **vde-commands** | Safe wrapper functions for VDE operations |
| **vde-parser** | Pattern-based natural language parser (intent detection, entity extraction) |
| **vde-naming** | VM naming conventions and validation |
| **vde-progress** | Progress bars and status indicators |
| **vde-audit** | VM audit trails and change tracking |
| **vde-metrics** | Performance metrics and monitoring |
| **vde-health** | Health checks and system status |
| **vde-path-utils** | Path manipulation utilities |

### VM Architecture
- **Language VMs (20 total)**: Ports 2200-2299 (c, cpp, asm, python, rust, js, csharp, ruby, go, java, kotlin, swift, php, scala, r, lua, flutter, elixir, haskell, zig)
- **Service VMs (7 total)**: Ports 2400-2499 (postgres, redis, mongodb, nginx, mysql, rabbitmq, couchdb)
- **Port Registry**: `.cache/port-registry` for fast port lookups

### Command Parser Architecture
- **9 supported intents**: list_vms, create_vm, start_vm, stop_vm, restart_vm, status, connect, add_vm_type, help
- **Data-driven VM types**: `scripts/data/vm-types.conf` (pipe-delimited format)

## Testing

- **BDD Framework**: Behave (Python) for behavior-driven testing
- **Test Location**: `tests/features/`
- **Test Categories**:
  - Docker-free tests (no container dependencies) — `tests/features/docker-free/`
  - Docker-required tests (full integration tests) — `tests/features/docker-required/`
- **Test Execution**: `./run-tests.zsh` for all tests, `./run-vde-parser-tests.zsh` for parser tests

### Test Commands
```bash
./run-tests.zsh              # Run all tests
./run-vde-parser-tests.zsh   # Run parser-specific tests
behave tests/features/       # Run BDD tests directly
```

## Security

- **SSH Agent Forwarding**: Private keys NEVER leave the host; only authentication socket is forwarded (read-only mount)
- **SSH Key Management**: All keys detected and loaded automatically; public keys synced to `public-ssh-keys/`
- **Validation**: All user inputs validated before execution; VM names validated for format
- **No secrets in code**: API keys, credentials, and secrets must never be committed
- **Parameter expansion**: Use parameterized queries for any external system interactions
- **Error handling**: Provide meaningful error messages with remediation steps via `vde-errors` library
