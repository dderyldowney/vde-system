# Section 10 Verification Law Update
<!-- @shared-law (Forge Component) -->

## Objective
To bring the orchestrator into compliance with Section 10 by performing a surgical strike on `lib/vm-common` to replace the "Host Assumption" with the "Physical Handshake" (Docker Probe).

## Key Files & Context
- `lib/vm-common`: Contains the `find_available_port` function.
- `bin/vde`: VDE CLI tool.

## Implementation Steps
1. Replace the `find_available_port` function in `lib/vm-common` with the provided refactored logic:
```zsh
find_available_port() {
    local min_port=$1
    local max_port=$2
    local registry_dir="${VDE_CACHE_DIR}/port-registry"
    
    mkdir -p "${registry_dir}"
    
    local port=${min_port}
    while [[ ${port} -le ${max_port} ]]; do
        # Atomic Reservation: mkdir is atomic across processes
        if mkdir "${registry_dir}/port-${port}.lock" 2>/dev/null; then
            
            # THE SEEKER'S RECON (Section 10.3): Physical Handshake
            # Attempt to bind the port via a transient Docker container
            if ! docker run --rm --name vde-recon-probe -p "${port}:22" vde-base true >/dev/null 2>&1; then
                # Port is a Ghost or occupied by Scavengers
                touch "${registry_dir}/port-${port}.lock/STALE_HOST"
                # Keep the lock to prevent others from retrying this failed port immediately
                port=$((port + 1))
                continue
            fi
            
            # Port is verified clear.
            echo "${port}"
            return 0
        fi
        port=$((port + 1))
    done
    return 1
}
```

## Verification & Testing
Run the following final strike sequence to verify the 3-VM parallel ignition:
```zsh
bin/vde stop --all && \
rm -rf .cache/port-registry/* .locks/vms/* && \
python3 -m behave tests/features/core-infrastructure/concurrency-stress.feature
```
