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
| `ANTHROPIC_AUTH_TOKEN` | Your Anthropic authentication token (highest priority) | `sk-ant-...` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | `sk-ant-...` |
| `CLAUDE_API_KEY` | Your Claude API key (legacy) | `sk-ant-...` |
| `ANTHROPIC_BASE_URL` | Custom base URL for Anthropic API (optional) | `https://...` |
| `ANTHROPIC_MODEL` | Custom model to use (optional) | `claude-3-5-sonnet-20241022`, `glm-4.7`, etc. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Default model for Anthropic-compatible APIs (optional) | `glm-4.7`, etc. |

### API Key Priority

The system checks for authentication in this order:
1. `ANTHROPIC_AUTH_TOKEN` (highest priority - recommended)
2. `ANTHROPIC_API_KEY`
3. `CLAUDE_API_KEY` (legacy support)

### Setting Up AI Mode

```bash
# Add to ~/.zshrc or ~/.bashrc
export VDE_USE_AI="true"
export ANTHROPIC_AUTH_TOKEN="your-api-key-here"

# Optional: Use a custom base URL (for proxies or alternative endpoints)
# export ANTHROPIC_BASE_URL="https://your-proxy.example.com/v1"

# Optional: Use a specific model
# export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"

# Reload shell
source ~/.zshrc
```

### Custom Base URL Use Cases

The `ANTHROPIC_BASE_URL` option is useful for:

- **Corporate Proxies**: Route API requests through your organization's proxy
- **Alternative Endpoints**: Use compatible API endpoints or gateways
- **Local Development**: Test with local mock servers or API simulators
- **Third-Party Providers**: Use Anthropic-compatible API providers

```bash
# Example: Using a corporate proxy
export ANTHROPIC_BASE_URL="https://api-gateway.internal.company.com/anthropic/v1"

# Example: Using Zhipu AI's Anthropic-compatible API
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_MODEL="glm-4.7"

# Example: Using a custom API gateway
export ANTHROPIC_BASE_URL="https://my-gateway.example.com/anthropic"
```

### Model Selection

The `ANTHROPIC_MODEL` and `ANTHROPIC_DEFAULT_SONNET_MODEL` options allow you to specify which model to use:

```bash
# Use Claude Sonnet (default)
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"

# Use Claude Haiku for faster responses
export ANTHROPIC_MODEL="claude-3-5-haiku-20241022"

# Use Claude Opus for more complex reasoning
export ANTHROPIC_MODEL="claude-3-opus-20240229"

# Use Zhipu AI's GLM model with Anthropic-compatible API
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.7"

# Or specify the model directly
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_MODEL="glm-4.7"
```

### Third-Party API Providers

VDE AI Assistant supports Anthropic-compatible APIs from third-party providers:

**Zhipu AI (GLM Models)**

```bash
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.7"
export ANTHROPIC_AUTH_TOKEN="your-zhipu-api-key"
```

This allows you to use alternative models while maintaining the same VDE AI interface.

### How AI API Calling Works

When AI mode is enabled (via `--ai` flag or `VDE_USE_AI=1`), the VDE AI Assistant:

1. **Checks for API availability**: Verifies that `vde-ai-api` library exists and API key is set
2. **Makes API request**: Sends your natural language command to the configured API endpoint
3. **Parses structured response**: Extracts the execution plan from the AI response
4. **Executes the plan**: Runs the parsed commands through VDE's execution engine
5. **Falls back gracefully**: If API calling fails, falls back to pattern-based parsing

**API Request Format:**

The system sends a structured request to the Anthropic Messages API:

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 1024,
  "system": "You are a command parser for VDE...",
  "messages": [
    {
      "role": "user",
      "content": "your natural language command"
    }
  ]
}
```

**Response Format:**

The AI returns a structured execution plan:

```
INTENT:start_vm
VM:python postgres
FLAGS:rebuild=false nocache=false
```

**Error Handling:**

- **No API key**: Falls back to pattern-based parsing with warning
- **API unavailable**: Falls back to pattern-based parsing with warning
- **API error**: Falls back to pattern-based parsing with error details
- **Malformed response**: Falls back to pattern-based parsing

This ensures the VDE AI Assistant remains functional even without AI API access.

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
