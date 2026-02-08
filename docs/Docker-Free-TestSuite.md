# Docker-Free Test Suite: Technical Summary of VDE

The **docker-free** test suite (146 passing scenarios) validates VDE's core infrastructure without requiring Docker containers. It confirms the following technical foundations:

## Test Coverage Overview

| Feature | Scenarios | Status |
|---------|-----------|--------|
| Cache System | 18 | ✅ Passing |
| Natural Language Parser | 46 | ✅ Passing |
| Shell Compatibility | 26 | ✅ Passing |
| VM Information & Discovery | 5 | ✅ Passing |
| VM Metadata Verification | 12 | ✅ Passing |
| Documented Development Workflows | 22 | ✅ Passing |
| VDE SSH Commands | 17 | ✅ Passing |

## 1. Shell Architecture

VDE is designed as a **zsh-first** orchestration system:

- **Native zsh features**: Uses `typeset -A` for associative arrays, process substitution `()`, and shell detection via `$_` or `$0`
- **Shell compatibility layer**: [`scripts/lib/vde-shell-compat`](scripts/lib/vde-shell-compat) abstracts shell differences for cross-shell support
- **Unicode & special character handling**: Keys/values support `/`, `:`, `-`, spaces, emojis, and newlines via hex encoding
- **Key patterns**: `[[` for string comparisons, `local` for function-scoped variables, exit codes 0/success, non-zero/failure

### Key Libraries

| Library | Purpose |
|---------|---------|
| `vde-shell-compat` | Portable shell operations (zsh/bash compatibility) |
| `vde-constants` | Centralized constants (return codes, port ranges, timeouts) |
| `vde-core` | Essential VDE functions (VM types, queries, caching) |
| `vm-common` | Full VDE functionality (VM types, ports, Docker, SSH, templates) |

## 2. Caching System

VDE implements a **file-based cache** for performance optimization:

### Cache Files

| Cache File | Location | Purpose |
|------------|----------|---------|
| VM Types Cache | `.cache/vm-types.cache` | Stores parsed VM_TYPE, VM_ALIASES, VM_DISPLAY, VM_INSTALL, VM_SVC_PORT arrays |
| Port Registry | `.cache/port-registry` | Persists port allocations (2200-2299 for lang, 2400-2499 for services) |

### Cache Invalidation Strategies

1. **mtime-based**: Cache invalid when `vm-types.conf` modified time > cache mtime
2. **Programmatic**: [`invalidate_vm_types_cache()`](scripts/lib/vde-core) removes cache file and resets `_VM_TYPES_LOADED` flag
3. **Manual**: `--no-cache` flag bypasses cache entirely
4. **Lazy loading**: VM types loaded only on first access, not during library sourcing

### Cache Format

```
ARRAY_NAME:key=value
# Comments preserved
```

## 3. Natural Language Parser

VDE's NLP enables **natural language command parsing** with intent detection:

### Supported Intents (9 Total)

| Intent | Example Phrases |
|--------|-----------------|
| `list_vms` | "list all vms", "show all language vms", "what services are available" |
| `create_vm` | "create a go vm", "create python and rust" |
| `start_vm` | "start the python vm", "start python, rust, and go", "start everything" |
| `stop_vm` | "stop the postgres container", "shutdown all vms" |
| `restart_vm` | "restart python", "rebuild and start rust", "rebuild python with no cache" |
| `status` | "what's currently running", "show status of python and rust" |
| `connect` | "how do I connect to python" |
| `add_vm_type` | "add new vm type" |
| `help` | "help", "what can I do" |

### Entity Extraction

- **VM names**: `python`, `rust`, `go`, `js` (and aliases like `py`→`python`)
- **Filters**: `lang` (languages only), `svc` (services only)
- **Flags**: `--rebuild`, `--no-cache`

### Security Features

- Rejects empty/whitespace-only input
- Handles injection attempts (`; rm -rf`, `&`, `"`) gracefully
- Validates plan lines with `INTENT:` and `VM:` prefixes

## 4. VM Type System

### VM Inventory

| Category | Count | Port Range |
|----------|-------|------------|
| Language VMs | 20 | 2200-2299 |
| Service VMs | 7 | 2400-2499 |

### Language VMs

`c`, `cpp`, `asm`, `python`, `rust`, `js`, `csharp`, `ruby`, `go`, `java`, `kotlin`, `swift`, `php`, `scala`, `r`, `lua`, `flutter`, `elixir`, `haskell`, `zig`

### Service VMs

`postgres`, `redis`, `mongodb`, `nginx`, `mysql`, `rabbitmq`, `couchdb`

### Configuration Source

Defined in [`scripts/data/vm-types.conf`](scripts/data/vm-types.conf) using **pipe-delimited format**:
```
VM_TYPE:language:python|Python 3.x|python3 install|2222
VM_ALIASES:python=py=python3
VM_SVC_PORT:postgres=5432
```

## 5. Test Suite Validation Status

### ✅ Production-Ready Features

- Core shell scripts and zsh compatibility
- Cache invalidation and mtime comparison logic
- Natural language intent detection and entity extraction
- VM metadata and port registry management
- Development workflows and SSH command interfaces

### ⏳ Work-In-Progress (@wip)

- SSH agent forwarding for external Git operations
- Docker container lifecycle management
- Full integration testing with running containers

## 6. Running the Tests

```bash
# Run all docker-free tests
./tests/run-docker-free-tests.zsh

# Run specific feature tests
behave tests/features/docker-free/cache-system.feature
behave tests/features/docker-free/natural-language-parser.feature
behave tests/features/docker-free/shell-compatibility.feature

# Run with verbose output
behave --format pretty tests/features/docker-free/
```

## 7. Conclusion

The docker-free test suite passing (146/146 scenarios) confirms that VDE's **core infrastructure is production-ready**:

1. **Shell architecture** is stable with proper zsh compatibility
2. **Caching system** correctly handles mtime invalidation and lazy loading
3. **NLP parser** accurately detects 9 intents and extracts VM entities
4. **VM type system** properly manages 27 VM types with port allocation

Only Docker-dependent features remain marked @wip, indicating the test suite is in harmony with the project's developmental state.
