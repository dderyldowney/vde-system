# VDE-NEW-VM
<!-- @forge (Agent Logic) -->
Guided workflow to add a new VM type following VDE-SPEC.md.

## Usage
/vde-new-vm $ARGUMENTS

`$ARGUMENTS` = `lang <name>` or `service <name>` (e.g., `lang erlang` or `service kafka`)

## Execution

**Step 1: Validate Input**

Parse `$ARGUMENTS`:
- Type: `lang` (port range 2200-2299) or `service` (port range 2400-2499)
- Name: VM identifier (lowercase, no spaces, no `vde-` prefix — it's added automatically)

Check for name conflict:
```zsh
grep -i "<name>" data/vm-types.json
```
If exists: report conflict and stop.

**Step 2: Port Assignment**

```zsh
grep "ssh_port" data/vm-types.json | sort
```
- Language VMs: assign next free port in 2200-2299
- Service VMs: assign next free port in 2400-2499
- Confirm port free: `lsof -i :<port>`

**Step 3: Template Discovery (Swarm — spawn simultaneously)**

- Scout A: find most similar existing VM in `data/vm-types.json` as data template
- Scout B: find matching compose template in `configs/docker/` as file template
- Spec reader: extract required fields from `docs/VDE-SPEC.md` VM configuration section

**Step 4: Implementation Plan**

Present to user:
```
VM TYPE: <name> (<lang|service>)
SSH PORT: <assigned port>
SPEC SECTION: <docs/VDE-SPEC.md reference>
FILES TO CREATE/MODIFY:
  - data/vm-types.json — add entry
  - configs/docker/vde-<name>/docker-compose.yml — from <template VM>
  - tests/features/core-infrastructure/vde-<name>.feature — BDD scenarios
TEMPLATE FROM: <most similar existing VM>
ESTIMATED SCOPE: <N files>
```

**HARD STOP**: Wait for user approval before creating any files.

**Step 5: Post-Creation Verification**

After implementation and user approval:
```zsh
python3 -m behave tests/features/core-infrastructure/vde-<name>.feature
./tests/run-docker-free-tests.zsh
```

Update `MEMORY.md` with new VM details and port assignment.