---
name: VDE startup must be fully automatic
description: User requires the 7-step startup checklist to execute automatically at session start and /new — no user input permitted before startup runs
type: feedback
---

The 7-step startup checklist must execute BEFORE control is handed to the user. No user typing should be required to trigger it.

**Why:** The user was frustrated that CLAUDE.md instructions only ran after the first user message, not proactively at startup.

**How to apply:**
- Initial startup is handled by a `claude()` zsh function in `~/.zshrc` — it runs `claude --print "..."` for startup, then `claude --continue` for interactive mode. Do NOT suggest removing or weakening this.
- `/new` is handled by `.claude/commands/new.md` and `.kilocode/commands/new.md` — these override the built-in `/new` with immediate 7-step execution.
- If the user reports startup still isn't automatic, check that `~/.zshrc` was sourced (`source ~/.zshrc`) and that the `claude` function is active (`type claude`).
