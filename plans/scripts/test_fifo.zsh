#!/usr/bin/env zsh
source "/Users/dderyldowney/VDE/lib/vm-common"
source "/Users/dderyldowney/VDE/lib/vde-core"
source "/Users/dderyldowney/VDE/lib/vm-lock"

LOCK_NAME="$1"
WAIT_TIME="$2"
ID="$3"

echo "ARRIVE:$ID:$(date +%s.%N)" >> "/Users/dderyldowney/VDE/plans/scripts/fifo_test.log"
if claim_lock "$LOCK_NAME"; then
    echo "ACQUIRE:$ID:$(date +%s.%N)" >> "/Users/dderyldowney/VDE/plans/scripts/fifo_test.log"
    # Small sleep to allow others to queue up
    zmodload zsh/zselect && zselect -t 50
    release_lock "$LOCK_NAME"
    echo "RELEASE:$ID:$(date +%s.%N)" >> "/Users/dderyldowney/VDE/plans/scripts/fifo_test.log"
else
    echo "FAIL:$ID:$(date +%s.%N)" >> "/Users/dderyldowney/VDE/plans/scripts/fifo_test.log"
fi
