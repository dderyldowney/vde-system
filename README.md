<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

# VDE - Your Virtual Development Playground! 🎉

![CI Status](https://github.com/dderyldowney/vde-system/actions/workflows/vde-ci.yml/badge.svg)


A modular, template-based Docker development environment supporting 19+ programming languages and 7+ services, all accessible via SSH with consistent user configuration. Designed for daily development work with VSCode Remote-SSH.

**Shell Support:** zsh 5.0+, bash 4.0+, bash 3.x (with fallbacks) — [See Requirements](docs/requirements.md)

---

## Hey There! 👋

Welcome to VDE — your new best friend for development environments. Whether you're a total beginner or a seasoned pro, whether you code in Python or Rust or something entirely new — VDE is here to make your life easier. You're going to love it here! ✨

> **🎉 New to VDE?** Start here: [**Why Use VDE?**](docs/WHY_USE_VDE.md) — Discover how VDE transforms your development workflow.

---

## Quick Links (Your Cheat Sheet!) 📇

| Section | Description |
|---------|-------------|
| **🎉 Why Use VDE?** | [Why Use VDE?](docs/WHY_USE_VDE.md) - Learn what VDE can do for you |
| **📘 User Guide** | [USER_GUIDE.md](USER_GUIDE.md) - Step-by-step guide for new users |
| **Getting Started** | [Requirements](docs/requirements.md) • [Quick Start](docs/quick-start.md) |
| **SSH & Agent Forwarding** | [SSH Configuration](docs/ssh-configuration.md) • [VM Communication](docs/advanced-usage.md#inter-container-communication) • [SSH Troubleshooting](docs/troubleshooting.md#ssh-agent-issues) |
| **Core Features** | [Available Scripts](docs/available-scripts.md) • [Predefined VM Types](docs/predefined-vm-types.md) • [Command Reference](docs/command-reference.md) |
| **Configuration** | [Extending VDE](docs/extending-vde.md) • [Directory Structure](docs/directory-structure.md) |
| **Development** | [VSCode Remote-SSH](docs/vscode-remote-ssh.md) • [Development Workflows](docs/development-workflows.md) |
| **Contributing** | [Contributing Guide](CONTRIBUTING.md) • [Style Guide](STYLE_GUIDE.md) • [Testing Guide](docs/TESTING.md) |
| **Reference** | [API Reference](docs/API.md) • [User Model](docs/user-model.md) • [Architecture](docs/ARCHITECTURE.md) • [Best Practices](docs/best-practices.md) |
| **Support** | [Troubleshooting](docs/troubleshooting.md) • [Rebuild Guidelines](docs/rebuild-guidelines.md) |

---

## Overview (The Good Stuff!) ✨

VDE provides isolated development environments for multiple programming languages and services, all accessible via SSH. Each environment has:

- **Consistent user setup** (`devuser` with zsh, neovim, oh-my-zsh)
- **SSH key-based access** on auto-allocated ports
- **Persistent workspace** mounted from your host
- **Shared network** for inter-container communication

### Key Features (Why You'll Love It)

- **19+ Language VMs**: Python, Rust, Go, Java, JavaScript, C#, Ruby, and more — all waiting for you!
- **7+ Service VMs**: PostgreSQL, Redis, MongoDB, Nginx, MySQL, RabbitMQ, CouchDB — ready when you are
- **Template-based**: Add new languages/services without code changes — it just works!
- **VSCode Ready**: Full IDE support via Remote-SSH — code in comfort
- **SSH Agent Forwarding**: VM-to-VM and VM-to-Host communication using your host's SSH keys — like magic!
- **Automatic SSH Setup**: VDE handles SSH agent, keys, and configuration automatically — zero manual setup

---

## Quick Start (You're 3 Commands Away!) 🚀

```bash
# 1. Navigate to your dev directory
cd ~/dev

# 2. List all predefined VM types
./scripts/vde list

# 3. Create a new language VM
./scripts/vde create go

# 4. Start the VM
./scripts/vde start go

# 5. Connect via SSH
ssh go-dev

# 6. Start working
cd ~/workspace
```

**And just like that...** you're a Go developer! 🎊

**Next Steps:**
- 📘 **Read the [USER_GUIDE.md](USER_GUIDE.md)** for a complete step-by-step walkthrough (it's really friendly!)
- Read the [Quick Start guide](docs/quick-start.md) for detailed setup
- See [Command Reference](docs/command-reference.md) for all available commands

---

## SSH Agent Forwarding & VM Communication (The Magic Sauce!) ✨

VDE includes **automatic SSH agent forwarding**, enabling seamless communication between VMs and with external services. It's like magic, but better!

### What This Means (In Plain English)

- **VM → VM**: SSH from one VM to another using your host's SSH keys — no copying required!
- **VM → Host**: Execute commands on your host from within a VM — super convenient!
- **VM → External**: Use your GitHub/GitLab keys from within any VM — your credentials, wherever you need them!
- **Automatic Setup**: No manual configuration required — VDE handles it all for you

### Example: VM-to-VM Communication

```bash
# From your host
ssh go-dev                    # Connect to Go VM

# From within Go VM
ssh python-dev                # SSH to Python VM (uses your host keys!)
ssh rust-dev pwd              # Check directory on Rust VM
scp python-dev:/data/file .   # Copy file from Python VM

# Use Git with your credentials
git clone github.com:user/repo  # Uses your GitHub SSH key
```

### Example: VM-to-Host Communication

```bash
# From within any VM
to-host ls ~/dev              # List host's dev directory
to-host tail -f logs/app.log  # View host's log files
```

### How It Works

- VDE automatically starts SSH agent and loads your keys
- Your SSH keys **never leave** the host machine (security)
- VMs access keys via SSH agent socket forwarding
- Works with any SSH key type (ed25519, RSA, ECDSA, DSA)
- All your SSH keys are automatically detected and used

**No manual setup required** — VDE handles everything for you. Sit back and relax! ☕

See [SSH Configuration](docs/ssh-configuration.md) for complete details.

---

## Documentation (We've Got You Covered!) 📚

### Getting Started (Your Journey Begins Here!) 🌟

| Document | Description |
|----------|-------------|
| [Requirements](docs/requirements.md) | System requirements and prerequisites |
| [Quick Start](docs/quick-start.md) | Get up and running in minutes — let's go! |

### Core Features (The Good Stuff!) 🌟

| Document | Description |
|----------|-------------|
| [Available Scripts](docs/available-scripts.md) | Overview of all VDE scripts |
| [Predefined VM Types](docs/predefined-vm-types.md) | All available languages and services |
| [Command Reference](docs/command-reference.md) | Complete command reference |

### Configuration (Make It Yours!) 🔧

| Document | Description |
|----------|-------------|
| [Extending VDE](docs/extending-vde.md) | Add new languages and services |
| [SSH Configuration & Agent Forwarding](docs/ssh-configuration.md) | SSH setup, agent forwarding, VM-to-VM communication |
| [Directory Structure](docs/directory-structure.md) | Complete directory layout |

### Development (Build Cool Things!) 💻

| Document | Description |
|----------|-------------|
| [VSCode Remote-SSH](docs/vscode-remote-ssh.md) | Using VSCode with VDE — code in comfort! |
| [Development Workflows](docs/development-workflows.md) | Example development scenarios |

### Reference (The Nitty Gritty) 📖

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete API reference for scripts and libraries |
| [User Model & Naming Conventions](docs/user-model.md) | User account and naming standards |
| [Architecture](docs/ARCHITECTURE.md) | Technical architecture details |
| [Advanced Usage](docs/advanced-usage.md) | Advanced techniques and patterns |
| [Rebuild Guidelines](docs/rebuild-guidelines.md) | When and how to rebuild |
| [Best Practices](docs/best-practices.md) | Recommended practices |

### Support

| Document | Description |
|----------|-------------|
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

---

## Example Workflows (Build Cool Things!) 🏗️

### Python API with PostgreSQL

```bash
./scripts/vde create python
./scripts/vde create postgres
./scripts/vde start python postgres
ssh python-dev
cd ~/workspace
pip install fastapi uvicorn psycopg2-binary
```

### Microservices Architecture (Your Distributed System!) 🌐

```bash
# Create VMs for each service
./scripts/create-virtual-for python   # API Gateway
./scripts/create-virtual-for go       # Payment Service
./scripts/create-virtual-for rust     # Analytics
./scripts/create-virtual-for postgres # Database
./scripts/create-virtual-for redis    # Cache

# Start all services
./scripts/vde start python go rust postgres redis

# Services can communicate via SSH (VM-to-VM)
# From python VM:
ssh postgres-dev psql -U devuser  # Connect to database
ssh redis-dev redis-cli           # Connect to cache
```

---

## Project Structure

```
$HOME/dev/
├── configs/docker/       # VM configurations (auto-generated)
├── data/                  # Service data persistence
├── docs/                  # Documentation
├── env-files/             # Environment variables per VM
├── logs/                  # Application logs
├── projects/              # Project source code
├── public-ssh-keys/       # SSH keys for containers
├── scripts/               # Management scripts
│   ├── lib/               # Shared libraries
│   └── templates/         # Docker Compose templates
└── README.md
```

See [Directory Structure](docs/directory-structure.md) for complete details.

---

## Support (We've Got Your Back!) 🆘

### Getting Help

```bash
# Built-in help
./scripts/vde help

# List available VMs
./scripts/vde list
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | See [Troubleshooting → Port Conflicts](docs/troubleshooting.md#port-conflicts) |
| SSH connection issues | See [SSH Configuration → Troubleshooting](docs/ssh-configuration.md#troubleshooting) |
| SSH agent not working | See [Troubleshooting → SSH Agent Issues](docs/troubleshooting.md#ssh-agent-issues) |
| VM-to-VM SSH not working | See [SSH Configuration → VM-to-VM](docs/ssh-configuration.md#vm-to-vm-communication) |
| Container won't start | See [Rebuild Guidelines](docs/rebuild-guidelines.md) |
| VSCode can't connect | See [VSCode Remote-SSH](docs/vscode-remote-ssh.md) |

---

## Appendix: Technical Deep Dives 🤓

**Quick heads up!** These documents go deep into the technical weeds. They're written for the fellow nerdy types (like VDE's creator!) who want to understand every nut and bolt of how VDE works under the hood.

**But hey!** Even if you're not a "nerdy type," you're more than welcome to follow along! It's not as scary as all that — we promise! 😉 These guides are comprehensive, detailed, and written for folks who love to understand *how* things work under the hood. You might just learn something cool!

For comprehensive technical documentation, see these in-depth guides:

1. **[Technical Deep Dive](docs/Technical-Deep-Dive.md)** - Complete technical deep-dive of the VDE system architecture and components. [← Back to README](../README.md)

2. **[VDE PARSER Technical Deep Dive](docs/VDE-PARSER-Technical-Deep-Dive.md)** - Focused technical analysis of the VDE natural language parser. [← Back to README](../README.md)

---

## License (Legal Stuff, But Still Important) ⚖️

This VDE system is provided as-is for development purposes.
