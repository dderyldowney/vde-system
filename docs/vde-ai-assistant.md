# VDE AI Assistant

The VDE AI Assistant provides a natural language interface for controlling your Virtual Development Environment. You can interact with VDE using plain English commands instead of memorizing script names and flags.

[← Back to README](../README.md)

---

## Overview

The VDE AI Assistant includes two modes:

| Mode | Command | Best For |
|------|---------|----------|
| **Command-Line** | `vde-ai` | One-shot commands, scripting |
| **Interactive Chat** | `vde-chat` | Conversational sessions, exploration |

---

## Command-Line Mode

Use `vde-ai` for one-shot natural language commands:

### Listing VMs

```bash
vde-ai "what VMs can I create?"
vde-ai "show all languages"
vde-ai "list services"
```

### Creating VMs

```bash
vde-ai "create a Go VM"
vde-ai "make Python and PostgreSQL"
vde-ai "set up a Rust environment"
```

### Starting VMs

```bash
vde-ai "start Go"
vde-ai "start Python and Rust"
vde-ai "start everything"
vde-ai "launch all languages"
```

### Stopping VMs

```bash
vde-ai "stop Go"
vde-ai "shutdown everything"
vde-ai "kill all services"
```

### Checking Status

```bash
vde-ai "what is running?"
vde-ai "show status"
vde-ai "what's currently running?"
```

### Getting Connection Info

```bash
vde-ai "how do I connect to Python?"
vde-ai "SSH into Go VM"
vde-ai "show connection info for PostgreSQL"
```

### Restarting VMs

```bash
vde-ai "restart Python"
vde-ai "rebuild and start Go"
vde-ai "rebuild everything with no cache"
```

---

## Interactive Chat Mode

Use `vde-chat` for an interactive conversational interface:

```bash
./scripts/vde-chat
```

### Example Session

```
[VDE] → create a Go VM and start it
[AI] → Creating Go VM...
       Starting Go VM...
       Done! Go VM is running.

[VDE] → how do I connect?
[AI] → SSH command: ssh go-dev
       Port: 2200
       Or use VSCode Remote-SSH with host: go-dev

[VDE] → what's running?
[AI] → go-dev
       postgres
       redis

[VDE] → stop everything
[AI] → Stopping all VMs...
       Done!

[VDE] → exit
```

### Special Commands

| Command | Purpose |
|---------|---------|
| `help` | Shows help information |
| `clear` | Clears the screen |
| `history` | Shows your command history in this session |
| `exit` or `quit` | Leaves chat mode |

---

## Options

Both `vde-ai` and `vde-chat` support the following options:

| Option | Purpose |
|--------|---------|
| `--ai` | Enable LLM-based parsing (requires `CLAUDE_API_KEY` or `ANTHROPIC_API_KEY`) |
| `--dry-run` | Show what would happen without executing |
| `--help, -h` | Show help message |

### Examples

```bash
# Dry run - preview actions
./scripts/vde-ai --dry-run "start python"

# Use AI mode (if configured with API key)
./scripts/vde-ai --ai "create a Python VM for web development"

# Show help
./scripts/vde-ai --help
./scripts/vde-chat --help
```

---

## Environment Variables

| Variable | Purpose | Values |
|----------|---------|--------|
| `VDE_USE_AI` | Enable LLM-based parsing by default | `1`, `true`, `yes` |
| `CLAUDE_API_KEY` | Your Claude API key | `sk-ant-...` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | `sk-ant-...` |

### Setting Up AI Mode

```bash
# Add to ~/.zshrc or ~/.bashrc
export VDE_USE_AI="true"
export ANTHROPIC_API_KEY="your-api-key-here"

# Reload shell
source ~/.zshrc
```

---

## Supported Intents

| Intent | Example Commands |
|--------|-----------------|
| **List VMs** | "what VMs can I create?", "show all languages", "list services" |
| **Create VMs** | "create a Go VM", "make Python and PostgreSQL" |
| **Start VMs** | "start Go", "start everything", "launch Python" |
| **Stop VMs** | "stop Go", "shutdown everything" |
| **Restart VMs** | "restart Python", "rebuild and start Go" |
| **Status** | "what is running?", "show status" |
| **Connection Info** | "how do I connect to Python?", "SSH into Go" |
| **Help** | "help", "what can I do?" |

---

## How It Works

The AI Assistant uses pattern-based natural language processing to understand your commands:

1. **Intent Detection**: Identifies what you want to do (create, start, stop, etc.)
2. **Entity Extraction**: Extracts VM names, flags (rebuild, no-cache), and filters
3. **Plan Generation**: Creates an execution plan
4. **Execution**: Calls the appropriate VDE scripts with validated parameters

The pattern-based approach is fast and works offline. For more advanced natural language understanding, you can enable LLM-based parsing with the `--ai` flag.

---

## Examples

### Simple Workflow

```bash
$ vde-ai "create a Go VM and start it"

Creating Go VM...
  - Allocated SSH port: 2200
  - Created: configs/docker/go/docker-compose.yml
  - Created: env-files/go.env
  - Created: projects/go/
  - Created: logs/go/
  - Updated SSH config: Host go-dev on port 2200

Starting Go VM...
  - Building image dev-go:latest...
  - Starting container go-dev...
  - Go VM is running!

SSH connect with: ssh go-dev
```

### Multi-Container Setup

```bash
$ vde-ai "I want to work on a Python API with PostgreSQL"

Creating Python VM...
Creating PostgreSQL VM...
Starting both VMs...

Done! You can now:
  - SSH to Python: ssh python-dev
  - SSH to PostgreSQL: ssh postgres
  - From Python, connect: psql -h postgres -U devuser
```

### Status Queries

```bash
$ vde-ai "what's currently running?"

Running VMs:
  - postgres (port 2400) - Status: running
  - redis (port 2401) - Status: running
  - python-dev (port 2222) - Status: running
```

---

## More Information

For comprehensive documentation, see:
- [VDE-AI-HOWTO.md](./VDE-AI-HOWTO.md) - Complete user guide with examples
- [VDE-AI-Technical-Deep-Dive.md](./VDE-AI-Technical-Deep-Dive.md) - Technical details
- [VDE-PARSER-Technical-Deep-Dive.md](./VDE-PARSER-Technical-Deep-Dive.md) - Parser internals

---

[← Back to README](../README.md)
