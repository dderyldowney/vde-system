---
name: Refresh language docs via context7 at session start
description: At every session resume, fetch fresh docs for project languages via context7 MCP before working
type: feedback
---

At every session start (or on user request "update your knowledge"), use context7 MCP to refresh docs for the languages used in VDE:

1. `behave` → `/behave/behave` — step defs, hooks, fixtures, context patterns
2. `Python` → `/websites/python_3_15` — subprocess, pathlib, json module, idiomatic patterns
3. `PyYAML` → `/yaml/pyyaml` — safe_load, safe_dump, multi-doc streams
4. `json` (stdlib) → covered under Python docs above

**Why:** context7 fetches live docs each session — the knowledge is not persisted in memory files. Re-fetching ensures idioms and API signatures stay current. User explicitly requested this be done on every resume.

**How to apply:** Run all four `mcp__context7__query-docs` calls in parallel during startup, after steps 1-4 of the 7-step checklist.
