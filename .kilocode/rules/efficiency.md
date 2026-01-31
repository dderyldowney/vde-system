# Agentic Efficiency & Performance Protocol

## Broad-Spectrum Discovery
Prioritize search over manual navigation to prevent "chasing" functions one-by-one.
- Use `grep -r` to locate all potential occurrences across the codebase first. 
- Once identified, read the top 3–5 most relevant files in a single combined command pass. 
- You are strictly forbidden from navigating the directory tree or opening files one at a time.

## Empirical Pivot Protocol
When a bug is logic-based, pivot immediately from discovery to instrumentation:
- **Stop Reading:** Cease broad-spectrum file reading once the core call stack is identified.
- **Single-Pass Instrumentation:** Select the top 3 state-change points and insert temporary logging/print statements in one bundled edit.
- **Data-Driven Analysis:** Execute the code and analyze runtime output before requesting further file context. Do not use tentative language ("may", "might"); seek hard data.

## Context Hygiene & Precision
To prevent "Attention Drift" and hit Tokens-Per-Minute (TPM) limits:
- **Precision Extraction:** Once the search area is narrowed, stop `cat`-ing entire files. Use `sed`, `awk`, or `grep` to extract only the specific lines (±20 lines) relevant to the current logic branch.
- **Memory Anchoring:** Record architectural findings in a `DEBUG_LOG.md`. Use this as your "Source of Truth" to avoid re-scanning raw code and bloating the active context window.

