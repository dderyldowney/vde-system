---
name: Refresh language docs via context7 at session start
description: At every session resume, fetch fresh docs for project languages via context7 MCP before working
type: feedback
---

At every session start (or on user request "update your knowledge"), use context7 MCP to refresh docs for the languages and tools used to implement VDE:

1. `Python` → `/websites/python_3_15` — subprocess, pathlib, json, os, sys, re, shlex, tempfile, unittest, pytest, argparse
2. `behave` → `/behave/behave` — step defs, hooks, fixtures, context patterns
3. `PyYAML` → `/yaml/pyyaml` — safe_load, safe_dump, multi-doc streams
4. `Docker` → `/docker/docker` — containers, images, networking, volumes, exec
5. `docker-compose` → `/docker/compose` — services, networks, volumes, build, healthcheck
6. `Zsh` → `/zsh-users/zsh` — associative arrays, process substitution, parameter expansion, zsh 5.x
7. `SSH` → `/openssh/openssh-portable` — config, key auth, port forwarding, ssh_config directives

**Why:** context7 fetches live docs each session — the knowledge is not persisted in memory files. Re-fetching ensures idioms and API signatures stay current. User explicitly requested this be done on every resume.

**How to apply:** Run all seven `mcp__context7__query-docs` calls in parallel during startup, after steps 1-4 of the 7-step checklist.
