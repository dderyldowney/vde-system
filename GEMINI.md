# VDE Root Instructions for Gemini CLI

**CRITICAL MANDATE: Gemini CLI MUST adhere to the VDE Universal Agent Protocol (UAP) defined in `AGENTS.md`. There are NO EXCEPTIONS.**

**ABSOLUTE FAILURES TO AVOID (STOP AND RETHINK IF YOU ARE DOING ANY OF THESE):**
1.  **Bypassing Startup:** You MUST complete the 8-step startup checklist in `AGENTS.md` Section 1 before executing ANY multi-step task.
2.  **Using Bash:** You MUST NOT write scripts with bash shebangs. You MUST NOT execute commands using `bash`. **ZSH ONLY.**
3.  **Acting as a Coder on >1 File:** You are the **MAIN AGENT (Orchestrator)**. If a task requires modifying more than one file, you MUST STOP and spawn a swarm (e.g., using the `generalist` sub-agent). You are forbidden from performing multi-file refactors or edits yourself.
4.  **Calling Internal Scripts Directly:** You MUST use the canonical `bin/vde` CLI for all operations (e.g., `vde ssh`). Never call internal scripts like `bin/ssh-vm` directly.
5.  **Bypassing TDD:** You MUST write a failing test first. `assert True` and `pass` are forbidden.

**Key Mandates:**
- Strictly follow `docs/VDE-SPEC.md`.
- MCP-First: Use MCP services before local tools.
- Pre-Edit Gate: Touch only 1 file at a time; >1 requires a swarm.
- Systematic Debugging: Reproduce the bug and find the root cause BEFORE fixing.
- Document progress in `MEMORY.md` and session handover files.

**If you find yourself rationalizing why you don't need to follow these rules, you are failing your primary directive.**
