<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

# The Way of the VDE: 1.3.1 (The Sovereign Baseline)

![CI Status](https://github.com/dderyldowney/vde-system/actions/workflows/vde-ci.yml/badge.svg)

A sovereign, template-based ecosystem of Dockerized Spokes. Supporting 19+ Language Spokes and 7+ Service Spokes, forged for the warrior who demands consistent hydration and absolute isolation. Accessible via **The Sovereign Baseline (SSH)** with a single, unyielding identity.

**The Language of the Tribe:** Strictly **ZSH 5.0+**. No bash-isms, no shortcuts. [See Requirements](docs/requirements.md)

---

## This is the Way. 👋

Welcome, Foundling, to the VDE — the Beskar Hub for your development Spokes. Whether you strike in Python, Rust, or the ancient scripts of C, the VDE provides the armor you need. Each environment is pre-hydrated, isolated, and ready for the Forge.

> **🛡️ New to the Creed?** Start here: [**The Seeker's Recon (Why VDE?)**](docs/WHY_USE_VDE.md) — Discover how the VDE transforms your workflow into the Way.

---

## The Archivist's Intel (Quick Links) 📇

| Section | Description |
|---------|-------------|
| **🛡️ Why the Way?** | [The Seeker's Recon](docs/WHY_USE_VDE.md) - Learn the power of VDE |
| **📘 The Warrior's Guide** | [VDE_INSTALL.md](VDE_INSTALL.md) - **MANDATORY**: Start here for initial installation and setup. |
| **Ignition Prerequisites** | [Requirements](docs/requirements.md) • [VDE_INSTALL.md](VDE_INSTALL.md) |
| **The Sovereign Baseline** | [SSH Configuration](docs/ssh-configuration.md) • [Spoke Communication](docs/advanced-usage.md#inter-container-communication) • [Handshake Troubleshooting](docs/troubleshooting.md#ssh-agent-issues) |
| **Core Mandates** | [Available Rituals](docs/available-scripts.md) • [Predefined Spokes](docs/predefined-vm-types.md) • [Command Reference](docs/command-reference.md) |
| **The Beskar Vault** | [Extending the Creed](docs/extending-vde.md) • [Directory Hierarchy](docs/directory-structure.md) |
| **The Forge** | [VSCode Remote-SSH](docs/vscode-remote-ssh.md) • [Development Guide](docs/DEVELOPMENT_GUIDE.md) |
| **The Tribe's Contribution** | [Contributing Guide](CONTRIBUTING.md) • [The Language of the Tribe](STYLE_GUIDE.md) • [Testing Mandates](docs/TESTING.md) |
| **Ancient Intel** | [API Reference](docs/API.md) • [Architecture 1.3.1](docs/ARCHITECTURE.md) • [Release Archive](https://github.com/dderyldowney/vde-system/tree/main/docs/releases) |
| **Reinforcements** | [Troubleshooting](docs/troubleshooting.md) • [Rebuild Mandates](docs/rebuild-guidelines.md) |
| **Evolution** | [Evolution Guide](#the-evolution-of-armor) - Keeping the Hub up-to-date |

---

## Prerequisites (The Warrior's Rights)

### Docker Sovereignty

To ignite the Spokes, you must have sovereignty over the Docker daemon. If the daemon denies your handshake:

- **Darwin (macOS):** Install Docker Desktop and ensure the engine is humming.
- **Linux:** Add your warrior to the guild: `sudo usermod -aG docker $USER`, then re-ignite your session.
- **Protocol Failures:** If Docker demands `sudo` for every strike, fix it with: `sudo usermod -aG docker $USER`

---

## The Evolution of Armor (Upgrade Guide)

The VDE is forged to preserve your Beskar and your Spokes during evolution. Here is how you keep your armor strong:

### Strengthening the Hub

```zsh
# Navigate to the VDE Root
cd ~/dev

# Pull the latest Intel from the Tribe
git pull

# Re-smelt the base images (The Forge Ritual)
vde rebuild
```

### What Occurs During Evolution

- **Your Spokes Remain Active**: Existing configurations in `configs/docker/` are protected.
- **New Spokes Appear**: New Language and Service templates added to the Beskar Vault become available.
- **The Beskar is Safe**: Your data (`data/`) and projects (`projects/`) are never struck.

---

## The Resol’nare (The Core Mandates) 🛡️

The VDE provides isolated jails for your work, all accessible via **The Sovereign Baseline**. Every jail contains:

- **The Tribal Identity** (`devuser` with zsh, neovim, and the oh-my-zsh ritual)
- **The Sovereign Baseline** on auto-allocated, audited ports
- **Persistent Beskar** (Workspace) mounted from your host
- **The Hub Network** for seamless inter-Spoke communication

### The Mandates of the Creed

- **19+ Language Spokes**: Python, Rust, Go, Java, JavaScript, C#, Ruby — the Hub supports them all.
- **7+ Service Spokes**: PostgreSQL, Redis, MongoDB, Nginx, MySQL, RabbitMQ, CouchDB — pre-hydrated and ready.
- **Born Ready (BTO)**: Add new Spokes via the Beskar Vault without rewriting the rituals — it just works.
- **The Forge Ready**: Full IDE support via Remote-SSH — code in the comfort of your armor.
- **SSH Agent Trust Bridge**: Spoke-to-Spoke and Spoke-to-Host communication using your host's identities — the magic of the Tribe.
- **Atomic SSH Setup**: The VDE handles the agent, the keys, and the config — zero manual toil.

---

## The Quick Strike (You're 3 Rituals Away!) 🚀

```zsh
# 1. Enter the VDE Root
cd ~/dev

# 2. Audit all predefined Spokes
vde list

# 3. Forge a new Language Spoke
vde create go

# 4. Ignite the Spoke
vde start go

# 5. Connect via **The Sovereign Baseline** (The Code Contract)
vde enter go                  # MANDATORY: 'vde enter go' MUST work (Code Contract).
ssh vde-go                    # SECONDARY: 'ssh vde-go' SHOULD work.

# 6. Begin your work
cd ~/workspace
```

**And just like that...** you are a Go warrior. 🛡️

**Next Rituals:**
- 📘 **Read the [Warrior's Guide (USER_GUIDE.md)](USER_GUIDE.md)** for a complete step-by-step walkthrough.
- Read the [Quick Start Intel](docs/quick-start.md) for detailed ignition.
- See the [Ritual Reference](docs/command-reference.md) for all available commands.

---

## SSH Agent Trust Bridge & Spoke Communication 🛡️

VDE includes **Atomic SSH Agent Forwarding**, enabling **The Sovereign Baseline** between Spokes and with external repositories.

### The Way of the Bridge

- **Spoke → Spoke**: SSH from one Spoke to another using your host's identity — the Beskar stays on the host.
- **Spoke → Host**: Execute commands on your host from within a jail — use `to-host`.
- **Spoke → External**: Use your GitHub/GitLab identities from within any Spoke — your honor goes where you go.
- **Zero-Toil Setup**: No manual configuration — the Tribe handles the handshake.

### Example: Spoke-to-Spoke Handshake

```zsh
# From your host (The Hub)
ssh vde-go                    # Connect to Go Spoke

# From within the Go Spoke
ssh vde-python                # Handshake with Python Spoke
ssh vde-rust pwd              # Audit the Rust Spoke
scp vde-python:/data/file .   # Extract intel from Python Spoke

# Strike a repository
git clone git@github.com:user/repo.git  # Uses your host identities
```

### Example: Spoke-to-Host Communication

```zsh
# From within any Spoke jail
to-host ls ~/dev              # Audit the Hub's directory
to-host tail -f logs/app.log  # Observe the Hub's logs
```

**No manual setup is permitted.** The VDE handles the handshake for you. This is the Way.

See [Handshake Configuration](docs/ssh-configuration.md) for complete intel.

---

## Intel (The Archive) 📚

### Ignition (The Journey Begins) 🌟

| Document | Description |
|----------|-------------|
| [Requirements](docs/requirements.md) | Hub requirements and prerequisites |
| [Quick Strike](docs/quick-start.md) | Ignite your Spokes in minutes. |

### Core Mandates 🌟

| Document | Description |
|----------|-------------|
| [Available Rituals](docs/available-scripts.md) | Overview of all VDE management scripts |
| [Predefined Spokes](docs/predefined-vm-types.md) | All available Languages and Services |
| [Ritual Reference](docs/command-reference.md) | Complete command reference |

### The Beskar Vault (Configuration) 🔧

| Document | Description |
|----------|-------------|
| [Extending the Creed](docs/extending-vde.md) | Forge new Spokes |
| [**The Sovereign Baseline**](docs/ssh-configuration.md) | SSH setup, agent trust, and Spoke communication |
| [Directory Hierarchy](docs/directory-structure.md) | The structure of the Hub |

### The Forge (Development) 💻

| Document | Description |
|----------|-------------|
| [VSCode Remote-SSH](docs/vscode-remote-ssh.md) | Code in comfort via **The Sovereign Baseline**. |
| [Development Guide](docs/DEVELOPMENT_GUIDE.md) | Example battle scenarios |

### Ancient Intel (Reference) 📖

| Document | Description |
|----------|-------------|
| [API Rituals](docs/API.md) | Complete API reference for scripts and libraries |
| [Technical Deep Dive](docs/Technical-Deep-Dive.md) | VDE Under the Hood |
| [Architecture 1.3.1](docs/ARCHITECTURE.md) | Technical blueprint of the Hub |

| [Advanced Strikes](docs/advanced-usage.md) | Advanced techniques and patterns |
| [Rebuild Mandates](docs/rebuild-guidelines.md) | When to re-smelt your armor |
| [The Way (Best Practices)](docs/best-practices.md) | Recommended practices for the Tribe |

---

## Battle Scenarios (Example Workflows) 🏗️

### Python API with PostgreSQL

```zsh
vde create python
vde create postgres
vde start python postgres
ssh vde-python
cd ~/workspace
pip install fastapi uvicorn psycopg2-binary
```

### The Sovereign Swarm (Distributed Systems) 🌐

```zsh
# Ignite Spokes for the Swarm
vde create python   # The Gatekeeper
vde create go       # The Payment Warrior
vde create rust     # The Analyst
vde create postgres # The Beskar Vault
vde create redis    # The Messenger

# Start the Swarm
vde start python go rust postgres redis

# Spokes communicate via the Trust Bridge
# From the python Spoke:
ssh vde-postgres psql -U devuser  # Connect to the Vault
ssh vde-redis redis-cli           # Connect to the Messenger
```

---

## Hub Structure

```
$HOME/dev/
├── configs/docker/       # Spoke configurations (Forged)
├── data/                  # Service Beskar persistence
├── docs/                  # Ancient Intel
├── env-files/             # Environment variables per Spoke
├── lib/                   # The Core Tribe Libraries
├── logs/                  # Hub & Spoke logs
├── projects/              # Warrior workspace
├── templates/             # Docker Forge templates
├── bin/                   # Ritual Management scripts
└── README.md              # The Way
```

---

## Reinforcements (The Tracking Fob) 🆘

### Seeking Help

```zsh
# Built-in Ritual help
vde help

# List all Spokes
vde list
```

### Protocol Blockades (Common Issues)

| Blockade | Resolution |
|-------|----------|
| Port Ambiguity | See [Troubleshooting → Port Conflicts](docs/troubleshooting.md#port-conflicts) |
| Handshake Failure | See [**The Sovereign Baseline** → Troubleshooting](docs/ssh-configuration.md#troubleshooting) |
| Agent Disconnect | See [Troubleshooting → SSH Agent Issues](docs/troubleshooting.md#ssh-agent-issues) |
| Spoke-to-Spoke Block | See [**The Sovereign Baseline** → Spoke Communication](docs/ssh-configuration.md#vm-to-vm-communication) |
| Spoke Won't Ignite | See [Rebuild Mandates](docs/rebuild-guidelines.md) |
| VSCode Denied | See [VSCode Remote-SSH](docs/vscode-remote-ssh.md) |

---

## Appendix: The Seeker's Technical Recon 🤓

**Heads up, Seeker!** These documents delve into the deep Beskar. They are written for the Armorers who want to understand every nut and bolt of the Hub.

For comprehensive technical intel, see these in-depth scrolls:

1. **[Technical Deep Dive](docs/Technical-Deep-Dive.md)** - Complete technical blueprint of the VDE system, templates, and the Parser Ritual. [← Back to The Way](README.md)

---

## The Creed (License) ⚖️

This VDE system is provided as-is for the warrior's journey. Use it with honor.

This is the Way.
# Test
