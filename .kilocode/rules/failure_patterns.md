# COMMON FAILURE PATTERNS

Internal "optimization" tendencies that cause failures:

1. **"This seems simple, I'll skip exploration"** → WRONG
2. **"I can batch these tasks"** → WRONG, ask user first
3. **"The review probably won't find issues"** → WRONG, review is mandatory
4. **"I'll set a context flag instead of running the command"** → WRONG, fake tests prohibited
5. **"I'll skip phases, the plan is obvious"** → WRONG, phases are invariant
6. **"User said 'go ahead', that's approval for everything"** → WRONG, only approved for the specific plan
7. **"I'll use grep/find/cat directly"** → WRONG, use MCP services first, internal tools as fallback

**When in doubt: Follow the literal instructions. Do NOT "optimize away" required steps.**
