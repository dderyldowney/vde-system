# Shell Configuration

## Shell Paths for VDE Project

This project uses **zsh exclusively**. `/bin/sh` and `/usr/bin/env sh` are forbidden.

| Shell | Path | Version Notes |
|-------|------|---------------|
| zsh | `/bin/zsh` | Use this path explicitly when running zsh scripts |
| bash | `/usr/local/bin/bash` | NOT SUPPORTED - zsh only |

## Shell Version Requirements

- **zsh**: Version 5.0 or later required (5.x recommended).
- **bash**: NOT SUPPORTED - this is a zsh-only project.

## Script Shebangs

**All scripts MUST use zsh:**

- For zsh scripts: `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **FORBIDDEN**: `#!/bin/sh`, `#!/usr/bin/env sh`, `#!/bin/bash`

## Project Standards

See [STYLE_GUIDE.md](../../STYLE_GUIDE.md) for complete coding standards including:
- Zsh-only requirement (Section: Shell Scripting Standards)
- Shell prohibition policy
- Code review requirements

## Running Tests

```bash
# For zsh unit tests
/bin/zsh tests/unit/vde-shell-compat.test.sh

# Verify zsh shebang compliance
zsh ./scripts/check-zsh-shebang.zsh
```
