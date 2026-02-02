#!/usr/bin/env zsh
# Run complete VDE test suite with failure capture

set -euo pipefail

# Configuration
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="test-logs"
RESULTS_DIR="tests"
BEHAVE_CMD="/Users/dderyldowney/Library/Python/3.9/bin/behave"

# Initialize
mkdir -p "$LOG_DIR"
declare -A phase_results

# Setup SSH agent for tests (required for ssh-agent tests)
echo "=== Setting up SSH Agent ==="
source tests/setup-ssh-agent.zsh

# Phase 1: Docker-free tests
echo "=== Phase 1: Docker-free BDD Tests ==="
if (cd tests/features && $BEHAVE_CMD docker-free/ --format json -o ../behave-results-docker-free.json) \
   > "$LOG_DIR/docker-free-$TIMESTAMP.log" 2>&1; then
    phase_results[docker_free]="PASS"
else
    phase_results[docker_free]="FAIL"
fi

# Phase 2: Unit tests
echo "=== Phase 2: Unit Tests ==="
if make test-unit > "$LOG_DIR/unit-$TIMESTAMP.log" 2>&1; then
    phase_results[unit]="PASS"
else
    phase_results[unit]="FAIL"
fi

# Phase 3: Integration tests
echo "=== Phase 3: Integration Tests ==="
if make test-integration > "$LOG_DIR/integration-$TIMESTAMP.log" 2>&1; then
    phase_results[integration]="PASS"
else
    phase_results[integration]="FAIL"
fi

# Phase 4: Docker-required tests (check Docker first)
echo "=== Phase 4: Docker-required BDD Tests ==="
if docker info >/dev/null 2>&1; then
    if (cd tests/features && $BEHAVE_CMD docker-required/ --format json -o ../behave-results-docker-required.json) \
       > "$LOG_DIR/docker-required-$TIMESTAMP.log" 2>&1; then
        phase_results[docker_required]="PASS"
    else
        phase_results[docker_required]="FAIL"
    fi
else
    echo "Docker daemon not running, skipping docker-required tests"
    phase_results[docker_required]="SKIP"
fi

# Generate summary JSON
cat > "$RESULTS_DIR/TEST_RESULTS_SUMMARY.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "phases": {
    "docker_free": "${phase_results[docker_free]}",
    "unit": "${phase_results[unit]}",
    "integration": "${phase_results[integration]}",
    "docker_required": "${phase_results[docker_required]}"
  },
  "logs": {
    "docker_free": "$LOG_DIR/docker-free-$TIMESTAMP.log",
    "unit": "$LOG_DIR/unit-$TIMESTAMP.log",
    "integration": "$LOG_DIR/integration-$TIMESTAMP.log",
    "docker_required": "$LOG_DIR/docker-required-$TIMESTAMP.log"
  }
}
EOF

# Print summary
echo ""
echo "=== Test Suite Summary ==="
for phase in docker_free unit integration docker_required; do
    echo "$phase: ${phase_results[$phase]}"
done

# Exit with failure if any phase failed
for result in "${phase_results[@]}"; do
    if [[ "$result" == "FAIL" ]]; then
        exit 1
    fi
done

# Cleanup SSH agent
echo ""
echo "=== Cleaning up SSH Agent ==="
source tests/setup-ssh-agent.zsh --cleanup
