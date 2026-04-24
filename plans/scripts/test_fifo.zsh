#!/usr/bin/env zsh
# @shared-law (FIFO Stress Test Script)
VDE_ROOT="${VDE_ROOT:-$(cd "$(dirname "$0:A")/../.." && pwd)}"
source "$VDE_ROOT/lib/vm-common"
source "$VDE_ROOT/lib/vde-core"
source "$VDE_ROOT/lib/vm-lock"

LOCK_NAME="$1"
WAIT_TIME="$2"
ID="$3"

echo "ARRIVE:$ID:$(date +%s.%N)" >> "$VDE_ROOT/plans/scripts/fifo_test.log"
if claim_lock "$LOCK_NAME"; then
    echo "ACQUIRE:$ID:$(date +%s.%N)" >> "$VDE_ROOT/plans/scripts/fifo_test.log"
    # Small sleep to allow others to queue up
    zmodload zsh/zselect && zselect -t 50
    release_lock "$LOCK_NAME"
    echo "RELEASE:$ID:$(date +%s.%N)" >> "$VDE_ROOT/plans/scripts/fifo_test.log"
else
    echo "FAIL:$ID:$(date +%s.%N)" >> "$VDE_ROOT/plans/scripts/fifo_test.log"
fi
