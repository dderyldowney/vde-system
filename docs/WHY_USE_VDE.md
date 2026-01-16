<p align="center"><img src="imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

# Why VDE? Your Development Environment, Simplified.

*Imagine having every programming language, every database, every tool you need—all ready to go in seconds. No installation headaches. No version conflicts. No "works on my machine" problems. Just pure development flow.*

---

## The Problem: "It Worked on My Laptop..."

We've all been there. You spend hours setting up your development environment:

- Installing Python 3.11 (but your project needs 3.9)
- Fighting with version conflicts (`npm install` giving you nightmares?)
- Setting up databases that mysteriously fail on your teammate's computer
- Spending more time configuring than actually coding
- That awkward moment when your local environment breaks and you have to start over

**Sound familiar?**

---

## The Solution: VDE - Your Virtual Development Environment

**VDE (Virtual Development Environment)** gives you isolated, ready-to-use containers for *any* programming language or service you need.

Think of it like having a workshop with every tool you could ever want—each tool in its own dedicated workspace, always ready, always clean, never interfering with anything else.

---

## What Do I Need? (Spoiler: Not Much)

You only need **three things** installed on your computer:

| What | Why | Already Have It? |
|------|-----|------------------|
| **Docker** | VDE runs everything in Docker containers | Open Terminal and run: `docker --version` |
| **Git** | To clone the VDE repository | Run: `git --version` |
| **Bash or Zsh** | Your shell (runs VDE scripts) | Run: `echo $SHELL` |

**That's it.** No language runtimes. No databases. No package managers. Just Docker, Git, and a shell.

### Don't Have One of Those? No Problem.

The [**User Guide**](./USER_GUIDE.md) includes **beginner-friendly, no-knowledge-required tutorials** for:

- Installing Docker Desktop (Mac, Windows, Linux)
- Installing Git
- Checking which shell you're using (bash or zsh)

Even if you've never used Terminal before, we've got you covered.

**We literally walk you through clicking buttons.** No assumptions about what you know.

---

## Getting Started: It's This Easy

Ready to have your mind blown? Here's all it takes to get started with Python:

```bash
# That's it. Seriously.
./scripts/create-virtual-for python
./scripts/start-virtual python
ssh python-dev
```

**Three commands.** That's all.

You now have a fully-functional Python development environment with:
- Python 3 and pip installed
- Its own isolated workspace
- SSH access with your keys
- Connection to shared services (PostgreSQL, Redis, MongoDB, etc.)
- Zero conflicts with anything else on your computer

---

## Want Rust Too? Go Ahead.

```bash
./scripts/create-virtual-for rust
./scripts/start-virtual rust
ssh rust-dev
```

Now you have Python **and** Rust running side-by-side. No conflicts. No version wars. They don't even know each other exist (unless you want them to).

---

## What Can I Run?

VDE supports **19 programming languages** out of the box:

| Category | Languages |
|----------|-----------|
| **Systems** | C, C++, Assembly, Rust |
| **Web** | JavaScript, PHP, Python |
| **Enterprise** | Java, Kotlin, C# |
| **Data Science** | Python, R |
| **Modern** | Go, Elixir, Haskell, Scala |
| **Mobile** | Flutter (Dart) |
| **Scripting** | Ruby, Lua, Swift, Zig |

Plus **7 shared services**:
- PostgreSQL, MySQL (databases)
- Redis (caching)
- MongoDB (document store)
- Nginx (web server)
- RabbitMQ, CouchDB (messaging)

All pre-configured. All ready to connect. All yours.

---

## The "Magic" Part: VMs Talking to VMs

This is where VDE gets *really* cool.

Imagine you're working in your Python container and you need to test something against the PostgreSQL database. You don't need to exit, open a new terminal, or mess with connection strings:

```bash
# From inside your Python VM
ssh postgres-dev psql -U devuser
```

That's it. You're now in PostgreSQL. Using **your** SSH keys. Without any setup.

Your VMs can SSH to each other. Your VMs can SSH to external services (like GitHub) using **your** credentials. Your VMs can even run commands on **your** host computer.

And the best part? Your private keys *never leave your computer*. They're safely forwarded through SSH agent magic. (We'll explain the details later—just know it's secure.)

---

## Real-World Example: A Full-Stack Project

Let's say you want to build a web app with:
- A Python backend
- A JavaScript frontend
- A PostgreSQL database
- Redis for caching

Here's your workflow:

```bash
# Create everything
./scripts/create-virtual-for python js postgres redis

# Start everything
./scripts/start-virtual python js postgres redis

# Connect to your Python backend
ssh python-dev
cd ~/workspace/my-app
pip install -r requirements.txt
python app.py
```

In another terminal:

```bash
# Connect to your JavaScript frontend
ssh js-dev
cd ~/workspace/my-app
npm install
npm start
```

Your Python app talks to `postgres` and `redis` by hostname. No connection strings to remember. No ports to memorize. It just works.

---

## But I Already Have a Development Environment...

That's great! But consider:

### 🤔 Problem: Learning a New Language
**Without VDE:** Install language, manage versions, risk breaking your current setup.
**With VDE:** `./scripts/create-virtual-for elixir` and you're done. Delete it when you're finished.

### 🤔 Problem: "Works on My Machine"
**Without VDE:** Endless debugging of environment differences.
**With VDE:** Everyone runs the exact same containers. Same versions. Same everything.

### 🤔 Problem: Testing Against Multiple Versions
**Without VDE:** Complex version management tools.
**With VDE:** Create a VM for Python 3.9 and another for 3.11. Test against both.

### 🤔 Problem: Dependency Hell
**Without VDE:** One project's dependencies break another's.
**With VDE:** Each project lives in isolation. No conflicts. Ever.

---

## You're in Control (Even If You Don't Know Docker)

VDE handles all the Docker complexity for you. You don't need to know:
- How to write Dockerfiles
- How to configure networks
- How to manage volumes
- How to set up SSH

**VDE does it all.**

But if you *do* know Docker, you'll love that VDE generates clean, readable `docker-compose.yml` files that you can customize to your heart's content.

---

## For the Curious: What's Actually Happening?

When you run `./scripts/create-virtual-for python`, VDE:

1. Finds an available SSH port (automatically)
2. Creates a Docker Compose configuration
3. Sets up your project directory
4. Adds an SSH config entry (`ssh python-dev` will work)
5. Starts the SSH agent (if not running)
6. Loads your SSH keys (or generates a pair if you don't have one)
7. Gets everything ready for `start-virtual`

When you run `./scripts/start-virtual python`, VDE:

1. Builds a Docker image with your language pre-installed
2. Creates a container with:
   - Your code mounted from your computer
   - SSH access configured
   - Agent forwarding enabled (for VM-to-VM communication)
   - A user account (`devuser`) with sudo access
3. Connects the container to the VDE network (so VMs can talk to each other)
4. Starts the SSH server

When you `ssh python-dev`:

1. Your SSH connection goes directly into the container
2. You land in `/home/devuser/workspace`
3. Your code is there (it's actually on your computer, mounted in)
4. Everything you need is ready

**And all of that happens in seconds.**

---

## For the AI Enthusiast: Natural Language Control

VDE includes an AI assistant that understands natural language:

```bash
./scripts/vde-ai "start python and postgres"
```

That's it. VDE figures out what you mean and does it.

You can also use interactive chat mode:

```bash
./scripts/vde-chat
```

Then just type what you want:
- "create a rust vm"
- "stop all running vms"
- "show me the status"
- "connect to the python vm"

No need to remember commands. Just say what you want.

---

## So... Why Should You Use VDE?

### For Beginners
- Learn any language without installation nightmares
- Experiment freely—can't break your actual computer
- Focus on coding, not configuring

### For Experienced Developers
- Rapid environment switching
- Consistent environments across teams
- Test against multiple language versions
- Isolate experimental projects

### For Teams
- Everyone runs the same environment
- New developer onboarding? "Run these three commands."
- No more "it works on my machine"
- Shared services (databases) available to everyone

### For Tinkerers
- Try a new language for a weekend (then delete it)
- Experiment with weird combinations
- Learn how Docker containers work (VDE generates readable configs)

### For Educators
- Students all have identical environments
- No debugging of student laptop configurations
- Focus on teaching concepts, not troubleshooting

---

## The "Is This For Me?" Checklist

You should use VDE if you answered "yes" to any of these:

- [ ] You've ever spent more than an hour setting up a development environment
- [ ] You've ever said "but it works on my machine"
- [ ] You want to learn a new language without commitment
- [ ] You work with multiple programming languages
- [ ] You've ever broken your environment installing something
- [ ] You want to try a technology without "polluting" your computer
- [ ] You want to isolate experimental or learning projects
- [ ] You want your team to have consistent environments

---

## What People Are Saying

*(Okay, we made these up, but they're what users would say if they were real)*

> "I went from 'I want to learn Rust' to writing Rust code in 30 seconds. That's not an exaggeration." — *Hypothetical Satisfied User*

> "My team's new developer onboarding went from 2 days of environment setup to 5 minutes. It's ridiculous." — *Imaginary Team Lead*

> "I tried Elixir for a weekend, then deleted the VM. No traces left. Perfect." — *Fictional Language Explorer*

> "I can't believe I used to install PostgreSQL locally. What was I thinking?" — *Retroactively Enlightened Developer*

---

## What If I Want to Stop Using VDE?

We get it. Sometimes you try something and it's not for you. Or maybe you're just done with a project and want to clean up.

**Good news: VDE is designed to be completely removable.**

### The Two-Step Farewell

```bash
# 1. Stop any running VMs
./scripts/shutdown-virtual all

# 2. Delete the VDE directory
cd ..
rm -rf dev/  # or whatever you named the directory
```

**That's it.** No leftover packages. No system changes to undo. No registry keys to clean. The directory is gone, and so is VDE.

Your Docker images will take up some disk space (you can clean those with Docker Desktop if you want), but VDE itself leaves zero trace on your system.

### Wait, Can I Keep My Code?

**Absolutely!** Your code is in the `projects/` directory inside the VDE folder. Before deleting VDE:

```bash
# Copy your projects somewhere safe
cp -r dev/projects ~/my-projects-backup

# Or move individual projects
mv dev/projects/python/my-app ~/my-app
```

Then delete VDE, and your projects live on.

**VDE is just a tool for your development—not a prison for your code.**

---

## Ready to Give It a Try?

**Your first VDE is three commands away:**

```bash
cd ~/dev  # or wherever you cloned this repo
./scripts/create-virtual-for python  # or any language you want
./scripts/start-virtual python
ssh python-dev
```

That's it. Welcome to easier development.

---

## Want to Learn More?

- [**Quick Start Guide**](./quick-start.md) - Step-by-step setup instructions
- [**User Guide**](./USER_GUIDE.md) - Comprehensive BDD scenarios
- [**Command Reference**](./command-reference.md) - All available commands
- [**SSH Configuration**](./ssh-configuration.md) - Deep dive on VM-to-VM communication
- [**Architecture**](./ARCHITECTURE.md) - How it all works under the hood

---

## TL;DR (Because We Know You're Busy)

**VDE gives you:**
- 19 programming languages, ready in seconds
- 7 shared services (databases, caching, etc.)
- Isolated environments (no conflicts)
- VM-to-VM communication
- Natural language control
- Zero Docker knowledge required

**You give it:**
- Three commands to get started

**Want to leave?**
- Two commands to completely remove it

**Fair trade?** We think so.

---

*[Home](../README.md) | [Quick Start](./quick-start.md) | [Documentation](./)*
