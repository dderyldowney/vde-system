#!/usr/bin/env zsh
VDE_ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Verify bin/vde-spine-check.zsh is NOT currently in bin/vde
if grep -q "vde-spine-check.zsh" "${VDE_ROOT_DIR}/bin/vde"; then
    echo "FAIL: vde-spine-check.zsh already integrated"
    exit 1
fi

# Simulate a spine check failure and verify bin/vde still runs
# Since it's not integrated, bin/vde help should still pass
"${VDE_ROOT_DIR}/bin/vde" help > /dev/null
if [[ $? -eq 0 ]]; then
    echo "SUCCESS: bin/vde runs without spine check (Integration Missing)"
else
    echo "FAIL: bin/vde failed unexpectedly"
    exit 1
fi
