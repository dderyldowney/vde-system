# Phase 25 Finalization: Lock-Queue Model (FIFO)

## Objective
Replace the current "Retry Ritual" (spinlock) in `lib/vm-lock` with a deterministic, First-In-First-Out (FIFO) queuing mechanism. This fulfills the Phase 25 mandate by preventing "thundering herd" race conditions in extremely high-concurrency environments.

## Key Files & Context
- `lib/vm-lock`: Contains the `claim_lock` and `release_lock` functions.

## Implementation Steps

### 1. The Ticket Queue (Arrival Sequencing)
- Before entering the retry loop, a process will register a "ticket" in a `.queue` directory associated with the target lock.
    ```zsh
    local queue_dir="${lock_file}.queue"
    mkdir -p "${queue_dir}" 2>/dev/null
    
    # Use ZSH native precise timing for ticket sequencing
    zmodload zsh/datetime 2>/dev/null
    local ticket_id="${EPOCHREALTIME:-$(date +%s).$RANDOM}-$$"
    local ticket_file="${queue_dir}/${ticket_id}"
    touch "${ticket_file}"
    ```

### 2. The Line Check (FIFO Enforcement)
- During the polling loop, a process will check if it holds the oldest ticket in the queue.
- **Rule**: A process may ONLY attempt the atomic `mkdir` lock if its ticket is the oldest in the queue directory.
    ```zsh
    # Find the oldest ticket (numerically sorted by timestamp)
    local oldest_ticket=$(ls -1 "${queue_dir}" 2>/dev/null | sort -n | head -n 1)
    
    if [[ "${oldest_ticket}" == "${ticket_id}" ]]; then
        # At the front of the line! Attempt atomic lock.
        if mkdir "${lock_file}" 2>/dev/null; then
            # ... record ownership ...
            return 0
        fi
    fi
    ```

### 3. Cleanup & Retreat
- If a process hits its maximum retry limit, it MUST remove its ticket from the queue before returning a failure.
- Update `release_lock` to remove the owning process's ticket from the queue, allowing the next process in line to proceed.

## Verification & Testing
- Create a new BDD scenario in `tests/features/core-infrastructure/concurrency-queue.feature` to verify strict FIFO ordering by launching 3 simultaneous background requests and checking their ignition sequence.
- Run `make test` to ensure the new logic does not break existing orchestration paths.