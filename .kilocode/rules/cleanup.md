# Session Termination & Cleanup Protocol

## Automatic Housekeeping
Once a fix is confirmed or the primary task is complete, you are MANDATED to perform these steps as part of the "Definition of Done":
1. **Batch Revert:** Do not remove logs one-by-one. Use `git checkout [files]` or a single `sed` command to revert temporary instrumentation across all affected files.
2. **Artifact Deletion:** Use a single `rm` command to delete `DEBUG_LOG.md` and any temporary diagnostic scripts.
3. **Silent Validation:** Perform one final execution of tests to ensure the cleanup is successful. Do not narrate every step; only report the final result.

## Rate Limit Protection (Batch Cleanup)
To avoid 429 errors during housekeeping:
1. **Avoid Recursive Scanning:** Do not "search" for your own edits file-by-file. Rely on your internal history or `git status` to identify modified files immediately.
2. **Atomic Actions:** Group all file deletions and code reverts into the fewest possible terminal commands. 
3. **Standby:** Once the cleanup command is issued, cease all further background "thinking" or API requests.

## Final Summary
Conclude the session with a concise, single-paragraph summary of the "Root Cause" and the "Resolution." Do not ask for separate permission to clean up; initiate this protocol immediately upon confirmation of the fix.

