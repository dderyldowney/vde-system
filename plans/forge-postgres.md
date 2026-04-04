# Implementation Plan: Forge PostgreSQL (vde-postgres)

## Objective
Forge the `vde-postgres` service environment with full server installation, database initialization, and remote access configuration, adhering to alphabetical re-indexing and port mandates.

## Key Files & Context
- `data/vm-types.json`: Authoritative configuration source.
- `data/vm-types.conf`: Legacy configuration source (must be synced).
- `configs/ssh/config`: SSH connectivity bridge.
- `bin/vde`: Authoritative orchestrator.

## Implementation Steps
1. **Material Truth Update**:
   - Update `vde-postgres` entry in `data/vm-types.json` with `postgresql postgresql-contrib` and the corrected, version-agnostic `custom_cmd`.
2. **Enforcement & Quality Gate**:
   - Run `vde-enforce-uap.zsh`.
   - Invoke `.conf` synchronization logic to mirror JSON changes.
3. **Execution**:
   - Run `bin/vde rebuild postgres`.
4. **Verification**:
   - Confirm database accessibility via SSH: `bin/vde enter postgres "psql -U devuser -d devuser -c 'SELECT version();'"`
   - Confirm SSH stability on port 2404.
5. **Lifecycle Cleanup**:
   - Execute `bin/vde stop postgres`.

## Verification & Testing
- `psql` command must return PostgreSQL version.
- `docker ps` must be empty at the end of the turn.
