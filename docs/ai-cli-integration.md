# AI CLI Integration

VDE provides excellent integration with modern AI CLI tools through its container-based architecture, unified `vde` CLI, and SSH access patterns.

[← Back to README](../README.md)

---

## Overview

VDE provides excellent integration with modern AI CLI tools through its container-based architecture and unified CLI.

### VDE's Built-in AI

VDE includes its own natural language interface for controlling VMs:

| Command | Purpose |
|---------|---------|
| `vde-ai "command"` | Execute natural language command (one-shot) |
| `vde-chat` | Interactive AI assistant session |
| `vde ai "command"` | Same as vde-ai (unified CLI) |
| `vde chat` | Same as vde-chat (unified CLI) |

**Supported intents:** list, create, start, stop, restart, status, connect, help

### Supported External AI Tools

| Tool | Integration | Best For |
|------|-------------|----------|
| **Claude Code** | Excellent (3 patterns) | Complex tasks, architecture |
| **Aider** | Good (SSH mode) | Git workflows, pair programming |
| **Cursor** | Excellent (Remote-SSH) | Refactoring, exploration |
| **Copilot** | Good (VSCode extension) | Boilerplate, completion |

---

## Claude Code Deep Dive

Claude Code (Anthropic's CLI coding assistant) has excellent integration with VDE.

### Understanding Claude Code + VDE Integration

There are **three main patterns** for using Claude Code with VDE:

#### Pattern 1: Host-Based (Recommended for Most Use Cases)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Host Machine          SSH              VDE Container                   │
│  ┌──────────┐         ┌──────┐         ┌──────────┐                │
│  │ Claude   │ ──────> │ :2222│ ──────> │ python-dev│               │
│  │  Code    │  edit  │      │  run    │          │                │
│  │          │ files  │      │ commands│          │                │
│  └──────────┘         └──────┘         └──────────┘                │
│                                                                     │
│  ✓ Claude edits files directly on host                              │
│  ✓ Claude runs commands via SSH                                     │
│  ✓ Best for: Most development work                                 │
└─────────────────────────────────────────────────────────────────────┘
```

#### Pattern 2: Container-Based (VSCode Remote-SSH)

```
┌─────────────────────────────────────────────────────────────────────┐
│   VDE Container (connected via VSCode Remote-SSH)                   │
│  ┌──────────────────────────────────────────┐                      │
│  │ VSCode ──────────────────> Claude Code    │                      │
│  │  │                    ──>  (npx)          │                      │
│  │  │                                      │                      │
│  │  └──> Integrated Terminal                │                      │
│  └──────────────────────────────────────────┘                      │
│                                                                     │
│  ✓ Claude runs inside the container                                 │
│  ✓ Direct access to all language tools                             │
│  ✓ Best for: Large codebases, complex debugging                    │
└─────────────────────────────────────────────────────────────────────┘
```

#### Pattern 3: Hybrid (Advanced)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Run Claude on host, but use it to manage multiple containers       │
│                                                                     │
│  Host: claude                                                       │
│    └─> "Start the python-dev container"                             │
│    └─> "Run tests in python-dev"                                    │
│    └─> "Check postgres logs"                                        │
│    └─> "Build the rust service"                                     │
│                                                                     │
│  ✓ Best for: Multi-service architectures, microservices            │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Pattern 1: Host-Based Claude Code (Recommended)

This is the **most common pattern**. Claude Code runs on your host machine and interacts with VDE containers via SSH.

**Setup:**

```bash
# 1. Navigate to your project directory (on host)
cd ~/dev/projects/python/my-api

# 2. Start Claude Code
claude

# Or if installed via npx
npx @anthropics/claude-code
```

**Configuration:**

Create a `.claude/project.md` file in your project directory:

```markdown
# VDE Python API Project

This is a FastAPI project running in the VDE python-dev container.

## VM Information
- **SSH Host**: `python-dev` (localhost:2203)
- **Container Name**: `python-dev`
- **Project Path**: `/home/devuser/workspace` (mounted from `~/dev/projects/python/`)
- **Host Path**: `~/dev/projects/python/my-api/`

## Available Services
- **PostgreSQL**: Host `postgres`, Port 5432, User `devuser`
  - Connect: `ssh postgres "psql -h localhost -U devuser"`
  - From container: `psql -h postgres -U devuser`

- **Redis**: Host `redis`, Port 6379
  - Connect: `ssh redis "redis-cli -h localhost"`
  - From container: `redis-cli -h redis`

## Development Commands
All commands should be run via SSH in the python-dev container:

**Environment Setup:**
```bash
vde start python  # Start VM first
ssh python-dev "cd ~/workspace && source .venv/bin/activate"
```

**Run Tests:**
```bash
ssh python-dev "cd ~/workspace && pytest"
```

**Run Server:**
```bash
ssh python-dev "cd ~/workspace && uvicorn main:app --reload --host 0.0.0.0"
```

**Install Dependencies:**
```bash
ssh python-dev "cd ~/workspace && pip install -r requirements.txt"
```
```

**Best Practices for Host-Based Pattern:**

1. **Use SSH for all container commands**:
   ```bash
   # Good
   ssh python-dev "pytest"

   # Bad (requires entering container first)
   ssh python-dev
   pytest
   ```

2. **Quote complex commands**:
   ```bash
   ssh python-dev "cd ~/workspace && source .venv/bin/activate && pytest"
   ```

3. **Use project.md for context**:
   - Keep it updated with your current commands
   - Document service dependencies
   - Include common workflows

4. **Leverage Claude's file editing**:
   - Claude edits files directly on the host
   - Changes are immediately visible in the container (via volume mount)
   - No need to copy files back and forth

---

### Pattern 2: Container-Based Claude Code

Run Claude Code inside the container for maximum tool access.

**Setup:**

```bash
# 1. Connect via VSCode Remote-SSH
# In VSCode: Cmd+Shift+P > "Remote-SSH: Connect to Host" > python-dev

# 2. Open the integrated terminal in VSCode

# 3. Navigate to workspace
cd ~/workspace

# 4. Start Claude Code
npx @anthropics/claude-code
```

**When to Use This Pattern:**

- Large codebases where network latency matters
- When you need direct access to language tools (type checkers, linters)
- Debugging complex issues that require multiple tool runs
- When working offline or with limited host resources

---

### Pattern 3: Multi-Container Management

Use Claude Code on the host to manage a microservices architecture.

**Setup:**

```bash
# On host, in the monorepo root
cd ~/dev
claude
```

**Example `.claude/project.md` for Monorepo:**

```markdown
# VDE Microservices Monorepo

This is a microservices application using multiple VDE containers.

## Services Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  API Gateway│ ───> │  User Svc    │ ───> │  PostgreSQL │
│  (Python)   │      │  (Go)        │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌──────────────┐
│   Redis     │ ◀─── │  Analytics   │
│             │      │  (Rust)      │
└─────────────┘      └──────────────┘
```

## Container Management

**Start all services:**
```bash
vde start python go rust postgres redis
```

**Stop all services:**
```bash
vde stop python go rust postgres redis
```

**Check status:**
```bash
vde status
vde health
```

## Service-Specific Commands

**API Gateway (Python):**
```bash
vde start python
ssh python-dev "cd ~/workspace && uvicorn main:app --reload"
ssh python-dev "cd ~/workspace && pytest"
```

**User Service (Go):**
```bash
vde start go
ssh go-dev "cd ~/workspace && go run main.go"
ssh go-dev "cd ~/workspace && go test ./..."
```
```

---

## Other AI CLI Tools

### Aider

Aider is a GPT-powered coding assistant that works well with VDE.

**Setup:**

```bash
# Install aider
pip install aider-chat

# Navigate to your project
cd ~/dev/projects/python/my-api

# Run aider (host-based)
aider --ssh python-dev
```

**Benefits:**
- Direct file editing in the container
- Built-in git integration
- Good for pair programming

---

### Cursor

Cursor is a fork of VSCode with AI integration built in.

**Setup:**

```bash
# 1. Install Cursor from cursor.sh

# 2. Open Cursor and connect to your VM via Remote-SSH
# File > Connect to Host... > python-dev

# 3. Open your project: /home/devuser/workspace

# 4. Use Cursor's AI features:
# - Cmd+L for chat
# - Cmd+K for inline editing
# - Cmd+I for code generation
```

**Benefits:**
- Native VSCode experience
- Direct container access
- Great for refactoring and code exploration

---

### GitHub Copilot

GitHub Copilot integrates with VSCode Remote-SSH.

**Setup:**

```bash
# 1. Install GitHub Copilot extension in VSCode

# 2. Connect to VM via Remote-SSH

# 3. Open a file in the workspace

# 4. Copilot works automatically:
# - Press Tab to accept suggestions
# - Ctrl+Enter for multi-line suggestions
# - Ctrl+Shift+Alt+/ for copilot chat
```

**Benefits:**
- Familiar VSCode interface
- Context-aware suggestions
- Good for boilerplate and documentation

---

## AI Tool Comparison

| Tool | VDE Integration | Best For | Setup Complexity |
|------|----------------|----------|------------------|
| **Claude Code** | Excellent (3 patterns) | Complex tasks, architecture | Medium |
| **Aider** | Good (SSH mode) | Git workflows, pair programming | Low |
| **Cursor** | Excellent (Remote-SSH) | Refactoring, exploration | Low |
| **Copilot** | Good (VSCode extension) | Boilerplate, completion | Low |

**Recommendation:** Start with **Claude Code** for its flexibility with VDE's multi-container architecture.

---

## Tips for AI Tools with VDE

**1. Always specify the container in commands:**
```
# Good
You: Run pytest in the python-dev container

# Bad
You: Run pytest
[Claude might run it on the host where it won't work]
```

**2. Use Claude's understanding of the architecture:**
```
You: The analytics service needs to read from the user service's API.
How should it connect?

Claude: Since both services are on the dev-net Docker network, the
analytics service should connect to 'go-dev:8001' (using the container
name as the hostname). Let me update the configuration...
```

**3. Leverage SSH for debugging:**
```
You: I'm getting a connection error. Debug this.

Claude: Let me check a few things:

1. Is the container running?
docker ps | grep postgres

2. Can we connect from the python container?
ssh python-dev "pg_isready -h postgres"

3. Let's check the postgres logs:
docker logs postgres --tail 50
```

**4. Use Claude for multi-step operations:**
```
You: Set up a new development environment for a JavaScript project
with Redis and PostgreSQL

Claude: I'll set this up step by step:

1. Create the JS VM:
vde create js

2. Create the service VMs:
vde create redis
vde create postgres

3. Start all VMs:
vde start js redis postgres

4. Create the project:
mkdir -p ~/dev/projects/js/myapp
cd ~/dev/projects/js/myapp

5. Initialize the project:
ssh js-dev "cd ~/workspace && npm init -y"

6. Install dependencies:
ssh js-dev "cd ~/workspace && npm install express pg redis"

All set! You can now:
- Connect: ssh js-dev
- Run: ssh js-dev "cd ~/workspace && node app.js"
```

---

[← Back to README](../README.md)
