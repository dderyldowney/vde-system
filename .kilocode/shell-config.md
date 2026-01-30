# Shell Configuration

## Shell Paths for VDE Project

This project uses the following shell interpreters:

| Shell | Path | Version Notes |
|-------|------|---------------|
| bash | `/usr/local/bin/bash` | Use this path explicitly when running bash scripts |
| zsh | `/bin/zsh` | Use this path explicitly when running zsh scripts |

## Script Shebangs

All scripts should use the appropriate shebang:

- For bash scripts: `#!/usr/local/bin/bash`
- For zsh scripts: `#!/bin/zsh`

## Running Tests

When running tests, ensure the correct shell interpreter is used:

```bash
# For bash unit tests
/usr/local/bin/bash tests/unit/vm-common.test.sh

# For zsh unit tests (if applicable)
/bin/zsh tests/unit/vde-shell-compat.test.sh
```
