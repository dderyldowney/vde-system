#!/usr/bin/env zsh
# @shared-law (Forge Component)
# test-pulse-tdd.zsh - Physical verification of Identity Pulse sentinel

VDE_ROOT_DIR="$(pwd)"
source "${VDE_ROOT_DIR}/lib/vde-log"
source "${VDE_ROOT_DIR}/lib/vde-pulse.zsh"

VM="python"
CONTAINER="vde-python"

echo "[TDD] Phase 1: Ensuring VM is running..."
./bin/vde start "${VM}" >/dev/null

echo "[TDD] Phase 2: Simulating Bridge Fracture (Killing socat inside Spoke)..."
docker exec -u root "${CONTAINER}" pkill socat

echo "[TDD] Phase 3: Executing Sentinel Strike (Should FAIL)..."
if vde_identity_pulse "${VM}"; then
    echo "\033[0;31m[FAILURE] TDD Strike Failed: Sentinel ALLOWED a fractured bridge.\033[0m"
    exit 1
else
    echo "\033[0;32m[SUCCESS] TDD Red Gauntlet: Sentinel BLOCKED the fractured bridge.\033[0m"
fi

echo "[TDD] Phase 4: Repairing Bridge (Restarting VM)..."
./bin/vde restart "${VM}" >/dev/null

echo "[TDD] Phase 5: Executing Sentinel Strike (Should PASS)..."
if vde_identity_pulse "${VM}"; then
    echo "\033[0;32m[SUCCESS] TDD Green Victory: Sentinel ALLOWED the healthy bridge.\033[0m"
else
    echo "\033[0;31m[FAILURE] TDD Strike Failed: Sentinel BLOCKED a healthy bridge.\033[0m"
    exit 1
fi

echo "\n\033[1;32m✓ Task 1 Certified: Identity Pulse is Rule 14 Compliant.\033[0m"
