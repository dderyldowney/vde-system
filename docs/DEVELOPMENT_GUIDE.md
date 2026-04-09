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

### Libraries (lib/)

| Library | Purpose |
|---------|---------|
| **vde-constants** | Centralized constants (return codes, port ranges, timeouts) |
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
- **Service VMs (7 total)**: Ports 2400-2499 (postgres, redis, mongodb, nginx, mysql, rabbitmq, couchdb)
- **Port Registry**: `.cache/port-registry` for fast port lookups

### Command Parser Architecture
- **9 supported intents**: list_vms, create_vm, start_vm, stop_vm, restart_vm, status, connect, add_vm_type, help
- **Data-driven VM types**: `data/vm-types.conf` (pipe-delimited format)

## Testing

- **BDD Framework**: Behave (Python) for behavior-driven testing
- **Test Location**: `tests/features/`
- **Test Categories**:
  - Docker-free tests (no container dependencies) — `tests/features/docker-free/`
  - Docker-required tests (full integration tests) — `tests/features/docker-required/`
- **Test Execution**: `./run-tests.zsh` for all tests, `./run-vde-parser-tests.zsh` for parser tests

### Test Commands
```zsh
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


---

## Development Workflows

Example workflows for common development scenarios with VDE.

[← Back to README](../README.md)

---

### Example 1: Python API with PostgreSQL

A full-stack Python API with PostgreSQL database.

```zsh
## 1. Create Python VM
vde create python

## 2. Create PostgreSQL VM
vde create postgres

## 3. Start both VMs
vde start python postgres

## 4. Connect to Python VM
ssh vde-python

## 5. Set up project
cd ~/workspace
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn psycopg2-binary

## 6. Test database connection
ssh postgres
createdb testdb
exit

psql -h postgres -U devuser -d testdb

## 7. Run your API
uvicorn main:app --reload
```

---

### Example 2: Full-Stack JavaScript with Redis

Node.js/Express application with Redis caching.

```zsh
## 1. Create VMs
vde create js
vde create redis

## 2. Start VMs
vde start js redis

## 3. Connect to JS VM
ssh vde-js

## 4. Set up Express app
cd ~/workspace
npm init -y
npm install express redis

## 5. Create app
cat > app.js << 'EOF'
const express = require('express');
const redis = require('redis');
const app = express();

const client = redis.createClient({
  host: 'redis',
  port: 6379
});

app.get('/', (req, res) => {
  res.send('Hello from VDE!');
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
EOF

## 6. Run app
node app.js
```

---

### Example 3: Microservices with Multiple Languages

A microservices architecture using different languages for each service.

```zsh
## 1. Create VMs for each service
vde create python   # API Gateway
vde create go       # Payment Service
vde create rust     # Analytics Service
vde create postgres # Database
vde create redis    # Cache

## 2. Start all VMs
vde start python go rust postgres redis

## 3. Each service runs in its own VM
## Python: ssh vde-python
## Go: ssh vde-go
## Rust: ssh vde-rust

## 4. Services communicate via Docker network
## vde-python can access: postgres, redis
## vde-go can access: postgres, redis
## etc.
```

---

### Daily Workflow

#### Morning Setup

```zsh
## Start your development environments
vde start python postgres redis
```

#### During Development

```zsh
## Check what's running
docker ps

## Connect to your primary VM
ssh vde-python

## Work in the container
cd ~/workspace
## ... do work ...
```

#### Evening Cleanup

```zsh
## Stop everything to save resources
vde stop all
```

---

### Troubleshooting Workflow

When something isn't working:

```zsh
## 1. Check container status
vde status

## 2. Check container logs
docker logs vde-python

## 3. Restart with rebuild
vde start python --rebuild

## 4. Connect and debug
ssh vde-python
## ... investigate inside container ...
```

---

[← Back to README](../README.md)


