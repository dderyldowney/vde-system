# Rate Limit & Efficiency Protocol

## Anti-Fragmentation & Batching
The API gateway is sensitive; you must minimize request frequency.
- Never use `read_file` or `ls` on individual items in a loop. 
- Use single, bundled commands (e.g., `cat file1 file2 file3` or `grep -A 20`) to pull all necessary context in ONE request. 
- Combine your analysis into a single, comprehensive reasoning block rather than multiple incremental "ping-pong" requests.

## Broad-Spectrum Discovery
Prioritize search over manual navigation to prevent "chasing" functions one-by-one.
- Use `grep -r` to locate all potential occurrences of a bug or function across the codebase first. 
- Once identified, read the top 3–5 most relevant files in a single combined command pass. 
- You are strictly forbidden from navigating the directory tree or opening files one at a time.

## Empirical Pivot Protocol
When a bug is deep or logic-based, pivot immediately from discovery to instrumentation:
- **Stop Reading:** Cease broad-spectrum file reading once the core call stack is identified.
- **State-Point Identification:** Select the top 3 most likely state-change points.
- **Single-Pass Instrumentation:** Insert temporary logging/print statements into these points in one bundled edit.
- **Data-Driven Analysis:** Execute the code and analyze runtime output before requesting further file context.

## Decisive Instrumentation & Authorization
Eliminate hesitation and "maybe" loops to save tokens and time.
- **Avoid Tentative Language:** Do not use "may," "might," or "possibly." 
- **Hypothesis-Driven Action:** State what result would "confirm" your theory and what would "refute" it, then execute the test immediately.
- **Batch Authorization:** Bundle all proposed edits into a single "Plan of Action" for approval. Provide pre-emptive justification for the whole batch to avoid one-by-one confirmation loops.

## Thought-Stream Limitation
Prevent "Reasoning Storms" and recursive speculation.
- If internal reasoning exceeds 200 words without a terminal action, you must truncate and execute a diagnostic command to refresh your context with external ground truth.
- Once a proposal is sent for user approval, cease all background API requests and "thinking" until a response is received to minimize idle gateway traffic.

