---
name: No direct docker calls in step files
description: Step files must use bin/vde CLI, not docker subprocess calls directly
type: feedback
---

Replace all direct `docker` subprocess calls in BDD step files with `vde` CLI calls via `run_vde_command()` or `_vde_cli()`.

**Why:** We are testing the VDE project, not Docker. Direct docker calls bypass the product under test and can mask bugs in the VDE CLI layer.

**How to apply:**
- `docker ps --filter name=vde-X` → `run_vde_command("ps -q")` + check name in output
- `docker ps -a --filter name=vde-X` → `run_vde_command("ps --all -q")` + check name
- `docker stop vde-X` → `run_vde_command("stop X")`
- `docker rm vde-X` → `run_vde_command("remove X")`
- `docker network inspect X` → `run_vde_command("networks")` + parse output
- All checks via `vde ps -q` (running only) or `vde ps --all -q` (any state)
