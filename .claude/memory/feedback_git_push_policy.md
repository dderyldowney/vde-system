---
name: Git push in batches — no per-commit push
description: User batches git pushes manually; never push after individual commits during a session
type: feedback
---

Do not push after each commit. The user collects commits locally throughout a session and pushes in batches at their discretion.

**Why:** User explicitly stated "we will do pushes in batches today" (2026-03-26 session).

**How to apply:**
- Commit freely when work is verified.
- Never run `git push` unless the user explicitly says "push" or "push now".
- At session end, note how many commits are ahead of origin so the user can push when ready.
