# Scratch Work Lives In The Project
<!-- @forge (Governance Sentinel) -->

## Where Scratch Work Goes
Scratch work lives under `<project root>/.scratch/`. This covers a scratch HOME, a scratch projects directory, and logs and test evidence.
Scratch work never goes in `/tmp` or in a tool's own scratch area.

## Layout
- Each run uses its own directory, `.scratch/<run>/`, where `<run>` is a short name for that run (for example the issue number).
- `.scratch/<run>/h` is the scratch HOME.
- `.scratch/<run>/p` is the scratch projects directory.
- Logs and evidence go directly in `.scratch/<run>/`.
- Anything private to a security item goes in the private security directory instead, not here.

## Why
Every write outside the project crosses the project/local-user boundary. Those crossings are kept rare and deliberate.
Long system scratch paths can exceed the unix socket path limit of about `104` characters, so scratch paths are kept short.

## Rules
1. Never touch the real user's `~/.ssh`, `~/.zshrc`, real HOME or real projects directory from a test or a run.
2. Point HOME at `.scratch/<run>/h` and VDE_PROJECTS_DIR at `.scratch/<run>/p` instead.
3. `.scratch/` is untracked and ignored by `.gitignore`.
4. When the work is done a run's directory is deleted: a run deletes only its own `.scratch/<run>/` directory, never the whole `.scratch/`, because other runs may be using it.
5. Never use `.scratch/` to hold anything the user must keep.
6. The private security directory (`VDE_SECURITY_DIR`, default `~/.vde-security`) is a separate, permanent location and is not scratch. Ledger entries, issue maps and any evidence that names an unfixed weakness go there, never in `.scratch/` or the repository, and the Forge refuses an in-repository location. When HOME points at `.scratch/<run>/h`, set `VDE_SECURITY_DIR` to the real private directory.

## Applies to
Every agent and every test run in this repository.
