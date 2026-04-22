#!/usr/bin/env zsh
# @armor (Concurrency Test Rig)
VDE_ROOT_DIR="${0:a:h:h:h}"
source "${VDE_ROOT_DIR}/lib/vm-common"
source "${VDE_ROOT_DIR}/lib/vde-core"
source "${VDE_ROOT_DIR}/lib/vm-lock"

LOCK_NAME="$1"
WAIT_TIME="$2"
ID="$3"

echo "ARRIVE:$ID:$(date +%s.%N)" >> "${VDE_ROOT_DIR}/plans/scripts/fifo_test.log"
if claim_lock "$LOCK_NAME"; then
    echo "ACQUIRE:$ID:$(date +%s.%N)" >> "${VDE_ROOT_DIR}/plans/scripts/fifo_test.log"
    # Small sleep to allow others to queue up
    zmodload zsh/zselect && zselect -t 50
    release_lock "$LOCK_NAME"
    echo "RELEASE:$ID:$(date +%s.%N)" >> "${VDE_ROOT_DIR}/plans/scripts/fifo_test.log"
else
    echo "FAIL:$ID:$(date +%s.%N)" >> "${VDE_ROOT_DIR}/plans/scripts/fifo_test.log"
fi
