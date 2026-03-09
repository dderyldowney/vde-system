#!/usr/bin/env zsh
# =============================================================================
# docker-test-utils.zsh — Shared Docker test lifecycle utilities
#
# Provides: Docker detection, container cleanup, readiness polling,
#           SSH agent tracking, and orphan process cleanup.
#
# Usage:
#   source "$PROJECT_ROOT/tests/lib/docker-test-utils.zsh"
#   docker_test_setup  # call once at top of test file
#   # ... tests ...
#   docker_test_teardown  # called automatically via EXIT trap
# =============================================================================

# Guard against double-sourcing
[[ "${_VDE_DOCKER_TEST_UTILS_LOADED:-}" == "1" ]] && return 0
_VDE_DOCKER_TEST_UTILS_LOADED=1

# Tracked state for teardown
_DOCKER_TEST_AGENT_PID=""
_DOCKER_TEST_AGENT_SOCK=""
_DOCKER_TEST_VMS=()                      # VMs created during this test run
_DOCKER_TEST_SETUP_CALLED=0

# =============================================================================
# DOCKER AVAILABILITY
# =============================================================================

# check_docker_available
# Returns 0 if Docker daemon is running and accessible, 1 otherwise.
# Prints a clear message so callers know why tests were skipped.
check_docker_available() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "[DOCKER] SKIP: docker binary not found in PATH" >&2
        return 1
    fi
    if ! docker info >/dev/null 2>&1; then
        echo "[DOCKER] SKIP: Docker daemon not running or not accessible (try: docker info)" >&2
        return 1
    fi
    echo "[DOCKER] Docker is available: $(docker version --format '{{.Server.Version}}' 2>/dev/null || echo 'unknown version')"
    return 0
}

# =============================================================================
# ORPHAN PROCESS CLEANUP
# =============================================================================

# kill_orphan_ssh_agents
# Kills ssh-agent processes whose PPID is 1 (fully orphaned — parent is dead).
kill_orphan_ssh_agents() {
    local killed=0
    # Get all ssh-agent PIDs whose parent is PID 1 (orphaned)
    while IFS= read -r pid; do
        [[ -z "$pid" ]] && continue
        local ppid
        ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
        if [[ "$ppid" == "1" ]]; then
            echo "[CLEANUP] Killing orphaned ssh-agent PID $pid"
            kill "$pid" 2>/dev/null && ((killed++))
        fi
    done < <(pgrep -x ssh-agent 2>/dev/null)
    [[ $killed -gt 0 ]] && echo "[CLEANUP] Killed $killed orphaned ssh-agent(s)"
    return 0
}

# kill_orphan_test_sessions
# Kills zsh processes running vde test scripts that have been running > 10 min.
# Prevents accumulation of stuck/disconnected test sessions.
kill_orphan_test_sessions() {
    local killed=0
    local cutoff_seconds=600   # 10 minutes
    local now
    now=$(date +%s)

    while IFS= read -r pid; do
        [[ -z "$pid" ]] && continue
        # Skip our own PID and this script's parent
        [[ "$pid" == "$$" || "$pid" == "$PPID" ]] && continue

        # Get process start time
        local etime
        etime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
        [[ -z "$etime" ]] && continue

        # Parse etime format: [[dd-]hh:]mm:ss
        local seconds=0
        if [[ "$etime" =~ ^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            seconds=$(( ${match[1]} * 86400 + ${match[2]} * 3600 + ${match[3]} * 60 + ${match[4]} ))
        elif [[ "$etime" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            seconds=$(( ${match[1]} * 3600 + ${match[2]} * 60 + ${match[3]} ))
        elif [[ "$etime" =~ ^([0-9]+):([0-9]+)$ ]]; then
            seconds=$(( ${match[1]} * 60 + ${match[2]} ))
        fi

        if [[ $seconds -gt $cutoff_seconds ]]; then
            local cmd
            cmd=$(ps -o args= -p "$pid" 2>/dev/null | head -c 80)
            echo "[CLEANUP] Killing stale test session PID $pid (${seconds}s old): $cmd"
            kill -TERM "$pid" 2>/dev/null && ((killed++))
        fi
    done < <(pgrep -f "vde.*test|test.*vde" 2>/dev/null)

    [[ $killed -gt 0 ]] && echo "[CLEANUP] Killed $killed stale test session(s)"
    return 0
}

# =============================================================================
# CONTAINER CLEANUP
# =============================================================================

# cleanup_vde_containers [--images]
# Stops and removes all running vde-* containers.
# Pass --images to also remove vde-* Docker images.
cleanup_vde_containers() {
    local remove_images=0
    [[ "${1:-}" == "--images" ]] && remove_images=1

    echo "[CLEANUP] Stopping all vde-* containers..."
    local containers
    containers=$(docker ps -a --filter "name=vde-" --format "{{.Names}}" 2>/dev/null)

    if [[ -z "$containers" ]]; then
        echo "[CLEANUP] No vde-* containers found"
    else
        echo "$containers" | while IFS= read -r c; do
            [[ -z "$c" ]] && continue
            echo "[CLEANUP]   Stopping: $c"
            docker stop "$c" >/dev/null 2>&1 || true
            docker rm -f "$c" >/dev/null 2>&1 || true
        done
    fi

    if [[ $remove_images -eq 1 ]]; then
        echo "[CLEANUP] Removing vde-* images..."
        docker images --filter "reference=vde-*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null \
            | while IFS= read -r img; do
                [[ -z "$img" ]] && continue
                echo "[CLEANUP]   Removing image: $img"
                docker rmi -f "$img" >/dev/null 2>&1 || true
            done
    fi

    # Remove any dangling state files left by the test VMs
    local state_dir="${VDE_ROOT_DIR:-$(pwd)}/.docker-state"
    if [[ -d "$state_dir" ]]; then
        echo "[CLEANUP] Clearing .docker-state/"
        rm -f "$state_dir"/vde-*.json 2>/dev/null || true
    fi

    echo "[CLEANUP] Done"
}

# cleanup_test_vm <vm_name>
# Stop and remove a single VM's container. Used in per-VM test teardown.
cleanup_test_vm() {
    local vm="$1"
    [[ -z "$vm" ]] && return 0
    local container="vde-${vm##vde-}"   # normalize: strip leading vde- if present
    echo "[CLEANUP] Stopping test VM: $container"
    docker stop "$container" >/dev/null 2>&1 || true
    docker rm -f "$container" >/dev/null 2>&1 || true
}

# =============================================================================
# CONTAINER READINESS POLLING
# =============================================================================

# wait_for_container_ready <vm_name> [timeout_seconds]
# Polls until the container is in 'running' state or timeout expires.
# Docker healthcheck status is also checked if configured.
# Returns 0 on success, 1 on timeout.
wait_for_container_ready() {
    local vm_name="$1"
    local timeout="${2:-120}"    # default 2 minutes
    local interval=5
    local elapsed=0
    local container="vde-${vm_name##vde-}"

    echo "[WAIT] Waiting for $container to be ready (timeout: ${timeout}s)..."

    while [[ $elapsed -lt $timeout ]]; do
        local status
        status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)

        if [[ "$status" == "running" ]]; then
            # Also check healthcheck if it exists
            local health
            health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container" 2>/dev/null)
            if [[ "$health" == "none" || "$health" == "healthy" ]]; then
                echo "[WAIT] $container is ready after ${elapsed}s (health: $health)"
                return 0
            elif [[ "$health" == "unhealthy" ]]; then
                echo "[WAIT] $container is unhealthy after ${elapsed}s" >&2
                return 1
            fi
            # still starting: wait
        elif [[ "$status" == "exited" || "$status" == "dead" ]]; then
            echo "[WAIT] $container exited unexpectedly (status: $status)" >&2
            docker logs "$container" 2>&1 | tail -20 >&2
            return 1
        fi

        printf "[WAIT] %ds: %s (status=%s, health=%s)\n" \
            "$elapsed" "$container" "${status:-not_found}" "${health:-?}"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo "[WAIT] TIMEOUT: $container not ready after ${timeout}s" >&2
    docker logs "$container" 2>&1 | tail -20 >&2
    return 1
}

# =============================================================================
# LIFECYCLE HOOKS
# =============================================================================

# docker_test_setup [vm_name...]
# Call at the top of a Docker test file:
#   1. Kills orphaned ssh-agents and stale test sessions
#   2. Checks Docker is available (exits 0 with SKIP message if not)
#   3. Cleans up any leftover vde-* containers
#   4. Starts a fresh ssh-agent tracked for teardown
#   5. Installs EXIT/INT/TERM traps to guarantee cleanup
docker_test_setup() {
    _DOCKER_TEST_VMS=("$@")
    _DOCKER_TEST_SETUP_CALLED=1

    echo ""
    echo "============================================================"
    echo " VDE Docker Test Setup"
    echo "============================================================"

    # Kill stale sessions and orphaned agents first
    kill_orphan_test_sessions
    kill_orphan_ssh_agents

    # Check Docker
    if ! check_docker_available; then
        echo "[DOCKER] Skipping Docker tests — daemon not available"
        exit 0
    fi

    # Pre-test cleanup
    cleanup_vde_containers

    # Start a tracked ssh-agent
    local agent_output
    agent_output=$(ssh-agent -s 2>/dev/null)
    if [[ -n "$agent_output" ]]; then
        eval "$agent_output" >/dev/null 2>&1
        _DOCKER_TEST_AGENT_PID="${SSH_AGENT_PID:-}"
        _DOCKER_TEST_AGENT_SOCK="${SSH_AUTH_SOCK:-}"
        echo "[SETUP] Started ssh-agent PID: $_DOCKER_TEST_AGENT_PID"
    fi

    # Install teardown trap
    trap 'docker_test_teardown' EXIT INT TERM

    echo "[SETUP] Docker test environment ready"
    echo "============================================================"
    echo ""
}

# docker_test_teardown
# Called automatically via trap. Cleans up containers, kills SSH agent,
# and prints a final summary line.
docker_test_teardown() {
    echo ""
    echo "============================================================"
    echo " VDE Docker Test Teardown"
    echo "============================================================"

    # Stop any VMs that were registered
    for vm in "${_DOCKER_TEST_VMS[@]}"; do
        cleanup_test_vm "$vm"
    done

    # Full container sweep for safety
    cleanup_vde_containers

    # Kill the ssh-agent we started
    if [[ -n "$_DOCKER_TEST_AGENT_PID" ]]; then
        echo "[TEARDOWN] Killing ssh-agent PID $_DOCKER_TEST_AGENT_PID"
        kill "$_DOCKER_TEST_AGENT_PID" 2>/dev/null || true
        unset SSH_AGENT_PID SSH_AUTH_SOCK
    fi

    # Kill any remaining orphans
    kill_orphan_ssh_agents

    echo "[TEARDOWN] Cleanup complete"
    echo "============================================================"
    echo ""
}
